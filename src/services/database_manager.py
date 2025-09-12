#!/usr/bin/env python3
"""
Database Manager Service
Handles all database operations, schema management, and data refresh logic
"""

import os
import sqlite3
import pandas as pd
import logging
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from flask import current_app

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced Database Manager to handle comprehensive gym data with auto-refresh"""
    
    def __init__(self, db_path='gym_bot.db'):
        self.db_path = db_path
        self.last_refresh = None
        self.refresh_interval = 3600  # 1 hour in seconds
        self.init_database()
        
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
            from clubos_fresh_data_api import ClubOSFreshDataAPI
            
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update members with fresh data
            # This would process the fresh_data and update the database
            # For now, we'll update the last_refresh timestamp
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_refresh_log (
                    id INTEGER PRIMARY KEY,
                    table_name TEXT,
                    last_refresh TIMESTAMP,
                    record_count INTEGER,
                    category_breakdown TEXT
                )
            """)
            
            # Log the refresh
            cursor.execute("""
                INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count, category_breakdown)
                VALUES (1, 'members', ?, (SELECT COUNT(*) FROM members), '{}')
            """, (datetime.now(),))
            
            cursor.execute("""
                INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count, category_breakdown)
                VALUES (2, 'prospects', ?, (SELECT COUNT(*) FROM prospects), '{}')
            """, (datetime.now(),))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating database with fresh data: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # --- Lightweight migration helpers ---
            def table_info(name: str):
                cursor.execute(f"PRAGMA table_info({name})")
                return [row[1] for row in cursor.fetchall()]

            def ensure_column(table: str, column_def_sql: str, column_name: str):
                cols = table_info(table)
                if column_name not in cols:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def_sql}")

            # Create members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY,
                    prospect_id TEXT UNIQUE,
                    guid TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    mobile_phone TEXT,
                    status TEXT,
                    status_message TEXT,
                    member_type TEXT,
                    user_type TEXT,
                    join_date TEXT,
                    amount_past_due REAL,
                    date_of_next_payment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration: ensure prospect_id exists on members
            ensure_column('members', 'prospect_id TEXT', 'prospect_id')
            # Migration: ensure guid exists for member profile lookups
            ensure_column('members', 'guid TEXT', 'guid')
            # Migration: ensure user_type exists (maps from member_type)
            ensure_column('members', 'user_type TEXT', 'user_type')
            # Migration: ensure mobile_phone exists (templates reference it)
            ensure_column('members', 'mobile_phone TEXT', 'mobile_phone')
            # Migration: ensure legacy phone column exists for compatibility
            ensure_column('members', 'phone TEXT', 'phone')
            
            # Create prospects table
            # Create prospects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prospect_id TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    status TEXT,
                    prospect_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration: ensure prospect_id exists on prospects
            ensure_column('prospects', 'prospect_id TEXT', 'prospect_id')
            
            # Create training_clients table with enhanced package data support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_clients (
                    id INTEGER PRIMARY KEY,
                    member_id TEXT,
                    clubos_member_id TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    member_name TEXT,
                    email TEXT,
                    phone TEXT,
                    status TEXT,
                    training_package TEXT,
                    trainer_name TEXT,
                    membership_type TEXT,
                    source TEXT,
                    active_packages TEXT,
                    package_summary TEXT,
                    package_details TEXT,
                    past_due_amount REAL DEFAULT 0.0,
                    total_past_due REAL DEFAULT 0.0,
                    payment_status TEXT,
                    sessions_remaining INTEGER DEFAULT 0,
                    last_session TEXT,
                    financial_summary TEXT,
                    last_updated TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create member_categories table for fast member classification
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_categories (
                    id INTEGER PRIMARY KEY,
                    member_id TEXT UNIQUE,
                    category TEXT,
                    status_message TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members (prospect_id)
                )
            """)
            
            # Create data_refresh_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_refresh_log (
                    table_name TEXT,
                    last_refresh TIMESTAMP,
                    record_count INTEGER,
                    category_breakdown TEXT
                )
            """)
            
            # Create funding_status_cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS funding_status_cache (
                    id INTEGER PRIMARY KEY,
                    member_name TEXT,
                    member_email TEXT,
                    member_id TEXT,
                    funding_status TEXT,
                    package_details TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cache_expiry TIMESTAMP
                )
            """)
            
            # Create events table for calendar functionality
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    location TEXT,
                    is_all_day BOOLEAN DEFAULT FALSE,
                    is_training_session BOOLEAN DEFAULT FALSE,
                    participants TEXT,
                    participant_emails TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate existing database by adding missing columns if they don't exist
            try:
                # Add phone column to prospects table if missing
                cursor.execute("PRAGMA table_info(prospects)")
                prospects_columns = [row[1] for row in cursor.fetchall()]
                if 'phone' not in prospects_columns:
                    cursor.execute("ALTER TABLE prospects ADD COLUMN phone TEXT")
                    logger.info("✅ Added missing 'phone' column to prospects table")
                if 'prospect_type' not in prospects_columns:
                    cursor.execute("ALTER TABLE prospects ADD COLUMN prospect_type TEXT")
                    logger.info("✅ Added missing 'prospect_type' column to prospects table")
                if 'status' not in prospects_columns:
                    cursor.execute("ALTER TABLE prospects ADD COLUMN status TEXT")
                    logger.info("✅ Added missing 'status' column to prospects table")
                
                # Migrate training_clients table to add enhanced package data columns
                cursor.execute("PRAGMA table_info(training_clients)")
                training_columns = [row[1] for row in cursor.fetchall()]
                
                training_column_migrations = [
                    ('clubos_member_id', 'TEXT'),
                    ('member_name', 'TEXT'),
                    ('trainer_name', 'TEXT'),
                    ('membership_type', 'TEXT'),
                    ('source', 'TEXT'),
                    ('active_packages', 'TEXT'),
                    ('package_summary', 'TEXT'),
                    ('package_details', 'TEXT'),
                    ('past_due_amount', 'REAL DEFAULT 0.0'),
                    ('total_past_due', 'REAL DEFAULT 0.0'),
                    ('payment_status', 'TEXT'),
                    ('sessions_remaining', 'INTEGER DEFAULT 0'),
                    ('last_session', 'TEXT'),
                    ('financial_summary', 'TEXT'),
                    ('last_updated', 'TIMESTAMP')
                ]
                
                for column_name, column_type in training_column_migrations:
                    if column_name not in training_columns:
                        cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {column_name} {column_type}")
                        logger.info(f"✅ Added missing '{column_name}' column to training_clients table")
                        
            except Exception as migrate_error:
                logger.warning(f"⚠️  Database migration warning: {migrate_error}")

            # Create indexes for better performance and add unique constraints
            # Guard index creation only if column exists to avoid errors on legacy DBs
            if 'prospect_id' in table_info('members'):
                # Create unique index on prospect_id to prevent duplicates
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_members_prospect_id_unique ON members(prospect_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)")
            if 'prospect_id' in table_info('prospects'):
                # Create unique index on prospect_id to prevent duplicates  
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_prospects_prospect_id_unique ON prospects(prospect_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_clients_member_id ON training_clients(member_id)")
            # Make member_categories.member_id unique to prevent duplicates
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_member_categories_member_id_unique ON member_categories(member_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_member_categories_category ON member_categories(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_funding_cache_member_name ON funding_status_cache(member_name)")
            
            conn.commit()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            conn.rollback()
        finally:
            conn.close()

    def save_members_to_db(self, members: List[Dict[str, Any]]) -> bool:
        """Upsert members into the database with minimal required fields.
        Expects list of dicts that may come from ClubHub API; we map keys safely.
        Prevents duplicates by checking prospect_id first.
        """
        if not members:
            return False
        
        # Use timeout and isolation level to prevent concurrent transaction conflicts
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level='IMMEDIATE')
        cursor = conn.cursor()
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

                # Check if member already exists by prospect_id
                cursor.execute("SELECT id FROM members WHERE prospect_id = ?", (str(prospect_id),))
                existing_member = cursor.fetchone()
                
                if existing_member:
                    # Update existing member
                    cursor.execute(
                        """
                        UPDATE members SET 
                            guid = ?, first_name = ?, last_name = ?, full_name = ?, email = ?, 
                            mobile_phone = ?, status = ?, status_message = ?, user_type = ?, 
                            amount_past_due = ?, base_amount_past_due = ?, missed_payments = ?, 
                            late_fees = ?, agreement_recurring_cost = ?, date_of_next_payment = ?, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE prospect_id = ?
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
                    # Insert new member
                    cursor.execute(
                        """
                        INSERT INTO members (
                            prospect_id, guid, first_name, last_name, full_name, email, mobile_phone,
                            status, status_message, user_type, amount_past_due, base_amount_past_due, 
                            missed_payments, late_fees, agreement_recurring_cost, date_of_next_payment, 
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
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
                    
                    # Insert/update member category (also prevent duplicates here)
                    cursor.execute("SELECT member_id FROM member_categories WHERE member_id = ?", (str(prospect_id),))
                    if cursor.fetchone():
                        # Update existing category
                        cursor.execute("""
                            UPDATE member_categories 
                            SET category = ?, status_message = ?, classified_at = CURRENT_TIMESTAMP
                            WHERE member_id = ?
                        """, (category, updated_status_message, str(prospect_id)))
                    else:
                        # Insert new category
                        cursor.execute("""
                            INSERT INTO member_categories 
                            (member_id, category, status_message, full_name, classified_at)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
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
    
    def save_prospects_to_db(self, prospects: List[Dict[str, Any]]) -> bool:
        """Upsert prospects into the database with minimal required fields.
        Expects list of dicts that may come from ClubHub API; we map keys safely.
        Prevents duplicates by checking prospect_id first.
        """
        if not prospects:
            return False
        conn = self.get_connection()
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

                # Check if prospect already exists by prospect_id
                cursor.execute("SELECT id FROM prospects WHERE prospect_id = ?", (str(prospect_id),))
                existing_prospect = cursor.fetchone()
                
                if existing_prospect:
                    # Update existing prospect
                    cursor.execute(
                        """
                        UPDATE prospects SET 
                            first_name = ?, last_name = ?, full_name = ?, email = ?, 
                            phone = ?, status = ?, prospect_type = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE prospect_id = ?
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
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
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
    
    def get_connection(self):
        """Get a database connection with proper row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results as list of dictionaries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return []
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
            LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_recent_prospects(self, limit: int = 5) -> List[Dict]:
        """Get recent prospects for dashboard display"""
        query = """
            SELECT first_name, last_name, email, status 
            FROM prospects 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_members_by_category(self, category: str) -> List[Dict]:
        """Get members by category with fallback logic"""
        try:
            # 1) Try the fast path: member_categories
            query = """
                SELECT m.*
                FROM members m
                JOIN member_categories mc ON m.guid = mc.member_id
                WHERE mc.category = ?
                ORDER BY m.created_at DESC
            """
            results = self.execute_query(query, (category,))
            if results:
                return results

            # 2) Broader DB heuristics if member_categories is empty
            logger.info(f"No members in member_categories for '{category}', applying DB heuristics")
            if category == 'green':
                # Consider members with no past due as green regardless of status label
                query = """
                    SELECT * FROM members
                    WHERE COALESCE(amount_past_due, 0) <= 0
                    AND (status NOT IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled') OR status IS NULL)
                    ORDER BY created_at DESC
                """
            elif category == 'past_due':
                query = """
                    SELECT * FROM members
                    WHERE (status_message LIKE '%Past Due 6-30 days%' 
                    OR status_message LIKE '%Past Due more than 30 days%')
                    ORDER BY amount_past_due DESC, created_at DESC
                """
            elif category == 'comp':
                query = """
                    SELECT * FROM members
                    WHERE (status_message LIKE '%comp%' OR status_message LIKE '%free%')
                    OR (user_type LIKE '%comp%')
                    ORDER BY created_at DESC
                """
            elif category == 'ppv':
                query = """
                    SELECT * FROM members
                    WHERE (status_message LIKE '%per visit%' OR status_message LIKE '%ppv%')
                    OR (user_type LIKE '%ppv%')
                    ORDER BY created_at DESC
                """
            elif category == 'staff':
                query = """
                    SELECT * FROM members
                    WHERE (status_message LIKE '%staff%' OR user_type LIKE '%staff%')
                    OR (email LIKE '%anytimefitness%')
                    ORDER BY created_at DESC
                """
            elif category == 'inactive':
                query = """
                    SELECT * FROM members
                    WHERE status IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled')
                    ORDER BY created_at DESC
                """
            else:
                return []

            db_results = self.execute_query(query)
            if db_results:
                return db_results

            # 3) Final fallback: filter in-memory cache if available
            try:
                app_cache = current_app.data_cache if hasattr(current_app, 'data_cache') else {}
                cached = app_cache.get('members') or []
            except Exception:
                cached = []

            if not cached:
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
                    'date_of_next_payment': m.get('date_of_next_payment') or m.get('nextPaymentDate'),
                }

            def matches(cat: str, m: Dict[str, Any]) -> bool:
                s = (m.get('status') or '').lower()
                sm = (m.get('status_message') or '').lower()
                mt = (m.get('member_type') or '').lower()
                apd = float(m.get('amount_past_due') or 0)
                em = (m.get('email') or '').lower()
                if cat == 'green':
                    return apd <= 0 and s not in ['inactive','suspended','cancelled']
                if cat == 'past_due':
                    return apd > 0 or 'past due' in sm
                if cat == 'comp':
                    return ('comp' in sm) or ('free' in sm) or ('comp' in mt)
                if cat == 'ppv':
                    return ('per visit' in sm) or ('ppv' in sm) or ('ppv' in mt)
                if cat == 'staff':
                    return ('staff' in sm) or ('staff' in mt) or ('anytimefitness' in em)
                if cat == 'inactive':
                    return s in ['inactive','suspended','cancelled']
                return False

            filtered = [norm(m) for m in cached if matches(category, norm(m))]
            return filtered
            
        except Exception as e:
            logger.error(f"Error getting members by category '{category}': {e}")
            return []
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get counts of members in each category with fallback logic"""
        try:
            # 1) Prefer counts from member_categories if present
            query = """
                SELECT category, COUNT(*) as count
                FROM member_categories
                GROUP BY category
            """
            results = self.execute_query(query)
            category_counts = {row['category']: row['count'] for row in results}
            if category_counts:
                return category_counts

            # 2) Dynamic DB counts with broader heuristics
            counts: Dict[str, int] = {}

            # Green
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE COALESCE(amount_past_due, 0) <= 0
                AND (status NOT IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled') OR status IS NULL)
                """
            )
            counts['green'] = result[0]['count'] if result else 0

            # Past due
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE (status_message LIKE '%Past Due 6-30 days%' 
                OR status_message LIKE '%Past Due more than 30 days%'
                """
            )
            counts['past_due'] = result[0]['count'] if result else 0

            # Comp
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message LIKE '%comp%' OR status_message LIKE '%free%' OR user_type LIKE '%comp%'
                """
            )
            counts['comp'] = result[0]['count'] if result else 0

            # PPV
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message LIKE '%per visit%' OR status_message LIKE '%ppv%' OR user_type LIKE '%ppv%'
                """
            )
            counts['ppv'] = result[0]['count'] if result else 0

            # Staff
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status_message LIKE '%staff%' OR user_type LIKE '%staff%' OR email LIKE '%anytimefitness%'
                """
            )
            counts['staff'] = result[0]['count'] if result else 0

            # Inactive
            result = self.execute_query(
                """
                SELECT COUNT(*) as count FROM members
                WHERE status IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled')
                """
            )
            counts['inactive'] = result[0]['count'] if result else 0

            # 3) If everything is zero, try cache-based counts
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
                                'status': m.get('status'),
                                'status_message': m.get('status_message') or m.get('statusMessage'),
                                'member_type': m.get('member_type') or m.get('user_type') or m.get('memberType'),
                                'amount_past_due': float(m.get('amount_past_due') or m.get('pastDueAmount') or 0),
                                'email': m.get('email'),
                                'first_name': first, 'last_name': last, 'full_name': full,
                            }
                            if ((cat == 'green' and nm['amount_past_due'] <= 0 and (nm['status'] or '').lower() not in ['inactive','suspended','cancelled']) or
                                (cat == 'past_due' and (nm['amount_past_due'] > 0 or 'past due' in (nm['status_message'] or '').lower())) or
                                (cat == 'comp' and (('comp' in (nm['status_message'] or '').lower()) or ('free' in (nm['status_message'] or '').lower()) or ('comp' in (nm['member_type'] or '').lower()))) or
                                (cat == 'ppv' and (('per visit' in (nm['status_message'] or '').lower()) or ('ppv' in (nm['status_message'] or '').lower()) or ('ppv' in (nm['member_type'] or '').lower()))) or
                                (cat == 'staff' and (('staff' in (nm['status_message'] or '').lower()) or ('staff' in (nm['member_type'] or '').lower()) or ('anytimefitness' in (nm['email'] or '').lower()))) or
                                (cat == 'inactive' and (nm['status'] or '').lower() in ['inactive','suspended','cancelled'])):
                                total += 1
                        return total

                    for cat in ['green','comp','ppv','staff','past_due','inactive']:
                        counts[cat] = tally(cat)

            return counts
            
        except Exception as e:
            logger.error(f"Error getting category counts: {e}")
            return {}
    
    def update_member_category(self, member_id: str, category: str, status_message: str = None, status: str = None):
        """Update or insert member category classification"""
        query = """
            INSERT OR REPLACE INTO member_categories 
            (member_id, category, status_message, status, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (member_id, category, status_message, status, datetime.now()))
    
    def lookup_member_name_by_email(self, email: str) -> str:
        """Look up proper member name (first + last) from database using email"""
        try:
            # First check members table
            query = """
                SELECT first_name, last_name, full_name FROM members 
                WHERE LOWER(email) = LOWER(?)
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
                WHERE LOWER(email) = LOWER(?)
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
        """Get training clients with their agreement information"""
        try:
            query = """
                SELECT tc.*, m.email as member_email, m.mobile_phone, m.status_message
                FROM training_clients tc
                LEFT JOIN members m ON tc.member_id = m.guid
                ORDER BY tc.first_name, tc.last_name
            """
            return self.execute_query(query)
            
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
            
        # Use the enhanced transaction isolation to prevent concurrent conflicts
        conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level='IMMEDIATE')
        cursor = conn.cursor()
        
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
                cursor.execute("SELECT id FROM training_clients WHERE member_id = ? OR clubos_member_id = ?", 
                             (str(member_id), str(clubos_member_id)))
                existing_client = cursor.fetchone()
                
                if existing_client:
                    # Update existing training client with all enhanced data
                    cursor.execute("""
                        UPDATE training_clients SET 
                            member_id = ?, clubos_member_id = ?, first_name = ?, last_name = ?, 
                            member_name = ?, email = ?, phone = ?,
                            trainer_name = ?, membership_type = ?, source = ?,
                            active_packages = ?, package_summary = ?, package_details = ?,
                            past_due_amount = ?, total_past_due = ?, payment_status = ?,
                            sessions_remaining = ?, last_session = ?, financial_summary = ?,
                            last_updated = ?
                        WHERE id = ?
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
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                CURRENT_TIMESTAMP)
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
            conn.close()

    def log_data_refresh(self, table_name: str, record_count: int, category_breakdown: Dict = None):
        """Log data refresh operation"""
        category_json = json.dumps(category_breakdown) if category_breakdown else '{}'
        
        # Check if table_name already exists in log
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM data_refresh_log WHERE table_name = ?", (table_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE data_refresh_log 
                    SET last_refresh = ?, record_count = ?, category_breakdown = ?
                    WHERE table_name = ?
                """, (datetime.now(), record_count, category_json, table_name))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO data_refresh_log (table_name, last_refresh, record_count, category_breakdown)
                    VALUES (?, ?, ?, ?)
                """, (table_name, datetime.now(), record_count, category_json))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error logging data refresh: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_recent_message_threads(self, limit=10):
        """Get recent message threads with latest message and unread status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if messages table exists, create if not
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
            
            # Get recent conversations grouped by member/conversation
            cursor.execute("""
                SELECT DISTINCT
                    COALESCE(member_id, from_user, to_user) as member_name,
                    conversation_id,
                    channel,
                    MAX(timestamp) as last_message_time,
                    COUNT(*) as message_count,
                    SUM(CASE WHEN status = 'received' AND delivery_status != 'read' THEN 1 ELSE 0 END) as unread_count
                FROM messages
                WHERE owner_id = '187032782'
                GROUP BY COALESCE(member_id, from_user, to_user), conversation_id
                ORDER BY 
                    SUM(CASE WHEN status = 'received' AND delivery_status != 'read' THEN 1 ELSE 0 END) DESC,
                    MAX(timestamp) DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            threads = []
            
            for row in rows:
                # Get the latest message for this thread
                cursor.execute("""
                    SELECT content, timestamp, from_user, status
                    FROM messages 
                    WHERE (member_id = ? OR from_user = ? OR to_user = ?)
                    AND conversation_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (row[0], row[0], row[0], row[1]))
                
                latest_msg = cursor.fetchone()
                
                thread = {
                    'id': row[1] or f"conv_{hash(row[0])}",
                    'member_id': hash(row[0]) % 1000000,  # Generate numeric ID
                    'member_name': row[0] or 'Unknown',
                    'member_full_name': row[0] or 'Unknown',
                    'member_email': f"{row[0].lower().replace(' ', '.')}@gym.com" if row[0] else '',
                    'thread_type': row[2] or 'system',
                    'thread_subject': f"Conversation with {row[0]}" if row[0] else 'System Message',
                    'status': 'active',
                    'last_message_at': row[3],
                    'latest_message': {
                        'message_content': latest_msg[0] if latest_msg else 'No messages',
                        'created_at': latest_msg[1] if latest_msg else row[3],
                        'sender_type': 'member' if latest_msg and latest_msg[2] != 'j.mayo' else 'staff',
                        'status': latest_msg[3] if latest_msg else 'sent'
                    } if latest_msg else None,
                    'unread_count': row[5] or 0
                }
                threads.append(thread)
            
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
                WHERE ABS(hash(COALESCE(member_id, from_user, to_user))) % 1000000 = ?
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
                WHERE (member_id = ? OR from_user = ? OR to_user = ?)
                ORDER BY timestamp ASC
                LIMIT ?
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
                    INSERT OR REPLACE INTO messages 
                    (id, message_type, content, timestamp, from_user, to_user, status, owner_id,
                     delivery_status, channel, member_id, conversation_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
