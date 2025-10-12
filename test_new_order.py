import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=" * 80)
print("TESTING NEW QUERY: ORDER BY timestamp DESC, ROWID DESC")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, from_user, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    ORDER BY timestamp DESC, ROWID DESC
    LIMIT 20
""")

print("\nTop 20 messages:\n")
for i, row in enumerate(cursor.fetchall(), 1):
    rowid, from_user, timestamp, created_at = row
    print(f"{i}. From: {from_user:25} | Timestamp: {timestamp:30} | ROWID: {rowid}")

print("\n" + "=" * 80)
print("Messages with ISO timestamps should appear first (2025-10-...)")
print("=" * 80)

conn.close()
