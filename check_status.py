#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('src/gym_bot.db')
cursor = conn.cursor()

print('=== STATUS VALUES ===')
cursor.execute('SELECT DISTINCT status FROM members WHERE status IS NOT NULL ORDER BY status')
statuses = cursor.fetchall()
print('Unique status values:')
for status in statuses:
    print(f'  "{status[0]}"')

print('\n=== STATUS_MESSAGE VALUES ===')
cursor.execute('SELECT DISTINCT status_message FROM members WHERE status_message IS NOT NULL AND status_message != "" ORDER BY status_message LIMIT 20')
status_messages = cursor.fetchall()
print('Sample status_message values:')
for msg in status_messages:
    print(f'  "{msg[0]}"')

print('\n=== STATUS + STATUS_MESSAGE COMBINATIONS ===')
cursor.execute('SELECT status, status_message, COUNT(*) as count FROM members WHERE status IS NOT NULL GROUP BY status, status_message ORDER BY count DESC LIMIT 15')
combinations = cursor.fetchall()
print('Most common status + status_message combinations:')
for combo in combinations:
    print(f'  Status: "{combo[0]}" | Message: "{combo[1]}" | Count: {combo[2]}')

print('\n=== SAMPLE MEMBER DATA ===')
cursor.execute('SELECT first_name, last_name, status, status_message, user_type FROM members WHERE status_message IS NOT NULL AND status_message != "" LIMIT 10')
samples = cursor.fetchall()
print('Sample members with status info:')
for sample in samples:
    print(f'  {sample[0]} {sample[1]} | Status: "{sample[2]}" | Message: "{sample[3]}" | Type: "{sample[4]}"')

conn.close()
