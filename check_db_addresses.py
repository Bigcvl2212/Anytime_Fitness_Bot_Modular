import sqlite3

# Check local database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) as total, COUNT(address) as with_address FROM members')
result = cursor.fetchone()
print(f'Total members: {result[0]}')
print(f'With addresses: {result[1]}')

cursor.execute('SELECT first_name, last_name, address, city, state, zip_code FROM members LIMIT 5')
rows = cursor.fetchall()
print('\nFirst 5 members:')
for row in rows:
    print(f'  {row[0]} {row[1]}: address={row[2]}, city={row[3]}, state={row[4]}, zip={row[5]}')

conn.close()
