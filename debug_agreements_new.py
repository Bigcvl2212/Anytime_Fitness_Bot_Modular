#!/usr/bin/env python3
"""
Debug script to test ClubOS package agreements API and delegation flow.
Based on browser network inspection showing the proper API flow.
"""

import json
import logging
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubOSDebugger:
    def __init__(self):
        try:
            from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
            self.username = CLUBOS_USERNAME
            self.password = CLUBOS_PASSWORD
        except Exception:
            self.username = None
            self.password = None
        
        self.base_url = "https://anytime.club-os.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        self.authenticated = False
        self.access_token: Optional[str] = None

    def login(self) -> bool:
        """Login to ClubOS"""
        try:
            print("🔐 Logging into ClubOS...")
            
            # Step 1: Get login page and extract tokens
            r0 = self.session.get(f"{self.base_url}/action/Login/view", timeout=20)
            if r0.status_code not in (200, 302):
                print(f"❌ Login view failed: {r0.status_code}")
                return False
            
            # Extract form tokens
            soup = BeautifulSoup(r0.text, 'html.parser')
            _sourcePage = ''
            __fp = ''
            
            sp = soup.find('input', {'name': '_sourcePage'})
            if sp:
                _sourcePage = sp.get('value', '')
            
            fp = soup.find('input', {'name': '__fp'})
            if fp:
                __fp = fp.get('value', '')
            
            # Step 2: POST login credentials
            form_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': _sourcePage,
                '__fp': __fp,
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'{self.base_url}/action/Login/view',
            }
            
            r1 = self.session.post(f"{self.base_url}/action/Login", 
                                  data=form_data, headers=headers, 
                                  timeout=30, allow_redirects=True)
            
            if r1.status_code not in (200, 302):
                print(f"❌ Login POST failed: {r1.status_code}")
                return False
            
            # Check for session cookie
            cookies = self.session.cookies.get_dict()
            if 'JSESSIONID' not in cookies:
                print("❌ No session cookie found - login failed")
                return False
            
            # Get access token if available
            self.access_token = cookies.get('apiV3AccessToken')
            
            print("✅ Login successful")
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def navigate_to_dashboard(self) -> bool:
        """Navigate to dashboard to establish session and get API tokens"""
        try:
            print("🏠 Navigating to Dashboard...")
            
            response = self.session.get(f"{self.base_url}/action/Dashboard/view", timeout=20)
            
            if response.status_code == 200:
                print(f"   📊 Dashboard Status: {response.status_code}")
                
                # Check for API token in cookies after dashboard visit
                cookies = self.session.cookies.get_dict()
                api_token = cookies.get('apiV3AccessToken')
                
                if api_token:
                    self.access_token = api_token
                    print(f"   ✅ Found API token: {api_token[:20]}...")
                else:
                    print("   ⚠️ No API token found in cookies, will try without Bearer token...")
                
                return True
            else:
                print(f"   ❌ Dashboard failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Dashboard navigation error: {e}")
            return False

    def delegate_to_member(self, member_id: str) -> bool:
        """Delegate to a specific member to access their data"""
        try:
            print(f"👤 Delegating to member {member_id}...")
            
            # Use the exact delegation endpoint pattern from browser inspection
            timestamp = int(time.time() * 1000)
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false"
            
            headers = {
                'Referer': f'{self.base_url}/action/Dashboard/view',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            # Add timestamp parameter for cache busting
            params = {'_': timestamp}
            
            # Try GET method as shown in browser logs
            response = self.session.get(delegate_url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Delegation Status: {response.status_code}")
            print(f"   📏 Response Length: {len(response.text)} bytes")
            
            if response.status_code in (200, 302):
                print("   ✅ Delegation successful")
                
                # After delegation, the cookies should be updated for this member's context
                print("   🔄 Checking delegation cookies...")
                cookies = self.session.cookies.get_dict()
                print(f"   🍪 Total cookies: {len(cookies)}")
                
                # Look for any delegation-related cookies
                for cookie_name, cookie_value in cookies.items():
                    if 'delegate' in cookie_name.lower() or 'member' in cookie_name.lower():
                        print(f"   🎯 Found delegation cookie: {cookie_name}")
                
                return True
            else:
                print(f"   ❌ Delegation failed: {response.status_code}")
                if response.text:
                    print(f"   Response preview: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Delegation error: {e}")
            return False

    def get_package_agreements_list(self) -> list:
        """Get the list of package agreements using the API endpoint"""
        try:
            print("📋 Fetching package agreements list...")
            
            timestamp = int(time.time() * 1000)
            list_url = f"{self.base_url}/api/agreements/package_agreements/list"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view',
            }
            
            # Add Bearer token if we have it
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            params = {'_': timestamp}
            
            response = self.session.get(list_url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 List API Status: {response.status_code}")
            print(f"   📏 Content-Length: {len(response.text)} bytes")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Found {len(data)} package agreements")
                    if data:
                        # Show first agreement as example
                        first_agreement = data[0]
                        print(f"   📄 Sample agreement: {first_agreement}")
                    return data
                except json.JSONDecodeError:
                    print(f"   ⚠️ Non-JSON response: {response.text[:200]}")
                    return []
            else:
                print(f"   ❌ Error Response: {response.text[:100]}")
                return []
                
        except Exception as e:
            print(f"❌ Package agreements list error: {e}")
            return []

    def get_agreement_details(self, agreement_id: str) -> dict:
        """Get detailed information about a specific agreement"""
        try:
            print(f"📄 Fetching agreement details for ID: {agreement_id}")
            
            timestamp = int(time.time() * 1000)
            
            # Try the V2 endpoint with includes
            details_url = f"{self.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view',
            }
            
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            params = {
                'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes'],
                '_': timestamp
            }
            
            response = self.session.get(details_url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Details API Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Agreement details retrieved")
                    return data
                except json.JSONDecodeError:
                    print(f"   ⚠️ Non-JSON response: {response.text[:200]}")
                    return {}
            else:
                print(f"   ❌ Error Response: {response.text[:100]}")
                return {}
                
        except Exception as e:
            print(f"❌ Agreement details error: {e}")
            return {}

    def get_billing_status(self, agreement_id: str) -> dict:
        """Get billing status for a specific agreement"""
        try:
            print(f"💰 Fetching billing status for agreement: {agreement_id}")
            
            timestamp = int(time.time() * 1000)
            billing_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
            
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view',
            }
            
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            params = {'_': timestamp}
            
            response = self.session.get(billing_url, headers=headers, params=params, timeout=20)
            
            print(f"   📊 Billing API Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Billing status retrieved")
                    return data
                except json.JSONDecodeError:
                    print(f"   ⚠️ Non-JSON response: {response.text[:200]}")
                    return {}
            else:
                print(f"   ❌ Error Response: {response.text[:100]}")
                return {}
                
        except Exception as e:
            print(f"❌ Billing status error: {e}")
            return {}

def main():
    """Test the complete ClubOS delegation and package agreements flow"""
    print("🧪 Testing complete ClubOS delegation and package agreements flow...")
    print()
    
    debugger = ClubOSDebugger()
    
    # Step 1: Login
    print("1️⃣ STEP 1: Login to ClubOS")
    if not debugger.login():
        print("❌ Login failed - cannot continue")
        return
    print()
    
    # Step 2: Navigate to dashboard for API tokens
    print("2️⃣ STEP 2: Navigate to Dashboard for API tokens")
    if not debugger.navigate_to_dashboard():
        print("❌ Dashboard navigation failed")
        return
    print()
    
    # Step 3: Try delegation with multiple members
    print("3️⃣ STEP 3: Try Delegation with Multiple Members")
    
    # Test members based on the assignees list
    test_members = [
        ("185182950", "Javae Dixon"),      # You mentioned she's hella past due on her package
        ("189425730", "Dennis Rost"),      # You mentioned checking Dennis before  
        ("125814462", "Mark Benzinger"),   # Original test member
        ("191215290", "Alejandra Espinoza"), # First in the list
    ]
    
    successful_delegation = None
    
    for member_id, member_name in test_members:
        print(f"\n👤 Testing delegation to {member_name} ({member_id})...")
        if debugger.delegate_to_member(member_id):
            print(f"   ✅ Delegation to {member_name} successful")
            successful_delegation = (member_id, member_name)
            break
        else:
            print(f"   ❌ Delegation to {member_name} failed")
    
    if not successful_delegation:
        print("❌ All delegation attempts failed")
        return
    
    member_id, member_name = successful_delegation
    print(f"\n🎯 Using {member_name} ({member_id}) for API testing...")
    print()
    
    # Step 4: Get package agreements list
    print("4️⃣ STEP 4: Get Package Agreements List")
    agreements_list = debugger.get_package_agreements_list()
    if not agreements_list:
        print("❌ No package agreements found")
        print()
        print("🔍 Let's try a different approach - checking the agreements page directly...")
        
        # Alternative: Try accessing the agreements page with member ID
        try:
            # Try with the delegated member ID
            agreements_page_url = f"{debugger.base_url}/action/Agreements?memberId={member_id}"
            print(f"🔍 Trying agreements page with member ID: {agreements_page_url}")
            response = debugger.session.get(agreements_page_url, timeout=20)
            print(f"📊 Agreements page status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()
                
                # Look for any mention of training or package agreements
                print(f"📄 Page content length: {len(page_text)} characters")
                if 'training' in page_text.lower() or 'package' in page_text.lower():
                    print("✅ Found training/package content on agreements page")
                    print(f"📄 Page content preview: {page_text[:1000]}...")
                    
                    # Look for specific patterns that might indicate agreements
                    if 'agreement' in page_text.lower():
                        print("🎯 Found 'agreement' text in page")
                    if 'session' in page_text.lower():
                        print("🎯 Found 'session' text in page")
                    if 'billing' in page_text.lower():
                        print("🎯 Found 'billing' text in page")
                        
                    # Try to find any table or structured data
                    tables = soup.find_all('table')
                    print(f"📊 Found {len(tables)} tables on the page")
                    
                    for i, table in enumerate(tables):
                        table_text = table.get_text(' ', strip=True)
                        if len(table_text) > 50:  # Only show substantial tables
                            print(f"📊 Table {i+1} content: {table_text[:200]}...")
                        
                else:
                    print("❌ No training/package content found on agreements page")
                    print(f"📄 Page text sample: {page_text[:500]}...")
            
        except Exception as e:
            print(f"❌ Direct agreements page access error: {e}")
            
        # Also try the PackageAgreements SPA page that was mentioned in original debug
        try:
            print("\n🔍 Trying PackageAgreements SPA page...")
            spa_url = f"{debugger.base_url}/action/PackageAgreements/spa/"
            response = debugger.session.get(spa_url, timeout=20)
            print(f"📊 SPA page status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()
                
                if len(page_text) > 100:
                    print(f"📄 SPA page content preview: {page_text[:500]}...")
                    
                    # Look for JavaScript that might tell us about API endpoints
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and 'api' in script.string.lower():
                            script_text = script.string
                            if '/api/' in script_text:
                                print("🎯 Found API references in JavaScript:")
                                # Extract API endpoints from JavaScript
                                import re
                                api_matches = re.findall(r'/api/[^"\']+', script_text)
                                for match in api_matches[:5]:  # Show first 5 matches
                                    print(f"   📡 {match}")
            
        except Exception as e:
            print(f"❌ SPA page access error: {e}")
        
        return
    print()
    
    # Step 5: Get details for each agreement
    print("5️⃣ STEP 5: Get Agreement Details")
    for i, agreement in enumerate(agreements_list[:3]):  # Limit to first 3 for testing
        agreement_id = agreement.get('id') or agreement.get('agreementId')
        if agreement_id:
            print(f"📄 Agreement {i+1}: ID {agreement_id}")
            details = debugger.get_agreement_details(str(agreement_id))
            billing = debugger.get_billing_status(str(agreement_id))
            print()
    
    print("✅ Complete delegation flow test finished!")

if __name__ == "__main__":
    main()
