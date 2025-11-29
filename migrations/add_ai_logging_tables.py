#!/usr/bin/env python3
"""
Database Migration: Add AI Logging Tables
Adds tables for tracking AI responses, decisions, and workflow triggers
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_bot.db')
    return sqlite3.connect(db_path)


def migrate():
    """Run migration to add AI logging tables"""
    print("=" * 80)
    print("AI LOGGING TABLES MIGRATION")
    print("=" * 80)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Table 1: AI Response Log
        print("\n1. Creating ai_response_log table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_response_log (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                member_id TEXT,
                intent TEXT NOT NULL,
                confidence REAL NOT NULL,
                response_sent TEXT,
                sent_at TEXT,
                workflow_triggered INTEGER DEFAULT 0,
                workflow_name TEXT,
                auto_sent INTEGER DEFAULT 1,
                flagged_for_review INTEGER DEFAULT 0,
                review_reason TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')
        print("   [OK] ai_response_log table created")

        # Table 2: Workflow Execution Log
        print("\n2. Creating workflow_execution_log table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_execution_log (
                id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                trigger_data TEXT,
                member_id TEXT,
                execution_status TEXT,
                result_data TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                error_message TEXT
            )
        ''')
        print("   [OK] workflow_execution_log table created")

        # Table 3: AI Conversations
        print("\n3. Creating ai_conversations table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                member_id TEXT,
                agent_type TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        print("   [OK] ai_conversations table created")

        # Table 4: AI Statistics
        print("\n4. Creating ai_statistics table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_date TEXT NOT NULL,
                messages_processed INTEGER DEFAULT 0,
                auto_responses_sent INTEGER DEFAULT 0,
                workflows_triggered INTEGER DEFAULT 0,
                human_reviews_flagged INTEGER DEFAULT 0,
                avg_confidence REAL,
                total_errors INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(stat_date)
            )
        ''')
        print("   [OK] ai_statistics table created")

        # Add columns to existing messages table
        print("\n5. Updating messages table with AI columns...")

        # Check which columns already exist
        cursor.execute("PRAGMA table_info(messages)")
        existing_columns = [row[1] for row in cursor.fetchall()]

        columns_to_add = [
            ('ai_processed', 'INTEGER', '0'),
            ('ai_responded', 'INTEGER', '0'),
            ('ai_confidence', 'REAL', 'NULL'),
            ('requires_human_review', 'INTEGER', '0'),
            ('review_reason', 'TEXT', 'NULL'),
            ('last_ai_response_at', 'TEXT', 'NULL')
        ]

        for col_name, col_type, default_val in columns_to_add:
            if col_name not in existing_columns:
                try:
                    if default_val == 'NULL':
                        cursor.execute(f'ALTER TABLE messages ADD COLUMN {col_name} {col_type}')
                    else:
                        cursor.execute(f'ALTER TABLE messages ADD COLUMN {col_name} {col_type} DEFAULT {default_val}')
                    print(f"   [OK] Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    print(f"   [WARNING] Column {col_name} may already exist: {e}")
            else:
                print(f"   [SKIP] Column {col_name} already exists")

        # Create indexes for performance
        print("\n6. Creating indexes...")

        indexes = [
            ('idx_ai_response_member', 'ai_response_log', 'member_id'),
            ('idx_ai_response_intent', 'ai_response_log', 'intent'),
            ('idx_ai_response_sent_at', 'ai_response_log', 'sent_at'),
            ('idx_workflow_exec_member', 'workflow_execution_log', 'member_id'),
            ('idx_workflow_exec_name', 'workflow_execution_log', 'workflow_name'),
            ('idx_ai_conv_session', 'ai_conversations', 'session_id'),
            ('idx_ai_conv_member', 'ai_conversations', 'member_id'),
            ('idx_messages_ai_processed', 'messages', 'ai_processed'),
            ('idx_messages_review', 'messages', 'requires_human_review')
        ]

        for idx_name, table_name, column_name in indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})')
                print(f"   [OK] Created index: {idx_name}")
            except sqlite3.OperationalError as e:
                print(f"   [SKIP] Index {idx_name} may already exist")

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 80)
        print("[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nAI logging tables are ready!")
        print("\nTables created:")
        print("  1. ai_response_log       - Tracks all AI responses")
        print("  2. workflow_execution_log - Tracks workflow triggers")
        print("  3. ai_conversations      - Stores AI conversation history")
        print("  4. ai_statistics         - Daily AI performance metrics")
        print("\nColumns added to messages table:")
        print("  - ai_processed, ai_responded, ai_confidence")
        print("  - requires_human_review, review_reason")
        print("  - last_ai_response_at")

        return True

    except Exception as e:
        print(f"\n[ERROR] MIGRATION FAILED: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def verify_migration():
    """Verify migration was successful"""
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    try:
        # Check each table exists
        tables = ['ai_response_log', 'workflow_execution_log', 'ai_conversations', 'ai_statistics']

        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"[OK] {table}: EXISTS (rows: {count})")
            else:
                print(f"[ERROR] {table}: NOT FOUND")

        # Check messages table columns
        cursor.execute("PRAGMA table_info(messages)")
        columns = [row[1] for row in cursor.fetchall()]

        ai_columns = ['ai_processed', 'ai_responded', 'ai_confidence', 'requires_human_review']
        print("\nMessages table AI columns:")
        for col in ai_columns:
            if col in columns:
                print(f"[OK] {col}: EXISTS")
            else:
                print(f"[ERROR] {col}: MISSING")

    finally:
        conn.close()


if __name__ == '__main__':
    print("\nStarting AI logging tables migration...")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    success = migrate()

    if success:
        verify_migration()
        print("\n[SUCCESS] Migration complete! AI logging is now enabled.\n")
        sys.exit(0)
    else:
        print("\n[ERROR] Migration failed. Please check errors above.\n")
        sys.exit(1)
