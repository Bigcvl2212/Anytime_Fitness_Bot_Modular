import sqlite3
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()
cursor.execute("SELECT ROWID, from_user, timestamp, created_at FROM messages WHERE from_user LIKE '%Sophia%' OR from_user LIKE '%Steve Tapp%' ORDER BY ROWID DESC LIMIT 10")
for r in cursor.fetchall():
    print(f"ROWID: {r[0]}, From: {r[1]}, Time: {r[2]}, Created: {r[3]}")
conn.close()
