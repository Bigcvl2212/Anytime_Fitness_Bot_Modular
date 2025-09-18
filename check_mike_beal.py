#!/usr/bin/env python3
"""
Check Mike Beal's status
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    # Check Mike Beal specifically
    cursor = conn.execute("""
        SELECT prospect_id, first_name, last_name, status_message, email 
        FROM members 
        WHERE first_name LIKE '%MIKE%' AND last_name LIKE '%BEAL%'
    """)
    
    row = cursor.fetchone()
    if row:
        print(f"Mike Beal: {row['prospect_id']} - {row['first_name']} {row['last_name']} - '{row['status_message']}' - {row['email']}")
        
        # Check if this ID should be in the real staff list
        real_staff_ids = ['191003722', '189425730', '191210406', '191015549', '191201279']
        if row['prospect_id'] in real_staff_ids:
            print("✅ Mike Beal IS in the real staff list")
        else:
            print("❌ Mike Beal is NOT in the real staff list - should he be?")
            print("Current real staff IDs:", real_staff_ids)
    else:
        print("Mike Beal not found")

if __name__ == "__main__":
    main()