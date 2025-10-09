import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get a message with actual content to see what we're working with
cursor.execute('''
    SELECT content FROM messages 
    WHERE channel = 'clubos' 
    AND LENGTH(content) > 50
    LIMIT 3
''')

messages = cursor.fetchall()
print("Sample message content structures:\n")

for i, msg in enumerate(messages, 1):
    content = msg[0]
    print(f"Message {i}:")
    print(f"{content[:200]}...")
    print("-" * 80)

conn.close()
