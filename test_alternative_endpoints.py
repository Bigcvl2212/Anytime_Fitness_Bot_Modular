#!/usr/bin/env python3
"""
Test alternative ClubOS endpoints to find the working one
"""

print("🧪 TESTING ALTERNATIVE CLUBOS ENDPOINTS")
print("=" * 50)

try:
    # Import the working API
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
    from src.config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
    
    # Test member details
    member_id = "125814462"  # Mark Benzinger's clubos_member_id
    expected_guid = "66082049"  # Mark Benzinger's GUID
    
    # Create API instance
    api = ClubOSTrainingPackageAPI()
    api.username = CLUBOS_USERNAME
    api.password = CLUBOS_PASSWORD
    
    # Authenticate and delegate
    api.authenticate()
    api.delegate_to_member(expected_guid)
    
    print(f"🔍 Testing alternative endpoints for GUID: {expected_guid}")
    print()
    
    # Test different endpoints
    endpoints_to_test = [
        f"/api/agreements/package_agreements/list?memberId={expected_guid}",
        f"/api/members/{expected_guid}/agreements",
        f"/api/members/{expected_guid}/agreements/package",
        f"/api/training/clients",
        f"/api/agreements/list?memberId={expected_guid}",
        f"/api/package_agreements/list?memberId={expected_guid}",
        f"/api/agreements?memberId={expected_guid}",
        f"/api/members/{expected_guid}/packages",
        f"/api/training/packages?memberId={expected_guid}"
    ]
    
    import time
    timestamp = int(time.time() * 1000)
    
    for i, endpoint in enumerate(endpoints_to_test, 1):
        print(f"🧪 Test {i}: {endpoint}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'{api.base_url}/action/Dashboard/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        # Add bearer token if available
        bearer = api.session_data.get('apiV3AccessToken') or api.access_token
        if bearer:
            headers['Authorization'] = f'Bearer {bearer}'
        
        url = f"{api.base_url}{endpoint}"
        if '?' not in endpoint:
            url += f"?_={timestamp}"
        
        try:
            response = api.session.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ SUCCESS! Response type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   ✅ Array with {len(data)} items")
                        if data:
                            print(f"   ✅ Sample item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not dict'}")
                    elif isinstance(data, dict):
                        print(f"   ✅ Object with keys: {list(data.keys())}")
                    print(f"   ✅ Raw data (first 200 chars): {str(data)[:200]}...")
                    print()
                except:
                    print(f"   ⚠️ Success but invalid JSON: {response.text[:100]}...")
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
