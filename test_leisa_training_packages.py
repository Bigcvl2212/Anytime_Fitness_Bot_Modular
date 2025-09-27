#!/usr/bin/env python3
"""
Test Training Package Pull for Leisa Morgan
Using discovered endpoints from Training_payments.har and working authentication from clubos_real_calendar_api.py
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

class ClubOSTrainingPackageTest:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.member_id = "53833814"  # Leisa Morgan's ProspectID
        self.authenticated = False
        self.session_data = {}
        self.access_token = None  # Add this for compatibility
        
        # Set default headers to mimic browser (EXACT pattern from clubos_api_client.py)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
    def authenticate(self):
        """Authenticate using the EXACT working pattern from clubos_api_client.py"""
        try:
            print("🔐 Attempting ClubOS web authentication using working HAR sequence...")
            
            # Step 1: Get login page and extract CSRF token (following working pattern)
            print("   📄 Fetching login page...")
            login_url = f"{self.base_url}/action/Login/view?__fsk=1221801756"
            login_response = self.session.get(login_url, timeout=30)
            
            if not login_response.ok:
                print(f"   ❌ Failed to load login page: {login_response.status_code}")
                return False
            
            # Extract required form fields using the working pattern
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            
            print("   ✅ Extracted form fields successfully")
            
            # Step 2: Submit login form with correct field names (working pattern)
            login_data = {
                'login': 'Submit',
                'username': 'j.mayo',
                'password': 'AnytimeFitness2020!',
                '_sourcePage': source_page.get('value') if source_page else '',
                '__fp': fp_token.get('value') if fp_token else ''
            }
            
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=login_headers,
                allow_redirects=True,
                timeout=30
            )
            
            # Step 3: Extract session information from cookies (working pattern)
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            api_v3_access_token = self.session.cookies.get('apiV3AccessToken')
            
            if not session_id:
                print("   ❌ Authentication failed - missing JSESSIONID")
                return False
            
            # Set the access token
            self.access_token = api_v3_access_token
            self.authenticated = True
            
            # Store session data
            self.session_data = {
                'loggedInUserId': logged_in_user_id,
                'delegatedUserId': delegated_user_id,
                'JSESSIONID': session_id,
                'apiV3AccessToken': api_v3_access_token
            }
            
            print(f"   ✅ Authentication successful - Session ID: {session_id[:20]}...")
            if logged_in_user_id:
                print(f"   👤 User ID: {logged_in_user_id}")
            if delegated_user_id:
                print(f"   🎭 Delegated User ID: {delegated_user_id}")
            if api_v3_access_token:
                print(f"   🔑 API V3 Access Token: {api_v3_access_token[:20]}...")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def get_member_agreements(self):
        """Get member's training package agreements"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
            
        print(f"\n📋 Fetching training agreements for member {self.member_id}...")
        
        # First, let's try to find the member's package agreements
        # We'll search for agreements associated with this member ID
        
        # The HAR file showed: /api/agreements/package_agreements/V2/{agreement_id}
        # But we need to find the agreement ID first
        
        # Try the general agreements endpoint
        agreements_url = f"{self.base_url}/api/agreements/package_agreements"
        
        headers = {
            'Authorization': f'Bearer {self.session_data["apiV3AccessToken"]}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        params = {
            'memberId': self.member_id,
            '_': int(datetime.now().timestamp() * 1000)
        }
        
        try:
            response = self.session.get(agreements_url, headers=headers, params=params)
            print(f"   📡 Request: GET {agreements_url}")
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if we're being redirected to login page
                if "action/Login" in response.url or "login" in response.text.lower():
                    print(f"   🚨 REDIRECTED TO LOGIN PAGE - Authentication failed!")
                    print(f"   📍 Final URL: {response.url}")
                    return "REDIRECTED_TO_LOGIN"
                else:
                    agreements = response.json()
                    print(f"   ✅ Found {len(agreements) if isinstance(agreements, list) else 'some'} agreements")
                    return agreements
            else:
                print(f"   ❌ Failed to get agreements: {response.status_code}")
                if response.status_code == 401:
                    print(f"   🚨 401 Unauthorized - Check authentication!")
                print(f"   📍 Response URL: {response.url}")
                print(f"   📄 Response: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching agreements: {e}")
            return None
    
    def get_member_training_packages(self):
        """Try alternative endpoints to find training packages"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
            
        print(f"\n🏋️ Searching for training packages for member {self.member_id}...")
        
        headers = {
            'Authorization': f'Bearer {self.session_data["apiV3AccessToken"]}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Try different endpoints that might contain training package info
        endpoints_to_try = [
            f"/api/members/{self.member_id}/agreements",
            f"/api/members/{self.member_id}/packages",
            f"/api/members/{self.member_id}/training",
            f"/api/staff/{self.session_data['loggedInUserId']}/members/{self.member_id}",
            f"/api/agreements/package_agreements/agreementTotalValue?memberId={self.member_id}",
            f"/api/member_payment_profiles?memberId={self.member_id}"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_try:
            try:
                url = f"{self.base_url}{endpoint}"
                params = {'_': int(datetime.now().timestamp() * 1000)}
                
                response = self.session.get(url, headers=headers, params=params)
                print(f"   📡 Trying: {endpoint}")
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                # Check if we're being redirected to login page
                if "action/Login" in response.url or "login" in response.text.lower():
                    print(f"   🚨 REDIRECTED TO LOGIN PAGE - Authentication failed!")
                    print(f"   📍 Final URL: {response.url}")
                    results[endpoint] = "REDIRECTED_TO_LOGIN"
                else:
                    try:
                        data = response.json()
                        results[endpoint] = data
                        print(f"   ✅ Success - Got data: {str(data)[:100]}...")
                    except:
                        results[endpoint] = response.text
                        print(f"   ✅ Success - Got text: {response.text[:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                if response.status_code == 401:
                    print(f"   🚨 401 Unauthorized - Check authentication!")
                print(f"   📍 Response URL: {response.url}")
                print(f"   📄 Response snippet: {response.text[:200]}...")            except Exception as e:
                print(f"   ❌ Error with {endpoint}: {e}")
        
        return results
    
    def search_for_agreement_id(self):
        """Search for Leisa's specific agreement ID"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
            
        print(f"\n🔍 Searching for Leisa's agreement ID...")
        
        # From the HAR file, we saw agreement ID 1616463 was used
        # Let's try some common patterns to find her agreement
        
        headers = {
            'Authorization': f'Bearer {self.session_data["apiV3AccessToken"]}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Try the specific agreement from HAR file as a test
        test_agreement_id = "1616463"
        
        endpoints_with_agreement = [
            f"/api/agreements/package_agreements/V2/{test_agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes",
            f"/api/agreements/package_agreements/{test_agreement_id}/billing_status",
            f"/api/agreements/package_agreements/{test_agreement_id}/salespeople"
        ]
        
        results = {}
        
        for endpoint in endpoints_with_agreement:
            try:
                url = f"{self.base_url}{endpoint}"
                params = {'_': int(datetime.now().timestamp() * 1000)}
                
                response = self.session.get(url, headers=headers, params=params)
                print(f"   📡 Testing: {endpoint}")
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Check if we're being redirected to login page
                    if "action/Login" in response.url or "login" in response.text.lower():
                        print(f"   🚨 REDIRECTED TO LOGIN PAGE - Authentication failed!")
                        print(f"   📍 Final URL: {response.url}")
                        results[endpoint] = "REDIRECTED_TO_LOGIN"
                    else:
                        try:
                            data = response.json()
                            results[endpoint] = data
                            print(f"   ✅ Success - Got agreement data")
                        except:
                            results[endpoint] = response.text
                            print(f"   ✅ Success - Got text response")
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    if response.status_code == 401:
                        print(f"   🚨 401 Unauthorized - Check authentication!")
                    print(f"   📍 Response URL: {response.url}")
                    print(f"   📄 Response snippet: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error with {endpoint}: {e}")
        
        return results

def main():
    print("🏋️ ClubOS Training Package Test - Leisa Morgan")
    print("=" * 50)
    
    tester = ClubOSTrainingPackageTest()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed, cannot proceed")
        return
    
    # Step 2: Try to get member agreements
    agreements = tester.get_member_agreements()
    if agreements:
        print(f"\n📋 Agreements found:")
        print(json.dumps(agreements, indent=2))
    
    # Step 3: Try alternative training package endpoints
    training_data = tester.get_member_training_packages()
    if training_data:
        print(f"\n🏋️ Training package search results:")
        for endpoint, data in training_data.items():
            print(f"\n{endpoint}:")
            if isinstance(data, dict) or isinstance(data, list):
                print(json.dumps(data, indent=2)[:500] + "..." if len(str(data)) > 500 else json.dumps(data, indent=2))
            else:
                print(str(data)[:500] + "..." if len(str(data)) > 500 else str(data))
    
    # Step 4: Test specific agreement endpoints
    agreement_data = tester.search_for_agreement_id()
    if agreement_data:
        print(f"\n📄 Agreement endpoint test results:")
        for endpoint, data in agreement_data.items():
            print(f"\n{endpoint}:")
            if isinstance(data, dict) or isinstance(data, list):
                print(json.dumps(data, indent=2)[:500] + "..." if len(str(data)) > 500 else json.dumps(data, indent=2))
            else:
                print(str(data)[:500] + "..." if len(str(data)) > 500 else str(data))

if __name__ == "__main__":
    main()
