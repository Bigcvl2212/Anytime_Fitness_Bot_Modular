#!/usr/bin/env python3
"""
Check status messages in database to match ClubHub categorization
"""

import sqlite3

def check_status_messages():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print('=== ALL STATUS MESSAGES IN DATABASE ===')
    cursor.execute("""
        SELECT 
            status_message,
            COUNT(*) as count
        FROM members
        GROUP BY status_message
        ORDER BY count DESC
    """)

    for row in cursor.fetchall():
        status_msg = row[0] or 'NULL'
        count = row[1]
        print(f'{status_msg}: {count} members')

    print('\n=== TOTAL MEMBERS ===')
    cursor.execute("SELECT COUNT(*) FROM members")
    total = cursor.fetchone()[0]
    print(f'Total members: {total}')

    conn.close()

if __name__ == "__main__":
    check_status_messages()