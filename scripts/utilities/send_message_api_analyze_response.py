#!/usr/bin/env python3
"""
Analyze API response content to understand what the 87-character responses contain
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from urllib.parse import urljoin
from config.secrets_local import get_secret

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "Analyze response SMS test!"
EMAIL_MESSAGE = "Analyze response email test!"

def send_message_api_analyze_response():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Setting up API session...")
        
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
        
        # Test the working endpoints with detailed response analysis
        working_endpoints = [
            "/action/Api/send-message",
            "/action/Api/follow-up"
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": f"{base_url}/action/Dashboard/view",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        # Test SMS
        print(f"\n📤 Testing SMS to {TARGET_NAME} (ID: {MEMBER_ID})...")
        
        for endpoint in working_endpoints:
            try:
                api_url = urljoin(base_url, endpoint)
                
                # Test with the most likely data format
                sms_data = {
                    "memberId": MEMBER_ID,
                    "message": SMS_MESSAGE,
                    "messageType": "text"
                }
                
                print(f"   🔍 Testing {endpoint}...")
                response = session.post(
                    api_url,
                    data=sms_data,
                    headers=headers,
                    timeout=10
                )
                
                print(f"      Status: {response.status_code}")
                print(f"      Response length: {len(response.text)} chars")
                print(f"      Response content: '{response.text}'")
                
                # Analyze response content
                response_lower = response.text.lower()
                if "success" in response_lower:
                    print(f"      ✅ SUCCESS keyword found!")
                if "sent" in response_lower:
                    print(f"      ✅ SENT keyword found!")
                if "error" in response_lower:
                    print(f"      ❌ ERROR keyword found!")
                if "failed" in response_lower:
                    print(f"      ❌ FAILED keyword found!")
                if "something isn't right" in response_lower:
                    print(f"      ⚠️ 'Something isn't right' message found!")
                
                # Check for JSON response
                try:
                    json_data = response.json()
                    print(f"      📄 JSON response: {json_data}")
                except:
                    print(f"      📄 Not JSON response")
                
                # Check for HTML response
                if "<html" in response.text.lower():
                    print(f"      🌐 HTML response detected")
                
                # Check for redirect
                if response.status_code in [301, 302, 303, 307, 308]:
                    print(f"      🔄 Redirect response")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error with {endpoint}: {e}")
        
        # Test Email
        print(f"\n📤 Testing Email to {TARGET_NAME} (ID: {MEMBER_ID})...")
        
        for endpoint in working_endpoints:
            try:
                api_url = urljoin(base_url, endpoint)
                
                # Test with email data format
                email_data = {
                    "memberId": MEMBER_ID,
                    "subject": "Analyze Response Test",
                    "message": EMAIL_MESSAGE,
                    "messageType": "email"
                }
                
                print(f"   🔍 Testing {endpoint}...")
                response = session.post(
                    api_url,
                    data=email_data,
                    headers=headers,
                    timeout=10
                )
                
                print(f"      Status: {response.status_code}")
                print(f"      Response length: {len(response.text)} chars")
                print(f"      Response content: '{response.text}'")
                
                # Analyze response content
                response_lower = response.text.lower()
                if "success" in response_lower:
                    print(f"      ✅ SUCCESS keyword found!")
                if "sent" in response_lower:
                    print(f"      ✅ SENT keyword found!")
                if "error" in response_lower:
                    print(f"      ❌ ERROR keyword found!")
                if "failed" in response_lower:
                    print(f"      ❌ FAILED keyword found!")
                if "something isn't right" in response_lower:
                    print(f"      ⚠️ 'Something isn't right' message found!")
                
                # Check for JSON response
                try:
                    json_data = response.json()
                    print(f"      📄 JSON response: {json_data}")
                except:
                    print(f"      📄 Not JSON response")
                
                # Check for HTML response
                if "<html" in response.text.lower():
                    print(f"      🌐 HTML response detected")
                
                # Check for redirect
                if response.status_code in [301, 302, 303, 307, 308]:
                    print(f"      🔄 Redirect response")
                
                print()
                
            except Exception as e:
                print(f"   ❌ Error with {endpoint}: {e}")
        
        print("🔍 Response analysis completed!")
            
    except Exception as e:
        print(f"❌ Error during API analysis: {e}")

if __name__ == "__main__":
    send_message_api_analyze_response() 