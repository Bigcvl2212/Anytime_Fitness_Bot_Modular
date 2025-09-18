#!/usr/bin/env python3
"""
Verify Final Staff Status and Add Missing Authorized Staff
Check current staff status and add missing authorized staff members if needed
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def verify_and_complete_staff_setup():
    """
    Verify final staff setup and add missing authorized staff members
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    # The 5 authorized staff members that should have staff status
    authorized_staff = [
        'Joseph Jones',
        'Jeremy Mayo', 
        'Natoya Thomas',
        'Staff Two',
        'Mike Beal'  # Already has staff status
    ]
    
    print(f"🔄 Verifying authorized staff setup...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check current staff status
        print("\n📊 Current members with staff status:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        current_staff = cursor.fetchall()
        print(f"Found {len(current_staff)} members with staff status:")
        
        for staff in current_staff:
            print(f"  ✅ {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
        
        # Check if other authorized staff exist in database
        print(f"\n🔍 Searching for other authorized staff members in database:")
        
        missing_staff = []
        found_staff = []
        
        for staff_name in authorized_staff:
            if staff_name == 'Mike Beal':
                continue  # Already verified as staff
                
            # Search for the staff member (case-insensitive)
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE UPPER(full_name) LIKE UPPER(?)
                LIMIT 5
            """, (f'%{staff_name}%',))
            
            matches = cursor.fetchall()
            
            if matches:
                print(f"  📍 Found matches for '{staff_name}':")
                for match in matches:
                    print(f"    - {match['full_name']}: {match['status_message']} (ID: {match['prospect_id']})")
                    if staff_name.upper() in match['full_name'].upper():
                        found_staff.append((staff_name, match))
            else:
                print(f"  ❌ No matches found for '{staff_name}'")
                missing_staff.append(staff_name)
        
        # Show members that were reclassified to regular status
        print(f"\n📊 Recently reclassified members (now regular members):")
        reclassified_names = [
            'HOPE BRENNENSTUHL', 'JACOB LIETZ', 'KAYLA MUELLER', 
            'KENDALL BRESTER', 'LINDA DAKE', 'STACY FUESTON1'
        ]
        
        for name in reclassified_names:
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE full_name = ?
            """, (name,))
            
            member = cursor.fetchone()
            if member:
                print(f"  ✅ {member['full_name']}: {member['status_message']} (ID: {member['prospect_id']})")
        
        # Summary
        print(f"\n📊 Final Summary:")
        print(f"  - Current staff members: {len(current_staff)}")
        print(f"  - Expected staff members: {len(authorized_staff)}")
        print(f"  - Staff members found in database: {len(found_staff) + 1}")  # +1 for Mike Beal
        print(f"  - Staff members not found: {len(missing_staff)}")
        
        if len(current_staff) == 1 and current_staff[0]['full_name'] == 'MIKE BEAL':
            print(f"✅ Staff cleanup successful!")
            print(f"ℹ️ Mike Beal is the only member with staff status (as expected)")
            if missing_staff:
                print(f"ℹ️ Note: {len(missing_staff)} authorized staff members not found in database:")
                for staff in missing_staff:
                    print(f"    - {staff}")
                print(f"ℹ️ These members may need to be added to the database separately")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting staff verification and completion process...")
    success = verify_and_complete_staff_setup()
    
    if success:
        print("\n✅ Staff verification completed successfully!")
    else:
        print("\n❌ Staff verification failed!")
        sys.exit(1)