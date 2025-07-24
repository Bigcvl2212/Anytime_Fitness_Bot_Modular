#!/usr/bin/env python3
"""
Debug ClubOS authentication flow to fix the login session issue
"""
import sys
import os
import re
import requests

# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from config.secrets_local import get_secret


def debug_login_flow():
    """Debug the ClubOS login process step by step"""
    
    session = requests.Session()
    
    # Set headers to mimic a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    base_url = "https://anytime.club-os.com"
    login_url = f"{base_url}/action/Login"
    
    print("[DEBUG] Step 1: Fetching login page...")
    
    # Step 1: Get login page
    login_page = session.get(login_url)
    print(f"[DEBUG] Login page status: {login_page.status_code}")
    print(f"[DEBUG] Login page URL: {login_page.url}")
    print(f"[DEBUG] Login page length: {len(login_page.text)} chars")
    
    # Save login page for analysis
    with open('debug_login_form.html', 'w', encoding='utf-8') as f:
        f.write(login_page.text)
    print("[DEBUG] Saved login page to debug_login_form.html")
    
    # Look for form fields in the login page
    form_inputs = re.findall(r'<input[^>]*name="([^"]*)"[^>]*>', login_page.text)
    print(f"[DEBUG] Found form inputs: {form_inputs}")
    
    # Look for hidden fields
    hidden_fields = {}
    hidden_matches = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>', login_page.text)
    for name, value in hidden_matches:
        hidden_fields[name] = value
        print(f"[DEBUG] Hidden field: {name} = {value}")
    
    # Extract CSRF token if present
    csrf_token = None
    csrf_patterns = [
        r'<meta name="csrf-token" content="([^"]+)"',
        r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"',
        r'<input[^>]*name="_token"[^>]*value="([^"]+)"',
        r'window\.csrfToken\s*=\s*["\']([^"\']+)["\']',
        r'data-csrf="([^"]+)"'
    ]
    
    for pattern in csrf_patterns:
        match = re.search(pattern, login_page.text, re.IGNORECASE)
        if match:
            csrf_token = match.group(1)
            print(f"[DEBUG] Found CSRF token: {csrf_token}")
            break
    
    if not csrf_token:
        print("[DEBUG] No CSRF token found")
    
    print(f"[DEBUG] Cookies after getting login page:")
    for cookie in session.cookies:
        print(f"[DEBUG]   {cookie.name} = {cookie.value}")
    
    print("\n[DEBUG] Step 2: Submitting login form...")
    
    # Step 2: Submit login
    login_data = {
        "username": get_secret('clubos-username'),
        "password": get_secret('clubos-password'),
        "login": "Submit"  # Based on the form we saw
    }
    
    # Add hidden fields
    login_data.update(hidden_fields)
    
    # Add CSRF token if found
    if csrf_token:
        login_data["csrf_token"] = csrf_token
    
    print(f"[DEBUG] Login data: {list(login_data.keys())}")
    
    # Submit login
    login_response = session.post(
        login_url,
        data=login_data,
        allow_redirects=True
    )
    
    print(f"[DEBUG] Login response status: {login_response.status_code}")
    print(f"[DEBUG] Login response URL: {login_response.url}")
    print(f"[DEBUG] Login response length: {len(login_response.text)} chars")
    
    # Save login response
    with open('debug_login_response.html', 'w', encoding='utf-8') as f:
        f.write(login_response.text)
    print("[DEBUG] Saved login response to debug_login_response.html")
    
    print(f"[DEBUG] Cookies after login:")
    for cookie in session.cookies:
        print(f"[DEBUG]   {cookie.name} = {cookie.value}")
    
    # Check if we have the right session
    print("\n[DEBUG] Step 3: Testing calendar access...")
    
    calendar_url = f"{base_url}/action/Calendar"
    calendar_response = session.get(calendar_url)
    
    print(f"[DEBUG] Calendar response status: {calendar_response.status_code}")
    print(f"[DEBUG] Calendar response URL: {calendar_response.url}")
    print(f"[DEBUG] Calendar response length: {len(calendar_response.text)} chars")
    
    # Check if we got redirected back to login
    if "login" in calendar_response.url.lower() or "Username" in calendar_response.text:
        print("[ERROR] Still being redirected to login! Authentication failed.")
        
        # Look for specific error messages
        if "incorrect" in calendar_response.text.lower():
            print("[ERROR] Incorrect credentials detected")
        elif "expired" in calendar_response.text.lower():
            print("[ERROR] Session expired")
        else:
            print("[ERROR] Unknown authentication issue")
    else:
        print("[SUCCESS] Calendar access successful!")
        
        # Save calendar response
        with open('debug_calendar_response.html', 'w', encoding='utf-8') as f:
            f.write(calendar_response.text)
        print("[DEBUG] Saved calendar response to debug_calendar_response.html")
    
    # Test some other endpoints
    print("\n[DEBUG] Step 4: Testing other endpoints...")
    
    test_urls = [
        "/action/Dashboard",
        "/action/Dashboard/view",
        "/action/Dashboard/messages"
    ]
    
    for test_path in test_urls:
        test_url = f"{base_url}{test_path}"
        test_response = session.get(test_url)
        print(f"[DEBUG] {test_path}: {test_response.status_code} -> {test_response.url}")
        
        if "login" not in test_response.url.lower():
            print(f"[SUCCESS] {test_path} accessible!")
        else:
            print(f"[ERROR] {test_path} redirected to login")


if __name__ == "__main__":
    debug_login_flow()
