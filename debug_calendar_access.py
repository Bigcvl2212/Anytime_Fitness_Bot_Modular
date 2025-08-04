"""
Debug Calendar Access with Working Authentication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import ClubOSIntegration
from config.secrets_local import get_secret
from bs4 import BeautifulSoup
import json
from datetime import datetime

def debug_calendar_access():
    """Debug calendar access using working authentication"""
    print("🔍 Starting calendar access debug...")
    
    # Initialize ClubOS integration with proper credentials
    clubos_username = get_secret("clubos-username")
    clubos_password = get_secret("clubos-password")
    
    print(f"🔑 Using username: {clubos_username}")
    print(f"🔑 Using password: {'*' * len(clubos_password) if clubos_password else 'NOT FOUND'}")
    
    integration = ClubOSIntegration(username=clubos_username, password=clubos_password)
    
    # Connect (authenticate)
    print("🔐 Connecting to ClubOS...")
    if not integration.connect():
        print("❌ Failed to connect to ClubOS!")
        return
    
    print("✅ Successfully authenticated with ClubOS!")
    print(f"🔗 Session status: {integration.client.is_authenticated}")
    print(f"📱 Session cookies: {list(integration.client.session.cookies.keys())}")
    
    # Test direct calendar page access
    print("\n📅 Testing direct calendar page access...")
    
    # Try the calendar page that we know works
    calendar_urls = [
        "/action/Calendar/view",
        "/action/Calendar", 
        "/calendar",
        "/action/Calendar/view?__fsk=1221801756",
        "/dashboard"
    ]
    
    for calendar_url in calendar_urls:
        print(f"\n🔄 Trying URL: {calendar_url}")
        
        try:
            full_url = f"https://anytime.club-os.com{calendar_url}"
            response = integration.client.session.get(full_url)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📏 Content Length: {len(response.text)}")
            print(f"🔗 Final URL: {response.url}")
            
            # Check if we're on a login page or actual content
            if "login" in response.text.lower() and "username" in response.text.lower():
                print("❌ Redirected to login page - authentication lost!")
            elif len(response.text) > 50000:
                print("✅ Got substantial content - likely authentic page!")
                
                # Save the content for analysis
                filename = f"data/debug_outputs/calendar_content_{calendar_url.replace('/', '_').replace('?', '_')}.html"
                os.makedirs("data/debug_outputs", exist_ok=True)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"💾 Saved content to: {filename}")
                
                # Quick analysis
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for calendar-related elements
                calendar_elements = soup.find_all(['div', 'table', 'ul'], class_=lambda x: x and 'calendar' in x.lower())
                print(f"📅 Found {len(calendar_elements)} calendar-related elements")
                
                # Look for event elements  
                event_elements = soup.find_all(['div', 'li', 'tr'], class_=lambda x: x and 'event' in x.lower())
                print(f"🎯 Found {len(event_elements)} event-related elements")
                
                # Look for JavaScript variables
                script_tags = soup.find_all('script')
                js_calendar_vars = []
                for script in script_tags:
                    if script.string:
                        script_text = script.string
                        if any(keyword in script_text.lower() for keyword in ['calendar', 'event', 'appointment', 'booking']):
                            js_calendar_vars.append(script_text[:200] + "..." if len(script_text) > 200 else script_text)
                
                print(f"🔧 Found {len(js_calendar_vars)} JavaScript sections with calendar keywords")
                
                # Look for AJAX endpoints
                ajax_endpoints = []
                for script in script_tags:
                    if script.string:
                        import re
                        # Look for AJAX URLs
                        ajax_matches = re.findall(r'["\']([^"\']*(?:ajax|api|calendar|event)[^"\']*)["\']', script.string, re.IGNORECASE)
                        ajax_endpoints.extend(ajax_matches)
                
                unique_endpoints = list(set([ep for ep in ajax_endpoints if len(ep) > 3 and '/' in ep]))
                print(f"🌐 Found {len(unique_endpoints)} potential AJAX endpoints:")
                for ep in unique_endpoints[:10]:  # Show first 10
                    print(f"   - {ep}")
                
            else:
                print("⚠️ Got small content - may be error page or redirect")
                print(f"📋 Preview: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error accessing {calendar_url}: {e}")

if __name__ == "__main__":
    debug_calendar_access()
