#!/usr/bin/env python3
"""
Check comp members and staff members to see what's happening with the counts
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    # Check comp members
    cursor = conn.execute("""
        SELECT status_message, COUNT(*) as count 
        FROM members 
        WHERE status_message LIKE '%comp%' OR status_message LIKE '%Comp%'
        GROUP BY status_message 
        ORDER BY count DESC
    """)
    
    print("=== COMP MEMBERS ===")
    total_comp = 0
    for row in cursor.fetchall():
        print(f"'{row['status_message']}': {row['count']}")
        total_comp += row['count']
    print(f"Total Comp: {total_comp}")
    
    # Check all staff members
    cursor = conn.execute("""
        SELECT status_message, COUNT(*) as count 
        FROM members 
        WHERE status_message LIKE '%staff%' OR status_message LIKE '%Staff%'
        GROUP BY status_message 
        ORDER BY count DESC
    """)
    
    print("\n=== ALL STAFF MEMBERS ===")
    total_staff = 0
    for row in cursor.fetchall():
        print(f"'{row['status_message']}': {row['count']}")
        total_staff += row['count']
    print(f"Total Staff: {total_staff}")
    
    # Check the real staff IDs to see if any are comp
    cursor = conn.execute("""
        SELECT prospect_id, first_name, last_name, status_message 
        FROM members 
        WHERE prospect_id IN ('191003722', '189425730', '191210406', '191015549', '191201279')
        ORDER BY first_name
    """)
    
    print("\n=== REAL STAFF MEMBERS ===")
    for row in cursor.fetchall():
        print(f"{row['prospect_id']}: {row['first_name']} {row['last_name']} - '{row['status_message']}'")
    
    # Check if any fake staff should be comp
    cursor = conn.execute("""
        SELECT prospect_id, first_name, last_name, status_message, email 
        FROM members 
        WHERE status_message IN ('Staff Member', 'Staff member', '')
        AND prospect_id NOT IN ('191003722', '189425730', '191210406', '191015549', '191201279')
        ORDER BY first_name
    """)
    
    print("\n=== FAKE STAFF MEMBERS (should these be comp?) ===")
    for row in cursor.fetchall():
        print(f"{row['prospect_id']}: {row['first_name']} {row['last_name']} - '{row['status_message']}' - {row['email']}")

if __name__ == "__main__":
    main()