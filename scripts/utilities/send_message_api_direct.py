#!/usr/bin/env python3
"""
Direct API solution using known member ID to bypass search issues
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from urllib.parse import urljoin
from config.secrets_local import get_secret

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "Direct API SMS test - this should definitely work!"
EMAIL_MESSAGE = "Direct API email test - this should definitely work!"

def send_message_api_direct():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Setting up direct API session...")
        
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
        
        # Test different messaging endpoints
        messaging_endpoints = [
            "/action/Dashboard/sendText",
            "/action/Dashboard/sendEmail", 
            "/action/Api/send-message",
            "/action/Api/follow-up",
            "/action/Dashboard/messages"
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"{base_url}/action/Dashboard/view",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # Try SMS first
        print(f"\n📤 Sending SMS to {TARGET_NAME} (ID: {MEMBER_ID})...")
        sms_success = False
        
        for endpoint in messaging_endpoints:
            try:
                sms_url = urljoin(base_url, endpoint)
                
                # Try different data formats
                sms_data_formats = [
                    {"memberId": MEMBER_ID, "message": SMS_MESSAGE, "messageType": "text"},
                    {"member_id": MEMBER_ID, "message": SMS_MESSAGE, "type": "sms"},
                    {"memberId": MEMBER_ID, "textMessage": SMS_MESSAGE},
                    {"member_id": MEMBER_ID, "sms_message": SMS_MESSAGE}
                ]
                
                for data_format in sms_data_formats:
                    try:
                        response = session.post(
                            sms_url,
                            data=data_format,
                            headers=headers,
                            timeout=10
                        )
                        
                        print(f"   🔍 Tried {endpoint} with data: {data_format}")
                        print(f"      Status: {response.status_code}")
                        print(f"      Response length: {len(response.text)} chars")
                        
                        if response.status_code in [200, 201]:
                            if "success" in response.text.lower() or "sent" in response.text.lower():
                                print(f"   ✅ SMS sent successfully via {endpoint}!")
                                sms_success = True
                                break
                        elif response.status_code == 403:
                            print(f"   ⚠️ 403 Forbidden - endpoint may be restricted")
                        elif response.status_code == 404:
                            print(f"   ⚠️ 404 Not Found - endpoint doesn't exist")
                        else:
                            print(f"   ⚠️ Unexpected status: {response.status_code}")
                            
                    except Exception as e:
                        print(f"   ⚠️ Error with data format: {e}")
                        continue
                
                if sms_success:
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error with endpoint {endpoint}: {e}")
                continue
        
        # Try Email
        print(f"\n📤 Sending Email to {TARGET_NAME} (ID: {MEMBER_ID})...")
        email_success = False
        
        for endpoint in messaging_endpoints:
            try:
                email_url = urljoin(base_url, endpoint)
                
                # Try different data formats for email
                email_data_formats = [
                    {"memberId": MEMBER_ID, "subject": "Direct API Test", "message": EMAIL_MESSAGE, "messageType": "email"},
                    {"member_id": MEMBER_ID, "subject": "Direct API Test", "body": EMAIL_MESSAGE, "type": "email"},
                    {"memberId": MEMBER_ID, "emailMessage": EMAIL_MESSAGE, "subject": "Direct API Test"},
                    {"member_id": MEMBER_ID, "email_message": EMAIL_MESSAGE, "subject": "Direct API Test"}
                ]
                
                for data_format in email_data_formats:
                    try:
                        response = session.post(
                            email_url,
                            data=data_format,
                            headers=headers,
                            timeout=10
                        )
                        
                        print(f"   🔍 Tried {endpoint} with data: {data_format}")
                        print(f"      Status: {response.status_code}")
                        print(f"      Response length: {len(response.text)} chars")
                        
                        if response.status_code in [200, 201]:
                            if "success" in response.text.lower() or "sent" in response.text.lower():
                                print(f"   ✅ Email sent successfully via {endpoint}!")
                                email_success = True
                                break
                        elif response.status_code == 403:
                            print(f"   ⚠️ 403 Forbidden - endpoint may be restricted")
                        elif response.status_code == 404:
                            print(f"   ⚠️ 404 Not Found - endpoint doesn't exist")
                        else:
                            print(f"   ⚠️ Unexpected status: {response.status_code}")
                            
                    except Exception as e:
                        print(f"   ⚠️ Error with data format: {e}")
                        continue
                
                if email_success:
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error with endpoint {endpoint}: {e}")
                continue
        
        # Summary
        print(f"\n📊 Direct API Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_success else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if email_success else '❌ Failed'}")
        
        if sms_success or email_success:
            print("\n🎉 At least one message was sent successfully via direct API!")
        else:
            print("\n⚠️ No messages were delivered via direct API.")
            
    except Exception as e:
        print(f"❌ Error during direct API messaging: {e}")

if __name__ == "__main__":
    send_message_api_direct() 