#!/usr/bin/env python3
"""
Check current staff members in database to identify the 5 correct ones
"""

import sqlite3

def check_staff_members():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print('=== CURRENT STAFF MEMBERS IN DATABASE ===')
    cursor.execute("""
        SELECT first_name, last_name, email, status_message
        FROM members
        WHERE status_message IN ('Staff Member', 'Staff member')
        ORDER BY first_name, last_name
    """)

    staff_members = cursor.fetchall()
    for i, row in enumerate(staff_members, 1):
        first_name = row[0] or ''
        last_name = row[1] or ''
        email = row[2] or ''
        status_msg = row[3] or ''
        print(f'{i}. {first_name} {last_name} - {email} - {status_msg}')

    print(f'\nTotal staff members found: {len(staff_members)}')
    
    print('\n=== TARGET STAFF ACCOUNTS (5 expected) ===')
    target_staff = [
        'Jeremy Mayo',
        'Natoya Thomas', 
        'Mike Beal',
        'Staff Two',
        'Joseph Jones'
    ]
    
    for name in target_staff:
        print(f'- {name}')

    print('\n=== CHECKING FOR MATCHES ===')
    for staff in staff_members:
        full_name = f"{staff[0] or ''} {staff[1] or ''}".strip().lower()
        for target in target_staff:
            if target.lower() in full_name or any(part.lower() in full_name for part in target.lower().split()):
                print(f'✅ MATCH: {staff[0]} {staff[1]} ({staff[2]}) likely matches "{target}"')
                break

    conn.close()

if __name__ == "__main__":
    check_staff_members()