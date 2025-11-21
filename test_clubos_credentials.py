#!/usr/bin/env python3
"""
Test ClubOS Credentials
Quick script to verify if your ClubOS credentials are working
"""

import requests
from bs4 import BeautifulSoup
import urllib3
import sys
import os

# Add the workspace to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_clubos_credentials():
    """Test ClubOS authentication with credentials from config"""
    print("=" * 60)
    print("ClubOS Credential Verification Test")
    print("=" * 60)

    # Import credentials
    try:
        from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD
        print(f"\n[OK] Loaded credentials from config/clubhub_credentials.py")
        print(f"  Username: {CLUBOS_USERNAME}")
        print(f"  Password: {'*' * len(CLUBOS_PASSWORD)}")
    except ImportError as e:
        print(f"\n[FAIL] Failed to import credentials: {e}")
        print(f"  Make sure config/clubhub_credentials.py exists")
        return False

    if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
        print(f"\n[FAIL] Credentials are empty in config file")
        return False

    # Test authentication
    print(f"\n>> Testing authentication to ClubOS...")

    base_url = "https://anytime.club-os.com"
    session = requests.Session()

    # Set headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    session.headers.update(headers)

    try:
        # Step 1: Get login page
        print(f"  >> Fetching login page...")
        login_url = f"{base_url}/action/Login/view"
        login_response = session.get(login_url, verify=False, timeout=30)

        if login_response.status_code != 200:
            print(f"  [FAIL] Failed to load login page: {login_response.status_code}")
            return False

        print(f"  [OK] Login page loaded successfully")

        # Step 2: Extract CSRF tokens
        print(f"  >> Extracting CSRF tokens...")
        soup = BeautifulSoup(login_response.text, 'html.parser')
        source_page = soup.find('input', {'name': '_sourcePage'})
        fp_token = soup.find('input', {'name': '__fp'})

        if not source_page or not fp_token:
            print(f"  [FAIL] Failed to find CSRF tokens in login page")
            return False

        source_page_value = source_page.get('value')
        fp_token_value = fp_token.get('value')
        print(f"  [OK] CSRF tokens extracted")

        # Step 3: Submit login
        print(f"  >> Submitting login credentials...")
        login_data = {
            'login': 'Submit',
            'username': CLUBOS_USERNAME,
            'password': CLUBOS_PASSWORD,
            '_sourcePage': source_page_value,
            '__fp': fp_token_value
        }

        auth_response = session.post(
            f"{base_url}/action/Login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects=True,
            verify=False,
            timeout=30
        )

        # Step 4: Check authentication result
        print(f"\n>> Authentication Result:")
        print(f"  Status Code: {auth_response.status_code}")
        print(f"  Final URL: {auth_response.url}")

        # Check for session cookie
        jsessionid = session.cookies.get('JSESSIONID')
        if jsessionid:
            print(f"  Session ID: {jsessionid[:20]}...")
        else:
            print(f"  Session ID: NOT FOUND")

        # Determine success or failure
        if 'Login' in auth_response.url or '/login' in auth_response.url.lower():
            print(f"\n[FAIL] AUTHENTICATION FAILED")
            print(f"  ClubOS redirected back to login page")
            print(f"  This means:")
            print(f"    - Username or password is incorrect")
            print(f"    - Account may be locked")
            print(f"    - CSRF tokens were invalid")
            print(f"\n[ACTION REQUIRED]:")
            print(f"  1. Verify username in ClubOS web interface")
            print(f"  2. Try resetting your password")
            print(f"  3. Update credentials in config/clubhub_credentials.py")
            return False

        if 'Session Expired' in auth_response.text:
            print(f"\n[FAIL] AUTHENTICATION FAILED")
            print(f"  ClubOS returned 'Session Expired'")
            print(f"  This usually means credentials are incorrect")
            print(f"\n[ACTION REQUIRED]:")
            print(f"  1. Verify credentials in ClubOS web interface")
            print(f"  2. Update credentials in config/clubhub_credentials.py")
            return False

        if not jsessionid:
            print(f"\n[FAIL] AUTHENTICATION FAILED")
            print(f"  No session cookie received from ClubOS")
            print(f"\n[ACTION REQUIRED]:")
            print(f"  1. Check if your account is active")
            print(f"  2. Try logging in through ClubOS web interface")
            return False

        # Success!
        print(f"\n[SUCCESS] AUTHENTICATION SUCCESSFUL!")
        print(f"  Your ClubOS credentials are working correctly")
        print(f"  Session established with ClubOS")

        return True

    except Exception as e:
        print(f"\n[ERROR] during authentication test:")
        print(f"  {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_clubos_credentials()

    print("\n" + "=" * 60)
    if success:
        print("[PASSED] Credential Test PASSED")
        print("Your ClubOS credentials are working correctly!")
    else:
        print("[FAILED] Credential Test FAILED")
        print("Please fix the issues above and try again")
    print("=" * 60)

    sys.exit(0 if success else 1)
