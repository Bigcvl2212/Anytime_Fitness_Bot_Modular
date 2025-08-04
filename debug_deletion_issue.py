#!/usr/bin/env python3
"""
Debug the actual deletion issue by trying different approaches
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO)

def debug_deletion():
    """Debug why deletion isn't working"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("✅ Authenticated")
        
        # Get a test event
        events = api.get_jeremy_mayo_events()
        test_event_id = events[0].id
        print(f"🎯 Testing deletion on event ID: {test_event_id}")
        
        # Try the current method
        print("\n1. Testing current deletion method...")
        result = api.remove_event_popup(test_event_id)
        print(f"Result: {result}")
        
        # Check if it's actually gone
        events_after = api.get_jeremy_mayo_events()
        print(f"Events before: {len(events)}, after: {len(events_after)}")
        
        if len(events_after) == len(events):
            print("❌ Current method doesn't actually delete events!")
            
            # Try different deletion approaches
            print("\n2. Trying alternative deletion methods...")
            
            # Method 1: Try DELETE HTTP method instead of POST
            print("   Trying DELETE HTTP method...")
            try:
                response = api.session.delete(
                    f"{api.base_url}/action/EventPopup/remove/{test_event_id}",
                    headers={
                        'Authorization': f'Bearer {api.get_bearer_token()}',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                )
                print(f"   DELETE response: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"   DELETE failed: {e}")
            
            # Method 2: Try different URL patterns
            print("   Trying different URL patterns...")
            for url_pattern in [
                f"/action/Calendar/removeEvent/{test_event_id}",
                f"/action/Calendar/deleteEvent/{test_event_id}",
                f"/action/Event/delete/{test_event_id}",
                f"/calendar/delete/{test_event_id}"
            ]:
                try:
                    response = api.session.post(
                        f"{api.base_url}{url_pattern}",
                        headers={
                            'Authorization': f'Bearer {api.get_bearer_token()}',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    )
                    print(f"   {url_pattern}: {response.status_code}")
                    if response.status_code == 200 and "OK" in response.text:
                        print(f"     ✅ Possible working endpoint!")
                except:
                    pass
            
            # Method 3: Try with different form data structure
            print("   Trying minimal form data...")
            try:
                response = api.session.post(
                    f"{api.base_url}/action/EventPopup/remove",
                    headers={
                        'Authorization': f'Bearer {api.get_bearer_token()}',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    data={
                        'id': test_event_id,
                        '_sourcePage': api.get_source_page_token(),
                        '__fp': api.get_fingerprint_token()
                    }
                )
                print(f"   Minimal data: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"   Minimal data failed: {e}")
        
        else:
            print("✅ Current method works!")

if __name__ == "__main__":
    debug_deletion()
