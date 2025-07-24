#!/usr/bin/env python3
"""
Correct messaging flow that replicates the exact Selenium steps
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
SMS_MESSAGE = "🎉 This is a REAL SMS sent via correct API flow!"
EMAIL_MESSAGE = "🎉 This is a REAL EMAIL sent via correct API flow!"

def get_secret(key):
    """Get secret from config"""
    try:
        from config.secrets_local import get_secret as get_secret_func
        return get_secret_func(key)
    except:
        return None

def send_message_correct_flow():
    """Send messages using the correct flow that replicates Selenium"""
    
    print("🚀 CORRECT MESSAGING FLOW")
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
        
        # Step 5: Get the messaging popup form
        print("📤 Step 5: Getting messaging popup form...")
        
        # The messaging form is loaded via AJAX when the Send Message button is clicked
        # We need to trigger the popup first
        popup_trigger_url = f"{BASE_URL}/action/FollowUp/popup"
        popup_data = {
            'memberId': TARGET_MEMBER_ID,
            'actAs': 'loggedIn'
        }
        
        popup_response = session.post(popup_trigger_url, data=popup_data)
        popup_response.raise_for_status()
        
        # Save popup response for debugging
        with open('popup_form_debug.html', 'w', encoding='utf-8') as f:
            f.write(popup_response.text)
        
        print(f"   📊 Popup Response Status: {popup_response.status_code}")
        print(f"   📊 Popup Response URL: {popup_response.url}")
        
        # Parse the popup form to get the correct form fields
        popup_soup = BeautifulSoup(popup_response.text, 'html.parser')
        
        # Find the form in the popup
        popup_form = popup_soup.find('form')
        if not popup_form:
            print("   ❌ No form found in popup response")
            return
        
        # Get the form action URL
        form_action = popup_form.get('action')
        if not form_action:
            form_action = f"{BASE_URL}/action/FollowUp/save"
        
        print(f"   📝 Form action: {form_action}")
        
        # Get all form fields
        form_fields = {}
        for input_field in popup_form.find_all('input'):
            name = input_field.get('name')
            value = input_field.get('value', '')
            if name:
                form_fields[name] = value
                print(f"   📝 Form field: {name} = {value}")
        
        # Step 6: Send SMS
        print("📱 Step 6: Sending SMS...")
        
        # Add SMS-specific fields
        sms_data = form_fields.copy()
        sms_data.update({
            'textMessage': SMS_MESSAGE,
            'followUpOutcomeNotes': 'Correct flow SMS test',
            'followUpType': 'text',
            'followUpWith': 'SMS'
        })
        
        sms_response = session.post(form_action, data=sms_data)
        sms_response.raise_for_status()
        
        # Save response for debugging
        with open('sms_response_correct_flow.html', 'w', encoding='utf-8') as f:
            f.write(sms_response.text)
        
        print(f"   📊 SMS Response Status: {sms_response.status_code}")
        print(f"   📊 SMS Response URL: {sms_response.url}")
        
        # Check if SMS was successful
        if "has been texted" in sms_response.text:
            print("   ✅ SMS sent successfully!")
        else:
            print("   ❌ SMS failed - check sms_response_correct_flow.html")
        
        # Step 7: Send Email
        print("📧 Step 7: Sending Email...")
        
        # Get fresh popup form for email
        popup_response = session.post(popup_trigger_url, data=popup_data)
        popup_response.raise_for_status()
        
        popup_soup = BeautifulSoup(popup_response.text, 'html.parser')
        popup_form = popup_soup.find('form')
        
        if popup_form:
            form_fields = {}
            for input_field in popup_form.find_all('input'):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_fields[name] = value
        
        # Add email-specific fields
        email_data = form_fields.copy()
        email_data.update({
            'emailSubject': 'Correct Flow Test Email',
            'emailBody': EMAIL_MESSAGE,
            'followUpOutcomeNotes': 'Correct flow email test',
            'followUpType': 'email',
            'followUpWith': 'Email'
        })
        
        email_response = session.post(form_action, data=email_data)
        email_response.raise_for_status()
        
        # Save response for debugging
        with open('email_response_correct_flow.html', 'w', encoding='utf-8') as f:
            f.write(email_response.text)
        
        print(f"   📊 Email Response Status: {email_response.status_code}")
        print(f"   📊 Email Response URL: {email_response.url}")
        
        # Check if Email was successful
        if "has been emailed" in email_response.text or "email sent" in email_response.text.lower():
            print("   ✅ Email sent successfully!")
        else:
            print("   ❌ Email failed - check email_response_correct_flow.html")
        
        print(f"\n🎉 CORRECT FLOW SUMMARY:")
        print(f"   ✅ Used proper login form fields")
        print(f"   ✅ Triggered messaging popup correctly")
        print(f"   ✅ Extracted form fields from popup")
        print(f"   ✅ Submitted to correct endpoints")
        print(f"   📧 Check your phone and email for the messages!")
        
    except Exception as e:
        print(f"❌ Error during API implementation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_message_correct_flow() 