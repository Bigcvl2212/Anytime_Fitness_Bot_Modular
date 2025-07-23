#!/usr/bin/env python3
"""
API solution that replicates the exact working flow from the web interface
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
SMS_MESSAGE = "API working flow SMS test - this should work!"
EMAIL_MESSAGE = "API working flow email test - this should work!"

def send_message_api_working_flow():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Setting up API working flow...")
        
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
        
        # Step 1: Navigate to dashboard and wait
        print("   📊 Navigating to dashboard...")
        dashboard_response = session.get(f"{base_url}/action/Dashboard/view")
        time.sleep(2)  # Wait for session to stabilize
        
        if dashboard_response.status_code != 200:
            print(f"   ❌ Dashboard navigation failed")
            return
        
        print("   ✅ Dashboard loaded successfully!")
        
        # Step 2: Navigate to search page
        print("   🔍 Navigating to search page...")
        search_url = f"{base_url}/action/Dashboard/search"
        search_response = session.get(search_url)
        time.sleep(1)  # Wait for session to stabilize
        
        if search_response.status_code != 200:
            print(f"   ❌ Search page failed")
            return
        
        print("   ✅ Search page loaded successfully!")
        
        # Step 3: Navigate to Jeremy's profile page
        print(f"   👤 Navigating to {TARGET_NAME}'s profile...")
        profile_url = f"{base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = session.get(profile_url)
        time.sleep(2)  # Wait for session to stabilize
        
        if profile_response.status_code != 200:
            print(f"   ❌ Profile navigation failed")
            return
        
        print("   ✅ Member profile loaded successfully!")
        
        # Step 4: Try the working API endpoints with fresh session
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": profile_url,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Try SMS with fresh session
        print(f"\n📤 Sending SMS to {TARGET_NAME} via working API...")
        sms_success = False
        
        sms_data = {
            "memberId": MEMBER_ID,
            "message": SMS_MESSAGE,
            "messageType": "text"
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
                print("   ⚠️ API still returning 'Something isn't right'")
            else:
                print(f"   ⚠️ Unexpected response: {sms_response.text}")
        
        # Try Email with fresh session
        print(f"\n📤 Sending Email to {TARGET_NAME} via working API...")
        email_success = False
        
        email_data = {
            "memberId": MEMBER_ID,
            "subject": "API Working Flow Test",
            "message": EMAIL_MESSAGE,
            "messageType": "email"
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
                print("   ⚠️ API still returning 'Something isn't right'")
            else:
                print(f"   ⚠️ Unexpected response: {email_response.text}")
        
        # If API still doesn't work, try the exact form submission that works in Selenium
        if not sms_success and not email_success:
            print(f"\n🔄 Trying exact Selenium form submission...")
            
            # Navigate to the exact URL that Selenium uses
            selenium_profile_url = f"{base_url}/action/Dashboard/member/{MEMBER_ID}"
            selenium_response = session.get(selenium_profile_url)
            time.sleep(1)
            
            # Try the exact form data that Selenium submits
            selenium_form_data = {
                "memberId": MEMBER_ID,
                "textMessage": SMS_MESSAGE,
                "emailMessage": EMAIL_MESSAGE,
                "followUpOutcomeNotes": "API test sent by Gym Bot"
            }
            
            selenium_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": selenium_profile_url,
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            selenium_submit_response = session.post(selenium_profile_url, data=selenium_form_data, headers=selenium_headers)
            
            print(f"   🔍 Selenium Form Response:")
            print(f"      Status: {selenium_submit_response.status_code}")
            print(f"      Response length: {len(selenium_submit_response.text)} chars")
            
            if selenium_submit_response.status_code == 200:
                if "success" in selenium_submit_response.text.lower() or "sent" in selenium_submit_response.text.lower():
                    print("   ✅ Selenium form submission successful!")
                    sms_success = True
                    email_success = True
                else:
                    print(f"   ⚠️ Selenium form response: {selenium_submit_response.text[:200]}...")
        
        # Summary
        print(f"\n📊 API Working Flow Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_success else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if email_success else '❌ Failed'}")
        
        if sms_success or email_success:
            print("\n🎉 At least one message was sent successfully via API!")
        else:
            print("\n⚠️ No messages were delivered via API.")
            
    except Exception as e:
        print(f"❌ Error during API working flow: {e}")

if __name__ == "__main__":
    send_message_api_working_flow() 