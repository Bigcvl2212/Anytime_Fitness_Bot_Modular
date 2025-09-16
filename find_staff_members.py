#!/usr/bin/env python3
"""
Search for the 5 specific staff members in the entire members database
"""

import sqlite3

def find_staff_members():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print('=== SEARCHING FOR SPECIFIC STAFF MEMBERS ===')
    
    target_staff = [
        'Jeremy Mayo',
        'Natoya Thomas', 
        'Mike Beal',
        'Staff Two',
        'Joseph Jones'
    ]
    
    for target_name in target_staff:
        print(f'\n--- Searching for: {target_name} ---')
        
        # Split name for search
        parts = target_name.lower().split()
        first_part = parts[0]
        last_part = parts[-1] if len(parts) > 1 else ''
        
        # Search by name parts
        cursor.execute("""
            SELECT first_name, last_name, email, status_message, prospect_id
            FROM members
            WHERE (LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ? OR LOWER(full_name) LIKE ?)
            OR (LOWER(first_name) LIKE ? AND LOWER(last_name) LIKE ?)
            ORDER BY first_name, last_name
        """, (f'%{first_part}%', f'%{last_part}%', f'%{target_name.lower()}%', 
              f'%{first_part}%', f'%{last_part}%'))
        
        matches = cursor.fetchall()
        
        if matches:
            print(f'Found {len(matches)} potential matches:')
            for match in matches:
                first_name = match[0] or ''
                last_name = match[1] or ''
                email = match[2] or ''
                status_msg = match[3] or ''
                prospect_id = match[4] or ''
                print(f'  • {first_name} {last_name} - {email} - {status_msg} - ID: {prospect_id}')
        else:
            print(f'❌ No matches found for {target_name}')

    print('\n=== ALL MEMBERS WITH "STAFF" IN STATUS MESSAGE ===')
    cursor.execute("""
        SELECT first_name, last_name, email, status_message, prospect_id
        FROM members
        WHERE status_message LIKE '%Staff%' OR status_message LIKE '%staff%'
        ORDER BY first_name, last_name
    """)
    
    all_staff = cursor.fetchall()
    print(f'Total staff members: {len(all_staff)}')
    for i, staff in enumerate(all_staff, 1):
        first_name = staff[0] or ''
        last_name = staff[1] or ''
        email = staff[2] or ''
        status_msg = staff[3] or ''
        prospect_id = staff[4] or ''
        print(f'{i:2d}. {first_name} {last_name} - {email} - {status_msg} - ID: {prospect_id}')

    conn.close()

if __name__ == "__main__":
    find_staff_members()