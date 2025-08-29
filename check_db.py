#!/usr/bin/env python3
import sqlite3, os

db_path = 'src/gym_bot.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check total members
    cur.execute('SELECT COUNT(*) FROM members')
    total = cur.fetchone()[0]
    print(f'Total members: {total}')
    
    # Check past due members
    cur.execute('SELECT COUNT(*) FROM members WHERE COALESCE(amount_past_due, 0) > 0')
    past_due_count = cur.fetchone()[0]
    print(f'Past due members (amount > 0): {past_due_count}')
    
    # Check status messages with Past Due
    cur.execute('SELECT COUNT(*) FROM members WHERE status_message LIKE "%Past Due%"')
    status_past_due = cur.fetchone()[0]
    print(f'Members with "Past Due" in status_message: {status_past_due}')
    
    # Sample some members to see their data
    cur.execute('SELECT first_name, last_name, amount_past_due, status_message, status LIMIT 10')
    print('\nSample members:')
    for row in cur.fetchall():
        print(f'  {row[0]} {row[1]} - Past Due: ${row[2] or 0}, Status: {row[4]}, Msg: {row[3]}')
    
    # Check member_categories table
    cur.execute('SELECT COUNT(*) FROM member_categories')
    cat_count = cur.fetchone()[0]
    print(f'\nMember categories entries: {cat_count}')
    
    # Check a few more members with different statuses
    print('\nLooking for members with different status patterns:')
    cur.execute('SELECT COUNT(*) FROM members WHERE status IN ("Inactive", "inactive", "Suspended", "suspended", "Cancelled", "cancelled")')
    inactive_count = cur.fetchone()[0]
    print(f'Inactive members: {inactive_count}')
    
    cur.execute('SELECT COUNT(*) FROM members WHERE status_message LIKE "%comp%" OR status_message LIKE "%free%" OR member_type LIKE "%comp%"')
    comp_count = cur.fetchone()[0]
    print(f'Comp members: {comp_count}')
    
    conn.close()
else:
    print('Database not found at', db_path)
