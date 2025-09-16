import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Test the exact query from database_manager.py
result = cursor.execute("""
    SELECT COUNT(*) FROM members
    WHERE prospect_id IN ('64309309', '55867562', '50909888', '62716557', '52750389')
""").fetchone()

print(f"Staff count by prospect IDs: {result[0]}")

# Also show the actual records
records = cursor.execute("""
    SELECT prospect_id, first_name, last_name, email, status_message FROM members
    WHERE prospect_id IN ('64309309', '55867562', '50909888', '62716557', '52750389')
    ORDER BY first_name, last_name
""").fetchall()

print(f"\nFound {len(records)} staff records:")
for record in records:
    print(f"  • {record[0]}: {record[1]} {record[2]} - {record[3]} - {record[4]}")

conn.close()