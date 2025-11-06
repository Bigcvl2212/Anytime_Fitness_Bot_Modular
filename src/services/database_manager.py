#!/usr/bin/env python3
"""
Simple SQLite Database Manager Service
Handles all database operations using SQLite only
"""

import os
import sys
import sqlite3
import pandas as pd
import logging
import json
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Iterator
from flask import current_app
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple SQLite-only Database Manager for gym data management"""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.last_refresh: Optional[datetime] = None
        self.refresh_interval: int = 3600  # 1 hour in seconds
        self.db_type: str = 'sqlite'  # Always SQLite

        # Use SQLite database
        if db_path:
            self.db_path = db_path
        else:
            # CRITICAL: When frozen, use writable AppData directory instead of Program Files
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - use user's AppData
                db_dir = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'data'
                db_dir.mkdir(parents=True, exist_ok=True)
                self.db_path = str(db_dir / 'gym_bot.db')
            else:
                # Running as script - use project root
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.db_path = os.path.join(project_root, 'gym_bot.db')

        self.db_name = os.path.basename(self.db_path)  # Add db_name attribute
        logger.info(f"💾 Using SQLite database: {self.db_path}")

        # Initialize the database schema
        self.init_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Get SQLite database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def init_schema(self) -> None:
        """Initialize SQLite database schema"""
        logger.info("💾 Initializing SQLite schema...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
            tables_exist = cursor.fetchone() is not None

            if tables_exist:
                logger.info("✅ SQLite schema already exists, running migrations...")
                # Run migrations for existing tables
                self._run_migrations(cursor)
                conn.commit()
                return

            # Create members table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prospect_id TEXT UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    mobile_phone TEXT,
                    status TEXT DEFAULT 'Active',
                    agreement_type TEXT,
                    club_name TEXT,
                    join_date TEXT,
                    amount_past_due REAL DEFAULT 0.0,
                    billing_day INTEGER,
                    last_payment_date TEXT,
                    next_billing_date TEXT,
                    payment_method TEXT,
                    membership_fee REAL DEFAULT 0.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


            # Create prospects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prospect_id TEXT UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    mobile_phone TEXT,
                    status TEXT,
                    source TEXT,
                    interest_level TEXT,
                    club_name TEXT,
                    created_date TEXT,
                    last_contact_date TEXT,
                    notes TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create training_clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prospect_id TEXT,
                    member_name TEXT,
                    email TEXT,
                    phone TEXT,
                    status TEXT,
                    trainer_name TEXT,
                    package_type TEXT,
                    sessions_total INTEGER DEFAULT 0,
                    sessions_used INTEGER DEFAULT 0,
                    sessions_remaining INTEGER DEFAULT 0,
                    package_cost REAL DEFAULT 0.0,
                    past_due_amount REAL DEFAULT 0.0,
                    next_session_date TEXT,
                    last_session_date TEXT,
                    club_name TEXT,
                    created_date TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    recipient_name TEXT,
                    recipient_email TEXT,
                    recipient_phone TEXT,
                    subject TEXT,
                    message_content TEXT,
                    message_type TEXT,
                    status TEXT,
                    sent_date TEXT,
                    delivered_date TEXT,
                    read_date TEXT,
                    club_name TEXT,
                    campaign_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info("✅ SQLite schema created successfully")

    def _run_migrations(self, cursor) -> None:
        """Run database migrations for existing tables"""
        logger.info("🔄 Running database migrations...")

        # Migration 1: Ensure prospect_id column exists in training_clients
        try:
            cursor.execute("PRAGMA table_info(training_clients)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'prospect_id' not in columns:
                logger.info("🔄 Adding prospect_id column to training_clients table")
                cursor.execute("ALTER TABLE training_clients ADD COLUMN prospect_id TEXT")
                logger.info("✅ Added prospect_id column to training_clients")
            else:
                logger.info("✅ prospect_id column already exists in training_clients")
        except Exception as e:
            logger.error(f"❌ Migration error for training_clients.prospect_id: {e}")

        # Migration 2: Ensure last_payment_date column exists in members
        try:
            cursor.execute("PRAGMA table_info(members)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'last_payment_date' not in columns:
                logger.info("🔄 Adding last_payment_date column to members table")
                cursor.execute("ALTER TABLE members ADD COLUMN last_payment_date TEXT")
                logger.info("✅ Added last_payment_date column to members")
            else:
                logger.info("✅ last_payment_date column already exists in members")
        except Exception as e:
            logger.error(f"❌ Migration error for members.last_payment_date: {e}")

        # Migration 3: Ensure messages table has all required columns for ClubOS sync
        try:
            cursor.execute("PRAGMA table_info(messages)")
            columns = [row[1] for row in cursor.fetchall()]

            missing_columns = []
            if 'content' not in columns:
                missing_columns.append(('content', 'TEXT'))
            if 'from_user' not in columns:
                missing_columns.append(('from_user', 'TEXT'))
            if 'channel' not in columns:
                missing_columns.append(('channel', 'TEXT'))
            if 'timestamp' not in columns:
                missing_columns.append(('timestamp', 'TEXT'))
            if 'owner_id' not in columns:
                missing_columns.append(('owner_id', 'TEXT'))
            if 'member_id' not in columns:
                missing_columns.append(('member_id', 'TEXT'))
            if 'conversation_id' not in columns:
                missing_columns.append(('conversation_id', 'TEXT'))
            if 'delivery_status' not in columns:
                missing_columns.append(('delivery_status', 'TEXT'))
            if 'recipient_name' not in columns:
                missing_columns.append(('recipient_name', 'TEXT'))

            for col_name, col_type in missing_columns:
                logger.info(f"🔄 Adding {col_name} column to messages table")
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added {col_name} column to messages")

            if missing_columns:
                logger.info(f"✅ Added {len(missing_columns)} columns to messages table")
            else:
                logger.info("✅ All required columns exist in messages table")
        except Exception as e:
            logger.error(f"❌ Migration error for messages table: {e}")

        # Migration 4: Add address fields to members table for collections reporting
        try:
            cursor.execute("PRAGMA table_info(members)")
            columns = [row[1] for row in cursor.fetchall()]

            missing_columns = []
            if 'phone' not in columns:
                missing_columns.append(('phone', 'TEXT'))
            if 'address' not in columns:
                missing_columns.append(('address', 'TEXT'))
            if 'city' not in columns:
                missing_columns.append(('city', 'TEXT'))
            if 'state' not in columns:
                missing_columns.append(('state', 'TEXT'))
            if 'zip_code' not in columns:
                missing_columns.append(('zip_code', 'TEXT'))
            if 'guid' not in columns:
                missing_columns.append(('guid', 'TEXT'))

            for col_name, col_type in missing_columns:
                logger.info(f"🔄 Adding {col_name} column to members table")
                cursor.execute(f"ALTER TABLE members ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added {col_name} column to members")

            if missing_columns:
                logger.info(f"✅ Added {len(missing_columns)} address columns to members table")
        except Exception as e:
            logger.error(f"❌ Migration error for members address fields: {e}")

        # Migration 5: Add address fields to training_clients table for collections reporting
        try:
            cursor.execute("PRAGMA table_info(training_clients)")
            columns = [row[1] for row in cursor.fetchall()]

            missing_columns = []
            if 'mobile_phone' not in columns:
                missing_columns.append(('mobile_phone', 'TEXT'))
            if 'address' not in columns:
                missing_columns.append(('address', 'TEXT'))
            if 'city' not in columns:
                missing_columns.append(('city', 'TEXT'))
            if 'state' not in columns:
                missing_columns.append(('state', 'TEXT'))
            if 'zip_code' not in columns:
                missing_columns.append(('zip_code', 'TEXT'))
            if 'clubos_member_id' not in columns:
                missing_columns.append(('clubos_member_id', 'TEXT'))
            if 'total_past_due' not in columns:
                missing_columns.append(('total_past_due', 'REAL DEFAULT 0.0'))
            if 'agreement_id' not in columns:
                missing_columns.append(('agreement_id', 'TEXT'))

            for col_name, col_type in missing_columns:
                logger.info(f"🔄 Adding {col_name} column to training_clients table")
                cursor.execute(f"ALTER TABLE training_clients ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added {col_name} column to training_clients")

            if missing_columns:
                logger.info(f"✅ Added {len(missing_columns)} address columns to training_clients table")
        except Exception as e:
            logger.error(f"❌ Migration error for training_clients address fields: {e}")

        # Migration 6: Add Phase 1 AI Agent columns to messages table
        try:
            cursor.execute("PRAGMA table_info(messages)")
            columns = [row[1] for row in cursor.fetchall()]

            missing_columns = []
            # AI processing tracking
            if 'ai_processed' not in columns:
                missing_columns.append(('ai_processed', 'INTEGER DEFAULT 0'))
            if 'ai_responded' not in columns:
                missing_columns.append(('ai_responded', 'INTEGER DEFAULT 0'))
            if 'ai_confidence_score' not in columns:
                missing_columns.append(('ai_confidence_score', 'REAL'))
            if 'ai_action_taken' not in columns:
                missing_columns.append(('ai_action_taken', 'TEXT'))
            if 'ai_response_sent_at' not in columns:
                missing_columns.append(('ai_response_sent_at', 'TIMESTAMP'))
            
            # Message threading and status
            if 'thread_id' not in columns:
                missing_columns.append(('thread_id', 'TEXT'))
            if 'requires_response' not in columns:
                missing_columns.append(('requires_response', 'INTEGER DEFAULT 0'))
            if 'sent_at' not in columns:
                missing_columns.append(('sent_at', 'TIMESTAMP'))
            if 'received_at' not in columns:
                missing_columns.append(('received_at', 'TIMESTAMP'))
            if 'read_at' not in columns:
                missing_columns.append(('read_at', 'TIMESTAMP'))
            
            # ClubOS metadata
            if 'clubos_message_id' not in columns:
                missing_columns.append(('clubos_message_id', 'TEXT'))
            if 'clubos_conversation_id' not in columns:
                missing_columns.append(('clubos_conversation_id', 'TEXT'))
            if 'from_member_id' not in columns:
                missing_columns.append(('from_member_id', 'TEXT'))
            if 'from_member_name' not in columns:
                missing_columns.append(('from_member_name', 'TEXT'))
            if 'to_staff_name' not in columns:
                missing_columns.append(('to_staff_name', 'TEXT'))

            for col_name, col_type in missing_columns:
                logger.info(f"🔄 Adding {col_name} column to messages table (Phase 1 AI Agent)")
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added {col_name} column to messages")

            if missing_columns:
                logger.info(f"✅ Added {len(missing_columns)} Phase 1 AI Agent columns to messages table")
            else:
                logger.info("✅ All Phase 1 AI Agent columns exist in messages table")
        except Exception as e:
            logger.error(f"❌ Migration error for Phase 1 AI Agent columns: {e}")

        # Migration 7: Create conversations table for message threading
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
            conversations_exists = cursor.fetchone() is not None

            if not conversations_exists:
                logger.info("🔄 Creating conversations table for message threading")
                cursor.execute("""
                    CREATE TABLE conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT UNIQUE NOT NULL,
                        member_id TEXT,
                        member_name TEXT,
                        last_message_at TIMESTAMP,
                        last_message_preview TEXT,
                        unread_count INTEGER DEFAULT 0,
                        requires_response INTEGER DEFAULT 0,
                        ai_handling INTEGER DEFAULT 0,
                        conversation_status TEXT DEFAULT 'active',
                        tags TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_member_id ON conversations(member_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(conversation_status)")
                
                logger.info("✅ Created conversations table with indexes")
            else:
                logger.info("✅ Conversations table already exists")
        except Exception as e:
            logger.error(f"❌ Migration error for conversations table: {e}")

        # Phase 3: AI Conversations table for workflow messaging
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ai_conversations'")
            ai_conversations_exists = cursor.fetchone() is not None

            if not ai_conversations_exists:
                logger.info("🔄 Creating ai_conversations table for Phase 3 workflow messaging")
                cursor.execute("""
                    CREATE TABLE ai_conversations (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        workflow_id TEXT,
                        timestamp TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_conversations_timestamp ON ai_conversations(timestamp DESC)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_conversations_workflow ON ai_conversations(workflow_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_conversations_type ON ai_conversations(type)")
                
                logger.info("✅ Created ai_conversations table with indexes")
            else:
                logger.info("✅ ai_conversations table already exists")
        except Exception as e:
            logger.error(f"❌ Migration error for ai_conversations table: {e}")

        # Phase 3: Approval Requests table for workflow approvals
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='approval_requests'")
            approval_requests_exists = cursor.fetchone() is not None

            if not approval_requests_exists:
                logger.info("🔄 Creating approval_requests table for Phase 3 workflow approvals")
                cursor.execute("""
                    CREATE TABLE approval_requests (
                        id TEXT PRIMARY KEY,
                        workflow_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        details TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        decided_by TEXT,
                        decided_at TEXT
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_approval_requests_workflow ON approval_requests(workflow_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_approval_requests_created ON approval_requests(created_at DESC)")
                
                logger.info("✅ Created approval_requests table with indexes")
            else:
                logger.info("✅ approval_requests table already exists")
        except Exception as e:
            logger.error(f"❌ Migration error for approval_requests table: {e}")

        logger.info("✅ Database migrations complete")

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """Execute a database query with proper error handling"""
        logger.debug(f"💾 SQLite Query: {query}")
        logger.debug(f"💾 Parameters: {params}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount

        except Exception as e:
            logger.error(f"❌ Database query error: {e}")
            logger.error(f"❌ Query: {query}")
            logger.error(f"❌ Parameters: {params}")
            raise

    def save_members_to_db(self, members_data: List[Dict[str, Any]]) -> bool:
        """Save members data to SQLite database"""
        if not members_data:
            logger.debug("No members data to save")
            return True

        logger.debug(f"Saving {len(members_data)} members to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for member in members_data:
                    # Use REPLACE to handle updates - updated to match current schema with address fields
                    cursor.execute("""
                        REPLACE INTO members (
                            prospect_id, guid, first_name, last_name, full_name, email,
                            phone, mobile_phone, address, city, state, zip_code,
                            status, status_message, member_type, user_type,
                            join_date, amount_past_due, date_of_next_payment,
                            base_amount_past_due, late_fees, missed_payments,
                            agreement_recurring_cost, agreement_id, agreement_guid, agreement_type,
                            club_name, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        member.get('prospect_id') or member.get('id'),
                        member.get('guid'),
                        member.get('first_name') or member.get('firstName'),
                        member.get('last_name') or member.get('lastName'),
                        member.get('full_name'),
                        member.get('email'),
                        member.get('phone') or member.get('phoneNumber'),
                        member.get('mobile_phone') or member.get('mobilePhone'),
                        member.get('address') or member.get('address1') or member.get('streetAddress'),
                        member.get('city'),
                        member.get('state'),
                        member.get('zip_code') or member.get('zip') or member.get('zipCode') or member.get('postalCode'),
                        member.get('status', 'Active'),
                        member.get('status_message', ''),
                        member.get('member_type', ''),
                        member.get('user_type', ''),
                        member.get('join_date'),
                        float(member.get('amount_past_due', 0.0)),
                        member.get('date_of_next_payment'),
                        float(member.get('base_amount_past_due', 0.0)),
                        float(member.get('late_fees', 0.0)),
                        int(member.get('missed_payments', 0)),
                        float(member.get('agreement_recurring_cost', 0.0)),
                        member.get('agreement_id'),
                        member.get('agreement_guid'),
                        member.get('agreement_type', ''),
                        member.get('club_name', ''),
                        member.get('created_at', datetime.now().isoformat()),
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"Saved {len(members_data)} members to database")
                return True

        except Exception as e:
            logger.error(f"Error saving members: {e}")
            return False

    def update_member_billing_info(self, member_id: str, member_data: Dict[str, Any]) -> bool:
        """Update billing information for a specific member."""
        try:
            with self.get_connection() as conn:
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
                        amount_past_due = ?,
                        base_amount_past_due = ?,
                        late_fees = ?,
                        missed_payments = ?,
                        date_of_next_payment = ?,
                        status = ?,
                        status_message = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE prospect_id = ? OR guid = ?
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
            return False

    def save_prospects_to_db(self, prospects_data: List[Dict[str, Any]]) -> bool:
        """Save prospects data to SQLite database"""
        if not prospects_data:
            logger.debug("No prospects data to save")
            return True

        logger.debug(f"Saving {len(prospects_data)} prospects to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for prospect in prospects_data:
                    cursor.execute("""
                        REPLACE INTO prospects (
                            prospect_id, first_name, last_name, full_name, email, phone, mobile_phone,
                            address, city, state, zip_code,
                            status, prospect_type, source, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prospect.get('prospect_id') or prospect.get('id'),
                        prospect.get('first_name') or prospect.get('firstName'),
                        prospect.get('last_name') or prospect.get('lastName'),
                        prospect.get('full_name') or f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip(),
                        prospect.get('email'),
                        prospect.get('phone') or prospect.get('phoneNumber') or prospect.get('homePhone'),
                        prospect.get('mobile_phone') or prospect.get('mobilePhone'),
                        prospect.get('address') or prospect.get('address1') or prospect.get('streetAddress'),
                        prospect.get('city'),
                        prospect.get('state'),
                        prospect.get('zip_code') or prospect.get('zipCode') or prospect.get('postalCode') or prospect.get('zip'),
                        prospect.get('status'),
                        prospect.get('prospect_type') or prospect.get('membershipType'),
                        prospect.get('source'),
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"Saved {len(prospects_data)} prospects to database")
                return True

        except Exception as e:
            logger.error(f"Error saving prospects: {e}")
            return False

    def save_training_clients_to_db(self, training_data: List[Dict[str, Any]]) -> bool:
        """Save training clients data to SQLite database"""
        if not training_data:
            logger.debug("No training clients data to save")
            return True

        logger.debug(f"Saving {len(training_data)} training clients to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for client in training_data:
                    # Helper function to serialize complex types to strings
                    def safe_value(value):
                        """Convert lists/dicts to JSON strings, None/empty to empty string"""
                        if value is None:
                            return None
                        if isinstance(value, (list, dict)):
                            return json.dumps(value)
                        return value
                    
                    # Serialize all potentially complex fields
                    active_packages = safe_value(client.get('active_packages'))
                    package_details = safe_value(client.get('package_details'))
                    address = safe_value(client.get('address'))
                    city = safe_value(client.get('city'))
                    state = safe_value(client.get('state'))
                    zip_code = safe_value(client.get('zip_code'))
                    email = safe_value(client.get('email'))
                    phone = safe_value(client.get('phone'))
                    mobile_phone = safe_value(client.get('mobile_phone'))
                    
                    cursor.execute("""
                        REPLACE INTO training_clients (
                            prospect_id, clubos_member_id, member_name, email, phone, mobile_phone,
                            address, city, state, zip_code,
                            status, payment_status, trainer_name, training_package,
                            active_packages, package_summary, package_details,
                            past_due_amount, total_past_due, sessions_remaining,
                            agreement_id, last_updated, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        client.get('prospect_id'),
                        client.get('clubos_member_id'),
                        safe_value(client.get('member_name')),
                        email,
                        phone,
                        mobile_phone,
                        address,
                        city,
                        state,
                        zip_code,
                        safe_value(client.get('status')),
                        safe_value(client.get('payment_status')),
                        safe_value(client.get('trainer_name')),
                        safe_value(client.get('training_package')),
                        active_packages,
                        safe_value(client.get('package_summary')),
                        package_details,
                        float(client.get('past_due_amount', 0.0)),
                        float(client.get('total_past_due', 0.0)),
                        client.get('sessions_remaining'),
                        client.get('agreement_id'),
                        client.get('last_updated'),
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"Saved {len(training_data)} training clients to database")
                return True

        except Exception as e:
            logger.error(f"Error saving training clients: {e}")
            logger.debug(f"Failed client data sample: {training_data[0] if training_data else 'None'}")
            return False

    def get_members(self, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Get members from database"""
        query = "SELECT * FROM members ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, fetch_all=True)

    def get_prospects(self, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Get prospects from database"""
        query = "SELECT * FROM prospects ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, fetch_all=True)

    def get_training_clients(self, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Get training clients from database"""
        query = "SELECT * FROM training_clients ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, fetch_all=True)

    def get_past_due_members(self, min_amount: float = 0) -> List[sqlite3.Row]:
        """Get members with past due amounts"""
        query = "SELECT * FROM members WHERE amount_past_due > ? ORDER BY amount_past_due DESC"
        return self.execute_query(query, (min_amount,), fetch_all=True)

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats: Dict[str, Any] = {}

        try:
            # Count members
            result = self.execute_query("SELECT COUNT(*) as count FROM members", fetch_one=True)
            stats['total_members'] = result[0] if result else 0

            # Count prospects
            result = self.execute_query("SELECT COUNT(*) as count FROM prospects", fetch_one=True)
            stats['total_prospects'] = result[0] if result else 0

            # Count training clients
            result = self.execute_query("SELECT COUNT(*) as count FROM training_clients", fetch_one=True)
            stats['total_training_clients'] = result[0] if result else 0

            # Count past due members
            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE amount_past_due > 0", fetch_one=True)
            stats['past_due_members'] = result[0] if result else 0

            # Sum past due amounts
            result = self.execute_query("SELECT SUM(amount_past_due) as total FROM members WHERE amount_past_due > 0", fetch_one=True)
            stats['total_past_due_amount'] = result[0] if result and result[0] else 0.0

        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            stats = {'error': str(e)}

        return stats

    @contextmanager
    def get_cursor(self, connection=None) -> Iterator[sqlite3.Cursor]:
        """
        Get database cursor with automatic cleanup (context manager).

        Args:
            connection: Optional existing connection. If None, creates new connection.

        Yields:
            sqlite3.Cursor: Database cursor for executing queries

        Example:
            >>> with db_manager.get_cursor() as cursor:
            ...     cursor.execute("SELECT * FROM members")
            ...     results = cursor.fetchall()
        """
        conn = connection if connection else self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            if not connection:  # Only close if we created the connection
                conn.close()

    def close_connection(self, connection: Optional[sqlite3.Connection] = None) -> None:
        """Close database connection (no-op for SQLite as connections are context-managed)"""
        if connection:
            connection.close()
        pass

    def save_messages_to_db(self, messages_data: List[Dict[str, Any]]) -> None:
        """Save messages data to SQLite database"""
        if not messages_data:
            logger.debug("No messages data to save")
            return

        logger.debug(f"Saving {len(messages_data)} messages to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for message in messages_data:
                    cursor.execute("""
                        REPLACE INTO messages (
                            message_id, recipient_name, recipient_email, recipient_phone,
                            subject, message_content, message_type, status, sent_date,
                            delivered_date, read_date, club_name, campaign_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        message.get('message_id'),
                        message.get('recipient_name'),
                        message.get('recipient_email'),
                        message.get('recipient_phone'),
                        message.get('subject'),
                        message.get('message_content'),
                        message.get('message_type'),
                        message.get('status'),
                        message.get('sent_date'),
                        message.get('delivered_date'),
                        message.get('read_date'),
                        message.get('club_name'),
                        message.get('campaign_id'),
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"Saved {len(messages_data)} messages to database")

        except Exception as e:
            logger.error(f"Error saving messages: {e}")
            raise

    def get_members_by_category(self, category):
        """Get members by category based on status_message"""
        try:
            if category == 'green':
                # Members in good standing
                query = "SELECT * FROM members WHERE status_message = 'Member is in good standing' ORDER BY full_name"
            elif category == 'past_due':
                # Past due 6-30 days and past due more than 30 days
                query = """SELECT * FROM members
                          WHERE status_message = 'Past Due 6-30 days'
                             OR status_message = 'Past Due more than 30 days.'
                          ORDER BY amount_past_due DESC"""
            elif category == 'yellow':
                # Members with billing/address issues (expiring or pending cancel)
                query = """SELECT * FROM members
                          WHERE status_message = 'Member will expire within 30 days.'
                             OR status_message = 'Member is pending cancel'
                          ORDER BY full_name"""
            elif category == 'comp':
                # Comp members
                query = "SELECT * FROM members WHERE status_message = 'Comp Member' ORDER BY full_name"
            elif category == 'ppv':
                # PPV members
                query = "SELECT * FROM members WHERE status_message = 'Pay Per Visit Member' ORDER BY full_name"
            elif category == 'staff':
                # Staff members
                query = "SELECT * FROM members WHERE status_message = 'Staff Member' ORDER BY full_name"
            elif category == 'inactive':
                # Inactive/cancelled/expired members
                query = """SELECT * FROM members
                          WHERE status_message = 'Member is pending cancel'
                             OR status_message = 'Account has been cancelled.'
                             OR status_message = 'Expired'
                             OR status_message = ''
                          ORDER BY full_name"""
            elif category == 'collections':
                # Members sent to collections
                query = "SELECT * FROM members WHERE status_message = 'Sent to Collections' ORDER BY full_name"
            elif category == 'expiring':
                # Members expiring soon
                query = "SELECT * FROM members WHERE status_message = 'Member will expire within 30 days.' ORDER BY full_name"
            elif category == 'active':
                # All active members (good standing + expiring)
                query = """SELECT * FROM members
                          WHERE status_message = 'Member is in good standing'
                             OR status_message = 'Member will expire within 30 days.'
                          ORDER BY full_name"""
            else:
                # Default - return all members
                query = "SELECT * FROM members ORDER BY full_name"

            result = self.execute_query(query, fetch_all=True)
            # Convert SQLite Row objects to dictionaries for .get() access
            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(f"❌ Error getting members by category {category}: {e}")
            return []

    def get_category_counts(self):
        """Get member counts by category based on status_message"""
        try:
            counts = {}

            # Basic counts
            result = self.execute_query("SELECT COUNT(*) as count FROM members", fetch_one=True)
            counts['total_members'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM prospects", fetch_one=True)
            counts['total_prospects'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM training_clients", fetch_one=True)
            counts['total_training_clients'] = result[0] if result else 0

            # Category counts based on exact status_message matches
            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Member is in good standing'", fetch_one=True)
            counts['green'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Past Due 6-30 days' OR status_message = 'Past Due more than 30 days.'", fetch_one=True)
            counts['past_due'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Member will expire within 30 days.' OR status_message = 'Member is pending cancel'", fetch_one=True)
            counts['yellow'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Comp Member'", fetch_one=True)
            counts['comp'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Pay Per Visit Member'", fetch_one=True)
            counts['ppv'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Staff Member'", fetch_one=True)
            counts['staff'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Member is pending cancel' OR status_message = 'Account has been cancelled.' OR status_message = 'Expired' OR status_message = ''", fetch_one=True)
            counts['inactive'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Sent to Collections'", fetch_one=True)
            counts['collections'] = result[0] if result else 0

            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Member will expire within 30 days.'", fetch_one=True)
            counts['expiring'] = result[0] if result else 0

            # Active members (good standing + expiring)
            result = self.execute_query("SELECT COUNT(*) as count FROM members WHERE status_message = 'Member is in good standing' OR status_message = 'Member will expire within 30 days.'", fetch_one=True)
            counts['active'] = result[0] if result else 0

            return counts
        except Exception as e:
            logger.error(f"❌ Error getting category counts: {e}")
            return {}

    def get_member_count(self):
        """Get total member count"""
        try:
            result = self.execute_query("SELECT COUNT(*) as count FROM members", fetch_one=True)
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"❌ Error getting member count: {e}")
            return 0

    def get_prospect_count(self):
        """Get total prospect count"""
        try:
            result = self.execute_query("SELECT COUNT(*) as count FROM prospects", fetch_one=True)
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"❌ Error getting prospect count: {e}")
            return 0

    def get_all_members(self):
        """Get all members from database"""
        try:
            result = self.execute_query("SELECT * FROM members ORDER BY full_name", fetch_all=True)
            # Convert SQLite Row objects to dictionaries for .get() access
            return [dict(row) for row in result] if result else []
        except Exception as e:
            logger.error(f"❌ Error getting all members: {e}")
            return []

    def get_member_by_id(self, member_id):
        """Get a specific member by ID"""
        try:
            result = self.execute_query(
                "SELECT * FROM members WHERE prospect_id = ? OR guid = ?",
                (member_id, member_id),
                fetch_one=True
            )
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Error getting member by ID {member_id}: {e}")
            return None

    def get_member_invoices(self, member_id):
        """Get all invoices for a specific member"""
        try:
            results = self.execute_query(
                "SELECT * FROM invoices WHERE member_id = ? ORDER BY created_at DESC",
                (member_id,),
                fetch_all=True
            )
            return [dict(row) for row in results] if results else []
        except Exception as e:
            logger.error(f"❌ Error getting invoices for member {member_id}: {e}")
            return []



    def get_monthly_revenue_calculation(self):
        """Get monthly revenue calculation (for members API)"""
        try:
            # Use agreement_recurring_cost for revenue paying members (good standing + some others)
            query = """
                SELECT
                    SUM(agreement_recurring_cost) as total_monthly_revenue,
                    COUNT(*) as active_members,
                    AVG(agreement_recurring_cost) as average_fee
                FROM members
                WHERE (status_message = 'Member is in good standing'
                   OR status_message = 'Member will expire within 30 days.'
                   OR status_message = 'Past Due 6-30 days'
                   OR status_message = 'Past Due more than 30 days.')
                   AND agreement_recurring_cost > 0
            """
            result = self.execute_query(query, fetch_one=True)

            if result:
                return {
                    'total_monthly_revenue': float(result[0]) if result[0] else 0.0,
                    'active_members': int(result[1]) if result[1] else 0,
                    'average_fee': float(result[2]) if result[2] else 0.0
                }
            else:
                return {'total_monthly_revenue': 0.0, 'active_members': 0, 'average_fee': 0.0}

        except Exception as e:
            logger.error(f"❌ Error calculating monthly revenue: {e}")
            return {'total_monthly_revenue': 0.0, 'active_members': 0, 'average_fee': 0.0}

    def get_training_client_count(self) -> int:
        """Get total training client count"""
        try:
            result = self.execute_query("SELECT COUNT(*) FROM training_clients", fetch_one=True)
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"❌ Error getting training client count: {e}")
            return 0

    def log_access_action(self, log_entry: Dict) -> bool:
        """Log access control actions for audit trail"""
        try:
            from typing import Dict

            # Create access_logs table if it doesn't exist
            if self.db_type == 'postgresql':
                create_table_query = """
                    CREATE TABLE IF NOT EXISTS access_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        member_id TEXT NOT NULL,
                        member_name TEXT,
                        action TEXT NOT NULL,
                        reason TEXT,
                        success BOOLEAN NOT NULL,
                        error TEXT,
                        automated BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
            else:  # SQLite
                create_table_query = """
                    CREATE TABLE IF NOT EXISTS access_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        member_id TEXT NOT NULL,
                        member_name TEXT,
                        action TEXT NOT NULL,
                        reason TEXT,
                        success INTEGER NOT NULL,
                        error TEXT,
                        automated INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """

            self.execute_query(create_table_query)

            # Insert log entry
            if self.db_type == 'postgresql':
                insert_query = """
                    INSERT INTO access_logs
                    (timestamp, member_id, member_name, action, reason, success, error, automated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            else:
                insert_query = """
                    INSERT INTO access_logs
                    (timestamp, member_id, member_name, action, reason, success, error, automated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """

            # Convert boolean to int for SQLite
            success_val = log_entry.get('success')
            if self.db_type != 'postgresql' and isinstance(success_val, bool):
                success_val = 1 if success_val else 0

            automated_val = log_entry.get('automated', False)
            if self.db_type != 'postgresql' and isinstance(automated_val, bool):
                automated_val = 1 if automated_val else 0

            params = (
                log_entry.get('timestamp'),
                log_entry.get('member_id'),
                log_entry.get('member_name'),
                log_entry.get('action'),
                log_entry.get('reason'),
                success_val,
                log_entry.get('error'),
                automated_val
            )

            result = self.execute_query(insert_query, params)
            logger.info(f"✅ Access action logged: {log_entry.get('action')} for {log_entry.get('member_name')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error logging access action: {e}")
            return False

    def get_monthly_revenue_calculation(self) -> Dict[str, Any]:
        """Calculate monthly revenue from memberships and training clients (deduplicated)."""
        try:
            # Get membership revenue
            members_query = """
                SELECT
                    COUNT(DISTINCT prospect_id) as active_members,
                    SUM(CAST(agreement_recurring_cost AS REAL)) as total_membership_revenue
                FROM members
                WHERE status = 'Active'
                    AND agreement_recurring_cost IS NOT NULL
                    AND agreement_recurring_cost > 0
            """
            members_result = self.execute_query(members_query, fetch_one=True)

            membership_revenue = float(members_result['total_membership_revenue'] or 0) if members_result else 0
            active_members = int(members_result['active_members'] or 0) if members_result else 0

            # Get training revenue (deduplicated by most recent entry per member/agreement)
            training_query = """
                SELECT
                    COUNT(DISTINCT member_key) as training_clients_count,
                    SUM(CAST(monthly_amount AS REAL)) as total_training_revenue
                FROM (
                    SELECT
                        tc.*,
                        COALESCE(tc.clubos_member_id, tc.prospect_id, tc.member_name) as member_key,
                        COALESCE(tc.agreement_id, 'default') as agreement_key,
                        CASE
                            WHEN tc.package_details IS NOT NULL AND tc.package_details != '' THEN
                                -- Extract monthly amount from package details JSON
                                CAST(
                                    COALESCE(
                                        json_extract(tc.package_details, '$[0].monthly_cost'),
                                        json_extract(tc.package_details, '$[0].amount'),
                                        0
                                    ) AS REAL
                                )
                            ELSE 0
                        END as monthly_amount
                    FROM training_clients tc
                    INNER JOIN (
                        SELECT
                            COALESCE(clubos_member_id, prospect_id, member_name) as mk,
                            COALESCE(agreement_id, 'default') as ak,
                            MAX(updated_at) as max_updated
                        FROM training_clients
                        GROUP BY mk, ak
                    ) latest
                    ON COALESCE(tc.clubos_member_id, tc.prospect_id, tc.member_name) = latest.mk
                    AND COALESCE(tc.agreement_id, 'default') = latest.ak
                    AND tc.updated_at = latest.max_updated
                    WHERE tc.payment_status != 'Cancelled'
                )
            """
            training_result = self.execute_query(training_query, fetch_one=True)

            training_revenue = float(training_result['total_training_revenue'] or 0) if training_result else 0
            training_clients_count = int(training_result['training_clients_count'] or 0) if training_result else 0

            total_revenue = membership_revenue + training_revenue

            logger.info(f"📊 Revenue calculation - Membership: ${membership_revenue:.2f}, Training: ${training_revenue:.2f}, Total: ${total_revenue:.2f}")

            return {
                'total_monthly_revenue': membership_revenue,
                'training_revenue': training_revenue,
                'combined_revenue': total_revenue,
                'active_members': active_members,
                'training_clients_count': training_clients_count
            }

        except Exception as e:
            logger.error(f"❌ Error calculating monthly revenue: {e}")
            return {
                'total_monthly_revenue': 0,
                'training_revenue': 0,
                'combined_revenue': 0,
                'active_members': 0,
                'training_clients_count': 0
            }