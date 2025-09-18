#!/usr/bin/env python3
"""
Reclassify Unauthorized Staff Members (Case-Insensitive)
Remove staff status from unauthorized users using case-insensitive matching
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def reclassify_unauthorized_staff_v2():
    """
    Reclassify unauthorized staff members using case-insensitive matching
    Based on actual database names found in previous verification
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    # Based on the previous run, these are the unauthorized staff members that need reclassification:
    # (using exact names from database)
    unauthorized_staff_ids = [
        '63318583',  # HOPE BRENNENSTUHL
        '55867069',  # JACOB LIETZ  
        '48371369',  # KAYLA MUELLER
        '65225549',  # KENDALL BRESTER
        '51676004',  # LINDA DAKE
        '48405704'   # STACY FUESTON1
    ]
    
    # Mike Beal should be kept as staff (ID: 50909888)
    # The other 4 authorized staff members (Joseph Jones, Jeremy Mayo, Natoya Thomas, Staff Two) 
    # don't appear to be in the database with staff status currently
    
    print(f"🔄 Reclassifying {len(unauthorized_staff_ids)} unauthorized staff members by ID...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Show current state
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
        
        # Reclassify unauthorized staff members by ID
        reclassified_count = 0
        
        for member_id in unauthorized_staff_ids:
            print(f"\n🔄 Processing member ID: {member_id}")
            
            # Find the member by ID
            cursor.execute("""
                SELECT full_name, status_message, prospect_id 
                FROM members 
                WHERE prospect_id = ? AND status_message LIKE '%Staff%'
            """, (member_id,))
            
            member = cursor.fetchone()
            
            if member:
                print(f"  📍 Found: {member['full_name']} with status '{member['status_message']}'")
                
                # Update their status to 'Member is in good standing'
                cursor.execute("""
                    UPDATE members 
                    SET status_message = 'Member is in good standing',
                        updated_at = ?
                    WHERE prospect_id = ? AND status_message LIKE '%Staff%'
                """, (datetime.now().isoformat(), member_id))
                
                if cursor.rowcount > 0:
                    print(f"  ✅ Reclassified {member['full_name']} to 'Member is in good standing'")
                    reclassified_count += 1
                else:
                    print(f"  ⚠️ Failed to update {member['full_name']}")
            else:
                print(f"  ⚠️ Member ID '{member_id}' not found or doesn't have staff status")
        
        # Check Mike Beal's status (should remain staff)
        print(f"\n📊 Verifying Mike Beal's staff status:")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE prospect_id = '50909888'
        """, )
        
        mike_beal = cursor.fetchone()
        if mike_beal:
            print(f"  ✅ {mike_beal['full_name']}: {mike_beal['status_message']} (ID: {mike_beal['prospect_id']})")
        else:
            print(f"  ❌ Mike Beal not found!")
        
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
            print(f"  - {staff['full_name']}: {staff['status_message']} (ID: {staff['prospect_id']})")
        
        # Commit changes
        conn.commit()
        
        print(f"\n🎉 Staff cleanup completed successfully!")
        print(f"📊 Summary:")
        print(f"  - Reclassified: {reclassified_count} unauthorized staff members")
        print(f"  - Remaining staff: {len(final_staff)} members")
        print(f"  - Expected: 1 staff member (Mike Beal)")
        
        if len(final_staff) == 1:
            print(f"✅ Staff count matches expected (1 member)")
        else:
            print(f"⚠️ Staff count: Expected 1, got {len(final_staff)}")
            if len(final_staff) > 1:
                print("ℹ️ Note: Other authorized staff may need to be added separately if they should have staff status")
        
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
    print("🔄 Starting unauthorized staff reclassification process (v2)...")
    success = reclassify_unauthorized_staff_v2()
    
    if success:
        print("\n✅ Staff reclassification completed successfully!")
    else:
        print("\n❌ Staff reclassification failed!")
        sys.exit(1)