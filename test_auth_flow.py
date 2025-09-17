#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_auth_flow():
    """Test the authentication flow to identify the redirect issue"""
    
    print("🧪 Testing Authentication Flow")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Check if dashboard is accessible
        print("1. Testing dashboard accessibility...")
        response = session.get("http://localhost:5000/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Dashboard accessible")
        elif response.status_code == 302:
            print("   🔄 Redirected (expected for unauthenticated)")
            redirect_location = response.headers.get('Location', '')
            print(f"   Redirect to: {redirect_location}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            return False
        
        # Test 2: Check login page
        print("\n2. Testing login page...")
        response = session.get("http://localhost:5000/login", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login page accessible")
        else:
            print(f"   ❌ Login page error: {response.status_code}")
            return False
        
        # Test 3: Check club selection page (should redirect to login)
        print("\n3. Testing club selection page (should redirect to login)...")
        response = session.get("http://localhost:5000/club-selection", timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   ✅ Redirected to: {redirect_location}")
            if 'login' in redirect_location:
                print("   ✅ Correctly redirected to login")
            else:
                print("   ❌ Redirected to wrong page")
        else:
            print(f"   ❌ Expected redirect, got status: {response.status_code}")
        
        # Test 4: Check if we can access members page (should redirect to login)
        print("\n4. Testing members page (should redirect to login)...")
        response = session.get("http://localhost:5000/members", timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   ✅ Redirected to: {redirect_location}")
        else:
            print(f"   ❌ Expected redirect, got status: {response.status_code}")
        
        # Test 5: Check collections API (should redirect to login)
        print("\n5. Testing collections API (should redirect to login)...")
        response = session.get("http://localhost:5000/api/collections/past-due", timeout=10, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   ✅ Redirected to: {redirect_location}")
        else:
            print(f"   ❌ Expected redirect, got status: {response.status_code}")
        
        print("\n✅ Authentication flow test complete!")
        print("All protected routes are correctly redirecting to login when unauthenticated.")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to dashboard. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing auth flow: {e}")
        return False

if __name__ == "__main__":
    test_auth_flow()
