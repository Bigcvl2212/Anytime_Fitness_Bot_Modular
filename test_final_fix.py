import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get latest sync time
cursor.execute("SELECT MAX(created_at) FROM messages WHERE channel='clubos'")
latest_sync = cursor.fetchone()[0]

print("=" * 80)
print(f"FINAL FIX: Latest sync = {latest_sync}")
print("Ordering by ROWID ASC within latest sync (ClubOS returns newest first)")
print("=" * 80)

cursor.execute("""
    SELECT ROWID, from_user, timestamp, created_at
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    AND created_at = ?
    ORDER BY ROWID ASC
    LIMIT 20
""", (latest_sync,))

print("\nTop 20 messages (should be Sophia Kovacs, Steve Tapp, Mark Benzinger...):\n")
for i, row in enumerate(cursor.fetchall(), 1):
    rowid, from_user, timestamp, created_at = row
    print(f"{i}. From: {from_user:25} | Timestamp: {timestamp:15} | ROWID: {rowid}")

conn.close()
print("\n" + "=" * 80)
print("✅ SUCCESS if Sophia Kovacs, Steve Tapp, Mark Benzinger are at the top!")
print("=" * 80)
