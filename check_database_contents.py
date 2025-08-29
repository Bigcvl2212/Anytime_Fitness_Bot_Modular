#!/usr/bin/env python3
"""
Quick check of database contents
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

if not os.path.exists(db_path):
    print(f"❌ Database file not found at: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== DATABASE CONTENTS SUMMARY ===')

# Check each table
tables = ['members', 'prospects', 'training_clients']

for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f'{table}: {count} records')
        
        if count > 0:
            # Show sample data
            cursor.execute(f"SELECT * FROM {table} LIMIT 1")
            columns = [description[0] for description in cursor.description]
            sample = cursor.fetchone()
            print(f'  Sample columns: {", ".join(columns[:5])}...')
            if sample:
                print(f'  Sample data: {sample[:5]}...')
    except Exception as e:
        print(f'{table}: ERROR - {e}')

# Check funding cache
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='funding_status_cache'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM funding_status_cache")
        count = cursor.fetchone()[0]
        print(f'funding_status_cache: {count} records')
    else:
        print('funding_status_cache: Table does not exist')
except Exception as e:
    print(f'funding_status_cache: ERROR - {e}')

conn.close()
