#!/usr/bin/env python3
"""
Test the complete ClubOS delegation and package agreements flow
"""

import sys
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_complete_delegation_flow():
    """Test the complete flow: Login -> Delegate -> Get Package Agreements"""
    
    print("🧪 Testing complete ClubOS delegation and package agreements flow...")
    
    # Set up session
    session = requests.Session()
    
    # 1. Login to ClubOS
    print("\n1️⃣ STEP 1: Login to ClubOS")
    login_url = "https://anytime.club-os.com/action/Login"
    login_data = {
        'email': CLUBOS_USERNAME,
        'password': CLUBOS_PASSWORD
    }
    
    login_response = session.post(login_url, data=login_data)
    print(f"   📊 Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        return
    
    print("   ✅ Login successful")
    
    # 2. Navigate to Dashboard to get API tokens
    print("\n2️⃣ STEP 2: Navigate to Dashboard for API tokens")
    dashboard_url = "https://anytime.club-os.com/action/Dashboard/view"
    dashboard_response = session.get(dashboard_url)
    print(f"   📊 Dashboard Status: {dashboard_response.status_code}")
    
    # Check for apiV3AccessToken cookie
    api_token = None
    for cookie in session.cookies:
        if cookie.name == 'apiV3AccessToken':
            api_token = cookie.value
            print(f"   🔑 Found API Token: {api_token[:50]}...")
            break
    
    if not api_token:
        print("   ⚠️ No API token found in cookies, checking other methods...")
        # Try to extract from page content
        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'apiV3AccessToken' in script.string:
                token_match = re.search(r'apiV3AccessToken["\']:\s*["\']([^"\']+)["\']', script.string)
                if token_match:
                    api_token = token_match.group(1)
                    print(f"   🔑 Found API Token in script: {api_token[:50]}...")
                    break
    
    # 3. Delegate to Mark Benzinger (who has package agreements)
    print("\n3️⃣ STEP 3: Delegate to Mark Benzinger (125814462)")
    mark_id = "125814462"
    delegate_url = f"https://anytime.club-os.com/action/Delegate/{mark_id}/url=false?_={int(time.time() * 1000)}"
    
    delegate_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://anytime.club-os.com/action/ClubServicesNew'
    }
    
    if api_token:
        delegate_headers['Authorization'] = f'Bearer {api_token}'
    
    delegate_response = session.get(delegate_url, headers=delegate_headers)
    print(f"   📊 Delegation Status: {delegate_response.status_code}")
    
    if delegate_response.status_code == 200:
        print("   ✅ Successfully delegated to Mark Benzinger")
        
        # Check if delegation cookies were set
        delegated_user_id = None
        for cookie in session.cookies:
            if cookie.name == 'delegatedUserId':
                delegated_user_id = cookie.value
                print(f"   👤 Delegated User ID: {delegated_user_id}")
                break
        
        if delegated_user_id != mark_id:
            print(f"   ⚠️ Warning: Expected delegation to {mark_id}, but got {delegated_user_id}")
    else:
        print(f"   ❌ Delegation failed: {delegate_response.status_code}")
        print(f"   Response: {delegate_response.text[:200]}")
        return
    
    # 4. Get Package Agreements List 
    print("\n4️⃣ STEP 4: Get Package Agreements List")
    agreements_list_url = f"https://anytime.club-os.com/api/agreements/package_agreements/list?_={int(time.time() * 1000)}"
    
    api_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://anytime.club-os.com/action/ClubServicesNew',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }
    
    if api_token:
        api_headers['Authorization'] = f'Bearer {api_token}'
    
    list_response = session.get(agreements_list_url, headers=api_headers)
    print(f"   📊 Agreements List Status: {list_response.status_code}")
    print(f"   📏 Content-Length: {len(list_response.content)} bytes")
    
    if list_response.status_code == 200:
        try:
            agreements_data = list_response.json()
            print(f"   ✅ JSON Response Success!")
            print(f"   📋 Data Type: {type(agreements_data)}")
            
            if isinstance(agreements_data, list):
                print(f"   📊 Found {len(agreements_data)} package agreements")
                
                # Show details of each agreement
                for i, agreement in enumerate(agreements_data):
                    print(f"\n   📦 Agreement {i+1}:")
                    if isinstance(agreement, dict):
                        for key, value in agreement.items():
                            if key in ['id', 'agreementId', 'packageName', 'totalValue', 'remainingSessions', 'status']:
                                print(f"      {key}: {value}")
                    else:
                        print(f"      Data: {agreement}")
                
                # If we found agreements, test getting details for the first one
                if agreements_data and isinstance(agreements_data[0], dict) and 'id' in agreements_data[0]:
                    print("\n5️⃣ STEP 5: Get Detailed Agreement Data")
                    agreement_id = agreements_data[0]['id']
                    
                    # Test the detailed endpoints
                    test_detailed_agreement_apis(session, api_headers, agreement_id)
                
            elif isinstance(agreements_data, dict):
                print(f"   📋 Response Keys: {list(agreements_data.keys())}")
                print(f"   📄 Full Response: {json.dumps(agreements_data, indent=2)}")
            
        except Exception as e:
            print(f"   ❌ JSON Parse Error: {e}")
            print(f"   📄 Raw Response: {list_response.text[:500]}")
    else:
        print(f"   ❌ Failed to get agreements list: {list_response.status_code}")
        print(f"   📄 Error Response: {list_response.text[:300]}")

def test_detailed_agreement_apis(session, headers, agreement_id):
    """Test the detailed agreement API endpoints"""
    
    print(f"   🔍 Testing detailed APIs for agreement ID: {agreement_id}")
    
    # 1. Billing Status
    billing_url = f"https://anytime.club-os.com/api/agreements/package_agreements/{agreement_id}/billing_status?_={int(time.time() * 1000)}"
    billing_response = session.get(billing_url, headers=headers)
    print(f"      💳 Billing Status: {billing_response.status_code}")
    if billing_response.status_code == 200:
        try:
            billing_data = billing_response.json()
            print(f"         Data: {billing_data}")
        except:
            print(f"         Text: {billing_response.text[:200]}")
    
    # 2. Full Agreement Data
    full_url = f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={int(time.time() * 1000)}"
    full_response = session.get(full_url, headers=headers)
    print(f"      📄 Full Agreement: {full_response.status_code}")
    if full_response.status_code == 200:
        try:
            full_data = full_response.json()
            print(f"         Keys: {list(full_data.keys()) if isinstance(full_data, dict) else 'Not dict'}")
            if isinstance(full_data, dict):
                key_fields = ['packageName', 'totalValue', 'remainingSessions', 'status', 'startDate', 'endDate']
                for field in key_fields:
                    if field in full_data:
                        print(f"         {field}: {full_data[field]}")
        except:
            print(f"         Text: {full_response.text[:200]}")
    
    # 3. Agreement Total Value
    total_url = f"https://anytime.club-os.com/api/agreements/package_agreements/agreementTotalValue?agreementId={agreement_id}&_={int(time.time() * 1000)}"
    total_response = session.get(total_url, headers=headers)
    print(f"      💰 Total Value: {total_response.status_code}")
    if total_response.status_code == 200:
        try:
            total_data = total_response.json()
            print(f"         Value: {total_data}")
        except:
            print(f"         Text: {total_response.text[:100]}")
    
    print(f"\n   🎯 SUCCESS! We can now get complete package agreement data!")

if __name__ == "__main__":
    test_complete_delegation_flow()

def test_complete_delegation_flow():
    """Parse the actual agreement document HTML for billing/payment info"""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    agreement_data = {}
    
    print("🔍 Parsing agreement document HTML...")
    
    # Look for contract/package information
    # Try to find package name/type
    package_elements = soup.find_all(['h1', 'h2', 'h3', 'div'], text=re.compile(r'(package|training|session|PT)', re.I))
    if package_elements:
        print(f"📦 Found {len(package_elements)} package-related elements")
        for elem in package_elements[:3]:  # Show first 3
            print(f"   - {elem.get_text().strip()}")
    
    # Look for pricing/billing information
    price_patterns = [
        r'\$\d+\.?\d*',  # Dollar amounts
        r'price.*?\$?\d+',  # Price followed by amount
        r'cost.*?\$?\d+',   # Cost followed by amount
        r'total.*?\$?\d+',  # Total followed by amount
        r'amount.*?\$?\d+'  # Amount followed by amount
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, html_content, re.I)
        if matches:
            print(f"💰 Found pricing pattern '{pattern}': {matches[:5]}")  # Show first 5
    
    # Look for session information
    session_patterns = [
        r'(\d+)\s*session[s]?',
        r'session[s]?\s*(\d+)',
        r'(\d+)\s*visit[s]?',
        r'remaining.*?(\d+)',
        r'used.*?(\d+)'
    ]
    
    for pattern in session_patterns:
        matches = re.findall(pattern, html_content, re.I)
        if matches:
            print(f"🏋️ Found session pattern '{pattern}': {matches[:5]}")  # Show first 5
    
    # Look for dates (start, end, expiration)
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or MM-DD-YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD or YYYY-MM-DD
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'  # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, html_content, re.I)
        if matches:
            print(f"📅 Found date pattern '{pattern}': {matches[:5]}")  # Show first 5
    
    # Look for specific divs or sections that might contain structured data
    print("\n🔍 Looking for structured data sections...")
    
    # Check for forms or input fields
    forms = soup.find_all('form')
    if forms:
        print(f"📝 Found {len(forms)} forms")
        for i, form in enumerate(forms[:2]):  # Check first 2 forms
            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"   Form {i+1}: {len(inputs)} input fields")
            for inp in inputs[:5]:  # Show first 5 inputs
                name = inp.get('name', '')
                value = inp.get('value', '')
                if name:
                    print(f"     - {name}: {value}")
    
    # Look for divs with specific classes that might contain billing info
    billing_classes = ['billing', 'payment', 'price', 'cost', 'total', 'amount', 'package', 'session']
    for cls in billing_classes:
        elements = soup.find_all('div', class_=re.compile(cls, re.I))
        if elements:
            print(f"� Found {len(elements)} elements with class containing '{cls}'")
            for elem in elements[:2]:  # Show first 2
                text = elem.get_text().strip()[:100]  # First 100 chars
                if text:
                    print(f"     - {text}")
    
    return agreement_data

def test_real_api_endpoints():
    """Test the REAL ClubOS API endpoints that you found in the browser"""
    
    print("🧪 Testing REAL ClubOS API endpoints from browser inspection...")
    
    # Set up session
    session = requests.Session()
    
    # Login to ClubOS
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
    
    # First navigate to the SPA page to establish proper context (like in browser)
    spa_url = "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/"
    print(f"🔄 Navigating to SPA page: {spa_url}")
    
    spa_response = session.get(spa_url)
    print(f"📊 SPA page response: {spa_response.status_code}")
    
    if spa_response.status_code != 200:
        print(f"❌ Failed to access SPA page: {spa_response.status_code}")
        return
    
    # Extract Bearer token from response if available
    bearer_token = None
    
    # Look for JWT token in page content or cookies
    soup = BeautifulSoup(spa_response.text, 'html.parser')
    
    # Check for token in script tags
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'eyJ' in script.string:  # JWT tokens start with eyJ
            # Look for bearer token pattern
            token_match = re.search(r'Bearer\s+([A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]*)', script.string)
            if token_match:
                bearer_token = token_match.group(1)
                break
            
            # Look for just JWT pattern
            jwt_match = re.search(r'eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]*', script.string)
            if jwt_match:
                bearer_token = jwt_match.group(0)
                break
    
    if not bearer_token:
        print("⚠️ No Bearer token found in page, trying without it...")
    else:
        print(f"� Found Bearer token: {bearer_token[:50]}...")
    
    # Set up API headers (like the real browser requests)
    api_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }
    
    if bearer_token:
        api_headers['Authorization'] = f'Bearer {bearer_token}'
    
    # Test the specific agreement ID from your browser (1675003)
    agreement_id = "1675003"
    
    print(f"\n🧪 Testing API endpoints for agreement ID: {agreement_id}")
    print("="*70)
    
    # 1. Test billing status endpoint
    billing_url = f"https://anytime.club-os.com/api/agreements/package_agreements/{agreement_id}/billing_status?_={int(time.time() * 1000)}"
    print(f"\n1️⃣ Testing billing status: {billing_url}")
    
    billing_response = session.get(billing_url, headers=api_headers)
    print(f"   📊 Status: {billing_response.status_code}")
    print(f"   📏 Content-Length: {len(billing_response.content)} bytes")
    
    if billing_response.status_code == 200:
        try:
            billing_data = billing_response.json()
            print(f"   ✅ JSON Response: {billing_data}")
        except:
            print(f"   � Text Response: {billing_response.text}")
    else:
        print(f"   ❌ Error Response: {billing_response.text[:200]}")
    
    # 2. Test full agreement endpoint  
    agreement_url = f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={int(time.time() * 1000)}"
    print(f"\n2️⃣ Testing full agreement: {agreement_url}")
    
    agreement_response = session.get(agreement_url, headers=api_headers)
    print(f"   📊 Status: {agreement_response.status_code}")
    print(f"   📏 Content-Length: {len(agreement_response.content)} bytes")
    
    if agreement_response.status_code == 200:
        try:
            agreement_data = agreement_response.json()
            print(f"   ✅ JSON Response Keys: {list(agreement_data.keys()) if isinstance(agreement_data, dict) else 'Not a dict'}")
            
            # Show key data if available
            if isinstance(agreement_data, dict):
                if 'packageName' in agreement_data:
                    print(f"   📦 Package Name: {agreement_data['packageName']}")
                if 'totalValue' in agreement_data:
                    print(f"   💰 Total Value: {agreement_data['totalValue']}")
                if 'remainingSessions' in agreement_data:
                    print(f"   🏋️ Remaining Sessions: {agreement_data['remainingSessions']}")
                if 'invoices' in agreement_data:
                    print(f"   🧾 Invoices: {len(agreement_data['invoices'])} found")
                
                # Show a sample of the full data
                print(f"   📋 Full Response Sample: {str(agreement_data)[:500]}...")
                
        except Exception as e:
            print(f"   📄 Text Response: {agreement_response.text[:500]}")
            print(f"   ⚠️ JSON Parse Error: {e}")
    else:
        print(f"   ❌ Error Response: {agreement_response.text[:200]}")
    
    # 3. Test agreement total value endpoint
    total_url = f"https://anytime.club-os.com/api/agreements/package_agreements/agreementTotalValue?agreementId={agreement_id}&_={int(time.time() * 1000)}"
    print(f"\n3️⃣ Testing agreement total: {total_url}")
    
    total_response = session.get(total_url, headers=api_headers)
    print(f"   📊 Status: {total_response.status_code}")
    print(f"   📏 Content-Length: {len(total_response.content)} bytes")
    
    if total_response.status_code == 200:
        try:
            total_data = total_response.json()
            print(f"   ✅ JSON Response: {total_data}")
        except:
            print(f"   📄 Text Response: {total_response.text}")
    else:
        print(f"   ❌ Error Response: {total_response.text[:200]}")
    
    print("\n" + "="*70)
    print("🎯 SUMMARY: These are the REAL API endpoints we should use!")
    print("   Instead of parsing HTML, we can get clean JSON data!")
    
    # Now we need to figure out how to get agreement IDs for each member
    print("\n🔍 Next step: We need to find how to get agreement IDs for each member...")
    print("   Current challenge: We have member IDs (189425730) but need agreement IDs (1675003)")

import time

if __name__ == "__main__":
    test_real_api_endpoints()
