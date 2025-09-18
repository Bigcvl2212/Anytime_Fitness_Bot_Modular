#!/usr/bin/env python3
"""
Fix Staff Members Dual Status
Update staff members to have both 'Member is in good standing' AND 'Staff Member' status
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def fix_staff_dual_status():
    """
    Fix staff members to have dual status: 'Member is in good standing, Staff Member'
    This ensures they count in both green members AND staff categories
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    # The 4 staff members that need dual status (Mike Beal already has it)
    staff_members_to_fix = [
        ('JOSEPH JONES', '52750389'),
        ('JEREMY MAYO', '64309309'), 
        ('NATOYA THOMAS', '55867562'),
        ('STAFF TWO', '62716557')
    ]
    
    print(f"🔄 Fixing dual status for {len(staff_members_to_fix)} staff members...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Show current staff status
        print("\n📊 Current staff members before fix:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        current_staff = cursor.fetchall()
        for staff in current_staff:
            has_dual = 'Member is in good standing' in staff['status_message']
            status_icon = "✅" if has_dual else "⚠️"
            print(f"  {status_icon} {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
        
        # Fix staff members to have dual status
        fixed_count = 0
        
        for name, member_id in staff_members_to_fix:
            print(f"\n🔄 Processing: {name} (ID: {member_id})")
            
            # Get current status
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE prospect_id = ?
            """, (member_id,))
            
            member = cursor.fetchone()
            
            if member:
                current_status = member['status_message']
                print(f"  📍 Current status: '{current_status}'")
                
                # Set to dual status
                new_status = 'Member is in good standing, Staff Member'
                
                cursor.execute("""
                    UPDATE members 
                    SET status_message = ?,
                        updated_at = ?
                    WHERE prospect_id = ?
                """, (new_status, datetime.now().isoformat(), member_id))
                
                if cursor.rowcount > 0:
                    print(f"  ✅ Updated {member['full_name']} to dual status: '{new_status}'")
                    fixed_count += 1
                else:
                    print(f"  ⚠️ Failed to update {member['full_name']}")
            else:
                print(f"  ❌ Member with ID '{member_id}' not found!")
        
        # Verify all staff now have correct dual status
        print(f"\n📊 Final staff status verification:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        final_staff = cursor.fetchall()
        print(f"Total staff members: {len(final_staff)}")
        
        all_have_dual = True
        for staff in final_staff:
            has_dual = 'Member is in good standing' in staff['status_message']
            status_icon = "✅" if has_dual else "❌"
            print(f"  {status_icon} {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
            if not has_dual:
                all_have_dual = False
        
        # Check green members count to verify staff are included
        print(f"\n📊 Verifying green members count (should include all staff):")
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Member is in good standing%'
        """)
        
        green_count = cursor.fetchone()['count']
        print(f"  Green members (Member is in good standing): {green_count}")
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Staff%'
        """)
        
        staff_count = cursor.fetchone()['count']
        print(f"  Staff members: {staff_count}")
        
        # Commit changes
        conn.commit()
        
        print(f"\n🎉 Staff dual status fix completed!")
        print(f"📊 Summary:")
        print(f"  - Fixed staff members: {fixed_count}")
        print(f"  - Total staff members: {len(final_staff)}")
        print(f"  - All have dual status: {'✅ Yes' if all_have_dual else '❌ No'}")
        print(f"  - Green members count: {green_count}")
        
        if all_have_dual:
            print(f"✅ All staff members now count as both GREEN members AND staff!")
        else:
            print(f"⚠️ Some staff members still missing dual status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during staff dual status fix: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting staff dual status fix...")
    success = fix_staff_dual_status()
    
    if success:
        print("\n✅ Staff dual status fix completed successfully!")
    else:
        print("\n❌ Staff dual status fix failed!")
        sys.exit(1)