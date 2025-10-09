import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check what the inbox query actually returns
cursor.execute('''
    SELECT
        id, content, from_user, owner_id, created_at, channel,
        timestamp, status, message_type
    FROM messages
    WHERE channel = 'clubos'
    AND from_user IS NOT NULL
    AND from_user != ''
    AND LENGTH(TRIM(content)) > 5
    ORDER BY created_at DESC
    LIMIT 5
''')

messages = cursor.fetchall()
print(f"Found {len(messages)} messages from inbox query\n")

for msg in messages:
    print(f"ID: {msg[0]}")
    print(f"From: {msg[2]}")
    print(f"Content preview: {msg[1][:100]}...")
    print(f"Owner ID: {msg[3]}")
    print(f"Channel: {msg[5]}")
    print("-" * 80)

conn.close()
