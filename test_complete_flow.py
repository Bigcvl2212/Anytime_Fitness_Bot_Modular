#!/usr/bin/env python3
"""
Test the complete ClubOS API flow including permissions
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_complete_clubos_flow():
    """Test the complete ClubOS API flow matching your browser exactly"""
    
    print("🧪 Testing complete ClubOS API flow...")
    
    # Set up session
    session = requests.Session()
    
    # Step 1: Login to ClubOS
    login_url = "https://anytime.club-os.com/action/Login"
    login_data = {
        'email': CLUBOS_USERNAME,
        'password': CLUBOS_PASSWORD
    }
    
    print("🔐 Step 1: Logging into ClubOS...")
    login_response = session.post(login_url, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Step 1.5: Get session data by calling Login as GET (like existing code)
    print("📋 Step 1.5: Getting session data via GET /action/Login...")
    session_data_response = session.get("https://anytime.club-os.com/action/Login")
    
    if session_data_response.status_code == 200:
        try:
            session_data = session_data_response.json()
            print("✅ Session data retrieved successfully")
            
            # Extract tokens like the existing code does
            api_v3_access_token = session_data.get('apiV3AccessToken')
            api_v3_id_token = session_data.get('apiV3IdToken')
            
            if api_v3_access_token:
                print(f"✅ Found apiV3AccessToken in session data: {api_v3_access_token[:50]}...")
                # Set as cookie for consistency
                session.cookies.set('apiV3AccessToken', api_v3_access_token)
            
            if api_v3_id_token:
                print(f"✅ Found apiV3IdToken in session data: {api_v3_id_token[:50]}...")
                session.cookies.set('apiV3IdToken', api_v3_id_token)
                
        except Exception as e:
            print(f"⚠️ Could not parse session data as JSON: {e}")
            print(f"Response content: {session_data_response.text[:200]}")
    else:
        print(f"❌ Session data request failed: {session_data_response.status_code}")
    
    # Step 2: Navigate to Dashboard/view to finalize session
    print("🏠 Step 2: Navigating to Dashboard/view to finalize session...")
    dashboard_url = "https://anytime.club-os.com/action/Dashboard/view"
    dashboard_response = session.get(dashboard_url)
    
    if dashboard_response.status_code != 200:
        print(f"❌ Dashboard navigation failed: {dashboard_response.status_code}")
        return
    
    print("✅ Dashboard navigation successful")
    
    # Step 3: Check for API tokens in cookies
    print("🍪 Step 3: Checking for API tokens...")
    
    api_v3_access_token = None
    api_v3_id_token = None
    
    for cookie in session.cookies:
        if cookie.name == 'apiV3AccessToken':
            api_v3_access_token = cookie.value
            print(f"✅ Found apiV3AccessToken: {api_v3_access_token[:50]}...")
        elif cookie.name == 'apiV3IdToken':
            api_v3_id_token = cookie.value
            print(f"✅ Found apiV3IdToken: {api_v3_id_token[:50]}...")
        elif cookie.name == 'loggedInUserId':
            print(f"👤 Logged in user ID: {cookie.value}")
        elif cookie.name == 'delegatedUserId':
            print(f"🔄 Delegated user ID: {cookie.value}")
    
    if not api_v3_access_token:
        print("❌ No apiV3AccessToken found - this is required for API calls")
        return
    
    # Step 4: Check user permissions
    print("\n👮 Step 4: Checking user permissions...")
    
    # Extract user ID from the ID token or cookies
    user_id = None
    for cookie in session.cookies:
        if cookie.name == 'loggedInUserId':
            user_id = cookie.value
            break
    
    if user_id:
        permissions_url = f"https://api.club-os.io/users/{user_id}/permissions?onlyAllow=true"
        
        permissions_headers = {
            'Authorization': f'Bearer {api_v3_access_token}',
            'id-token': api_v3_id_token,
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://anytime.club-os.com',
            'Referer': 'https://anytime.club-os.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
        }
        
        print(f"📞 Calling permissions API: {permissions_url}")
        permissions_response = session.get(permissions_url, headers=permissions_headers)
        
        print(f"📊 Permissions Status: {permissions_response.status_code}")
        
        if permissions_response.status_code == 200:
            try:
                permissions_data = permissions_response.json()
                print(f"✅ Permissions loaded successfully")
                
                # Look for agreement-related permissions
                agreement_permissions = []
                for perm in permissions_data:
                    if isinstance(perm, dict) and 'name' in perm:
                        perm_name = perm['name'].lower()
                        if 'agreement' in perm_name or 'package' in perm_name or 'billing' in perm_name:
                            agreement_permissions.append(perm)
                
                print(f"🔐 Found {len(agreement_permissions)} agreement-related permissions:")
                for perm in agreement_permissions[:5]:  # Show first 5
                    print(f"   - {perm.get('name', 'Unknown')}: {perm.get('allowed', 'Unknown')}")
                
                # Save full permissions for analysis
                with open('user_permissions.json', 'w') as f:
                    json.dump(permissions_data, f, indent=2)
                print(f"💾 Saved full permissions to 'user_permissions.json'")
                
            except Exception as e:
                print(f"❌ Error parsing permissions: {e}")
                print(f"Raw response: {permissions_response.text[:500]}")
        else:
            print(f"❌ Permissions check failed: {permissions_response.text[:200]}")
    
    # Step 5: Navigate to ClubServices to establish proper context
    print("\n🏪 Step 5: Navigating to ClubServices page...")
    
    clubservices_url = "https://anytime.club-os.com/action/ClubServicesNew"
    clubservices_response = session.get(clubservices_url)
    
    print(f"📊 ClubServices Status: {clubservices_response.status_code}")
    
    if clubservices_response.status_code == 200:
        print("✅ ClubServices navigation successful")
    else:
        print(f"⚠️ ClubServices navigation failed, but continuing...")
    
    # Step 6: Try the package agreements list API
    print("\n📋 Step 6: Testing package agreements list API...")
    
    list_url = "https://anytime.club-os.com/api/agreements/package_agreements/list"
    
    # Use the exact headers from your browser
    api_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Authorization': f'Bearer {api_v3_access_token}',
        'Priority': 'u=1, i',
        'Referer': 'https://anytime.club-os.com/action/ClubServicesNew',
        'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
        'X-Newrelic-Id': 'VgYBWFdXCRABVVFTBgUBVVQJ'
    }
    
    print(f"📞 Calling list API: {list_url}")
    list_response = session.get(list_url, headers=api_headers)
    
    print(f"📊 List API Status: {list_response.status_code}")
    print(f"📏 Content-Length: {len(list_response.content)} bytes")
    
    if list_response.status_code == 200:
        try:
            list_data = list_response.json()
            print(f"✅ Package agreements list loaded successfully!")
            print(f"📊 Found {len(list_data)} package agreements")
            
            # Show summary of each agreement
            for i, agreement in enumerate(list_data[:5]):  # Show first 5
                if isinstance(agreement, dict):
                    agreement_id = agreement.get('id', 'Unknown')
                    member_name = agreement.get('memberName', 'Unknown')
                    package_name = agreement.get('packageName', 'Unknown')
                    status = agreement.get('status', 'Unknown')
                    
                    print(f"   {i+1}. ID: {agreement_id}, Member: {member_name}, Package: {package_name}, Status: {status}")
            
            # Save full list for analysis
            with open('package_agreements_list.json', 'w') as f:
                json.dump(list_data, f, indent=2)
            print(f"💾 Saved full agreements list to 'package_agreements_list.json'")
            
            # Test detailed agreement API with first agreement
            if list_data and len(list_data) > 0:
                first_agreement = list_data[0]
                if isinstance(first_agreement, dict) and 'id' in first_agreement:
                    agreement_id = first_agreement['id']
                    
                    print(f"\n🔍 Step 7: Testing detailed agreement API for ID {agreement_id}...")
                    
                    # Test the detailed endpoints
                    detail_endpoints = [
                        f"https://anytime.club-os.com/api/agreements/package_agreements/{agreement_id}/billing_status",
                        f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes",
                        f"https://anytime.club-os.com/api/agreements/package_agreements/agreementTotalValue?agreementId={agreement_id}"
                    ]
                    
                    for endpoint in detail_endpoints:
                        endpoint_name = endpoint.split('/')[-1].split('?')[0]
                        print(f"\n📞 Testing {endpoint_name}: {endpoint}")
                        
                        detail_response = session.get(endpoint, headers=api_headers)
                        print(f"   📊 Status: {detail_response.status_code}")
                        
                        if detail_response.status_code == 200:
                            try:
                                detail_data = detail_response.json()
                                print(f"   ✅ Success! Data keys: {list(detail_data.keys()) if isinstance(detail_data, dict) else 'Not a dict'}")
                                
                                # Save the detailed data
                                filename = f"agreement_{agreement_id}_{endpoint_name}.json"
                                with open(filename, 'w') as f:
                                    json.dump(detail_data, f, indent=2)
                                print(f"   💾 Saved to {filename}")
                                
                            except Exception as e:
                                print(f"   📄 Text response: {detail_response.text[:200]}")
                        else:
                            print(f"   ❌ Error: {detail_response.text[:200]}")
            
        except Exception as e:
            print(f"❌ Error parsing list response: {e}")
            print(f"Raw response: {list_response.text[:500]}")
    else:
        print(f"❌ List API failed: {list_response.text[:200]}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   If the list API worked, we now have the complete flow!")
    print(f"   1. Login → 2. Dashboard → 3. Get tokens → 4. Check permissions → 5. ClubServices → 6. List agreements → 7. Get details")

if __name__ == "__main__":
    test_complete_clubos_flow()
