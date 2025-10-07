import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT full_name, email, mobile_phone, address, city, state, zip_code, amount_past_due 
    FROM members 
    WHERE status_message LIKE '%Past Due%' 
    ORDER BY full_name
""")

rows = cursor.fetchall()

print('\n' + '=' * 120)
print('=== PAST DUE MEMBERS - FULL ADDRESS LIST ===')
print('=' * 120)
print(f'\nTotal Past Due: {len(rows)} members\n')

for row in rows:
    print('-' * 120)
    print(f'Name:        {row[0]}')
    print(f'Email:       {row[1] or "NO EMAIL"}')
    print(f'Phone:       {row[2] or "NO PHONE"}')
    print(f'Address:     {row[3] or "NO ADDRESS"}')
    print(f'City:        {row[4] or "NO CITY"}')
    print(f'State:       {row[5] or "NO STATE"}')
    print(f'Zip Code:    {row[6] or "NO ZIP"}')
    print(f'Past Due:    ${row[7]:.2f}')

print('-' * 120)
print('\n')

conn.close()
