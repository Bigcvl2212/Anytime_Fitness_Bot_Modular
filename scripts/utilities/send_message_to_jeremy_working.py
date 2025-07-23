#!/usr/bin/env python3
"""
Send a message and email to Jeremy Mayo via ClubOS API, printing full API responses.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Jeremy Mayo's member ID
SMS_MESSAGE = "This is a test SMS sent via ClubOS API - it should work this time!"
EMAIL_MESSAGE = "This is a test EMAIL sent via ClubOS API - it should work this time!"

def extract_csrf_token(html_content):
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

def send_message_and_email():
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

    # Step 1: Navigate to messages page to get proper form structure
    print("\n📄 Navigating to messages page...")
    messages_url = f"{client.base_url}/action/Dashboard/messages"
    headers = client.auth.get_headers()
    
    try:
        response = client.auth.session.get(messages_url, headers=headers, timeout=30, verify=False)
        print(f"   Status: {response.status_code}")
        
        if response.ok:
            # Extract CSRF token from messages page
            csrf_token = extract_csrf_token(response.text)
            if csrf_token:
                print(f"   ✅ Found CSRF token: {csrf_token[:20]}...")
            else:
                print("   ⚠️ No CSRF token found")
            
            # Step 2: Send SMS with proper form data
            print(f"\n📤 Sending SMS to {TARGET_NAME}...")
            message_data = {
                "memberId": MEMBER_ID,
                "messageType": "text",
                "messageText": SMS_MESSAGE,
                "sendMethod": "sms"
            }
            
            # Add CSRF token if found
            if csrf_token:
                message_data["csrf_token"] = csrf_token
            
            response = client.auth.session.post(
                messages_url,
                data=message_data,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            print(f"   SMS Status: {response.status_code}")
            print(f"   SMS Response: {response.text[:500]}")
            
            # Check if SMS was actually sent
            if "success" in response.text.lower() or "sent" in response.text.lower():
                print("   ✅ SMS appears to have been sent successfully!")
            else:
                print("   ⚠️ SMS may not have been delivered")
            
            # Step 3: Send Email
            print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
            message_data = {
                "memberId": MEMBER_ID,
                "messageType": "email",
                "messageText": EMAIL_MESSAGE,
                "sendMethod": "email"
            }
            
            # Add CSRF token if found
            if csrf_token:
                message_data["csrf_token"] = csrf_token
            
            response = client.auth.session.post(
                messages_url,
                data=message_data,
                headers=headers,
                timeout=30,
                verify=False
            )
            
            print(f"   Email Status: {response.status_code}")
            print(f"   Email Response: {response.text[:500]}")
            
            # Check if email was actually sent
            if "success" in response.text.lower() or "sent" in response.text.lower():
                print("   ✅ Email appears to have been sent successfully!")
            else:
                print("   ⚠️ Email may not have been delivered")
            
            print("\n📊 Summary:")
            print("   If you received the messages, the API is working!")
            print("   If not, we may need to try a different approach.")
                
        else:
            print(f"   ❌ Failed to load messages page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_and_email() 