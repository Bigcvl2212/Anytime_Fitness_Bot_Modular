#!/usr/bin/env python3
"""Test the fixed inbox sorting"""

import sqlite3

# Connect to database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=" * 80)
print("FIXED INBOX QUERY - Top 15 messages (sorted by created_at DESC, ROWID DESC)")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, id, from_user, content, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    ORDER BY created_at DESC, ROWID DESC
    LIMIT 15
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    rowid, msg_id, from_user, content, timestamp, created_at = row
    print(f"\n{i}. From: {from_user}")
    print(f"   Created: {created_at}")
    print(f"   Display Time: {timestamp}")
    print(f"   ROWID: {rowid}")
    print(f"   Content: {content[:80]}...")

conn.close()
print("\n" + "=" * 80)
print("This should show the most recently synced messages first")
print("=" * 80)
