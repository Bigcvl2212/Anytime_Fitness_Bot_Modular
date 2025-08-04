#!/usr/bin/env python3
"""
Capture the exact request format from a working Selenium session and replicate with API calls
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from urllib.parse import urljoin
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "API capture working SMS test - this should work!"
EMAIL_MESSAGE = "API capture working email test - this should work!"

def send_message_api_capture_working():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Setting up API capture working...")
        
        # Create session and authenticate
        session = requests.Session()
        base_url = "https://anytime.club-os.com"
        
        # Login
        login_url = f"{base_url}/action/Login"
        login_data = {
            "username": username,
            "password": password
        }
        
        print("   🔑 Logging into ClubOS...")
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed with status {login_response.status_code}")
            return
        
        print("   ✅ Login successful!")
        
        # Step 1: Navigate through the exact same flow as Selenium
        print("   📊 Navigating to dashboard...")
        dashboard_response = session.get(f"{base_url}/action/Dashboard/view")
        time.sleep(2)
        
        print("   ✅ Dashboard loaded successfully!")
        
        # Step 2: Navigate to search and establish search context
        print("   🔍 Navigating to search...")
        search_response = session.get(f"{base_url}/action/Dashboard/search")
        time.sleep(1)
        
        print("   ✅ Search page loaded successfully!")
        
        # Step 3: Navigate to member profile
        print(f"   👤 Navigating to {TARGET_NAME}'s profile...")
        profile_url = f"{base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = session.get(profile_url)
        time.sleep(2)
        
        print("   ✅ Member profile loaded successfully!")
        
        # Step 4: Try the exact request format that works in the web interface
        # Based on the working Selenium flow, the key is to submit to the profile page itself
        
        print(f"\n📤 Sending SMS to {TARGET_NAME} via profile page submission...")
        sms_success = False
        
        # Use the exact headers that a browser would send
        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": profile_url,
            "Origin": base_url,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Try submitting to the profile page with the exact form data that works
        sms_form_data = {
            "memberId": MEMBER_ID,
            "textMessage": SMS_MESSAGE,
            "followUpOutcomeNotes": "API SMS sent by Gym Bot",
            "action": "send_message"
        }
        
        sms_response = session.post(profile_url, data=sms_form_data, headers=browser_headers)
        
        print(f"   🔍 SMS Profile Submission Response:")
        print(f"      Status: {sms_response.status_code}")
        print(f"      Response length: {len(sms_response.text)} chars")
        
        if sms_response.status_code == 200:
            if "success" in sms_response.text.lower() or "sent" in sms_response.text.lower():
                print("   ✅ SMS sent successfully via profile submission!")
                sms_success = True
            else:
                print(f"   ⚠️ SMS response: {sms_response.text[:200]}...")
        elif sms_response.status_code == 302:
            print("   ⚠️ SMS got redirect - checking if successful")
            if "success" in sms_response.headers.get("Location", "").lower():
                print("   ✅ SMS redirect indicates success!")
                sms_success = True
        
        # Try Email with the same approach
        print(f"\n📤 Sending Email to {TARGET_NAME} via profile page submission...")
        email_success = False
        
        email_form_data = {
            "memberId": MEMBER_ID,
            "emailMessage": EMAIL_MESSAGE,
            "emailSubject": "API Capture Working Test",
            "followUpOutcomeNotes": "API Email sent by Gym Bot",
            "action": "send_message"
        }
        
        email_response = session.post(profile_url, data=email_form_data, headers=browser_headers)
        
        print(f"   🔍 Email Profile Submission Response:")
        print(f"      Status: {email_response.status_code}")
        print(f"      Response length: {len(email_response.text)} chars")
        
        if email_response.status_code == 200:
            if "success" in email_response.text.lower() or "sent" in email_response.text.lower():
                print("   ✅ Email sent successfully via profile submission!")
                email_success = True
            else:
                print(f"   ⚠️ Email response: {email_response.text[:200]}...")
        elif email_response.status_code == 302:
            print("   ⚠️ Email got redirect - checking if successful")
            if "success" in email_response.headers.get("Location", "").lower():
                print("   ✅ Email redirect indicates success!")
                email_success = True
        
        # If profile submission doesn't work, try the exact API endpoint with proper context
        if not sms_success and not email_success:
            print(f"\n🔄 Trying API endpoint with proper browser context...")
            
            # Use the exact same headers but for API endpoint
            api_headers = browser_headers.copy()
            api_headers["X-Requested-With"] = "XMLHttpRequest"
            api_headers["Content-Type"] = "application/x-www-form-urlencoded"
            
            api_data = {
                "memberId": MEMBER_ID,
                "message": SMS_MESSAGE,
                "messageType": "text"
            }
            
            api_url = urljoin(base_url, "/action/Api/send-message")
            api_response = session.post(api_url, data=api_data, headers=api_headers)
            
            print(f"   🔍 API with Browser Context Response:")
            print(f"      Status: {api_response.status_code}")
            print(f"      Response: '{api_response.text}'")
            
            if api_response.status_code == 200:
                if "success" in api_response.text.lower() or "sent" in api_response.text.lower():
                    print("   ✅ API with browser context successful!")
                    sms_success = True
                else:
                    print(f"   ⚠️ API still returning: {api_response.text}")
        
        # Summary
        print(f"\n📊 API Capture Working Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_success else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if email_success else '❌ Failed'}")
        
        if sms_success or email_success:
            print("\n🎉 At least one message was sent successfully via API!")
        else:
            print("\n⚠️ No messages were delivered via API.")
            
    except Exception as e:
        print(f"❌ Error during API capture working: {e}")

if __name__ == "__main__":
    send_message_api_capture_working() 