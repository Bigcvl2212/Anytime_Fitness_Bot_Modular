#!/usr/bin/env python3
"""
Send messages with proper session state management and detailed debugging
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup
import time

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"

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

def send_message_with_session():
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
        # Step 1: Get dashboard and verify session
        print("\n📄 Getting dashboard...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        print(f"   Dashboard Status: {response.status_code}")
        
        if not response.ok:
            print(f"   ❌ Failed to load dashboard: {response.status_code}")
            return
        
        # Check if we're still logged in
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("   ⚠️ Session expired, re-authenticating...")
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
        
        # Step 2: Get member profile
        print(f"\n👤 Getting member profile...")
        profile_url = f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if not profile_response.ok:
            print(f"   ❌ Failed to load profile: {profile_response.status_code}")
            return
        
        print(f"   ✅ Profile loaded successfully")
        
        # Check if profile page shows we're logged in
        if "login" in profile_response.text.lower() and "username" in profile_response.text.lower():
            print("   ❌ Profile page shows login form - session issue")
            return
        
        # Step 3: Send SMS via follow-up endpoint
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        
        followup_url = f"{client.base_url}/action/Dashboard/follow-up"
        
        # Build form data
        sms_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Test SMS via session management - should work now!",
            "followUpOutcomeNotes": "Session test",
            "type": "text",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            sms_data["csrf_token"] = csrf_token
        
        # Use proper headers with referer
        sms_headers = headers.copy()
        sms_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": profile_url,
            "Origin": client.base_url
        })
        
        print(f"   Submitting to: {followup_url}")
        print(f"   Form data: {sms_data}")
        
        sms_response = client.auth.session.post(
            followup_url,
            data=sms_data,
            headers=sms_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   SMS Response Status: {sms_response.status_code}")
        print(f"   SMS Response Length: {len(sms_response.text)}")
        
        # Analyze the response
        if sms_response.ok:
            if "success" in sms_response.text.lower():
                print("   ✅ SUCCESS detected in SMS response!")
            elif "error" in sms_response.text.lower():
                print("   ❌ ERROR detected in SMS response")
            elif len(sms_response.text) < 1000:
                print(f"   ✅ Short SMS response (likely success): {sms_response.text}")
            else:
                print("   ⚠️ Long SMS response, checking content...")
                
                # Look for specific keywords
                keywords = ["sent", "delivered", "message", "follow", "up", "success", "error"]
                found_keywords = []
                for keyword in keywords:
                    if keyword in sms_response.text.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"   📝 Found keywords in SMS response: {found_keywords}")
                
                # Save response for manual inspection
                with open('sms_response.html', 'w', encoding='utf-8') as f:
                    f.write(sms_response.text)
                print("   💾 Saved SMS response to sms_response.html")
        else:
            print(f"   ❌ SMS failed with status {sms_response.status_code}")
        
        # Step 4: Send Email
        print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
        
        email_data = {
            "memberId": MEMBER_ID,
            "emailSubject": "Test Email via Session Management",
            "emailBody": "This is a test email sent via session management - should work now!",
            "followUpOutcomeNotes": "Session email test",
            "type": "email",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            email_data["csrf_token"] = csrf_token
        
        print(f"   Submitting email to: {followup_url}")
        print(f"   Email form data: {email_data}")
        
        email_response = client.auth.session.post(
            followup_url,
            data=email_data,
            headers=sms_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Email Response Status: {email_response.status_code}")
        print(f"   Email Response Length: {len(email_response.text)}")
        
        # Analyze the email response
        if email_response.ok:
            if "success" in email_response.text.lower():
                print("   ✅ SUCCESS detected in email response!")
            elif "error" in email_response.text.lower():
                print("   ❌ ERROR detected in email response")
            elif len(email_response.text) < 1000:
                print(f"   ✅ Short email response (likely success): {email_response.text}")
            else:
                print("   ⚠️ Long email response, checking content...")
                
                # Look for specific keywords
                found_keywords = []
                for keyword in keywords:
                    if keyword in email_response.text.lower():
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"   📝 Found keywords in email response: {found_keywords}")
                
                # Save response for manual inspection
                with open('email_response.html', 'w', encoding='utf-8') as f:
                    f.write(email_response.text)
                print("   💾 Saved email response to email_response.html")
        else:
            print(f"   ❌ Email failed with status {email_response.status_code}")
        
        print(f"\n📊 Session Management Summary:")
        print(f"   If you received the messages, the session management is working!")
        print(f"   Check the saved HTML files for detailed response analysis")
        print(f"   The key was maintaining proper session state and using correct headers")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_with_session() 