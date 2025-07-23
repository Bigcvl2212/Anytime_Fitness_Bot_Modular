#!/usr/bin/env python3
"""
API solution that maintains proper session state by navigating through web interface first
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from urllib.parse import urljoin
from config.secrets_local import get_secret

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "API session state SMS test - this should work!"
EMAIL_MESSAGE = "API session state email test - this should work!"

def send_message_api_session_state():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Setting up API session with proper state...")
        
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
        
        # Step 1: Navigate to dashboard to establish session state
        print("   📊 Navigating to dashboard...")
        dashboard_response = session.get(f"{base_url}/action/Dashboard/view")
        if dashboard_response.status_code != 200:
            print(f"   ❌ Dashboard navigation failed")
            return
        
        print("   ✅ Dashboard loaded successfully!")
        
        # Step 2: Navigate to member profile to establish member context
        print(f"   👤 Navigating to {TARGET_NAME}'s profile...")
        profile_url = f"{base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = session.get(profile_url)
        
        if profile_response.status_code != 200:
            print(f"   ❌ Profile navigation failed")
            return
        
        print("   ✅ Member profile loaded successfully!")
        
        # Step 3: Now try API calls with proper session state
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": profile_url,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Try SMS with proper session state
        print(f"\n📤 Sending SMS to {TARGET_NAME} via API with session state...")
        sms_success = False
        
        sms_data = {
            "memberId": MEMBER_ID,
            "message": SMS_MESSAGE,
            "messageType": "text",
            "followUpOutcomeNotes": "API SMS sent by Gym Bot"
        }
        
        sms_url = urljoin(base_url, "/action/Api/send-message")
        sms_response = session.post(sms_url, data=sms_data, headers=headers)
        
        print(f"   🔍 SMS API Response:")
        print(f"      Status: {sms_response.status_code}")
        print(f"      Response: '{sms_response.text}'")
        
        if sms_response.status_code == 200:
            if "success" in sms_response.text.lower() or "sent" in sms_response.text.lower():
                print("   ✅ SMS sent successfully via API!")
                sms_success = True
            elif "something isn't right" in sms_response.text.lower():
                print("   ⚠️ API still returning 'Something isn't right' - trying alternative approach")
            else:
                print(f"   ⚠️ Unexpected response: {sms_response.text}")
        
        # Try Email with proper session state
        print(f"\n📤 Sending Email to {TARGET_NAME} via API with session state...")
        email_success = False
        
        email_data = {
            "memberId": MEMBER_ID,
            "subject": "API Session State Test",
            "message": EMAIL_MESSAGE,
            "messageType": "email",
            "followUpOutcomeNotes": "API Email sent by Gym Bot"
        }
        
        email_url = urljoin(base_url, "/action/Api/send-message")
        email_response = session.post(email_url, data=email_data, headers=headers)
        
        print(f"   🔍 Email API Response:")
        print(f"      Status: {email_response.status_code}")
        print(f"      Response: '{email_response.text}'")
        
        if email_response.status_code == 200:
            if "success" in email_response.text.lower() or "sent" in email_response.text.lower():
                print("   ✅ Email sent successfully via API!")
                email_success = True
            elif "something isn't right" in email_response.text.lower():
                print("   ⚠️ API still returning 'Something isn't right' - trying alternative approach")
            else:
                print(f"   ⚠️ Unexpected response: {email_response.text}")
        
        # If API still doesn't work, try form submission approach
        if not sms_success and not email_success:
            print(f"\n🔄 Trying form submission approach...")
            
            # Try submitting to the member profile page directly
            form_data = {
                "memberId": MEMBER_ID,
                "textMessage": SMS_MESSAGE,
                "emailMessage": EMAIL_MESSAGE,
                "followUpOutcomeNotes": "Form submission test",
                "action": "send_message"
            }
            
            form_response = session.post(profile_url, data=form_data, headers=headers)
            
            print(f"   🔍 Form Submission Response:")
            print(f"      Status: {form_response.status_code}")
            print(f"      Response length: {len(form_response.text)} chars")
            
            if form_response.status_code == 200:
                if "success" in form_response.text.lower() or "sent" in form_response.text.lower():
                    print("   ✅ Form submission successful!")
                    sms_success = True
                    email_success = True
                else:
                    print(f"   ⚠️ Form submission response: {form_response.text[:200]}...")
        
        # Summary
        print(f"\n📊 API Session State Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_success else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if email_success else '❌ Failed'}")
        
        if sms_success or email_success:
            print("\n🎉 At least one message was sent successfully via API!")
        else:
            print("\n⚠️ No messages were delivered via API.")
            
    except Exception as e:
        print(f"❌ Error during API session state messaging: {e}")

if __name__ == "__main__":
    send_message_api_session_state() 