#!/usr/bin/env python3
"""
Check the overlapping member to understand the issue
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    # Check the yellow/inactive overlap member
    cursor = conn.execute("""
        SELECT prospect_id, first_name, last_name, status_message, agreement_id 
        FROM members 
        WHERE prospect_id = '20532778'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"YELLOW/INACTIVE OVERLAP:")
        print(f"ID: {row['prospect_id']}")
        print(f"Name: {row['first_name']} {row['last_name']}")
        print(f"Status: '{row['status_message']}'")
        print(f"Agreement ID: {row['agreement_id']}")
        print()
        
        # Determine which category this should be in
        if row['status_message'] in ['Invalid Billing Information.', 'Invalid/Bad Address information.', 'Member is pending cancel', 'Member will expire within 30 days.', 'Account has been cancelled.']:
            print("✅ Should be in YELLOW category (account issue)")
        elif row['status_message'] in ['Staff Member', 'Staff member', ''] and row['prospect_id'] not in ['191003722', '189425730', '191210406', '191015549', '191201279']:
            print("✅ Should be in INACTIVE category (fake staff)")
        else:
            print("❓ Unclear which category this should be in")

if __name__ == "__main__":
    main()