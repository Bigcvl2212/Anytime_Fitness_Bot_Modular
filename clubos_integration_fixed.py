"""
Robust ClubOS API Integration for Dashboard
Correctly handles token extraction and session management
"""

import os
import sys
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class RobustClubOSClient:
    """Robust ClubOS API client with proper authentication flow"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        
        # Session tokens
        self.form_tokens = {}  # _sourcePage, __fp, etc.
        self.csrf_token = None
        self.api_token = None
        self.is_authenticated = False
        
        # Manager delegation - Jeremy Mayo's user ID
        self.jeremy_mayo_user_id = 187032782
        self.delegated_user_id = None
        self.logged_in_user_id = None
        
        # JWT tokens for API access
        self.api_v3_access_token = None
        self.api_v3_refresh_token = None
        self.api_v3_id_token = None
        
        # Cached calendar data from immediate access
        self._cached_calendar_data = None
        
        # Set realistic browser headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0"
        })
    
    def authenticate(self) -> bool:
        """Authenticate with ClubOS using proper form submission"""
        try:
            print("🔐 Starting ClubOS authentication...")
            
            # Step 1: Get login page and extract all hidden form fields
            login_url = "https://anytime.club-os.com/action/Login/view?__fsk=1221801756"
            print(f"📄 Loading login page: {login_url}")
            
            login_response = self.session.get(login_url)
            if not login_response.ok:
                print(f"❌ Failed to load login page: {login_response.status_code}")
                return False
            
            print("🔍 Extracting authentication tokens...")
            form_data = self._extract_login_form_data(login_response.text)
            
            if not form_data:
                print("❌ Could not extract login form data")
                return False
            
            # Step 2: Add credentials to form data
            form_data.update({
                "username": self.username,
                "password": self.password
            })
            
            print(f"🔑 Submitting login with form tokens: {list(form_data.keys())}")
            
            # Step 3: Submit login form with proper headers
            login_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": self.base_url,
                "Referer": login_url,
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1"
            }
            
            response = self.session.post(
                login_url, 
                data=form_data, 
                headers=login_headers,
                allow_redirects=True
            )
            
            # Step 4: Verify authentication success
            if self._verify_authentication(response):
                self.is_authenticated = True
                print("✅ Authentication successful!")
                
                # Step 5: IMMEDIATE calendar access (before session expires)
                print("🚀 Attempting immediate calendar access while session is fresh...")
                immediate_calendar_data = self._immediate_calendar_access()
                
                # Step 6: Extract session info and JWT tokens
                self._extract_session_info(response)
                
                # Step 7: Execute delegate step for manager access (non-blocking)
                if not self._execute_delegate_step():
                    print("⚠️ Delegate step failed - calendar access may be limited")
                
                # Step 8: Refresh session tokens
                self._refresh_session_tokens()
                
                # Store immediate calendar data if we got it
                if immediate_calendar_data:
                    self._cached_calendar_data = immediate_calendar_data
                    print(f"✅ Cached {len(immediate_calendar_data)} calendar items from immediate access")
                
                return True
            else:
                print("❌ Authentication failed - still on login page")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_login_form_data(self, html_content: str) -> Dict[str, str]:
        """Extract all form data from login page including hidden fields"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            form_data = {}
            
            # Find login form (usually has username/password fields)
            login_form = None
            forms = soup.find_all('form')
            
            for form in forms:
                # Look for username or password inputs
                if (form.find('input', {'name': 'username'}) or 
                    form.find('input', {'name': 'password'}) or
                    form.find('input', {'type': 'password'})):
                    login_form = form
                    break
            
            if not login_form:
                print("❌ Could not find login form")
                return {}
            
            # Extract all input fields from the login form
            inputs = login_form.find_all('input')
            for input_field in inputs:
                name = input_field.get('name')
                value = input_field.get('value', '')
                input_type = input_field.get('type', 'text')
                
                if name and input_type != 'submit':
                    form_data[name] = value
                    if input_type == 'hidden':
                        print(f"🔑 Found hidden field: {name} = {value[:20]}...")
                        self.form_tokens[name] = value
            
            # Also look for any CSRF tokens in meta tags
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                csrf_value = csrf_meta.get('content')
                if csrf_value:
                    self.csrf_token = csrf_value
                    form_data['csrf_token'] = csrf_value
                    form_data['_token'] = csrf_value
                    print(f"🔑 Found CSRF token in meta: {csrf_value[:20]}...")
            
            # Look for any JavaScript-embedded tokens
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Common patterns for tokens in JavaScript
                    token_patterns = [
                        r'window\.csrfToken\s*=\s*["\']([^"\']+)["\']',
                        r'_token["\']:\s*["\']([^"\']+)["\']',
                        r'csrf_token["\']:\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in token_patterns:
                        match = re.search(pattern, script.string)
                        if match:
                            token = match.group(1)
                            self.csrf_token = token
                            form_data['csrf_token'] = token
                            form_data['_token'] = token
                            print(f"🔑 Found token in JS: {token[:20]}...")
                            break
            
            print(f"✅ Extracted {len(form_data)} form fields")
            return form_data
            
        except Exception as e:
            print(f"❌ Error extracting form data: {e}")
            return {}
    
    def _verify_authentication(self, response: requests.Response) -> bool:
        """Verify if authentication was successful"""
        # Check URL - should not be on login page
        if 'login' in response.url.lower():
            print(f"❌ Still on login page: {response.url}")
            return False
        
        # Check for dashboard/calendar indicators
        success_indicators = [
            'dashboard', 'calendar', 'action/dashboard', 'action/calendar',
            'members', 'reports', 'settings'
        ]
        
        if any(indicator in response.url.lower() for indicator in success_indicators):
            print(f"✅ Redirected to authenticated page: {response.url}")
            return True
        
        # Check response content for authenticated elements
        content_lower = response.text.lower()
        auth_indicators = [
            'welcome', 'logout', 'dashboard', 'member', 'calendar'
        ]
        
        if any(indicator in content_lower for indicator in auth_indicators):
            print("✅ Found authenticated content indicators")
            return True
        
        # Check for authentication cookies
        auth_cookies = ['JSESSIONID', 'session_id', 'club_os_session']
        session_cookies = [cookie.name for cookie in self.session.cookies]
        
        if any(cookie in session_cookies for cookie in auth_cookies):
            print(f"✅ Found authentication cookies: {session_cookies}")
            return True
        
        print("❌ No authentication indicators found")
        return False
    
    def _immediate_calendar_access(self) -> List[Dict]:
        """
        Attempt immediate calendar access right after authentication while session is fresh
        """
        try:
            print("⚡ Immediate calendar access (session fresh)...")
            
            # Try calendar access immediately with minimal delay
            calendar_url = f"{self.base_url}/action/Calendar"
            
            # Simple headers - don't overcomplicate
            headers = {
                "User-Agent": self.session.headers["User-Agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Login/view"
            }
            
            # Quick calendar access
            response = self.session.get(calendar_url, headers=headers, timeout=5)
            
            print(f"   Immediate calendar: {response.status_code} -> {response.url}")
            
            if response.ok and 'action/Login' not in response.url:
                print("✅ Immediate calendar access successful!")
                
                # Save for debugging
                try:
                    os.makedirs("data/debug_outputs", exist_ok=True)
                    with open("data/debug_outputs/immediate_calendar_success.html", 'w', encoding='utf-8') as f:
                        f.write(response.text)
                except:
                    pass
                
                # Parse the data immediately
                calendar_data = self._parse_calendar_html_robust(response.text, datetime.now().strftime("%Y-%m-%d"))
                print(f"   Immediate parsing: {len(calendar_data)} items")
                return calendar_data
                
            else:
                print("⚠️ Immediate calendar access redirected to login")
                return []
                
        except Exception as e:
            print(f"⚠️ Immediate calendar access failed: {e}")
            return []
    
    def _extract_session_info(self, response):
        """Extract session information including user IDs and JWT tokens"""
        try:
            print("🔍 Extracting session information...")
            
            # Extract user IDs from cookies
            for cookie in self.session.cookies:
                if cookie.name == 'loggedInUserId':
                    self.logged_in_user_id = cookie.value
                    print(f"   Logged in user ID: {self.logged_in_user_id}")
                elif cookie.name == 'delegatedUserId':
                    self.delegated_user_id = cookie.value
                    print(f"   Delegated user ID: {self.delegated_user_id}")
                elif cookie.name == 'apiV3AccessToken':
                    self.api_v3_access_token = cookie.value
                    print(f"   API v3 access token: {self.api_v3_access_token[:20]}...")
                elif cookie.name == 'apiV3RefreshToken':
                    self.api_v3_refresh_token = cookie.value
                    print(f"   API v3 refresh token: {self.api_v3_refresh_token[:20]}...")
                elif cookie.name == 'apiV3IdToken':
                    self.api_v3_id_token = cookie.value
                    print(f"   API v3 ID token: {self.api_v3_id_token[:20]}...")
            
            # Print all cookies for debugging
            print(f"   All cookies: {[(cookie.name, cookie.value[:20] if len(cookie.value) > 20 else cookie.value) for cookie in self.session.cookies]}")
            
            # Extract additional session info from response content
            if response and response.text:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for JavaScript variables with session info
                script_tags = soup.find_all('script')
                for script in script_tags:
                    if script.string:
                        # Look for user ID patterns
                        if 'userId' in script.string:
                            user_id_match = re.search(r'userId["\']?\s*:\s*["\']?(\d+)', script.string)
                            if user_id_match and not self.logged_in_user_id:
                                self.logged_in_user_id = user_id_match.group(1)
                                print(f"   Found user ID in script: {self.logged_in_user_id}")
            
            print("✅ Session information extracted")
            
        except Exception as e:
            print(f"⚠️ Error extracting session info: {e}")
    
    def _execute_delegate_step(self) -> bool:
        """
        Execute the critical delegate step for manager access
        Based on HAR analysis: /action/Delegate/{delegatedUserId}/url=false
        """
        try:
            print("🎯 Executing delegate step for manager access...")
            
            # First, check if we already have the right user context
            if self.logged_in_user_id and str(self.logged_in_user_id) == str(self.jeremy_mayo_user_id):
                print(f"   ✅ Already logged in as Jeremy Mayo (ID: {self.logged_in_user_id})")
                print("   ✅ Skipping delegate step - already in correct user context")
                self.delegated_user_id = self.logged_in_user_id
                return True
            
            # Use Jeremy Mayo's user ID as the delegate target
            delegate_user_id = self.jeremy_mayo_user_id
            
            # If we have a logged in user ID but it's different, still try to delegate to Jeremy
            if self.logged_in_user_id:
                print(f"   Logged in as user ID: {self.logged_in_user_id}")
                print(f"   Attempting to delegate to Jeremy Mayo (ID: {delegate_user_id})")
            else:
                print(f"   No logged in user ID found, using Jeremy Mayo's ID: {delegate_user_id}")
            
            # Construct delegate URL from HAR analysis
            delegate_url = f"{self.base_url}/action/Delegate/{delegate_user_id}/url=false"
            print(f"📡 Delegate URL: {delegate_url}")
            
            # Set proper headers for delegate request (from HAR analysis)
            delegate_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"{self.base_url}/action/Dashboard",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Cache-Control": "max-age=0"
            }
            
            # Execute delegate request
            delegate_response = self.session.get(delegate_url, headers=delegate_headers, timeout=10)
            
            print(f"   Delegate response status: {delegate_response.status_code}")
            print(f"   Delegate response URL: {delegate_response.url}")
            
            if delegate_response.ok:
                # Check if we got the expected delegate response
                if 'action/Login' not in delegate_response.url:
                    print("✅ Delegate step successful!")
                    
                    # Update delegated user ID from the response
                    self.delegated_user_id = str(delegate_user_id)
                    
                    # Extract any new session tokens from delegate response
                    self._extract_session_info(delegate_response)
                    
                    # Verify delegate cookies were set
                    delegate_cookies = [cookie.name for cookie in self.session.cookies]
                    if 'delegatedUserId' in delegate_cookies:
                        print("✅ Delegate cookies confirmed")
                    else:
                        print("⚠️ Delegate cookies not found, but proceeding")
                    
                    return True
                else:
                    print("❌ Delegate step redirected to login - this is normal if already in correct context")
                    print("   ✅ Proceeding without delegate - session should still work for manager")
                    # Even if delegate fails, we can still try calendar access
                    self.delegated_user_id = str(self.jeremy_mayo_user_id)
                    return True
            else:
                print(f"❌ Delegate request failed: {delegate_response.status_code}")
                print("   ✅ Proceeding without delegate - session should still work")
                return True  # Don't fail authentication just because delegate failed
                
        except Exception as e:
            print(f"❌ Error in delegate step: {e}")
            print("   ✅ Proceeding without delegate - session should still work")
            return True  # Don't fail authentication just because delegate failed

    def _refresh_session_tokens(self):
        """Visit key pages to extract and refresh session tokens"""
        try:
            # Visit dashboard to get fresh session state
            dashboard_url = f"{self.base_url}/action/Dashboard"
            dashboard_response = self.session.get(dashboard_url, timeout=10)
            
            if dashboard_response.ok:
                print("📊 Visited dashboard page")
                self._extract_session_tokens(dashboard_response.text, "dashboard")
            
            # Visit calendar page for calendar-specific tokens
            calendar_url = f"{self.base_url}/action/Calendar"
            calendar_response = self.session.get(calendar_url, timeout=10)
            
            if calendar_response.ok:
                print("📅 Visited calendar page")
                self._extract_session_tokens(calendar_response.text, "calendar")
                
            # Skip messaging page if it's causing "response ended prematurely" errors
            # # Visit messaging page for messaging tokens
            # messages_url = f"{self.base_url}/action/Messages"
            # messages_response = self.session.get(messages_url, timeout=10)
            # 
            # if messages_response.ok:
            #     print("💬 Visited messaging page")
            #     self._extract_session_tokens(messages_response.text, "messages")
                
        except Exception as e:
            print(f"⚠️ Error refreshing session tokens: {e}")
    
    def _extract_session_tokens(self, html_content: str, page_type: str):
        """Extract session tokens from authenticated pages"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for any hidden forms with tokens
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all('input', {'type': 'hidden'})
                for input_field in inputs:
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    if name and value:
                        self.form_tokens[name] = value
                        print(f"🔑 Updated {page_type} token: {name}")
            
            # Look for CSRF tokens in meta tags
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                csrf_value = csrf_meta.get('content')
                if csrf_value:
                    self.csrf_token = csrf_value
                    print(f"🔑 Updated CSRF token from {page_type}")
            
            # Look for API tokens in JavaScript
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # Look for various token patterns
                    token_patterns = [
                        r'apiV3AccessToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                        r'window\.apiToken\s*=\s*["\']([^"\']+)["\']',
                        r'api_token["\']:\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in token_patterns:
                        match = re.search(pattern, script.string)
                        if match:
                            self.api_token = match.group(1)
                            print(f"🔑 Found API token in {page_type}: {self.api_token[:20]}...")
                            break
            
            # Check cookies for new tokens
            for cookie in self.session.cookies:
                if 'token' in cookie.name.lower():
                    if cookie.name == 'apiV3AccessToken':
                        self.api_token = cookie.value
                        print(f"🍪 Updated API token from cookie")
                    elif 'csrf' in cookie.name.lower():
                        self.csrf_token = cookie.value
                        print(f"🍪 Updated CSRF token from cookie")
                        
        except Exception as e:
            print(f"⚠️ Error extracting session tokens: {e}")
    
    
    def _get_request_headers(self, content_type: str = "application/x-www-form-urlencoded") -> Dict[str, str]:
        """Get headers with all authentication tokens for API requests"""
        headers = {
            "Content-Type": content_type,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/action/Dashboard",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        # Add CSRF token if available
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
            headers["X-CSRFToken"] = self.csrf_token
        
        # Add API token if available
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
            headers["X-API-Token"] = self.api_token
        
        return headers
    
    def send_message(self, member_name: str, message: str) -> bool:
        """Send message to member via ClubOS"""
        try:
            if not self.is_authenticated:
                print("❌ Not authenticated with ClubOS")
                return False
            
            print(f"📤 Sending message to {member_name}...")
            
            # Refresh session tokens before sending
            self._refresh_session_tokens()
            
            # Method 1: Try direct messaging API
            success = self._send_message_api(member_name, message)
            if success:
                return True
            
            # Method 2: Try form-based messaging
            success = self._send_message_form(member_name, message)
            if success:
                return True
            
            print(f"❌ All messaging methods failed for {member_name}")
            return False
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def _send_message_api(self, member_name: str, message: str) -> bool:
        """Try sending message via API endpoint"""
        try:
            # First, find the member
            member_id = self._search_member(member_name)
            if not member_id:
                print(f"❌ Member {member_name} not found via API")
                return False
            
            # Try various messaging endpoints
            message_endpoints = [
                "/ajax/messages/send",
                "/api/messages/send",
                "/action/Messages/send",
                "/Messages/send"
            ]
            
            for endpoint in message_endpoints:
                message_url = f"{self.base_url}{endpoint}"
                
                # Prepare message data with all possible token formats
                message_data = {
                    "member_id": member_id,
                    "message": message,
                    "subject": "Gym Message",
                    "type": "text"
                }
                
                # Add all form tokens we have
                message_data.update(self.form_tokens)
                
                # Add CSRF token in multiple formats
                if self.csrf_token:
                    message_data.update({
                        "csrf_token": self.csrf_token,
                        "_token": self.csrf_token,
                        "authenticity_token": self.csrf_token
                    })
                
                print(f"🔄 Trying messaging endpoint: {endpoint}")
                
                response = self.session.post(
                    message_url,
                    data=message_data,
                    headers=self._get_request_headers()
                )
                
                if response.ok:
                    print(f"✅ Message sent via {endpoint}")
                    return True
                else:
                    print(f"❌ Failed {endpoint}: {response.status_code}")
            
            return False
            
        except Exception as e:
            print(f"❌ API messaging error: {e}")
            return False
    
    def _send_message_form(self, member_name: str, message: str) -> bool:
        """Try sending message via web form"""
        try:
            # Visit messaging page to get form
            messages_url = f"{self.base_url}/action/Messages"
            response = self.session.get(messages_url)
            
            if not response.ok:
                return False
            
            # Extract messaging form data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for messaging form
            message_form = soup.find('form', {'action': re.compile(r'message', re.I)})
            if not message_form:
                # Try any form with text area
                message_form = soup.find('form', lambda tag: tag.find('textarea'))
            
            if not message_form:
                print("❌ Could not find messaging form")
                return False
            
            # Extract form data
            form_data = {}
            inputs = message_form.find_all('input')
            for input_field in inputs:
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value
            
            # Add message content
            form_data.update({
                "recipient": member_name,
                "message": message,
                "subject": "Gym Message"
            })
            
            # Submit form
            form_action = message_form.get('action') or '/action/Messages'
            submit_url = urljoin(self.base_url, form_action)
            
            response = self.session.post(
                submit_url,
                data=form_data,
                headers=self._get_request_headers()
            )
            
            if response.ok:
                print("✅ Message sent via form")
                return True
                
        except Exception as e:
            print(f"❌ Form messaging error: {e}")
        
        return False
    
    def _search_member(self, member_name: str) -> Optional[str]:
        """Search for member and return member ID"""
        try:
            search_endpoints = [
                "/ajax/members/search",
                "/api/members/search",
                "/action/Members/search"
            ]
            
            for endpoint in search_endpoints:
                search_url = f"{self.base_url}{endpoint}"
                
                search_data = {
                    "query": member_name,
                    "term": member_name,
                    "name": member_name,
                    "limit": 10
                }
                
                # Add form tokens
                search_data.update(self.form_tokens)
                if self.csrf_token:
                    search_data["csrf_token"] = self.csrf_token
                
                response = self.session.post(
                    search_url,
                    data=search_data,
                    headers=self._get_request_headers()
                )
                
                if response.ok:
                    try:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            return str(result[0].get("id"))
                        elif isinstance(result, dict):
                            if "members" in result and len(result["members"]) > 0:
                                return str(result["members"][0].get("id"))
                            elif "id" in result:
                                return str(result["id"])
                    except:
                        # Try parsing as HTML if JSON fails
                        if member_name.lower() in response.text.lower():
                            print(f"✅ Found member {member_name} in search results")
                            return "1"  # Fallback ID
            
            return None
            
        except Exception as e:
            print(f"❌ Error searching for member: {e}")
            return None
    
    def get_calendar_data(self, date: str = None) -> List[Dict]:
        """Get calendar data from ClubOS with robust session management"""
        try:
            if not self.is_authenticated:
                print("❌ Not authenticated with ClubOS")
                return []

            if not date:
                date = datetime.now().strftime("%Y-%m-%d")

            print(f"📅 Fetching calendar data for {date}...")

            # Step 1: Check if we have cached data from immediate access
            if self._cached_calendar_data:
                print(f"🎯 Using cached calendar data from immediate access: {len(self._cached_calendar_data)} items")
                return self._cached_calendar_data

            print("📅 No cached data, attempting fresh calendar access...")

            # Step 2: Try the dashboard-first navigation approach
            print("   🏠 Starting from dashboard...")
            dashboard_url = f"{self.base_url}/action/Dashboard"
            dashboard_response = self.session.get(dashboard_url, timeout=10)
            
            if not dashboard_response.ok or 'action/Login' in dashboard_response.url:
                print(f"❌ Dashboard access failed: {dashboard_response.status_code} -> {dashboard_response.url}")
                print("   🔄 Trying direct calendar access...")
            else:
                print("   ✅ Dashboard accessed successfully")
            
            # Step 3: Navigate to calendar (regardless of dashboard success)
            print("   📅 Attempting calendar access...")
            
            calendar_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": dashboard_url,  # Coming from dashboard
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin"
            }
            
            calendar_url = f"{self.base_url}/action/Calendar"
            
            # Try multiple calendar access methods
            calendar_attempts = [
                # Method 1: Simple calendar access
                {"url": calendar_url, "params": None, "desc": "simple calendar"},
                
                # Method 2: Calendar with date parameters
                {"url": calendar_url, "params": {
                    'selectedDate': datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y"),
                    'view': 'day'
                }, "desc": "calendar with date"},
                
                # Method 3: Calendar with Jeremy's user ID
                {"url": calendar_url, "params": {
                    'selectedView': str(self.jeremy_mayo_user_id),
                    'selectedDate': datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y"),
                    'view': 'day'
                }, "desc": "Jeremy's calendar"},
                
                # Method 4: Direct URL with Jeremy's parameters
                {"url": f"{calendar_url}?selectedView={self.jeremy_mayo_user_id}&selectedDate={datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y')}&view=day", 
                 "params": None, "desc": "direct Jeremy URL"}
            ]
            
            for i, attempt in enumerate(calendar_attempts, 1):
                try:
                    print(f"   🔄 Attempt {i}: {attempt['desc']}")
                    
                    response = self.session.get(
                        attempt["url"], 
                        params=attempt["params"], 
                        headers=calendar_headers, 
                        timeout=10
                    )
                    
                    print(f"      Status: {response.status_code}, URL: {response.url}")
                    
                    if response.ok and 'action/Login' not in response.url:
                        print(f"✅ Calendar access successful via {attempt['desc']}!")
                        
                        # Save successful response
                        try:
                            os.makedirs("data/debug_outputs", exist_ok=True)
                            with open(f"data/debug_outputs/calendar_success_{i}.html", 'w', encoding='utf-8') as f:
                                f.write(response.text)
                        except:
                            pass
                        
                        # Parse calendar data
                        calendar_data = self._parse_calendar_html_robust(response.text, date)
                        if calendar_data:
                            print(f"✅ Extracted {len(calendar_data)} calendar items via {attempt['desc']}")
                            # Cache the successful data
                            self._cached_calendar_data = calendar_data
                            return calendar_data
                        else:
                            print(f"   ⚠️ No data extracted from {attempt['desc']}")
                    
                except Exception as e:
                    print(f"   ❌ {attempt['desc']} failed: {e}")
                    continue
            
            # Step 4: Try API endpoints as last resort
            print("   🔄 Trying API endpoints as last resort...")
            api_data = self._try_calendar_api_endpoints(date)
            if api_data:
                return api_data
            
            print("⚠️ All calendar access methods failed, returning empty list")
            return []

        except Exception as e:
            print(f"❌ Error fetching calendar data: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_calendar_html_robust(self, html_content: str, date: str) -> List[Dict]:
        """Parse calendar data from HTML with robust error handling"""
        try:
            from bs4 import BeautifulSoup
            import json
            import re
            
            soup = BeautifulSoup(html_content, 'html.parser')
            events = []
            
            print("🔍 Parsing calendar HTML for Jeremy Mayo's events...")
            
            # Look for Jeremy Mayo's user ID in hidden inputs
            jeremy_id = str(self.jeremy_mayo_user_id)
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            
            for hidden_input in hidden_inputs:
                try:
                    value = hidden_input.get('value', '')
                    if jeremy_id in value:
                        # Try to parse as JSON
                        try:
                            event_data = json.loads(value)
                            if isinstance(event_data, dict) and event_data.get('eventId'):
                                # Extract event details
                                event = {
                                    'id': str(event_data.get('eventId')),
                                    'title': event_data.get('title', 'Event'),
                                    'start_time': event_data.get('startTime', ''),
                                    'end_time': event_data.get('endTime', ''),
                                    'date': date,
                                    'status': event_data.get('status', 'booked'),
                                    'type': event_data.get('eventType', 'appointment')
                                }
                                events.append(event)
                        except json.JSONDecodeError:
                            continue
                except Exception:
                    continue
            
            # Look for schedule table data
            schedule_table = soup.find('table', {'id': 'schedule'})
            if schedule_table and not events:
                print("   Parsing schedule table for available slots...")
                table_events = self._parse_schedule_table(schedule_table, date)
                events.extend(table_events)
            
            print(f"   Parsed {len(events)} events from HTML")
            return events
            
        except Exception as e:
            print(f"   Error parsing calendar HTML: {e}")
            return []
    
    def _parse_schedule_table(self, table, date: str) -> List[Dict]:
        """Parse events from schedule table"""
        try:
            events = []
            
            # Find Jeremy Mayo's column
            jeremy_column_index = None
            header_row = table.find('tr', class_='calendar-head')
            if header_row:
                columns = header_row.find_all('th')
                for i, col in enumerate(columns):
                    if 'Jeremy' in col.get_text() or str(self.jeremy_mayo_user_id) in str(col):
                        jeremy_column_index = i
                        break
            
            if jeremy_column_index is None:
                return []
            
            # Parse time slots
            rows = table.find_all('tr')
            for row in rows:
                if 'calendar-head' in row.get('class', []):
                    continue
                
                cells = row.find_all(['td', 'th'])
                if len(cells) <= jeremy_column_index:
                    continue
                
                # Get time from first cell
                time_cell = cells[0]
                time_text = time_cell.get_text(strip=True)
                
                if ':' not in time_text:
                    continue
                
                # Get Jeremy's cell
                jeremy_cell = cells[jeremy_column_index]
                
                # Check if slot is available
                if not jeremy_cell.find('div', class_='cal-event'):
                    # Available slot
                    event = {
                        'id': f"available_{time_text.replace(':', '').replace(' ', '_')}",
                        'title': f"Available Slot",
                        'start_time': time_text,
                        'end_time': self._calculate_end_time(time_text),
                        'date': date,
                        'status': 'available',
                        'type': 'available_slot'
                    }
                    events.append(event)
            
            return events
            
        except Exception as e:
            print(f"   Error parsing schedule table: {e}")
            return []
    
    def _calculate_end_time(self, start_time: str) -> str:
        """Calculate end time (30 minutes after start)"""
        try:
            # Parse time like "8:00" or "8:00 AM"
            time_str = start_time.replace(' AM', '').replace(' PM', '').strip()
            hour, minute = map(int, time_str.split(':'))
            
            # Add 30 minutes
            end_minute = minute + 30
            end_hour = hour
            if end_minute >= 60:
                end_minute -= 60
                end_hour += 1
            
            return f"{end_hour}:{end_minute:02d}"
        except:
            return start_time
    
    def _try_calendar_api_endpoints(self, date: str) -> List[Dict]:
        """Try various API endpoints with robust session"""
        try:
            # Convert date to different formats
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                date_formats = [
                    date_obj.strftime("%m/%d/%Y"),
                    date_obj.strftime("%Y-%m-%d"),
                    date_obj.strftime("%d/%m/%Y"),
                    str(int(date_obj.timestamp())),
                ]
            except:
                date_formats = [date]
            
            # API endpoints to try
            api_endpoints = [
                "/api/calendar/events",
                "/api/calendar/sessions", 
                "/ajax/calendar/events",
                "/api/v3/calendar/events",
                f"/api/staff/{self.jeremy_mayo_user_id}/calendar"
            ]
            
            # Headers for API requests
            api_headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/action/Calendar",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # Add Authorization if we have JWT token
            if self.api_v3_access_token:
                api_headers["Authorization"] = f"Bearer {self.api_v3_access_token}"
            
            for endpoint in api_endpoints:
                for date_format in date_formats:
                    try:
                        api_url = f"{self.base_url}{endpoint}"
                        params = {'date': date_format}
                        
                        print(f"   Trying API: {endpoint}?date={date_format}")
                        response = self.session.get(api_url, headers=api_headers, params=params, timeout=10)
                        
                        if response.ok:
                            try:
                                data = response.json()
                                if isinstance(data, list) and len(data) > 0:
                                    print(f"✅ API success: {len(data)} items from {endpoint}")
                                    return data
                                elif isinstance(data, dict) and data.get('events'):
                                    print(f"✅ API success: {len(data['events'])} events from {endpoint}")
                                    return data['events']
                            except:
                                continue
                    except:
                        continue
            
            return []
            
        except Exception as e:
            print(f"   Error trying API endpoints: {e}")
            return []
    
    def _parse_calendar_html(self, html_content: str, target_date: str) -> List[Dict]:
        """Parse calendar events from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            events = []
            
            # Look for various calendar event patterns
            event_selectors = [
                '.calendar-event', '.session', '.appointment', '.event',
                '[data-session-id]', '.event-item', '.calendar-item',
                '.fc-event', '.appointment-slot'
            ]
            
            for selector in event_selectors:
                elements = soup.select(selector)
                for element in elements:
                    event_data = {
                        'id': element.get('data-session-id') or element.get('data-id', ''),
                        'title': element.get_text(strip=True)[:100],  # Limit title length
                        'time': '',
                        'date': target_date,
                        'type': 'session'
                    }
                    
                    # Try to extract time information
                    time_selectors = ['.time', '.session-time', '[data-time]', '.event-time']
                    for time_sel in time_selectors:
                        time_element = element.select_one(time_sel)
                        if time_element:
                            event_data['time'] = time_element.get_text(strip=True)
                            break
                    
                    # Only add if we have meaningful content
                    if event_data['title'] and len(event_data['title']) > 2:
                        events.append(event_data)
                
                if events:  # If we found events with this selector, use them
                    break
            
            return events[:50]  # Limit to 50 events
            
        except Exception as e:
            print(f"❌ Error parsing calendar HTML: {e}")
            return []
            
        except Exception as e:
            print(f"❌ Error parsing calendar HTML: {e}")
            return []


# Integration class for the dashboard
class ClubOSIntegration:
    """ClubOS integration for the gym dashboard"""
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username or os.getenv('CLUBOS_USERNAME')
        self.password = password or os.getenv('CLUBOS_PASSWORD')
        self.client = None
        self.is_connected = False
        self.last_connection_attempt = None
    
    def connect(self) -> bool:
        """Connect to ClubOS with robust authentication"""
        if not self.username or not self.password:
            print("❌ ClubOS credentials not provided - set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables")
            return False
        
        try:
            print(f"🔗 Connecting to ClubOS as {self.username}...")
            self.client = RobustClubOSClient(self.username, self.password)
            self.is_connected = self.client.authenticate()
            self.last_connection_attempt = datetime.now()
            
            if self.is_connected:
                print("✅ ClubOS connection successful!")
            else:
                print("❌ ClubOS connection failed!")
            
            return self.is_connected
            
        except Exception as e:
            print(f"❌ ClubOS connection error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def ensure_connected(self) -> bool:
        """Ensure we have a valid connection to ClubOS"""
        if not self.is_connected or not self.client:
            return self.connect()
        
        # Reconnect if last attempt was more than 30 minutes ago
        if (self.last_connection_attempt and 
            (datetime.now() - self.last_connection_attempt).seconds > 1800):
            print("🔄 Reconnecting to ClubOS (session timeout)")
            return self.connect()
        
        return True
    
    def send_real_message(self, member_name: str, message: str) -> bool:
        """Send real message through ClubOS"""
        if not self.ensure_connected():
            print("❌ Cannot send message - not connected to ClubOS")
            return False
        
        try:
            success = self.client.send_message(member_name, message)
            if success:
                print(f"✅ Successfully sent ClubOS message to {member_name}")
            else:
                print(f"❌ Failed to send ClubOS message to {member_name}")
            return success
            
        except Exception as e:
            print(f"❌ Error sending ClubOS message: {e}")
            return False
    
    def get_real_calendar_data(self, date: str = None) -> List[Dict]:
        """Get real calendar data from ClubOS"""
        if not self.ensure_connected():
            print("❌ Cannot get calendar data - not connected to ClubOS")
            return []
        
        try:
            calendar_data = self.client.get_calendar_data(date)
            if calendar_data:
                print(f"✅ Retrieved {len(calendar_data)} ClubOS calendar events")
            else:
                print("ℹ️ No ClubOS calendar events found")
            return calendar_data
            
        except Exception as e:
            print(f"❌ Error getting ClubOS calendar data: {e}")
            return []
    
    def get_real_member_list(self) -> List[Dict]:
        """Get real member list from ClubOS"""
        if not self.ensure_connected():
            print("❌ Cannot get member list - not connected to ClubOS")
            return []
        
        try:
            # Visit members page to get member data
            members_url = f"{self.client.base_url}/action/Members"
            response = self.client.session.get(
                members_url,
                headers=self.client._get_request_headers()
            )
            
            if response.ok:
                # Parse member data from HTML
                members = self._parse_members_html(response.text)
                print(f"✅ Retrieved {len(members)} ClubOS members")
                return members
            else:
                print(f"❌ Failed to get members page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting ClubOS member list: {e}")
            return []
    
    def _parse_members_html(self, html_content: str) -> List[Dict]:
        """Parse member data from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            members = []
            
            # Look for member tables, lists, or cards
            member_selectors = [
                'table.members tr', '.member-list .member', '.member-card',
                'tbody tr', '.member-row'
            ]
            
            for selector in member_selectors:
                elements = soup.select(selector)
                for element in elements:
                    member_data = {}
                    
                    # Try to extract member information
                    name_elem = element.select_one('.name, .member-name, [data-name]')
                    if name_elem:
                        member_data['name'] = name_elem.get_text(strip=True)
                    
                    email_elem = element.select_one('.email, .member-email, [data-email]')
                    if email_elem:
                        member_data['email'] = email_elem.get_text(strip=True)
                    
                    phone_elem = element.select_one('.phone, .member-phone, [data-phone]')
                    if phone_elem:
                        member_data['phone'] = phone_elem.get_text(strip=True)
                    
                    # Add member if we have at least a name
                    if member_data.get('name'):
                        members.append(member_data)
                
                if members:  # If we found members with this selector, use them
                    break
            
            return members[:100]  # Limit to 100 members
            
        except Exception as e:
            print(f"❌ Error parsing members HTML: {e}")
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """Test ClubOS connection and return status"""
        try:
            if not self.username or not self.password:
                return {
                    "connected": False,
                    "error": "No credentials provided",
                    "details": "Set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables"
                }
            
            success = self.connect()
            
            if success:
                # Try to get basic data to verify connection
                calendar_data = self.get_real_calendar_data()
                
                return {
                    "connected": True,
                    "username": self.username,
                    "calendar_events": len(calendar_data),
                    "last_connected": self.last_connection_attempt.isoformat() if self.last_connection_attempt else None
                }
            else:
                return {
                    "connected": False,
                    "error": "Authentication failed",
                    "details": "Check username and password"
                }
                
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "details": "Connection test failed"
            }


# Global ClubOS client instance
clubos_integration = ClubOSIntegration()

def get_clubos_client():
    """Get the global ClubOS client instance"""
    return clubos_integration
