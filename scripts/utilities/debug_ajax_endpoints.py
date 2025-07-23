#!/usr/bin/env python3
"""
Test different AJAX endpoints that might handle messaging
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import re
from bs4 import BeautifulSoup
import time
import json

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

def test_ajax_endpoints():
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
        # Get dashboard and CSRF token
        print("\n📄 Getting dashboard...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        csrf_token = extract_csrf_token(response.text)
        
        # Get member profile
        print(f"\n👤 Getting member profile...")
        profile_url = f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if not profile_response.ok:
            print(f"   ❌ Failed to load profile: {profile_response.status_code}")
            return
        
        print(f"   ✅ Profile loaded successfully")
        
        # Test different AJAX endpoints that might handle messaging
        ajax_endpoints = [
            "/ajax/message/send",
            "/ajax/followup/send", 
            "/ajax/communication/send",
            "/ajax/members/message",
            "/ajax/dashboard/send-message",
            "/api/message/send",
            "/api/followup/send",
            "/api/communication/send"
        ]
        
        # Test different data formats
        test_data_formats = [
            # JSON format
            {
                "data": json.dumps({
                    "memberId": MEMBER_ID,
                    "message": "Test SMS via AJAX",
                    "type": "text",
                    "notes": "AJAX test"
                }),
                "headers": {"Content-Type": "application/json"}
            },
            # Form data format
            {
                "data": {
                    "memberId": MEMBER_ID,
                    "message": "Test SMS via AJAX",
                    "type": "text", 
                    "notes": "AJAX test"
                },
                "headers": {"Content-Type": "application/x-www-form-urlencoded"}
            },
            # URL-encoded format
            {
                "data": f"memberId={MEMBER_ID}&message=Test SMS via AJAX&type=text&notes=AJAX test",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"}
            }
        ]
        
        for endpoint in ajax_endpoints:
            print(f"\n🔍 Testing AJAX endpoint: {endpoint}")
            
            for i, format_data in enumerate(test_data_formats):
                try:
                    # Add CSRF token if we have it
                    if csrf_token:
                        if isinstance(format_data["data"], dict):
                            format_data["data"]["csrf_token"] = csrf_token
                        elif isinstance(format_data["data"], str):
                            format_data["data"] += f"&csrf_token={csrf_token}"
                    
                    # Add AJAX headers
                    test_headers = headers.copy()
                    test_headers.update(format_data["headers"])
                    test_headers.update({
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json, text/javascript, */*; q=0.01"
                    })
                    
                    print(f"   Testing format {i+1}: {format_data['headers']['Content-Type']}")
                    
                    response = client.auth.session.post(
                        f"{client.base_url}{endpoint}",
                        data=format_data["data"],
                        headers=test_headers,
                        timeout=30,
                        verify=False
                    )
                    
                    print(f"   Status: {response.status_code}")
                    print(f"   Response length: {len(response.text)}")
                    
                    # Analyze the response
                    if response.ok:
                        if "success" in response.text.lower():
                            print(f"   ✅ SUCCESS detected!")
                        elif "error" in response.text.lower():
                            print(f"   ❌ ERROR detected")
                        elif len(response.text) < 500:
                            print(f"   ✅ Short response (likely success): {response.text}")
                        else:
                            print(f"   ⚠️ Long response, checking content...")
                            
                            # Look for JSON response
                            try:
                                json_response = json.loads(response.text)
                                print(f"   📝 JSON response: {json_response}")
                            except:
                                # Look for specific keywords
                                keywords = ["sent", "delivered", "message", "success", "error"]
                                found_keywords = []
                                for keyword in keywords:
                                    if keyword in response.text.lower():
                                        found_keywords.append(keyword)
                                
                                if found_keywords:
                                    print(f"   📝 Found keywords: {found_keywords}")
                                
                                # Save response for manual inspection
                                with open(f'ajax_response_{endpoint.replace("/", "_")}_{i}.html', 'w', encoding='utf-8') as f:
                                    f.write(response.text)
                                print(f"   💾 Saved response to ajax_response_{endpoint.replace('/', '_')}_{i}.html")
                    else:
                        print(f"   ❌ Failed with status {response.status_code}")
                        if response.status_code == 403:
                            print(f"   🔒 403 Forbidden - might need different authentication")
                        elif response.status_code == 404:
                            print(f"   🔍 404 Not Found - endpoint doesn't exist")
                        
                except Exception as e:
                    print(f"   ⚠️ Error: {e}")
                    continue
        
        print(f"\n📊 AJAX Test Summary:")
        print(f"   Check the saved HTML files for successful responses")
        print(f"   Look for JSON responses that indicate success")
        print(f"   The key is finding the right AJAX endpoint + data format")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_ajax_endpoints() 