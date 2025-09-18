#!/usr/bin/env python3
"""
Research effective ban types and methods
Try to find the correct way to actually block member access
"""

from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def research_effective_bans():
    print('🔬 === Researching Effective Ban Methods ===')
    
    try:
        # Authenticate
        secrets_manager = SecureSecretsManager()
        email = secrets_manager.get_secret("clubhub-email")
        password = secrets_manager.get_secret("clubhub-password")
        
        client = ClubHubAPIClient()
        auth_success = client.authenticate(email, password)
        
        if not auth_success:
            print("❌ Authentication failed")
            return
            
        member_id = "63235560"  # Timothy Greuel
        
        print('🔍 1. Testing different ban types systematically...')
        
        # Try ban types 0-10 to see which ones work
        for ban_type in range(0, 11):
            print(f'\n   Testing banType {ban_type}...')
            
            ban_data = {
                "member": {"id": int(member_id)},
                "note": f"Testing banType {ban_type} for effective access control",
                "banType": ban_type,
                "isAdminBan": True
            }
            
            try:
                # Apply ban
                ban_result = client.put_member_bans(member_id, ban_data)
                print(f"     Ban result: {ban_result}")
                
                # Test access immediately
                from datetime import datetime
                checkin_data = {
                    "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                    "door": {"id": 772},
                    "club": {"id": 1156},
                    "manual": True
                }
                
                access_result = client.post_member_usage(member_id, checkin_data)
                
                if access_result and access_result.get('admitted'):
                    print(f"     ❌ banType {ban_type}: Member can still access (admitted: {access_result.get('admitted')})")
                else:
                    print(f"     ✅ banType {ban_type}: ACCESS DENIED! This ban type works!")
                    print(f"        Access result: {access_result}")
                    
            except Exception as e:
                print(f"     Error testing banType {ban_type}: {e}")
        
        print('\n🔍 2. Trying alternative ban approaches...')
        
        # Try different API endpoints or methods
        alternative_methods = [
            {
                "name": "Admin Ban with banType 1",
                "data": {
                    "member": {"id": int(member_id)},
                    "note": "Admin ban - access restriction",
                    "banType": 1,
                    "isAdminBan": True,
                    "permanent": True
                }
            },
            {
                "name": "Security Ban with banType 2", 
                "data": {
                    "member": {"id": int(member_id)},
                    "note": "Security ban - no access",
                    "banType": 2,
                    "isAdminBan": True,
                    "reason": "PAYMENT_ISSUE"
                }
            }
        ]
        
        for method in alternative_methods:
            print(f'\n   Testing {method["name"]}...')
            try:
                ban_result = client.put_member_bans(member_id, method["data"])
                print(f"     Ban result: {ban_result}")
                
                # Test access
                access_result = client.post_member_usage(member_id, checkin_data)
                if access_result and access_result.get('admitted'):
                    print(f"     ❌ {method['name']}: Still allows access")
                else:
                    print(f"     ✅ {method['name']}: ACCESS BLOCKED!")
                    
            except Exception as e:
                print(f"     Error with {method['name']}: {e}")
        
        print('\n🔍 3. Investigating member status modification...')
        
        # Maybe we need to change member status instead of using bans
        # Try to find member update endpoints
        try:
            # Get current member status
            member_details = client.get_member_details(member_id)
            if member_details:
                current_status = member_details.get('status')
                print(f"   Current member status: {current_status}")
                
                # Look for status codes that might disable access
                status_codes_to_try = [0, 2, 3, 5, 9, 10, 99]  # Common "disabled" status codes
                
                for status_code in status_codes_to_try:
                    print(f"   Investigating what status {status_code} means...")
                    # We won't actually change the status without knowing what it means
                    # But we can research the status codes
                    
        except Exception as e:
            print(f"   Error investigating member status: {e}")
        
        print('\n🔍 4. Checking if there\'s a separate access control system...')
        
        # Maybe there's a different endpoint for access control
        # Let's see what other endpoints are available
        try:
            # Try to find access-specific endpoints
            print("   Looking for access control endpoints...")
            
            # Maybe there's a door access endpoint
            # Or a member privileges endpoint
            # Or a suspension system separate from bans
            
            print("   This may require reviewing ClubHub API documentation")
            print("   to find the correct access restriction method")
            
        except Exception as e:
            print(f"   Error: {e}")
            
    except Exception as e:
        print(f"❌ Research failed: {e}")

if __name__ == "__main__":
    research_effective_bans()