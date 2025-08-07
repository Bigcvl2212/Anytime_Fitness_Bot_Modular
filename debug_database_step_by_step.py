#!/usr/bin/env python3
"""
Debug database queries step by step
"""

import sqlite3
import json

def debug_database():
    """Debug database step by step"""
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print("🔍 Debugging database queries...")
    
    # 1. Check if members table exists and has data
    cursor.execute("SELECT COUNT(*) FROM members")
    member_count = cursor.fetchone()[0]
    print(f"   Total members in database: {member_count}")
    
    # 2. Check status values
    try:
        cursor.execute("SELECT DISTINCT status FROM members LIMIT 10")
        statuses = cursor.fetchall()
        print(f"   Status values: {[s[0] for s in statuses]}")
    except Exception as e:
        print(f"   Error getting statuses: {e}")
    
    # 3. Check status messages
    try:
        cursor.execute("SELECT DISTINCT status_message FROM members LIMIT 10")
        status_messages = cursor.fetchall()
        print(f"   Status messages: {[s[0] for s in status_messages if s[0]]}")
    except Exception as e:
        print(f"   Error getting status messages: {e}")
    
    # 4. Check Dennis specifically
    try:
        cursor.execute("SELECT id, full_name, status, status_message FROM members WHERE full_name LIKE '%DENNIS%' AND full_name LIKE '%ROST%'")
        dennis_results = cursor.fetchall()
        print(f"   Dennis results: {len(dennis_results)} found")
        for result in dennis_results:
            print(f"     {result}")
    except Exception as e:
        print(f"   Error finding Dennis: {e}")
    
    # 5. Get first 5 members to see data structure
    try:
        cursor.execute("SELECT id, full_name, status, status_message, last_visit FROM members LIMIT 5")
        sample_members = cursor.fetchall()
        print(f"   Sample members:")
        for member in sample_members:
            print(f"     {member}")
    except Exception as e:
        print(f"   Error getting sample members: {e}")
    
    # 6. Get members with recent activity (regardless of status)
    try:
        cursor.execute("""
            SELECT id, full_name, status, status_message, last_visit 
            FROM members 
            WHERE last_visit IS NOT NULL 
            AND last_visit != ''
            ORDER BY last_visit DESC 
            LIMIT 10
        """)
        recent_members = cursor.fetchall()
        print(f"   Recent active members: {len(recent_members)} found")
        for member in recent_members:
            print(f"     {member}")
    except Exception as e:
        print(f"   Error getting recent members: {e}")
    
    # 7. Test ClubOS API with Dennis's ID directly
    print(f"\n🧪 Testing ClubOS API with Dennis's ID (65828815)...")
    
    try:
        import sys
        sys.path.append('.')
        from clubos_training_api import ClubOSTrainingPackageAPI
        
        api = ClubOSTrainingPackageAPI()
        if api.authenticate():
            print("   ✅ ClubOS authentication successful")
            
            # Test Dennis's ID
            dennis_payment = api.get_member_payment_status("65828815")
            print(f"   Dennis payment status (65828815): {dennis_payment}")
            
            # Test a few other IDs to see if any work
            test_ids = ["65828815", "35043379", "46010869", "46091114"]
            for test_id in test_ids:
                payment = api.get_member_payment_status(test_id)
                print(f"   ID {test_id}: {payment}")
                
            # Also try some random member IDs from the sample
            if recent_members:
                for member in recent_members[:3]:
                    member_id = member[0]
                    member_name = member[1]
                    payment = api.get_member_payment_status(str(member_id))
                    print(f"   {member_name} (ID: {member_id}): {payment}")
        else:
            print("   ❌ ClubOS authentication failed")
            
    except Exception as e:
        print(f"   ❌ Error testing ClubOS API: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 Debugging database and API...")
    print("=" * 60)
    
    debug_database()
    
    print("\n" + "=" * 60)
    print("🏁 Debug complete!")
