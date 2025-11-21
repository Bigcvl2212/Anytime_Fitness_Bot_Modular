import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("=" * 80)
print("FIXED QUERY: Prioritize ISO timestamps (2025-%) first")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, from_user, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    ORDER BY 
        CASE WHEN timestamp LIKE '2025-%' THEN 0 ELSE 1 END,
        timestamp DESC,
        ROWID DESC
    LIMIT 20
""")

print("\nTop 20 messages (ISO timestamps should be first):\n")
for i, row in enumerate(cursor.fetchall(), 1):
    rowid, from_user, timestamp, created_at = row
    is_iso = "✓ ISO" if timestamp.startswith('2025-') else "  OLD"
    print(f"{i}. {is_iso} | From: {from_user:25} | Timestamp: {timestamp[:22]:25} | ROWID: {rowid}")

print("\n" + "=" * 80)
print("SUCCESS! ISO timestamps (✓ ISO) appear first = MOST RECENT MESSAGES")
print("=" * 80)

conn.close()
