import sqlite3
from datetime import datetime

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print('\n=== TESTING ROWID ASC (What inbox will show now) ===\n')

# Get most recent 15 messages with ROWID ASC (new query)
messages = cursor.execute('''
    SELECT from_user, timestamp, created_at, content 
    FROM messages 
    WHERE channel = "clubos"
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    ORDER BY ROWID ASC 
    LIMIT 15
''').fetchall()

for i, msg in enumerate(messages, 1):
    from_user, timestamp, created_at, content = msg
    print(f'{i}. FROM: {from_user}')
    print(f'   TIMESTAMP FROM CLUBOS: {timestamp}')
    print(f'   CONTENT: {content[:60]}...')
    print()

conn.close()
