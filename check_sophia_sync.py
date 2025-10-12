import sqlite3
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Find the exact created_at time for Sophia's message
cursor.execute("SELECT created_at FROM messages WHERE ROWID = 863319")
sophia_time = cursor.fetchone()[0]
print(f"Sophia's sync time: {sophia_time}")

# Find MIN and MAX ROWID for that sync
cursor.execute("SELECT MIN(ROWID), MAX(ROWID) FROM messages WHERE created_at = ?", (sophia_time,))
r = cursor.fetchone()
print(f"ROWID range for that sync: {r[0]} to {r[1]}")

# Show first 10 messages from that sync
cursor.execute("""
    SELECT ROWID, from_user, timestamp 
    FROM messages 
    WHERE created_at = ? 
    ORDER BY ROWID ASC 
    LIMIT 10
""", (sophia_time,))

print("\nFirst 10 messages (ROWID ASC):")
for row in cursor.fetchall():
    print(f"ROWID: {row[0]}, From: {row[1]}, Time: {row[2]}")

conn.close()
