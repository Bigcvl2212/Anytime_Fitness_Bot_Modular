#!/usr/bin/env python3
"""Test the fixed inbox query"""
import sqlite3
import sys

# Add UTF-8 support for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db_path = r'C:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\gym_bot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# The EXACT query from messaging.py
cursor.execute("""
    SELECT
        id, content, from_user, owner_id, created_at, channel,
        timestamp, status, message_type, ROWID
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    AND ROWID >= 863319
    ORDER BY ROWID ASC
    LIMIT 20
""")

messages = cursor.fetchall()

print("✅ FIXED INBOX QUERY RESULTS:")
print("-" * 80)
for i, msg in enumerate(messages, 1):
    msg_id, content, from_user, owner_id, created_at, channel, timestamp, status, msg_type, rowid = msg
    content_preview = content[:50] + "..." if len(content) > 50 else content
    print(f"{i}. {from_user:25} | {timestamp:15} | ROWID: {rowid}")

conn.close()

print("\n" + "=" * 80)
print("Expected order: Sophia Kovacs, Steve Tapp, Steve Tapp, Mark Benzinger, Seth Phillips")
