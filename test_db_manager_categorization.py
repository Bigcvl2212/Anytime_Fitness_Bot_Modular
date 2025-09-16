#!/usr/bin/env python3
"""Test the database_manager get_category_counts method directly"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.database_manager import DatabaseManager

def test_categorization():
    """Test the updated categorization logic"""
    print("=== TESTING DATABASE MANAGER CATEGORIZATION ===")
    
    db = DatabaseManager()
    counts = db.get_category_counts()
    
    print("\n🔢 Category Counts from DatabaseManager:")
    print(f"🟢 Green: {counts.get('green', 0)} (ClubHub: 308)")
    print(f"🟡 Past Due: {counts.get('past_due', 0)} (ClubHub: 22)")
    print(f"🔴 Red: {counts.get('red', 0)} (ClubHub: 17)")
    print(f"🧊 Frozen: {counts.get('frozen', 0)} (ClubHub: 3)")
    print(f"🎫 Comp: {counts.get('comp', 0)} (ClubHub: 31)")
    print(f"💰 PPV: {counts.get('ppv', 0)} (ClubHub: 116)")
    print(f"👥 Staff: {counts.get('staff', 0)} (ClubHub: 5)")
    print(f"❌ Inactive: {counts.get('inactive', 0)}")
    
    total = sum(counts.values())
    print(f"\n📊 Total categorized: {total}")
    
    # Test staff query specifically
    print(f"\n=== STAFF VERIFICATION ===")
    staff_records = db.execute_query("""
        SELECT prospect_id, first_name, last_name, email, status_message FROM members
        WHERE prospect_id IN ('64309309', '55867562', '50909888', '62716557', '52750389')
        ORDER BY first_name, last_name
    """)
    
    print(f"Staff records found: {len(staff_records) if staff_records else 0}")
    if staff_records:
        for record in staff_records:
            print(f"  • {record['prospect_id']}: {record['first_name']} {record['last_name']} - {record['status_message']}")

if __name__ == "__main__":
    test_categorization()