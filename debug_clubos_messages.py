#!/usr/bin/env python3
"""
Debug ClubOS Messages
Understand the exact structure and endpoints for message loading
"""

import sys
import os
sys.path.insert(0, 'src')

import requests
from config.secrets_local import get_secret

def debug_clubos_messages():
    """Debug ClubOS message loading"""
    print("🔍 Debugging ClubOS Message Loading")
    
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ Credentials not found")
        return
    
    print(f"✅ Using credentials: {username[:5]}...")
    
    session = requests.Session()
    base_url = "https://anytime.club-os.com"
    
    # Set browser headers
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    })
    
    # Login
    print("🔐 Logging in...")
    login_url = f"{base_url}/action/Login"
    response = session.get(login_url)
    
    login_data = {
        "username": username,
        "password": password,
        "rememberMe": "false"
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"Login response: {response.status_code}")
    print(f"Final URL: {response.url}")
    print(f"Response contains 'Dashboard': {'Dashboard' in response.text}")
    print(f"Response contains login form: {'username' in response.text and 'password' in response.text}")
    
    # Check if we're actually logged in by looking for dashboard content
    if ("Dashboard" in response.url or 
        "dashboard" in response.text.lower() or 
        "logout" in response.text.lower() or
        response.status_code == 200):
        print("✅ Login appears successful")
    else:
        print("❌ Login may have failed")
        print(f"Response preview: {response.text[:500]}...")
        return
    
    print("✅ Login successful")
    
    # Try different message endpoints
    endpoints_to_try = [
        f"{base_url}/action/Dashboard/view",
        f"{base_url}/action/Dashboard",
        f"{base_url}/action/Messages",
        f"{base_url}/action/Dashboard/messages",
        f"{base_url}/action/Dashboard/messageList",
        f"{base_url}/action/Api/messages",
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n📡 Testing endpoint: {endpoint}")
        
        try:
            # Try without params
            response = session.get(endpoint)
            print(f"  Status: {response.status_code}")
            print(f"  Content length: {len(response.text)}")
            print(f"  Contains 'message-list': {'message-list' in response.text}")
            print(f"  Contains 'follow-up': {'follow-up' in response.text}")
            print(f"  Contains 'messages': {'messages' in response.text.lower()}")
            
            # Try with owner param (Jeremy Mayo's ID)
            if "?" not in endpoint:
                params_response = session.get(endpoint, params={"owner": "187032782"})
                print(f"  With owner param - Status: {params_response.status_code}")
                print(f"  With owner param - Length: {len(params_response.text)}")
                
                if params_response.text != response.text:
                    print("  ⚠️ Different response with owner param!")
            
            # Look for specific message indicators
            if "message-count" in response.text:
                print("  🎯 Found message-count element!")
            
            if "message-list" in response.text:
                print("  🎯 Found message-list element!")
                
            # Save response for analysis if it looks promising
            if ("message" in response.text.lower() and len(response.text) > 5000):
                filename = f"debug_response_{endpoint.split('/')[-1]}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  💾 Saved response to {filename}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n🔍 Looking for AJAX endpoints in dashboard...")
    
    # Get main dashboard and look for JavaScript that loads messages
    dashboard_response = session.get(f"{base_url}/action/Dashboard/view")
    
    if "loadMessages" in dashboard_response.text or "ajax" in dashboard_response.text.lower():
        print("🎯 Found AJAX loading patterns!")
        
        # Save dashboard for analysis
        with open("debug_dashboard.html", 'w', encoding='utf-8') as f:
            f.write(dashboard_response.text)
        print("💾 Saved dashboard to debug_dashboard.html")
    
    print("\n✅ Debug complete - check saved files for analysis")

if __name__ == "__main__":
    debug_clubos_messages()


