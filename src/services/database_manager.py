#!/usr/bin/env python3
"""
Simple SQLite Database Manager Service
Handles all database operations using SQLite only
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
    """Simple SQLite-only Database Manager for gym data management"""

    def __init__(self, db_path=None):
        self.last_refresh = None
        self.refresh_interval = 3600  # 1 hour in seconds
        self.db_type = 'sqlite'  # Always SQLite

        # Use SQLite database
        if db_path:
            self.db_path = db_path
        else:
            # Default to gym_bot.db in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(project_root, 'gym_bot.db')

        logger.info(f"💾 Using SQLite database: {self.db_path}")

        # Initialize the database schema
        self.init_schema()

    def get_connection(self):
        """Get SQLite database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def init_schema(self):
        """Initialize SQLite database schema"""
        logger.info("💾 Initializing SQLite schema...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
            if cursor.fetchone():
                logger.info("✅ SQLite schema already exists, skipping creation")
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

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute a database query with proper error handling"""
        logger.info(f"💾 SQLite Query: {query}")
        logger.info(f"💾 Parameters: {params}")

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

    def save_members_to_db(self, members_data):
        """Save members data to SQLite database"""
        if not members_data:
            logger.warning("⚠️ No members data to save")
            return

        logger.info(f"💾 Saving {len(members_data)} members to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for member in members_data:
                    # Use REPLACE to handle updates - updated to match current schema
                    cursor.execute("""
                        REPLACE INTO members (
                            prospect_id, guid, first_name, last_name, full_name, email,
                            phone, mobile_phone, status, status_message, member_type, user_type,
                            join_date, amount_past_due, date_of_next_payment,
                            base_amount_past_due, late_fees, missed_payments,
                            agreement_recurring_cost, agreement_id, agreement_guid, agreement_type,
                            club_name, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        member.get('prospect_id') or member.get('id'),
                        member.get('guid'),
                        member.get('first_name') or member.get('firstName'),
                        member.get('last_name') or member.get('lastName'),
                        member.get('full_name'),
                        member.get('email'),
                        member.get('phone'),
                        member.get('mobile_phone'),
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
                logger.info(f"✅ Saved {len(members_data)} members to database")

        except Exception as e:
            logger.error(f"❌ Error saving members: {e}")
            raise

    def save_prospects_to_db(self, prospects_data):
        """Save prospects data to SQLite database"""
        if not prospects_data:
            logger.warning("⚠️ No prospects data to save")
            return

        logger.info(f"💾 Saving {len(prospects_data)} prospects to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for prospect in prospects_data:
                    cursor.execute("""
                        REPLACE INTO prospects (
                            prospect_id, first_name, last_name, email, mobile_phone,
                            status, source, interest_level, club_name, created_date,
                            last_contact_date, notes, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prospect.get('prospect_id'),
                        prospect.get('first_name'),
                        prospect.get('last_name'),
                        prospect.get('email'),
                        prospect.get('mobile_phone'),
                        prospect.get('status'),
                        prospect.get('source'),
                        prospect.get('interest_level'),
                        prospect.get('club_name'),
                        prospect.get('created_date'),
                        prospect.get('last_contact_date'),
                        prospect.get('notes'),
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"✅ Saved {len(prospects_data)} prospects to database")

        except Exception as e:
            logger.error(f"❌ Error saving prospects: {e}")
            raise

    def save_training_clients_to_db(self, training_data):
        """Save training clients data to SQLite database"""
        if not training_data:
            logger.warning("⚠️ No training clients data to save")
            return

        logger.info(f"💾 Saving {len(training_data)} training clients to SQLite database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                for client in training_data:
                    cursor.execute("""
                        REPLACE INTO training_clients (
                            prospect_id, member_name, email, phone, status, trainer_name,
                            package_type, sessions_total, sessions_used, sessions_remaining,
                            package_cost, past_due_amount, next_session_date,
                            last_session_date, club_name, created_date, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        client.get('prospect_id'),
                        client.get('member_name'),
                        client.get('email'),
                        client.get('phone'),
                        client.get('status'),
                        client.get('trainer_name'),
                        client.get('package_type'),
                        int(client.get('sessions_total', 0)),
                        int(client.get('sessions_used', 0)),
                        int(client.get('sessions_remaining', 0)),
                        float(client.get('package_cost', 0.0)),
                        float(client.get('past_due_amount', 0.0)),
                        client.get('next_session_date'),
                        client.get('last_session_date'),
                        client.get('club_name'),
                        client.get('created_date'),
                        datetime.now().isoformat()
                    ))

                conn.commit()
                logger.info(f"✅ Saved {len(training_data)} training clients to database")

        except Exception as e:
            logger.error(f"❌ Error saving training clients: {e}")
            raise

    def get_members(self, limit=None):
        """Get members from database"""
        query = "SELECT * FROM members ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, fetch_all=True)

    def get_prospects(self, limit=None):
        """Get prospects from database"""
        query = "SELECT * FROM prospects ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, fetch_all=True)

    def get_training_clients(self, limit=None):
        """Get training clients from database"""
        query = "SELECT * FROM training_clients ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"

        return self.execute_query(query, fetch_all=True)

    def get_past_due_members(self, min_amount=0):
        """Get members with past due amounts"""
        query = "SELECT * FROM members WHERE amount_past_due > ? ORDER BY amount_past_due DESC"
        return self.execute_query(query, (min_amount,), fetch_all=True)

    def get_database_stats(self):
        """Get database statistics"""
        stats = {}

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

    def get_cursor(self, connection=None):
        """Get database cursor (for compatibility with existing code)"""
        if connection:
            return connection.cursor()
        conn = self.get_connection()
        return conn.cursor()

    def close_connection(self, connection=None):
        """Close database connection (no-op for SQLite as connections are context-managed)"""
        if connection:
            connection.close()
        pass

    def save_messages_to_db(self, messages_data):
        """Save messages data to SQLite database"""
        if not messages_data:
            logger.warning("⚠️ No messages data to save")
            return

        logger.info(f"💾 Saving {len(messages_data)} messages to SQLite database...")

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
                logger.info(f"✅ Saved {len(messages_data)} messages to database")

        except Exception as e:
            logger.error(f"❌ Error saving messages: {e}")
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

    def save_invoice(self, invoice_data):
        """Save invoice data to database"""
        try:
            # For now, just log the invoice since we don't have an invoices table
            # This could be expanded to create an invoices table if needed
            logger.info(f"💾 Invoice saved (logged): {invoice_data.get('id', 'unknown')} for ${invoice_data.get('total_amount', 0)}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving invoice: {e}")
            return False

    def get_member_invoices(self, member_id):
        """Get invoices for a specific member"""
        try:
            # For now, return empty list since we don't have an invoices table
            # This could be expanded to query an actual invoices table if needed
            logger.info(f"📋 Getting invoices for member {member_id} (not implemented yet)")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting member invoices for {member_id}: {e}")
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