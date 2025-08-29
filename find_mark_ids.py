#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

print('=== Mark Benzinger ID Mapping ===')
cursor.execute('SELECT member_id, member_name, clubos_member_id FROM training_clients WHERE member_name LIKE ? AND member_name LIKE ?', ('%Mark%', '%Benzinger%'))
training_result = cursor.fetchone()
if training_result:
    print(f'Training table - member_id: {training_result[0]}, name: {training_result[1]}, clubos_member_id: {training_result[2]}')
else:
    print('Mark Benzinger not found in training_clients table')

cursor.execute('SELECT guid, full_name FROM members WHERE full_name LIKE ? AND full_name LIKE ?', ('%Mark%', '%Benzinger%'))
members_result = cursor.fetchone()
if members_result:
    print(f'Members table - GUID: {members_result[0]}, name: {members_result[1]}')
else:
    print('Mark Benzinger not found in members table')

print('\n=== First 5 Training Clients ID Mapping ===')
cursor.execute('SELECT member_id, member_name, clubos_member_id FROM training_clients LIMIT 5')
for row in cursor.fetchall():
    print(f'member_id: {row[0]}, name: {row[1]}, clubos_member_id: {row[2]}')

conn.close()
