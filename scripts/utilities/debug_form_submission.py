#!/usr/bin/env python3
"""
Debug the actual form submission by getting the form HTML and submitting it correctly
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

def debug_form_submission():
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
        
        # Look for forms in the profile page
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        forms = soup.find_all('form')
        
        print(f"\n🔍 Found {len(forms)} forms on the profile page")
        
        for i, form in enumerate(forms):
            print(f"\n   Form {i+1}:")
            print(f"     Action: {form.get('action', 'No action')}")
            print(f"     Method: {form.get('method', 'No method')}")
            print(f"     ID: {form.get('id', 'No ID')}")
            print(f"     Class: {form.get('class', 'No class')}")
            
            # Look for input fields
            inputs = form.find_all('input')
            print(f"     Input fields ({len(inputs)}):")
            for inp in inputs:
                print(f"       - name='{inp.get('name', 'No name')}' type='{inp.get('type', 'No type')}' value='{inp.get('value', 'No value')[:50]}...'")
            
            # Look for textarea fields
            textareas = form.find_all('textarea')
            print(f"     Textarea fields ({len(textareas)}):")
            for ta in textareas:
                print(f"       - name='{ta.get('name', 'No name')}' id='{ta.get('id', 'No ID')}'")
        
        # Try to find the follow-up form by looking for specific elements
        print(f"\n🔍 Looking for follow-up form elements...")
        
        # Look for elements that might be part of the follow-up form
        followup_elements = soup.find_all(text=re.compile(r'follow.?up|send.?message|text.?message', re.IGNORECASE))
        if followup_elements:
            print(f"   Found {len(followup_elements)} follow-up related elements")
            for elem in followup_elements[:5]:  # Show first 5
                print(f"     - {elem.strip()[:100]}...")
        
        # Try different form submission approaches
        print(f"\n📤 Trying form submission approaches...")
        
        # Approach 1: Try the follow-up endpoint with proper form data
        followup_url = f"{client.base_url}/action/Dashboard/follow-up"
        
        # Build form data based on what we see in the Selenium code
        form_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Test SMS via form submission",
            "followUpOutcomeNotes": "Form submission test",
            "type": "text",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            form_data["csrf_token"] = csrf_token
        
        # Try with different headers
        test_headers = headers.copy()
        test_headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": profile_url
        })
        
        print(f"   Submitting to {followup_url}")
        print(f"   Form data: {form_data}")
        
        response = client.auth.session.post(
            followup_url,
            data=form_data,
            headers=test_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Length: {len(response.text)}")
        
        if response.ok:
            if "success" in response.text.lower():
                print(f"   ✅ SUCCESS detected!")
            elif "error" in response.text.lower():
                print(f"   ❌ ERROR detected")
            elif len(response.text) < 1000:
                print(f"   ✅ Short response (likely success): {response.text}")
            else:
                print(f"   ⚠️ Long response, checking content...")
                
                # Save response for manual inspection
                with open('form_submission_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved response to form_submission_response.html")
        else:
            print(f"   ❌ Failed with status {response.status_code}")
        
        # Approach 2: Try submitting to the profile page itself
        print(f"\n📤 Trying submission to profile page...")
        
        profile_form_data = {
            "memberId": MEMBER_ID,
            "textMessage": "Test SMS via profile submission",
            "followUpOutcomeNotes": "Profile submission test",
            "type": "text",
            "action": "send",
            "submit": "Send Message"
        }
        
        if csrf_token:
            profile_form_data["csrf_token"] = csrf_token
        
        profile_response = client.auth.session.post(
            profile_url,
            data=profile_form_data,
            headers=test_headers,
            timeout=30,
            verify=False
        )
        
        print(f"   Profile Response Status: {profile_response.status_code}")
        print(f"   Profile Response Length: {len(profile_response.text)}")
        
        if profile_response.ok:
            if "success" in profile_response.text.lower():
                print(f"   ✅ SUCCESS detected!")
            elif "error" in profile_response.text.lower():
                print(f"   ❌ ERROR detected")
            elif len(profile_response.text) < 1000:
                print(f"   ✅ Short response (likely success): {profile_response.text}")
            else:
                print(f"   ⚠️ Long response, checking content...")
                
                # Save response for manual inspection
                with open('profile_submission_response.html', 'w', encoding='utf-8') as f:
                    f.write(profile_response.text)
                print(f"   💾 Saved response to profile_submission_response.html")
        else:
            print(f"   ❌ Failed with status {profile_response.status_code}")
        
        print(f"\n📊 Form Submission Summary:")
        print(f"   Check the saved HTML files to see what the responses contain")
        print(f"   The key is finding the right form action URL and field names")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_form_submission() 