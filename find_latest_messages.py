import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get today's date
today = '2025-10-09%'  # Pattern match for today

print("=" * 80)
print(f"Messages synced TODAY (October 9, 2025):")
print("=" * 80)

cursor.execute("""
    SELECT COUNT(*), MIN(created_at), MAX(created_at)
    FROM messages
    WHERE created_at LIKE ?
    AND channel = 'clubos'
""", (today,))

row = cursor.fetchone()
print(f"\nCount: {row[0]}")
print(f"Earliest sync: {row[1]}")
print(f"Latest sync: {row[2]}")

print("\n" + "=" * 80)
print("Check distinct sync times:")
print("=" * 80)

cursor.execute("""
    SELECT DISTINCT created_at, COUNT(*) as msg_count
    FROM messages
    WHERE channel = 'clubos'
    GROUP BY created_at
    ORDER BY created_at DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row[0]} - {row[1]} messages")

print("\n" + "=" * 80)
print("SOLUTION: Messages from the MOST RECENT sync (top group above)")
print("=" * 80)

# Get the most recent sync timestamp
cursor.execute("""
    SELECT MAX(created_at)
    FROM messages
    WHERE channel = 'clubos'
""")
latest_sync = cursor.fetchone()[0]
print(f"\nLatest sync: {latest_sync}")

cursor.execute("""
    SELECT ROWID, from_user, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND created_at = ?
    AND from_user IS NOT NULL
    AND from_user != ''
    ORDER BY ROWID DESC
    LIMIT 15
""", (latest_sync,))

print(f"\nTop 15 messages from latest sync (by ROWID DESC):\n")
for i, row in enumerate(cursor.fetchall(), 1):
    print(f"{i}. From: {row[1]:25} | Display: {row[2]:15} | ROWID: {row[0]}")

conn.close()
