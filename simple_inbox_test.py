import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("Top 15 messages with new sorting (created_at DESC, ROWID DESC):\n")

cursor.execute("""
    SELECT ROWID, from_user, timestamp, created_at
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
    print(f"{i}. From: {row[1]:25} | Display: {row[2]:15} | Created: {row[3]} | ROWID: {row[0]}")

conn.close()
