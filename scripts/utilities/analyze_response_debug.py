#!/usr/bin/env python3
"""
Analyze the actual response to understand why messages aren't being delivered
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup
import time

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"

def extract_csrf_token(html_content):
    """Extract CSRF token from HTML content"""
    try:
        csrf_patterns = [
            r'<meta name="csrf-token" content="([^"]+)"',
            r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"',
            r'<input[^>]*name="_token"[^>]*value="([^"]+)"',
            r'window\.csrfToken\s*=\s*["\']([^"\']+)["\']',
            r'data-csrf="([^"]+)"'
        ]
        
        for pattern in csrf_patterns:
            match = re.search(pattern, html_content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    except Exception as e:
        print(f"   ⚠️ Error extracting CSRF token: {e}")
        return None

def analyze_response_debug():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    auth_service = ClubOSAPIAuthentication()
    if not auth_service.login(username, password):
        print("❌ ClubOS authentication failed")
        return
    
    client = ClubOSAPIClient(auth_service)
    print("✅ ClubOS authentication successful!")

    try:
        # Get dashboard and profile
        print("\n📄 Getting dashboard and profile...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("   ❌ Session expired, re-authenticating...")
            if not auth_service.login(username, password):
                print("   ❌ Re-authentication failed")
                return
            response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        
        print("   ✅ Dashboard loaded successfully")
        
        # Get member profile
        profile_url = f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if not profile_response.ok:
            print(f"   ❌ Failed to load profile: {profile_response.status_code}")
            return
        
        print(f"   ✅ Profile loaded successfully")
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(profile_response.text)
        
        # Try to send a message and capture the exact response
        print(f"\n📤 Sending test message and analyzing response...")
        
        sms_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Test message for response analysis",
            "followUpOutcomeNotes": "Response analysis test",
            "type": "text",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            sms_data["csrf_token"] = csrf_token
        
        sms_headers = headers.copy()
        sms_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": profile_url,
            "Origin": client.base_url
        })
        
        print(f"   Submitting to: {profile_url}")
        print(f"   Form data: {sms_data}")
        
        sms_response = client.auth.session.post(
            profile_url,
            data=sms_data,
            headers=sms_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Response Status: {sms_response.status_code}")
        print(f"   Response Length: {len(sms_response.text)}")
        print(f"   Response Headers: {dict(sms_response.headers)}")
        
        # Save the full response
        with open('full_response_analysis.html', 'w', encoding='utf-8') as f:
            f.write(sms_response.text)
        print("   💾 Saved full response to full_response_analysis.html")
        
        # Analyze the response
        print(f"\n🔍 Analyzing response content...")
        
        # Check if it's an HTML page (which means form was processed but not sent)
        if "<html" in sms_response.text.lower():
            print("   ⚠️ Response is an HTML page - form was processed but message may not have been sent")
            
            # Look for success/error messages in the HTML
            soup = BeautifulSoup(sms_response.text, 'html.parser')
            
            # Look for success messages
            success_patterns = [
                "success", "sent", "delivered", "message sent", "follow-up sent"
            ]
            
            found_success = False
            for pattern in success_patterns:
                if pattern in sms_response.text.lower():
                    print(f"   ✅ Found success indicator: '{pattern}'")
                    found_success = True
            
            if not found_success:
                print("   ❌ No success indicators found in response")
            
            # Look for error messages
            error_patterns = [
                "error", "failed", "invalid", "not found", "permission denied"
            ]
            
            found_error = False
            for pattern in error_patterns:
                if pattern in sms_response.text.lower():
                    print(f"   ❌ Found error indicator: '{pattern}'")
                    found_error = True
            
            if not found_error:
                print("   ✅ No error indicators found in response")
            
            # Check if we got redirected
            if sms_response.history:
                print(f"   📍 Response was redirected: {len(sms_response.history)} redirects")
                for resp in sms_response.history:
                    print(f"      - {resp.status_code}: {resp.url}")
                print(f"      Final URL: {sms_response.url}")
            
            # Look for any JavaScript that might indicate what happened
            scripts = soup.find_all('script')
            print(f"   📜 Found {len(scripts)} script tags in response")
            
            for i, script in enumerate(scripts):
                script_content = script.string if script.string else ''
                if 'success' in script_content.lower() or 'error' in script_content.lower():
                    print(f"   📜 Script {i+1} contains success/error keywords")
                    print(f"      Content: {script_content[:200]}...")
        
        else:
            print("   ✅ Response is not HTML - might be actual API response")
            print(f"   📄 Response content: {sms_response.text[:500]}...")
        
        # Try a different approach - look for actual API endpoints
        print(f"\n🔍 Looking for actual API endpoints...")
        
        # Try to find AJAX endpoints that might handle messaging
        api_endpoints = [
            "/ajax/message/send",
            "/ajax/followup/send",
            "/api/v1/messages/send",
            "/api/v2/messages/send",
            "/action/Api/send-message",
            "/action/Api/follow-up"
        ]
        
        for endpoint in api_endpoints:
            try:
                api_url = f"{client.base_url}{endpoint}"
                
                api_data = {
                    "memberId": MEMBER_ID,
                    "message": "Test API endpoint",
                    "type": "text"
                }
                
                if csrf_token:
                    api_data["csrf_token"] = csrf_token
                
                api_headers = headers.copy()
                api_headers.update({
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/json"
                })
                
                api_response = client.auth.session.post(
                    api_url,
                    json=api_data,
                    headers=api_headers,
                    timeout=30,
                    verify=False
                )
                
                print(f"   {endpoint}: {api_response.status_code}")
                
                if api_response.ok and len(api_response.text) < 1000:
                    print(f"   ✅ {endpoint} might be working: {api_response.text}")
                
            except Exception as e:
                print(f"   ❌ {endpoint} failed: {e}")
        
        print(f"\n📊 Response Analysis Summary:")
        print(f"   The issue is that we're getting HTML page responses instead of API responses")
        print(f"   This means the form is being processed but messages aren't being sent")
        print(f"   We need to find the actual API endpoint that handles message sending")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    analyze_response_debug() 