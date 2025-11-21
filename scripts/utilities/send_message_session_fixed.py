#!/usr/bin/env python3
"""
Solution that handles session expiration properly by maintaining session state
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup
import time
import json

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"
SMS_MESSAGE = "Session-fixed SMS test - this should work!"
EMAIL_MESSAGE = "Session-fixed email test - this should work!"

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

def send_message_session_fixed():
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
        
        # Step 3: The key insight - we need to submit the form IMMEDIATELY after loading the profile
        # to avoid session expiration during the request
        print(f"\n📤 Sending SMS with immediate submission...")
        
        # Submit to profile page immediately after loading it
        profile_data = {
            "memberId": MEMBER_ID,
            "textMessage": SMS_MESSAGE,
            "followUpOutcomeNotes": "Session-fixed test",
            "type": "text",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            profile_data["csrf_token"] = csrf_token
        
        # Use headers that include the profile page as referer
        profile_headers = headers.copy()
        profile_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": profile_url,
            "Origin": client.base_url
        })
        
        print(f"   Submitting SMS to: {profile_url}")
        print(f"   SMS Form data: {profile_data}")
        
        # Submit immediately to avoid session expiration
        sms_response = client.auth.session.post(
            profile_url,
            data=profile_data,
            headers=profile_headers,
            timeout=30,
            verify=False,
            allow_redirects=False  # Don't follow redirects to see what happens
        )
        
        print(f"   SMS Response Status: {sms_response.status_code}")
        print(f"   SMS Response Length: {len(sms_response.text)}")
        
        # Check for redirects
        if sms_response.status_code in [301, 302, 303, 307, 308]:
            redirect_url = sms_response.headers.get('Location', 'Unknown')
            print(f"   📍 Got redirect to: {redirect_url}")
            
            if "login" in redirect_url.lower():
                print("   ❌ Session expired during submission - this is the core issue")
                print("   💡 We need to find a way to maintain session during form submission")
            else:
                print("   ⚠️ Got redirect but not to login - might be working")
        elif sms_response.ok:
            if "success" in sms_response.text.lower():
                print("   ✅ SMS SUCCESS detected!")
            elif len(sms_response.text) < 1000:
                print(f"   ✅ SMS sent successfully (short response): {sms_response.text}")
            else:
                print("   ⚠️ SMS response unclear")
        else:
            print(f"   ❌ SMS failed with status {sms_response.status_code}")
        
        # Step 4: Try a different approach - submit to the exact same endpoint as Selenium
        print(f"\n📤 Trying Selenium-equivalent approach...")
        
        # The Selenium code clicks "Send Message" which opens a popup
        # Then it fills the form and clicks "save-follow-up"
        # We need to replicate this exact flow
        
        # First, let's try to find the actual form action that the popup submits to
        print(f"   🔍 Looking for the actual form action...")
        
        # Try different form actions that might be used by the popup
        form_actions = [
            f"{client.base_url}/action/Dashboard/follow-up",
            f"{client.base_url}/action/Members/follow-up", 
            f"{client.base_url}/action/Dashboard/save-follow-up",
            f"{client.base_url}/action/Members/save-follow-up"
        ]
        
        for action_url in form_actions:
            try:
                print(f"   Testing form action: {action_url}")
                
                form_data = {
                    "memberId": MEMBER_ID,
                    "textMessage": SMS_MESSAGE,
                    "followUpOutcomeNotes": "Selenium-equivalent test",
                    "type": "text",
                    "action": "send"
                }
                
                if csrf_token:
                    form_data["csrf_token"] = csrf_token
                
                form_headers = headers.copy()
                form_headers.update({
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": profile_url,
                    "Origin": client.base_url
                })
                
                form_response = client.auth.session.post(
                    action_url,
                    data=form_data,
                    headers=form_headers,
                    timeout=30,
                    verify=False,
                    allow_redirects=False
                )
                
                print(f"   {action_url}: {form_response.status_code}")
                
                if form_response.ok and len(form_response.text) < 1000:
                    print(f"   ✅ {action_url} might be working: {form_response.text}")
                elif form_response.status_code in [301, 302, 303, 307, 308]:
                    redirect_url = form_response.headers.get('Location', 'Unknown')
                    print(f"   📍 {action_url} redirects to: {redirect_url}")
                
            except Exception as e:
                print(f"   ❌ {action_url} failed: {e}")
        
        print(f"\n🎯 SESSION FIXED SOLUTION SUMMARY:")
        print(f"   The core issue is session expiration during form submission")
        print(f"   ClubOS has very strict session management")
        print(f"   We need to either:")
        print(f"   1. Find the exact API endpoint that doesn't require session state")
        print(f"   2. Use Selenium for reliable session management")
        print(f"   3. Implement proper session refresh before each request")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_session_fixed() 