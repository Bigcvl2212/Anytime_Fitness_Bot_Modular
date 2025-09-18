#!/usr/bin/env python3
"""
Check the final overlapping member between green and collections
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute("""
        SELECT prospect_id, first_name, last_name, status_message, agreement_id 
        FROM members 
        WHERE prospect_id = '40775697'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"OVERLAP MEMBER:")
        print(f"ID: {row['prospect_id']}")
        print(f"Name: {row['first_name']} {row['last_name']}")
        print(f"Status: '{row['status_message']}'")
        print(f"Agreement ID: {row['agreement_id']}")
        print()
        
        if row['status_message'] == 'Member is in good standing' and row['agreement_id'] is None:
            print("✅ Has 'good standing' status but NULL agreement_id")
            print("❓ Should this be GREEN (trust the status) or COLLECTIONS (no agreement)?")
            print("💡 RECOMMENDATION: Since they're in good standing, they should be GREEN only")
            print("   Collections should exclude members with good standing status")

if __name__ == "__main__":
    main()