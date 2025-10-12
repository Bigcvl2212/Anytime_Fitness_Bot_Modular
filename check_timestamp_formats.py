import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Count ISO format timestamps
cursor.execute('SELECT COUNT(*) FROM messages WHERE channel="clubos" AND timestamp LIKE "2025-%"')
iso_count = cursor.fetchone()[0]

# Count non-ISO format timestamps  
cursor.execute('SELECT COUNT(*) FROM messages WHERE channel="clubos" AND timestamp NOT LIKE "2025-%"')
non_iso_count = cursor.fetchone()[0]

print(f"ISO format timestamps (2025-...): {iso_count}")
print(f"Non-ISO format timestamps: {non_iso_count}")

# Show samples of non-ISO
cursor.execute('SELECT DISTINCT timestamp FROM messages WHERE channel="clubos" AND timestamp NOT LIKE "2025-%" LIMIT 20')
print("\nSample non-ISO timestamps:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()
