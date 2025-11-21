#!/usr/bin/env python3
"""Debug script to check inbox message ordering"""

import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=" * 80)
print("INBOX MESSAGE ORDER DEBUG")
print("=" * 80)

# Check what columns exist
cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()
print("\nAvailable columns in messages table:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

print("\n" + "=" * 80)
print("NEWEST 10 MESSAGES (by ROWID DESC):")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, id, from_user, content, timestamp, created_at, channel
    FROM messages 
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    ORDER BY ROWID DESC
    LIMIT 10
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    rowid, msg_id, from_user, content, timestamp, created_at, channel = row
    print(f"\n{i}. ROWID: {rowid}")
    print(f"   From: {from_user}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Created: {created_at}")
    print(f"   Content: {content[:80] if content else 'N/A'}...")

print("\n" + "=" * 80)
print("OLDEST 10 MESSAGES (by ROWID ASC):")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, id, from_user, content, timestamp, created_at, channel
    FROM messages 
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    ORDER BY ROWID ASC
    LIMIT 10
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    rowid, msg_id, from_user, content, timestamp, created_at, channel = row
    print(f"\n{i}. ROWID: {rowid}")
    print(f"   From: {from_user}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Created: {created_at}")
    print(f"   Content: {content[:80] if content else 'N/A'}...")

print("\n" + "=" * 80)
print("TIMESTAMP SORTING TEST (DESC):")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, id, from_user, timestamp, created_at
    FROM messages 
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND timestamp IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 10
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    rowid, msg_id, from_user, timestamp, created_at = row
    print(f"{i}. ROWID: {rowid}, Timestamp: {timestamp}, From: {from_user}")

print("\n" + "=" * 80)
print("CREATED_AT SORTING TEST (DESC):")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, id, from_user, timestamp, created_at
    FROM messages 
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND created_at IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 10
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    rowid, msg_id, from_user, timestamp, created_at = row
    print(f"{i}. ROWID: {rowid}, Created: {created_at}, From: {from_user}")

conn.close()
print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
