#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT full_name, mobile_phone, LENGTH(mobile_phone) as phone_len, email
    FROM members 
    WHERE status_message LIKE '%Past Due 6-30 days%'
    LIMIT 5
''')

results = cursor.fetchall()
print('Sample member data for debugging:')
for name, phone, phone_len, email in results:
    phone_clean = phone.strip() if phone else ""
    email_clean = email.strip() if email else ""
    print(f'{name}:')
    print(f'  Phone: "{phone}" (length: {phone_len})')
    print(f'  Phone stripped: "{phone_clean}" (empty: {not bool(phone_clean)})')
    print(f'  Email: "{email}"')
    print(f'  Email valid: {"@" in email_clean if email_clean else False}')
    print()

conn.close()