#!/usr/bin/env python3
"""
Check the 4 uncategorized members with empty status to determine where they belong
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    uncategorized_ids = ['48237031', '55403978', '59450962', '63027441']
    
    print("=== UNCATEGORIZED MEMBERS WITH EMPTY STATUS ===")
    for member_id in uncategorized_ids:
        cursor = conn.execute("""
            SELECT prospect_id, first_name, last_name, status_message, agreement_id, amount_past_due, email
            FROM members 
            WHERE prospect_id = ?
        """, (member_id,))
        
        row = cursor.fetchone()
        if row:
            print(f"\nID: {row['prospect_id']}")
            print(f"Name: {row['first_name']} {row['last_name']}")
            print(f"Status: '{row['status_message']}'")
            print(f"Agreement ID: {row['agreement_id']}")
            print(f"Amount Past Due: {row['amount_past_due']}")
            print(f"Email: {row['email']}")
            
            # Determine category
            if row['agreement_id'] is None:
                print("→ Should be COLLECTIONS (NULL agreement_id)")
            elif row['status_message'] == '' and row['prospect_id'] not in ['191003722', '189425730', '191210406', '191015549', '191201279']:
                print("→ Should be INACTIVE (empty status, not real staff)")
            else:
                print("→ Unclear categorization")
    
    print(f"\n=== RECOMMENDATION ===")
    print("These 4 members have empty status messages and should go to inactive category")
    print("They were excluded because our inactive logic requires agreement_id IS NOT NULL")
    print("But some might have NULL agreement_id, making them collections candidates")

if __name__ == "__main__":
    main()