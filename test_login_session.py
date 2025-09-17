#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_login_session():
    """Test the login process and session handling"""
    
    print("🧪 Testing Login Session Handling")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Step 1: Get login page
        print("1. Getting login page...")
        response = session.get("http://localhost:5000/login", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("   ❌ Cannot access login page")
            return False
        
        # Step 2: Check cookies after login page
        print(f"   Cookies after login page: {dict(session.cookies)}")
        
        # Step 3: Try to access a protected route (should redirect to login)
        print("\n2. Testing protected route before login...")
        response = session.get("http://localhost:5000/members", timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Correctly redirected to login")
        else:
            print(f"   ❌ Expected redirect, got status: {response.status_code}")
        
        # Step 4: Check if we can access club selection (should redirect to login)
        print("\n3. Testing club selection before login...")
        response = session.get("http://localhost:5000/club-selection", timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✅ Correctly redirected to login")
        else:
            print(f"   ❌ Expected redirect, got status: {response.status_code}")
        
        print("\n✅ Session handling test complete!")
        print("The issue is likely in the login process itself or session persistence.")
        print("\nTo debug further, you should:")
        print("1. Check the browser's developer tools for cookies")
        print("2. Look at the Flask logs when you try to login")
        print("3. Check if the session is being saved properly after login")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing login session: {e}")
        return False

if __name__ == "__main__":
    test_login_session()
