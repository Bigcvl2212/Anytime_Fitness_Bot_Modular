#!/usr/bin/env python3
"""
Reverse engineer the exact endpoint by analyzing the working Selenium flow
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
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

def reverse_engineer_endpoint():
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
        # Step 1: Analyze the exact Selenium flow
        print("\n🔍 Analyzing Selenium flow...")
        print("   Selenium does: Dashboard → Search → Click Member → Send Message → Submit Form")
        print("   We need to replicate this with HTTP requests")
        
        # Step 2: Get dashboard and maintain session
        print("\n📄 Getting dashboard...")
        dashboard_url = f"{client.base_url}/action/Dashboard/view"
        headers = client.auth.get_headers()
        
        response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        print(f"   Dashboard Status: {response.status_code}")
        
        if not response.ok:
            print(f"   ❌ Failed to load dashboard: {response.status_code}")
            return
        
        # Check if we're logged in
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("   ❌ Session expired, re-authenticating...")
            if not auth_service.login(username, password):
                print("   ❌ Re-authentication failed")
                return
            response = client.auth.session.get(dashboard_url, headers=headers, timeout=30, verify=False)
        
        print("   ✅ Dashboard loaded successfully")
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(response.text)
        if csrf_token:
            print(f"   ✅ Found CSRF token: {csrf_token[:20]}...")
        else:
            print("   ⚠️ No CSRF token found")
        
        # Step 3: Get member profile (this is the key - we need to be on the member's page)
        print(f"\n👤 Getting member profile for {TARGET_NAME}...")
        
        # The key insight: We need to be on the member's profile page when submitting
        profile_url = f"{client.base_url}/action/Dashboard/member/{MEMBER_ID}"
        profile_response = client.auth.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if not profile_response.ok:
            print(f"   ❌ Failed to load profile: {profile_response.status_code}")
            return
        
        print(f"   ✅ Profile loaded successfully")
        
        # Step 4: Analyze the profile page to understand the form structure
        print(f"\n🔍 Analyzing profile page structure...")
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # Look for any forms or JavaScript that handles messaging
        forms = soup.find_all('form')
        print(f"   Found {len(forms)} forms on profile page")
        
        # Look for JavaScript that might handle form submission
        scripts = soup.find_all('script')
        print(f"   Found {len(scripts)} script tags")
        
        # Look for AJAX endpoints in JavaScript
        ajax_endpoints = []
        for script in scripts:
            script_content = script.string if script.string else ''
            # Look for AJAX calls
            ajax_matches = re.findall(r'url\s*[:=]\s*["\']([^"\']+)["\']', script_content)
            ajax_endpoints.extend(ajax_matches)
        
        if ajax_endpoints:
            print(f"   Found AJAX endpoints: {ajax_endpoints}")
        
        # Step 5: Try different approaches based on what we found
        
        # Approach 1: Submit to the profile page itself with proper form data
        print(f"\n📤 Approach 1: Submitting to profile page...")
        
        profile_form_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Test SMS via profile page submission",
            "followUpOutcomeNotes": "Profile page test",
            "type": "text",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            profile_form_data["csrf_token"] = csrf_token
        
        # Use headers that mimic being on the profile page
        profile_headers = headers.copy()
        profile_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": profile_url,
            "Origin": client.base_url
        })
        
        profile_submit_response = client.auth.session.post(
            profile_url,
            data=profile_form_data,
            headers=profile_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Profile Submit Status: {profile_submit_response.status_code}")
        print(f"   Profile Submit Length: {len(profile_submit_response.text)}")
        
        if profile_submit_response.ok:
            if "success" in profile_submit_response.text.lower():
                print("   ✅ SUCCESS detected in profile submission!")
            elif len(profile_submit_response.text) < 1000:
                print(f"   ✅ Short response (likely success): {profile_submit_response.text}")
            else:
                print("   ⚠️ Long response, checking content...")
                
                # Save response for analysis
                with open('profile_submit_response.html', 'w', encoding='utf-8') as f:
                    f.write(profile_submit_response.text)
                print("   💾 Saved profile submit response")
        else:
            print(f"   ❌ Profile submission failed: {profile_submit_response.status_code}")
        
        # Approach 2: Try the follow-up endpoint with proper context
        print(f"\n📤 Approach 2: Submitting to follow-up endpoint with context...")
        
        followup_url = f"{client.base_url}/action/Dashboard/follow-up"
        
        followup_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Test SMS via follow-up with context",
            "followUpOutcomeNotes": "Follow-up context test",
            "type": "text",
            "action": "send"
        }
        
        if csrf_token:
            followup_data["csrf_token"] = csrf_token
        
        # Use headers that include the profile page as referer
        followup_headers = headers.copy()
        followup_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": profile_url,
            "Origin": client.base_url,
            "X-Requested-With": "XMLHttpRequest"
        })
        
        followup_response = client.auth.session.post(
            followup_url,
            data=followup_data,
            headers=followup_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Follow-up Status: {followup_response.status_code}")
        print(f"   Follow-up Length: {len(followup_response.text)}")
        
        if followup_response.ok:
            if "success" in followup_response.text.lower():
                print("   ✅ SUCCESS detected in follow-up submission!")
            elif len(followup_response.text) < 1000:
                print(f"   ✅ Short response (likely success): {followup_response.text}")
            else:
                print("   ⚠️ Long response, checking content...")
                
                # Save response for analysis
                with open('followup_response.html', 'w', encoding='utf-8') as f:
                    f.write(followup_response.text)
                print("   💾 Saved follow-up response")
        else:
            print(f"   ❌ Follow-up submission failed: {followup_response.status_code}")
        
        # Approach 3: Try to find the actual endpoint by analyzing the response
        print(f"\n📤 Approach 3: Analyzing responses for clues...")
        
        # Look for redirects or new endpoints in the responses
        if profile_submit_response.ok:
            print("   Analyzing profile submit response...")
            if "redirect" in profile_submit_response.text.lower():
                print("   📍 Found redirect in profile response")
            if "location" in profile_submit_response.headers:
                print(f"   📍 Found location header: {profile_submit_response.headers['location']}")
        
        if followup_response.ok:
            print("   Analyzing follow-up response...")
            if "redirect" in followup_response.text.lower():
                print("   📍 Found redirect in follow-up response")
            if "location" in followup_response.headers:
                print(f"   📍 Found location header: {followup_response.headers['location']}")
        
        print(f"\n📊 Reverse Engineering Summary:")
        print(f"   The key is understanding the exact page context and form submission")
        print(f"   Check the saved HTML files for clues about the correct endpoint")
        print(f"   We need to replicate the exact same session state as Selenium")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    reverse_engineer_endpoint() 