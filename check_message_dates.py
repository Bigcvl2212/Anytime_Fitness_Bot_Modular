import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get messages with dates in content
cursor.execute('''
    SELECT content, created_at, timestamp 
    FROM messages 
    WHERE content LIKE '%Jan %' 
    ORDER BY id DESC 
    LIMIT 5
''')

print("Sample messages with dates:")
print("="*80)
for content, created_at, timestamp in cursor.fetchall():
    print(f"\nContent: {content[:100]}...")
    print(f"Created: {created_at}")
    print(f"Timestamp: {timestamp}")
    print("-"*80)

conn.close()
