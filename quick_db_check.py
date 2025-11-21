#!/usr/bin/env python3
"""
Direct database check without any imports
"""

import sqlite3
import os

# Direct database access
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
print(f'Database path: {db_path}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check members table
    cursor.execute("SELECT COUNT(*) FROM members")
    member_count = cursor.fetchone()[0]
    print(f'✅ Total members: {member_count}')
    
    if member_count > 0:
        # Check status_message patterns for categorization
        cursor.execute("SELECT DISTINCT status_message, COUNT(*) FROM members WHERE status_message IS NOT NULL GROUP BY status_message ORDER BY COUNT(*) DESC LIMIT 15")
        statuses = cursor.fetchall()
        print('\n📊 Status message patterns:')
        for status, count in statuses:
            print(f'  "{status}": {count}')
            
        # Check sample member data
        cursor.execute("SELECT first_name, last_name, status_message FROM members LIMIT 5")
        samples = cursor.fetchall()
        print('\n👥 Sample members:')
        for member in samples:
            print(f'  {member[0]} {member[1]}: "{member[2]}"')
    
    conn.close()
else:
    print('❌ Database file does not exist')
