#!/usr/bin/env python3
"""
Add Staff Status to Authorized Members
Update the 4 remaining authorized staff members to have staff status
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def add_staff_status_to_authorized():
    """
    Add staff status to the 4 authorized staff members who should have it
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    # The 4 authorized staff members that need staff status added
    # (Mike Beal already has staff status)
    authorized_staff_to_update = [
        ('JOSEPH JONES', '52750389'),
        ('JEREMY MAYO', '64309309'), 
        ('NATOYA THOMAS', '55867562'),
        ('STAFF TWO', '62716557')
    ]
    
    print(f"🔄 Adding staff status to {len(authorized_staff_to_update)} authorized staff members...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Show current staff status
        print("\n📊 Current staff members:")
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
        
        # Add staff status to authorized members
        updated_count = 0
        
        for name, member_id in authorized_staff_to_update:
            print(f"\n🔄 Processing: {name} (ID: {member_id})")
            
            # Verify the member exists and get current status
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE prospect_id = ?
            """, (member_id,))
            
            member = cursor.fetchone()
            
            if member:
                print(f"  📍 Found: {member['full_name']} with status '{member['status_message']}'")
                
                # Update their status to 'Staff Member' 
                # But keep Mike Beal's dual status as both member and staff
                if member['full_name'] == 'MIKE BEAL':
                    # Mike Beal should have both statuses
                    new_status = 'Member is in good standing, Staff Member'
                else:
                    # Others should have staff status
                    new_status = 'Staff Member'
                
                cursor.execute("""
                    UPDATE members 
                    SET status_message = ?,
                        updated_at = ?
                    WHERE prospect_id = ?
                """, (new_status, datetime.now().isoformat(), member_id))
                
                if cursor.rowcount > 0:
                    print(f"  ✅ Updated {member['full_name']} to '{new_status}'")
                    updated_count += 1
                else:
                    print(f"  ⚠️ Failed to update {member['full_name']}")
            else:
                print(f"  ❌ Member with ID '{member_id}' not found!")
        
        # Also update Mike Beal to have dual status if he doesn't already
        print(f"\n🔄 Ensuring Mike Beal has dual member/staff status:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE prospect_id = '50909888'
        """)
        
        mike_beal = cursor.fetchone()
        if mike_beal:
            current_status = mike_beal['status_message']
            print(f"  📍 Mike Beal current status: '{current_status}'")
            
            # If he doesn't have both statuses, update him
            if 'Member is in good standing' not in current_status:
                new_dual_status = 'Member is in good standing, Staff Member'
                cursor.execute("""
                    UPDATE members 
                    SET status_message = ?,
                        updated_at = ?
                    WHERE prospect_id = '50909888'
                """, (new_dual_status, datetime.now().isoformat()))
                
                if cursor.rowcount > 0:
                    print(f"  ✅ Updated Mike Beal to dual status: '{new_dual_status}'")
                else:
                    print(f"  ⚠️ Failed to update Mike Beal")
            else:
                print(f"  ✅ Mike Beal already has appropriate dual status")
        
        # Final verification
        print(f"\n📊 Final staff status verification:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        final_staff = cursor.fetchall()
        print(f"Total members with staff status after updates: {len(final_staff)}")
        
        for staff in final_staff:
            print(f"  ✅ {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
        
        # Commit changes
        conn.commit()
        
        print(f"\n🎉 Staff setup completed successfully!")
        print(f"📊 Summary:")
        print(f"  - Updated staff members: {updated_count}")
        print(f"  - Total staff members: {len(final_staff)}")
        print(f"  - Expected staff members: 5")
        
        if len(final_staff) == 5:
            print(f"✅ Staff count matches expected (5 members)")
        else:
            print(f"⚠️ Staff count: Expected 5, got {len(final_staff)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during staff status update: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting authorized staff status update process...")
    success = add_staff_status_to_authorized()
    
    if success:
        print("\n✅ Staff status update completed successfully!")
    else:
        print("\n❌ Staff status update failed!")
        sys.exit(1)