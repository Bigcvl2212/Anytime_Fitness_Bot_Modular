#!/usr/bin/env python3
"""
Simple test for fixed ClubOS messaging - minimal dependencies
Tests the fixed implementation without importing other modules that have dependencies.
"""

import requests
import sys
import os
import time
from typing import Dict, Optional

# Add the project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# ClubOS Configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"

# Jeremy Mayo details
JEREMY_MAYO_ID = "187032782"

def get_secret(secret_name: str) -> str:
    """Simple secret getter - replace with actual implementation"""
    # For testing, these would need to be provided
    secrets = {
        "clubos-username": os.getenv("CLUBOS_USERNAME", ""),
        "clubos-password": os.getenv("CLUBOS_PASSWORD", "")
    }
    return secrets.get(secret_name, "")

class SimpleClubOSClient:
    """Simplified ClubOS client for testing"""
    
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
            login_response = self.session.get(LOGIN_URL, timeout=30)
            if not login_response.ok:
                print(f"❌ Could not load login page: {login_response.status_code}")
                return False
            
            # Submit login
            login_data = {
                "username": username,
                "password": password,
                "login": "Submit"
            }
            
            response = self.session.post(LOGIN_URL, data=login_data, timeout=30)
            
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
    
    def send_message_via_followup(self, member_id: str, message: str, message_type: str) -> bool:
        """Send message using /action/FollowUp/save endpoint"""
        try:
            print(f"📤 Sending {message_type} via FollowUp endpoint...")
            
            endpoint = "/action/FollowUp/save"
            url = f"{self.base_url}{endpoint}"
            
            if message_type == "text":
                action_code = "3"  # SMS
                form_data = {
                    "followUpStatus": "1",
                    "followUpType": "3",
                    "memberSalesFollowUpStatus": "6",
                    "followUpLog.tfoUserId": member_id,
                    "followUpLog.outcome": "3",
                    "textMessage": message,
                    "event.createdFor.tfoUserId": member_id,
                    "event.eventType": "ORIENTATION",
                    "duration": "2",
                    "event.remindAttendeesMins": "120",
                    "followUpUser.tfoUserId": member_id,
                    "followUpUser.role.id": "7",
                    "followUpUser.clubId": "291",
                    "followUpUser.clubLocationId": "3586",
                    "followUpLog.followUpAction": action_code,
                    "memberStudioSalesDefaultAccount": member_id,
                    "memberStudioSupportDefaultAccount": member_id,
                    "ptSalesDefaultAccount": member_id,
                    "ptSupportDefaultAccount": member_id
                }
            else:  # email
                action_code = "2"  # Email
                form_data = {
                    "followUpStatus": "1",
                    "followUpType": "3",
                    "memberSalesFollowUpStatus": "6",
                    "followUpLog.tfoUserId": member_id,
                    "followUpLog.outcome": "2",
                    "emailSubject": "Message from ClubOS API",
                    "emailMessage": f"<p>{message}</p>",
                    "event.createdFor.tfoUserId": member_id,
                    "event.eventType": "ORIENTATION",
                    "duration": "2",
                    "event.remindAttendeesMins": "120",
                    "followUpUser.tfoUserId": member_id,
                    "followUpUser.role.id": "7",
                    "followUpUser.clubId": "291",
                    "followUpUser.clubLocationId": "3586",
                    "followUpLog.followUpAction": action_code,
                    "memberStudioSalesDefaultAccount": member_id,
                    "memberStudioSupportDefaultAccount": member_id,
                    "ptSalesDefaultAccount": member_id,
                    "ptSupportDefaultAccount": member_id
                }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"{self.base_url}/action/Dashboard/view",
                "Origin": self.base_url
            }
            
            response = self.session.post(url, data=form_data, headers=headers, timeout=30)
            
            print(f"   Response status: {response.status_code}")
            print(f"   Response preview: {response.text[:200]}")
            
            if response.status_code == 200:
                print(f"✅ {message_type.upper()} sent successfully!")
                return True
            else:
                print(f"❌ {message_type.upper()} failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending {message_type}: {e}")
            return False

def test_messaging():
    """Test ClubOS messaging"""
    print("🚀 TESTING FIXED CLUBOS MESSAGING")
    print("=" * 50)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ Missing ClubOS credentials")
        print("   Set CLUBOS_USERNAME and CLUBOS_PASSWORD environment variables")
        return False
    
    # Create client and login
    client = SimpleClubOSClient()
    if not client.login(username, password):
        return False
    
    # Test SMS
    print(f"\n📱 Testing SMS to Jeremy Mayo ({JEREMY_MAYO_ID})...")
    sms_result = client.send_message_via_followup(
        JEREMY_MAYO_ID, 
        "Test SMS from FIXED ClubOS API - form submission working!", 
        "text"
    )
    
    time.sleep(2)  # Rate limiting
    
    # Test Email
    print(f"\n📧 Testing Email to Jeremy Mayo ({JEREMY_MAYO_ID})...")
    email_result = client.send_message_via_followup(
        JEREMY_MAYO_ID,
        "Test Email from FIXED ClubOS API - the API endpoints were failing but form submission works!",
        "email"
    )
    
    # Results
    print(f"\n📊 RESULTS:")
    print(f"SMS:   {'✅ SUCCESS' if sms_result else '❌ FAILED'}")
    print(f"EMAIL: {'✅ SUCCESS' if email_result else '❌ FAILED'}")
    
    if sms_result or email_result:
        print("\n🎉 SOLUTION WORKING!")
        print("✅ ClubOS messaging via form submission is functional")
        return True
    else:
        print("\n❌ SOLUTION NEEDS MORE WORK")
        return False

if __name__ == "__main__":
    success = test_messaging()
    exit(0 if success else 1)