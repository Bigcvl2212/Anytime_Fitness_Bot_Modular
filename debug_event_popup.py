#!/usr/bin/env python3
"""
Debug what the event popup is actually returning
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI

def debug_event_popup():
    """Debug what the event popup endpoint returns"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Get first event
    events = api.get_jeremy_mayo_events()
    if not events:
        print("❌ No events found")
        return
    
    test_event = events[0]
    event_id = test_event.id
    
    print(f"🔍 Debugging event popup for {event_id}")
    
    # Try different endpoints
    endpoints_to_try = [
        f"/action/EventPopup/show/{event_id}",
        f"/action/EventPopup/edit/{event_id}",
        f"/action/EventPopup?id={event_id}",
        f"/action/Calendar/eventPopup?id={event_id}",
        f"/action/Calendar/event/{event_id}"
    ]
    
    headers = {
        'Authorization': f'Bearer {api.get_bearer_token()}',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://anytime.club-os.com/action/Calendar'
    }
    
    for endpoint in endpoints_to_try:
        try:
            print(f"\n🌐 Testing endpoint: {endpoint}")
            
            response = api.session.get(
                f"{api.base_url}{endpoint}",
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content Length: {len(response.text)}")
            print(f"   Preview: {response.text[:200]}...")
            
            if response.status_code == 200 and len(response.text) > 1000:
                print(f"   ✅ This endpoint looks promising!")
                
                # Save the content for analysis
                with open(f"debug_event_popup_{event_id}.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"   💾 Saved content to debug_event_popup_{event_id}.html")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎯 Summary:")
    print("If any endpoint showed promising results, check the saved HTML file")
    print("We need to find the endpoint that returns the actual event form")

if __name__ == "__main__":
    debug_event_popup()
