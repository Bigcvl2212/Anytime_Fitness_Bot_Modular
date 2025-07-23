#!/usr/bin/env python3
"""
Proper ClubOS API authentication solution using the patterns from the codebase
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from urllib.parse import urljoin
from config.secrets_local import get_secret
import time
import re

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "API proper auth SMS test - this should work!"
EMAIL_MESSAGE = "API proper auth email test - this should work!"

class ClubOSProperAuth:
    """Proper ClubOS API authentication using codebase patterns"""
    
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.access_token = None
        self.bearer_token = None
        self.is_authenticated = False
        self.base_url = "https://anytime.club-os.com"
        
        # Set headers to match real ClubOS browser requests from codebase
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Upgrade-Insecure-Requests": "1"
        })
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate with ClubOS using proper session management"""
        try:
            print("🔐 Attempting ClubOS proper authentication...")
            
            # Step 1: Get login page to extract CSRF token
            print("   📄 Fetching login page...")
            login_page_response = self.session.get(f"{self.base_url}/action/Login/view", timeout=30)
            
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
                f"{self.base_url}/action/Login",
                data=login_data,
                allow_redirects=True,
                timeout=30
            )
            
            # Step 3: Check if login was successful
            if self._is_login_successful(login_response):
                print("   ✅ Login successful!")
                self.is_authenticated = True
                
                # Extract API tokens from cookies
                self._extract_api_tokens()
                
                return True
            else:
                print("   ❌ Login failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def _extract_csrf_token(self, html_content: str) -> str:
        """Extract CSRF token from HTML content"""
        try:
            # Look for CSRF token in meta tags
            csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', html_content)
            if csrf_match:
                return csrf_match.group(1)
            
            # Look for CSRF token in input fields
            csrf_match = re.search(r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', html_content)
            if csrf_match:
                return csrf_match.group(1)
            
            # Look for CSRF token in script tags
            csrf_match = re.search(r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)["\']', html_content)
            if csrf_match:
                return csrf_match.group(1)
            
            return None
        except Exception as e:
            print(f"   ⚠️ Error extracting CSRF token: {e}")
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
    
    def _extract_api_tokens(self):
        """Extract API tokens from session cookies"""
        try:
            # Extract key cookies that ClubOS uses
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            api_access_token = self.session.cookies.get('apiV3AccessToken')
            api_id_token = self.session.cookies.get('apiV3IdToken')
            
            if logged_in_user_id:
                print(f"   👤 Logged in user ID: {logged_in_user_id}")
            if delegated_user_id:
                print(f"   👥 Delegated user ID: {delegated_user_id}")
            if api_access_token:
                print(f"   🔑 API Access Token found: {api_access_token[:30]}...")
                self.access_token = api_access_token
            if api_id_token:
                print(f"   🆔 API ID Token found: {api_id_token[:30]}...")
                
        except Exception as e:
            print(f"   ⚠️ Error extracting user IDs: {e}")
    
    def get_headers(self) -> dict:
        """Get authenticated headers for API requests matching real ClubOS requests"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base_url}/action/Dashboard/view",
            "Origin": self.base_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        # Include all session cookies (this is critical for ClubOS)
        if self.session.cookies:
            cookie_string = "; ".join([f"{k}={v}" for k, v in self.session.cookies.items()])
            headers["Cookie"] = cookie_string
            print(f"   🍪 Including {len(self.session.cookies)} cookies in request")
        
        # Include API tokens if available
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            print(f"   🔑 Including API access token in headers")
        
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
            headers["X-CSRF-TOKEN"] = self.csrf_token
            print(f"   🛡️ Including CSRF token in headers: {self.csrf_token[:20]}...")
        
        return headers

def send_message_api_proper_auth():
    """Send messages using proper ClubOS API authentication"""
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    try:
        print("🔐 Setting up proper ClubOS API authentication...")
        
        # Create authentication instance
        auth = ClubOSProperAuth()
        
        # Login
        if not auth.login(username, password):
            print("❌ Authentication failed")
            return
        
        print("✅ Authentication successful!")
        
        # Navigate through required pages to establish session
        print("   📊 Navigating to dashboard...")
        dashboard_response = auth.session.get(f"{auth.base_url}/action/Dashboard/view")
        time.sleep(2)
        
        print("   🔍 Navigating to search...")
        search_response = auth.session.get(f"{auth.base_url}/action/Dashboard/search")
        time.sleep(1)
        
        print(f"   👤 Navigating to {TARGET_NAME}'s profile...")
        profile_url = f"{auth.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = auth.session.get(profile_url)
        time.sleep(2)
        
        print("   ✅ Member profile loaded successfully!")
        
        # Get proper headers for API requests
        headers = auth.get_headers()
        
        results = {"sms": False, "email": False, "success": False}
        
        # Try SMS with proper authentication
        print(f"\n📤 Sending SMS to {TARGET_NAME} via proper API...")
        sms_data = {
            "memberId": MEMBER_ID,
            "message": SMS_MESSAGE,
            "messageType": "text"
        }
        
        sms_url = urljoin(auth.base_url, "/action/Api/send-message")
        sms_response = auth.session.post(sms_url, data=sms_data, headers=headers)
        
        print(f"   🔍 SMS API Response:")
        print(f"      Status: {sms_response.status_code}")
        print(f"      Response: '{sms_response.text}'")
        
        if sms_response.status_code == 200:
            if "success" in sms_response.text.lower() or "sent" in sms_response.text.lower():
                print("   ✅ SMS sent successfully via proper API!")
                results["sms"] = True
            elif "something isn't right" in sms_response.text.lower():
                print("   ⚠️ API still returning 'Something isn't right'")
            else:
                print(f"   ⚠️ Unexpected response: {sms_response.text}")
        
        # Try Email with proper authentication
        print(f"\n📤 Sending Email to {TARGET_NAME} via proper API...")
        email_data = {
            "memberId": MEMBER_ID,
            "subject": "API Proper Auth Test",
            "message": EMAIL_MESSAGE,
            "messageType": "email"
        }
        
        email_url = urljoin(auth.base_url, "/action/Api/send-message")
        email_response = auth.session.post(email_url, data=email_data, headers=headers)
        
        print(f"   🔍 Email API Response:")
        print(f"      Status: {email_response.status_code}")
        print(f"      Response: '{email_response.text}'")
        
        if email_response.status_code == 200:
            if "success" in email_response.text.lower() or "sent" in email_response.text.lower():
                print("   ✅ Email sent successfully via proper API!")
                results["email"] = True
            elif "something isn't right" in email_response.text.lower():
                print("   ⚠️ API still returning 'Something isn't right'")
            else:
                print(f"   ⚠️ Unexpected response: {email_response.text}")
        
        # If API still doesn't work, try the profile page submission with proper auth
        if not results["sms"] and not results["email"]:
            print(f"\n🔄 Trying profile page submission with proper authentication...")
            
            # Use the exact form data that works
            form_data = {
                "memberId": MEMBER_ID,
                "textMessage": SMS_MESSAGE,
                "emailMessage": EMAIL_MESSAGE,
                "followUpOutcomeNotes": "API proper auth test sent by Gym Bot",
                "action": "send_message"
            }
            
            # Use browser-like headers for form submission
            form_headers = headers.copy()
            form_headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1"
            })
            
            form_response = auth.session.post(profile_url, data=form_data, headers=form_headers)
            
            print(f"   🔍 Form Submission Response:")
            print(f"      Status: {form_response.status_code}")
            print(f"      Response length: {len(form_response.text)} chars")
            
            if form_response.status_code == 200:
                if "success" in form_response.text.lower() or "sent" in form_response.text.lower():
                    print("   ✅ Form submission successful with proper auth!")
                    results["sms"] = True
                    results["email"] = True
                else:
                    print(f"   ⚠️ Form response: {form_response.text[:200]}...")
        
        # Summary
        results["success"] = results["sms"] or results["email"]
        
        print(f"\n📊 Proper API Authentication Results:")
        print(f"   SMS: {'✅ Success' if results['sms'] else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if results['email'] else '❌ Failed'}")
        
        if results["success"]:
            print("\n🎉 Messages sent successfully via proper API authentication!")
        else:
            print("\n⚠️ No messages were delivered via proper API authentication.")
            
    except Exception as e:
        print(f"❌ Error during proper API authentication: {e}")

if __name__ == "__main__":
    send_message_api_proper_auth() 