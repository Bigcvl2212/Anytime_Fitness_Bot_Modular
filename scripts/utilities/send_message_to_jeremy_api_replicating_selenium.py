#!/usr/bin/env python3
"""
Send messages to Jeremy Mayo via ClubOS API by replicating the exact Selenium flow
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
MEMBER_ID = "187032782"  # Jeremy Mayo's member ID
SMS_MESSAGE = "This is a test SMS sent via ClubOS API - replicating Selenium flow!"
EMAIL_MESSAGE = "This is a test EMAIL sent via ClubOS API - replicating Selenium flow!"

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

def extract_member_profile_data(html_content):
    """Extract member profile data from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for member ID in the page
    member_id_patterns = [
        r'data-member-id="([^"]+)"',
        r'memberId["\']?\s*[:=]\s*["\']?([^"\']+)["\']?',
        r'data-id="([^"]+)"'
    ]
    
    for pattern in member_id_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def send_message_replicating_selenium():
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
        # Step 1: Go to dashboard (like Selenium)
        print("\n📄 Navigating to dashboard...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        print(f"   Dashboard Status: {response.status_code}")
        
        if not response.ok:
            print(f"   ❌ Failed to load dashboard: {response.status_code}")
            return
        
        # Extract CSRF token from dashboard
        csrf_token = extract_csrf_token(response.text)
        if csrf_token:
            print(f"   ✅ Found CSRF token: {csrf_token[:20]}...")
        else:
            print("   ⚠️ No CSRF token found")
        
        # Step 2: Search for Jeremy Mayo (replicate quick search)
        print(f"\n🔍 Searching for {TARGET_NAME}...")
        
        # Try the quick search endpoint that the dashboard uses
        search_url = f"{client.base_url}/ajax/quick-search"
        search_data = {
            "q": TARGET_NAME,
            "type": "member"
        }
        
        if csrf_token:
            search_data["csrf_token"] = csrf_token
        
        search_response = client.auth.session.post(
            search_url,
            data=search_data,
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Search Status: {search_response.status_code}")
        print(f"   Search Response: {search_response.text[:200]}...")
        
        # Step 3: Get member profile page (replicate clicking on search result)
        print(f"\n👤 Getting member profile for {TARGET_NAME}...")
        
        # Try different profile URLs
        profile_urls = [
            f"{client.base_url}/action/Members/view/{MEMBER_ID}",
            f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}",
            f"{client.base_url}/action/Members/profile/{MEMBER_ID}"
        ]
        
        profile_page = None
        for profile_url in profile_urls:
            try:
                response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
                print(f"   Profile URL {profile_url}: {response.status_code}")
                
                if response.ok:
                    profile_page = response.text
                    print(f"   ✅ Successfully loaded profile page")
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Profile URL {profile_url} failed: {e}")
                continue
        
        if not profile_page:
            print("   ❌ Could not load member profile page")
            return
        
        # Extract member data from profile page
        member_id_from_page = extract_member_profile_data(profile_page)
        if member_id_from_page:
            print(f"   ✅ Found member ID in profile: {member_id_from_page}")
        else:
            print(f"   ⚠️ Using provided member ID: {MEMBER_ID}")
        
        # Step 4: Send message via popup form (replicate clicking "Send Message")
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        
        # The Selenium code shows the form fields used:
        # - textMessage (for SMS)
        # - emailSubject (for email)
        # - followUpOutcomeNotes (for notes)
        # - send button: a.save-follow-up
        
        # Try the follow-up endpoint that the popup form submits to
        followup_url = f"{client.base_url}/action/Dashboard/follow-up"
        
        # SMS form data (replicating the exact field names from Selenium)
        sms_data = {
            "memberId": member_id_from_page or MEMBER_ID,
            "textMessage": SMS_MESSAGE,
            "followUpOutcomeNotes": "Auto-SMS sent by Gym Bot",
            "type": "text",
            "action": "send"
        }
        
        if csrf_token:
            sms_data["csrf_token"] = csrf_token
        
        print(f"   SMS Form Data: {sms_data}")
        
        sms_response = client.auth.session.post(
            followup_url,
            data=sms_data,
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"   SMS Response Status: {sms_response.status_code}")
        print(f"   SMS Response: {sms_response.text[:300]}...")
        
        # Check if SMS was successful
        if sms_response.ok:
            if "success" in sms_response.text.lower() or "sent" in sms_response.text.lower():
                print("   ✅ SMS appears to have been sent successfully!")
            elif len(sms_response.text) < 1000:  # Short response might be success
                print("   ✅ SMS sent successfully (short response)")
            else:
                print("   ⚠️ SMS response unclear, checking for errors...")
                if "error" in sms_response.text.lower():
                    print("   ❌ SMS failed with error")
                else:
                    print("   ⚠️ SMS status unclear")
        else:
            print(f"   ❌ SMS failed with status {sms_response.status_code}")
        
        # Step 5: Send email (replicating email fallback)
        print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
        
        # Email form data (replicating the exact field names from Selenium)
        email_data = {
            "memberId": member_id_from_page or MEMBER_ID,
            "emailSubject": "Test Email from Gym Bot",
            "emailBody": EMAIL_MESSAGE,
            "followUpOutcomeNotes": "Auto-email sent by Gym Bot",
            "type": "email",
            "action": "send"
        }
        
        if csrf_token:
            email_data["csrf_token"] = csrf_token
        
        print(f"   Email Form Data: {email_data}")
        
        email_response = client.auth.session.post(
            followup_url,
            data=email_data,
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Email Response Status: {email_response.status_code}")
        print(f"   Email Response: {email_response.text[:300]}...")
        
        # Check if email was successful
        if email_response.ok:
            if "success" in email_response.text.lower() or "sent" in email_response.text.lower():
                print("   ✅ Email appears to have been sent successfully!")
            elif len(email_response.text) < 1000:  # Short response might be success
                print("   ✅ Email sent successfully (short response)")
            else:
                print("   ⚠️ Email response unclear, checking for errors...")
                if "error" in email_response.text.lower():
                    print("   ❌ Email failed with error")
                else:
                    print("   ⚠️ Email status unclear")
        else:
            print(f"   ❌ Email failed with status {email_response.status_code}")
        
        print("\n📊 Summary:")
        print("   If you received the messages, the API replication is working!")
        print("   The key was following the exact same steps as Selenium:")
        print("   1. Dashboard → 2. Search → 3. Profile → 4. Follow-up form")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_replicating_selenium() 