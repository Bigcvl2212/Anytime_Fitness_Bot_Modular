#!/usr/bin/env python3
"""
Reverse engineer ClubOS API endpoints to make messaging work
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from bs4 import BeautifulSoup
from config.secrets_local import get_secret
import re
import json
import time

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"
SMS_MESSAGE = "API reverse engineering test - this WILL work!"
EMAIL_MESSAGE = "API reverse engineering email test - this WILL work!"

class ClubOSAPIReverseEngineer:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.csrf_token = None
        self.auth_token = None
        self.session_data = {}
        
        # Set comprehensive headers to mimic real browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })

    def login(self, username, password):
        """Login and capture all session data"""
        print("🔐 Starting comprehensive login analysis...")
        
        # Step 1: Get login page and extract all tokens
        login_page_url = f"{self.base_url}/action/Login"
        print(f"   📄 Loading login page: {login_page_url}")
        
        login_page = self.session.get(login_page_url)
        print(f"   Status: {login_page.status_code}")
        
        soup = BeautifulSoup(login_page.text, 'html.parser')
        
        # Find the login form and extract its action (with jsessionid)
        login_form = soup.find('form', {'id': 'loginForm'})
        if not login_form:
            print("❌ Could not find login form!")
            return False
        form_action = login_form.get('action')
        if not form_action.startswith('http'):
            form_action = f"{self.base_url}{form_action}"
        print(f"   📝 Using form action URL: {form_action}")
        
        # Extract all input fields from the form
        login_data = {}
        for inp in login_form.find_all('input'):
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                login_data[name] = value
        # Overwrite with real username/password
        login_data['username'] = username
        login_data['password'] = password
        
        print(f"   📤 Submitting login with data: {login_data}")
        
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.base_url,
            "Referer": login_page_url
        })
        
        login_response = self.session.post(form_action, data=login_data, allow_redirects=False)
        print(f"   📥 Login response: {login_response.status_code}")
        
        # Handle redirect to dashboard
        if login_response.status_code in [301, 302, 303, 307, 308]:
            redirect_location = login_response.headers.get('Location', '')
            if redirect_location.startswith('/'):
                redirect_url = f"{self.base_url}{redirect_location}"
            else:
                redirect_url = redirect_location
            final_response = self.session.get(redirect_url)
            print(f"   📍 Final URL: {final_response.url}")
            if "Dashboard" in final_response.url or "dashboard" in final_response.url:
                print("   ✅ Login successful!")
                return True
            else:
                print(f"   ❌ Login failed. Final URL: {final_response.url}")
                return False
        else:
            print(f"   ❌ Unexpected response code: {login_response.status_code}")
            return False

    def analyze_dashboard(self):
        """Analyze dashboard for messaging-related tokens and endpoints"""
        print("\n📊 Analyzing dashboard for messaging data...")
        
        dashboard_url = f"{self.base_url}/action/Dashboard/view"
        dashboard_response = self.session.get(dashboard_url)
        
        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        
        # Look for messaging-related forms or AJAX endpoints
        forms = soup.find_all('form')
        for form in forms:
            action = form.get('action', '')
            if 'message' in action.lower() or 'follow' in action.lower():
                print(f"   📝 Found messaging form: {action}")
                
                # Extract all form inputs
                inputs = form.find_all('input')
                for inp in inputs:
                    name = inp.get('name')
                    value = inp.get('value')
                    if name and value:
                        print(f"      🔑 Form field {name}: {value[:20]}...")
                        self.session_data[name] = value
        
        # Look for AJAX endpoints in scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for API endpoints
                endpoint_matches = re.findall(r'["\'](/action/[^"\']+)["\']', script.string)
                for endpoint in endpoint_matches:
                    if 'message' in endpoint.lower() or 'follow' in endpoint.lower():
                        print(f"   🎯 Found messaging endpoint: {endpoint}")
        
        return True

    def get_member_profile_data(self, member_id):
        """Get member profile page and extract all messaging-related data"""
        print(f"\n👤 Analyzing member profile for {member_id}...")
        
        profile_url = f"{self.base_url}/action/Dashboard/member/{member_id}"
        profile_response = self.session.get(profile_url)
        
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # Look for message forms or buttons
        message_buttons = soup.find_all('a', {'data-original-title': 'Send Message'})
        for button in message_buttons:
            print(f"   📤 Found send message button: {button.get('href', 'No href')}")
        
        # Look for member-specific tokens or data
        member_data = {}
        
        # Extract any hidden inputs that might be member-specific
        inputs = soup.find_all('input', type='hidden')
        for inp in inputs:
            name = inp.get('name', '')
            value = inp.get('value', '')
            if name and value:
                member_data[name] = value
                print(f"   🔑 Member data {name}: {value[:20]}...")
        
        # Look for member-specific JavaScript variables
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and member_id in script.string:
                # Extract any variables that mention the member ID
                var_matches = re.findall(rf'(\w+)\s*[:=]\s*["\']?{member_id}["\']?', script.string)
                for var_name in var_matches:
                    print(f"   🎯 Found member variable: {var_name} = {member_id}")
                    member_data[var_name] = member_id
        
        self.session_data.update(member_data)
        return member_data

    def extract_modal_fields(self, member_id):
        """Extract hidden fields and user info from the member profile page/modal."""
        profile_url = f"{self.base_url}/action/Dashboard/member/{member_id}"
        profile_response = self.session.get(profile_url)
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        modal_fields = {}
        # Extract all hidden inputs
        for inp in soup.find_all('input', type='hidden'):
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                modal_fields[name] = value
        # Extract user info if present
        # You may need to parse more deeply for clubId, clubLocationId, account IDs, etc.
        # For now, set placeholders
        modal_fields['followUpUser.firstName'] = "Jeremy"
        modal_fields['followUpUser.lastName'] = "Mayo"
        modal_fields['followUpUser.email'] = "mayo.jeremy2212@gmail.com"
        modal_fields['followUpUser.mobilePhone'] = "+1 (715) 586-8669"
        modal_fields['followUpUser.role.id'] = "7"
        modal_fields['followUpUser.clubId'] = modal_fields.get('clubId', "291")
        modal_fields['followUpUser.clubLocationId'] = modal_fields.get('clubLocationId', "1444")
        modal_fields['memberStudioSalesDefaultAccount'] = modal_fields.get('memberStudioSalesDefaultAccount', "185095557")
        modal_fields['memberStudioSupportDefaultAccount'] = modal_fields.get('memberStudioSupportDefaultAccount', "185095557")
        modal_fields['ptSalesDefaultAccount'] = modal_fields.get('ptSalesDefaultAccount', "185095557")
        modal_fields['ptSupportDefaultAccount'] = modal_fields.get('ptSupportDefaultAccount', "185095557")
        return modal_fields

    def send_sms(self, member_id, delegated_user_id, message, bearer_token):
        url = f"{self.base_url}/action/FollowUp/save"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/action/Dashboard/view",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
        }
        modal_fields = self.extract_modal_fields(member_id)
        payload = {
            "followUpStatus": "1",
            "followUpType": "3",
            "followUpSequence": "",
            "memberSalesFollowUpStatus": "18",
            "followUpLog.id": "",
            "followUpLog.tfoUserId": delegated_user_id,
            "followUpLog.outcome": "2",
            "emailSubject": "Jeremy Mayo has sent you a message",
            "emailMessage": "<p>Type message here...</p>",
            "textMessage": message,
            "event.id": "",
            "event.startTime": "",
            "event.createdFor.tfoUserId": member_id,
            "event.eventType": "ORIENTATION",
            "startTimeSlotId": "",
            "duration": "2",
            "event.remindAttendeesMins": "120",
            "followUpLog.reason": "",
            "followUpOutcomeNotes": "",
            "followUpLog.followUpWithOrig": "",
            "followUpLog.followUpWith": "",
            "followUpLog.followUpDate": "",
            "followUpUser.tfoUserId": delegated_user_id,
            "followUpUser.role.id": modal_fields['followUpUser.role.id'],
            "followUpUser.clubId": modal_fields['followUpUser.clubId'],
            "followUpUser.clubLocationId": modal_fields['followUpUser.clubLocationId'],
            "followUpLog.followUpAction": "3",
            "memberStudioSalesDefaultAccount": modal_fields['memberStudioSalesDefaultAccount'],
            "memberStudioSupportDefaultAccount": modal_fields['memberStudioSupportDefaultAccount'],
            "ptSalesDefaultAccount": modal_fields['ptSalesDefaultAccount'],
            "ptSupportDefaultAccount": modal_fields['ptSupportDefaultAccount'],
            "followUpUser.firstName": modal_fields['followUpUser.firstName'],
            "followUpUser.lastName": modal_fields['followUpUser.lastName'],
            "followUpUser.email": modal_fields['followUpUser.email'],
            "followUpUser.mobilePhone": modal_fields['followUpUser.mobilePhone'],
            "followUpUser.homePhone": "",
            "followUpUser.workPhone": "",
            "memberId": member_id,
            "delegatedUserId": delegated_user_id,
            "loggedInUserId": member_id,
            "followUpMethod": "Text",
            "actAs": "loggedIn",
        }
        # Add all hidden modal fields (_sourcePage, __fp, etc.)
        for k, v in modal_fields.items():
            if k not in payload:
                payload[k] = v
        response = self.session.post(url, data=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return response

    def test_all_messaging_endpoints(self, member_id, message):
        """Test every possible messaging endpoint with all captured data"""
        print(f"\n🧪 Testing all messaging endpoints for member {member_id}...")
        
        # Extract delegated user ID and Bearer token from cookies
        delegated_user_id = None
        bearer_token = None
        for cookie in self.session.cookies:
            if cookie.name == "delegatedUserId":
                delegated_user_id = cookie.value
            if cookie.name == "apiV3AccessToken":
                bearer_token = cookie.value
        if not delegated_user_id:
            print("❌ Could not find delegatedUserId in cookies!")
        if not bearer_token:
            print("❌ Could not find Bearer token in cookies!")
        if delegated_user_id and bearer_token:
            print(f"🔑 Using delegatedUserId={delegated_user_id}")
            print(f"🔑 Using Bearer token (truncated)={bearer_token[:20]}...")
            response = self.send_sms(member_id, delegated_user_id, message, bearer_token)
            if response.status_code == 200 and "error" not in response.text.lower() and "something isn't right" not in response.text.lower():
                print("✅ SMS sent successfully!")
                return ["/action/FollowUp/save"]
            else:
                print("❌ SMS send failed. Response:")
                print(response.text)
        else:
            print("❌ Missing required authentication for SMS send.")
        return []

def reverse_engineer_clubos_api():
    """Main function to reverse engineer ClubOS messaging API"""
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    print("🔍 REVERSE ENGINEERING CLUBOS MESSAGING API")
    print("=" * 60)
    
    engineer = ClubOSAPIReverseEngineer()
    
    # Step 1: Login and capture all tokens
    if not engineer.login(username, password):
        print("❌ Login failed")
        return
    
    # Step 2: Analyze dashboard
    engineer.analyze_dashboard()
    
    # Step 3: Get member profile data
    engineer.get_member_profile_data(MEMBER_ID)
    
    # Step 4: Test all endpoints
    successful_endpoints = engineer.test_all_messaging_endpoints(MEMBER_ID, SMS_MESSAGE)
    
    # Summary
    print(f"\n📊 REVERSE ENGINEERING RESULTS")
    print("=" * 40)
    print(f"Total session data captured: {len(engineer.session_data)} items")
    print(f"Successful endpoints: {len(successful_endpoints)}")
    
    for endpoint in successful_endpoints:
        print(f"   ✅ {endpoint}")
    
    if successful_endpoints:
        print(f"\n🎉 SUCCESS! Found {len(successful_endpoints)} working endpoint(s)")
        print("🔧 Ready to implement working API solution")
    else:
        print(f"\n⚠️ No endpoints worked with current approach")
        print("🔍 Need to capture more authentication data or try different approach")

if __name__ == "__main__":
    reverse_engineer_clubos_api()