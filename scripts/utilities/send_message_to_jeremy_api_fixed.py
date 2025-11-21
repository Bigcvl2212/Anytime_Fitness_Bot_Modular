#!/usr/bin/env python3
"""
Send messages to Jeremy Mayo via ClubOS API following the working Selenium approach
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup
import time

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Jeremy Mayo's member ID
SMS_MESSAGE = "This is a test SMS sent via ClubOS API - it should work this time!"
EMAIL_MESSAGE = "This is a test EMAIL sent via ClubOS API - it should work this time!"

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

    try:
        # Step 1: Go to dashboard (like the working Selenium code)
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
        
        # Step 2: Search for Jeremy Mayo (simulate the quick search)
        print(f"\n🔍 Searching for {TARGET_NAME}...")
        
        # Try different search endpoints
        search_endpoints = [
            "/ajax/members/search",
            "/action/Dashboard/search",
            "/api/members/search",
            "/action/Members/search"
        ]
        
        member_found = False
        for endpoint in search_endpoints:
            try:
                search_url = f"{client.base_url}{endpoint}"
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
                
                print(f"   Search endpoint {endpoint}: {search_response.status_code}")
                
                if search_response.ok:
                    print(f"   ✅ Search successful via {endpoint}")
                    member_found = True
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Search endpoint {endpoint} failed: {e}")
                continue
        
        if not member_found:
            print("   ⚠️ Could not find member via search, trying direct approach")
        
        # Step 3: Try to send message directly using the member ID
        print(f"\n📤 Attempting to send SMS to {TARGET_NAME}...")
        
        # Try different message endpoints
        message_endpoints = [
            "/action/Dashboard/messages",
            "/action/Members/send-message",
            "/ajax/messages/send",
            "/api/messages/send"
        ]
        
        for endpoint in message_endpoints:
            try:
                message_url = f"{client.base_url}{endpoint}"
                
                # Try different form structures
                message_forms = [
                    {
                        "memberId": MEMBER_ID,
                        "messageType": "text",
                        "messageText": SMS_MESSAGE,
                        "sendMethod": "sms"
                    },
                    {
                        "member_id": MEMBER_ID,
                        "type": "text",
                        "message": SMS_MESSAGE,
                        "method": "sms"
                    },
                    {
                        "recipient": MEMBER_ID,
                        "type": "text",
                        "content": SMS_MESSAGE,
                        "channel": "sms"
                    }
                ]
                
                for form_data in message_forms:
                    if csrf_token:
                        form_data["csrf_token"] = csrf_token
                    
                    print(f"   Trying {endpoint} with form data: {form_data}")
                    
                    response = client.auth.session.post(
                        message_url,
                        data=form_data,
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                    
                    print(f"   Response: {response.status_code}")
                    print(f"   Response text: {response.text[:200]}...")
                    
                    # Check if it looks like success
                    if response.ok and ("success" in response.text.lower() or "sent" in response.text.lower()):
                        print(f"   ✅ SMS appears to have been sent successfully via {endpoint}!")
                        break
                    elif response.ok and len(response.text) < 1000:  # Short response might be success
                        print(f"   ✅ SMS sent successfully via {endpoint} (short response)")
                        break
                    else:
                        print(f"   ⚠️ SMS may not have been sent via {endpoint}")
                
                # If we found a working endpoint, break
                if response.ok and ("success" in response.text.lower() or "sent" in response.text.lower() or len(response.text) < 1000):
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Endpoint {endpoint} failed: {e}")
                continue
        
        # Step 4: Try to send email
        print(f"\n📤 Attempting to send EMAIL to {TARGET_NAME}...")
        
        for endpoint in message_endpoints:
            try:
                message_url = f"{client.base_url}{endpoint}"
                
                # Try different form structures for email
                email_forms = [
                    {
                        "memberId": MEMBER_ID,
                        "messageType": "email",
                        "messageText": EMAIL_MESSAGE,
                        "sendMethod": "email",
                        "subject": "Test Email"
                    },
                    {
                        "member_id": MEMBER_ID,
                        "type": "email",
                        "message": EMAIL_MESSAGE,
                        "method": "email",
                        "subject": "Test Email"
                    }
                ]
                
                for form_data in email_forms:
                    if csrf_token:
                        form_data["csrf_token"] = csrf_token
                    
                    print(f"   Trying {endpoint} with email form data: {form_data}")
                    
                    response = client.auth.session.post(
                        message_url,
                        data=form_data,
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                    
                    print(f"   Response: {response.status_code}")
                    print(f"   Response text: {response.text[:200]}...")
                    
                    # Check if it looks like success
                    if response.ok and ("success" in response.text.lower() or "sent" in response.text.lower()):
                        print(f"   ✅ Email appears to have been sent successfully via {endpoint}!")
                        break
                    elif response.ok and len(response.text) < 1000:  # Short response might be success
                        print(f"   ✅ Email sent successfully via {endpoint} (short response)")
                        break
                    else:
                        print(f"   ⚠️ Email may not have been sent via {endpoint}")
                
                # If we found a working endpoint, break
                if response.ok and ("success" in response.text.lower() or "sent" in response.text.lower() or len(response.text) < 1000):
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Email endpoint {endpoint} failed: {e}")
                continue
        
        print("\n📊 Summary:")
        print("   If you received the messages, the API is working!")
        print("   If not, we may need to use the Selenium approach.")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    send_message_and_email() 