import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("="*80)
print("FINAL FIX - Most recent 10 seconds of messages, sorted by created_at DESC, ROWID ASC")
print("="*80)

cursor.execute("""
    SELECT
        ROWID, from_user, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    AND created_at >= (
        SELECT MAX(created_at) - 10 
        FROM messages 
        WHERE channel = 'clubos'
    )
    ORDER BY created_at DESC, ROWID ASC
    LIMIT 20
""")

print("\nTop 20 messages:\n")
for i, row in enumerate(cursor.fetchall(), 1):
    rowid, from_user, timestamp, created_at = row
    marker = "✓✓✓" if from_user in ["Sophia Kovacs", "Steve Tapp", "Mark Benzinger"] else "   "
    print(f"{i}. {marker} {from_user:25} | {timestamp:15} | Created: {created_at}")

print("\n" + "="*80)
conn.close()
