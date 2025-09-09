#!/usr/bin/env python3
import sqlite3
from datetime import datetime, date

print('=== CHECKING EVENTS DATA ===')
conn = sqlite3.connect('gym_bot.db')
cursor = conn.cursor()

# Check if events table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
events_table = cursor.fetchone()
print('Events table exists:', bool(events_table))

if events_table:
    # Count total events
    cursor.execute('SELECT COUNT(*) FROM events')
    total_events = cursor.fetchone()[0]
    print('Total events in database:', total_events)
    
    # Check recent events
    today = date.today()
    cursor.execute('SELECT COUNT(*) FROM events WHERE date(start_time) = ?', (today,))
    today_events = cursor.fetchone()[0]
    print('Events today:', today_events)
    
    # Show sample events
    cursor.execute('SELECT id, title, start_time, participants FROM events ORDER BY start_time DESC LIMIT 5')
    sample_events = cursor.fetchall()
    print('\nSample events:')
    for event in sample_events:
        print(f'- ID: {event[0]}, Title: {event[1]}, Start: {event[2]}, Participants: {event[3]}')
else:
    print('No events table found!')
    # Show what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Available tables:', [table[0] for table in tables])

conn.close()
