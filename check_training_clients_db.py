import sqlite3

conn = sqlite3.connect(r'C:\Users\mayoj\AppData\Local\GymBot\data\gym_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) as count FROM training_clients')
total = cursor.fetchone()['count']
print(f'Total training clients: {total}')

cursor.execute('''
    SELECT member_name, total_past_due, past_due_amount, payment_status,
           active_packages, package_details
    FROM training_clients
    ORDER BY total_past_due DESC
    LIMIT 10
''')

print('\nTop 10 by past due amount:')
for row in cursor.fetchall():
    print(f'\nName: {row["member_name"]}')
    print(f'  Total Past Due: {row["total_past_due"]} (type: {type(row["total_past_due"])})')
    print(f'  Past Due Amount: {row["past_due_amount"]} (type: {type(row["past_due_amount"])})')
    print(f'  Payment Status: {row["payment_status"]}')
    print(f'  Active Packages: {row["active_packages"]}')
    print(f'  Package Details: {row["package_details"][:100] if row["package_details"] else "None"}...')

# Check for duplicates
cursor.execute('''
    SELECT member_name, COUNT(*) as count
    FROM training_clients
    GROUP BY member_name
    HAVING COUNT(*) > 1
    ORDER BY count DESC
    LIMIT 5
''')

print('\n\nDuplicate training clients:')
for row in cursor.fetchall():
    print(f'  {row["member_name"]}: {row["count"]} entries')

conn.close()
