import sqlite3

# Check AppData database
conn = sqlite3.connect(r'C:\Users\mayoj\AppData\Local\GymBot\data\gym_bot.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) as total, COUNT(address) as with_address FROM members')
result = cursor.fetchone()
print(f'Total members in AppData DB: {result[0]}')
print(f'With addresses: {result[1]}')

cursor.execute('SELECT first_name, last_name, address FROM members WHERE address IS NOT NULL LIMIT 5')
rows = cursor.fetchall()
print('\nSample members with addresses:')
for row in rows:
    print(f'  {row[0]} {row[1]}: {row[2]}')

# Check admin users
cursor.execute('SELECT username, manager_id FROM admin_users')
users = cursor.fetchall()
print(f'\nAdmin users in AppData DB: {len(users)}')
for user in users:
    print(f'  {user[0]} (manager_id: {user[1]})')

conn.close()
