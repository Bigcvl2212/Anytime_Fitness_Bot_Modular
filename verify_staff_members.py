#!/usr/bin/env python3
"""
Verify Staff Members List
Check current staff members against expected list of 5
"""

import sqlite3
import sys
import os

def verify_staff_members():
    """Verify staff members in database against expected list"""
    print("🔍 Verifying Staff Members List")
    print("=" * 50)
    
    # Expected staff members
    expected_staff = [
        'Joseph Jones',
        'Jeremy Mayo', 
        'Natoya Thomas',
        'Staff two',
        'Mike Beal'
    ]
    
    print("Expected staff members:")
    for i, name in enumerate(expected_staff, 1):
        print(f"   {i}. {name}")
    
    # Connect to database
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
        
    print(f"\n📂 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Find all members with "Staff" in status_message
        print("\n1. Members with 'Staff' in status_message:")
        cursor.execute("""
            SELECT id, prospect_id, full_name, status_message, status
            FROM members 
            WHERE status_message LIKE '%Staff%'
            ORDER BY full_name
        """)
        
        staff_members = cursor.fetchall()
        print(f"   Count: {len(staff_members)}")
        
        if staff_members:
            print("   Current staff members in database:")
            for member in staff_members:
                name = member['full_name'] or 'No Name'
                status_msg = member['status_message']
                prospect_id = member['prospect_id'] or 'No ID'
                print(f"   • {name} (ID: {prospect_id}) - '{status_msg}'")
        
        # 2. Check which expected staff are missing
        print(f"\n2. Expected staff verification:")
        found_expected = []
        missing_expected = []
        
        for expected_name in expected_staff:
            # Look for exact match or partial match
            cursor.execute("""
                SELECT full_name, status_message
                FROM members 
                WHERE full_name LIKE ? OR full_name LIKE ?
            """, (f'%{expected_name}%', f'{expected_name}%'))
            
            matches = cursor.fetchall()
            if matches:
                found_expected.append(expected_name)
                for match in matches:
                    print(f"   ✅ FOUND: {expected_name} -> {match['full_name']} ('{match['status_message']}')")
            else:
                missing_expected.append(expected_name)
                print(f"   ❌ MISSING: {expected_name}")
        
        # 3. Check for extra staff members not in expected list
        print(f"\n3. Extra staff members (not in expected list):")
        extra_staff = []
        
        for member in staff_members:
            member_name = member['full_name'] or 'No Name'
            is_expected = False
            
            for expected_name in expected_staff:
                if expected_name.lower() in member_name.lower() or member_name.lower() in expected_name.lower():
                    is_expected = True
                    break
            
            if not is_expected:
                extra_staff.append(member)
                print(f"   ⚠️ EXTRA: {member_name} (ID: {member['prospect_id'] or 'No ID'})")
        
        if not extra_staff:
            print("   ✅ No extra staff members found")
        
        # 4. Summary
        print(f"\n4. Summary:")
        print(f"   • Expected staff: {len(expected_staff)}")
        print(f"   • Found expected: {len(found_expected)}")
        print(f"   • Missing expected: {len(missing_expected)}")
        print(f"   • Total staff in DB: {len(staff_members)}")
        print(f"   • Extra staff in DB: {len(extra_staff)}")
        
        if len(found_expected) == len(expected_staff) and len(extra_staff) == 0:
            print(f"   ✅ Staff list is correct!")
        else:
            print(f"   ⚠️ Staff list needs cleanup")
            
            if missing_expected:
                print(f"   Missing staff: {', '.join(missing_expected)}")
            
            if extra_staff:
                print(f"   Extra staff to remove: {', '.join([m['full_name'] for m in extra_staff])}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking staff members: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_staff_members()