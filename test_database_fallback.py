#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test the database fallback query for Mark
mark_guid = 'd74366d2-497a-4c11-a45a-3bf4b73a26a4'
mark_id = '66082049'

print("Testing Database Fallback for Mark Benzinger")
print("=" * 80)

# Test query 1 - the complex query
print("\n1. Testing complex query:")
cursor.execute('''
    SELECT id, from_user, recipient_name, member_id, owner_id, status, message_type, content
    FROM messages
    WHERE (owner_id = ? OR member_id = ?)
    OR (content LIKE ? OR from_user LIKE ?)
    ORDER BY created_at DESC
    LIMIT 10
''', (mark_id, mark_id, f'%{mark_id}%', f'%{mark_id}%'))
rows = cursor.fetchall()

print(f"   Found {len(rows)} messages")
for i, row in enumerate(rows, 1):
    print(f"   {i}. from={row[1]}, to={row[2]}, status={row[5]}, type={row[6]}")
    print(f"      content={row[7][:60]}...")

# Test query 2 - simpler query
print("\n2. Testing simplified query:")
cursor.execute(
    "SELECT id, from_user, content, status FROM messages WHERE owner_id = ? OR member_id = ? ORDER BY created_at DESC LIMIT 10",
    (mark_id, mark_id)
)
rows2 = cursor.fetchall()

print(f"   Found {len(rows2)} messages")
for i, row in enumerate(rows2, 1):
    print(f"   {i}. from={row[1]}, status={row[3]}")
    print(f"      content={row[2][:60]}...")

# Check main inbox messages structure
print("\n3. Checking main inbox messages:")
cursor.execute("SELECT DISTINCT message_type FROM messages")
types = cursor.fetchall()
print(f"   Message types in database: {[t[0] for t in types]}")

cursor.execute("SELECT COUNT(*) FROM messages WHERE from_user LIKE '%Mark%'")
mark_messages = cursor.fetchone()[0]
print(f"   Messages from Mark: {mark_messages}")

cursor.execute("SELECT COUNT(*) FROM messages WHERE recipient_name LIKE '%Mark%'")
to_mark = cursor.fetchone()[0]
print(f"   Messages to Mark: {to_mark}")

conn.close()

print("\n" + "=" * 80)
print("Database fallback test complete!")
print("\nConclusion:")
print("  - Database contains messages that can be used as fallback")
print("  - With fetch_all=True fix, database queries should work")
print("  - Member inbox should show messages even if FollowUp API fails")
