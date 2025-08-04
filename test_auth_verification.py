#!/usr/bin/env python3
"""
Test basic authenticated endpoints to verify our authentication is working
"""

import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

class ClubOSAuthTest:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
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
        """Authenticate using EXACT sequence from working pattern"""
        try:
            print("🔐 Attempting ClubOS authentication...")
            
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
            
            # Extract form fields
            soup = BeautifulSoup(login_response.text, 'html.parser')
            hidden_inputs = soup.find_all('input', type='hidden')
            form_data = {}
            
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            if '_sourcePage' not in form_data or '__fp' not in form_data:
                print("   ❌ Missing required CSRF tokens!")
                return False
            
            # Step 2: POST login
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
            
            if auth_response.status_code == 200 and "action/Login" in auth_response.url:
                print("   🚨 LOGIN FAILED - Still on login page")
                return False
            
            # Extract authentication tokens
            api_v3_access_token = self.session.cookies.get('apiV3AccessToken')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            
            if not api_v3_access_token or not logged_in_user_id:
                print("   ❌ Authentication failed - missing tokens")
                return False
            
            self.session_data = {
                'loggedInUserId': logged_in_user_id,
                'apiV3AccessToken': api_v3_access_token
            }
            
            self.access_token = api_v3_access_token
            self.authenticated = True
            
            print(f"   ✅ Authentication successful!")
            print(f"   👤 User ID: {logged_in_user_id}")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def test_basic_endpoints(self):
        """Test basic endpoints to verify authentication"""
        if not self.authenticated:
            print("❌ Not authenticated")
            return
            
        print(f"\n🧪 Testing basic authenticated endpoints...")
        
        # Test basic endpoints that should work
        test_endpoints = [
            "/action/Dashboard/view",
            "/action/Calendar",
            "/action/Members",
            "/ajax/user/current",
            "/api/users/current"
        ]
        
        for endpoint in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f'{self.base_url}/action/Dashboard/view'
                }
                
                print(f"   📡 Testing: {endpoint}")
                response = self.session.get(url, headers=headers, timeout=10)
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    if "action/Login" in response.url:
                        print(f"   🚨 REDIRECTED TO LOGIN - Session expired")
                    else:
                        print(f"   ✅ Success - {len(response.text)} chars received")
                        
                        # Save successful responses for analysis
                        if endpoint.startswith('/api/'):
                            try:
                                data = response.json()
                                print(f"   📋 JSON data keys: {list(data.keys()) if isinstance(data, dict) else 'List/Other'}")
                            except:
                                print(f"   📄 Non-JSON response")
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    print(f"   📄 Response snippet: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error with {endpoint}: {e}")

def main():
    print("🧪 ClubOS Authentication Verification Test")
    print("=" * 50)
    
    tester = ClubOSAuthTest()
    
    # Step 1: Authenticate
    if not tester.authenticate():
        print("❌ Authentication failed, cannot proceed")
        return
    
    # Step 2: Test basic endpoints
    tester.test_basic_endpoints()

if __name__ == "__main__":
    main()
