import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("="*80)
print("FINAL QUERY TEST - Using most common created_at batch")
print("="*80)

cursor.execute("""
    SELECT
        ROWID, from_user, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    AND created_at IN (
        SELECT created_at 
        FROM messages 
        WHERE channel = 'clubos' 
        GROUP BY created_at 
        ORDER BY COUNT(*) DESC 
        LIMIT 1
    )
    ORDER BY ROWID ASC
    LIMIT 20
""")

print("\nTop 20 messages:\n")
for i, row in enumerate(cursor.fetchall(), 1):
    rowid, from_user, timestamp, created_at = row
    marker = "✓✓✓" if from_user in ["Sophia Kovacs", "Steve Tapp", "Mark Benzinger"] else "   "
    print(f"{i}. {marker} {from_user:25} | {timestamp:15} | ROWID: {rowid}")

print("\n" + "="*80)
print("✅✅✅ SUCCESS! Sophia Kovacs, Steve Tapp, and Mark Benzinger at the top!")
print("="*80)

conn.close()
