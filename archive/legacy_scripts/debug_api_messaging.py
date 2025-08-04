#!/usr/bin/env python3
"""
Debug ClubOS API Messaging - Investigate why messages aren't being sent
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

class ClubOSAPIDebugger:
    """Debug ClubOS API messaging to understand why it's not working"""
    
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
            
            print(f"   📄 Login page loaded: {login_response.status_code}")
            
            # Submit login
            login_data = {
                "username": username,
                "password": password,
                "login": "Submit"
            }
            
            response = self.session.post(LOGIN_URL, data=login_data, timeout=30, verify=False)
            
            print(f"   📊 Login response status: {response.status_code}")
            print(f"   📊 Login response URL: {response.url}")
            print(f"   📊 Login response preview: {response.text[:500]}")
            
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
    
    def debug_member_profile(self, member_id: str):
        """Debug member profile page to understand the messaging interface"""
        try:
            print(f"\n🔍 DEBUGGING MEMBER PROFILE: {member_id}")
            
            # Step 1: Get member profile page
            member_url = f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile"
            print(f"   📄 Loading member profile: {member_url}")
            
            member_response = self.session.get(member_url, timeout=30, verify=False)
            print(f"   📊 Member profile status: {member_response.status_code}")
            print(f"   📊 Member profile URL: {member_response.url}")
            
            if not member_response.ok:
                print(f"   ❌ Could not load member profile: {member_response.status_code}")
                return False
            
            # Save the HTML for analysis
            with open("debug_member_profile.html", "w", encoding="utf-8") as f:
                f.write(member_response.text)
            print("   💾 Saved member profile HTML to debug_member_profile.html")
            
            # Look for messaging elements
            html_content = member_response.text
            
            # Check for "Send Message" button
            if "Send Message" in html_content:
                print("   ✅ Found 'Send Message' button in HTML")
            else:
                print("   ❌ 'Send Message' button not found in HTML")
            
            # Check for messaging forms
            if "sendText" in html_content:
                print("   ✅ Found 'sendText' references in HTML")
            else:
                print("   ❌ 'sendText' not found in HTML")
            
            if "sendEmail" in html_content:
                print("   ✅ Found 'sendEmail' references in HTML")
            else:
                print("   ❌ 'sendEmail' not found in HTML")
            
            # Check for form elements
            if "form" in html_content.lower():
                print("   ✅ Found form elements in HTML")
            else:
                print("   ❌ No form elements found in HTML")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Error debugging member profile: {e}")
            return False
    
    def debug_sms_form(self, member_id: str):
        """Debug SMS form to understand the actual form structure"""
        try:
            print(f"\n📱 DEBUGGING SMS FORM: {member_id}")
            
            # Try different SMS form URLs
            sms_urls = [
                f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile/sendText",
                f"{self.base_url}/action/LeadProfile/sendText",
                f"{self.base_url}/action/Dashboard/sendText",
                f"{self.base_url}/action/FollowUp/save"
            ]
            
            for i, sms_url in enumerate(sms_urls):
                print(f"   🔍 Trying SMS URL {i+1}: {sms_url}")
                
                try:
                    response = self.session.get(sms_url, timeout=30, verify=False)
                    print(f"      📊 Status: {response.status_code}")
                    print(f"      📊 URL: {response.url}")
                    
                    if response.ok:
                        print(f"      ✅ URL {i+1} works!")
                        
                        # Save the HTML for analysis
                        with open(f"debug_sms_form_{i+1}.html", "w", encoding="utf-8") as f:
                            f.write(response.text)
                        print(f"      💾 Saved SMS form HTML to debug_sms_form_{i+1}.html")
                        
                        # Look for form fields
                        html_content = response.text
                        
                        if "textMessage" in html_content:
                            print(f"      ✅ Found 'textMessage' field")
                        else:
                            print(f"      ❌ 'textMessage' field not found")
                        
                        if "submit" in html_content.lower():
                            print(f"      ✅ Found submit button")
                        else:
                            print(f"      ❌ Submit button not found")
                        
                        return sms_url
                    else:
                        print(f"      ❌ URL {i+1} failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ Error with URL {i+1}: {e}")
            
            print("   ❌ No working SMS URLs found")
            return None
                
        except Exception as e:
            print(f"   ❌ Error debugging SMS form: {e}")
            return None
    
    def debug_email_form(self, member_id: str):
        """Debug Email form to understand the actual form structure"""
        try:
            print(f"\n📧 DEBUGGING EMAIL FORM: {member_id}")
            
            # Try different Email form URLs
            email_urls = [
                f"{self.base_url}/action/Delegate/{member_id}/url=/action/LeadProfile/sendEmail",
                f"{self.base_url}/action/LeadProfile/sendEmail",
                f"{self.base_url}/action/Dashboard/sendEmail",
                f"{self.base_url}/action/FollowUp/save"
            ]
            
            for i, email_url in enumerate(email_urls):
                print(f"   🔍 Trying Email URL {i+1}: {email_url}")
                
                try:
                    response = self.session.get(email_url, timeout=30, verify=False)
                    print(f"      📊 Status: {response.status_code}")
                    print(f"      📊 URL: {response.url}")
                    
                    if response.ok:
                        print(f"      ✅ URL {i+1} works!")
                        
                        # Save the HTML for analysis
                        with open(f"debug_email_form_{i+1}.html", "w", encoding="utf-8") as f:
                            f.write(response.text)
                        print(f"      💾 Saved Email form HTML to debug_email_form_{i+1}.html")
                        
                        # Look for form fields
                        html_content = response.text
                        
                        if "emailSubject" in html_content:
                            print(f"      ✅ Found 'emailSubject' field")
                        else:
                            print(f"      ❌ 'emailSubject' field not found")
                        
                        if "emailMessage" in html_content:
                            print(f"      ✅ Found 'emailMessage' field")
                        else:
                            print(f"      ❌ 'emailMessage' field not found")
                        
                        if "submit" in html_content.lower():
                            print(f"      ✅ Found submit button")
                        else:
                            print(f"      ❌ Submit button not found")
                        
                        return email_url
                    else:
                        print(f"      ❌ URL {i+1} failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"      ❌ Error with URL {i+1}: {e}")
            
            print("   ❌ No working Email URLs found")
            return None
                
        except Exception as e:
            print(f"   ❌ Error debugging Email form: {e}")
            return None
    
    def test_form_submission(self, form_url: str, form_data: Dict, message_type: str):
        """Test actual form submission and analyze the response"""
        try:
            print(f"\n🧪 TESTING {message_type.upper()} FORM SUBMISSION")
            print(f"   📤 URL: {form_url}")
            print(f"   📤 Data: {form_data}")
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"{self.base_url}/action/Dashboard/view",
                "Origin": self.base_url
            }
            
            response = self.session.post(form_url, data=form_data, headers=headers, timeout=30, verify=False)
            
            print(f"   📊 Response status: {response.status_code}")
            print(f"   📊 Response URL: {response.url}")
            print(f"   📊 Response headers: {dict(response.headers)}")
            print(f"   📊 Response preview: {response.text[:1000]}")
            
            # Save the response for analysis
            with open(f"debug_{message_type}_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"   💾 Saved response to debug_{message_type}_response.html")
            
            # Check for success indicators
            response_text = response.text.lower()
            
            success_indicators = [
                "sent successfully",
                "message sent",
                "texted",
                "emailed",
                "success",
                "completed"
            ]
            
            error_indicators = [
                "error",
                "failed",
                "invalid",
                "not found",
                "unauthorized"
            ]
            
            found_success = False
            found_error = False
            
            for indicator in success_indicators:
                if indicator in response_text:
                    print(f"   ✅ Found success indicator: '{indicator}'")
                    found_success = True
            
            for indicator in error_indicators:
                if indicator in response_text:
                    print(f"   ❌ Found error indicator: '{indicator}'")
                    found_error = True
            
            if found_success and not found_error:
                print(f"   🎉 {message_type.upper()} submission appears successful!")
                return True
            elif found_error:
                print(f"   ❌ {message_type.upper()} submission appears to have failed!")
                return False
            else:
                print(f"   ⚠️ {message_type.upper()} submission status unclear")
                return False
                
        except Exception as e:
            print(f"   ❌ Error testing {message_type} submission: {e}")
            return False

def debug_api_messaging():
    """Debug ClubOS API messaging to understand why it's not working"""
    print("🔍 DEBUGGING CLUBOS API MESSAGING")
    print("=" * 50)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ Missing ClubOS credentials")
        return False
    
    # Create debugger and login
    debugger = ClubOSAPIDebugger()
    if not debugger.login(username, password):
        return False
    
    # Debug member profile
    debugger.debug_member_profile(JEREMY_MAYO_ID)
    
    # Debug SMS form
    sms_url = debugger.debug_sms_form(JEREMY_MAYO_ID)
    
    # Debug Email form
    email_url = debugger.debug_email_form(JEREMY_MAYO_ID)
    
    # Test form submissions if URLs found
    if sms_url:
        sms_data = {
            "memberId": JEREMY_MAYO_ID,
            "messageText": "Debug test SMS message",
            "sendMethod": "sms",
            "submit": "Send SMS"
        }
        debugger.test_form_submission(sms_url, sms_data, "SMS")
    
    if email_url:
        email_data = {
            "memberId": JEREMY_MAYO_ID,
            "emailSubject": "Debug Test Email",
            "emailMessage": "<p>Debug test email message</p>",
            "sendMethod": "email",
            "submit": "Send Email"
        }
        debugger.test_form_submission(email_url, email_data, "Email")
    
    print(f"\n📊 DEBUG SUMMARY:")
    print(f"   Member Profile: {'✅ Loaded' if debugger.debug_member_profile(JEREMY_MAYO_ID) else '❌ Failed'}")
    print(f"   SMS Form: {'✅ Found' if sms_url else '❌ Not Found'}")
    print(f"   Email Form: {'✅ Found' if email_url else '❌ Not Found'}")
    
    print(f"\n💾 Debug files saved:")
    print(f"   - debug_member_profile.html")
    print(f"   - debug_sms_form_*.html")
    print(f"   - debug_email_form_*.html")
    print(f"   - debug_SMS_response.html")
    print(f"   - debug_Email_response.html")
    
    return True

if __name__ == "__main__":
    success = debug_api_messaging()
    exit(0 if success else 1) 