"""
Debug Request Sequence to Understand Session Management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import RobustClubOSClient
import requests
from bs4 import BeautifulSoup

def debug_request_sequence():
    """Debug the exact request sequence during authentication"""
    print("🔍 Starting detailed request sequence debug...")
    
    username = os.getenv('CLUBOS_USERNAME')
    password = os.getenv('CLUBOS_PASSWORD')
    
    if not username or not password:
        print("❌ Missing credentials")
        return
    
    # Create a session with detailed logging
    session = requests.Session()
    
    # Set headers like the client does
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0"
    })
    
    print("📱 Session headers configured")
    
    # Step 1: Get login page
    print("\n🔗 Step 1: Getting login page...")
    login_url = "https://anytime.club-os.com/action/Login/view?__fsk=1221801756"
    response = session.get(login_url)
    
    print(f"📊 Login page status: {response.status_code}")
    print(f"🔗 Login page URL: {response.url}")
    print(f"🍪 Cookies after login page: {list(session.cookies.keys())}")
    
    # Extract form data
    soup = BeautifulSoup(response.text, 'html.parser')
    form_data = {}
    
    login_form = None
    forms = soup.find_all('form')
    for form in forms:
        if form.find('input', {'name': 'username'}):
            login_form = form
            break
    
    if not login_form:
        print("❌ No login form found!")
        return
    
    inputs = login_form.find_all('input')
    for input_field in inputs:
        name = input_field.get('name')
        value = input_field.get('value', '')
        input_type = input_field.get('type', 'text')
        
        if name and input_type != 'submit':
            form_data[name] = value
            print(f"🔑 Form field: {name} = {value[:20]}...")
    
    # Add credentials
    form_data['username'] = username
    form_data['password'] = password
    
    # Step 2: Submit login
    print("\n🔐 Step 2: Submitting login...")
    login_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": login_url,
        "Origin": "https://anytime.club-os.com",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1"
    }
    
    login_post_url = "https://anytime.club-os.com/action/Login"
    response = session.post(login_post_url, data=form_data, headers=login_headers, allow_redirects=True)
    
    print(f"📊 Login response status: {response.status_code}")
    print(f"🔗 Login response URL: {response.url}")
    print(f"🍪 Cookies after login: {dict(session.cookies)}")
    print(f"📏 Response content length: {len(response.text)}")
    
    # Check if we're still on login page
    if "login" in response.text.lower() and "username" in response.text.lower():
        print("❌ Still on login page after authentication!")
        return
    else:
        print("✅ Authentication appears successful!")
    
    # Step 3: Try to access calendar immediately 
    print("\n📅 Step 3: Immediate calendar access...")
    calendar_url = "https://anytime.club-os.com/action/Calendar/view"
    response = session.get(calendar_url)
    
    print(f"📊 Calendar status: {response.status_code}")
    print(f"🔗 Calendar URL: {response.url}")
    print(f"📏 Calendar content length: {len(response.text)}")
    
    if "login" in response.text.lower() and "username" in response.text.lower():
        print("❌ Calendar redirected to login!")
        
        # Let's check the response headers and see what's happening
        print("\n🔍 Analyzing failed calendar request...")
        print(f"📋 Response headers: {dict(response.headers)}")
        print(f"🍪 Current cookies: {dict(session.cookies)}")
        
        # Try to understand the redirect
        if 'redirect' in response.url:
            print(f"🔄 Redirect URL detected: {response.url}")
    else:
        print("✅ Calendar access successful!")
        
        # Save successful calendar content
        with open("data/debug_outputs/successful_calendar.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("💾 Saved successful calendar content")

if __name__ == "__main__":
    debug_request_sequence()
