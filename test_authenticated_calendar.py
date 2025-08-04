"""
Corrected Calendar Access Using Proper Integration Pattern
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import ClubOSIntegration
from bs4 import BeautifulSoup
import json
from datetime import datetime

def test_calendar_access():
    """Test calendar access using the proper integration pattern"""
    print("🔍 Testing calendar access with proper integration...")
    
    # Initialize and connect
    integration = ClubOSIntegration()
    if not integration.connect():
        print("❌ Failed to connect!")
        return
    
    print("✅ Connected successfully!")
    
    # The key insight: use the client that's already authenticated 
    # Let's see what URLs the client actually visited during authentication
    print(f"\n🔍 Client authentication status: {integration.client.is_authenticated}")
    print(f"🍪 Session cookies: {dict(integration.client.session.cookies)}")
    
    # Test using the authenticated client directly (this should work)
    print("\n📅 Testing calendar access using authenticated client...")
    
    try:
        # Try the dashboard URL that worked during authentication
        dashboard_url = "https://anytime.club-os.com/action/Dashboard/view"
        print(f"🔄 Accessing dashboard: {dashboard_url}")
        
        response = integration.client.session.get(dashboard_url)
        print(f"📊 Dashboard Status: {response.status_code}")
        print(f"📏 Dashboard Content Length: {len(response.text)}")
        print(f"🔗 Dashboard Final URL: {response.url}")
        
        # Check if this is actually the dashboard or login redirect
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("❌ Dashboard redirected to login!")
        else:
            print("✅ Dashboard access successful!")
            
            # Save dashboard content
            with open("data/debug_outputs/authenticated_dashboard.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved dashboard content")
        
        # Now try calendar URL that was visited during authentication
        calendar_url = "https://anytime.club-os.com/action/Calendar/view"
        print(f"\n🔄 Accessing calendar: {calendar_url}")
        
        response = integration.client.session.get(calendar_url)
        print(f"📊 Calendar Status: {response.status_code}")
        print(f"📏 Calendar Content Length: {len(response.text)}")
        print(f"🔗 Calendar Final URL: {response.url}")
        
        # Check if this is actually the calendar or login redirect
        if "login" in response.text.lower() and "username" in response.text.lower():
            print("❌ Calendar redirected to login!")
        else:
            print("✅ Calendar access successful!")
            
            # Save calendar content
            with open("data/debug_outputs/authenticated_calendar.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved calendar content")
            
            # Quick analysis of calendar content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for calendar-specific elements
            print(f"\n📋 Analyzing calendar content...")
            
            # Look for forms (booking forms, etc.)
            forms = soup.find_all('form')
            print(f"📝 Found {len(forms)} forms")
            
            # Look for calendar-related classes
            calendar_divs = soup.find_all('div', class_=lambda x: x and any(keyword in x.lower() for keyword in ['calendar', 'schedule', 'appointment', 'booking']))
            print(f"📅 Found {len(calendar_divs)} calendar-related divs")
            
            # Look for JavaScript that might contain calendar data
            scripts = soup.find_all('script')
            calendar_scripts = []
            for script in scripts:
                if script.string and any(keyword in script.string.lower() for keyword in ['calendar', 'event', 'appointment', 'schedule', 'booking']):
                    calendar_scripts.append(script.string)
            
            print(f"🔧 Found {len(calendar_scripts)} scripts with calendar keywords")
            
            # Look for table structures (might contain schedule data)
            tables = soup.find_all('table')
            print(f"📊 Found {len(tables)} tables")
            
            # Look for list structures (might contain events)
            lists = soup.find_all(['ul', 'ol'])
            print(f"📋 Found {len(lists)} lists")
            
            # Look for any data attributes that might contain calendar info
            elements_with_data = soup.find_all(attrs=lambda x: x and any(key.startswith('data-') for key in x.keys()))
            calendar_data_elements = [el for el in elements_with_data if any(keyword in str(el.get('data-' + attr, '')).lower() for attr in ['date', 'event', 'calendar', 'appointment'] for keyword in ['date', 'event', 'calendar', 'appointment'])]
            print(f"🏷️ Found {len(calendar_data_elements)} elements with calendar-related data attributes")
        
    except Exception as e:
        print(f"❌ Error during calendar access: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_access()
