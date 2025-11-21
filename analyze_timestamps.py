import sqlite3
from collections import Counter

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Get unique timestamp patterns
cursor.execute("""
    SELECT DISTINCT timestamp
    FROM messages
    WHERE channel = 'clubos'
    AND timestamp IS NOT NULL
    ORDER BY timestamp
    LIMIT 50
""")

print("Sample timestamp values from database:\n")
for i, row in enumerate(cursor.fetchall(), 1):
    print(f"{i}. '{row[0]}'")

conn.close()
