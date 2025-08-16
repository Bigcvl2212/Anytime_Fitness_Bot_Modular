#!/usr/bin/env python3
"""
Final attempt - use the existing working ClubOS auth from clubos_training_api.py and test agreement endpoints
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import requests
import json
import time

def test_with_existing_auth():
    """Use the existing working authentication to test agreement endpoints"""
    
    print("🧪 Testing agreement endpoints with existing working ClubOS auth...")
    
    # Use the existing working ClubOS API
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate using the existing working method
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authenticated successfully using existing method")
    
    # Check what tokens we have
    print(f"🔑 Access token: {api.access_token[:50] if api.access_token else 'None'}...")
    print(f"🔑 Session data keys: {list(api.session_data.keys())}")
    
    # Get the Bearer token
    bearer_token = api.access_token or api.session_data.get('apiV3AccessToken')
    
    if not bearer_token:
        print("❌ No Bearer token available")
        return
    
    print(f"🔑 Using Bearer token: {bearer_token[:50]}...")
    
    # Set up headers exactly like the working browser request
    headers = {
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
        'sec-fetch-site': 'same-origin',
        'priority': 'u=1, i'
    }
    
    # Navigate to ClubServicesNew first (as in browser)
    print("🔄 Navigating to ClubServicesNew...")
    clubservices_response = api.session.get("https://anytime.club-os.com/action/ClubServicesNew")
    print(f"📊 ClubServicesNew status: {clubservices_response.status_code}")
    
    # Now try the agreements list API
    list_url = "https://anytime.club-os.com/api/agreements/package_agreements/list"
    print(f"📋 Testing: {list_url}")
    
    response = api.session.get(list_url, headers=headers)
    print(f"📊 Status: {response.status_code}")
    print(f"📏 Content-Length: {len(response.content)} bytes")
    
    if response.status_code == 200:
        print("🎉 SUCCESS!")
        try:
            data = response.json()
            print(f"📋 Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"📊 Found {len(data)} agreements")
                
                for i, agreement in enumerate(data[:3]):  # Show first 3
                    print(f"\n📦 Agreement {i+1}:")
                    if isinstance(agreement, dict):
                        for key, value in agreement.items():
                            if len(str(value)) < 100:
                                print(f"   {key}: {value}")
                            else:
                                print(f"   {key}: {str(value)[:100]}... (truncated)")
            else:
                print(f"📄 Response: {data}")
            
            # Save the response
            with open('working_agreements_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Saved to 'working_agreements_response.json'")
            
        except Exception as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"📄 Raw response: {response.text[:500]}")
    
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"📄 Error response: {response.text[:300]}")
        
        # Debug: print all cookies and headers
        print(f"\n🍪 Current cookies:")
        for cookie in api.session.cookies:
            print(f"   {cookie.name}: {cookie.value[:50]}...")
        
        print(f"\n📋 Request headers sent:")
        for key, value in headers.items():
            if len(value) < 100:
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: {value[:50]}...")

if __name__ == "__main__":
    test_with_existing_auth()
