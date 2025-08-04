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
        self.access_token = None
        
        # Set EXACT headers to mimic WORKING browser (User ID 187032782)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
    def authenticate(self):
        """Authenticate using EXACT sequence from Training_payments.har"""
        try:
            print("🔐 Attempting ClubOS authentication using EXACT HAR sequence...")
            
            # Step 1: GET login page (use dynamic fsk value)
            print("   📄 Fetching login page...")
            login_get_url = f"{self.base_url}/action/Login/view"
            
            # Set EXACT headers from WORKING HAR sequence (User ID 187032782)
            get_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'DNT': '1',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            login_response = self.session.get(login_get_url, headers=get_headers, timeout=30)
            
            if not login_response.ok:
                print(f"   ❌ Failed to load login page: {login_response.status_code}")
                return False
            
            # Extract form fields dynamically from the actual page
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Find the login form
            login_form = soup.find('form')
            if not login_form:
                print("   ❌ No login form found!")
                return False
            
            # Extract ALL hidden fields from the form
            hidden_inputs = login_form.find_all('input', type='hidden')
            form_data = {}
            
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
                    print(f"   🔑 Found hidden field {name}: {value[:20]}..." if len(value) > 20 else f"   🔑 Found hidden field {name}: {value}")
            
            # Make sure we have the required tokens
            if '_sourcePage' not in form_data or '__fp' not in form_data:
                print("   ❌ Missing required CSRF tokens!")
                print("   � Available form fields:", list(form_data.keys()))
                return False
            
            # Step 2: POST login with dynamically extracted CSRF tokens
            login_data = {
                'login': 'Submit',
                'username': 'j.mayo', 
                'password': 'j@SD4fjhANK5WNA',
                '_sourcePage': form_data['_sourcePage'],
                '__fp': form_data['__fp']
            }
            
            # EXACT headers from WORKING HAR sequence (User ID 187032782)
            post_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Cache-Control': 'max-age=0',
                'Origin': 'https://anytime.club-os.com',
                'Referer': login_get_url,
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            print("   📤 Submitting login form with exact HAR sequence...")
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=post_headers,
                allow_redirects=True,
                timeout=30
            )
            
            print(f"   📊 Auth response status: {auth_response.status_code}")
            print(f"   📍 Auth response URL: {auth_response.url}")
            
            # HAR shows successful login returns 302, then redirects
            if auth_response.status_code == 200 and "action/Login" in auth_response.url:
                print("   🚨 LOGIN FAILED - Still on login page")
                
                # Check for specific error messages
                if "locked" in auth_response.text.lower() or "too many" in auth_response.text.lower():
                    print("   🔒 ACCOUNT LOCKED - Too many login attempts")
                elif "invalid" in auth_response.text.lower() or "incorrect" in auth_response.text.lower():
                    print("   ❌ INVALID CREDENTIALS")
                else:
                    print("   📄 Login page response snippet:")
                    # Look for error messages in the response
                    soup = BeautifulSoup(auth_response.text, 'html.parser')
                    error_divs = soup.find_all(['div', 'span', 'p'], class_=lambda x: x and any(word in x.lower() for word in ['error', 'alert', 'warning', 'message']))
                    if error_divs:
                        for error_div in error_divs:
                            print(f"   ⚠️  Error message: {error_div.get_text().strip()}")
                    else:
                        print(auth_response.text[:300] + "...")
                
                return False
            
            # Extract all cookies (should include apiV3AccessToken, loggedInUserId, etc.)
            print("   🍪 All cookies received:")
            for cookie_name, cookie_value in self.session.cookies.items():
                if len(cookie_value) > 50:
                    print(f"      {cookie_name}: {cookie_value[:50]}...")
                else:
                    print(f"      {cookie_name}: {cookie_value}")
            
            # Verify we have the required tokens
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            api_v3_access_token = self.session.cookies.get('apiV3AccessToken')
            
            if not api_v3_access_token:
                print("   ❌ Authentication failed - missing apiV3AccessToken")
                return False
            
            if not logged_in_user_id:
                print("   ❌ Authentication failed - missing loggedInUserId")
                return False
            
            # Store session data
            self.session_data = {
                'loggedInUserId': logged_in_user_id,
                'delegatedUserId': delegated_user_id,
                'JSESSIONID': session_id,
                'apiV3AccessToken': api_v3_access_token
            }
            
            self.access_token = api_v3_access_token
            self.authenticated = True
            
            print(f"   ✅ Authentication successful!")
            print(f"   👤 User ID: {logged_in_user_id}")
            print(f"   🎭 Delegated User ID: {delegated_user_id}")
            print(f"   🔑 API Token: {api_v3_access_token[:20]}...")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def navigate_to_training_packages(self, target_member_id="185777276"):
        """Follow the EXACT navigation flow from Training_Endpoints.har (CORRECTED SEQUENCE)"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
            
        print(f"\n🏋️ Following EXACT navigation flow from Training_Endpoints.har...")
        print(f"   🎯 Target Member ID: {target_member_id}")
        
        try:
            # CORRECTED SEQUENCE: Delegate FIRST, then navigate to packages page
            # Step 1: Set delegation to target member FIRST (this is the key difference!)
            print(f"   🎭 Step 1: Setting delegation to member {target_member_id} FIRST...")
            
            delegation_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view'  # HAR shows referer is Dashboard after login
            }
            
            delegate_url = f"{self.base_url}/action/Delegate/{target_member_id}/url=false"
            delegate_params = {'_': int(datetime.now().timestamp() * 1000)}
            
            delegate_response = self.session.get(delegate_url, headers=delegation_headers, params=delegate_params)
            print(f"   📊 Delegation Status: {delegate_response.status_code}")
            
            if delegate_response.status_code != 200:
                print(f"   ❌ Failed to set delegation: {delegate_response.status_code}")
                return None
                
            # Step 2: THEN navigate to PackageAgreementUpdated/spa/ (the training packages page)
            print("   📦 Step 2: Navigating to Training Packages page AFTER delegation...")
            
            package_agreement_url = f"{self.base_url}/action/PackageAgreementUpdated/spa/"
            package_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Referer': f'{self.base_url}/action/Dashboard/view'  # Referer is now Dashboard
            }
            
            package_response = self.session.get(package_agreement_url, headers=package_headers)
            print(f"   📊 Package Agreement Status: {package_response.status_code}")
            
            if package_response.status_code != 200:
                print(f"   ❌ Failed to load PackageAgreementUpdated: {package_response.status_code}")
                return None
            
            # CRITICAL STEP: The server embeds the correctly signed, delegated JWT directly into the page's HTML.
            print("   🔍 Parsing page HTML to extract the pre-made delegated JWT...")
            
            try:
                page_html = package_response.text
                
                # Use regex to find the ACCESS_TOKEN variable and extract its value.
                token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', page_html)
                
                if token_match:
                    delegated_token = token_match.group(1)
                    self.session_data['delegated_api_token'] = delegated_token
                    print(f"   ✅ SUCCESS: Directly extracted the delegated ACCESS_TOKEN from inline JavaScript!")
                    print(f"   🔑 Captured Token: {self.session_data['delegated_api_token'][:30]}...")
                else:
                    print("   ❌ FAILED: Could not find the ACCESS_TOKEN variable in the page's JavaScript.")
                    return None

            except Exception as e:
                print(f"   ❌ FAILED: An error occurred during HTML parsing: {e}")
                return None

            print("   ✅ Successfully navigated and prepared the delegated token!")
            return package_response
            
        except Exception as e:
            print(f"   ❌ Navigation error: {e}")
            return None
    
    def test_training_package_apis(self, target_member_id="185777276"):
        """
        Dynamically discovers package agreements for a member and then
        tests the billing-related API endpoints for each discovered agreement by
        replicating the exact sequence from a working HAR file.
        """
        if not self.authenticated:
            print("❌ Not authenticated")
            return None

        print(f"\n🔗 Dynamically discovering and testing packages for Member ID: {target_member_id}...")
        
        # STEP 1: Discover active package agreements for the member
        active_agreements = self._discover_member_agreements(target_member_id)
        
        if not active_agreements:
            print(f"   ❌ No active, valid package agreements found for Member ID {target_member_id}.")
            return None
            
        print(f"   ✅ Found {len(active_agreements)} active agreement(s) to test.")
        
        # STEP 2: Test billing endpoints for each discovered agreement
        all_results = {}
        for agreement in active_agreements:
            agreement_id = agreement.get('id')
            if agreement_id:
                results = self._test_billing_for_agreement(agreement)
                all_results[agreement_id] = results
                
        return all_results

    def _discover_member_agreements(self, target_member_id):
        """
        Tries various API endpoints to find a member's active package agreements.
        """
        print(f"   🔍 STEP 1: Discovering current package agreements for Member ID {target_member_id}...")
        
        import time
        timestamp = str(int(time.time() * 1000))
        
        # Use endpoints known to list agreements for a specific member
        discovery_endpoints = [
            f"/api/agreements/package_agreements/list?memberId={target_member_id}",
            f"/api/agreements/package_agreements/active?memberId={target_member_id}",
            f"/api/members/{target_member_id}/active_agreements",
            f"/api/agreements/package_agreements?memberId={target_member_id}",
        ]
        
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Authorization': f'Bearer {self.session_data["apiV3AccessToken"]}',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/'
        }
        
        for endpoint in discovery_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                params = {'_': timestamp}
                
                print(f"   📡 Discovering via: {endpoint}")
                response = self.session.get(url, headers=api_headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and data:
                        # Filter for agreements with a valid ID and status 2 (Active)
                        active_agreements = [agreement for agreement in data if agreement.get('id') and agreement.get('agreementStatus') == 2]
                        
                        if active_agreements:
                            print(f"   ✅ Found {len(active_agreements)} active agreement(s) for Member ID {target_member_id}.")
                            return active_agreements
                        else:
                            print(f"   ⚠️ No active agreements found in this response.")
                    else:
                        print(f"   ⚠️ Unexpected data format: {data}")
                else:
                    print(f"   ❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"   ❌ Exception while discovering agreements: {e}")
        
        print(f"   ⚠️ Discovery failed. Falling back to direct check for Agreement ID 1522516...")
        try:
            url = f"{self.base_url}/api/agreements/package_agreements/1522516"
            params = {'_': timestamp}
            response = self.session.get(url, headers=api_headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('id') and data.get('agreementStatus') == 2:
                    print(f"   ✅ Fallback successful. Found active Agreement ID 1522516.")
                    return [data] # Return as a list to match the expected format
        except Exception as e:
            print(f"   ❌ Fallback check failed: {e}")

        return []

    def _test_billing_for_agreement(self, agreement_data):
        """
        Follows the EXACT HAR sequence for a given agreement, using its dynamic data.
        """
        # Dynamically capture all required data from the discovered agreement
        agreement_id = agreement_data.get('id')
        start_date = agreement_data.get('startDate', '2024-01-01').split('T')[0] # Get just the date part
        duration = agreement_data.get('duration', 12)
        duration_type = agreement_data.get('durationType', 5)
        billing_duration = agreement_data.get('billingDuration', 2)
        billing_duration_type = agreement_data.get('billingDurationType', 6)
        location_id = agreement_data.get('locationId', 3586)

        print(f"\n   🔬 STEP 2: Testing billing sequence for Agreement ID: {agreement_id}...")
        
        import time
        base_timestamp = int(time.time() * 1000)
        
        # Dynamically construct the sequence of API calls using data from the discovered agreement
        exact_sequence = [
            {'url': f"/api/sales-tax/{location_id}/effectiveTaxes?effectiveDate={start_date}&_={base_timestamp}"},
            {'url': f"/api/agreements/package_agreements/{agreement_id}/billing_status?_={base_timestamp + 1}"},
            {'url': f"/api/agreements/package_agreements/V2/{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={base_timestamp + 2}"},
            {'url': f"/api/agreements/package_agreements/agreementTotalValue?agreementId={agreement_id}&_={base_timestamp + 3}"},
            {'url': f"/api/agreements/package_agreements/{agreement_id}/salespeople?_={base_timestamp + 4}"},
            {'url': f"/api/users/employee?locationId={location_id}&_={base_timestamp + 5}"},
            {'url': f"/api/package-agreement-proposals/scheduled-payments-count?duration={duration}&durationType={duration_type}&billingDuration={billing_duration}&billingDurationType={billing_duration_type}&startDate={start_date}&_={base_timestamp + 880}"},
            {'url': f"/api/member_payment_profiles?_={base_timestamp + 1055}"}
        ]
        
        # Use the SPECIAL delegated token for billing calls
        auth_token = self.session_data.get('delegated_api_token', self.session_data['apiV3AccessToken'])
        print(f"   🔑 Using Authorization Token: {auth_token[:30]}...")
        
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Authorization': f'Bearer {auth_token}',
            'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/'
        }
        
        results = {}
        print(f"   🎯 Executing {len(exact_sequence)} API calls in sequence for Agreement ID {agreement_id}...")
        
        for i, call in enumerate(exact_sequence):
            try:
                time.sleep(0.1) # Small delay to mimic browser
                url = f"{self.base_url}{call['url']}"
                
                print(f"   📡 Call {i+1}: {call['url']}")
                response = self.session.get(url, headers=api_headers, timeout=15)
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    results[call['url']] = data
                    print(f"   ✅ SUCCESS!")
                else:
                    print(f"   ❌ FAILED: {response.status_code} - {response.text[:200]}")
                    results[call['url']] = f"HTTP_{response.status_code}"
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results[call['url']] = f"ERROR: {str(e)}"
        
        return results

def main():
    print("🏋️ ClubOS Training Package Test - Following EXACT HAR Navigation Flow")
    print("=" * 70)
    
    tester = ClubOSTrainingPackageTest()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed, cannot proceed")
        return
    
    # Step 2: Follow the EXACT navigation flow from Training_payments.har
    print(f"\n🧭 Following EXACT navigation sequence from HAR file...")
    navigation_result = tester.navigate_to_training_packages()
    
    if not navigation_result:
        print("❌ Navigation failed, cannot proceed to API testing")
        return
    
    # Step 3: Test the exact API endpoints from HAR file  
    api_results_by_agreement = tester.test_training_package_apis(target_member_id="185777276")
    
    if api_results_by_agreement:
        for agreement_id, api_results in api_results_by_agreement.items():
            print(f"\n\n📊 Results for Agreement ID: {agreement_id}")
            print("=" * 50)
            
            for endpoint, result in api_results.items():
                print(f"\n🔗 {endpoint}")
                
                if isinstance(result, str) and result.startswith("HTTP_"):
                    print(f"   ❌ {result}")
                elif isinstance(result, str) and result.startswith("ERROR:"):
                    print(f"   ❌ {result}")
                elif isinstance(result, (dict, list)):
                    print(f"   ✅ SUCCESS - Got data:")
                    print(json.dumps(result, indent=4)[:500] + "..." if len(str(result)) > 500 else json.dumps(result, indent=4))
                else:
                    print(f"   ✅ SUCCESS - Got response:")
                    print(str(result)[:300] + "..." if len(str(result)) > 300 else str(result))
            
            # Summary for this agreement
            successful_endpoints = [k for k, v in api_results.items() if isinstance(v, (dict, list))]
            failed_endpoints = [k for k, v in api_results.items() if not isinstance(v, (dict, list))]
            
            print(f"\n📈 SUMMARY for Agreement {agreement_id}:")
            print(f"✅ Successful endpoints: {len(successful_endpoints)}")
            print(f"❌ Failed endpoints: {len(failed_endpoints)}")
            
            if successful_endpoints:
                print(f"\n🎯 WORKING ENDPOINTS for {agreement_id}:")
                for endpoint in successful_endpoints:
                    print(f"   ✅ {endpoint}")
                    
            if failed_endpoints:
                print(f"\n🚨 FAILED ENDPOINTS for {agreement_id}:")
                for endpoint in failed_endpoints:
                    print(f"   ❌ {endpoint} - {api_results[endpoint]}")
    
    print(f"\n🏁 Test completed - Following HAR navigation sequence")
    print("=" * 70)

if __name__ == "__main__":
    main()
