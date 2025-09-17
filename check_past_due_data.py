#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta

# Connect to local SQLite database
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check for past due members
print('Past due members:')
cursor.execute('SELECT full_name, amount_past_due, status, email, phone FROM members WHERE amount_past_due > 0 LIMIT 10')
members = cursor.fetchall()
for row in members:
    print(f'  {row[0]}: ${row[1]} ({row[2]}) - {row[3]} - {row[4]}')

print(f'\nTotal past due members: {len(members)}')

# Check for past due training clients
print('\nPast due training clients:')
cursor.execute('SELECT member_name, past_due_amount, payment_status, email, phone FROM training_clients WHERE past_due_amount > 0 LIMIT 10')
training_clients = cursor.fetchall()
for row in training_clients:
    print(f'  {row[0]}: ${row[1]} ({row[2]}) - {row[3]} - {row[4]}')

print(f'\nTotal past due training clients: {len(training_clients)}')

# Check if we have agreement data
print('\nChecking for agreement data in training clients:')
cursor.execute('SELECT member_name, package_details, active_packages FROM training_clients WHERE package_details IS NOT NULL AND package_details != "" LIMIT 5')
agreements = cursor.fetchall()
for row in agreements:
    print(f'  {row[0]}: packages={row[2]}, details={row[1][:100]}...')

conn.close()
