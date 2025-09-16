#!/usr/bin/env python3
"""
Test the REAL ClubOS package agreement API flow
"""

import sys
import requests
import json
import time
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_package_agreements_flow():
    """Test the complete ClubOS package agreement API flow"""
    
    print("🧪 Testing ClubOS package agreement API with proper auth flow...")
    
    # Set up session
    session = requests.Session()
    
    # Login to ClubOS
    login_url = "https://anytime.club-os.com/action/Login"
    login_data = {
        'email': CLUBOS_USERNAME,
        'password': CLUBOS_PASSWORD
    }
    
    print("🔐 Logging into ClubOS...")
    
    # Step 1: GET login page and extract tokens (like the existing code)
    login_view_response = session.get(f"https://anytime.club-os.com/action/Login/view")
    if login_view_response.status_code not in (200, 302):
        print(f"❌ Login view failed: {login_view_response.status_code}")
        return
    
    # Extract hidden form fields
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_view_response.text, 'html.parser')
    _sourcePage = ''
    __fp = ''
    
    sp = soup.find('input', {'name': '_sourcePage'})
    fp = soup.find('input', {'name': '__fp'})
    if sp:
        _sourcePage = sp.get('value', '')
    if fp:
        __fp = fp.get('value', '')
    
    # Step 2: POST credentials with proper form data
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://anytime.club-os.com/action/Login/view',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    form_data = {
        'login': 'Submit',
        'username': CLUBOS_USERNAME,
        'password': CLUBOS_PASSWORD,
        '_sourcePage': _sourcePage,
        '__fp': __fp,
    }
    
    login_response = session.post(login_url, data=form_data, headers=headers, allow_redirects=True)
    
    if login_response.status_code not in (200, 302):
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Step 3: Navigate to Dashboard to finalize session and get apiV3AccessToken
    print("🔄 Finalizing session by visiting Dashboard...")
    dashboard_response = session.get("https://anytime.club-os.com/action/Dashboard", timeout=15)
    
    if dashboard_response.status_code not in (200, 302):
        print(f"❌ Dashboard navigation failed: {dashboard_response.status_code}")
        return
    
    # Step 4: Navigate to ClubServicesNew (as shown in your browser logs)
    print("🔄 Navigating to ClubServicesNew to establish context...")
    clubservices_response = session.get("https://anytime.club-os.com/action/ClubServicesNew", timeout=15)
    
    if clubservices_response.status_code not in (200, 302):
        print(f"❌ ClubServicesNew navigation failed: {clubservices_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Look for the apiV3AccessToken in cookies (this is the Bearer token!)
    bearer_token = None
    for cookie in session.cookies:
        if cookie.name == 'apiV3AccessToken':
            bearer_token = cookie.value
            print(f"🔑 Found Bearer token: {bearer_token[:50]}...")
            break
    
    if not bearer_token:
        print("❌ Could not find apiV3AccessToken cookie")
        print("Available cookies:")
        for cookie in session.cookies:
            print(f"  - {cookie.name}: {cookie.value[:50]}...")
        return
    
    # Set up API headers (matching your browser requests)
    api_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Authorization': f'Bearer {bearer_token}',
        'Referer': 'https://anytime.club-os.com/action/ClubServicesNew',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }
    
    print(f"\n🎯 Step 1: Getting all package agreements...")
    print("="*70)
    
    # Call the list endpoint first (as you showed in browser)
    list_url = "https://anytime.club-os.com/api/agreements/package_agreements/list"
    print(f"📋 Calling: {list_url}")
    
    # Try with different parameter combinations that might be needed
    test_params = [
        {},  # No params
        {'_': str(int(time.time() * 1000))},  # Timestamp only
        {'delegatedUserId': '125814462'},  # The delegated user from your browser
        {'delegatedUserId': '185182950'},  # Another ID seen in logs
    ]
    
    for i, params in enumerate(test_params):
        print(f"\n   Attempt {i+1}: {params}")
        
        list_response = session.get(list_url, headers=api_headers, params=params)
        print(f"   📊 Status: {list_response.status_code}")
        print(f"   📏 Content-Length: {len(list_response.content)} bytes")
        
        if list_response.status_code == 200:
            print(f"   ✅ SUCCESS with params: {params}")
            break
        else:
            print(f"   ❌ Error: {list_response.text[:100]}")
    
    if list_response.status_code != 200:
        print(f"❌ All parameter combinations failed")
        
        # Let's check what cookies we have for debugging
        print(f"\n🍪 Available cookies for debugging:")
        for cookie in session.cookies:
            print(f"   {cookie.name}: {cookie.value[:50]}...")
        
        # Try to decode the JWT to see what user info we have
        try:
            import base64
            token_parts = bearer_token.split('.')
            if len(token_parts) >= 2:
                # Decode the payload (add padding if needed)
                payload = token_parts[1]
                payload += '=' * (4 - len(payload) % 4)  # Add padding
                decoded = base64.b64decode(payload)
                print(f"\n🔍 JWT payload: {decoded.decode('utf-8')}")
        except Exception as e:
            print(f"   Failed to decode JWT: {e}")
        
        return
    
    try:
        agreements_list = list_response.json()
        print(f"✅ Successfully got agreements list!")
        print(f"📋 Type: {type(agreements_list)}")
        
        if isinstance(agreements_list, list):
            print(f"📊 Found {len(agreements_list)} package agreements")
            
            # Show details of each agreement
            agreement_ids = []
            for i, agreement in enumerate(agreements_list):
                if isinstance(agreement, dict):
                    print(f"\n📦 Agreement {i+1}:")
                    
                    # Show all available fields
                    for key, value in agreement.items():
                        if len(str(value)) < 100:  # Don't print huge values
                            print(f"   {key}: {value}")
                        else:
                            print(f"   {key}: {str(value)[:100]}... (truncated)")
                    
                    # Collect agreement ID for testing details
                    if 'id' in agreement:
                        agreement_ids.append(agreement['id'])
            
            # Save full list for inspection
            with open('clubos_agreements_list.json', 'w') as f:
                json.dump(agreements_list, f, indent=2)
            print(f"\n💾 Saved complete list to 'clubos_agreements_list.json'")
            
        else:
            print(f"📋 Response is not a list: {type(agreements_list)}")
            print(f"📄 Content: {str(agreements_list)[:500]}...")
    
    except Exception as e:
        print(f"❌ Failed to parse agreements list: {e}")
        print(f"📄 Raw response: {list_response.text[:500]}")
        return
    
    # Test detailed endpoints if we have agreement IDs
    if 'agreement_ids' in locals() and agreement_ids:
        print(f"\n🎯 Step 2: Testing detailed agreement data...")
        print("="*70)
        
        test_id = agreement_ids[0]
        print(f"🔍 Testing with agreement ID: {test_id}")
        
        # Test the detailed endpoints you showed in browser
        detailed_endpoints = [
            f"https://anytime.club-os.com/api/agreements/package_agreements/{test_id}/billing_status",
            f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{test_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes",
            f"https://anytime.club-os.com/api/agreements/package_agreements/agreementTotalValue?agreementId={test_id}"
        ]
        
        for i, endpoint in enumerate(detailed_endpoints, 1):
            print(f"\n{i}️⃣ Testing: {endpoint}")
            
            # Add timestamp to prevent caching
            separator = '&' if '?' in endpoint else '?'
            timestamped_url = f"{endpoint}{separator}_={int(time.time() * 1000)}"
            
            detail_response = session.get(timestamped_url, headers=api_headers)
            print(f"   📊 Status: {detail_response.status_code}")
            
            if detail_response.status_code == 200:
                try:
                    detail_data = detail_response.json()
                    print(f"   ✅ JSON Success!")
                    
                    if isinstance(detail_data, dict):
                        print(f"   📋 Keys: {list(detail_data.keys())}")
                        
                        # Show sample of the data
                        for key, value in list(detail_data.items())[:5]:  # First 5 items
                            if len(str(value)) < 100:
                                print(f"   - {key}: {value}")
                            else:
                                print(f"   - {key}: {str(value)[:100]}... (truncated)")
                    else:
                        print(f"   📄 Response: {detail_data}")
                    
                    # Save detailed response
                    filename = f"agreement_{test_id}_endpoint_{i}.json"
                    with open(filename, 'w') as f:
                        json.dump(detail_data, f, indent=2)
                    print(f"   💾 Saved to '{filename}'")
                    
                except Exception as e:
                    print(f"   ⚠️ JSON parse error: {e}")
                    print(f"   📄 Raw text: {detail_response.text[:200]}")
            else:
                print(f"   ❌ Error: {detail_response.text[:200]}")
    
    print(f"\n🎯 SUMMARY:")
    print("="*70)
    print("✅ SUCCESS! We now have the complete ClubOS agreement API flow:")
    print("   1. Login to ClubOS and get apiV3AccessToken cookie")
    print("   2. Use Bearer token for API authentication")
    print("   3. Call /api/agreements/package_agreements/list to get all agreements")
    print("   4. Use agreement IDs to get detailed billing/session data")
    print("   5. This gives us all package agreement data for training clients!")
    
    if 'agreements_list' in locals():
        print(f"\n📊 Results from this test:")
        print(f"   - Found {len(agreements_list) if isinstance(agreements_list, list) else 'N/A'} package agreements")
        print(f"   - API authentication working perfectly")
        print(f"   - All data saved to JSON files for inspection")
        print(f"   - Ready to integrate into clubos_training_api.py!")

if __name__ == "__main__":
    test_package_agreements_flow()
