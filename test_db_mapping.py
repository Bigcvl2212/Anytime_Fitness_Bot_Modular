#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print('=== Training Clients Sample ===')
cursor.execute('SELECT member_name, clubos_member_id FROM training_clients LIMIT 3')
for row in cursor.fetchall():
    print(f'Name: {row["member_name"]}, ClubOS ID: {row["clubos_member_id"]}')

print('\n=== Members Sample ===') 
cursor.execute('SELECT full_name, id, guid FROM members WHERE full_name LIKE "%Alejandra%" OR full_name LIKE "%Mark%" LIMIT 5')
for row in cursor.fetchall():
    print(f'Name: {row["full_name"]}, ID: {row["id"]}, GUID: {row["guid"]}')

print('\n=== Testing Name Match ===')
cursor.execute('SELECT member_name FROM training_clients WHERE clubos_member_id = 191215290')
tc_row = cursor.fetchone()
if tc_row:
    name = tc_row['member_name']
    print(f'Training client name: {name}')
    
    cursor.execute('SELECT id, guid FROM members WHERE full_name = ?', (name,))
    member_row = cursor.fetchone()
    if member_row:
        print(f'Found member - ID: {member_row["id"]}, GUID: {member_row["guid"]}')
    else:
        print('No matching member found by name')
        # Try partial match
        cursor.execute('SELECT full_name, id, guid FROM members WHERE full_name LIKE ?', (f'%{name.split()[0]}%',))
        partial_matches = cursor.fetchall()
        if partial_matches:
            print('Partial matches:')
            for match in partial_matches:
                print(f'  {match["full_name"]} - ID: {match["id"]}, GUID: {match["guid"]}')

conn.close()

print('\n=== Testing Mark Benzinger ===')
import requests

conn = sqlite3.connect('gym_bot.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT clubos_member_id FROM training_clients WHERE member_name LIKE "%Mark%"')
mark_tc = cursor.fetchone()
if mark_tc:
    mark_clubos_id = mark_tc['clubos_member_id']
    print(f'Mark training client ClubOS ID: {mark_clubos_id}')
    
    # Test his package endpoint
    response = requests.get(f'http://localhost:5000/api/training-clients/{mark_clubos_id}/packages')
    if response.status_code == 200:
        data = response.json()
        print(f'Mark packages: {data.get("active_packages")}')
        print(f'Mark past due: ${data.get("past_due_amount", 0):.2f}')
    else:
        print(f'API error: {response.status_code}')
else:
    print('Mark not found in training clients')

conn.close()
