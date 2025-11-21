import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print("Status Messages:")
cursor.execute('SELECT status_message, COUNT(*) FROM members GROUP BY status_message ORDER BY COUNT(*) DESC')
for row in cursor.fetchall():
    status = row[0] if row[0] else 'NULL'
    print(f'  {status}: {row[1]}')

# Check updated staff count
cursor.execute("SELECT COUNT(*) FROM members WHERE status_message IN ('Staff Member', 'Staff member')")
staff_count = cursor.fetchone()[0]
print(f'\nUpdated Staff Count: {staff_count}')

conn.close()