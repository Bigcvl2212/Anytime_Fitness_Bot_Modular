import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0]
    print(f'Members in database: {count}')
    
    if count > 0:
        cursor.execute("SELECT DISTINCT status_message, COUNT(*) FROM members WHERE status_message IS NOT NULL GROUP BY status_message ORDER BY COUNT(*) DESC LIMIT 10")
        statuses = cursor.fetchall()
        print('\nStatus messages:')
        for status, cnt in statuses:
            print(f'  "{status}": {cnt}')
    
    conn.close()
else:
    print('No database found')
