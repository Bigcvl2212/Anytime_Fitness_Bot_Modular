#!/usr/bin/env python3

import sqlite3

# Connect to local SQLite database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check what tables we have and their structure
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Available tables:')
for table in tables:
    print(f'  - {table[0]}')

print('\nMembers table structure:')
cursor.execute('PRAGMA table_info(members)')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

print('\nTraining clients table structure:')
cursor.execute('PRAGMA table_info(training_clients)')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

# Check for past due data
print('\nPast due members:')
cursor.execute('SELECT member_name, past_due_amount, payment_status FROM members WHERE payment_status = "Past Due" LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row[0]}: ${row[1]} ({row[2]})')

print('\nPast due training clients:')
cursor.execute('SELECT member_name, past_due_amount, payment_status FROM training_clients WHERE payment_status = "Past Due" LIMIT 5')
for row in cursor.fetchall():
    print(f'  {row[0]}: ${row[1]} ({row[2]})')

conn.close()
