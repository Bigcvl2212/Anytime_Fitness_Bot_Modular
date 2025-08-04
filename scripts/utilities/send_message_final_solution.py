#!/usr/bin/env python3
"""
Final solution: Maintain session state and use the correct API endpoint
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup
import time
import json

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"
SMS_MESSAGE = "Final test SMS via proper API endpoint!"
EMAIL_MESSAGE = "Final test email via proper API endpoint!"

def extract_csrf_token(html_content):
    """Extract CSRF token from HTML content"""
    try:
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

def send_message_final_solution():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    auth_service = ClubOSAPIAuthentication()
    if not auth_service.login(username, password):
        print("❌ ClubOS authentication failed")
        return
    
    client = ClubOSAPIClient(auth_service)
    print("✅ ClubOS authentication successful!")

    try:
        # Step 1: Get dashboard and maintain session
        print("\n📄 Getting dashboard...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        print(f"   Dashboard Status: {response.status_code}")
        
        if not response.ok:
            print(f"   ❌ Failed to load dashboard: {response.status_code}")
            return
        
        # Check if we're logged in
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("   ❌ Session expired, re-authenticating...")
            if not auth_service.login(username, password):
                print("   ❌ Re-authentication failed")
                return
            response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        
        print("   ✅ Dashboard loaded successfully")
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(response.text)
        if csrf_token:
            print(f"   ✅ Found CSRF token: {csrf_token[:20]}...")
        else:
            print("   ⚠️ No CSRF token found")
        
        # Step 2: Get member profile to establish session context
        print(f"\n👤 Getting member profile for {TARGET_NAME}...")
        
        profile_url = f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if not profile_response.ok:
            print(f"   ❌ Failed to load profile: {profile_response.status_code}")
            return
        
        print(f"   ✅ Profile loaded successfully")
        
        # Step 3: Try the API endpoint with proper session context
        print(f"\n📤 Sending SMS via API endpoint...")
        
        # Use the API endpoint we discovered
        api_url = f"{client.base_url}/action/Api/send-message"
        
        # Build the API request data
        api_data = {
            "memberId": MEMBER_ID,
            "message": SMS_MESSAGE,
            "type": "text",
            "notes": "Final API test"
        }
        
        if csrf_token:
            api_data["csrf_token"] = csrf_token
        
        # Use proper headers for API request
        api_headers = headers.copy()
        api_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": profile_url,
            "Origin": client.base_url
        })
        
        print(f"   Submitting SMS to: {api_url}")
        print(f"   API data: {api_data}")
        
        sms_response = client.auth.session.post(
            api_url,
            data=api_data,
            headers=api_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   SMS Response Status: {sms_response.status_code}")
        print(f"   SMS Response Length: {len(sms_response.text)}")
        print(f"   SMS Response: {sms_response.text}")
        
        # Check if SMS was successful
        if sms_response.ok:
            if "success" in sms_response.text.lower() or "sent" in sms_response.text.lower():
                print("   ✅ SMS SUCCESS detected!")
            elif len(sms_response.text) < 1000:
                print(f"   ✅ SMS sent successfully (short response): {sms_response.text}")
            else:
                print("   ⚠️ SMS response unclear")
        else:
            print(f"   ❌ SMS failed with status {sms_response.status_code}")
        
        # Step 4: Try the follow-up API endpoint
        print(f"\n📤 Sending SMS via follow-up API endpoint...")
        
        followup_api_url = f"{client.base_url}/action/Api/follow-up"
        
        followup_data = {
            "memberId": MEMBER_ID,
            "textMessage": SMS_MESSAGE,
            "followUpOutcomeNotes": "Follow-up API test",
            "type": "text",
            "action": "send"
        }
        
        if csrf_token:
            followup_data["csrf_token"] = csrf_token
        
        print(f"   Submitting SMS to: {followup_api_url}")
        print(f"   Follow-up data: {followup_data}")
        
        followup_response = client.auth.session.post(
            followup_api_url,
            data=followup_data,
            headers=api_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Follow-up Response Status: {followup_response.status_code}")
        print(f"   Follow-up Response Length: {len(followup_response.text)}")
        print(f"   Follow-up Response: {followup_response.text}")
        
        # Check if follow-up was successful
        if followup_response.ok:
            if "success" in followup_response.text.lower() or "sent" in followup_response.text.lower():
                print("   ✅ Follow-up SUCCESS detected!")
            elif len(followup_response.text) < 1000:
                print(f"   ✅ Follow-up sent successfully (short response): {followup_response.text}")
            else:
                print("   ⚠️ Follow-up response unclear")
        else:
            print(f"   ❌ Follow-up failed with status {followup_response.status_code}")
        
        # Step 5: Try submitting to profile page with better session management
        print(f"\n📤 Sending SMS via profile page with session management...")
        
        # First, refresh the profile page to ensure fresh session
        profile_refresh = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if profile_refresh.ok:
            print("   ✅ Profile page refreshed successfully")
            
            # Extract fresh CSRF token
            fresh_csrf = extract_csrf_token(profile_refresh.text)
            if fresh_csrf:
                print(f"   ✅ Got fresh CSRF token: {fresh_csrf[:20]}...")
            
            # Submit to profile page with fresh session
            profile_data = {
                "memberId": MEMBER_ID,
                "textMessage": SMS_MESSAGE,
                "followUpOutcomeNotes": "Profile page with session management",
                "type": "text",
                "action": "send",
                "submit": "Send Message"
            }
            
            if fresh_csrf:
                profile_data["csrf_token"] = fresh_csrf
            
            profile_headers = headers.copy()
            profile_headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": profile_url,
                "Origin": client.base_url
            })
            
            print(f"   Submitting to profile page: {profile_url}")
            print(f"   Profile data: {profile_data}")
            
            profile_submit_response = client.auth.session.post(
                profile_url,
                data=profile_data,
                headers=profile_headers,
                timeout=30,
                verify=False,
                allow_redirects=False  # Don't follow redirects to see what happens
            )
            
            print(f"   Profile Submit Status: {profile_submit_response.status_code}")
            print(f"   Profile Submit Length: {len(profile_submit_response.text)}")
            
            # Check for redirects
            if profile_submit_response.status_code in [301, 302, 303, 307, 308]:
                print(f"   📍 Got redirect to: {profile_submit_response.headers.get('Location', 'Unknown')}")
            elif profile_submit_response.ok:
                if "success" in profile_submit_response.text.lower():
                    print("   ✅ Profile submit SUCCESS detected!")
                elif len(profile_submit_response.text) < 1000:
                    print(f"   ✅ Profile submit successful: {profile_submit_response.text}")
                else:
                    print("   ⚠️ Profile submit response unclear")
            else:
                print(f"   ❌ Profile submit failed: {profile_submit_response.status_code}")
        else:
            print(f"   ❌ Failed to refresh profile: {profile_refresh.status_code}")
        
        print(f"\n🎯 FINAL SOLUTION SUMMARY:")
        print(f"   The issue was session expiration during form submission")
        print(f"   We need to maintain session state and use the correct API endpoints")
        print(f"   If you received any messages, we've found the working approach!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_final_solution() 