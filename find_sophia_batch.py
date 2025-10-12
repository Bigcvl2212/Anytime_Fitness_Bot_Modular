import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Find the created_at time that contains Sophia Kovacs with "2:14 PM"
cursor.execute("""
    SELECT created_at, COUNT(*) as msg_count
    FROM messages
    WHERE channel = 'clubos'
    AND created_at >= (SELECT MAX(created_at) - 30 FROM messages WHERE channel = 'clubos')
    GROUP BY created_at
    ORDER BY created_at DESC
""")

print("Recent sync batches (last 30 seconds):\n")
for row in cursor.fetchall():
    print(f"Time: {row[0]}, Count: {row[1]} messages")

# Now find which batch has Sophia with "2:14 PM"
cursor.execute("""
    SELECT created_at
    FROM messages
    WHERE from_user LIKE '%Sophia%'
    AND timestamp = '2:14 PM'
    LIMIT 1
""")

sophia_time = cursor.fetchone()
if sophia_time:
    print(f"\n✓ Sophia Kovacs '2:14 PM' is in batch: {sophia_time[0]}")
    
    # Test query with that specific time
    cursor.execute("""
        SELECT ROWID, from_user, timestamp
        FROM messages
        WHERE channel = 'clubos'
        AND created_at = ?
        AND from_user IS NOT NULL
        AND from_user != ''
        ORDER BY ROWID ASC
        LIMIT 10
    """, sophia_time)
    
    print("\nFirst 10 messages from Sophia's batch:\n")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {row[1]:25} | {row[2]:15} | ROWID: {row[0]}")

conn.close()
