#!/usr/bin/env python3
"""
Investigate and test the actual ban functionality
Check if Timothy Greuel is really banned and debug the ban system
"""

import sqlite3
from src.services.member_access_control import MemberAccessControl
from src.services.api.clubhub_api_client import ClubHubAPIClient

def investigate_ban_system():
    print('🔍 === Investigating Ban System ===')
    
    # First, let's check Timothy Greuel's current ban status via API
    print('\n🔍 Checking Timothy Greuel ban status via ClubHub API...')
    
    try:
        # Initialize ClubHub client
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        email = secrets_manager.get_secret("clubhub-email")
        password = secrets_manager.get_secret("clubhub-password")
        
        client = ClubHubAPIClient()
        auth_success = client.authenticate(email, password)
        
        if not auth_success:
            print("❌ Failed to authenticate with ClubHub")
            return
            
        print("✅ ClubHub authentication successful")
        
        # Try to get Timothy Greuel's ban status
        member_id = "63235560"  # Timothy Greuel's ID
        
        print(f'\n🔍 Checking ban status for member {member_id}...')
        
        # Try different approaches to check ban status
        # 1. Try to get member bans (this might return 405 but let's see)
        print("1. Attempting GET member bans...")
        try:
            ban_status = client.get_member_bans(member_id)
            print(f"   Ban status response: {ban_status}")
        except Exception as e:
            print(f"   GET bans failed: {e}")
        
        # 2. Try to get member details to see if banned status is included
        print("2. Getting member details...")
        try:
            member_details = client.get_member_details(member_id)
            if member_details:
                print(f"   Member details keys: {list(member_details.keys()) if isinstance(member_details, dict) else 'Not a dict'}")
                # Look for ban-related fields
                ban_fields = []
                if isinstance(member_details, dict):
                    for key, value in member_details.items():
                        if 'ban' in key.lower() or 'lock' in key.lower() or 'access' in key.lower():
                            ban_fields.append(f"{key}: {value}")
                
                if ban_fields:
                    print(f"   Ban-related fields found:")
                    for field in ban_fields:
                        print(f"     {field}")
                else:
                    print(f"   No obvious ban-related fields found")
            else:
                print(f"   No member details returned")
        except Exception as e:
            print(f"   Get member details failed: {e}")
        
        # 3. Try to check if member can access gym (attempt a check-in)
        print("3. Testing access by attempting check-in...")
        try:
            from datetime import datetime
            checkin_data = {
                "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                "door": {"id": 772},
                "club": {"id": 1156},
                "manual": True
            }
            
            checkin_result = client.post_member_usage(member_id, checkin_data)
            if checkin_result:
                print(f"   ⚠️ Check-in SUCCEEDED - member is NOT banned! Result: {checkin_result}")
            else:
                print(f"   ✅ Check-in FAILED - member might be banned")
        except Exception as e:
            print(f"   Check-in test failed: {e}")
            
        # 4. Let's examine the actual ban API call more closely
        print("\n4. Testing ban API call directly...")
        
        # Try the ban again but with more debugging
        ban_data = {
            "member": {"id": int(member_id)},
            "note": f"Test ban - debugging system"
        }
        
        print(f"   Ban data being sent: {ban_data}")
        
        # Make the ban request with detailed debugging
        try:
            ban_result = client.put_member_bans(member_id, ban_data)
            print(f"   Ban API response: {ban_result}")
            
            # Check if the response indicates success but no actual ban
            if ban_result and isinstance(ban_result, dict):
                if 'isBanned' in ban_result:
                    print(f"   isBanned field: {ban_result['isBanned']}")
                if 'banType' in ban_result:
                    print(f"   banType field: {ban_result['banType']}")
                if 'isAdminBan' in ban_result:
                    print(f"   isAdminBan field: {ban_result['isAdminBan']}")
                    
        except Exception as e:
            print(f"   Direct ban API call failed: {e}")
            
        # 5. Try to understand what banType 3 means
        print("\n5. Investigating ban types...")
        print("   banType 3 might not be an effective ban type")
        print("   Let's try different ban approaches...")
        
        # Try with different ban data structures
        alternative_ban_data = [
            {
                "member": {"id": int(member_id)},
                "note": "Test ban - alternative structure 1",
                "banType": 1  # Try different ban type
            },
            {
                "memberId": int(member_id),
                "note": "Test ban - alternative structure 2",
                "isAdminBan": True
            },
            {
                "member": {"id": int(member_id)},
                "note": "Test ban - alternative structure 3",
                "banType": 2,
                "isAdminBan": True
            }
        ]
        
        for i, alt_data in enumerate(alternative_ban_data, 1):
            print(f"   Trying alternative ban structure {i}: {alt_data}")
            try:
                result = client.put_member_bans(member_id, alt_data)
                print(f"     Result: {result}")
            except Exception as e:
                print(f"     Failed: {e}")
                
    except Exception as e:
        print(f"❌ Investigation failed: {e}")

def check_timothy_actual_access():
    """Check if Timothy can actually access the gym by trying a check-in"""
    print('\n🧪 === Testing Timothy\'s Actual Access ===')
    
    try:
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        email = secrets_manager.get_secret("clubhub-email")
        password = secrets_manager.get_secret("clubhub-password")
        
        client = ClubHubAPIClient()
        auth_success = client.authenticate(email, password)
        
        if auth_success:
            member_id = "63235560"
            from datetime import datetime
            
            checkin_data = {
                "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                "door": {"id": 772},
                "club": {"id": 1156},
                "manual": True
            }
            
            print(f"Attempting check-in for member {member_id}...")
            result = client.post_member_usage(member_id, checkin_data)
            
            if result:
                print(f"🚨 PROBLEM: Member {member_id} can still check in! Ban is NOT working!")
                print(f"Check-in result: {result}")
                return False
            else:
                print(f"✅ Good: Member {member_id} cannot check in - ban appears to be working")
                return True
        else:
            print("❌ Could not authenticate to test access")
            return None
            
    except Exception as e:
        print(f"❌ Access test failed: {e}")
        return None

if __name__ == "__main__":
    investigate_ban_system()
    check_timothy_actual_access()