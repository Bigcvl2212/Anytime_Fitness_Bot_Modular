#!/usr/bin/env python3
"""
Test ClubOS API authentication methods
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
import time
from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_api_auth_methods():
    """Try different ways to authenticate with ClubOS APIs"""
    
    print("🧪 Testing ClubOS API authentication methods...")
    
    # Set up session
    session = requests.Session()
    
    # Login to ClubOS first
    login_url = "https://anytime.club-os.com/action/Login"
    login_data = {
        'email': CLUBOS_USERNAME,
        'password': CLUBOS_PASSWORD
    }
    
    print("🔐 Logging into ClubOS...")
    login_response = session.post(login_url, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Print all cookies to see what we have
    print(f"\n🍪 Session cookies after login:")
    for cookie in session.cookies:
        if len(cookie.value) < 100:  # Don't print huge tokens
            print(f"   {cookie.name}: {cookie.value}")
        else:
            print(f"   {cookie.name}: {cookie.value[:50]}... (length: {len(cookie.value)})")
    
    # Look for potential bearer tokens in cookies
    potential_tokens = []
    for cookie in session.cookies:
        if 'token' in cookie.name.lower() or 'jwt' in cookie.name.lower() or 'auth' in cookie.name.lower():
            potential_tokens.append((cookie.name, cookie.value))
        elif cookie.value.startswith('eyJ'):  # JWT tokens start with eyJ
            potential_tokens.append((cookie.name, cookie.value))
    
    print(f"\n🔑 Potential auth tokens found: {len(potential_tokens)}")
    for name, value in potential_tokens:
        print(f"   {name}: {value[:50]}...")
    
    # Try to access one of the simpler API endpoints with different auth methods
    agreement_id = "1675003"
    test_url = f"https://anytime.club-os.com/api/agreements/package_agreements/{agreement_id}/billing_status"
    
    print(f"\n🧪 Testing API access with different auth methods...")
    print(f"Target URL: {test_url}")
    
    # Method 1: Session cookies only (no extra headers)
    print(f"\n1️⃣ Method 1: Session cookies only")
    response1 = session.get(test_url)
    print(f"   Status: {response1.status_code}")
    print(f"   Response: {response1.text[:200]}")
    
    # Method 2: Add referer header
    print(f"\n2️⃣ Method 2: Session cookies + Referer header")
    headers_with_referer = {
        'Referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/'
    }
    response2 = session.get(test_url, headers=headers_with_referer)
    print(f"   Status: {response2.status_code}")
    print(f"   Response: {response2.text[:200]}")
    
    # Method 3: Add X-Requested-With (AJAX style)
    print(f"\n3️⃣ Method 3: Session cookies + AJAX headers")
    ajax_headers = {
        'Referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*'
    }
    response3 = session.get(test_url, headers=ajax_headers)
    print(f"   Status: {response3.status_code}")
    print(f"   Response: {response3.text[:200]}")
    
    # Method 4: Try with potential bearer tokens
    for name, token in potential_tokens:
        print(f"\n4️⃣ Method 4: Using token from '{name}' as Bearer")
        bearer_headers = {
            'Authorization': f'Bearer {token}',
            'Referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': '*/*'
        }
        response4 = session.get(test_url, headers=bearer_headers)
        print(f"   Status: {response4.status_code}")
        print(f"   Response: {response4.text[:200]}")
        
        if response4.status_code == 200:
            print(f"   ✅ SUCCESS! Token '{name}' works!")
            
            # Try to parse the response
            try:
                data = response4.json()
                print(f"   📋 JSON Data: {data}")
                return True, token, name
            except:
                print(f"   📄 Text Data: {response4.text}")
                return True, token, name
    
    # Method 5: Check if we need to visit a specific page first to get a fresh token
    print(f"\n5️⃣ Method 5: Get fresh token from SPA page")
    
    spa_url = "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    spa_response = session.get(spa_url)
    
    if spa_response.status_code == 200:
        # Look for tokens in the SPA page
        soup = BeautifulSoup(spa_response.text, 'html.parser')
        
        # Check all script tags for tokens
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            if script.string and ('token' in script.string.lower() or 'eyJ' in script.string):
                print(f"   📄 Script {i+1} contains token-related content:")
                
                # Look for JWT patterns
                jwt_matches = re.findall(r'eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]*', script.string)
                for j, jwt in enumerate(jwt_matches):
                    print(f"      JWT {j+1}: {jwt[:50]}...")
                    
                    # Test this JWT as bearer token
                    bearer_headers = {
                        'Authorization': f'Bearer {jwt}',
                        'Referer': spa_url,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': '*/*'
                    }
                    test_response = session.get(test_url, headers=bearer_headers)
                    print(f"      Test Status: {test_response.status_code}")
                    
                    if test_response.status_code == 200:
                        print(f"      ✅ SUCCESS! JWT from script works!")
                        try:
                            data = test_response.json()
                            print(f"      📋 JSON Data: {data}")
                            return True, jwt, f"script_{i+1}_jwt_{j+1}"
                        except:
                            print(f"      📄 Text Data: {test_response.text}")
                            return True, jwt, f"script_{i+1}_jwt_{j+1}"
    
    print(f"\n❌ None of the authentication methods worked")
    print(f"   We may need to investigate the exact browser flow further")
    return False, None, None

if __name__ == "__main__":
    success, token, source = test_api_auth_methods()
    
    if success:
        print(f"\n🎯 SOLUTION FOUND!")
        print(f"   Token Source: {source}")
        print(f"   Token: {token[:50]}...")
        print(f"   We can now use this for all API calls!")
    else:
        print(f"\n🔍 NEXT STEPS:")
        print(f"   1. We need to examine the exact browser network flow")
        print(f"   2. Look for any special authentication endpoints") 
        print(f"   3. Check if there's a specific API login endpoint")
