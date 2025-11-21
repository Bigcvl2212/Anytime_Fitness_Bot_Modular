#!/usr/bin/env python3
"""
Debug the follow-up response to understand why messages aren't being delivered
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
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

def debug_followup_response():
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
        
        # Try different follow-up endpoints and form structures
        followup_endpoints = [
            "/action/Dashboard/follow-up",
            "/action/Members/follow-up",
            "/ajax/follow-up/send",
            "/action/Dashboard/send-message"
        ]
        
        # Try different form structures based on what we see in the Selenium code
        form_variations = [
            # Variation 1: Basic follow-up
            {
                "memberId": MEMBER_ID,
                "textMessage": "Test SMS via API debugging",
                "followUpOutcomeNotes": "Debug test",
                "type": "text",
                "action": "send"
            },
            # Variation 2: With different field names
            {
                "member_id": MEMBER_ID,
                "message": "Test SMS via API debugging",
                "notes": "Debug test",
                "messageType": "text",
                "send": "1"
            },
            # Variation 3: With form submission
            {
                "memberId": MEMBER_ID,
                "textMessage": "Test SMS via API debugging",
                "followUpOutcomeNotes": "Debug test",
                "submit": "Send Message"
            },
            # Variation 4: With AJAX headers
            {
                "memberId": MEMBER_ID,
                "textMessage": "Test SMS via API debugging",
                "followUpOutcomeNotes": "Debug test",
                "type": "text",
                "action": "send",
                "ajax": "1"
            }
        ]
        
        for endpoint in followup_endpoints:
            print(f"\n🔍 Testing endpoint: {endpoint}")
            
            for i, form_data in enumerate(form_variations):
                try:
                    # Add CSRF token if we have it
                    if csrf_token:
                        form_data["csrf_token"] = csrf_token
                    
                    # Try with different headers
                    test_headers = headers.copy()
                    test_headers.update({
                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded"
                    })
                    
                    print(f"   Testing variation {i+1}: {form_data}")
                    
                    response = client.auth.session.post(
                        f"{client.base_url}{endpoint}",
                        data=form_data,
                        headers=test_headers,
                        timeout=30,
                        verify=False
                    )
                    
                    print(f"   Status: {response.status_code}")
                    print(f"   Response length: {len(response.text)}")
                    
                    # Analyze the response
                    if response.ok:
                        if "success" in response.text.lower():
                            print(f"   ✅ SUCCESS detected in response!")
                        elif "error" in response.text.lower():
                            print(f"   ❌ ERROR detected in response")
                        elif len(response.text) < 500:
                            print(f"   ✅ Short response (likely success): {response.text}")
                        else:
                            print(f"   ⚠️ Long response, checking for clues...")
                            
                            # Look for specific keywords
                            keywords = ["sent", "delivered", "message", "follow", "up"]
                            found_keywords = []
                            for keyword in keywords:
                                if keyword in response.text.lower():
                                    found_keywords.append(keyword)
                            
                            if found_keywords:
                                print(f"   📝 Found keywords: {found_keywords}")
                            
                            # Save response for manual inspection
                            with open(f'debug_response_{endpoint.replace("/", "_")}_{i}.html', 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            print(f"   💾 Saved response to debug_response_{endpoint.replace('/', '_')}_{i}.html")
                    else:
                        print(f"   ❌ Failed with status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error: {e}")
                    continue
        
        print(f"\n📊 Debug Summary:")
        print(f"   Check the saved HTML files to see what the responses contain")
        print(f"   Look for success/error messages in the HTML")
        print(f"   The key is finding the right endpoint + form structure combination")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_followup_response() 