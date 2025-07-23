#!/usr/bin/env python3
"""
Final attempt to send messages via HTTP requests following the exact Selenium flow
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

def send_message_final_attempt():
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
        # Step 1: Go to dashboard (exactly like Selenium)
        print("\n📄 Navigating to dashboard...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        print(f"   Dashboard Status: {response.status_code}")
        
        if not response.ok:
            print(f"   ❌ Failed to load dashboard: {response.status_code}")
            return
        
        # Check if we're logged in
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("   ❌ Session expired, cannot proceed")
            return
        
        print("   ✅ Dashboard loaded successfully")
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(response.text)
        if csrf_token:
            print(f"   ✅ Found CSRF token: {csrf_token[:20]}...")
        else:
            print("   ⚠️ No CSRF token found")
        
        # Step 2: Search for Jeremy Mayo (replicate Selenium search)
        print(f"\n🔍 Searching for {TARGET_NAME}...")
        
        # Try the search endpoint that the dashboard uses
        search_url = f"{client.base_url}/ajax/quick-search"
        search_data = {
            "q": TARGET_NAME,
            "type": "member"
        }
        
        if csrf_token:
            search_data["csrf_token"] = csrf_token
        
        search_headers = headers.copy()
        search_headers.update({
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        })
        
        search_response = client.auth.session.post(
            search_url,
            data=search_data,
            headers=search_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Search Status: {search_response.status_code}")
        if search_response.ok:
            print("   ✅ Search completed")
        else:
            print("   ⚠️ Search failed, continuing anyway")
        
        # Step 3: Get member profile (replicate clicking on search result)
        print(f"\n👤 Getting member profile for {TARGET_NAME}...")
        
        # Use the working profile URL we found earlier
        profile_url = f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if not profile_response.ok:
            print(f"   ❌ Failed to load profile: {profile_response.status_code}")
            return
        
        print(f"   ✅ Profile loaded successfully")
        
        # Step 4: Send message via the follow-up endpoint (replicate clicking "Send Message")
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        
        # Use the exact endpoint and form structure from our successful tests
        followup_url = f"{client.base_url}/action/Dashboard/follow-up"
        
        # Build form data exactly like the Selenium code
        sms_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Final test SMS via HTTP API - this should work!",
            "followUpOutcomeNotes": "Final HTTP API test",
            "type": "text",
            "action": "send"
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
        
        print(f"   Submitting SMS to: {followup_url}")
        print(f"   SMS Form data: {sms_data}")
        
        sms_response = client.auth.session.post(
            followup_url,
            data=sms_data,
            headers=sms_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   SMS Response Status: {sms_response.status_code}")
        print(f"   SMS Response Length: {len(sms_response.text)}")
        
        # Check if SMS was successful
        if sms_response.ok:
            if "success" in sms_response.text.lower():
                print("   ✅ SMS SUCCESS detected!")
            elif len(sms_response.text) < 1000:
                print(f"   ✅ SMS sent successfully (short response): {sms_response.text}")
            else:
                print("   ⚠️ SMS response unclear, checking for errors...")
                if "error" in sms_response.text.lower():
                    print("   ❌ SMS failed with error")
                else:
                    print("   ⚠️ SMS status unclear")
                    
                    # Save response for analysis
                    with open('final_sms_response.html', 'w', encoding='utf-8') as f:
                        f.write(sms_response.text)
                    print("   💾 Saved SMS response to final_sms_response.html")
        else:
            print(f"   ❌ SMS failed with status {sms_response.status_code}")
        
        # Step 5: Send Email
        print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
        
        email_data = {
            "memberId": MEMBER_ID,
            "emailSubject": "Final Test Email via HTTP API",
            "emailBody": "This is a final test email sent via HTTP API - this should work!",
            "followUpOutcomeNotes": "Final HTTP API email test",
            "type": "email",
            "action": "send"
        }
        
        if csrf_token:
            email_data["csrf_token"] = csrf_token
        
        print(f"   Submitting email to: {followup_url}")
        print(f"   Email Form data: {email_data}")
        
        email_response = client.auth.session.post(
            followup_url,
            data=email_data,
            headers=sms_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Email Response Status: {email_response.status_code}")
        print(f"   Email Response Length: {len(email_response.text)}")
        
        # Check if email was successful
        if email_response.ok:
            if "success" in email_response.text.lower():
                print("   ✅ Email SUCCESS detected!")
            elif len(email_response.text) < 1000:
                print(f"   ✅ Email sent successfully (short response): {email_response.text}")
            else:
                print("   ⚠️ Email response unclear, checking for errors...")
                if "error" in email_response.text.lower():
                    print("   ❌ Email failed with error")
                else:
                    print("   ⚠️ Email status unclear")
                    
                    # Save response for analysis
                    with open('final_email_response.html', 'w', encoding='utf-8') as f:
                        f.write(email_response.text)
                    print("   💾 Saved email response to final_email_response.html")
        else:
            print(f"   ❌ Email failed with status {email_response.status_code}")
        
        print(f"\n📊 Final Attempt Summary:")
        print(f"   If you received the messages, the HTTP API approach is working!")
        print(f"   If not, we may need to use Selenium for reliable message delivery.")
        print(f"   The key was following the exact same flow as the working Selenium code:")
        print(f"   1. Dashboard → 2. Search → 3. Profile → 4. Follow-up form")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_final_attempt() 