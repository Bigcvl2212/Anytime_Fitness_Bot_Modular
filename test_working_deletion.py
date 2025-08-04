#!/usr/bin/env python3
"""
Test the working deletion endpoints
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("🎯 TESTING WORKING DELETION ENDPOINTS")
print("=" * 40)

api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")

if api.authenticate():
    print("✅ Authentication successful!")
    
    # Get current event count
    before_events = api.get_jeremy_mayo_events()
    print(f"📅 Events before: {len(before_events)}")
    
    # Test with event 152375110 
    test_event_id = 152375110
    print(f"\n🎯 Testing deletion of event {test_event_id}")
    
    headers = api.standard_headers.copy()
    headers.update({
        'Authorization': f'Bearer {api.get_bearer_token()}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{api.base_url}/action/Calendar'
    })
    
    # Try the /action/Calendar/deleteEvent endpoint
    print("\n🧪 Testing /action/Calendar/deleteEvent")
    try:
        data = {'eventId': str(test_event_id)}
        
        response = api.session.post(
            f"{api.base_url}/action/Calendar/deleteEvent",
            headers=headers,
            data=data
        )
        
        print(f"   Response: {response.status_code}")
        print(f"   Content length: {len(response.text)}")
        
        if "Something isn't right" in response.text:
            print("   ❌ Got error message")
        elif response.status_code == 200:
            print("   ✅ Success response!")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check if event was deleted
    print("\n📅 Checking if event was deleted...")
    after_events = api.get_jeremy_mayo_events()
    print(f"   Events after: {len(after_events)}")
    
    still_exists = any(e.id == test_event_id for e in after_events)
    if not still_exists:
        print("✅ SUCCESS: Event deleted!")
    else:
        print("❌ Event still exists")
        
        # Try the other endpoint
        print("\n🧪 Testing /action/Calendar/removeEvent")
        try:
            response = api.session.post(
                f"{api.base_url}/action/Calendar/removeEvent", 
                headers=headers,
                data=data
            )
            
            print(f"   Response: {response.status_code}")
            
            # Check again
            final_events = api.get_jeremy_mayo_events()
            print(f"   Events after removeEvent: {len(final_events)}")
            
            still_exists2 = any(e.id == test_event_id for e in final_events)
            if not still_exists2:
                print("✅ SUCCESS: Event deleted with removeEvent!")
            else:
                print("❌ Event still exists after both attempts")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
else:
    print("❌ Authentication failed")
