#!/usr/bin/env python3
"""
Quick test to verify ClubOS authentication and calendar access
"""
import sys
import os

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from services.api.clubos_api_client import ClubOSAPIAuthentication
from config.secrets_local import get_secret

def test_auth_and_calendar():
    """Test authentication and calendar access"""
    
    # Initialize and authenticate
    auth_service = ClubOSAPIAuthentication()
    print("[INFO] Authenticating with ClubOS...")
    
    if not auth_service.login(get_secret('clubos-username'), get_secret('clubos-password')):
        print("[ERROR] Authentication failed")
        return
    
    print("[INFO] Authentication successful")
    print(f"[INFO] Session cookies: {list(auth_service.session.cookies.keys())}")
    
    # Test different calendar URLs
    calendar_urls = [
        "/action/Calendar",
        "/action/Dashboard",
        "/action/Dashboard/view",
        "/calendar",
        "/scheduling"
    ]
    
    for url in calendar_urls:
        full_url = f"{auth_service.base_url}{url}"
        print(f"\n[TEST] Accessing: {full_url}")
        
        response = auth_service.session.get(full_url)
        print(f"[TEST] Status: {response.status_code}")
        
        # Check if we got redirected to login
        if "js-login-form" in response.text:
            print("[TEST] ❌ Redirected to login page")
        elif "Calendar" in response.text or "calendar" in response.text:
            print("[TEST] ✅ Appears to be calendar content")
            print(f"[TEST] Content length: {len(response.text)} chars")
        else:
            print("[TEST] ❓ Unknown content type")
            print(f"[TEST] Content length: {len(response.text)} chars")
            # Show first 200 chars
            print(f"[TEST] Preview: {response.text[:200]}...")

if __name__ == "__main__":
    test_auth_and_calendar()
