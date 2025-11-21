#!/usr/bin/env python3
"""
Comprehensive Staff System Verification
Test and verify the persistent staff designation system works correctly
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def comprehensive_staff_verification():
    """
    Comprehensive verification of the staff designation system
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    print(f"🔍 Comprehensive Staff System Verification\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Verify staff_designations table exists and has correct data
        print("1️⃣ **STAFF_DESIGNATIONS TABLE VERIFICATION**")
        cursor.execute("""
            SELECT prospect_id, full_name, role, is_active, added_date, notes
            FROM staff_designations 
            WHERE is_active = TRUE
            ORDER BY full_name
        """)
        
        staff_designations = cursor.fetchall()
        
        if staff_designations:
            print(f"✅ staff_designations table exists with {len(staff_designations)} active entries:")
            for staff in staff_designations:
                print(f"   • {staff['full_name']} (ID: {staff['prospect_id']}) - {staff['role']}")
        else:
            print("❌ No active staff designations found!")
            return False
        
        # 2. Verify current staff status in members table
        print(f"\n2️⃣ **MEMBERS TABLE STAFF STATUS**")
        cursor.execute("""
            SELECT full_name, status_message, prospect_id 
            FROM members 
            WHERE status_message LIKE '%Staff%' 
            ORDER BY full_name
        """)
        
        current_staff = cursor.fetchall()
        
        if current_staff:
            print(f"✅ Found {len(current_staff)} members with staff status:")
            all_have_dual = True
            for staff in current_staff:
                has_member_status = 'Member is in good standing' in staff['status_message']
                has_staff_status = 'Staff Member' in staff['status_message']
                dual_status = has_member_status and has_staff_status
                status_icon = "✅" if dual_status else "❌"
                
                print(f"   {status_icon} {staff['full_name']}: '{staff['status_message']}' (ID: {staff['prospect_id']})")
                
                if not dual_status:
                    all_have_dual = False
            
            if all_have_dual:
                print("🎉 All staff members have correct dual status!")
            else:
                print("⚠️ Some staff members missing dual status")
        else:
            print("❌ No staff members found in members table!")
        
        # 3. Verify green members count includes staff
        print(f"\n3️⃣ **GREEN MEMBERS COUNT VERIFICATION**")
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Member is in good standing%'
        """)
        
        green_count = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Staff%'
        """)
        
        staff_count = cursor.fetchone()['count']
        
        print(f"📊 Green members (Member is in good standing): {green_count}")
        print(f"📊 Staff members: {staff_count}")
        print(f"📊 Staff members should be included in green count: {'✅ Yes' if staff_count <= green_count else '❌ No'}")
        
        # 4. Test staff designation application function
        print(f"\n4️⃣ **STAFF DESIGNATION FUNCTION TEST**")
        try:
            from src.utils.staff_designations import apply_staff_designations, verify_staff_designations
            
            # Test apply function
            success, applied_count, message = apply_staff_designations()
            print(f"✅ apply_staff_designations() result: {message}")
            
            # Test verification function
            verification = verify_staff_designations()
            if verification['success']:
                print(f"✅ verify_staff_designations() - All correct: {verification['all_correct']}")
                print(f"📊 Total authorized staff: {verification['total_staff']}")
            else:
                print(f"❌ verify_staff_designations() error: {verification['error']}")
                
        except Exception as e:
            print(f"❌ Error testing staff functions: {e}")
        
        # 5. Simulate sync impact test
        print(f"\n5️⃣ **SYNC PERSISTENCE SIMULATION**")
        print("🔄 Simulating ClubHub sync by temporarily removing staff status...")
        
        # Store current statuses
        original_statuses = {}
        for staff in staff_designations:
            cursor.execute("""
                SELECT status_message FROM members WHERE prospect_id = ?
            """, (staff['prospect_id'],))
            
            result = cursor.fetchone()
            if result:
                original_statuses[staff['prospect_id']] = result['status_message']
        
        # Simulate sync by removing staff status (set to just Member is in good standing)
        for staff_id in original_statuses:
            cursor.execute("""
                UPDATE members 
                SET status_message = 'Member is in good standing'
                WHERE prospect_id = ?
            """, (staff_id,))
        
        print("   📝 Temporarily removed staff status (simulating ClubHub sync overwrite)")
        
        # Verify staff status is gone
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Staff%'
        """)
        
        temp_staff_count = cursor.fetchone()['count']
        print(f"   📊 Staff count after simulated sync: {temp_staff_count}")
        
        # Now restore using our function
        success, restored_count, message = apply_staff_designations()
        print(f"   🔄 Staff restoration result: {message}")
        
        # Verify restoration worked
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Staff%'
        """)
        
        final_staff_count = cursor.fetchone()['count']
        print(f"   📊 Staff count after restoration: {final_staff_count}")
        
        # Restore original transaction (rollback simulation changes)
        conn.rollback()
        print("   ↩️ Simulation changes rolled back")
        
        # 6. Final Summary
        print(f"\n6️⃣ **FINAL VERIFICATION SUMMARY**")
        
        # Re-check everything after rollback
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Member is in good standing%' AND status_message LIKE '%Staff%'
        """)
        
        dual_status_count = cursor.fetchone()['count']
        
        success_checks = [
            len(staff_designations) == 5,  # 5 authorized staff in designations table
            len(current_staff) == 5,       # 5 staff members in members table
            all_have_dual,                 # All staff have dual status
            dual_status_count == 5,        # 5 members with both statuses
            staff_count <= green_count,    # Staff included in green count
            final_staff_count == 5         # Restoration function works
        ]
        
        all_checks_passed = all(success_checks)
        
        print(f"📋 System Status:")
        print(f"   • Staff designations table: {'✅' if len(staff_designations) == 5 else '❌'} ({len(staff_designations)}/5 entries)")
        print(f"   • Current staff members: {'✅' if len(current_staff) == 5 else '❌'} ({len(current_staff)}/5 members)")
        print(f"   • All have dual status: {'✅' if all_have_dual else '❌'}")
        print(f"   • Staff included in green: {'✅' if staff_count <= green_count else '❌'}")
        print(f"   • Restoration function works: {'✅' if final_staff_count == 5 else '❌'}")
        
        if all_checks_passed:
            print(f"\n🎉 **ALL SYSTEMS GO!**")
            print(f"✅ Staff designation system is fully operational")
            print(f"✅ Staff status will persist across ClubHub syncs")
            print(f"✅ Staff members count in both GREEN and STAFF categories")
            print(f"✅ System ready for production use")
        else:
            print(f"\n⚠️ **SOME ISSUES DETECTED**")
            print(f"❌ System needs attention before production use")
        
        return all_checks_passed
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Starting Comprehensive Staff System Verification...\n")
    success = comprehensive_staff_verification()
    
    if success:
        print(f"\n✅ Comprehensive verification PASSED!")
        print(f"\n📋 **ANSWER TO USER'S QUESTIONS:**")
        print(f"❓ 'Will sync undo everything?' → ✅ NO - Staff status now persists across syncs")
        print(f"❓ 'Will recategorizations persist?' → ✅ YES - Stored in staff_designations table") 
        print(f"❓ 'Are staff excluded from green count?' → ✅ NO - Staff count as BOTH green AND staff")
        print(f"❓ 'Should staff be in both categories?' → ✅ YES - All staff have dual status")
    else:
        print(f"\n❌ Comprehensive verification FAILED!")
        sys.exit(1)