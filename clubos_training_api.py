#!/usr/bin/env python3
"""
ClubOS Training Package API - Working implementation
Extracted from enhanced_dashboard_with_agreements.py for better modularity
"""

import requests
import json
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ClubOSTrainingPackageAPI:
    """
    Integrated ClubOS Training Package API for dashboard use
    Uses the working authentication and token extraction from test_leisa_training_packages_clean.py
    """
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        self.session_data = {}
        self.access_token = None
        
        # Set headers to mimic working browser
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
        """Authenticate using the working HAR sequence"""
        try:
            print("🔐 Authenticating with ClubOS...")
            
            # Step 1: GET login page
            login_get_url = f"{self.base_url}/action/Login/view"
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
            
            # Extract form fields dynamically
            soup = BeautifulSoup(login_response.text, 'html.parser')
            login_form = soup.find('form')
            if not login_form:
                print("   ❌ No login form found!")
                return False
            
            # Extract ALL hidden fields
            hidden_inputs = login_form.find_all('input', type='hidden')
            form_data = {}
            
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            # Check for required tokens
            if '_sourcePage' not in form_data or '__fp' not in form_data:
                print("   ❌ Missing required CSRF tokens!")
                return False
            
            # Step 2: POST login with extracted CSRF tokens
            login_data = {
                'login': 'Submit',
                'username': 'j.mayo', 
                'password': 'j@SD4fjhANK5WNA',
                '_sourcePage': form_data['_sourcePage'],
                '__fp': form_data['__fp']
            }
            
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
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=post_headers,
                allow_redirects=True,
                timeout=30
            )
            
            # Check for successful login
            if auth_response.status_code == 200 and "action/Login" in auth_response.url:
                print("   🚨 LOGIN FAILED - Still on login page")
                return False
            
            # Extract cookies
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            api_v3_access_token = self.session.cookies.get('apiV3AccessToken')
            
            if not api_v3_access_token or not logged_in_user_id:
                print("   ❌ Authentication failed - missing required tokens")
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
            return True
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def get_member_payment_status(self, member_id):
        """Get payment status for a specific member - REAL DATA ONLY"""
        if not self.authenticated:
            if not self.authenticate():
                return None  # No fallbacks - return None if can't authenticate
        
        try:
            # Step 1: Set delegation to target member
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
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false"
            delegate_params = {'_': int(datetime.now().timestamp() * 1000)}
            
            delegate_response = self.session.get(delegate_url, headers=delegation_headers, params=delegate_params)
            
            if delegate_response.status_code != 200:
                return None
                
            # Step 2: Navigate to PackageAgreementUpdated/spa/ to get the delegated token
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
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            
            package_response = self.session.get(package_agreement_url, headers=package_headers)
            
            if package_response.status_code != 200:
                return None
            
            # Extract the delegated ACCESS_TOKEN from the page's JavaScript
            page_html = package_response.text
            token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', page_html)
            
            if not token_match:
                return None
                
            delegated_token = token_match.group(1)
            
            # Step 3: Call billing_status API with the delegated token
            timestamp = int(time.time() * 1000)
            
            # First, discover active agreements for this member
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Authorization': f'Bearer {delegated_token}',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/'
            }
            
            # Try to find active agreements
            discovery_endpoints = [
                f"/api/agreements/package_agreements/list?memberId={member_id}",
                f"/api/agreements/package_agreements/active?memberId={member_id}",
                f"/api/members/{member_id}/active_agreements",
                f"/api/agreements/package_agreements?memberId={member_id}",
            ]
            
            for endpoint in discovery_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    params = {'_': timestamp}
                    
                    response = self.session.get(url, headers=api_headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and data:
                            # Filter for active agreements (status 2)
                            active_agreements = [agreement for agreement in data if agreement.get('id') and agreement.get('agreementStatus') == 2]
                            
                            if active_agreements:
                                # Get billing status for the first active agreement
                                agreement_id = active_agreements[0].get('id')
                                billing_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
                                billing_params = {'_': timestamp + 1}
                                
                                billing_response = self.session.get(billing_url, headers=api_headers, params=billing_params, timeout=10)
                                
                                if billing_response.status_code == 200:
                                    billing_data = billing_response.json()
                                    
                                    # Check if there are past due items
                                    past_due_items = billing_data.get('past', [])
                                    
                                    if past_due_items:
                                        return "Past Due"
                                    else:
                                        return "Current"
                                        
                except Exception as e:
                    continue
            
            return None  # No fallbacks - return None if can't get real data
            
        except Exception as e:
            print(f"Error getting payment status for member {member_id}: {e}")
            return None  # No fallbacks
