#!/usr/bin/env python3
"""
Test completely fresh authentication with Mark Benzinger
"""
import sys
sys.path.append('.')
sys.path.append('src')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI
from src.config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
import time

def test_fresh():
    print("🧪 Testing fresh authentication with Mark Benzinger")
    print(f"📝 Username: {CLUBOS_USERNAME}")
    print(f"🔐 Password length: {len(CLUBOS_PASSWORD) if CLUBOS_PASSWORD else 0}")
    
    try:
        # Create completely fresh API instance
        api = ClubOSTrainingPackageAPI()
        api.username = CLUBOS_USERNAME
        api.password = CLUBOS_PASSWORD
        
        print("🔑 Step 1: Fresh Authentication")
        auth_result = api.authenticate()
        print(f"   Auth result: {auth_result}")
        print(f"   Session cookies: {list(api.session.cookies.keys())}")
        
        if not auth_result:
            print("❌ Authentication failed!")
            return
        
        print("\n👤 Step 2: Delegate to Mark's GUID (66082049)")
        # Clear any existing delegation cookies 
        cookies_to_remove = []
        for cookie in api.session.cookies:
            if cookie.name in ['delegatedUserId', 'staffDelegatedUserId']:
                cookies_to_remove.append((cookie.name, cookie.domain, cookie.path))
        
        for name, domain, path in cookies_to_remove:
            api.session.cookies.clear(domain, path, name)
        
        delegate_result = api.delegate_to_member("66082049")
        print(f"   Delegate result: {delegate_result}")
        
        # Check delegation cookies
        delegation_cookies = []
        for cookie in api.session.cookies:
            if cookie.name == 'delegatedUserId':
                delegation_cookies.append(cookie.value)
        print(f"   Delegation cookies: {delegation_cookies}")
        
        if not delegate_result:
            print("❌ Delegation failed!")
            return
            
        print("\n📋 Step 3: Test /list endpoint directly")
        timestamp = int(time.time() * 1000)
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{api.base_url}/action/PackageAgreementUpdated/spa/',
        }
        
        # Add authorization if available
        bearer = api.session_data.get('apiV3AccessToken') or api.access_token
        if bearer:
            headers['Authorization'] = f'Bearer {bearer}'
        
        list_url = f"{api.base_url}/api/agreements/package_agreements/list"
        params = {
            'memberId': '66082049',  # Mark's GUID
            '_': timestamp
        }
        
        print(f"   URL: {list_url}")
        print(f"   Params: {params}")
        print(f"   Headers: {headers}")
        
        response = api.session.get(list_url, headers=headers, params=params, timeout=15)
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        print(f"   Response body: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS: Found {len(data) if isinstance(data, list) else 'N/A'} agreements")
                print(f"   Data: {data}")
            except Exception as e:
                print(f"❌ JSON parsing error: {e}")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fresh()
