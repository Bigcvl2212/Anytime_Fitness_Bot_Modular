#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('Looking for test members from working API:')
print('1. Javae Dixon (185182950)')
cursor.execute('SELECT * FROM members WHERE guid = ?', ('185182950',))
result = cursor.fetchone()
if result:
    print(f'   Found: {result["full_name"]} - GUID: {result["guid"]}')
else:
    print('   Not found in members table')

print('2. Grace Sphatt (185777276)') 
cursor.execute('SELECT * FROM members WHERE guid = ?', ('185777276',))
result = cursor.fetchone()
if result:
    print(f'   Found: {result["full_name"]} - GUID: {result["guid"]}')
else:
    print('   Not found in members table')

print('')
print('Checking training clients for these names:')
cursor.execute('SELECT * FROM training_clients WHERE member_name LIKE "%Javae%" OR member_name LIKE "%Grace%"')
results = cursor.fetchall()
for r in results:
    print(f'   Training Client: {r["member_name"]} - ClubOS ID: {r["clubos_member_id"]}')

print('')
print('Now let me check if these IDs exist anywhere in our database:')
cursor.execute('SELECT * FROM members WHERE guid IN ("185182950", "185777276")')
results = cursor.fetchall()
for r in results:
    print(f'   Member: {r["full_name"]} - GUID: {r["guid"]}')

conn.close()
