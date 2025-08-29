#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print('Training clients table schema:')
cursor.execute('PRAGMA table_info(training_clients)')
columns = cursor.fetchall()
for col in columns:
    print(f'Column: {col[1]} ({col[2]})')

print('\nTraining clients in database:')
cursor.execute('SELECT * FROM training_clients LIMIT 3')
rows = cursor.fetchall()
col_names = [description[0] for description in cursor.description]
print(f'Columns: {col_names}')
for row in rows:
    print(f'Row: {dict(zip(col_names, row))}')

print('\nMembers table sample:')
cursor.execute('SELECT full_name, id, guid, prospect_id FROM members WHERE full_name LIKE "%Alejandra%" OR full_name LIKE "%Mark%" LIMIT 5')
for row in cursor.fetchall():
    print(f'Name: {row[0]}, ID: {row[1]}, GUID: {row[2]}, Prospect ID: {row[3]}')

conn.close()
