#!/usr/bin/env python3
"""
Create local SQLite database for local development
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

def create_database():
    """Create SQLite database with basic schema"""
    print("🔧 Creating local SQLite database...")

    # Database path for local development (same directory as script)
    script_dir = Path(__file__).parent
    db_path = script_dir / 'gym_bot.db'

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create basic tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS members (
            prospect_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            mobile_phone TEXT,
            status TEXT,
            status_message TEXT,
            member_type TEXT,
            join_date TEXT,
            amount_past_due REAL DEFAULT 0,
            date_of_next_payment TEXT,
            agreement_id TEXT,
            agreement_guid TEXT,
            agreement_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS prospects (
            prospect_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            mobile_phone TEXT,
            status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS training_clients (
            member_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            mobile_phone TEXT,
            package_details TEXT,
            past_due_amount REAL DEFAULT 0,
            total_past_due REAL DEFAULT 0,
            payment_status TEXT,
            status_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS member_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    # Create tables
    for table_sql in tables:
        cursor.execute(table_sql)
        print(f"✅ Created table")

    # Insert some sample data
    cursor.execute("""
        INSERT OR IGNORE INTO members (prospect_id, first_name, last_name, full_name, email, status_message)
        VALUES ('TEST123', 'Test', 'User', 'Test User', 'test@example.com', 'Current')
    """)

    # Commit changes
    conn.commit()
    conn.close()

    print(f"✅ Database created at: {db_path}")
    print(f"📊 Database size: {os.path.getsize(db_path)} bytes")

    return True

if __name__ == "__main__":
    create_database()

