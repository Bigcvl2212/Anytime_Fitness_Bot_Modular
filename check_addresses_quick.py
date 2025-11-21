import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check past due members
cursor.execute('''
    SELECT prospect_id, full_name, amount_past_due, address, city, state, zip_code
    FROM members
    WHERE amount_past_due > 0
    LIMIT 10
''')

rows = cursor.fetchall()
print('Past Due Members with Address Data:')
print('=' * 80)

for row in rows:
    print(f'ID: {row[0]}, Name: {row[1]}, Past Due: {row[2]}')
    print(f'  Address: {row[3]}')
    print(f'  City: {row[4]}, State: {row[5]}, Zip: {row[6]}')
    print('-' * 80)

# Check training clients
print('\n\nTraining Clients with Address Data:')
print('=' * 80)

cursor.execute('PRAGMA table_info(training_clients)')
columns = cursor.fetchall()
print('Training Clients columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

cursor.execute('''
    SELECT member_id, full_name, past_due_amount, address, city, state, zip_code
    FROM training_clients
    WHERE past_due_amount > 0
    LIMIT 10
''')

try:
    rows = cursor.fetchall()
    for row in rows:
        print(f'ID: {row[0]}, Name: {row[1]}, Past Due: {row[2]}')
        print(f'  Address: {row[3]}')
        print(f'  City: {row[4]}, State: {row[5]}, Zip: {row[6]}')
        print('-' * 80)
except Exception as e:
    print(f'Error reading training clients: {e}')

conn.close()
