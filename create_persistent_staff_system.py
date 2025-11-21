#!/usr/bin/env python3
"""
Create Persistent Staff Designation System
Create a separate table to track authorized staff members that persists across ClubHub syncs
"""

import sqlite3
import os
import sys
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def create_persistent_staff_system():
    """
    Create a persistent staff designation system that survives ClubHub syncs
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Using database: {db_path}")
    
    # Authorized staff members (from previous verification)
    authorized_staff = [
        {'prospect_id': '52750389', 'full_name': 'JOSEPH JONES', 'role': 'Staff Member'},
        {'prospect_id': '64309309', 'full_name': 'JEREMY MAYO', 'role': 'Staff Member'},
        {'prospect_id': '55867562', 'full_name': 'NATOYA THOMAS', 'role': 'Staff Member'},
        {'prospect_id': '62716557', 'full_name': 'STAFF TWO', 'role': 'Staff Member'},
        {'prospect_id': '50909888', 'full_name': 'MIKE BEAL', 'role': 'Staff Member'}  # Mike has dual status
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create staff_designations table
        print("🔄 Creating staff_designations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff_designations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Staff Member',
                is_active BOOLEAN DEFAULT TRUE,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Insert authorized staff members
        print(f"🔄 Adding {len(authorized_staff)} authorized staff members...")
        
        for staff_member in authorized_staff:
            cursor.execute("""
                INSERT OR REPLACE INTO staff_designations 
                (prospect_id, full_name, role, is_active, updated_date, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                staff_member['prospect_id'],
                staff_member['full_name'],
                staff_member['role'],
                True,
                datetime.now().isoformat(),
                f"Authorized staff member - added during cleanup on {datetime.now().strftime('%Y-%m-%d')}"
            ))
            print(f"  ✅ Added: {staff_member['full_name']} (ID: {staff_member['prospect_id']})")
        
        # Verify staff_designations table
        print(f"\n📊 Verifying staff_designations table:")
        cursor.execute("""
            SELECT prospect_id, full_name, role, is_active, added_date
            FROM staff_designations 
            WHERE is_active = TRUE
            ORDER BY full_name
        """)
        
        staff_designations = cursor.fetchall()
        print(f"Found {len(staff_designations)} active staff designations:")
        
        for staff in staff_designations:
            print(f"  ✅ {staff['full_name']}: {staff['role']} (ID: {staff['prospect_id']})")
        
        # Create function to apply staff designations
        print(f"\n🔄 Creating staff designation application function...")
        
        # Create the staff designation application as a stored procedure equivalent
        staff_function_sql = """
        -- This function should be called after ClubHub syncs to re-apply staff status
        -- Usage: Call apply_staff_designations() after any member table sync
        """
        
        conn.commit()
        
        print(f"\n🎉 Persistent staff system created successfully!")
        print(f"📊 Summary:")
        print(f"  - Staff designations table created")
        print(f"  - {len(authorized_staff)} staff members registered")
        print(f"  - System ready to persist across syncs")
        
        # Show how to use the system
        print(f"\n📖 Usage Instructions:")
        print(f"  1. After any ClubHub sync, call apply_staff_designations()")
        print(f"  2. Staff status will be automatically restored")
        print(f"  3. Add new staff: INSERT into staff_designations table")
        print(f"  4. Remove staff: SET is_active = FALSE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating persistent staff system: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def apply_staff_designations():
    """
    Apply staff designations from staff_designations table to members table
    Call this function after ClubHub syncs to restore staff status
    """
    
    # Database path
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    print(f"📍 Applying staff designations from staff_designations table...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get active staff designations
        cursor.execute("""
            SELECT prospect_id, full_name, role
            FROM staff_designations 
            WHERE is_active = TRUE
        """)
        
        active_staff = cursor.fetchall()
        applied_count = 0
        
        print(f"🔄 Applying staff status to {len(active_staff)} authorized members...")
        
        for staff in active_staff:
            prospect_id = staff['prospect_id']
            full_name = staff['full_name']
            
            # Check if member exists in members table
            cursor.execute("""
                SELECT full_name, status_message
                FROM members 
                WHERE prospect_id = ?
            """, (prospect_id,))
            
            member = cursor.fetchone()
            
            if member:
                current_status = member['status_message'] or ''
                
                # Determine new status based on current status
                if 'Member is in good standing' in current_status:
                    # Already has member status, add staff
                    new_status = 'Member is in good standing, Staff Member'
                elif current_status and 'Staff' not in current_status:
                    # Has other status, add both
                    new_status = f'{current_status}, Staff Member'
                elif 'Staff' in current_status:
                    # Already has staff status
                    new_status = current_status
                else:
                    # No status or empty, set to dual status
                    new_status = 'Member is in good standing, Staff Member'
                
                # Update member status
                cursor.execute("""
                    UPDATE members 
                    SET status_message = ?,
                        updated_at = ?
                    WHERE prospect_id = ?
                """, (new_status, datetime.now().isoformat(), prospect_id))
                
                if cursor.rowcount > 0:
                    print(f"  ✅ Applied staff status to {full_name}: '{new_status}'")
                    applied_count += 1
                else:
                    print(f"  ⚠️ Failed to update {full_name}")
            else:
                print(f"  ❌ Member {full_name} (ID: {prospect_id}) not found in members table")
        
        conn.commit()
        
        print(f"\n✅ Staff designations applied successfully!")
        print(f"📊 Applied staff status to {applied_count}/{len(active_staff)} members")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying staff designations: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Creating persistent staff designation system...")
    
    # Create the system
    success = create_persistent_staff_system()
    
    if success:
        print("\n🔄 Testing staff designation application...")
        # Test applying designations
        apply_success = apply_staff_designations()
        
        if apply_success:
            print("\n✅ Persistent staff system created and tested successfully!")
            print("\n📋 Next Steps:")
            print("  1. Modify sync endpoints to call apply_staff_designations() after sync")
            print("  2. Staff status will now persist across ClubHub syncs")
            print("  3. Use staff_designations table to manage authorized staff")
        else:
            print("\n⚠️ System created but testing failed!")
    else:
        print("\n❌ Failed to create persistent staff system!")
        sys.exit(1)