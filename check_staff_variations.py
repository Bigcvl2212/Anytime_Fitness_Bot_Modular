import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check both staff variations
cursor.execute("SELECT first_name, last_name, status_message FROM members WHERE status_message IN ('Staff Member', 'Staff member')")
staff = cursor.fetchall()

print(f"Total staff found: {len(staff)}")
print("\nStaff members:")
for s in staff:
    print(f"  {s[0]} {s[1]} - '{s[2]}'")

# Show the count breakdown
cursor.execute("SELECT status_message, COUNT(*) FROM members WHERE status_message IN ('Staff Member', 'Staff member') GROUP BY status_message")
counts = cursor.fetchall()
print(f"\nBreakdown:")
for status, count in counts:
    print(f"  '{status}': {count}")

conn.close()