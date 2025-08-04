#!/usr/bin/env python3
"""
Send messages to Jeremy Mayo via direct HTTP requests to ClubOS
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from config.secrets_local import get_secret

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Jeremy Mayo's member ID
SMS_MESSAGE = "This is a test SMS sent via direct HTTP request!"
EMAIL_MESSAGE = "This is a test EMAIL sent via direct HTTP request!"

def main():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    # Create session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    try:
        print("🔐 Logging into ClubOS...")
        
        # Step 1: Get login page
        login_url = "https://anytime.club-os.com/action/Login"
        login_page = session.get(login_url, timeout=30)
        
        if not login_page.ok:
            print(f"❌ Failed to load login page: {login_page.status_code}")
            return
        
        # Extract CSRF token if present
        import re
        csrf_token = None
        csrf_patterns = [
            r'<meta name="csrf-token" content="([^"]+)"',
            r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"',
            r'<input[^>]*name="_token"[^>]*value="([^"]+)"',
            r'window\.csrfToken\s*=\s*["\']([^"\']+)["\']',
            r'data-csrf="([^"]+)"'
        ]
        
        for pattern in csrf_patterns:
            match = re.search(pattern, login_page.text, re.IGNORECASE)
            if match:
                csrf_token = match.group(1)
                print(f"Found CSRF token: {csrf_token[:20]}...")
                break
        
        # Step 2: Submit login form
        login_data = {
            "username": username,
            "password": password,
            "submit": "Login"
        }
        
        # Add CSRF token if found
        if csrf_token:
            login_data["csrf_token"] = csrf_token
        
        login_response = session.post(login_url, data=login_data, allow_redirects=True, timeout=30)
        
        # Debug: Print response details
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response URL: {login_response.url}")
        print(f"Login response headers: {dict(login_response.headers)}")
        print(f"Login response text (first 500 chars): {login_response.text[:500]}")
        
        # Check if login was successful
        if "Dashboard" not in login_response.url and "dashboard" not in login_response.url.lower():
            print("❌ Login failed - not redirected to dashboard")
            return
        
        print("✅ Login successful!")
        
        # Step 3: Send SMS
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        sms_data = {
            "memberId": MEMBER_ID,
            "messageType": "text",
            "messageText": SMS_MESSAGE,
            "sendMethod": "sms"
        }
        
        sms_response = session.post(
            "https://anytime.club-os.com/action/Dashboard/messages",
            data=sms_data,
            timeout=30,
            verify=False
        )
        
        print(f"SMS Status: {sms_response.status_code}")
        print(f"SMS Response: {sms_response.text[:500]}")
        
        # Step 4: Send Email
        print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
        email_data = {
            "memberId": MEMBER_ID,
            "messageType": "email",
            "messageText": EMAIL_MESSAGE,
            "sendMethod": "email"
        }
        
        email_response = session.post(
            "https://anytime.club-os.com/action/Dashboard/messages",
            data=email_data,
            timeout=30,
            verify=False
        )
        
        print(f"Email Status: {email_response.status_code}")
        print(f"Email Response: {email_response.text[:500]}")
        
        # Check results
        if sms_response.ok and email_response.ok:
            print("\n✅ Both messages sent successfully!")
        else:
            print("\n⚠️ Some messages may not have been delivered.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 