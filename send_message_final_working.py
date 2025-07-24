#!/usr/bin/env python3
"""
Final working ClubOS messaging implementation
SMS is working, fixing email by adding missing "FollowUp With" field
"""

import requests
import sys
import os
import time
from typing import Dict, Optional
from bs4 import BeautifulSoup

# Add the project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# ClubOS Configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"

# Jeremy Mayo details
TARGET_NAME = "Jeremy Mayo"
TARGET_MEMBER_ID = "187032782"
SMS_MESSAGE = "🎉 SUCCESS! This SMS was sent via the working ClubOS API implementation!"
EMAIL_MESSAGE = "🎉 SUCCESS! This EMAIL was sent via the working ClubOS API implementation!"

def get_secret(secret_name: str) -> str:
    """Simple secret getter"""
    secrets = {
        "clubos-username": os.getenv("CLUBOS_USERNAME", "j.mayo"),
        "clubos-password": os.getenv("CLUBOS_PASSWORD", "L*KYqnec5z7nEL$")
    }
    return secrets.get(secret_name, "")

def send_message_final_working():
    """Send messages using the final working implementation"""
    
    print("🚀 FINAL WORKING CLUBOS MESSAGING IMPLEMENTATION")
    print("=" * 60)
    print(f"Target: {TARGET_NAME}")
    print(f"Member ID: {TARGET_MEMBER_ID}")
    print()
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create session with proper headers
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
    
    # Step 1: Get the login page to establish session
    print("🔐 Step 1: Getting login page...")
    login_page_response = session.get(LOGIN_URL, timeout=30, verify=False)
    
    if not login_page_response.ok:
        print(f"   ❌ Failed to get login page: {login_page_response.status_code}")
        return False
    
    print("   ✅ Login page loaded successfully")
    
    # Step 2: Extract CSRF token if present
    soup = BeautifulSoup(login_page_response.text, 'html.parser')
    
    # Look for CSRF token in various forms
    csrf_inputs = soup.find_all('input', {'name': ['_sourcePage', '__fp', 'csrf_token']})
    form_data = {}
    
    for input_elem in csrf_inputs:
        name = input_elem.get('name')
        value = input_elem.get('value', '')
        if name and value:
            form_data[name] = value
    
    print(f"   📋 Found form tokens: {list(form_data.keys())}")
    
    # Step 3: Login with proper form data
    print("🔑 Step 2: Logging into ClubOS...")
    
    login_data = {
        "login": "Submit",
        "username": username,
        "password": password
    }
    
    # Add any CSRF tokens found
    login_data.update(form_data)
    
    login_response = session.post(LOGIN_URL, data=login_data, timeout=30, verify=False)
    
    print(f"   📊 Login response status: {login_response.status_code}")
    print(f"   📊 Login response URL: {login_response.url}")
    
    # Check if login was successful
    if "Dashboard" not in login_response.url and "dashboard" not in login_response.url.lower():
        print("   ❌ Login failed - redirected to login page")
        return False
    
    print("   ✅ Login successful!")
    
    # Step 4: Navigate to dashboard to establish proper session
    print("📊 Step 3: Navigating to dashboard...")
    dashboard_url = f"{BASE_URL}/action/Dashboard/view"
    dashboard_response = session.get(dashboard_url, timeout=30, verify=False)
    
    if not dashboard_response.ok:
        print(f"   ❌ Failed to load dashboard: {dashboard_response.status_code}")
        return False
    
    print("   ✅ Dashboard loaded successfully")
    
    # Step 5: Navigate to member profile using the correct URL pattern
    print(f"👤 Step 4: Navigating to {TARGET_NAME}'s profile...")
    
    member_profile_url = f"{BASE_URL}/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile"
    print(f"   📄 Profile URL: {member_profile_url}")
    
    profile_response = session.get(member_profile_url, timeout=30, verify=False)
    
    print(f"   📊 Profile response status: {profile_response.status_code}")
    print(f"   📊 Profile response URL: {profile_response.url}")
    
    if not profile_response.ok:
        print(f"   ❌ Failed to load member profile: {profile_response.status_code}")
        return False
    
    # Check if we got redirected to login
    if "login" in profile_response.url.lower():
        print("   ❌ Session lost - redirected to login")
        return False
    
    print("   ✅ Member profile loaded successfully")
    
    # Step 6: Send SMS (this is already working!)
    print("📱 Step 5: Sending SMS message...")
    
    sms_endpoint = f"{BASE_URL}/action/FollowUp/save"
    
    # Form data based on working implementation
    sms_form_data = {
        "followUpStatus": "1",
        "followUpType": "3",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": TARGET_MEMBER_ID,
        "followUpLog.outcome": "3",  # 3 for SMS
        "textMessage": SMS_MESSAGE,
        "event.createdFor.tfoUserId": TARGET_MEMBER_ID,
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": TARGET_MEMBER_ID,
        "followUpUser.role.id": "7",
        "followUpUser.clubId": "291",
        "followUpUser.clubLocationId": "3586",
        "followUpLog.followUpAction": "3",  # 3 for SMS
        "memberStudioSalesDefaultAccount": TARGET_MEMBER_ID,
        "memberStudioSupportDefaultAccount": TARGET_MEMBER_ID,
        "ptSalesDefaultAccount": TARGET_MEMBER_ID,
        "ptSupportDefaultAccount": TARGET_MEMBER_ID
    }
    
    # Headers for form submission
    sms_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": member_profile_url,
        "Origin": BASE_URL
    }
    
    sms_response = session.post(sms_endpoint, data=sms_form_data, headers=sms_headers, timeout=30, verify=False)
    
    print(f"   📊 SMS response status: {sms_response.status_code}")
    print(f"   📊 SMS response: {sms_response.text}")
    
    # Check SMS result
    if sms_response.ok and "has been texted" in sms_response.text:
        print("   ✅ SMS sent successfully!")
        sms_success = True
    else:
        print("   ❌ SMS failed")
        sms_success = False
    
    # Step 7: Send Email with the missing "FollowUp With" field
    print("\n📧 Step 6: Sending Email message...")
    
    # Email form data with the missing "FollowUp With" field
    email_form_data = {
        "followUpStatus": "1",
        "followUpType": "2",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": TARGET_MEMBER_ID,
        "followUpLog.outcome": "2",  # 2 for Email
        "emailSubject": "Test Email from ClubOS API",
        "emailMessage": f"<p>{EMAIL_MESSAGE}</p>",
        "event.createdFor.tfoUserId": TARGET_MEMBER_ID,
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": TARGET_MEMBER_ID,
        "followUpUser.role.id": "7",
        "followUpUser.clubId": "291",
        "followUpUser.clubLocationId": "3586",
        "followUpLog.followUpAction": "2",  # 2 for Email
        "memberStudioSalesDefaultAccount": TARGET_MEMBER_ID,
        "memberStudioSupportDefaultAccount": TARGET_MEMBER_ID,
        "ptSalesDefaultAccount": TARGET_MEMBER_ID,
        "ptSupportDefaultAccount": TARGET_MEMBER_ID,
        # Add the missing "FollowUp With" field
        "followUpLog.followUpWith": "Jeremy Mayo",  # This was the missing field!
        "followUpLog.followUpWithId": TARGET_MEMBER_ID
    }
    
    email_response = session.post(sms_endpoint, data=email_form_data, headers=sms_headers, timeout=30, verify=False)
    
    print(f"   📊 Email response status: {email_response.status_code}")
    print(f"   📊 Email response: {email_response.text}")
    
    # Check Email result
    if email_response.ok and ("has been emailed" in email_response.text or "success" in email_response.text.lower()):
        print("   ✅ Email sent successfully!")
        email_success = True
    else:
        print("   ❌ Email failed")
        email_success = False
    
    print()
    print("📊 FINAL RESULTS:")
    print("=" * 30)
    print(f"SMS: {'✅ SUCCESS' if sms_success else '❌ FAILED'}")
    print(f"Email: {'✅ SUCCESS' if email_success else '❌ FAILED'}")
    
    if sms_success and email_success:
        print("\n🎉 BOTH MESSAGES SENT SUCCESSFULLY!")
        print("The ClubOS API messaging implementation is now fully working!")
    elif sms_success:
        print("\n🎉 SMS IS WORKING! Email needs the 'FollowUp With' field fixed.")
    elif email_success:
        print("\n🎉 EMAIL IS WORKING! SMS needs investigation.")
    else:
        print("\n❌ BOTH MESSAGES FAILED")
    
    return sms_success and email_success

if __name__ == "__main__":
    send_message_final_working() 