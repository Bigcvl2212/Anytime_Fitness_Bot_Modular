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
from decimal import Decimal, ROUND_HALF_UP
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
        """Get SQLite database connection with improved concurrency settings"""
        # Set timeout to 30 seconds to handle concurrent operations
        conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name

        # Enable WAL mode for better concurrency (allows multiple readers with one writer)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA foreign_keys = ON')

        # Set busy timeout for additional safety
        conn.execute('PRAGMA busy_timeout=30000')

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
                    guid TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    mobile_phone TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    status TEXT DEFAULT 'Active',
                    status_message TEXT,
                    member_type TEXT,
                    user_type TEXT,
                    agreement_type TEXT,
                    agreement_id TEXT,
                    agreement_guid TEXT,
                    agreement_status TEXT,
                    club_name TEXT,
                    join_date TEXT,
                    date_of_next_payment TEXT,
                    amount_past_due REAL DEFAULT 0.0,
                    base_amount_past_due REAL DEFAULT 0.0,
                    late_fees REAL DEFAULT 0.0,
                    missed_payments INTEGER DEFAULT 0,
                    billing_day INTEGER,
                    last_payment_date TEXT,
                    next_billing_date TEXT,
                    payment_method TEXT,
                    membership_fee REAL DEFAULT 0.0,
                    agreement_recurring_cost REAL DEFAULT 0.0,
                    payment_plan_exempt BOOLEAN DEFAULT 0,
                    created_at TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


            # Create prospects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prospect_id TEXT UNIQUE,
                    first_name TEXT,
                    last_updated TEXT,
                    agreement_id TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    mobile_phone TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip_code TEXT,
                    status TEXT,
                    prospect_type TEXT,
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
                        clubos_member_id TEXT,
                        member_name TEXT,
                        email TEXT,
                        phone TEXT,
                        mobile_phone TEXT,
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        status TEXT,
                        payment_status TEXT,
                        trainer_name TEXT,
                        training_package TEXT,
                        package_type TEXT,
                        active_packages TEXT,
                        package_summary TEXT,
                        package_details TEXT,
                        sessions_total INTEGER DEFAULT 0,
                        sessions_used INTEGER DEFAULT 0,
                        sessions_remaining INTEGER DEFAULT 0,
                        package_cost REAL DEFAULT 0.0,
                        past_due_amount REAL DEFAULT 0.0,
                        total_past_due REAL DEFAULT 0.0,
                        next_session_date TEXT,
                        last_session_date TEXT,
                        club_name TEXT,
                        created_date TEXT,
                        last_updated TEXT,
                        agreement_id TEXT,
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

            # Create invoices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL,
                    square_invoice_id TEXT UNIQUE,
                    amount REAL NOT NULL,
                    status TEXT,
                    payment_method TEXT,
                    delivery_method TEXT,
                    due_date TEXT,
                    payment_date TEXT,
                    square_payment_id TEXT,
                    notes TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_member_id ON invoices(member_id)")

            # Create payment plan tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL UNIQUE,
                    plan_name TEXT,
                    status TEXT DEFAULT 'active',
                    total_amount REAL NOT NULL,
                    balance_remaining REAL NOT NULL,
                    installment_amount REAL NOT NULL,
                    installments_total INTEGER NOT NULL,
                    installments_paid INTEGER DEFAULT 0,
                    frequency_days INTEGER DEFAULT 14,
                    next_payment_due TEXT,
                    last_payment_date TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    notes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_plans_member_id ON payment_plans(member_id)")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_plan_installments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    installment_number INTEGER NOT NULL,
                    due_date TEXT,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    paid_date TEXT,
                    amount_paid REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(plan_id) REFERENCES payment_plans(id) ON DELETE CASCADE,
                    UNIQUE(plan_id, installment_number)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_plan_installments_plan ON payment_plan_installments(plan_id)")

            # Ensure migrations run even on fresh databases so optional columns exist
            self._run_migrations(cursor)
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

        # Migration 8: Add status_message column to members table for campaign categorization
        try:
            cursor.execute("PRAGMA table_info(members)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'status_message' not in columns:
                logger.info("🔄 Adding status_message column to members table")
                cursor.execute("ALTER TABLE members ADD COLUMN status_message TEXT")
                logger.info("✅ Added status_message column to members")
            else:
                logger.info("✅ status_message column already exists in members")
        except Exception as e:
            logger.error(f"❌ Migration error for members.status_message: {e}")

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

        # Migration 8: Add billing breakdown fields to members table for past due cards
        try:
            cursor.execute("PRAGMA table_info(members)")
            columns = [row[1] for row in cursor.fetchall()]

            missing_columns = []
            if 'base_amount_past_due' not in columns:
                missing_columns.append(('base_amount_past_due', 'REAL DEFAULT 0.0'))
            if 'late_fees' not in columns:
                missing_columns.append(('late_fees', 'REAL DEFAULT 0.0'))
            if 'missed_payments' not in columns:
                missing_columns.append(('missed_payments', 'INTEGER DEFAULT 0'))

            for col_name, col_type in missing_columns:
                logger.info(f"🔄 Adding {col_name} column to members table for past due calculations")
                cursor.execute(f"ALTER TABLE members ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added {col_name} column to members")

            if missing_columns:
                logger.info(f"✅ Added {len(missing_columns)} billing breakdown columns to members table")
            else:
                logger.info("✅ All billing breakdown columns already exist in members table")
        except Exception as e:
            logger.error(f"❌ Migration error for members billing breakdown fields: {e}")

        # Migration 9: Add processed_members column to bulk_checkin_runs table if missing
        try:
            # Check if bulk_checkin_runs table exists
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='bulk_checkin_runs'
            """)
            table_exists = cursor.fetchone()

            if table_exists:
                cursor.execute("PRAGMA table_info(bulk_checkin_runs)")
                columns = [row[1] for row in cursor.fetchall()]

                if 'processed_members' not in columns:
                    logger.info("🔄 Adding processed_members column to bulk_checkin_runs table")
                    cursor.execute("ALTER TABLE bulk_checkin_runs ADD COLUMN processed_members INTEGER DEFAULT 0")
                    logger.info("✅ Added processed_members column to bulk_checkin_runs")
                else:
                    logger.info("✅ processed_members column already exists in bulk_checkin_runs")
            else:
                logger.info("ℹ️ bulk_checkin_runs table doesn't exist yet - will be created on first use")
        except Exception as e:
            logger.error(f"❌ Migration error for bulk_checkin_runs processed_members field: {e}")

        # Migration 10: Add payment_plan_exempt column to members table for auto-lock exemptions
        try:
            cursor.execute("PRAGMA table_info(members)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'payment_plan_exempt' not in columns:
                logger.info("🔄 Adding payment_plan_exempt column to members table")
                cursor.execute("ALTER TABLE members ADD COLUMN payment_plan_exempt BOOLEAN DEFAULT 0")
                logger.info("✅ Added payment_plan_exempt column to members")
            else:
                logger.info("✅ payment_plan_exempt column already exists in members table")
        except Exception as e:
            logger.error(f"❌ Migration error for members payment_plan_exempt field: {e}")

        # Migration 11: Add AI knowledge base documents table (with all required columns)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_knowledge_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_by TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, title)
                )
            """)
            
            # Check if we need to add missing columns to existing table
            cursor.execute("PRAGMA table_info(ai_knowledge_documents)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'is_active' not in columns and 'active' in columns:
                # Rename active to is_active
                logger.info("🔄 Migrating 'active' column to 'is_active'")
                cursor.execute("ALTER TABLE ai_knowledge_documents RENAME COLUMN active TO is_active")
            elif 'is_active' not in columns:
                cursor.execute("ALTER TABLE ai_knowledge_documents ADD COLUMN is_active BOOLEAN DEFAULT 1")
                
            if 'created_by' not in columns:
                logger.info("🔄 Adding 'created_by' column to ai_knowledge_documents")
                cursor.execute("ALTER TABLE ai_knowledge_documents ADD COLUMN created_by TEXT")
                
            if 'tags' not in columns:
                logger.info("🔄 Adding 'tags' column to ai_knowledge_documents")
                cursor.execute("ALTER TABLE ai_knowledge_documents ADD COLUMN tags TEXT")
            
            logger.info("✅ AI knowledge documents table ready")
        except Exception as e:
            logger.error(f"❌ Migration error for ai_knowledge_documents table: {e}")

        # Migration 12: Add AI workflow settings table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_workflow_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_name TEXT NOT NULL UNIQUE,
                    enabled BOOLEAN DEFAULT 0,
                    config TEXT,
                    last_run TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default workflow settings if they don't exist
            default_workflows = [
                ('auto_reply_messages', 0, '{"response_delay_seconds": 30}'),
                ('prospect_outreach', 0, '{"check_interval_minutes": 5}'),
                ('past_due_reminders', 0, '{"reminder_hour": 9, "max_reminders_per_day": 1}'),
                ('auto_lock_past_due', 0, '{"grace_period_days": 7, "respect_payment_plans": true}'),
                ('square_invoice_automation', 0, '{"auto_send": false}')
            ]
            
            for workflow_name, enabled, config in default_workflows:
                cursor.execute("""
                    INSERT OR IGNORE INTO ai_workflow_settings (workflow_name, enabled, config)
                    VALUES (?, ?, ?)
                """, (workflow_name, enabled, config))
            
            logger.info("✅ AI workflow settings table ready with defaults")
        except Exception as e:
            logger.error(f"❌ Migration error for ai_workflow_settings table: {e}")

        # Migration 13: Ensure invoices table exists for payment tracking
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL,
                    square_invoice_id TEXT UNIQUE,
                    amount REAL NOT NULL,
                    status TEXT,
                    payment_method TEXT,
                    delivery_method TEXT,
                    due_date TEXT,
                    payment_date TEXT,
                    square_payment_id TEXT,
                    notes TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_member_id ON invoices(member_id)")
            logger.info("✅ Invoices table verified")
        except Exception as e:
            logger.error(f"❌ Migration error for invoices table: {e}")

        # Migration 14: Ensure payment plan tables exist
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT NOT NULL UNIQUE,
                    plan_name TEXT,
                    status TEXT DEFAULT 'active',
                    total_amount REAL NOT NULL,
                    balance_remaining REAL NOT NULL,
                    installment_amount REAL NOT NULL,
                    installments_total INTEGER NOT NULL,
                    installments_paid INTEGER DEFAULT 0,
                    frequency_days INTEGER DEFAULT 14,
                    next_payment_due TEXT,
                    last_payment_date TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    notes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_plans_member_id ON payment_plans(member_id)")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_plan_installments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    installment_number INTEGER NOT NULL,
                    due_date TEXT,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    paid_date TEXT,
                    amount_paid REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(plan_id) REFERENCES payment_plans(id) ON DELETE CASCADE,
                    UNIQUE(plan_id, installment_number)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_plan_installments_plan ON payment_plan_installments(plan_id)")
            logger.info("✅ Payment plan tables verified")
        except Exception as e:
            logger.error(f"❌ Migration error for payment plan tables: {e}")

        # Migration 15: Add member_name column to payment_plans table
        try:
            cursor.execute("PRAGMA table_info(payment_plans)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'member_name' not in columns:
                logger.info("🔄 Adding member_name column to payment_plans table")
                cursor.execute("ALTER TABLE payment_plans ADD COLUMN member_name TEXT")
                logger.info("✅ Added member_name column to payment_plans")
            else:
                logger.info("✅ member_name column already exists in payment_plans")
        except Exception as e:
            logger.error(f"❌ Migration error for payment_plans.member_name: {e}")

        # Migration 16: Add ClubOS leads tracking columns to prospects table
        try:
            cursor.execute("PRAGMA table_info(prospects)")
            columns = [row[1] for row in cursor.fetchall()]

            missing_columns = []
            if 'last_contact_date' not in columns:
                missing_columns.append(('last_contact_date', 'TEXT'))
            if 'created_date' not in columns:
                missing_columns.append(('created_date', 'TEXT'))
            if 'interest_level' not in columns:
                missing_columns.append(('interest_level', 'TEXT'))
            if 'club_name' not in columns:
                missing_columns.append(('club_name', 'TEXT'))
            if 'notes' not in columns:
                missing_columns.append(('notes', 'TEXT'))

            for col_name, col_type in missing_columns:
                logger.info(f"🔄 Adding {col_name} column to prospects table")
                cursor.execute(f"ALTER TABLE prospects ADD COLUMN {col_name} {col_type}")
                logger.info(f"✅ Added {col_name} column to prospects")

            if not missing_columns:
                logger.info("✅ All ClubOS leads tracking columns exist in prospects table")
        except Exception as e:
            logger.error(f"❌ Migration error for prospects table ClubOS columns: {e}")

        logger.info("✅ Database migrations complete")

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        max_retries: int = 3
    ) -> Any:
        """Execute a database query with proper error handling and retry logic for locked database"""
        logger.debug(f"💾 SQLite Query: {query}")
        logger.debug(f"💾 Parameters: {params}")

        retry_count = 0
        last_error = None

        while retry_count <= max_retries:
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

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() and retry_count < max_retries:
                    retry_count += 1
                    wait_time = 0.1 * (2 ** retry_count)  # Exponential backoff: 0.2s, 0.4s, 0.8s
                    logger.warning(f"⚠️ Database locked, retrying in {wait_time}s (attempt {retry_count}/{max_retries})")
                    time.sleep(wait_time)
                    last_error = e
                    continue
                else:
                    logger.error(f"❌ Database query error after {retry_count} retries: {e}")
                    logger.error(f"❌ Query: {query}")
                    logger.error(f"❌ Parameters: {params}")
                    raise

            except Exception as e:
                logger.error(f"❌ Database query error: {e}")
                logger.error(f"❌ Query: {query}")
                logger.error(f"❌ Parameters: {params}")
                raise

        # If we got here, all retries failed
        if last_error:
            logger.error(f"❌ All {max_retries} retries exhausted for database query")
            raise last_error

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
                # Comp members - FIXED: ClubHub returns lowercase "member"
                query = """SELECT * FROM members
                          WHERE status_message IN ('Comp member', 'Comp Member')
                          ORDER BY full_name"""
            elif category == 'ppv':
                # PPV members - FIXED: ClubHub returns lowercase "pay per visit member"
                query = """SELECT * FROM members
                          WHERE status_message IN ('Pay per visit member', 'Pay Per Visit Member')
                          ORDER BY full_name"""
            elif category == 'staff':
                # Staff members - FIXED: ClubHub returns lowercase "member"
                query = """SELECT * FROM members
                          WHERE status_message IN ('Staff member', 'Staff Member')
                          ORDER BY full_name"""
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

    # --- Helper utilities for member profile aggregation ---
    @staticmethod
    def _normalize_float(value: Any) -> float:
        """Safely convert a numeric-looking value to float."""
        if value in (None, "", "None"):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(Decimal(str(value)))
        except Exception:
            return 0.0

    @staticmethod
    def _as_datetime(value: Any) -> Optional[datetime]:
        """Convert assorted date strings to datetime for calculations."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%m/%d/%Y"):
                try:
                    return datetime.strptime(value.split("Z")[0], fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _serialize_date(value: Any) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _deserialize_json(value: Any) -> Any:
        if not value:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except Exception:
            return None

    @staticmethod
    def _resolve_member_key(member: Dict[str, Any]) -> Optional[str]:
        for key_name in ("prospect_id", "guid", "id"):
            if member.get(key_name):
                return str(member[key_name])
        return None

    def _find_member_record(self, member_identifier: str) -> Optional[sqlite3.Row]:
        """Locate a member using multiple identifier strategies."""
        if not member_identifier:
            return None

        lookups: List[Tuple[str, Tuple[Any, ...]]] = []
        # Try numeric primary key
        if isinstance(member_identifier, (int, float)) or str(member_identifier).isdigit():
            lookups.append(("SELECT * FROM members WHERE id = ? LIMIT 1", (int(member_identifier),)))

        sanitized = str(member_identifier).strip()
        lookups.extend([
            ("SELECT * FROM members WHERE prospect_id = ? LIMIT 1", (sanitized,)),
            ("SELECT * FROM members WHERE guid = ? LIMIT 1", (sanitized,))
        ])

        if " " in sanitized:
            lookups.append(("SELECT * FROM members WHERE LOWER(full_name) = LOWER(?) LIMIT 1", (sanitized,)))

        for query, params in lookups:
            result = self.execute_query(query, params, fetch_one=True)
            if result:
                return result
        return None

    def _build_membership_summary(self, member: Dict[str, Any]) -> Dict[str, Any]:
        """Compile membership billing metrics into a single structure."""
        next_payment_amount = member.get('amount_of_next_payment')
        if not next_payment_amount:
            next_payment_amount = member.get('agreement_recurring_cost')

        return {
            'agreement_id': member.get('agreement_id'),
            'agreement_type': member.get('agreement_type') or 'Membership',
            'agreement_status': member.get('agreement_status') or member.get('status'),
            'agreement_start_date': member.get('agreement_start_date') or member.get('join_date'),
            'agreement_end_date': member.get('agreement_end_date'),
            'amount_past_due': self._normalize_float(member.get('amount_past_due')),
            'base_amount_past_due': self._normalize_float(member.get('base_amount_past_due')),
            'late_fees': self._normalize_float(member.get('late_fees')),
            'missed_payments': int(member.get('missed_payments') or 0),
            'next_payment_date': member.get('date_of_next_payment') or member.get('next_billing_date'),
            'next_payment_amount': self._normalize_float(next_payment_amount),
            'billing_day': member.get('billing_day'),
            'status_message': member.get('status_message') or member.get('status') or 'Unknown',
            'payment_method': member.get('payment_method'),
            'club_name': member.get('club_name'),
            'agreement_recurring_cost': self._normalize_float(member.get('agreement_recurring_cost'))
        }

    def _build_payment_status(
        self,
        membership_summary: Dict[str, Any],
        payment_plan: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        status = {
            'text': 'Current',
            'class': 'success',
            'next_payment_date': membership_summary.get('next_payment_date'),
            'next_payment_amount': membership_summary.get('next_payment_amount'),
            'amount_past_due': membership_summary.get('amount_past_due', 0.0)
        }

        amount_past_due = membership_summary.get('amount_past_due', 0.0)
        if amount_past_due and amount_past_due > 0:
            status['text'] = f"Past Due (${amount_past_due:.2f})"
            status['class'] = 'danger'

        # Warn if payment due within 7 days
        due_date = self._as_datetime(membership_summary.get('next_payment_date'))
        if due_date and due_date >= datetime.now():
            days_until_due = (due_date - datetime.now()).days
            if days_until_due <= 7 and amount_past_due == 0:
                status['text'] = 'Due Soon'
                status['class'] = 'warning'

        if payment_plan:
            plan_status = payment_plan.get('status', 'active')
            status['payment_plan'] = {
                'status': plan_status,
                'next_payment_due': payment_plan.get('next_payment_due'),
                'balance_remaining': payment_plan.get('balance_remaining'),
                'installments_remaining': payment_plan.get('installments_total', 0) - payment_plan.get('installments_paid', 0)
            }

            # Active payment plans downgrade severity unless they are delinquent themselves
            if plan_status in ('active', 'pending') and amount_past_due > 0:
                status['text'] = f"On Payment Plan (${amount_past_due:.2f} past due)"
                status['class'] = 'warning'

        return status

    def _build_agreements_summary(self, member: Dict[str, Any], membership_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        agreements: List[Dict[str, Any]] = []
        if membership_summary.get('agreement_id') or membership_summary.get('agreement_type'):
            agreements.append({
                'agreement_id': membership_summary.get('agreement_id'),
                'agreement_type': membership_summary.get('agreement_type'),
                'start_date': membership_summary.get('agreement_start_date'),
                'end_date': membership_summary.get('agreement_end_date'),
                'rate': membership_summary.get('next_payment_amount') or membership_summary.get('agreement_recurring_cost'),
                'status': membership_summary.get('agreement_status') or membership_summary.get('status_message'),
                'member_rate': membership_summary.get('agreement_recurring_cost')
            })
        return agreements

    def _get_training_packages_for_member(self, member: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match training_clients rows to a member across multiple identifiers."""
        member_key = self._resolve_member_key(member)
        member_name = member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()

        if not member_key and not member_name:
            return []

        rows = self.execute_query(
            """
            SELECT * FROM training_clients
            WHERE clubos_member_id = ?
               OR prospect_id = ?
               OR LOWER(TRIM(member_name)) = LOWER(TRIM(?))
            ORDER BY updated_at DESC
            LIMIT 10
            """,
            (member_key or '', member_key or '', member_name or ''),
            fetch_all=True
        )

        packages: List[Dict[str, Any]] = []
        for row in rows or []:
            row_dict = dict(row)
            package_details = self._deserialize_json(row_dict.get('package_details'))
            active_packages = self._deserialize_json(row_dict.get('active_packages'))
            packages.append({
                'member_name': row_dict.get('member_name'),
                'trainer_name': row_dict.get('trainer_name'),
                'package_type': row_dict.get('training_package') or row_dict.get('package_type'),
                'payment_status': row_dict.get('payment_status') or row_dict.get('status'),
                'sessions_remaining': row_dict.get('sessions_remaining'),
                'total_past_due': self._normalize_float(row_dict.get('total_past_due') or row_dict.get('past_due_amount')),
                'agreement_id': row_dict.get('agreement_id'),
                'active_packages': active_packages,
                'package_details': package_details,
                'last_updated': row_dict.get('updated_at')
            })

        return packages

    def get_payment_plan(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Return payment plan and installments for a member if it exists."""
        if not member_id:
            return None

        plan_row = self.execute_query(
            "SELECT * FROM payment_plans WHERE member_id = ?",
            (str(member_id),),
            fetch_one=True
        )

        if not plan_row:
            return None

        plan = dict(plan_row)
        plan['total_amount'] = self._normalize_float(plan.get('total_amount'))
        plan['balance_remaining'] = self._normalize_float(plan.get('balance_remaining'))
        plan['installment_amount'] = self._normalize_float(plan.get('installment_amount'))

        installments = self.execute_query(
            "SELECT * FROM payment_plan_installments WHERE plan_id = ? ORDER BY installment_number",
            (plan['id'],),
            fetch_all=True
        )

        plan['installments'] = [
            {
                'id': inst['id'],
                'installment_number': inst['installment_number'],
                'due_date': inst['due_date'],
                'amount': self._normalize_float(inst['amount']),
                'status': inst['status'],
                'paid_date': inst['paid_date'],
                'amount_paid': self._normalize_float(inst.get('amount_paid'))
            }
            for inst in installments or []
        ]

        return plan

    def save_payment_plan(self, member_id: str, plan_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create or replace a manual payment plan and its installments."""
        if not member_id:
            raise ValueError('member_id is required for payment plans')

        total_amount = Decimal(str(plan_payload.get('total_amount', 0)))
        installments_total = int(plan_payload.get('installments_total') or plan_payload.get('installment_count') or 0)
        frequency_days = int(plan_payload.get('frequency_days') or 14)
        start_date = plan_payload.get('start_date') or datetime.now().date().isoformat()

        installments_input = plan_payload.get('installments') or []
        if installments_total == 0 and installments_input:
            installments_total = len(installments_input)

        if total_amount <= 0 or installments_total <= 0:
            raise ValueError('Total amount and installments_total must be greater than zero')

        plan_name = plan_payload.get('plan_name') or 'Manual Payment Plan'
        notes = plan_payload.get('notes')
        created_by = plan_payload.get('created_by')

        # Build installments schedule if not provided
        installments: List[Dict[str, Any]] = []

        if installments_input:
            for idx, inst in enumerate(installments_input, start=1):
                due_date = inst.get('due_date')
                amount = Decimal(str(inst.get('amount', 0)))
                installments.append({
                    'installment_number': idx,
                    'due_date': due_date,
                    'amount': float(amount)
                })
        else:
            start_dt = self._as_datetime(start_date) or datetime.now()
            base_amount = (total_amount / installments_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            remainder = total_amount - (base_amount * installments_total)

            for i in range(installments_total):
                due_dt = start_dt + timedelta(days=frequency_days * i)
                amount = base_amount
                if i == installments_total - 1:
                    amount += remainder
                installments.append({
                    'installment_number': i + 1,
                    'due_date': due_dt.date().isoformat(),
                    'amount': float(amount)
                })

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM payment_plans WHERE member_id = ?", (str(member_id),))
            existing = cursor.fetchone()

            plan_fields = (
                plan_name,
                'active',
                float(total_amount),
                float(total_amount),  # reset balance when plan is created
                float(total_amount / installments_total),
                installments_total,
                0,
                frequency_days,
                installments[0]['due_date'] if installments else None,
                None,
                start_date,
                installments[-1]['due_date'] if installments else None,
                notes,
                created_by
            )

            if existing:
                plan_id = existing['id'] if isinstance(existing, sqlite3.Row) else existing[0]
                cursor.execute(
                    """
                    UPDATE payment_plans
                    SET plan_name = ?, status = ?, total_amount = ?, balance_remaining = ?,
                        installment_amount = ?, installments_total = ?, installments_paid = ?,
                        frequency_days = ?, next_payment_due = ?, last_payment_date = ?,
                        start_date = ?, end_date = ?, notes = ?, created_by = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    plan_fields + (plan_id,)
                )
                cursor.execute("DELETE FROM payment_plan_installments WHERE plan_id = ?", (plan_id,))
            else:
                cursor.execute(
                    """
                    INSERT INTO payment_plans (
                        member_id, plan_name, status, total_amount, balance_remaining,
                        installment_amount, installments_total, installments_paid,
                        frequency_days, next_payment_due, last_payment_date,
                        start_date, end_date, notes, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (str(member_id),) + plan_fields
                )
                plan_id = cursor.lastrowid

            for inst in installments:
                cursor.execute(
                    """
                    INSERT INTO payment_plan_installments (
                        plan_id, installment_number, due_date, amount, status
                    ) VALUES (?, ?, ?, ?, 'pending')
                    """,
                    (plan_id, inst['installment_number'], inst['due_date'], inst['amount'])
                )

            # Flag member as exempt from auto-lock routines
            cursor.execute(
                "UPDATE members SET payment_plan_exempt = 1, updated_at = CURRENT_TIMESTAMP WHERE prospect_id = ? OR guid = ?",
                (str(member_id), str(member_id))
            )

            conn.commit()

        return self.get_payment_plan(member_id)

    def mark_payment_plan_installment_paid(
        self,
        member_id: str,
        installment_id: int,
        paid_amount: Optional[float] = None,
        paid_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark a payment plan installment as paid and update plan rollups."""
        paid_date = paid_date or datetime.now().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM payment_plan_installments WHERE id = ?", (installment_id,))
            installment = cursor.fetchone()
            if not installment:
                raise ValueError('Installment not found')

            plan_id = installment['plan_id']
            amount_due = self._normalize_float(installment['amount'])
            amount_to_apply = self._normalize_float(paid_amount) or amount_due

            cursor.execute(
                """
                UPDATE payment_plan_installments
                SET status = 'paid', paid_date = ?, amount_paid = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (paid_date, amount_to_apply, installment_id)
            )

            # Update plan rollups
            cursor.execute("SELECT * FROM payment_plans WHERE id = ?", (plan_id,))
            plan_row = cursor.fetchone()
            if not plan_row:
                raise ValueError('Payment plan not found for installment')

            new_balance = max(0.0, self._normalize_float(plan_row['balance_remaining']) - amount_to_apply)
            installments_paid = int(plan_row['installments_paid'] or 0) + 1

            cursor.execute(
                """
                UPDATE payment_plans
                SET balance_remaining = ?, installments_paid = ?, last_payment_date = ?,
                    next_payment_due = (
                        SELECT due_date FROM payment_plan_installments
                        WHERE plan_id = ? AND status != 'paid'
                        ORDER BY installment_number LIMIT 1
                    ),
                    status = CASE WHEN ? >= installments_total THEN 'completed' ELSE status END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (new_balance, installments_paid, paid_date, plan_id, installments_paid, plan_id)
            )

            # If plan completed, remove exemption flag
            cursor.execute(
                "SELECT status FROM payment_plans WHERE id = ?",
                (plan_id,)
            )
            status_row = cursor.fetchone()
            if status_row and status_row['status'] == 'completed':
                cursor.execute(
                    "UPDATE members SET payment_plan_exempt = 0, updated_at = CURRENT_TIMESTAMP WHERE prospect_id = ? OR guid = ?",
                    (str(member_id), str(member_id))
                )

            conn.commit()

        return self.get_payment_plan(member_id)

    def get_member_profile_context(self, member_identifier: str) -> Optional[Dict[str, Any]]:
        """Aggregate membership, training, invoices, and payment plan data for UI/API."""
        member_row = self._find_member_record(member_identifier)
        if not member_row:
            return None

        member = dict(member_row)
        member_key = self._resolve_member_key(member)

        membership_summary = self._build_membership_summary(member)
        payment_plan = self.get_payment_plan(member_key)
        payment_status = self._build_payment_status(membership_summary, payment_plan)
        agreements = self._build_agreements_summary(member, membership_summary)
        invoices = self.get_member_invoices(member_key) if member_key else []
        training_packages = self._get_training_packages_for_member(member)

        return {
            'member': member,
            'membership_summary': membership_summary,
            'payment_status': payment_status,
            'agreements': agreements,
            'payments': invoices,
            'invoices': invoices,
            'training_packages': training_packages,
            'payment_plan': payment_plan
        }



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