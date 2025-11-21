import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print('=== Messages synced today with November timestamps ===')
cursor.execute("""
    SELECT from_user, created_at, timestamp
    FROM messages
    WHERE channel=? AND created_at LIKE ? AND timestamp LIKE ?
    ORDER BY ROWID DESC LIMIT 5
""", ('clubos', '2025-11-21%', '%Nov%'))

results = cursor.fetchall()
if results:
    for r in results:
        print(f'From: {r[0]}, Created: {r[1]}, ClubOS Time: {r[2]}')
else:
    print('NO MESSAGES WITH NOVEMBER TIMESTAMP SYNCED TODAY')

print('\n=== All unique timestamps from todays sync (last 20) ===')
cursor.execute("""
    SELECT DISTINCT timestamp
    FROM messages
    WHERE channel=? AND created_at LIKE ?
    ORDER BY ROWID DESC LIMIT 20
""", ('clubos', '2025-11-21%'))

for r in cursor.fetchall():
    print(f'  {r[0]}')

conn.close()
