#!/usr/bin/env python3
"""
Try direct API deletion and also test different parameters
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("🔬 TESTING DIRECT API DELETION")
print("=" * 40)

api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")

if api.authenticate():
    print("✅ Authentication successful!")
    
    test_event_id = 152375110
    print(f"\n🎯 Testing event {test_event_id}")
    
    # Test different parameter combinations
    headers = api.standard_headers.copy()
    headers.update({
        'Authorization': f'Bearer {api.get_bearer_token()}',
        'Content-Type': 'application/json',  # Try JSON instead
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{api.base_url}/action/Calendar'
    })
    
    # Try direct API deletion with different parameters
    test_cases = [
        {
            'endpoint': '/api/calendar/events',
            'method': 'DELETE',
            'url_suffix': f'/{test_event_id}',
            'data': None
        },
        {
            'endpoint': '/api/calendar/events',
            'method': 'POST', 
            'url_suffix': '/delete',
            'data': {'id': test_event_id}
        },
        {
            'endpoint': '/api/calendar/events',
            'method': 'POST',
            'url_suffix': '',
            'data': {'action': 'delete', 'eventId': test_event_id}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['method']} {test_case['endpoint']}{test_case['url_suffix']}")
        
        try:
            url = f"{api.base_url}{test_case['endpoint']}{test_case['url_suffix']}"
            
            if test_case['method'] == 'DELETE':
                response = api.session.delete(url, headers=headers)
            else:
                if test_case['data']:
                    import json
                    response = api.session.post(
                        url, 
                        headers=headers,
                        data=json.dumps(test_case['data'])
                    )
                else:
                    response = api.session.post(url, headers=headers)
            
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text[:500]
                print(f"   Content preview: {content}")
                
                # Check if it worked
                after_events = api.get_jeremy_mayo_events()
                still_exists = any(e.id == test_event_id for e in after_events)
                
                if not still_exists:
                    print("   ✅ SUCCESS: Event deleted!")
                    break
                else:
                    print("   ❌ Event still exists")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # If nothing worked, let's try to understand what ClubOS expects
    print(f"\n🔍 Final check - getting event details to understand structure...")
    
    # Get the actual event data to see what we're working with
    events = api.get_jeremy_mayo_events()
    target_event = next((e for e in events if e.id == test_event_id), None)
    
    if target_event:
        print(f"   Event {test_event_id} details:")
        print(f"   - Title: {target_event.title}")
        print(f"   - Status: {target_event.funding_status}")
        print(f"   - Attendees: {len(target_event.attendees) if target_event.attendees else 0}")
        print(f"   - Start: {target_event.start_time}")
        print(f"   - Type: {target_event.event_type}")
    else:
        print(f"   Event {test_event_id} not found in current events")
        
else:
    print("❌ Authentication failed")
