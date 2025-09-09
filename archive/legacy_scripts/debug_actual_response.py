#!/usr/bin/env python3
"""
Debug the actual response when sending messages to see what's really happening
"""

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import requests
from bs4 import BeautifulSoup

TARGET_MEMBER_ID = "187032782"

def debug_actual_response():
    """Debug what's actually happening in the response"""
    
    print("🔍 DEBUGGING ACTUAL MESSAGE RESPONSE")
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
    
    # Test the actual messaging endpoint that's being used
    print("📤 TESTING ACTUAL MESSAGING ENDPOINT")
    print("-" * 40)
    
    # The endpoint being used in the current implementation
    endpoint = "/action/Dashboard/messages"
    url = f"{auth_service.base_url}{endpoint}"
    
    print(f"🔍 Testing URL: {url}")
    
    # Test SMS form data
    sms_data = {
        "memberId": TARGET_MEMBER_ID,
        "messageType": "text",
        "messageText": "Debug test SMS message",
        "sendMethod": "sms"
    }
    
    print(f"📤 SMS Data: {sms_data}")
    
    try:
        response = auth_service.session.post(
            url,
            data=sms_data,
            headers=auth_service.get_headers(),
            timeout=30,
            verify=False
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response URL: {response.url}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        # Save the full response
        with open("debug_actual_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("💾 Saved full response to debug_actual_response.html")
        
        # Check if this is actually a messaging form
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for messaging-related content
        text_content = soup.get_text().lower()
        
        print(f"\n🔍 RESPONSE ANALYSIS:")
        print(f"   Contains 'message': {'✅' if 'message' in text_content else '❌'}")
        print(f"   Contains 'text': {'✅' if 'text' in text_content else '❌'}")
        print(f"   Contains 'sms': {'✅' if 'sms' in text_content else '❌'}")
        print(f"   Contains 'email': {'✅' if 'email' in text_content else '❌'}")
        print(f"   Contains 'form': {'✅' if 'form' in text_content else '❌'}")
        
        # Look for success/error indicators
        success_indicators = ['sent', 'success', 'message sent', 'texted', 'emailed']
        error_indicators = ['error', 'failed', 'invalid', 'not found', 'unauthorized']
        
        found_success = False
        found_error = False
        
        for indicator in success_indicators:
            if indicator in text_content:
                print(f"   ✅ Found success indicator: '{indicator}'")
                found_success = True
        
        for indicator in error_indicators:
            if indicator in text_content:
                print(f"   ❌ Found error indicator: '{indicator}'")
                found_error = True
        
        if found_success and not found_error:
            print(f"   🎉 Response indicates SUCCESS!")
        elif found_error:
            print(f"   ❌ Response indicates FAILURE!")
        else:
            print(f"   ⚠️ Response status unclear")
        
        # Check if we got redirected to a different page
        if "dashboard" in response.url.lower() or "login" in response.url.lower():
            print(f"   ⚠️ Got redirected to: {response.url}")
        
        # Look for forms in the response
        forms = soup.find_all('form')
        print(f"\n📋 FORMS FOUND: {len(forms)}")
        for i, form in enumerate(forms):
            print(f"   Form {i+1}:")
            print(f"      Action: {form.get('action', 'N/A')}")
            print(f"      Method: {form.get('method', 'N/A')}")
            inputs = form.find_all('input')
            print(f"      Inputs: {len(inputs)}")
            for inp in inputs:
                print(f"         - {inp.get('name', 'N/A')}: {inp.get('type', 'N/A')}")
        
        # Look for any messaging-related elements
        messaging_elements = soup.find_all(['a', 'button', 'input'], 
                                         string=lambda text: text and any(word in text.lower() for word in ['message', 'text', 'sms', 'email']))
        print(f"\n📱 MESSAGING ELEMENTS FOUND: {len(messaging_elements)}")
        for elem in messaging_elements:
            print(f"   - {elem.name}: {elem.get_text(strip=True)}")
        
        print(f"\n📄 RESPONSE PREVIEW (first 1000 chars):")
        print(f"{response.text[:1000]}...")
        
    except Exception as e:
        print(f"❌ Error testing messaging endpoint: {e}")
        return False
    
    return True

if __name__ == "__main__":
    debug_actual_response() 