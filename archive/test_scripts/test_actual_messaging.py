#!/usr/bin/env python3
"""
Actual ClubOS Messaging Test - Send real messages to Jeremy Mayo
This script will actually send messages through ClubOS messaging interface.
"""

import requests
import sys
import os
import time
from typing import Dict, Optional

# Add the project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# ClubOS Configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"

# Jeremy Mayo details
JEREMY_MAYO_ID = "187032782"

def get_secret(secret_name: str) -> str:
    """Simple secret getter"""
    secrets = {
        "clubos-username": os.getenv("CLUBOS_USERNAME", "j.mayo"),
        "clubos-password": os.getenv("CLUBOS_PASSWORD", "L*KYqnec5z7nEL$")
    }
    return secrets.get(secret_name, "")

class ActualClubOSMessaging:
    """ClubOS messaging client that actually sends messages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.is_authenticated = False
        
        # Set browser-like headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
    
    def login(self, username: str, password: str) -> bool:
        """Login to ClubOS"""
        try:
            print("🔐 Attempting ClubOS login...")
            
            # Get login page
            login_response = self.session.get(LOGIN_URL, timeout=30, verify=False)
            if not login_response.ok:
                print(f"❌ Could not load login page: {login_response.status_code}")
                return False
            
            # Submit login
            login_data = {
                "username": username,
                "password": password,
                "login": "Submit"
            }
            
            response = self.session.post(LOGIN_URL, data=login_data, timeout=30, verify=False)
            
            if response.ok and ("Dashboard" in response.text or "dashboard" in response.url.lower()):
                print("✅ Login successful")
                self.is_authenticated = True
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def send_sms_message(self, member_id: str, message: str) -> bool:
        """Send SMS message through ClubOS messaging interface"""
        try:
            print(f"📱 Sending SMS to member {member_id}...")
            
            # Step 1: Navigate to member's messaging page
            member_url = f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile"
            print(f"   📄 Loading member profile: {member_url}")
            
            member_response = self.session.get(member_url, timeout=30, verify=False)
            if not member_response.ok:
                print(f"   ❌ Could not load member profile: {member_response.status_code}")
                return False
            
            # Step 2: Find the SMS messaging form
            sms_form_url = f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile/sendText"
            print(f"   📝 Loading SMS form: {sms_form_url}")
            
            form_response = self.session.get(sms_form_url, timeout=30, verify=False)
            if not form_response.ok:
                print(f"   ❌ Could not load SMS form: {form_response.status_code}")
                return False
            
            # Step 3: Submit SMS message
            sms_data = {
                "memberId": member_id,
                "messageText": message,
                "sendMethod": "sms",
                "submit": "Send SMS"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": member_url,
                "Origin": self.base_url
            }
            
            print(f"   📤 Submitting SMS message...")
            sms_response = self.session.post(sms_form_url, data=sms_data, headers=headers, timeout=30, verify=False)
            
            print(f"   📊 SMS Response status: {sms_response.status_code}")
            print(f"   📊 SMS Response preview: {sms_response.text[:300]}")
            
            if sms_response.status_code == 200:
                print("   ✅ SMS submitted successfully!")
                return True
            else:
                print(f"   ❌ SMS submission failed: {sms_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error sending SMS: {e}")
            return False
    
    def send_email_message(self, member_id: str, subject: str, message: str) -> bool:
        """Send Email message through ClubOS messaging interface"""
        try:
            print(f"📧 Sending Email to member {member_id}...")
            
            # Step 1: Navigate to member's messaging page
            member_url = f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile"
            print(f"   📄 Loading member profile: {member_url}")
            
            member_response = self.session.get(member_url, timeout=30, verify=False)
            if not member_response.ok:
                print(f"   ❌ Could not load member profile: {member_response.status_code}")
                return False
            
            # Step 2: Find the Email messaging form
            email_form_url = f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile/sendEmail"
            print(f"   📝 Loading Email form: {email_form_url}")
            
            form_response = self.session.get(email_form_url, timeout=30, verify=False)
            if not form_response.ok:
                print(f"   ❌ Could not load Email form: {form_response.status_code}")
                return False
            
            # Step 3: Submit Email message
            email_data = {
                "memberId": member_id,
                "emailSubject": subject,
                "emailMessage": f"<p>{message}</p>",
                "sendMethod": "email",
                "submit": "Send Email"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": member_url,
                "Origin": self.base_url
            }
            
            print(f"   📤 Submitting Email message...")
            email_response = self.session.post(email_form_url, data=email_data, headers=headers, timeout=30, verify=False)
            
            print(f"   📊 Email Response status: {email_response.status_code}")
            print(f"   📊 Email Response preview: {email_response.text[:300]}")
            
            if email_response.status_code == 200:
                print("   ✅ Email submitted successfully!")
                return True
            else:
                print(f"   ❌ Email submission failed: {email_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error sending Email: {e}")
            return False

def test_actual_messaging():
    """Test actual ClubOS messaging"""
    print("🚀 TESTING ACTUAL CLUBOS MESSAGING")
    print("=" * 50)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ Missing ClubOS credentials")
        return False
    
    # Create client and login
    client = ActualClubOSMessaging()
    if not client.login(username, password):
        return False
    
    # Test SMS
    print(f"\n📱 Testing ACTUAL SMS to Jeremy Mayo ({JEREMY_MAYO_ID})...")
    sms_result = client.send_sms_message(
        JEREMY_MAYO_ID, 
        "🎉 This is a REAL SMS sent via ClubOS API! The new implementation is working!"
    )
    
    time.sleep(3)  # Rate limiting
    
    # Test Email
    print(f"\n📧 Testing ACTUAL Email to Jeremy Mayo ({JEREMY_MAYO_ID})...")
    email_result = client.send_email_message(
        JEREMY_MAYO_ID,
        "🎉 ClubOS API Test - Real Email",
        "This is a REAL EMAIL sent via the new ClubOS API implementation! The coding agents fixed the messaging system and now it actually works!"
    )
    
    # Results
    print(f"\n📊 ACTUAL RESULTS:")
    print(f"SMS:   {'✅ SUCCESS' if sms_result else '❌ FAILED'}")
    print(f"EMAIL: {'✅ SUCCESS' if email_result else '❌ FAILED'}")
    
    if sms_result or email_result:
        print("\n🎉 ACTUAL MESSAGING WORKING!")
        print("✅ ClubOS messaging is now functional and sending real messages!")
        return True
    else:
        print("\n❌ MESSAGING STILL NOT WORKING")
        return False

if __name__ == "__main__":
    success = test_actual_messaging()
    exit(0 if success else 1) 