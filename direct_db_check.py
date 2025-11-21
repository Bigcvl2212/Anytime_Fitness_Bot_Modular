#!/usr/bin/env python3
"""
Direct database check without Flask startup
"""

import sqlite3
import os

# Direct database access
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
print(f'Database path: {db_path}')
print(f'Database exists: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print('\n=== DATABASE CONTENTS ===')
    
    # Check members table
    try:
        cursor.execute("SELECT COUNT(*) FROM members")
        member_count = cursor.fetchone()[0]
        print(f'Total members: {member_count}')
        
        if member_count > 0:
            # Check status_message patterns
            cursor.execute("SELECT DISTINCT status_message, COUNT(*) FROM members GROUP BY status_message ORDER BY COUNT(*) DESC LIMIT 10")
            statuses = cursor.fetchall()
            print('\nTop status messages:')
            for status, count in statuses:
                print(f'  "{status}": {count}')
        else:
            print('❌ No members in database')
            
    except Exception as e:
        print(f'Error checking members: {e}')
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f'\nTables in database: {[table[0] for table in tables]}')
    
    conn.close()
else:
    print('❌ Database file does not exist')
