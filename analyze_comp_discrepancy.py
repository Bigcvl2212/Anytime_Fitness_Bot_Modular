#!/usr/bin/env python3
"""
Analyze the categorization discrepancy - you expect 31 comp but we have 32
"""

import sqlite3

def main():
    conn = sqlite3.connect("gym_bot.db")
    conn.row_factory = sqlite3.Row
    
    print("=== ANALYSIS: Comp Count Discrepancy ===")
    print("Database shows: 32 comp members")
    print("Expected: 31 comp members")
    print("Difference: +1 (we have 1 too many)")
    print()
    
    # Show all comp members
    cursor = conn.execute("""
        SELECT prospect_id, first_name, last_name, status_message, email 
        FROM members 
        WHERE status_message = 'Comp Member'
        ORDER BY first_name
    """)
    
    print("=== ALL 32 COMP MEMBERS ===")
    comp_members = cursor.fetchall()
    for i, row in enumerate(comp_members, 1):
        print(f"{i:2d}. {row['prospect_id']}: {row['first_name']} {row['last_name']} - {row['email']}")
    
    print(f"\nTotal: {len(comp_members)} comp members")
    print()
    
    # Check if any of the fake staff should actually be inactive instead of yellow
    print("=== RECOMMENDATION ===")
    print("Some of those 'Staff Member' people might have:")
    print("1. Transferred to another gym (should be inactive)")
    print("2. Cancelled their membership (should be inactive)")
    print("3. Been comp members that got miscategorized")
    print()
    print("Looking at the fake staff list, these look suspicious:")
    
    suspicious_staff = [
        "68481548: Anytime Test",  # Clearly a test account
        "68867188: Staff One",     # Generic staff account
        "37354360: PAIGE ERMER",   # Has fonddulacwi@anytimefitness.com email
    ]
    
    for staff in suspicious_staff:
        print(f"- {staff}")
    
    print()
    print("NEXT STEPS:")
    print("1. Move fake staff members to inactive category if they transferred/cancelled")
    print("2. This should reduce yellow category and fix comp count")
    print("3. Keep only the 5 real staff members in staff category")

if __name__ == "__main__":
    main()