#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import ClubOSIntegration

def test_calendar():
    print("=== TESTING CALENDAR FETCH DIRECTLY ===")
    
    # Use the ClubOS integration directly
    clubos = ClubOSIntegration()
    
    if clubos.connect():
        print("✅ Connected successfully")
        
        # Test accessing calendar page directly
        print("\n📅 Testing direct calendar page access...")
        calendar_url = f"{clubos.client.base_url}/action/Calendar"
        
        response = clubos.client.session.get(
            calendar_url,
            headers={
                'Referer': f'{clubos.client.base_url}/action/Dashboard'
            },
            timeout=15
        )
        
        if response.ok:
            print(f"   ✅ Direct calendar access successful ({len(response.text)} chars)")
            
            # Save for debugging
            os.makedirs("data/debug_outputs", exist_ok=True)
            with open("data/debug_outputs/direct_calendar_test.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Check if this is a login page or actual calendar
            if "login" in response.text.lower() and "username" in response.text.lower():
                print("   ❌ Still redirected to login page")
            else:
                print("   ✅ Got actual calendar page!")
                
                # Look for calendar structure elements
                if "calendar" in response.text.lower():
                    print("   📅 Contains calendar-related content")
                if "187032782" in response.text:  # Jeremy's ID
                    print("   👤 Found Jeremy's ID in the page")
                if "schedule" in response.text.lower():
                    print("   📋 Contains schedule-related content")
        else:
            print(f"   ❌ Failed to access calendar page: {response.status_code}")
        
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    test_calendar()
