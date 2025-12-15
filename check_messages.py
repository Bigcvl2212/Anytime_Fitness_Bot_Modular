import sqlite3
import os

db_path = r'C:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\gym_bot.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check most recent messages
print("--- Most recent 10 messages ---")
cur.execute('''
    SELECT id, from_user, timestamp, substr(content,1,60), ai_processed
    FROM messages 
    WHERE channel = 'clubos'
    ORDER BY timestamp DESC
    LIMIT 10
''')
for row in cur.fetchall():
    print(f"ai_proc={row[4]} | {row[2]} | {row[1]} | {row[3]}")

conn.close()
