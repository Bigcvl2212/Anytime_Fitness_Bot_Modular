#!/usr/bin/env python3
"""
Fix Database Schema - Add Missing Columns
"""
import sqlite3
from datetime import datetime

print("=" * 60)
print("FIXING DATABASE SCHEMA")
print("=" * 60)

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Add missing columns to members table
print("\nAdding missing columns to members table...")
missing_member_columns = [
    ('agreement_id', 'TEXT'),
    ('agreement_guid', 'TEXT'),
    ('agreement_type', 'TEXT'),
    ('agreement_recurring_cost', 'REAL'),
]

for col_name, col_type in missing_member_columns:
    try:
        cursor.execute(f"ALTER TABLE members ADD COLUMN {col_name} {col_type}")
        print(f"  Added {col_name} column")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f"  {col_name} column already exists")
        else:
            print(f"  Error adding {col_name}: {e}")

# Add missing columns to prospects table
print("\nAdding missing columns to prospects table...")
missing_prospect_columns = [
    ('mobile_phone', 'TEXT'),
    ('phone', 'TEXT'),
    ('address', 'TEXT'),
    ('city', 'TEXT'),
    ('state', 'TEXT'),
    ('zip_code', 'TEXT'),
]

for col_name, col_type in missing_prospect_columns:
    try:
        cursor.execute(f"ALTER TABLE prospects ADD COLUMN {col_name} {col_type}")
        print(f"  Added {col_name} column")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f"  {col_name} column already exists")
        else:
            print(f"  Error adding {col_name}: {e}")

# Create bulk_checkin_runs table
print("\nCreating bulk_checkin_runs table...")
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bulk_checkin_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT UNIQUE,
            status TEXT,
            total_members INTEGER,
            processed_count INTEGER,
            success_count INTEGER,
            error_count INTEGER,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_log TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  Created bulk_checkin_runs table")
except Exception as e:
    print(f"  Error creating table: {e}")

conn.commit()
conn.close()

print("\n" + "=" * 60)
print("DATABASE SCHEMA FIXED")
print("=" * 60)
