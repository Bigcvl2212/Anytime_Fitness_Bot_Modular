#!/usr/bin/env python3
"""
Check what status messages we actually have in the database
"""

import sqlite3
import os

# Direct database access
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== ALL STATUS MESSAGES IN DATABASE ===')

# Get all unique status messages with counts
cursor.execute("SELECT status_message, COUNT(*) FROM members WHERE status_message IS NOT NULL AND status_message != '' GROUP BY status_message ORDER BY COUNT(*) DESC")
all_statuses = cursor.fetchall()

if all_statuses:
    print(f'Total unique status patterns: {len(all_statuses)}')
    print('\nAll status messages (ordered by frequency):')
    for status, count in all_statuses:
        print(f'  "{status}": {count} members')
else:
    print('❌ NO status messages found in database')

print(f'\n=== TOTAL MEMBERS IN DATABASE ===')
cursor.execute("SELECT COUNT(*) FROM members")
total_members = cursor.fetchone()[0]
print(f'Total members: {total_members}')

print(f'\n=== MEMBERS WITH NULL/EMPTY STATUS ===')
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message IS NULL OR status_message = ''")
null_status = cursor.fetchone()[0]
print(f'Members with null/empty status: {null_status}')

conn.close()
