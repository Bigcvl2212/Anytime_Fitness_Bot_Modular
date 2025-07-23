#!/usr/bin/env python3
"""
API solution that replicates the exact form submission that works in the web interface
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from urllib.parse import urljoin
from config.secrets_local import get_secret
import re

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "API form submission SMS test - this should work!"
EMAIL_MESSAGE = "API form submission email test - this should work!"

def send_message_api_form_submission():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Setting up API form submission...")
        
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
        
        # Step 1: Navigate to dashboard
        print("   📊 Navigating to dashboard...")
        dashboard_response = session.get(f"{base_url}/action/Dashboard/view")
        if dashboard_response.status_code != 200:
            print(f"   ❌ Dashboard navigation failed")
            return
        
        print("   ✅ Dashboard loaded successfully!")
        
        # Step 2: Search for Jeremy Mayo to get the proper member context
        print(f"   🔍 Searching for {TARGET_NAME}...")
        search_url = f"{base_url}/action/Dashboard/search"
        search_response = session.get(search_url)
        
        if search_response.status_code != 200:
            print(f"   ❌ Search page failed")
            return
        
        # Extract CSRF token if present
        csrf_token = None
        csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', search_response.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   ✅ Found CSRF token")
        
        # Step 3: Navigate to Jeremy's profile page
        print(f"   👤 Navigating to {TARGET_NAME}'s profile...")
        profile_url = f"{base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = session.get(profile_url)
        
        if profile_response.status_code != 200:
            print(f"   ❌ Profile navigation failed")
            return
        
        print("   ✅ Member profile loaded successfully!")
        
        # Extract any additional tokens from the profile page
        profile_csrf_token = None
        csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', profile_response.text)
        if csrf_match:
            profile_csrf_token = csrf_match.group(1)
            print(f"   ✅ Found profile CSRF token")
        
        # Use the most recent CSRF token
        final_csrf_token = profile_csrf_token or csrf_token
        
        # Step 4: Try form submission to the profile page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": profile_url,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        if final_csrf_token:
            headers["X-CSRF-Token"] = final_csrf_token
        
        # Try SMS form submission
        print(f"\n📤 Sending SMS to {TARGET_NAME} via form submission...")
        sms_success = False
        
        sms_form_data = {
            "memberId": MEMBER_ID,
            "textMessage": SMS_MESSAGE,
            "followUpOutcomeNotes": "API SMS sent by Gym Bot"
        }
        
        if final_csrf_token:
            sms_form_data["csrf_token"] = final_csrf_token
        
        sms_response = session.post(profile_url, data=sms_form_data, headers=headers)
        
        print(f"   🔍 SMS Form Response:")
        print(f"      Status: {sms_response.status_code}")
        print(f"      Response length: {len(sms_response.text)} chars")
        
        if sms_response.status_code == 200:
            if "success" in sms_response.text.lower() or "sent" in sms_response.text.lower():
                print("   ✅ SMS sent successfully via form submission!")
                sms_success = True
            else:
                print(f"   ⚠️ SMS response: {sms_response.text[:200]}...")
        elif sms_response.status_code == 302:
            print("   ⚠️ SMS got redirect - checking if it was successful")
            # Check if we got redirected to a success page
            if "success" in sms_response.headers.get("Location", "").lower():
                print("   ✅ SMS redirect indicates success!")
                sms_success = True
        
        # Try Email form submission
        print(f"\n📤 Sending Email to {TARGET_NAME} via form submission...")
        email_success = False
        
        email_form_data = {
            "memberId": MEMBER_ID,
            "emailMessage": EMAIL_MESSAGE,
            "emailSubject": "API Form Submission Test",
            "followUpOutcomeNotes": "API Email sent by Gym Bot"
        }
        
        if final_csrf_token:
            email_form_data["csrf_token"] = final_csrf_token
        
        email_response = session.post(profile_url, data=email_form_data, headers=headers)
        
        print(f"   🔍 Email Form Response:")
        print(f"      Status: {email_response.status_code}")
        print(f"      Response length: {len(email_response.text)} chars")
        
        if email_response.status_code == 200:
            if "success" in email_response.text.lower() or "sent" in email_response.text.lower():
                print("   ✅ Email sent successfully via form submission!")
                email_success = True
            else:
                print(f"   ⚠️ Email response: {email_response.text[:200]}...")
        elif email_response.status_code == 302:
            print("   ⚠️ Email got redirect - checking if it was successful")
            # Check if we got redirected to a success page
            if "success" in email_response.headers.get("Location", "").lower():
                print("   ✅ Email redirect indicates success!")
                email_success = True
        
        # If form submission doesn't work, try the follow-up endpoint with proper context
        if not sms_success and not email_success:
            print(f"\n🔄 Trying follow-up endpoint with proper context...")
            
            # First navigate to the follow-up page
            followup_url = f"{base_url}/action/Dashboard/follow-up"
            followup_response = session.get(followup_url)
            
            if followup_response.status_code == 200:
                print("   ✅ Follow-up page loaded")
                
                # Try submitting to follow-up endpoint
                followup_data = {
                    "memberId": MEMBER_ID,
                    "textMessage": SMS_MESSAGE,
                    "emailMessage": EMAIL_MESSAGE,
                    "followUpOutcomeNotes": "Follow-up test"
                }
                
                if final_csrf_token:
                    followup_data["csrf_token"] = final_csrf_token
                
                followup_submit_response = session.post(followup_url, data=followup_data, headers=headers)
                
                print(f"   🔍 Follow-up Submit Response:")
                print(f"      Status: {followup_submit_response.status_code}")
                print(f"      Response: {followup_submit_response.text[:200]}...")
                
                if followup_submit_response.status_code == 200:
                    if "success" in followup_submit_response.text.lower():
                        print("   ✅ Follow-up submission successful!")
                        sms_success = True
                        email_success = True
        
        # Summary
        print(f"\n📊 API Form Submission Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_success else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if email_success else '❌ Failed'}")
        
        if sms_success or email_success:
            print("\n🎉 At least one message was sent successfully via API form submission!")
        else:
            print("\n⚠️ No messages were delivered via API form submission.")
            
    except Exception as e:
        print(f"❌ Error during API form submission: {e}")

if __name__ == "__main__":
    send_message_api_form_submission() 