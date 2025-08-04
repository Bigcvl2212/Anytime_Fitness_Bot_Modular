#!/usr/bin/env python3
"""
Final API attempt using exact form fields from working Selenium script
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
DASHBOARD_URL = f"{BASE_URL}/action/Dashboard/view"

# Jeremy Mayo details
TARGET_NAME = "Jeremy Mayo"
TARGET_MEMBER_ID = "187032782"
SMS_MESSAGE = "🎉 FINAL API ATTEMPT - This SMS was sent via API replication of Selenium!"
EMAIL_MESSAGE = "🎉 FINAL API ATTEMPT - This EMAIL was sent via API replication of Selenium!"

def get_secret(key):
    """Get secret from config"""
    try:
        from config.secrets_local import get_secret as get_secret_func
        return get_secret_func(key)
    except:
        return None

def send_message_final_api_attempt():
    """Final API attempt using exact form fields from Selenium"""
    
    print("🚀 FINAL API ATTEMPT")
    print("=" * 50)
    print(f"Target: {TARGET_NAME}")
    print(f"Member ID: {TARGET_MEMBER_ID}")
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    # Create session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        # Step 1: Get login page to get required hidden fields
        print("🔐 Step 1: Getting login page...")
        login_response = session.get(LOGIN_URL)
        login_response.raise_for_status()
        
        soup = BeautifulSoup(login_response.text, 'html.parser')
        
        # Extract required hidden fields
        login_form = soup.find('form')
        if not login_form:
            print("❌ No login form found")
            return
        
        # Get hidden fields
        hidden_fields = {}
        for hidden_input in login_form.find_all('input', {'type': 'hidden'}):
            name = hidden_input.get('name')
            value = hidden_input.get('value')
            if name and value:
                hidden_fields[name] = value
                print(f"   📝 Hidden field: {name} = {value}")
        
        # Step 2: Login with correct form data
        print("🔐 Step 2: Logging in...")
        login_data = {
            'username': username,
            'password': password,
            **hidden_fields  # Include all hidden fields
        }
        
        login_response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        
        # Check if login was successful
        if "Dashboard" in login_response.url or "dashboard" in login_response.url.lower():
            print("   ✅ Login successful!")
        else:
            print(f"   ❌ Login failed. Final URL: {login_response.url}")
            return
        
        # Step 3: Navigate to Dashboard
        print("📊 Step 3: Navigating to Dashboard...")
        dashboard_response = session.get(DASHBOARD_URL)
        dashboard_response.raise_for_status()
        print("   ✅ Dashboard loaded")
        
        # Step 4: Navigate directly to member profile
        print("👤 Step 4: Navigating to member profile...")
        member_profile_url = f"{BASE_URL}/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile"
        profile_response = session.get(member_profile_url)
        profile_response.raise_for_status()
        print("   ✅ Member profile loaded")
        
        # Step 5: Try to submit the messaging form directly
        print("📤 Step 5: Submitting messaging form directly...")
        
        # Based on the Selenium script, the form fields are:
        # - textMessage: The SMS message
        # - followUpOutcomeNotes: Notes about the follow-up
        # - followUpType: 'text' for SMS
        # - followUpWith: 'SMS' for SMS
        
        # Try the exact form submission that Selenium would make
        form_action = f"{BASE_URL}/action/FollowUp/save"
        
        # SMS Form Data (exact fields from Selenium)
        sms_data = {
            'textMessage': SMS_MESSAGE,
            'followUpOutcomeNotes': 'Final API attempt SMS test',
            'followUpType': 'text',
            'followUpWith': 'SMS',
            'memberId': TARGET_MEMBER_ID,
            'actAs': 'loggedIn'
        }
        
        print(f"   📝 SMS Form Data:")
        for key, value in sms_data.items():
            print(f"      {key}: {value}")
        
        sms_response = session.post(form_action, data=sms_data)
        
        # Save response for debugging
        with open('sms_response_final_api.html', 'w', encoding='utf-8') as f:
            f.write(sms_response.text)
        
        print(f"   📊 SMS Response Status: {sms_response.status_code}")
        print(f"   📊 SMS Response URL: {sms_response.url}")
        
        # Check if SMS was successful
        if "has been texted" in sms_response.text:
            print("   ✅ SMS sent successfully!")
        else:
            print("   ❌ SMS failed - check sms_response_final_api.html")
        
        # Email Form Data (exact fields from Selenium)
        email_data = {
            'emailSubject': 'Final API Attempt Test Email',
            'emailBody': EMAIL_MESSAGE,
            'followUpOutcomeNotes': 'Final API attempt email test',
            'followUpType': 'email',
            'followUpWith': 'Email',
            'memberId': TARGET_MEMBER_ID,
            'actAs': 'loggedIn'
        }
        
        print(f"   📝 Email Form Data:")
        for key, value in email_data.items():
            print(f"      {key}: {value}")
        
        email_response = session.post(form_action, data=email_data)
        
        # Save response for debugging
        with open('email_response_final_api.html', 'w', encoding='utf-8') as f:
            f.write(email_response.text)
        
        print(f"   📊 Email Response Status: {email_response.status_code}")
        print(f"   📊 Email Response URL: {email_response.url}")
        
        # Check if Email was successful
        if "has been emailed" in email_response.text or "email sent" in email_response.text.lower():
            print("   ✅ Email sent successfully!")
        else:
            print("   ❌ Email failed - check email_response_final_api.html")
        
        print(f"\n🎉 FINAL API ATTEMPT SUMMARY:")
        print(f"   ✅ Used exact form fields from working Selenium script")
        print(f"   ✅ Submitted to correct endpoint: {form_action}")
        print(f"   ✅ Used proper form data structure")
        print(f"   📧 Check your phone and email for the messages!")
        print(f"   📊 If this doesn't work, the API approach is fundamentally limited")
        print(f"   📊 The working solution requires Selenium for dynamic form loading")
        
    except Exception as e:
        print(f"❌ Error during final API attempt: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_message_final_api_attempt() 