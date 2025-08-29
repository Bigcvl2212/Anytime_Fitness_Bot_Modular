"""
ClubOS Web API Client Service
Handles authentication and API calls to ClubOS web interface to replace Selenium automation.
"""

import time
import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse

from config.constants import CLUBOS_LOGIN_URL, CLUBOS_CALENDAR_URL
from utils.debug_helpers import debug_page_state


class ClubOSAPIAuthentication:
    """Handles ClubOS web API authentication"""
    
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.access_token = None
        self.is_authenticated = False
        self.login_url = CLUBOS_LOGIN_URL
        self.base_url = "https://anytime.club-os.com"
        
        # Set default headers to mimic browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with ClubOS web interface using the working HAR sequence
        
        Args:
            username: ClubOS username
            password: ClubOS password
            
        Returns:
            bool: True if login successful, False otherwise
        """
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
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            
            print("   ✅ Extracted form fields successfully")
            
            # Step 2: Submit login form with correct field names (working pattern)
            login_data = {
                'login': 'Submit',
                'username': username,
                'password': password,
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
            self.is_authenticated = True
            
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
    
    def _extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Extract CSRF token from HTML content"""
        try:
            # Look for CSRF token in meta tags
            csrf_patterns = [
                r'<meta name="csrf-token" content="([^"]+)"',
                r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"',
                r'<input[^>]*name="_token"[^>]*value="([^"]+)"',
                r'window\.csrfToken\s*=\s*["\']([^"\']+)["\']',
                r'data-csrf="([^"]+)"'
            ]
            
            for pattern in csrf_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"   ⚠️ Error extracting CSRF token: {e}")
            return None
    
    def _extract_access_token(self, html_content: str) -> Optional[str]:
        """Extract access token from authenticated page"""
        try:
            # Look for JWT tokens or access tokens
            token_patterns = [
                r'window\.accessToken\s*=\s*["\']([^"\']+)["\']',
                r'window\.token\s*=\s*["\']([^"\']+)["\']',
                r'data-token="([^"]+)"',
                r'Bearer\s+([A-Za-z0-9\-._~+/]+=*)',
                r'eyJ[A-Za-z0-9\-._~+/]+=*'  # JWT pattern
            ]
            
            for pattern in token_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"   ⚠️ Error extracting access token: {e}")
            return None
    
    def _is_login_successful(self, response: requests.Response) -> bool:
        """Check if login was successful"""
        try:
            # Check for redirect to dashboard or calendar
            success_urls = ["dashboard", "calendar", "action/dashboard", "action/calendar"]
            for url_part in success_urls:
                if url_part.lower() in response.url.lower():
                    return True
            
            # Check for authentication cookies
            has_session = any(cookie.name == 'JSESSIONID' for cookie in self.session.cookies)
            has_api_token = any(cookie.name == 'apiV3AccessToken' for cookie in self.session.cookies)
            
            if has_session or has_api_token:
                return True
            
            # Check for authentication indicators in response
            success_indicators = [
                "dashboard",
                "calendar", 
                "logout",
                "user_id",
                "session_id",
                "welcome",
                "apiV3AccessToken"
            ]
            
            response_text_lower = response.text.lower()
            for indicator in success_indicators:
                if indicator.lower() in response_text_lower:
                    return True
            
            # Check for login failure indicators
            error_indicators = [
                "invalid credentials",
                "login failed",
                "authentication error",
                "invalid username or password",
                "incorrect username",
                "incorrect password"
            ]
            
            for error in error_indicators:
                if error.lower() in response_text_lower:
                    return False
            
            # If response is large (>50KB) and we have a session cookie, assume success
            if len(response.text) > 50000 and has_session:
                return True
            
            # If no clear indicators, check status code
            return response.status_code == 200
            
        except Exception as e:
            print(f"   ⚠️ Error checking login status: {e}")
            return False
    
    def _capture_additional_tokens(self):
        """
        Capture additional required tokens and cookies for full ClubOS API access
        This method visits specific endpoints to trigger token generation
        """
        print("   🔧 Capturing additional authentication tokens...")
        
        try:
            # First, try to get to the dashboard properly by following redirects
            print("      📍 Establishing authenticated session...")
            
            # Visit dashboard first with proper headers
            dashboard_response = self.session.get(
                f"{self.base_url}/action/Dashboard/view",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin"
                },
                allow_redirects=True,
                timeout=30
            )
            
            print(f"      📊 Dashboard response: {dashboard_response.status_code} - Final URL: {dashboard_response.url}")
            
            # Check if we're actually authenticated by looking at the URL
            if "Login" in dashboard_response.url:
                print("      ❌ Still redirected to login - trying alternative authentication")
                
                # Try submitting login form again with current session
                from config.secrets_local import get_secret
                login_data = {
                    "username": get_secret('clubos-username'),
                    "password": get_secret('clubos-password'),
                    "submit": "Login"
                }
                
                reauth_response = self.session.post(
                    self.login_url,
                    data=login_data,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Referer": self.login_url
                    },
                    allow_redirects=True,
                    timeout=30
                )
                
                print(f"      🔄 Re-auth response: {reauth_response.status_code} - Final URL: {reauth_response.url}")
                
                # Update dashboard response
                if "Dashboard" in reauth_response.url or "Calendar" in reauth_response.url:
                    dashboard_response = reauth_response
                    print("      ✅ Re-authentication successful")
            
            # Extract user ID and other important values from the authenticated page
            if dashboard_response.status_code == 200 and "Login" not in dashboard_response.url:
                print("      🔍 Extracting user context from authenticated page...")
                self._extract_user_context(dashboard_response.text)
            
            # Print final cookie summary
            print("   📋 Final authentication cookies:")
            for cookie in self.session.cookies:
                if cookie.name in ['JSESSIONID', 'loggedInUserId', 'delegatedUserId', 'apiV3AccessToken', 'apiV3RefreshToken', 'apiV3IdToken']:
                    value_preview = cookie.value[:20] + "..." if len(cookie.value) > 20 else cookie.value
                    print(f"      {cookie.name}: {value_preview}")
            
        except Exception as e:
            print(f"   ❌ Error capturing additional tokens: {e}")
    
    def _extract_user_context(self, html_content: str):
        """Extract user context and set missing cookies from authenticated page"""
        try:
            import re
            
            # Look for user ID patterns in the HTML
            user_patterns = [
                r'loggedInUserId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
                r'delegatedUserId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
                r'userId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
                r'currentUser["\']?\s*[:=]\s*["\'][^"\']*userId["\']?\s*[:=]\s*["\']?(\d+)["\']?'
            ]
            
            for pattern in user_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    user_id = matches[0]
                    cookie_name = pattern.split('[')[0] if '[' in pattern else 'loggedInUserId'
                    
                    # Set the user ID cookie if we don't have it
                    existing_cookie = next((c for c in self.session.cookies if c.name == cookie_name), None)
                    if not existing_cookie:
                        self.session.cookies.set(cookie_name, user_id, domain='.club-os.com')
                        print(f"      🔑 Set {cookie_name}: {user_id}")
            
            # Look for JWT tokens in script tags or variables
            jwt_patterns = [
                r'apiV3AccessToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'accessToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'window\.token\s*=\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in jwt_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    token = matches[0]
                    if token.startswith('ey'):  # JWT tokens start with 'ey'
                        self.session.cookies.set('apiV3AccessToken', token, domain='.club-os.com')
                        self.access_token = token
                        print(f"      🔑 Extracted JWT token: {token[:20]}...")
                        break
                        
        except Exception as e:
            print(f"      ⚠️ Error extracting user context: {e}")
    
    def _extract_jwt_tokens_from_html(self, html_content: str):
        """Extract JWT tokens from HTML content and set them as cookies"""
        try:
            import re
            
            # Patterns to find JWT tokens in JavaScript
            jwt_patterns = [
                r'apiV3AccessToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'apiV3RefreshToken["\']?\s*[:=]\s*["\']([^"\']+)["\']', 
                r'apiV3IdToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'loggedInUserId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
                r'delegatedUserId["\']?\s*[:=]\s*["\']?(\d+)["\']?'
            ]
            
            for pattern in jwt_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    token_name = pattern.split('[')[0]  # Extract token name from pattern
                    token_value = matches[0]
                    
                    # Set as cookie
                    self.session.cookies.set(token_name, token_value, domain='.club-os.com')
                    print(f"      🔑 Extracted {token_name}: {token_value[:20]}...")
                    
        except Exception as e:
            print(f"      ⚠️ Error extracting JWT tokens: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in self.session.cookies.items()]),
            "Referer": self.base_url,
            "Origin": self.base_url
        }
        # Always use apiV3AccessToken as Bearer token if present
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
        return headers
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self.is_authenticated


class ClubOSAPIClient:
    """ClubOS web API client for replacing Selenium automation"""
    
    def __init__(self, auth_service: ClubOSAPIAuthentication):
        self.auth = auth_service
        self.base_url = "https://anytime.club-os.com"
        self.session = auth_service.session
        
        # API endpoints (to be discovered)
        self.endpoints = {
            "calendar": {
                "sessions": "/api/calendar/sessions",
                "create": "/api/calendar/sessions/create",
                "update": "/api/calendar/sessions/{id}/update",
                "delete": "/api/calendar/sessions/{id}/delete"
            },
            "members": {
                "search": "/api/members/search",
                "details": "/api/members/{id}",
                "agreements": "/api/members/{id}/agreements"
            },
            "messages": {
                "send": "/api/messages/send",
                "history": "/api/messages/history",
                "templates": "/api/messages/templates"
            },
            "training": {
                "sessions": "/api/training/sessions",
                "clients": "/api/training/clients",
                "packages": "/api/training/packages"
            }
        }
    
    def discover_api_endpoints(self) -> Dict[str, Any]:
        """
        Discover actual API endpoints by analyzing network traffic
        
        Returns:
            Dict containing discovered endpoints
        """
        print("🔍 Discovering ClubOS API endpoints...")
        
        discovered_endpoints = {}
        
        try:
            # Visit key pages and capture AJAX requests
            pages_to_analyze = [
                "/action/Calendar",
                "/action/Dashboard/messages", 
                "/action/Dashboard/PersonalTraining",
                "/action/Dashboard/view"
            ]
            
            for page in pages_to_analyze:
                print(f"   📄 Analyzing {page}...")
                page_url = urljoin(self.base_url, page)
                
                response = self.session.get(page_url, headers=self.auth.get_headers())
                if response.ok:
                    # Extract potential API endpoints from JavaScript
                    endpoints = self._extract_endpoints_from_js(response.text)
                    if endpoints:
                        discovered_endpoints[page] = endpoints
                        print(f"   ✅ Found {len(endpoints)} endpoints in {page}")
                
                time.sleep(1)  # Rate limiting
            
            return discovered_endpoints
            
        except Exception as e:
            print(f"   ❌ Error discovering endpoints: {e}")
            return {}
    
    def _extract_endpoints_from_js(self, html_content: str) -> List[str]:
        """Extract API endpoints from JavaScript code"""
        endpoints = []
        
        try:
            # Look for AJAX URLs in JavaScript
            patterns = [
                r'url:\s*["\']([^"\']+/api/[^"\']+)["\']',
                r'fetch\(["\']([^"\']+/api/[^"\']+)["\']',
                r'\.ajax\([^)]*url:\s*["\']([^"\']+/api/[^"\']+)["\']',
                r'axios\.(get|post|put|delete)\(["\']([^"\']+/api/[^"\']+)["\']',
                r'["\'](/api/[^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        endpoints.extend(match)
                    else:
                        endpoints.append(match)
            
            return list(set(endpoints))  # Remove duplicates
            
        except Exception as e:
            print(f"   ⚠️ Error extracting endpoints: {e}")
            return []
    
    def get_calendar_sessions(self, date: str = None) -> List[Dict]:
        """
        Get calendar sessions for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format, defaults to today
            
        Returns:
            List of calendar sessions
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"📅 Fetching calendar sessions for {date}...")
        
        try:
            # Try discovered API endpoint first
            if "calendar" in self.endpoints:
                api_url = urljoin(self.base_url, self.endpoints["calendar"]["sessions"])
                params = {"date": date}
                
                response = self.session.get(api_url, params=params, headers=self.auth.get_headers())
                
                if response.ok:
                    return response.json()
            
            # Fallback: Parse calendar page HTML
            return self._parse_calendar_page(date)
            
        except Exception as e:
            print(f"   ❌ Error fetching calendar sessions: {e}")
            return []
    
    def _parse_calendar_page(self, date: str) -> List[Dict]:
        """Parse calendar sessions from HTML page"""
        try:
            calendar_url = f"{CLUBOS_CALENDAR_URL}?date={date}"
            response = self.session.get(calendar_url, headers=self.auth.get_headers())
            
            if not response.ok:
                return []
            
            # Extract session data from HTML
            sessions = []
            
            # Look for session elements in HTML
            session_patterns = [
                r'<div[^>]*class="[^"]*session[^"]*"[^>]*>([^<]+)</div>',
                r'<tr[^>]*class="[^"]*session[^"]*"[^>]*>([^<]+)</tr>',
                r'data-session-id="([^"]+)"[^>]*>([^<]+)</'
            ]
            
            for pattern in session_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        sessions.append({
                            "id": match[0],
                            "title": match[1].strip()
                        })
                    else:
                        sessions.append({
                            "title": match.strip()
                        })
            
            return sessions
            
        except Exception as e:
            print(f"   ❌ Error parsing calendar page: {e}")
            return []
    
    def create_calendar_session(self, session_data: Dict) -> bool:
        """
        Create a new calendar session
        
        Args:
            session_data: Session details (title, date, time, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"📝 Creating calendar session: {session_data.get('title', 'Unknown')}")
        
        try:
            # Try discovered API endpoint first
            if "calendar" in self.endpoints:
                api_url = urljoin(self.base_url, self.endpoints["calendar"]["create"])
                
                response = self.session.post(
                    api_url,
                    json=session_data,
                    headers=self.auth.get_headers()
                )
                
                if response.ok:
                    print("   ✅ Session created successfully via API")
                    return True
            
            # Fallback: Use form submission
            return self._create_session_via_form(session_data)
            
        except Exception as e:
            print(f"   ❌ Error creating session: {e}")
            return False
    
    def _create_session_via_form(self, session_data: Dict) -> bool:
        """Create session using form submission (fallback method)"""
        try:
            # This would involve form submission similar to Selenium
            # Implementation depends on discovered form structure
            print("   ⚠️ Form submission not yet implemented")
            return False
            
        except Exception as e:
            print(f"   ❌ Error in form submission: {e}")
            return False
    
    def search_members(self, query: str) -> List[Dict]:
        """
        Search members by name or email
        
        Args:
            query: Search term
            
        Returns:
            List of matching members
        """
        print(f"🔍 Searching members for: {query}")
        
        try:
            # Try discovered API endpoint first
            if "members" in self.endpoints:
                api_url = urljoin(self.base_url, self.endpoints["members"]["search"])
                params = {"q": query}
                
                response = self.session.get(api_url, params=params, headers=self.auth.get_headers())
                
                if response.ok:
                    return response.json()
            
            # Fallback: Parse search results from HTML
            return self._parse_member_search_results(query)
            
        except Exception as e:
            print(f"   ❌ Error searching members: {e}")
            return []
    
    def _parse_member_search_results(self, query: str) -> List[Dict]:
        """Parse member search results from HTML"""
        try:
            # This would involve parsing search results page
            # Implementation depends on discovered page structure
            print("   ⚠️ HTML parsing not yet implemented")
            return []
            
        except Exception as e:
            print(f"   ❌ Error parsing search results: {e}")
            return []
    
    def send_message(self, member_id: str, message: str, message_type: str = "text") -> bool:
        """
        Send message to member
        
        Args:
            member_id: Member ID
            message: Message content
            message_type: Type of message (text, email, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"💬 Sending {message_type} message to member {member_id}")
        
        try:
            # Try discovered API endpoint first
            if "messages" in self.endpoints:
                api_url = urljoin(self.base_url, self.endpoints["messages"]["send"])
                
                message_data = {
                    "member_id": member_id,
                    "message": message,
                    "type": message_type
                }
                
                response = self.session.post(
                    api_url,
                    json=message_data,
                    headers=self.auth.get_headers()
                )
                
                if response.ok:
                    print("   ✅ Message sent successfully via API")
                    return True
            
            # Fallback: Use form submission
            return self._send_message_via_form(member_id, message, message_type)
            
        except Exception as e:
            print(f"   ❌ Error sending message: {e}")
            return False
    
    def _send_message_via_form(self, member_id: str, message: str, message_type: str) -> bool:
        """Send message using form submission (working implementation)"""
        try:
            endpoint = "/action/Dashboard/messages"
            headers = self.auth.get_headers()
            message_data = {
                "memberId": member_id,
                "messageType": message_type,
                "messageText": message,
                "sendMethod": "sms" if message_type == "text" else "email"
            }
            
            response = self.auth.session.post(
                f"{self.base_url}{endpoint}",
                data=message_data,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            if response.ok:
                print("   ✅ Message sent successfully via form submission")
                return True
            else:
                print(f"   ❌ Message send failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"   ❌ Error in form submission: {e}")
            return False


def create_clubos_api_client(username: str, password: str) -> Optional[ClubOSAPIClient]:
    """
    Create and authenticate ClubOS API client
    
    Args:
        username: ClubOS username
        password: ClubOS password
        
    Returns:
        ClubOSAPIClient instance if authentication successful, None otherwise
    """
    try:
        auth_service = ClubOSAPIAuthentication()
        
        if auth_service.login(username, password):
            client = ClubOSAPIClient(auth_service)
            
            # Discover API endpoints
            discovered_endpoints = client.discover_api_endpoints()
            if discovered_endpoints:
                print(f"✅ Discovered {len(discovered_endpoints)} API endpoint groups")
            
            return client
        else:
            print("❌ Failed to authenticate with ClubOS")
            return None
            
    except Exception as e:
        print(f"❌ Error creating ClubOS API client: {e}")
        return None 