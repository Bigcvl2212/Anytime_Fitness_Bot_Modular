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
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get existing table info to check what columns exist
            def table_info(table_name):
                try:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    return [row[1] for row in cursor.fetchall()]
                except:
                    return []
            
            # Create members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY,
                    prospect_id TEXT UNIQUE,
                    guid TEXT UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    mobile_phone TEXT,
                    phone TEXT,
                    status TEXT,
                    status_message TEXT,
                    member_type TEXT,
                    user_type TEXT,
                    amount_past_due REAL DEFAULT 0.0,
                    next_payment_date TEXT,
                    next_payment_amount REAL DEFAULT 0.0,
                    address1 TEXT,
                    city TEXT,
                    state TEXT,
                    zip TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create prospects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id INTEGER PRIMARY KEY,
                    prospect_id TEXT UNIQUE,
                    guid TEXT UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    mobile_phone TEXT,
                    phone TEXT,
                    status TEXT,
                    status_message TEXT,
                    lead_source TEXT,
                    interest_level TEXT,
                    follow_up_date TEXT,
                    address1 TEXT,
                    city TEXT,
                    state TEXT,
                    zip TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create training_clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_clients (
                    id INTEGER PRIMARY KEY,
                    clubos_member_id TEXT,
                    member_id TEXT,
                    member_name TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    status TEXT,
                    trainer_name TEXT,
                    training_package TEXT,
                    active_packages TEXT,
                    past_due_amount REAL DEFAULT 0.0,
                    total_past_due REAL DEFAULT 0.0,
                    payment_status TEXT DEFAULT 'Current',
                    sessions_remaining INTEGER DEFAULT 0,
                    last_session TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if we need to migrate the existing training_clients table
            existing_columns = table_info('training_clients')
            required_columns = [
                'clubos_member_id', 'member_name', 'first_name', 'last_name', 
                'trainer_name', 'active_packages', 'past_due_amount', 'total_past_due', 
                'payment_status', 'sessions_remaining', 'last_session', 'last_updated'
            ]
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                logger.info(f"🔄 Migrating training_clients table to add missing columns: {missing_columns}")
                
                for column in missing_columns:
                    try:
                        if column in ['past_due_amount', 'total_past_due']:
                            cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {column} REAL DEFAULT 0.0")
                        elif column in ['sessions_remaining']:
                            cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {column} INTEGER DEFAULT 0")
                        elif column in ['active_packages', 'payment_status', 'last_updated']:
                            cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {column} TEXT DEFAULT ''")
                        else:
                            cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {column} TEXT")
                        
                        logger.info(f"✅ Added column: {column}")
                    except Exception as e:
                        logger.warning(f"⚠️ Column {column} might already exist: {e}")
                
                logger.info("✅ Training clients table migration completed")
            
            # Create member_categories table for fast member classification
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_categories (
                    id INTEGER PRIMARY KEY,
                    member_id TEXT UNIQUE,
                    category TEXT,
                    status_message TEXT,
                    full_name TEXT,
                    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            
            # Create indexes for better performance
            # Guard index creation only if column exists to avoid errors on legacy DBs
            if 'prospect_id' in table_info('members'):
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_prospect_id ON members(prospect_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)")
            if 'prospect_id' in table_info('prospects'):
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_prospect_id ON prospects(prospect_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_clients_member_id ON training_clients(member_id)")
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
        """
        if not members:
            return False
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            for m in members:
                # Normalize keys from possible variants
                prospect_id = (
                    m.get('prospect_id') or m.get('prospectId') or m.get('clubos_member_id') or m.get('id')
                )
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

                # Use INSERT OR REPLACE with correct column names from existing schema
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO members (
                        prospect_id, guid, first_name, last_name, full_name, email, mobile_phone,
                        status, status_message, user_type, amount_past_due, date_of_next_payment, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        str(prospect_id) if prospect_id is not None else None,  # prospect_id column
                        str(prospect_id) if prospect_id is not None else None,  # guid column (use same value)
                        first_name,
                        last_name,
                        full_name,
                        email,
                        mobile_phone,
                        status,
                        status_message,
                        member_type,  # Maps to user_type column
                        float(amount_past_due) if amount_past_due not in (None, '') else 0,
                        date_of_next_payment,
                    ),
                )
                
                # Also update the category classification based on amount_past_due
                if prospect_id:
                    # Use the same classification logic as clean_dashboard.py
                    status_message_lower = str(status_message or '').lower()
                    status_lower = str(status or '').lower()
                    past_due_amount = float(amount_past_due or 0)
                    
                    # Default category and status message
                    category = 'green'
                    updated_status_message = status_message
                    
                    # Past due members (highest priority) - check status message patterns
                    if ('past due more than 30' in status_message_lower or 
                        'delinquent' in status_message_lower or 
                        past_due_amount > 100):  # Higher amounts typically = longer past due
                        category = 'past_due'
                        updated_status_message = 'Past Due more than 30 days'
                    elif ('past due 6-30' in status_message_lower or 
                          'past due' in status_message_lower or 
                          'overdue' in status_message_lower or
                          (past_due_amount > 0 and past_due_amount <= 100)):
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
                    
                    # Insert/update member category
                    cursor.execute("""
                        INSERT OR REPLACE INTO member_categories 
                        (member_id, category, status_message, classified_at)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """, (str(prospect_id), category, updated_status_message))
            conn.commit()
            logger.info(f"✅ Successfully saved {len(members)} members to database")
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
                    WHERE COALESCE(amount_past_due, 0) > 0
                    OR (status_message LIKE '%Past Due%')
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
                WHERE COALESCE(amount_past_due, 0) > 0 OR status_message LIKE '%Past Due%'
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
            (member_id, category, status_message, classified_at)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (member_id, category, status_message, datetime.now()))
    
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
    
    def save_training_clients_to_db(self, training_clients: List[Dict]) -> bool:
        """Save or update training clients with their agreement data to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            logger.info(f"💾 Saving {len(training_clients)} training clients to database...")
            
            for client in training_clients:
                try:
                    # Debug: Log what we're trying to save
                    logger.info(f"💾 Saving client: {client.get('member_name', 'Unknown')} - ClubOS ID: {client.get('clubos_member_id')}")
                    
                    # Check if training client already exists
                    cursor.execute("""
                        SELECT id FROM training_clients 
                        WHERE clubos_member_id = ? OR member_id = ?
                    """, (client.get('clubos_member_id'), client.get('member_id')))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing record - use existing columns
                        cursor.execute("""
                            UPDATE training_clients SET
                                clubos_member_id = ?,
                                member_id = ?,
                                member_name = ?,
                                first_name = ?,
                                last_name = ?,
                                email = ?,
                                phone = ?,
                                trainer_name = ?,
                                payment_status = ?,
                                last_updated = ?
                            WHERE id = ?
                        """, (
                            client.get('clubos_member_id'),
                            client.get('member_id'),
                            client.get('member_name', ''),
                            client.get('first_name', ''),
                            client.get('last_name', ''),
                            client.get('email', ''),
                            client.get('phone', ''),
                            client.get('trainer_name', ''),
                            client.get('payment_status', 'Current'),
                            datetime.now().isoformat(),
                            existing[0]
                        ))
                        logger.info(f"✅ Updated existing client {existing[0]}")
                    else:
                        # Insert new record - use existing columns
                        cursor.execute("""
                            INSERT INTO training_clients (
                                clubos_member_id, member_id, member_name, first_name, last_name,
                                email, phone, trainer_name, payment_status, created_at, last_updated
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            client.get('clubos_member_id'),
                            client.get('member_id'),
                            client.get('member_name', ''),
                            client.get('first_name', ''),
                            client.get('last_name', ''),
                            client.get('email', ''),
                            client.get('phone', ''),
                            client.get('trainer_name', ''),
                            client.get('payment_status', 'Current'),
                            datetime.now().isoformat(),
                            datetime.now().isoformat()
                        ))
                        logger.info(f"✅ Inserted new client with ID: {cursor.lastrowid}")
                        
                except Exception as client_error:
                    logger.error(f"❌ Error saving training client {client.get('member_name', 'Unknown')}: {client_error}")
                    continue
            
            conn.commit()
            logger.info(f"✅ Successfully saved {len(training_clients)} training clients to database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving training clients to database: {e}")
            if 'conn' in locals():
                conn.rollback()
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
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
