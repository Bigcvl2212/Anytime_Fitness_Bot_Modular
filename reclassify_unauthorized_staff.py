#!/usr/bin/env python3
"""
Reclassify Unauthorized Staff Members
Remove staff status from 11 unauthorized users and reclassify them as regular members
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def reclassify_unauthorized_staff():
    """
    Reclassify unauthorized staff members to 'Member is in good standing' status
    Keep only 5 legitimate staff members: Joseph Jones, Jeremy Mayo, Natoya Thomas, Staff Two, Mike Beal
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    # List of unauthorized staff members to reclassify
    unauthorized_staff = [
        'Anytime Test',
        'Brandon Pagel', 
        'Hope Brennenstuhl',
        'Jacob Lietz',
        'Joe Laurent',
        'Kayla Mueller',
        'Kendall Brester',
        'Linda Dake',
        'Stacy Fueston1',
        'Stacy Fueston',
        'Staff One'
    ]
    
    # Authorized staff members (should keep staff status)
    authorized_staff = [
        'Joseph Jones',
        'Jeremy Mayo', 
        'Natoya Thomas',
        'Staff Two',
        'Mike Beal'
    ]
    
    print(f"🔄 Reclassifying {len(unauthorized_staff)} unauthorized staff members...")
    print(f"✅ Preserving staff status for {len(authorized_staff)} authorized staff members...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First, let's verify current staff status
        print("\n📊 Current staff members before changes:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        current_staff = cursor.fetchall()
        print(f"Found {len(current_staff)} members with staff status:")
        
        for staff in current_staff:
            print(f"  - {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
        
        # Reclassify unauthorized staff members
        reclassified_count = 0
        
        for member_name in unauthorized_staff:
            print(f"\n🔄 Processing: {member_name}")
            
            # Find the member
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE full_name = ? AND status_message LIKE '%Staff%'
            """, (member_name,))
            
            member = cursor.fetchone()
            
            if member:
                print(f"  📍 Found: {member['full_name']} with status '{member['status_message']}'")
                
                # Update their status to 'Member is in good standing'
                cursor.execute("""
                    UPDATE members 
                    SET status_message = 'Member is in good standing',
                        updated_at = ?
                    WHERE full_name = ? AND status_message LIKE '%Staff%'
                """, (datetime.now().isoformat(), member_name))
                
                if cursor.rowcount > 0:
                    print(f"  ✅ Reclassified {member['full_name']} to 'Member is in good standing'")
                    reclassified_count += 1
                else:
                    print(f"  ⚠️ Failed to update {member['full_name']}")
            else:
                print(f"  ⚠️ Member '{member_name}' not found or doesn't have staff status")
        
        # Verify authorized staff still have appropriate status
        print(f"\n📊 Verifying authorized staff members:")
        
        for staff_name in authorized_staff:
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE full_name = ?
            """, (staff_name,))
            
            member = cursor.fetchone()
            
            if member:
                print(f"  ✅ {member['full_name']}: {member['status_message']} (ID: {member['prospect_id']})")
            else:
                print(f"  ❌ Authorized staff member '{staff_name}' not found!")
        
        # Final staff count verification
        print(f"\n📊 Final staff status verification:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        final_staff = cursor.fetchall()
        print(f"Total members with staff status after cleanup: {len(final_staff)}")
        
        for staff in final_staff:
            is_authorized = staff['full_name'] in authorized_staff
            status_icon = "✅" if is_authorized else "⚠️"
            print(f"  {status_icon} {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
        
        # Commit changes
        conn.commit()
        
        print(f"\n🎉 Staff cleanup completed successfully!")
        print(f"📊 Summary:")
        print(f"  - Reclassified: {reclassified_count} unauthorized staff members")
        print(f"  - Remaining staff: {len(final_staff)} members")
        print(f"  - Expected staff: {len(authorized_staff)} members")
        
        if len(final_staff) == len(authorized_staff):
            print(f"✅ Staff count matches expected ({len(authorized_staff)} members)")
        else:
            print(f"⚠️ Staff count mismatch! Expected {len(authorized_staff)}, got {len(final_staff)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during staff reclassification: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting unauthorized staff reclassification process...")
    success = reclassify_unauthorized_staff()
    
    if success:
        print("\n✅ Staff reclassification completed successfully!")
    else:
        print("\n❌ Staff reclassification failed!")
        sys.exit(1)