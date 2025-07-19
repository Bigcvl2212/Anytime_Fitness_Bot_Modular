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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.constants import CLUBOS_LOGIN_URL, CLUBOS_CALENDAR_URL

# Simple debug function to avoid import issues
def debug_page_state(*args, **kwargs):
    """Simple debug function placeholder"""
    pass


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
        Authenticate with ClubOS web interface
        
        Args:
            username: ClubOS username
            password: ClubOS password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            print("🔐 Attempting ClubOS web authentication...")
            
            # Step 1: Get login page to extract CSRF token
            print("   📄 Fetching login page...")
            login_page_response = self.session.get(self.login_url, timeout=30)
            
            if not login_page_response.ok:
                print(f"   ❌ Failed to load login page: {login_page_response.status_code}")
                return False
            
            # Extract CSRF token from login page
            csrf_token = self._extract_csrf_token(login_page_response.text)
            if csrf_token:
                self.csrf_token = csrf_token
                print(f"   ✅ Extracted CSRF token: {csrf_token[:20]}...")
            else:
                print("   ⚠️ No CSRF token found, proceeding without...")
            
            # Step 2: Submit login form
            print("   🔑 Submitting login credentials...")
            login_data = {
                "username": username,
                "password": password,
                "submit": "Login"
            }
            
            # Add CSRF token if available
            if self.csrf_token:
                login_data["csrf_token"] = self.csrf_token
            
            login_response = self.session.post(
                self.login_url,
                data=login_data,
                allow_redirects=True,
                timeout=30
            )
            
            # Step 3: Check if login was successful
            if self._is_login_successful(login_response):
                self.is_authenticated = True
                self.access_token = self._extract_access_token(login_response.text)
                print("   ✅ ClubOS authentication successful!")
                return True
            else:
                print("   ❌ ClubOS authentication failed")
                return False
                
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
            # Check for redirect to dashboard
            if "Dashboard" in response.url or "dashboard" in response.url.lower():
                return True
            
            # Check for authentication indicators in response
            success_indicators = [
                "Dashboard",
                "Welcome",
                "Logout",
                "user_id",
                "session_id"
            ]
            
            for indicator in success_indicators:
                if indicator.lower() in response.text.lower():
                    return True
            
            # Check for error indicators
            error_indicators = [
                "Invalid credentials",
                "Login failed",
                "Authentication error",
                "Invalid username or password"
            ]
            
            for error in error_indicators:
                if error.lower() in response.text.lower():
                    return False
            
            # If no clear indicators, assume success if we got a 200 response
            return response.status_code == 200
            
        except Exception as e:
            print(f"   ⚠️ Error checking login status: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        headers = {
            "Cookie": "; ".join([f"{k}={v}" for k, v in self.session.cookies.items()]),
            "Referer": self.base_url,
            "Origin": self.base_url
        }
        
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
        Send message to member using working ClubOS form submission
        
        Args:
            member_id: Member ID
            message: Message content
            message_type: Type of message (text, email, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"💬 Sending {message_type} message to member {member_id}")
        
        try:
            # Skip failing API endpoints and use working form submission directly
            # The /action/Api/* endpoints consistently return "Something isn't right" 
            # But /action/FollowUp/save works with proper form data
            return self._send_message_via_form(member_id, message, message_type)
            
        except Exception as e:
            print(f"   ❌ Error sending message: {e}")
            return False
    
    def _send_message_via_form(self, member_id: str, message: str, message_type: str) -> bool:
        """Send message using form submission to working ClubOS endpoints"""
        try:
            print(f"   📝 Using form submission for {message_type} message to member {member_id}")
            
            if message_type.lower() == "text":
                return self._send_text_via_form(member_id, message)
            elif message_type.lower() == "email":
                return self._send_email_via_form(member_id, message)
            else:
                print(f"   ❌ Unsupported message type: {message_type}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in form submission: {e}")
            return False
    
    def _send_text_via_form(self, member_id: str, message: str) -> bool:
        """Send SMS using ClubOS form submission to working endpoint"""
        try:
            # Use the working /action/FollowUp/save endpoint for SMS
            endpoint = "/action/FollowUp/save"
            url = f"{self.base_url}{endpoint}"
            
            # Prepare form data based on working script pattern
            form_data = {
                "followUpStatus": "1",
                "followUpType": "3", 
                "memberSalesFollowUpStatus": "6",
                "followUpLog.tfoUserId": member_id,  # Use member_id as sender for now
                "followUpLog.outcome": "3",  # 3 for SMS action
                "textMessage": message,
                "event.createdFor.tfoUserId": member_id,
                "event.eventType": "ORIENTATION",
                "duration": "2",
                "event.remindAttendeesMins": "120", 
                "followUpUser.tfoUserId": member_id,
                "followUpUser.role.id": "7",
                "followUpUser.clubId": "291",  # Default club ID
                "followUpUser.clubLocationId": "3586",  # Default location ID
                "followUpLog.followUpAction": "3",  # 3 for SMS
                "memberStudioSalesDefaultAccount": member_id,
                "memberStudioSupportDefaultAccount": member_id,
                "ptSalesDefaultAccount": member_id,
                "ptSupportDefaultAccount": member_id
            }
            
            # Prepare headers for form submission
            headers = self.auth.get_headers()
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view"
            })
            
            response = self.session.post(url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("   ✅ SMS sent successfully via form submission")
                return True
            else:
                print(f"   ❌ SMS form submission failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in SMS form submission: {e}")
            return False
    
    def _send_email_via_form(self, member_id: str, message: str, subject: str = "Message from ClubOS") -> bool:
        """Send Email using ClubOS form submission to working endpoint"""
        try:
            # Use the working /action/FollowUp/save endpoint for Email
            endpoint = "/action/FollowUp/save"
            url = f"{self.base_url}{endpoint}"
            
            # Prepare form data based on working script pattern
            form_data = {
                "followUpStatus": "1",
                "followUpType": "3",
                "memberSalesFollowUpStatus": "6", 
                "followUpLog.tfoUserId": member_id,  # Use member_id as sender for now
                "followUpLog.outcome": "2",  # 2 for Email action
                "emailSubject": subject,
                "emailMessage": f"<p>{message}</p>",  # Wrap in HTML paragraph
                "event.createdFor.tfoUserId": member_id,
                "event.eventType": "ORIENTATION",
                "duration": "2",
                "event.remindAttendeesMins": "120",
                "followUpUser.tfoUserId": member_id, 
                "followUpUser.role.id": "7",
                "followUpUser.clubId": "291",  # Default club ID
                "followUpUser.clubLocationId": "3586",  # Default location ID
                "followUpLog.followUpAction": "2",  # 2 for Email
                "memberStudioSalesDefaultAccount": member_id,
                "memberStudioSupportDefaultAccount": member_id,
                "ptSalesDefaultAccount": member_id,
                "ptSupportDefaultAccount": member_id
            }
            
            # Prepare headers for form submission
            headers = self.auth.get_headers()
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view"
            })
            
            response = self.session.post(url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("   ✅ Email sent successfully via form submission")
                return True
            else:
                print(f"   ❌ Email form submission failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in Email form submission: {e}")
            return False


    def send_message_to_member_profile(self, member_id: str, message: str, message_type: str = "text") -> bool:
        """
        Send message by submitting directly to member profile page (alternative working approach)
        
        Args:
            member_id: Member ID
            message: Message content  
            message_type: Type of message (text, email, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"👤 Sending {message_type} message to member {member_id} via profile page")
        
        try:
            # Navigate to member profile page first 
            profile_url = f"{self.base_url}/action/Dashboard/member/{member_id}"
            
            # Get the member profile page to establish context
            headers = self.auth.get_headers()
            headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view"
            })
            
            profile_response = self.session.get(profile_url, headers=headers, timeout=30)
            
            if profile_response.status_code != 200:
                print(f"   ❌ Could not access member profile: {profile_response.status_code}")
                return False
            
            print(f"   ✅ Accessed member profile page")
            
            # Submit message form directly to profile page with browser headers
            if message_type.lower() == "text":
                return self._submit_text_to_profile(member_id, message, profile_url)
            elif message_type.lower() == "email": 
                return self._submit_email_to_profile(member_id, message, profile_url)
            else:
                print(f"   ❌ Unsupported message type: {message_type}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in member profile submission: {e}")
            return False
    
    def _submit_text_to_profile(self, member_id: str, message: str, profile_url: str) -> bool:
        """Submit SMS directly to member profile page"""
        try:
            # Use form submission to member profile with SMS data
            form_data = {
                "memberId": member_id,
                "message": message,
                "messageType": "text",
                "sendMethod": "sms",
                "action": "send_message"
            }
            
            headers = self.auth.get_headers()
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": profile_url,
                "Origin": self.base_url
            })
            
            response = self.session.post(profile_url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 200 and "success" in response.text.lower():
                print("   ✅ SMS sent successfully via member profile")
                return True
            else:
                print(f"   ⚠️ Profile SMS response: {response.status_code}")
                # Even if not explicitly successful, try the working FollowUp approach as backup
                return self._send_text_via_form(member_id, message)
                
        except Exception as e:
            print(f"   ❌ Error in profile SMS submission: {e}")
            return False
    
    def _submit_email_to_profile(self, member_id: str, message: str, profile_url: str, subject: str = "Message from ClubOS") -> bool:
        """Submit Email directly to member profile page"""
        try:
            # Use form submission to member profile with Email data
            form_data = {
                "memberId": member_id,
                "subject": subject,
                "message": message,
                "messageType": "email",
                "sendMethod": "email",
                "action": "send_message"
            }
            
            headers = self.auth.get_headers()
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": profile_url,
                "Origin": self.base_url
            })
            
            response = self.session.post(profile_url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 200 and "success" in response.text.lower():
                print("   ✅ Email sent successfully via member profile")
                return True
            else:
                print(f"   ⚠️ Profile Email response: {response.status_code}")
                # Even if not explicitly successful, try the working FollowUp approach as backup
                return self._send_email_via_form(member_id, message, subject)
                
        except Exception as e:
            print(f"   ❌ Error in profile Email submission: {e}")
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