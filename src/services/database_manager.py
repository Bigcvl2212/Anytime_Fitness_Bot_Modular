#!/usr/bin/env python3
"""
Database Manager Service
Handles all database operations, schema management, and data refresh logic
"""

import os
import pandas as pd
import logging
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from flask import current_app

# PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced Database Manager to handle comprehensive gym data with auto-refresh
    Uses PostgreSQL exclusively for all database operations
    """
    
    def __init__(self, db_path=None):
        self.last_refresh = None
        self.refresh_interval = 3600  # 1 hour in seconds
        
        # ALWAYS USE POSTGRESQL - NO MORE SQLITE!
        self.db_type = 'postgresql'
        
        if not POSTGRES_AVAILABLE:
            logger.error("❌ PostgreSQL required but psycopg2 not installed")
            raise ImportError("psycopg2-binary required for PostgreSQL support")
        
        # Parse DATABASE_URL or use individual environment variables
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Parse Cloud SQL connection string
            logger.info(f"🔗 Parsing DATABASE_URL: {database_url[:50]}...")
            self.postgres_config = self._parse_database_url(database_url)
        else:
            # Fallback to individual environment variables
            logger.info("📝 Using individual database environment variables")
            self.postgres_config = {
                'host': os.getenv('DB_HOST', os.getenv('POSTGRES_HOST', 'localhost')),
                'port': int(os.getenv('DB_PORT', os.getenv('POSTGRES_PORT', '5432'))),
                'dbname': os.getenv('DB_NAME', os.getenv('POSTGRES_DATABASE', 'gym_bot')),
                'user': os.getenv('DB_USER', os.getenv('POSTGRES_USER', 'postgres')),
                'password': os.getenv('DB_PASSWORD', os.getenv('POSTGRES_PASSWORD', ''))
            }
        # Add convenience properties for health checks
        self.db_host = self.postgres_config['host']
        self.db_name = self.postgres_config['dbname']
        logger.info(f"🐘 Using PostgreSQL database: {self.postgres_config['host']}:{self.postgres_config['port']}/{self.postgres_config['dbname']}")
            
        self.init_database()
    
    def _parse_database_url(self, database_url):
        """Parse DATABASE_URL for Cloud SQL connection"""
        try:
            from urllib.parse import urlparse, parse_qs
            
            # Parse the URL
            parsed = urlparse(database_url)
            
            # Extract connection parameters
            config = {
                'user': parsed.username or 'postgres',
                'password': parsed.password or '',
                'dbname': parsed.path.lstrip('/') or 'gym_bot',
                'port': parsed.port or 5432
            }
            
            # Check for Cloud SQL socket connection
            query_params = parse_qs(parsed.query)
            
            if 'host' in query_params and query_params['host'][0].startswith('/cloudsql/'):
                # Cloud SQL Unix socket connection
                config['host'] = query_params['host'][0]
                logger.info(f"🌐 Using Cloud SQL socket: {config['host']}")
            elif parsed.hostname:
                # Regular TCP connection
                config['host'] = parsed.hostname
                logger.info(f"🌐 Using TCP connection: {config['host']}:{config['port']}")
            else:
                # Default to localhost
                config['host'] = 'localhost'
                logger.warning("⚠️ No host found in DATABASE_URL, defaulting to localhost")
            
            logger.info(f"🔗 Parsed database config: user={config['user']}, db={config['dbname']}, host={config['host'][:30]}...")
            return config
            
        except Exception as e:
            logger.error(f"❌ Error parsing DATABASE_URL: {e}")
            # Fallback configuration
            return {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'gym_bot',
                'user': 'postgres',
                'password': ''
            }
    
    def get_connection(self):
        """Get PostgreSQL database connection"""
        return psycopg2.connect(**self.postgres_config)
    
    def get_cursor(self, conn):
        """Get PostgreSQL cursor with RealDictCursor for row dictionary access"""
        try:
            return conn.cursor(cursor_factory=RealDictCursor)
        except TypeError:
            # Fallback for older psycopg2 versions
            return conn.cursor()
    
    def close_connection(self, conn):
        """Close database connection safely"""
        try:
            if conn:
                conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Warning closing database connection: {e}")
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Execute PostgreSQL query with proper parameter formatting"""
        # Convert SQLite ? placeholders to PostgreSQL %s placeholders, but preserve LIKE patterns
        if '?' in query:
            import re
            # First, temporarily replace LIKE patterns with placeholders
            like_patterns = []
            def preserve_like(match):
                pattern = match.group(0)
                like_patterns.append(pattern)
                return f"__LIKE_PATTERN_{len(like_patterns) - 1}__"
            
            # Preserve LIKE patterns with % wildcards
            query = re.sub(r"LIKE\s+'[^']*%[^']*'", preserve_like, query, flags=re.IGNORECASE)
            
            # Now replace ? with %s safely
            query = query.replace('?', '%s')
            
            # Restore LIKE patterns
            for i, pattern in enumerate(like_patterns):
                query = query.replace(f"__LIKE_PATTERN_{i}__", pattern)
        
        # Debug logging for PostgreSQL
        logger.info(f"🐘 PostgreSQL Query: {query}")
        logger.info(f"🐘 Parameters: {params}")
        
        conn = self.get_connection()
        cursor = self.get_cursor(conn)
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            result = None
            # Auto-detect SELECT queries and fetch results
            query_type = query.strip().upper()
            if query_type.startswith('SELECT'):
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    # Default to fetch_all for SELECT queries
                    result = cursor.fetchall()
                    # Return empty list instead of None for consistency
                    if result is None:
                        result = []
            elif fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            
            conn.commit()
            return result
            
        except Exception as e:
            logger.error(f"❌ SQL execution error: {e}")
            logger.error(f"   Query: {query}")
            logger.error(f"   Params: {params}")
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
        
    def needs_refresh(self):
        """Check if database needs refreshing based on time interval"""
        if self.last_refresh is None:
            return True
        return (datetime.now() - self.last_refresh).total_seconds() > self.refresh_interval
    
    def get_fresh_data_from_clubos(self):
        """Get fresh data from ClubOS APIs"""
        try:
            logger.info("🔄 Fetching fresh data from ClubOS APIs")
            
            # Import here to avoid circular imports
            # The module lives at src/clubos_fresh_data_api.py
            from src.services.api.clubos_fresh_data_api import ClubOSFreshDataAPI
            
            # Use the fresh data API to get real-time data
            fresh_data_api = ClubOSFreshDataAPI()
            fresh_members = fresh_data_api.get_fresh_members()
            fresh_prospects = fresh_data_api.get_fresh_prospects()
            summary = fresh_data_api.get_fresh_data_summary()
            
            fresh_data = {
                'members': fresh_members,
                'prospects': fresh_prospects,
                'summary': summary,
                'updated_at': datetime.now().isoformat()
            }
            
            logger.info("✅ Fresh data fetched successfully")
            return fresh_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching fresh data: {e}")
            return None
    
    def refresh_database(self, force=False):
        """Refresh the database with latest data from ClubOS"""
        if not force and not self.needs_refresh():
            logger.info("⚠️ Database is fresh, skipping refresh")
            return False
            
        logger.info("🔄 Starting database refresh")
        
        try:
            # Get fresh data from ClubOS
            fresh_data = self.get_fresh_data_from_clubos()
            
            if fresh_data:
                # Update database with fresh data
                self._update_database_with_fresh_data(fresh_data)
                self.last_refresh = datetime.now()
                logger.info("✅ Database refreshed successfully")
                return True
            else:
                # Fallback to existing CSV data but update the timestamp
                logger.warning("⚠️ Using existing CSV data as fallback")
                self.last_refresh = datetime.now()
                return False
                
        except Exception as e:
            logger.error(f"❌ Database refresh failed: {e}")
            return False
    
    def _update_database_with_fresh_data(self, fresh_data):
        """Update database tables with fresh data"""
        conn = self.get_connection()
        # Use regular cursor for INSERT operations to avoid RealDictCursor issues
        cursor = conn.cursor()
        
        try:
            logger.info("🔄 Processing fresh data for database update...")
            
            # Process and insert members data
            if fresh_data.get('members'):
                members_data = fresh_data['members']
                logger.info(f"👥 Processing {len(members_data)} members...")
                
                success_count = 0
                error_count = 0
                
                for member in members_data:
                    try:
                        # Use PostgreSQL UPSERT with ON CONFLICT
                        cursor.execute("""
                            INSERT INTO members (
                                prospect_id, first_name, last_name, full_name, email, phone, mobile_phone,
                                status, status_message, member_type, join_date, amount_past_due,
                                date_of_next_payment, created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (prospect_id) DO UPDATE SET
                                first_name = EXCLUDED.first_name,
                                last_name = EXCLUDED.last_name,
                                full_name = EXCLUDED.full_name,
                                email = EXCLUDED.email,
                                phone = EXCLUDED.phone,
                                mobile_phone = EXCLUDED.mobile_phone,
                                status = EXCLUDED.status,
                                status_message = EXCLUDED.status_message,
                                member_type = EXCLUDED.member_type,
                                join_date = EXCLUDED.join_date,
                                amount_past_due = EXCLUDED.amount_past_due,
                                date_of_next_payment = EXCLUDED.date_of_next_payment,
                                updated_at = EXCLUDED.updated_at
                        """, (
                            member.get('ProspectID'),
                            member.get('FirstName'),
                            member.get('LastName'),
                            member.get('Name'),
                            member.get('Email'),
                            member.get('Phone'),
                            member.get('MobilePhone'),
                            member.get('Status'),
                            member.get('StatusMessage'),
                            member.get('MembershipType'),
                            member.get('MemberSince'),
                            float(member.get('AmountPastDue', 0) or 0),
                            member.get('NextPaymentDate'),
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        success_count += 1
                        
                    except Exception as member_error:
                        error_count += 1
                        logger.warning(f"⚠️ Failed to insert member {member.get('ProspectID', 'Unknown')}: {member_error}")
                        # Log problematic data for debugging
                        if '% characters' in str(member_error) or 'syntax error' in str(member_error):
                            logger.warning(f"   Problematic member data: {member}")
                        continue
                
                logger.info(f"✅ Processed {len(members_data)} members: {success_count} successful, {error_count} failed")
            
            # Process and insert prospects data
            if fresh_data.get('prospects'):
                prospects_data = fresh_data['prospects']
                logger.info(f"🎅 Processing {len(prospects_data)} prospects...")
                
                prospect_success_count = 0
                prospect_error_count = 0
                
                for prospect in prospects_data:
                    try:
                        # Skip prospects without a valid ID
                        prospect_id = prospect.get('ProspectID')
                        if not prospect_id:
                            logger.warning(f"Skipping prospect without ID: {prospect.get('Name', 'Unknown')}")
                            prospect_error_count += 1
                            continue
                            
                        # Use PostgreSQL ON CONFLICT for UPSERT
                        cursor.execute("""
                            INSERT INTO prospects (
                                prospect_id, first_name, last_name, full_name, email, phone,
                                status, prospect_type, created_at, updated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (prospect_id) DO UPDATE SET
                                first_name = EXCLUDED.first_name,
                                last_name = EXCLUDED.last_name,
                                full_name = EXCLUDED.full_name,
                                email = EXCLUDED.email,
                                phone = EXCLUDED.phone,
                                status = EXCLUDED.status,
                                prospect_type = EXCLUDED.prospect_type,
                                updated_at = EXCLUDED.updated_at
                        """, (
                            prospect_id,
                            prospect.get('FirstName'),
                            prospect.get('LastName'),
                            prospect.get('Name'),
                            prospect.get('Email'),
                            prospect.get('Phone'),
                            prospect.get('Status'),
                            prospect.get('ProspectType'),
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        prospect_success_count += 1
                        
                    except Exception as prospect_error:
                        prospect_error_count += 1
                        logger.warning(f"⚠️ Failed to insert prospect {prospect.get('ProspectID', 'Unknown')}: {prospect_error}")
                        continue
                
                logger.info(f"✅ Processed {len(prospects_data)} prospects: {prospect_success_count} successful, {prospect_error_count} failed")
            
            # Log the refresh with actual counts
            # Create log table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_refresh_log (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT,
                    last_refresh TIMESTAMP,
                    record_count INTEGER,
                    category_breakdown TEXT
                )
            """)
            
            # Get current counts after insert  
            cursor.execute("SELECT COUNT(*) FROM members")
            member_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM prospects")
            prospect_count = cursor.fetchone()[0]
            
            # Insert refresh logs
            now = datetime.now()
            cursor.execute("""
                INSERT INTO data_refresh_log (table_name, last_refresh, record_count, category_breakdown)
                VALUES (%s, %s, %s, %s)
            """, ('members', now, member_count, '{}'))
            
            cursor.execute("""
                INSERT INTO data_refresh_log (table_name, last_refresh, record_count, category_breakdown)
                VALUES (%s, %s, %s, %s)
            """, ('prospects', now, prospect_count, '{}'))
            
            # Commit all changes
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating database with fresh data: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize PostgreSQL database with all necessary tables"""
        logger.info("🐘 Initializing PostgreSQL schema...")
        try:
            # First check if schema already exists (quick check)
            conn = self.get_connection()
            cursor = self.get_cursor(conn)
            
            # Quick test to see if members table exists (most critical table)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'members'
                );
            """)
            result = cursor.fetchone()
            # Handle both RealDictCursor and regular cursor results
            if hasattr(result, 'values'):
                # RealDictCursor returns dict-like object
                table_exists = list(result.values())[0]
            else:
                # Regular cursor returns tuple
                table_exists = result[0]
            conn.close()
            
            if table_exists:
                logger.info("✅ PostgreSQL schema already exists, skipping creation")
                return
            
            # If tables don't exist, try to create them with timeout
            logger.info("🏗️ Creating PostgreSQL schema (this may take a moment)...")
            from .database_migration import PostgreSQLMigrator
            migrator = PostgreSQLMigrator('', self.postgres_config)
            migrator.create_postgres_schema()
            logger.info("✅ PostgreSQL schema initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL schema initialization failed: {e}")
            logger.info("🔄 Continuing with existing schema (assuming tables exist)")
            # Don't raise - allow Flask to continue if schema exists

    def save_members_to_db(self, members: List[Dict[str, Any]]) -> bool:
        """Upsert members into the database with minimal required fields.
        Expects list of dicts that may come from ClubHub API; we map keys safely.
        Prevents duplicates by checking prospect_id first.
        """
        if not members:
            return False
        
        # Use timeout and isolation level to prevent concurrent transaction conflicts
        conn = self.get_connection()
        # Use regular cursor for INSERT operations to avoid RealDictCursor issues
        cursor = conn.cursor()
        
        # PostgreSQL connection established
        try:
            inserted_count = 0
            updated_count = 0
            
            for m in members:
                # Normalize keys from possible variants
                prospect_id = (
                    m.get('prospect_id') or m.get('prospectId') or m.get('clubos_member_id') or m.get('id')
                )
                
                # Skip if no prospect_id
                if not prospect_id:
                    continue
                    
                first_name = m.get('first_name') or m.get('firstName')
                last_name = m.get('last_name') or m.get('lastName')
                full_name = m.get('full_name') or (
                    f"{first_name or ''} {last_name or ''}".strip() if (first_name or last_name) else None
                )
                email = m.get('email')
                mobile_phone = m.get('mobile_phone') or m.get('mobilePhone') or m.get('phone')
                status = m.get('status')
                status_message = m.get('status_message') or m.get('statusMessage')
                member_type = m.get('member_type') or m.get('user_type') or m.get('memberType')
                amount_past_due = m.get('amount_past_due') or m.get('pastDueAmount') or 0
                date_of_next_payment = m.get('date_of_next_payment') or m.get('nextPaymentDate')

                # Check if member already exists by prospect_id (PostgreSQL)
                cursor.execute("SELECT id FROM members WHERE prospect_id = %s", (str(prospect_id),))
                existing_member = cursor.fetchone()
                
                if existing_member:
                    # Update existing member (PostgreSQL)
                    cursor.execute(
                        """
                        UPDATE members SET 
                            guid = %s, first_name = %s, last_name = %s, full_name = %s, email = %s, 
                            mobile_phone = %s, status = %s, status_message = %s, user_type = %s, 
                            amount_past_due = %s, base_amount_past_due = %s, missed_payments = %s, 
                            late_fees = %s, agreement_recurring_cost = %s, date_of_next_payment = %s, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE prospect_id = %s
                        """,
                        (
                            str(prospect_id),  # guid column (use same value as prospect_id)
                            first_name,
                            last_name,
                            full_name,
                            email,
                            mobile_phone,
                            status,
                            status_message,
                            member_type,  # Maps to user_type column
                            float(amount_past_due) if amount_past_due not in (None, '') else 0,
                            float(m.get('base_amount_past_due', 0)),
                            int(m.get('missed_payments', 0)),
                            float(m.get('late_fees', 0)),
                            float(m.get('agreement_recurring_cost', 0)),
                            date_of_next_payment,
                            str(prospect_id)  # WHERE condition
                        ),
                    )
                    updated_count += 1
                else:
                    # Insert new member (PostgreSQL)
                    cursor.execute(
                        """
                        INSERT INTO members (
                            prospect_id, guid, first_name, last_name, full_name, email, mobile_phone,
                            status, status_message, user_type, amount_past_due, base_amount_past_due, 
                            missed_payments, late_fees, agreement_recurring_cost, date_of_next_payment, 
                            created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """,
                        (
                            str(prospect_id),  # prospect_id column
                            str(prospect_id),  # guid column (use same value)
                            first_name,
                            last_name,
                            full_name,
                            email,
                            mobile_phone,
                            status,
                            status_message,
                            member_type,  # Maps to user_type column
                            float(amount_past_due) if amount_past_due not in (None, '') else 0,
                            float(m.get('base_amount_past_due', 0)),
                            int(m.get('missed_payments', 0)),
                            float(m.get('late_fees', 0)),
                            float(m.get('agreement_recurring_cost', 0)),
                            date_of_next_payment,
                        ),
                    )
                    inserted_count += 1
                
                # Also update the category classification based on amount_past_due
                if prospect_id:
                    # Use the same classification logic as clean_dashboard.py
                    status_message_lower = str(status_message or '').lower()
                    status_lower = str(status or '').lower()
                    past_due_amount = float(amount_past_due or 0)
                    
                    # Default category and status message
                    category = 'green'
                    updated_status_message = status_message
                    
                    # Past due members - ONLY if they have specific ClubHub status messages
                    if ('past due more than 30 days' in status_message_lower):
                        category = 'past_due'
                        updated_status_message = 'Past Due more than 30 days'
                    elif ('past due 6-30 days' in status_message_lower):
                        category = 'past_due'
                        updated_status_message = 'Past Due 6-30 days'
                    
                    # Staff members
                    elif ('staff' in status_message_lower or 'staff' in status_lower):
                        category = 'staff'
                    
                    # Comp members
                    elif ('comp' in status_message_lower or 'comp' in status_lower or 'free' in status_message_lower):
                        category = 'comp'
                    
                    # Pay per visit members
                    elif ('pay per visit' in status_message_lower or 'ppv' in status_message_lower):
                        category = 'ppv'
                    
                    # Inactive members
                    elif (any(inactive in status_message_lower for inactive in ['cancelled', 'cancel', 'expire', 'pending', 'suspended']) or
                          status_lower in ['inactive', 'suspended', 'cancelled']):
                        category = 'inactive'
                    
                    # Green members (in good standing) - default for active members
                    elif ('good standing' in status_message_lower or 'active' in status_lower or status_lower == 'active'):
                        category = 'green'
                    
                    # Insert/update member category (PostgreSQL UPSERT)
                    cursor.execute("""
                        INSERT INTO member_categories (member_id, category, status_message, full_name, classified_at)
                        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (member_id) DO UPDATE SET
                            category = EXCLUDED.category,
                            status_message = EXCLUDED.status_message,
                            classified_at = EXCLUDED.classified_at
                    """, (str(prospect_id), category, updated_status_message, full_name))
            
            conn.commit()
            logger.info(f"✅ Successfully processed {len(members)} members to database ({inserted_count} inserted, {updated_count} updated)")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving members to DB: {e}")
            logger.error(f"❌ Error details: {str(e)}")
            if hasattr(e, 'args') and e.args:
                logger.error(f"❌ Error args: {e.args}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_member_billing_info(self, member_id: str, member_data: Dict[str, Any]) -> bool:
        """Update billing information for a specific member."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Extract billing fields from member data
            amount_past_due = float(member_data.get('amount_past_due', 0))
            base_amount_past_due = float(member_data.get('base_amount_past_due', 0))
            late_fees = float(member_data.get('late_fees', 0))
            missed_payments = int(member_data.get('missed_payments', 0))
            date_of_next_payment = member_data.get('date_of_next_payment')
            status = member_data.get('status', '')
            status_message = member_data.get('status_message', '')
            
            # Update billing fields
            cursor.execute("""
                UPDATE members SET 
                    amount_past_due = %s,
                    base_amount_past_due = %s,
                    late_fees = %s,
                    missed_payments = %s,
                    date_of_next_payment = %s,
                    status = %s,
                    status_message = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE prospect_id = %s OR guid = %s
            """, (
                amount_past_due,
                base_amount_past_due, 
                late_fees,
                missed_payments,
                date_of_next_payment,
                status,
                status_message,
                member_id,
                member_id
            ))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.debug(f"✅ Updated billing info for member {member_id}")
                return True
            else:
                logger.warning(f"⚠️ No member found with ID {member_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating billing for member {member_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def save_prospects_to_db(self, prospects: List[Dict[str, Any]]) -> bool:
        """Upsert prospects into the database with minimal required fields.
        Expects list of dicts that may come from ClubHub API; we map keys safely.
        Prevents duplicates by checking prospect_id first.
        """
        if not prospects:
            return False
        conn = self.get_connection()
        # Use regular cursor for INSERT operations to avoid RealDictCursor issues
        cursor = conn.cursor()
        try:
            inserted_count = 0
            updated_count = 0
            
            for p in prospects:
                # Normalize keys from possible variants
                prospect_id = (
                    p.get('prospect_id') or p.get('prospectId') or p.get('id')
                )
                
                # Skip if no prospect_id
                if not prospect_id:
                    continue
                    
                first_name = p.get('first_name') or p.get('firstName')
                last_name = p.get('last_name') or p.get('lastName')
                full_name = p.get('full_name') or (
                    f"{first_name or ''} {last_name or ''}".strip() if (first_name or last_name) else None
                )
                email = p.get('email')
                phone = p.get('phone') or p.get('mobile_phone') or p.get('mobilePhone')
                status = p.get('status')
                prospect_type = p.get('prospect_type') or p.get('prospectType') or p.get('type')

                # Check if prospect already exists by prospect_id - use correct placeholders
                cursor.execute("SELECT id FROM prospects WHERE prospect_id = %s", (str(prospect_id),))
                existing_prospect = cursor.fetchone()
                
                if existing_prospect:
                    # Update existing prospect
                    cursor.execute(
                        """
                        UPDATE prospects SET 
                            first_name = %s, last_name = %s, full_name = %s, email = %s, 
                            phone = %s, status = %s, prospect_type = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE prospect_id = %s
                        """,
                        (
                            first_name,
                            last_name,
                            full_name,
                            email,
                            phone,
                            status,
                            prospect_type,
                            str(prospect_id)  # WHERE condition
                        ),
                    )
                    updated_count += 1
                else:
                    # Insert new prospect
                    cursor.execute(
                        """
                        INSERT INTO prospects (
                            prospect_id, first_name, last_name, full_name, email, phone,
                            status, prospect_type, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """,
                        (
                            str(prospect_id),  # prospect_id column
                            first_name,
                            last_name,
                            full_name,
                            email,
                            phone,
                            status,
                            prospect_type,
                        ),
                    )
                    inserted_count += 1
            
            conn.commit()
            logger.info(f"✅ Prospects saved to database: {inserted_count} inserted, {updated_count} updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving prospects to DB: {e}")
            logger.error(f"❌ Error details: {str(e)}")
            if hasattr(e, 'args') and e.args:
                logger.error(f"❌ Error args: {e.args}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an update/insert/delete query and return success status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Update execution failed: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_member_count(self) -> int:
        """Get total member count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM members")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error getting member count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_prospect_count(self) -> int:
        """Get total prospect count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM prospects")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error getting prospect count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_training_client_count(self) -> int:
        """Get total training client count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM training_clients")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"❌ Error getting training client count: {e}")
            return 0
        finally:
            conn.close()
    
    def get_recent_members(self, limit: int = 5) -> List[Dict]:
        """Get recent members for dashboard display"""
        query = """
            SELECT first_name, last_name, email, status 
            FROM members 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_recent_prospects(self, limit: int = 5) -> List[Dict]:
        """Get recent prospects for dashboard display"""
        query = """
            SELECT first_name, last_name, email, status 
            FROM prospects 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_members_by_category(self, category: str) -> List[Dict]:
        """Get members by category with enhanced logic for green members and revenue categories"""
        try:
            # 1) Try the fast path: member_categories
            query = """
                SELECT m.*
                FROM members m
                JOIN member_categories mc ON m.guid = mc.member_id OR m.prospect_id = mc.member_id
                WHERE mc.category = %s
                ORDER BY m.created_at DESC
            """
            results = self.execute_query(query, (category,))
            if results:
                logger.info(f"✅ Found {len(results)} {category} members from member_categories table")
                return results

            # 2) Enhanced DB heuristics with proper green member identification
            logger.info(f"No members in member_categories for '{category}', applying enhanced DB heuristics")
            
            if category == 'green':
                # Green members: "Member is in good standing" only
                query = """
                    SELECT * FROM members
                    WHERE status_message = 'Member is in good standing'
                    ORDER BY created_at DESC
                """
            elif category == 'past_due':
                # Yellow/Past Due: Multiple status messages (ClubHub lumps these together)
                query = """
                    SELECT * FROM members
                    WHERE status_message IN (
                        'Past Due 6-30 days',
                        'Invalid Billing Information.',
                        'Invalid/Bad Address information.',
                        'Member is pending cancel',
                        'Member will expire within 30 days.'
                    )
                    ORDER BY created_at DESC
                """
            elif category == 'red':
                # Red members: Past due more than 30 days, cancelled accounts
                query = """
                    SELECT * FROM members
                    WHERE status_message IN (
                        'Past Due more than 30 days.',
                        'Account has been cancelled.'
                    )
                    ORDER BY created_at DESC
                """
            elif category == 'comp':
                # Comp members: "Comp Member" exactly
                query = """
                    SELECT * FROM members
                    WHERE status_message = 'Comp Member'
                    ORDER BY created_at DESC
                """
            elif category == 'ppv':
                # PPV members: "Pay Per Visit Member" exactly
                query = """
                    SELECT * FROM members
                    WHERE status_message = 'Pay Per Visit Member'
                    ORDER BY created_at DESC
                """
            elif category == 'staff':
                # Staff members: Both variations
                query = """
                    SELECT * FROM members
                    WHERE status_message IN ('Staff Member', 'Staff member')
                    ORDER BY created_at DESC
                """
            elif category == 'frozen':
                # Frozen members
                query = """
                    SELECT * FROM members
                    WHERE status_message LIKE '%frozen%' OR status_message LIKE '%Frozen%'
                    ORDER BY created_at DESC
                """
            elif category == 'inactive':
                query = """
                    SELECT * FROM members
                    WHERE status IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled')
                    OR status_message LIKE '%cancelled%'
                    OR status_message LIKE '%expire%'
                    OR status_message LIKE '%suspended%'
                    ORDER BY created_at DESC
                """
            # NEW: Additional revenue-generating categories
            elif category == 'expiring_soon':
                # Members expiring within 30 days (still revenue-generating until expiry)
                query = """
                    SELECT * FROM members
                    WHERE agreement_end_date IS NOT NULL 
                    AND date(agreement_end_date) BETWEEN date('now') AND date('now', '+30 days')
                    AND COALESCE(amount_past_due, 0) = 0
                    ORDER BY agreement_end_date ASC
                """
            elif category == 'billing_issues':
                # Members with invalid billing info but still active (still should pay)
                query = """
                    SELECT * FROM members
                    WHERE (status_message LIKE '%billing%' OR status_message LIKE '%payment%')
                    AND status_message NOT LIKE '%Past Due%'
                    AND (status NOT IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled') OR status IS NULL)
                    ORDER BY created_at DESC
                """
            elif category == 'address_issues':
                # Members with invalid/bad address but still active
                query = """
                    SELECT * FROM members
                    WHERE (status_message LIKE '%address%' OR status_message LIKE '%contact%')
                    AND status_message NOT LIKE '%Past Due%'
                    AND (status NOT IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled') OR status IS NULL)
                    ORDER BY created_at DESC
                """
            else:
                return []

            db_results = self.execute_query(query)
            if db_results:
                logger.info(f"✅ Found {len(db_results)} {category} members using DB heuristics")
                return db_results

            # 3) Enhanced fallback: filter in-memory cache with better green member logic
            try:
                app_cache = current_app.data_cache if hasattr(current_app, 'data_cache') else {}
                cached = app_cache.get('members') or []
            except Exception:
                cached = []

            if not cached:
                logger.info(f"⚠️ No cached data available for {category} members")
                return []

            def norm(m: Dict[str, Any]) -> Dict[str, Any]:
                # Normalize keys for cache entries
                first = m.get('first_name') or m.get('firstName')
                last = m.get('last_name') or m.get('lastName')
                full = m.get('full_name') or m.get('fullName') or (f"{first or ''} {last or ''}".strip() or None)
                return {
                    'prospect_id': str(m.get('prospect_id') or m.get('prospectId') or m.get('clubos_member_id') or m.get('id') or ''),
                    'id': m.get('id'),
                    'guid': m.get('guid'),
                    'first_name': first,
                    'last_name': last,
                    'full_name': full,
                    'email': m.get('email'),
                    'mobile_phone': m.get('mobile_phone') or m.get('mobilePhone') or m.get('phone'),
                    'status': m.get('status'),
                    'status_message': m.get('status_message') or m.get('statusMessage'),
                    'member_type': m.get('member_type') or m.get('user_type') or m.get('memberType'),
                    'amount_past_due': float(m.get('amount_past_due') or m.get('pastDueAmount') or 0),
                    'agreement_recurring_cost': float(m.get('agreement_recurring_cost', 0)),
                    'date_of_next_payment': m.get('date_of_next_payment') or m.get('nextPaymentDate'),
                }

            def matches(cat: str, m: Dict[str, Any]) -> bool:
                s = (m.get('status') or '').lower()
                sm = (m.get('status_message') or '').lower()
                mt = (m.get('member_type') or '').lower()
                apd = float(m.get('amount_past_due') or 0)
                em = (m.get('email') or '').lower()
                
                if cat == 'green':
                    # Enhanced green member criteria - exclude all non-revenue generating types
                    return (apd <= 0 and 
                           s not in ['inactive','suspended','cancelled'] and
                           'comp' not in sm and 'comp' not in mt and
                           'staff' not in sm and 'staff' not in mt and
                           'per visit' not in sm and 'ppv' not in sm and 'ppv' not in mt and
                           'past due' not in sm and
                           'anytimefitness' not in em)
                elif cat == 'past_due':
                    return apd > 0 or 'past due' in sm
                elif cat == 'comp':
                    return ('comp' in sm) or ('free' in sm) or ('comp' in mt)
                elif cat == 'ppv':
                    return ('per visit' in sm) or ('ppv' in sm) or ('ppv' in mt)
                elif cat == 'staff':
                    return ('staff' in sm) or ('staff' in mt) or ('anytimefitness' in em)
                elif cat == 'inactive':
                    return s in ['inactive','suspended','cancelled']
                return False

            filtered = [norm(m) for m in cached if matches(category, norm(m))]
            logger.info(f"✅ Found {len(filtered)} {category} members from cache filtering")
            return filtered
            
        except Exception as e:
            logger.error(f"Error getting members by category '{category}': {e}")
            return []
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get counts of members by exact status messages to match ClubHub categorization"""
        try:
            # Count members by their exact status messages from ClubHub
            counts: Dict[str, int] = {}

            # GREEN MEMBERS: "Member is in good standing" (308 expected)
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message = 'Member is in good standing'
                """
            )
            counts['green'] = result[0]['count'] if result else 0

            # YELLOW/PAST DUE MEMBERS: Multiple status messages (22 expected)
            # - Past Due 6-30 days: 8 
            # - Invalid billing: 2
            # - Invalid address: 3
            # - Member pending cancel: 4
            # - Member will expire in 30 days: 5
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message IN (
                    'Past Due 6-30 days',
                    'Invalid Billing Information.',
                    'Invalid/Bad Address information.',
                    'Member is pending cancel',
                    'Member will expire within 30 days.'
                )
                """
            )
            counts['past_due'] = result[0]['count'] if result else 0

            # RED MEMBERS: Multiple status messages (17 expected)  
            # - Past Due more than 30 days: 16
            # - Account has been cancelled: 1
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message IN (
                    'Past Due more than 30 days.',
                    'Account has been cancelled.'
                )
                """
            )
            counts['red'] = result[0]['count'] if result else 0

            # FROZEN MEMBERS (3 expected) - Need to check if we have any
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message LIKE '%frozen%' OR status_message LIKE '%Frozen%'
                """
            )
            counts['frozen'] = result[0]['count'] if result else 0

            # COMP MEMBERS: "Comp Member" (31 expected, but we have 32)
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message = 'Comp Member'
                """
            )
            counts['comp'] = result[0]['count'] if result else 0

            # PPV MEMBERS: "Pay Per Visit Member" (116 expected)
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message = 'Pay Per Visit Member'
                """
            )
            counts['ppv'] = result[0]['count'] if result else 0

            # STAFF MEMBERS: Only the 5 specific staff accounts by their exact prospect IDs
            # Jeremy Mayo: 64309309, Natoya Thomas: 55867562, Mike Beal: 50909888, Staff Two: 62716557, Joseph Jones: 52750389
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE prospect_id IN ('64309309', '55867562', '50909888', '62716557', '52750389')
                """
            )
            counts['staff'] = result[0]['count'] if result else 0

            # INACTIVE MEMBERS: Expired, NULL status, etc.
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message IN ('Expired') OR status_message IS NULL
                """
            )
            counts['inactive'] = result[0]['count'] if result else 0

            logger.info(f"✅ ClubHub-matched category counts: {counts}")

            # 3) Enhanced cache-based counting if DB counts are all zero
            if sum(counts.values()) == 0:
                try:
                    app_cache = current_app.data_cache if hasattr(current_app, 'data_cache') else {}
                    cached = app_cache.get('members') or []
                except Exception:
                    cached = []

                if cached:
                    def tally(cat: str) -> int:
                        total = 0
                        for m in cached:
                            first = m.get('first_name') or m.get('firstName')
                            last = m.get('last_name') or m.get('lastName')
                            full = m.get('full_name') or m.get('fullName') or (f"{first or ''} {last or ''}".strip() or None)
                            nm = {
                                'status': (m.get('status') or '').lower(),
                                'status_message': (m.get('status_message') or m.get('statusMessage') or '').lower(),
                                'member_type': (m.get('member_type') or m.get('user_type') or m.get('memberType') or '').lower(),
                                'amount_past_due': float(m.get('amount_past_due') or m.get('pastDueAmount') or 0),
                                'email': (m.get('email') or '').lower(),
                                'first_name': first, 'last_name': last, 'full_name': full,
                            }
                            
                            if cat == 'green':
                                # Enhanced green criteria - exclude non-revenue generating types
                                if (nm['amount_past_due'] <= 0 and 
                                   nm['status'] not in ['inactive','suspended','cancelled'] and
                                   'comp' not in nm['status_message'] and 'comp' not in nm['member_type'] and
                                   'staff' not in nm['status_message'] and 'staff' not in nm['member_type'] and
                                   'per visit' not in nm['status_message'] and 'ppv' not in nm['status_message'] and 'ppv' not in nm['member_type'] and
                                   'past due' not in nm['status_message'] and
                                   'anytimefitness' not in nm['email']):
                                    total += 1
                            elif cat == 'past_due':
                                if nm['amount_past_due'] > 0 or 'past due' in nm['status_message']:
                                    total += 1
                            elif cat == 'comp':
                                if ('comp' in nm['status_message']) or ('free' in nm['status_message']) or ('comp' in nm['member_type']):
                                    total += 1
                            elif cat == 'ppv':
                                if ('per visit' in nm['status_message']) or ('ppv' in nm['status_message']) or ('ppv' in nm['member_type']):
                                    total += 1
                            elif cat == 'staff':
                                if ('staff' in nm['status_message']) or ('staff' in nm['member_type']) or ('anytimefitness' in nm['email']):
                                    total += 1
                            elif cat == 'inactive':
                                if nm['status'] in ['inactive','suspended','cancelled']:
                                    total += 1
                        return total

                    for cat in ['green','comp','ppv','staff','past_due','inactive']:
                        counts[cat] = tally(cat)
                        
                    logger.info(f"✅ Cache-based counts: {counts}")

            return counts
            
        except Exception as e:
            logger.error(f"Error getting category counts: {e}")
            return {}
    
    def update_member_category(self, member_id: str, category: str, status_message: str = None, status: str = None):
        """Update or insert member category classification"""
        query = """
            INSERT INTO member_categories 
            (member_id, category, status_message, status, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (member_id) DO UPDATE SET
                category = EXCLUDED.category,
                status_message = EXCLUDED.status_message,
                status = EXCLUDED.status,
                updated_at = EXCLUDED.updated_at
        """
        return self.execute_update(query, (member_id, category, status_message, status, datetime.now()))
    
    def lookup_member_name_by_email(self, email: str) -> str:
        """Look up proper member name (first + last) from database using email"""
        try:
            # First check members table
            query = """
                SELECT first_name, last_name, full_name FROM members 
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
            """
            results = self.execute_query(query, (email,))
            
            if results:
                member = results[0]
                # Prefer full_name if available, otherwise construct from first + last
                if member.get('full_name'):
                    return member['full_name']
                elif member.get('first_name') or member.get('last_name'):
                    return f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
            
            # Fallback: check prospects table
            query = """
                SELECT first_name, last_name, full_name FROM prospects 
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
            """
            results = self.execute_query(query, (email,))
            
            if results:
                prospect = results[0]
                if prospect.get('full_name'):
                    return prospect['full_name']
                elif prospect.get('first_name') or prospect.get('last_name'):
                    return f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip()
            
            # No match found
            return None
            
        except Exception as e:
            logger.error(f"❌ Error looking up member name by email: {e}")
            return None
    
    def get_training_clients_with_agreements(self) -> List[Dict]:
        """Get training clients with their agreement information and corrected past due amounts"""
        try:
            import json
            query = """
                SELECT tc.*, m.email as member_email, m.mobile_phone, m.status_message
                FROM training_clients tc
                LEFT JOIN members m ON tc.member_id = m.guid
                ORDER BY tc.first_name, tc.last_name
            """
            clients = self.execute_query(query)
            
            # Handle None result from execute_query
            if clients is None:
                logger.info("ℹ️ No training clients found in database")
                return []
            
            # Fix past due amounts from package_details JSON using CORRECT ClubOS API structure
            for client in clients:
                try:
                    actual_past_due = 0.0
                    
                    # Method 1: Check if package_details contains billing status data
                    if client.get('package_details'):
                        package_details_str = client['package_details']
                        
                        # Skip empty arrays
                        if package_details_str and package_details_str != '[]':
                            package_details = json.loads(package_details_str)
                            
                            if isinstance(package_details, list) and package_details:
                                for package in package_details:
                                    if isinstance(package, dict):
                                        # Priority 1: Check for amount_owed field (ClubOS integration stores this)
                                        amount_owed = package.get('amount_owed', 0) or 0
                                        if isinstance(amount_owed, (int, float)) and amount_owed > 0:
                                            actual_past_due += float(amount_owed)
                                            logger.debug(f"📊 Found amount_owed: ${amount_owed} for {client.get('member_name')}")
                                        
                                        # Priority 2: Only check billing_status if no amount_owed was found
                                        elif 'billing_status' in package:
                                            billing_status = package['billing_status']
                                            if isinstance(billing_status, dict) and 'past' in billing_status:
                                                past_items = billing_status['past']
                                                if isinstance(past_items, list):
                                                    for item in past_items:
                                                        if isinstance(item, dict) and 'amount' in item:
                                                            past_amount = float(item.get('amount', 0))
                                                            actual_past_due += past_amount
                                                            logger.debug(f"📊 Found billing past due: ${past_amount} for {client.get('member_name')}")
                            
                            elif isinstance(package_details, dict):
                                # If package_details is a single object instead of array
                                amount_owed = package_details.get('amount_owed', 0) or 0
                                if isinstance(amount_owed, (int, float)) and amount_owed > 0:
                                    actual_past_due += float(amount_owed)
                                    logger.debug(f"📊 Found single amount_owed: ${amount_owed} for {client.get('member_name')}")
                                
                                # Only check billing_status if no amount_owed was found
                                elif 'billing_status' in package_details:
                                    billing_status = package_details['billing_status']
                                    if isinstance(billing_status, dict) and 'past' in billing_status:
                                        past_items = billing_status['past']
                                        if isinstance(past_items, list):
                                            for item in past_items:
                                                if isinstance(item, dict) and 'amount' in item:
                                                    past_amount = float(item.get('amount', 0))
                                                    actual_past_due += past_amount
                                                    logger.debug(f"📊 Found single billing past due: ${past_amount} for {client.get('member_name')}")
                    
                    # Method 2: Fallback to existing past_due_amount field if no package_details
                    if actual_past_due == 0.0 and client.get('past_due_amount'):
                        past_due_db = client.get('past_due_amount', 0.0)
                        if isinstance(past_due_db, (int, float)) and past_due_db > 0:
                            actual_past_due = float(past_due_db)
                            logger.debug(f"📊 Using DB past_due_amount: ${actual_past_due} for {client.get('member_name')}")
                    
                    # Update the client record with correct past due amount
                    client['actual_past_due'] = actual_past_due
                    client['amount_owed'] = actual_past_due  # For template compatibility
                    client['has_past_due'] = actual_past_due > 0
                    
                    # Log the final result for debugging
                    if actual_past_due > 0:
                        logger.info(f"💰 {client.get('member_name', 'Unknown')}: ${actual_past_due:.2f} past due")
                    
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    logger.warning(f"⚠️ Error parsing package_details for {client.get('member_name', 'unknown')}: {e}")
                    # Fallback to existing past_due_amount
                    fallback_amount = client.get('past_due_amount', 0.0)
                    client['actual_past_due'] = float(fallback_amount) if fallback_amount else 0.0
                    client['amount_owed'] = client['actual_past_due']  # For template compatibility
                    client['has_past_due'] = client['actual_past_due'] > 0
            
            return clients
            
        except Exception as e:
            logger.error(f"❌ Error getting training clients with agreements: {e}")
            return []
    
    def classify_member_status_enhanced(self, member_data: Dict[str, Any]) -> str:
        """Enhanced member classification based on clean dashboard logic"""
        # Ensure status_message and status are strings, handle None/NoneType values
        status_message = str(member_data.get('statusMessage', member_data.get('status_message', ''))).lower()
        status = str(member_data.get('status', '')).lower()
        member_type = str(member_data.get('memberType', member_data.get('member_type', ''))).lower()
        amount_past_due = float(member_data.get('amount_past_due', member_data.get('pastDueAmount', 0)))
        
        # Past due members (highest priority)
        if ('past due more than 30' in status_message or 
            'delinquent' in status_message or 
            amount_past_due > 100):
            return 'past_due_red'
        elif ('past due 6-30' in status_message or 
              'past due' in status_message or 
              'overdue' in status_message or
              (amount_past_due > 0 and amount_past_due <= 100)):
            return 'past_due_yellow'
        
        # Staff members
        if ('staff' in status_message or 'staff' in status or 'staff' in member_type):
            return 'staff'
        
        # Comp members
        if ('comp' in status_message or 'comp' in status or 'free' in status_message):
            return 'comp'
        
        # Pay per visit members
        if ('pay per visit' in status_message or 'ppv' in status_message):
            return 'ppv'
        
        # Training clients
        if ('training' in status_message or 'personal' in status_message or 'training' in member_type):
            return 'training'
        
        # Inactive members
        if (any(inactive in status_message for inactive in ['cancelled', 'cancel', 'expire', 'pending', 'suspended']) or
              status in ['inactive', 'suspended', 'cancelled']):
            return 'inactive'
        
        # Green members (in good standing) - default
        if ('good standing' in status_message or 'active' in status or status == 'active'):
            return 'green'
        
        # Default to green if unclear
        return 'green'

    def save_training_clients_to_db(self, training_clients: List[Dict[str, Any]]) -> bool:
        """Upsert training clients into the database with enhanced agreement data.
        Expects list of dicts from ClubOS integration with package and payment details.
        """
        if not training_clients:
            return False
            
        # Use PostgreSQL connection
        conn = self.get_connection()
        cursor = self.get_cursor(conn)
        
        try:
            inserted_count = 0
            updated_count = 0
            
            for tc in training_clients:
                # Extract all the enhanced data from ClubOS integration
                member_id = tc.get('member_id') or tc.get('clubos_member_id') or tc.get('id')
                clubos_member_id = tc.get('clubos_member_id') or member_id
                
                # Skip if no member_id
                if not member_id:
                    logger.warning(f"⚠️ Skipping training client with no member_id: {tc}")
                    continue
                    
                # Basic info
                first_name = tc.get('first_name', '')
                last_name = tc.get('last_name', '')
                full_name = tc.get('full_name') or tc.get('member_name') or f"{first_name} {last_name}".strip()
                member_name = tc.get('member_name') or full_name
                email = tc.get('email', '')
                phone = tc.get('phone', '')
                status = tc.get('status', 'Active')
                
                # Training info
                trainer_name = tc.get('trainer_name', 'Jeremy Mayo')
                membership_type = tc.get('membership_type', 'Personal Training')
                source = tc.get('source', 'clubos_assignees_with_agreements')
                
                # Package data
                active_packages = tc.get('active_packages', [])
                package_summary = tc.get('package_summary', '')
                package_details = tc.get('package_details', [])
                
                # Financial data
                past_due_amount = float(tc.get('past_due_amount', 0.0))
                total_past_due = float(tc.get('total_past_due', 0.0))
                payment_status = tc.get('payment_status', 'Current')
                sessions_remaining = int(tc.get('sessions_remaining', 0))
                last_session = tc.get('last_session', 'See ClubOS')
                financial_summary = tc.get('financial_summary', 'Current')
                last_updated = tc.get('last_updated', '')
                
                # Convert complex data to JSON strings for storage
                import json
                active_packages_json = json.dumps(active_packages) if active_packages else '[]'
                package_details_json = json.dumps(package_details) if package_details else '[]'
                
                # Check if training client already exists by member_id
                cursor.execute("SELECT id FROM training_clients WHERE member_id = %s OR clubos_member_id = %s", 
                             (str(member_id), str(clubos_member_id)))
                existing_client = cursor.fetchone()
                
                if existing_client:
                    # Update existing training client with all enhanced data
                    cursor.execute("""
                        UPDATE training_clients SET 
                            member_id = %s, clubos_member_id = %s, first_name = %s, last_name = %s, 
                            member_name = %s, email = %s, phone = %s,
                            trainer_name = %s, membership_type = %s, source = %s,
                            active_packages = %s, package_summary = %s, package_details = %s,
                            past_due_amount = %s, total_past_due = %s, payment_status = %s,
                            sessions_remaining = %s, last_session = %s, financial_summary = %s,
                            last_updated = %s
                        WHERE id = %s
                    """, (
                        str(member_id), str(clubos_member_id), first_name, last_name,
                        member_name, email, phone,
                        trainer_name, membership_type, source,
                        active_packages_json, package_summary, package_details_json,
                        past_due_amount, total_past_due, payment_status,
                        sessions_remaining, last_session, financial_summary,
                        last_updated, existing_client[0]
                    ))
                    updated_count += 1
                else:
                    # Insert new training client with all enhanced data
                    cursor.execute("""
                        INSERT INTO training_clients (
                            member_id, clubos_member_id, first_name, last_name, member_name,
                            email, phone, trainer_name, membership_type, source,
                            active_packages, package_summary, package_details,
                            past_due_amount, total_past_due, payment_status,
                            sessions_remaining, last_session, financial_summary,
                            last_updated, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                NOW())
                    """, (
                        str(member_id), str(clubos_member_id), first_name, last_name, member_name,
                        email, phone, trainer_name, membership_type, source,
                        active_packages_json, package_summary, package_details_json,
                        past_due_amount, total_past_due, payment_status,
                        sessions_remaining, last_session, financial_summary,
                        last_updated
                    ))
                    inserted_count += 1
            
            conn.commit()
            logger.info(f"✅ Training clients database: {inserted_count} inserted, {updated_count} updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save training clients: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            self.close_connection(conn)

    def log_data_refresh(self, table_name: str, record_count: int, category_breakdown: Dict = None):
        """Log data refresh operation"""
        try:
            category_json = json.dumps(category_breakdown) if category_breakdown else '{}'
            
            # Check if table_name already exists in log using execute_query
            existing = self.execute_query("SELECT id FROM data_refresh_log WHERE table_name = %s", 
                                        (table_name,), fetch_one=True)
            
            if existing:
                # Update existing record
                self.execute_query("""
                    UPDATE data_refresh_log 
                    SET last_refresh = NOW(), record_count = %s, category_breakdown = %s
                    WHERE table_name = %s
                """, (record_count, category_json, table_name))
            else:
                # Insert new record
                self.execute_query("""
                    INSERT INTO data_refresh_log (table_name, last_refresh, record_count, category_breakdown)
                    VALUES (%s, NOW(), %s, %s)
                """, (table_name, record_count, category_json))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error logging data refresh: {e}")
            return False
    
    def fetch_and_store_real_clubos_messages(self, limit=20):
        """Fetch real messages from ClubOS and store them in the database"""
        try:
            logger.info("🔄 Fetching real ClubOS messages...")
            
            # Try to get messages from ClubOS API using the enhanced service
            try:
                from .api.enhanced_clubos_service import ClubOSAPIService
                from .authentication.secure_secrets_manager import SecureSecretsManager
                
                secrets_manager = SecureSecretsManager()
                username = secrets_manager.get_secret('clubos-username')
                password = secrets_manager.get_secret('clubos-password')
                
                if not username or not password:
                    logger.warning("⚠️ ClubOS credentials not found, using sample messages")
                    return self._create_sample_messages()
                
                # Initialize ClubOS API service
                clubos_service = ClubOSAPIService(username, password)
                
                # Get the last message sender (most recent conversation)
                recent_sender = clubos_service.get_last_message_sender()
                
                messages = []
                if recent_sender:
                    logger.info(f"✅ Found recent sender: {recent_sender}")
                    # Get conversation for the recent sender
                    try:
                        conversation = clubos_service.scrape_conversation_for_contact(recent_sender)
                        
                        if conversation and len(conversation) > 0:
                            for i, msg in enumerate(conversation[-limit:]):
                                message_data = {
                                    'id': f"clubos_{recent_sender.replace(' ', '_')}_{i}",
                                    'member_name': recent_sender,
                                    'message_content': msg.get('content', 'No message content'),
                                    'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                                    'sender_type': 'member' if msg.get('sender') != 'j.mayo' else 'staff',
                                    'channel': 'ClubOS',
                                    'status': 'received' if msg.get('sender') != 'j.mayo' else 'sent',
                                    'unread': msg.get('sender') != 'j.mayo' and i >= len(conversation) - 5  # Mark last 5 from members as unread
                                }
                                messages.append(message_data)
                        else:
                            logger.warning(f"⚠️ No conversation history found for {recent_sender}, using sample messages")
                            # Create a sample message from this real sender
                            messages.append({
                                'id': f"real_sender_{recent_sender.replace(' ', '_')}",
                                'member_name': recent_sender,
                                'message_content': f"Hi! This is a recent message from {recent_sender} (detected via ClubOS)",
                                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                                'sender_type': 'member',
                                'channel': 'ClubOS',
                                'status': 'received',
                                'unread': True
                            })
                    except Exception as conv_error:
                        logger.warning(f"⚠️ Error getting conversation for {recent_sender}: {conv_error}")
                        # Create a sample message from this real sender anyway
                        messages.append({
                            'id': f"real_sender_{recent_sender.replace(' ', '_')}",
                            'member_name': recent_sender,
                            'message_content': f"Hi! This is a recent message from {recent_sender} (detected via ClubOS)",
                            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                            'sender_type': 'member',
                            'channel': 'ClubOS',
                            'status': 'received',
                            'unread': True
                        })
                
                # If no messages from API, create sample messages
                if not messages:
                    messages = self._create_sample_messages()
                    
            except Exception as api_error:
                logger.warning(f"⚠️ ClubOS API error: {api_error}, using sample messages")
                messages = self._create_sample_messages()
            
            # Store messages in database
            self._store_messages_in_database(messages)
            
            logger.info(f"✅ Stored {len(messages)} messages in database")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error fetching ClubOS messages: {e}")
            return self._create_sample_messages()
    
    def _create_sample_messages(self):
        """Create sample message data for testing"""
        sample_messages = [
            {
                'id': 'sample_1',
                'member_name': 'Sarah Johnson',
                'message_content': 'Hi! I wanted to ask about changing my training schedule. Can we move my Tuesday session to Thursday?',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'sender_type': 'member',
                'channel': 'ClubOS',
                'status': 'received',
                'unread': True
            },
            {
                'id': 'sample_2', 
                'member_name': 'Mike Chen',
                'message_content': 'Thanks for the great workout today! Looking forward to next week.',
                'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                'sender_type': 'member',
                'channel': 'ClubOS',
                'status': 'received',
                'unread': True
            },
            {
                'id': 'sample_3',
                'member_name': 'Emily Rodriguez',
                'message_content': 'I need to cancel tomorrow\'s session due to a family emergency. Can we reschedule?',
                'timestamp': (datetime.now() - timedelta(hours=12)).isoformat(),
                'sender_type': 'member',
                'channel': 'ClubOS',
                'status': 'received',
                'unread': False
            },
            {
                'id': 'sample_4',
                'member_name': 'David Martinez',
                'message_content': 'Quick question about my training package - how many sessions do I have left?',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'sender_type': 'member',
                'channel': 'ClubOS',
                'status': 'received',
                'unread': False
            },
            {
                'id': 'sample_5',
                'member_name': 'Lisa Thompson',
                'message_content': 'Just wanted to say thank you for helping me reach my fitness goals! The progress has been amazing.',
                'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
                'sender_type': 'member',
                'channel': 'ClubOS',
                'status': 'received',
                'unread': False
            }
        ]
        return sample_messages
    
    def _store_messages_in_database(self, messages):
        """Store messages in the database"""
        conn = self.get_connection()
        cursor = self.get_cursor(conn)
        
        try:
            # Ensure messages table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    message_type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    from_user TEXT,
                    to_user TEXT,
                    status TEXT,
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_status TEXT DEFAULT 'received',
                    campaign_id TEXT,
                    channel TEXT DEFAULT 'clubos',
                    member_id TEXT,
                    message_actions TEXT,
                    is_confirmation BOOLEAN DEFAULT FALSE,
                    is_opt_in BOOLEAN DEFAULT FALSE,
                    is_opt_out BOOLEAN DEFAULT FALSE,
                    has_emoji BOOLEAN DEFAULT FALSE,
                    emoji_reactions TEXT,
                    conversation_id TEXT,
                    thread_id TEXT
                )
            """)
            
            # Clear existing sample messages
            cursor.execute("DELETE FROM messages WHERE id LIKE 'sample_%%' OR id LIKE 'clubos_%%'")
            # Insert new messages
            for msg in messages:
                cursor.execute("""
                    INSERT INTO messages (
                        id, content, timestamp, from_user, status, delivery_status,
                        channel, member_id, conversation_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        timestamp = EXCLUDED.timestamp,
                        delivery_status = EXCLUDED.delivery_status
                """, (
                    msg['id'],
                    msg['message_content'],
                    msg['timestamp'],
                    msg['member_name'],
                    msg['status'],
                    'unread' if msg['unread'] else 'read',
                    msg['channel'],
                    msg['member_name'].replace(' ', '_'),
                    f"conv_{msg['member_name'].replace(' ', '_')}"
                ))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error storing messages: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def _ensure_messages_table_exists(self, cursor):
        """Helper method to ensure messages table exists"""
        if self.db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    message_type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    from_user TEXT,
                    to_user TEXT,
                    status TEXT,
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_status TEXT DEFAULT 'received',
                    campaign_id TEXT,
                    channel TEXT DEFAULT 'clubos',
                    member_id TEXT,
                    message_actions TEXT,
                    is_confirmation BOOLEAN DEFAULT FALSE,
                    is_opt_in BOOLEAN DEFAULT FALSE,
                    is_opt_out BOOLEAN DEFAULT FALSE,
                    has_emoji BOOLEAN DEFAULT FALSE,
                    emoji_reactions TEXT,
                    conversation_id TEXT,
                    thread_id TEXT
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    message_type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    from_user TEXT,
                    to_user TEXT,
                    status TEXT,
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_status TEXT DEFAULT 'received',
                    campaign_id TEXT,
                    channel TEXT DEFAULT 'clubos',
                    member_id TEXT,
                    message_actions TEXT,
                    is_confirmation BOOLEAN DEFAULT FALSE,
                    is_opt_in BOOLEAN DEFAULT FALSE,
                    is_opt_out BOOLEAN DEFAULT FALSE,
                    has_emoji BOOLEAN DEFAULT FALSE,
                    emoji_reactions TEXT,
                    conversation_id TEXT,
                    thread_id TEXT
                )
            """)
    
    def get_recent_message_threads(self, limit=10):
        """Get recent message threads with latest message and unread status"""
        # Only fetch ClubOS messages if not recently fetched (cache for 5 minutes)
        try:
            cache_key = 'last_clubos_message_fetch'
            last_fetch = getattr(self, cache_key, None)
            current_time = datetime.now()
            
            if not last_fetch or (current_time - last_fetch).total_seconds() > 300:  # 5 minutes
                self.fetch_and_store_real_clubos_messages(limit * 2)  # Fetch more to have variety
                setattr(self, cache_key, current_time)
            else:
                logger.info(f"ℹ️ Using cached ClubOS messages (last fetch: {(current_time - last_fetch).total_seconds():.0f}s ago)")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch real ClubOS messages: {e}")
        
        conn = self.get_connection()
        cursor = self.get_cursor(conn)
        
        try:
            # Ensure messages table exists
            self._ensure_messages_table_exists(cursor)
            
            # Check if we have any messages at all
            cursor.execute("SELECT COUNT(*) as count FROM messages")
            
            count_result = cursor.fetchone()
            message_count = 0
            
            if count_result:
                if hasattr(count_result, 'keys'):
                    message_count = count_result.get('count', 0) or count_result.get('COUNT(*)', 0)
                else:
                    message_count = count_result[0] if len(count_result) > 0 else 0
            
            logger.info(f"📊 Found {message_count} total messages in database")
            
            if message_count == 0:
                logger.info("ℹ️ No messages in database, returning empty threads")
                return []
            
            # Simple query to get all messages, then group them in Python (more reliable)
            cursor.execute("""
                SELECT id, content, timestamp, from_user, status, delivery_status,
                       channel, member_id, conversation_id
                FROM messages
                ORDER BY timestamp DESC
                LIMIT %s
            """, (limit * 5,))  # Get more messages to have variety
            
            # Fetch all recent messages
            all_messages = cursor.fetchall()
            logger.info(f"📬 Retrieved {len(all_messages)} messages from database")
            
            # Group messages by member/conversation in Python (more reliable than complex SQL)
            conversation_groups = {}
            
            for msg in all_messages:
                try:
                    # Handle RealDictRow vs tuple access
                    if hasattr(msg, 'keys'):
                        member_name = msg.get('from_user') or msg.get('member_id') or 'Unknown'
                        content = msg.get('content', 'No content')
                        timestamp = msg.get('timestamp')
                        status = msg.get('status', 'sent')
                        delivery_status = msg.get('delivery_status', 'read')
                        channel = msg.get('channel', 'ClubOS')
                        conversation_id = msg.get('conversation_id', f"conv_{member_name.replace(' ', '_')}")
                    else:
                        member_name = msg[3] if len(msg) > 3 else 'Unknown'  # from_user
                        content = msg[1] if len(msg) > 1 else 'No content'   # content
                        timestamp = msg[2] if len(msg) > 2 else datetime.now().isoformat()  # timestamp
                        status = msg[4] if len(msg) > 4 else 'sent'  # status
                        delivery_status = msg[5] if len(msg) > 5 else 'read'  # delivery_status
                        channel = msg[6] if len(msg) > 6 else 'ClubOS'  # channel
                        conversation_id = msg[8] if len(msg) > 8 else f"conv_{member_name.replace(' ', '_')}"  # conversation_id
                    
                    # Skip empty member names
                    if not member_name or member_name.strip() == '':
                        continue
                    
                    # Group by conversation
                    conv_key = f"{member_name}_{conversation_id}"
                    
                    if conv_key not in conversation_groups:
                        conversation_groups[conv_key] = {
                            'member_name': member_name,
                            'conversation_id': conversation_id,
                            'channel': channel,
                            'messages': [],
                            'unread_count': 0,
                            'latest_timestamp': timestamp
                        }
                    
                    conversation_groups[conv_key]['messages'].append({
                        'content': content,
                        'timestamp': timestamp,
                        'sender': member_name,
                        'status': status
                    })
                    
                    # Count unread messages
                    if status == 'received' and delivery_status == 'unread':
                        conversation_groups[conv_key]['unread_count'] += 1
                    
                    # Update latest timestamp
                    if timestamp > conversation_groups[conv_key]['latest_timestamp']:
                        conversation_groups[conv_key]['latest_timestamp'] = timestamp
                        
                except Exception as msg_error:
                    logger.warning(f"⚠️ Error processing message: {msg_error}")
                    continue
            
            # Convert to thread format and sort
            threads = []
            for conv_key, conv_data in conversation_groups.items():
                try:
                    member_name = conv_data['member_name']
                    
                    # Skip threads where the "member" is actually staff (j.mayo)
                    if member_name == 'j.mayo':
                        continue
                    
                    # Find the most recent member message (not staff response)
                    latest_member_msg = None
                    latest_overall_msg = None
                    
                    for msg in conv_data['messages']:
                        if not latest_overall_msg:
                            latest_overall_msg = msg
                        
                        # Look for the most recent message from the actual member (not staff)
                        if msg['sender'] != 'j.mayo' and not latest_member_msg:
                            latest_member_msg = msg
                    
                    # Use member message if available, otherwise use the latest overall message
                    display_msg = latest_member_msg if latest_member_msg else latest_overall_msg
                    
                    if not display_msg:
                        continue
                    
                    thread = {
                        'id': conv_data['conversation_id'],
                        'member_id': hash(member_name) % 1000000,
                        'member_name': member_name,
                        'member_full_name': member_name,
                        'member_email': f"{member_name.lower().replace(' ', '.')}@gym.com",
                        'thread_type': conv_data['channel'].lower() if conv_data['channel'] else 'clubos',
                        'thread_subject': f"Conversation with {member_name}",
                        'status': 'active',
                        'last_message_at': display_msg['timestamp'],
                        'latest_message': {
                            'message_content': display_msg['content'],
                            'created_at': display_msg['timestamp'],
                            'sender_type': 'member' if display_msg['sender'] != 'j.mayo' else 'staff',
                            'status': display_msg['status']
                        },
                        'unread_count': conv_data['unread_count']
                    }
                    threads.append(thread)
                    
                except Exception as thread_error:
                    logger.warning(f"⚠️ Error creating thread: {thread_error}")
                    continue
            
            # Sort by unread count (desc) then by timestamp (desc)
            threads.sort(key=lambda t: (t['unread_count'], t['last_message_at']), reverse=True)
            
            # Limit results
            threads = threads[:limit]
            
            logger.info(f"✅ Created {len(threads)} conversation threads")
            
            return threads
            
        except Exception as e:
            logger.error(f"❌ Error getting recent message threads: {e}")
            return []
        finally:
            conn.close()
    
    def get_thread_messages(self, member_id, limit=50):
        """Get all messages for a specific member across all their threads"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Find member name from member_id hash
            cursor.execute("""
                SELECT DISTINCT 
                    COALESCE(member_id, from_user, to_user) as member_name,
                    conversation_id,
                    channel
                FROM messages
                WHERE ABS(EXTRACT(EPOCH FROM timestamp)::INTEGER) % 1000000 = %s
                ORDER BY timestamp DESC
            """, (member_id,))
            
            member_info = cursor.fetchone()
            if not member_info:
                return []
            
            member_name = member_info[0]
            
            # Get all messages for this member
            cursor.execute("""
                SELECT 
                    id, content, from_user, to_user, status, timestamp, 
                    message_type, channel, conversation_id
                FROM messages
                WHERE (member_id = %s OR from_user = %s OR to_user = %s)
                ORDER BY timestamp ASC
                LIMIT %s
            """, (member_name, member_name, member_name, limit))
            
            messages = []
            for msg_row in cursor.fetchall():
                message = {
                    'id': msg_row[0],
                    'message_content': msg_row[1],
                    'sender_type': 'member' if msg_row[2] != 'j.mayo' else 'staff',
                    'sender_name': msg_row[2] or 'Unknown',
                    'direction': 'inbound' if msg_row[2] != 'j.mayo' else 'outbound',
                    'status': msg_row[4],
                    'created_at': msg_row[5],
                    'message_type': msg_row[6] or 'text',
                    'thread_type': msg_row[7] or 'system'
                }
                messages.append(message)
            
            # Return in thread format expected by the template
            threads = [{
                'thread_id': 1,
                'thread_type': member_info[2] or 'system',
                'thread_subject': f"Conversation with {member_name}",
                'status': 'active',
                'messages': messages
            }]
            
            return threads
            
        except Exception as e:
            logger.error(f"❌ Error getting thread messages for member {member_id}: {e}")
            return []
        finally:
            conn.close()
    
    def get_monthly_revenue_calculation(self) -> Dict[str, float]:
        """Calculate monthly revenue only from active members (excluding comp, staff, PPV, past due, inactive)"""
        try:
            import json
            # Only ACTIVE members generate monthly revenue
            # Active = Not (past due OR PPV OR inactive OR frozen OR comp OR staff)
            
            # MEMBER REVENUE: Only "Member is in good standing" (active paying members)
            member_revenue_query = """
                SELECT 
                    COALESCE(SUM(agreement_recurring_cost), 0) as member_revenue,
                    COUNT(*) as revenue_members
                FROM members
                WHERE status_message = 'Member is in good standing'
                AND COALESCE(agreement_recurring_cost, 0) > 0
            """
            
            member_result = self.execute_query(member_revenue_query)
            member_revenue = float(member_result[0]['member_revenue']) if member_result else 0.0
            revenue_members_count = int(member_result[0]['revenue_members']) if member_result else 0
            
            # TRAINING CLIENT REVENUE: Extract recurring fees from package_details JSON
            training_clients = self.execute_query("""
                SELECT package_details, payment_status
                FROM training_clients
                WHERE package_details IS NOT NULL AND package_details != ''
            """)
            
            training_revenue = 0.0
            training_clients_count = len(training_clients)
            
            for client in training_clients:
                try:
                    if client['package_details']:
                        # Parse package_details JSON to extract monthly recurring amounts
                        package_details = json.loads(client['package_details'])
                        if isinstance(package_details, list):
                            for package in package_details:
                                if isinstance(package, dict):
                                    # Look for recurring payment amount fields
                                    recurring_amount = (
                                        package.get('recurring_amount', 0) or
                                        package.get('monthly_amount', 0) or
                                        package.get('payment_amount', 0) or
                                        0
                                    )
                                    if isinstance(recurring_amount, (int, float)) and recurring_amount > 0:
                                        training_revenue += float(recurring_amount)
                                    # Also check for estimated monthly based on payment schedule
                                    elif package.get('scheduled_payments_count', 0) > 0 and package.get('invoice_count', 0) > 0:
                                        # Estimate monthly payment based on payment schedule
                                        total_paid = package.get('total_paid', 0) or 0
                                        if total_paid > 0 and package.get('invoice_count', 0) > 0:
                                            estimated_monthly = float(total_paid) / max(1, package.get('invoice_count', 1))
                                            if estimated_monthly > 0:
                                                training_revenue += estimated_monthly
                except (json.JSONDecodeError, TypeError, KeyError) as e:
                    logger.warning(f"⚠️ Error parsing package_details for training client: {e}")
                    continue
            
            # TOTAL MONTHLY REVENUE
            total_monthly_revenue = member_revenue + training_revenue
            
            logger.info(f"💰 Monthly Revenue Calculation:")
            logger.info(f"   Member Revenue: ${member_revenue:.2f} from {revenue_members_count} members")
            logger.info(f"   Training Revenue: ${training_revenue:.2f} from {training_clients_count} clients")
            logger.info(f"   Total Monthly Revenue: ${total_monthly_revenue:.2f}")
            
            return {
                'member_revenue': member_revenue,
                'training_revenue': training_revenue,
                'total_monthly_revenue': total_monthly_revenue,
                'revenue_members_count': revenue_members_count,
                'training_clients_count': training_clients_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating monthly revenue: {e}")
            return {
                'member_revenue': 0.0,
                'training_revenue': 0.0,
                'total_monthly_revenue': 0.0,
                'revenue_members_count': 0,
                'training_clients_count': 0
            }

    def add_sample_message_data(self):
        """Add some sample message data for testing the inbox"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Ensure messages table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    message_type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    from_user TEXT,
                    to_user TEXT,
                    status TEXT,
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_status TEXT DEFAULT 'received',
                    campaign_id TEXT,
                    channel TEXT DEFAULT 'clubos',
                    member_id TEXT,
                    message_actions TEXT,
                    is_confirmation BOOLEAN DEFAULT FALSE,
                    is_opt_in BOOLEAN DEFAULT FALSE,
                    is_opt_out BOOLEAN DEFAULT FALSE,
                    has_emoji BOOLEAN DEFAULT FALSE,
                    emoji_reactions TEXT,
                    conversation_id TEXT,
                    thread_id TEXT
                )
            """)
            
            # Get some member names from training clients or create sample ones
            cursor.execute("SELECT member_name FROM training_clients LIMIT 5")
            existing_members = cursor.fetchall()
            
            sample_conversations = []
            if existing_members:
                for member_row in existing_members[:3]:
                    member_name = member_row[0]
                    conv_id = f"conv_{hash(member_name) % 10000}"
                    
                    sample_conversations.extend([
                        {
                            'id': f"{conv_id}_1",
                            'content': f"Hi, this is {member_name}. I have a question about my training schedule.",
                            'from_user': member_name,
                            'to_user': 'j.mayo',
                            'member_id': member_name,
                            'conversation_id': conv_id,
                            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                            'status': 'received'
                        },
                        {
                            'id': f"{conv_id}_2", 
                            'content': f"Hi {member_name}! I'd be happy to help with your training schedule. What specifically would you like to know?",
                            'from_user': 'j.mayo',
                            'to_user': member_name,
                            'member_id': member_name,
                            'conversation_id': conv_id,
                            'timestamp': (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                            'status': 'sent'
                        }
                    ])
            else:
                # Create default sample data
                sample_conversations = [
                    {
                        'id': 'sample_1',
                        'content': 'Hi, I have a question about my payment schedule',
                        'from_user': 'Jessica Williams',
                        'to_user': 'j.mayo',
                        'member_id': 'Jessica Williams',
                        'conversation_id': 'conv_jessica',
                        'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
                        'status': 'received'
                    },
                    {
                        'id': 'sample_2',
                        'content': 'Can I reschedule my session for tomorrow?',
                        'from_user': 'David Thompson',
                        'to_user': 'j.mayo',
                        'member_id': 'David Thompson',
                        'conversation_id': 'conv_david',
                        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                        'status': 'received'
                    }
                ]
            
            # Insert sample messages
            for msg in sample_conversations:
                cursor.execute("""
                    INSERT INTO messages 
                    (id, message_type, content, timestamp, from_user, to_user, status, owner_id,
                     delivery_status, channel, member_id, conversation_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        timestamp = EXCLUDED.timestamp,
                        status = EXCLUDED.status
                """, (
                    msg['id'],
                    'text',
                    msg['content'],
                    msg['timestamp'],
                    msg['from_user'],
                    msg['to_user'],
                    msg['status'],
                    '187032782',
                    msg['status'],
                    'clubos',
                    msg['member_id'],
                    msg['conversation_id']
                ))
            
            conn.commit()
            logger.info(f"✅ Added {len(sample_conversations)} sample messages to database")
            
        except Exception as e:
            logger.error(f"❌ Error adding sample message data: {e}")
        finally:
            conn.close()
    
    def save_invoice(self, invoice_data: Dict[str, Any]) -> bool:
        """Save Square invoice data to database"""
        try:
            query = """
                INSERT INTO invoices 
                (member_id, square_invoice_id, amount, status, payment_method, 
                 delivery_method, due_date, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (square_invoice_id) DO UPDATE SET
                    amount = EXCLUDED.amount,
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            params = (
                invoice_data.get('member_id'),
                invoice_data.get('square_invoice_id'),
                invoice_data.get('amount'),
                invoice_data.get('status', 'sent'),
                invoice_data.get('payment_method'),
                invoice_data.get('delivery_method'),
                invoice_data.get('due_date'),
                invoice_data.get('notes')
            )
            return self.execute_query(query, params) is not None
        except Exception as e:
            logger.error(f"❌ Error saving invoice: {e}")
            return False
    
    def get_member_invoices(self, member_id: str) -> List[Dict]:
        """Get all invoices for a specific member"""
        try:
            query = """
                SELECT * FROM invoices 
                WHERE member_id = %s 
                ORDER BY created_at DESC
            """
            return self.execute_query(query, (member_id,))
        except Exception as e:
            logger.error(f"❌ Error getting member invoices: {e}")
            return []
    
    def update_invoice_status(self, square_invoice_id: str, status: str, payment_date: str = None, square_payment_id: str = None) -> bool:
        """Update invoice status (e.g., when payment is received)"""
        try:
            query = """
                UPDATE invoices 
                SET status = %s, payment_date = %s, square_payment_id = %s, updated_at = CURRENT_TIMESTAMP
                WHERE square_invoice_id = %s
            """
            params = (status, payment_date, square_payment_id, square_invoice_id)
            return self.execute_query(query, params) is not None
        except Exception as e:
            logger.error(f"❌ Error updating invoice status: {e}")
            return False
    
    def get_pending_invoices(self) -> List[Dict]:
        """Get all pending invoices (sent but not paid)"""
        try:
            query = """
                SELECT * FROM invoices 
                WHERE status = 'sent' 
                ORDER BY created_at DESC
            """
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"❌ Error getting pending invoices: {e}")
            return []
