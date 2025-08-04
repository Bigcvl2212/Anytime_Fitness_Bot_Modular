#!/usr/bin/env python3
"""
Debug real ClubOS messaging to find actual endpoints and see what's happening
"""

from services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import requests
from bs4 import BeautifulSoup
import re

TARGET_MEMBER_ID = "18703278"

def debug_real_messaging():
    """Debug the actual messaging process to see what's happening"""
    
    print("🔍 DEBUGGING REAL CLUBOS MESSAGING")
    print("=" * 50)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create authentication service and authenticate
    print("🔐 Authenticating with ClubOS...")
    auth_service = ClubOSAPIAuthentication()
    
    if not auth_service.login(username, password):
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    print()
    
    # Step 1: Find the actual member profile page
    print("1. FINDING MEMBER PROFILE PAGE")
    print("-" * 40)
    
    profile_urls_to_try = [
        f"/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile",
        f"/action/Members/profile/{TARGET_MEMBER_ID}",
        f"/action/Members/view/{TARGET_MEMBER_ID}",
        f"/action/Delegate/{TARGET_MEMBER_ID}/url=/action/Dashboard",
        f"/action/Delegate/{TARGET_MEMBER_ID}/url=false"
    ]
    
    member_profile_url = None
    for url in profile_urls_to_try:
        print(f"   🔍 Trying: {url}")
        response = auth_service.session.get(
            f"{auth_service.base_url}{url}",
            headers=auth_service.get_headers(),
            timeout=30,
            verify=False
        )
        
        print(f"      Status: {response.status_code}")
        print(f"      Final URL: {response.url}")
        
        if response.ok:
            # Check if this is actually a member profile page
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text().lower()
            
            if 'jeremy' in text_content and 'mayo' in text_content:
                print(f"      ✅ Found Jeremy Mayo's profile!")
                member_profile_url = url
                break
            else:
                print(f"      ❌ Not Jeremy's profile")
        else:
            print(f"      ❌ Failed to load")
    
    if not member_profile_url:
        print("❌ Could not find member profile page")
        return False
    
    print(f"✅ Member profile URL: {member_profile_url}")
    print()
    
    # Step 2: Look for messaging forms on the profile page
    print("2. LOOKING FOR MESSAGING FORMS")
    print("-" * 40)
    
    response = auth_service.session.get(
        f"{auth_service.base_url}{member_profile_url}",
        headers=auth_service.get_headers(),
        timeout=30,
        verify=False
    )
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for messaging buttons/links
    messaging_elements = []
    
    # Look for "Send Message" buttons
    send_message_buttons = soup.find_all('a', href=re.compile(r'sendText|sendEmail|message', re.I))
    for button in send_message_buttons:
        messaging_elements.append({
            'type': 'link',
            'text': button.get_text(strip=True),
            'href': button.get('href', ''),
            'onclick': button.get('onclick', '')
        })
    
    # Look for forms with messaging fields
    forms = soup.find_all('form')
    for form in forms:
        form_text = form.get_text().lower()
        if 'message' in form_text or 'text' in form_text or 'email' in form_text:
            messaging_elements.append({
                'type': 'form',
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'fields': [input.get('name', '') for input in form.find_all('input')]
            })
    
    print(f"Found {len(messaging_elements)} messaging elements:")
    for elem in messaging_elements:
        print(f"   - {elem}")
    
    # Step 3: Try to find the actual messaging endpoints
    print()
    print("3. TRYING ACTUAL MESSAGING ENDPOINTS")
    print("-" * 40)
    
    messaging_endpoints = [
        f"/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile/sendText",
        f"/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile/sendEmail",
        f"/action/LeadProfile/sendText",
        f"/action/LeadProfile/sendEmail",
        f"/action/Dashboard/sendText",
        f"/action/Dashboard/sendEmail",
        f"/action/FollowUp/save",
        f"/action/Messages/send",
        f"/action/Messages/sendText",
        f"/action/Messages/sendEmail"
    ]
    
    working_endpoints = []
    for endpoint in messaging_endpoints:
        print(f"   🔍 Trying: {endpoint}")
        try:
            response = auth_service.session.get(
                f"{auth_service.base_url}{endpoint}",
                headers=auth_service.get_headers(),
                timeout=30,
                verify=False
            )
            
            print(f"      Status: {response.status_code}")
            print(f"      Final URL: {response.url}")
            
            if response.ok:
                # Check if this is a messaging form
                soup = BeautifulSoup(response.text, 'html.parser')
                text_content = soup.get_text().lower()
                
                if 'message' in text_content or 'text' in text_content or 'email' in text_content:
                    print(f"      ✅ Looks like a messaging form!")
                    working_endpoints.append(endpoint)
                    
                    # Save the HTML for analysis
                    with open(f"debug_messaging_form_{len(working_endpoints)}.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print(f"      💾 Saved HTML to debug_messaging_form_{len(working_endpoints)}.html")
                else:
                    print(f"      ❌ Not a messaging form")
            else:
                print(f"      ❌ Failed to load")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print(f"✅ Found {len(working_endpoints)} working messaging endpoints:")
    for endpoint in working_endpoints:
        print(f"   - {endpoint}")
    
    # Step 4: Test actual message sending
    if working_endpoints:
        print()
        print("4. TESTING ACTUAL MESSAGE SENDING")
        print("-" * 40)
        
        test_message = "Debug test message from API"
        
        for endpoint in working_endpoints:
            print(f"   📤 Testing SMS via: {endpoint}")
            
            # Try SMS form data
            sms_data = {
                "memberId": TARGET_MEMBER_ID,
                "messageText": test_message,
                "sendMethod": "sms",
                "submit": "Send SMS"
            }
            
            try:
                response = auth_service.session.post(
                    f"{auth_service.base_url}{endpoint}",
                    data=sms_data,
                    headers=auth_service.get_headers(),
                    timeout=30,
                    verify=False
                )
                
                print(f"      Status: {response.status_code}")
                print(f"      Final URL: {response.url}")
                print(f"      Response preview: {response.text[:500]}...")
                
                # Save response for analysis
                with open(f"debug_sms_response_{endpoint.replace('/', '_')}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"      💾 Saved response to debug_sms_response_{endpoint.replace('/', '_')}.html")
                
                # Check for success indicators
                response_text = response.text.lower()
                if 'sent' in response_text or 'success' in response_text:
                    print(f"      ✅ Looks like it worked!")
                elif 'error' in response_text or 'failed' in response_text:
                    print(f"      ❌ Looks like it failed!")
                else:
                    print(f"      ⚠️ Status unclear")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    print()
    print("📊 DEBUG SUMMARY:")
    print(f"   Member Profile: {'✅ Found' if member_profile_url else '❌ Not Found'}")
    print(f"   Messaging Elements: {len(messaging_elements)}")
    print(f"   Working Endpoints: {len(working_endpoints)}")
    
    return True

if __name__ == "__main__":
    debug_real_messaging() 