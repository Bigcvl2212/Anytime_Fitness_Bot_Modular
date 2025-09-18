#!/usr/bin/env python3
"""
Check if "Staff Member" status people exist in ClubOS using the correct ClubOS API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager
from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_staff_members():
    """Check 21 'Staff Member' status people in ClubOS using the correct API"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        
        # Get all "Staff Member" status people (should be 22)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prospect_id, first_name, last_name, full_name, email, mobile_phone 
            FROM members 
            WHERE status = 'Staff Member'
        """)
        
        staff_members = cursor.fetchall()
        conn.close()
        
        print(f"Found {len(staff_members)} people with 'Staff Member' status")
        
        # Real staff (prospect_ids from database_manager.py)
        real_staff_ids = {'191003722', '189425730', '191210406', '191015549', '191201279'}
        
        # Initialize ClubOS API
        clubos_api = ClubOSTrainingPackageAPI()
        
        # Authenticate with ClubOS
        if not clubos_api.authenticate():
            print("❌ Failed to authenticate with ClubOS")
            return None
            
        print("✅ Authenticated with ClubOS")
        
        # Check each person in ClubOS
        found_active = []
        found_inactive = []
        not_found = []
        
        for member in staff_members:
            prospect_id, first_name, last_name, full_name, email, mobile_phone = member
            
            # Skip real staff
            if str(prospect_id) in real_staff_ids:
                print(f"✅ REAL STAFF: {full_name} (ID: {prospect_id})")
                continue
            
            print(f"\n🔍 Checking: {full_name} (ID: {prospect_id})")
            
            # Search for this person in ClubOS
            try:
                # Search by name and email if available
                clubos_member_id = clubos_api.search_member_id(full_name, email, mobile_phone)
                
                if clubos_member_id:
                    # Found in ClubOS - check payment status as a proxy for active/inactive
                    payment_status = clubos_api.get_member_payment_status(clubos_member_id)
                    
                    if payment_status:
                        # If they have a payment status, they're likely active
                        found_active.append((prospect_id, full_name, clubos_member_id, payment_status))
                        print(f"✅ FOUND ACTIVE: {full_name} - ClubOS ID: {clubos_member_id} - Payment: {payment_status}")
                    else:
                        # Found but no payment status - could be inactive
                        found_inactive.append((prospect_id, full_name, clubos_member_id, 'No payment data'))
                        print(f"⚠️ FOUND INACTIVE: {full_name} - ClubOS ID: {clubos_member_id} - No payment data")
                else:
                    not_found.append((prospect_id, full_name))
                    print(f"❌ NOT FOUND: {full_name}")
                    
            except Exception as e:
                print(f"❌ ERROR checking {full_name}: {e}")
                not_found.append((prospect_id, full_name))
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"Real Staff: {len(real_staff_ids)} members")
        print(f"Found Active: {len(found_active)} members")
        print(f"Found Inactive: {len(found_inactive)} members") 
        print(f"Not Found: {len(not_found)} members")
        print(f"Total checked: {len(staff_members) - len(real_staff_ids)} members")
        
        # Show details
        if found_active:
            print(f"\n✅ FOUND ACTIVE ({len(found_active)}):")
            for prospect_id, name, clubos_id, payment in found_active:
                print(f"  - {name} (DB: {prospect_id}, ClubOS: {clubos_id}, Payment: {payment})")
        
        if found_inactive:
            print(f"\n⚠️ FOUND INACTIVE ({len(found_inactive)}):")
            for prospect_id, name, clubos_id, payment in found_inactive:
                print(f"  - {name} (DB: {prospect_id}, ClubOS: {clubos_id}, Status: {payment})")
        
        if not_found:
            print(f"\n❌ NOT FOUND ({len(not_found)}):")
            for prospect_id, name in not_found:
                print(f"  - {name} (DB: {prospect_id})")
        
        # Show categorization recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"- Move {len(found_active)} to 'Green' category")
        print(f"- Move {len(found_inactive) + len(not_found)} to 'Inactive' category")
        
        return {
            'real_staff': real_staff_ids,
            'found_active': found_active,
            'found_inactive': found_inactive,
            'not_found': not_found
        }
        
    except Exception as e:
        logger.error(f"Error checking staff members: {e}")
        return None

if __name__ == "__main__":
    results = check_staff_members()