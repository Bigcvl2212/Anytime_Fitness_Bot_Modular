#!/usr/bin/env python3
"""
Explore ClubOS deletion endpoints
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("🔍 EXPLORING CLUBOS DELETION METHODS")
print("=" * 40)

# Initialize API
api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")

if api.authenticate():
    print("✅ Authentication successful!")
    
    # Let's try different deletion endpoints
    test_event_id = 152375110
    print(f"\n🎯 Testing with event {test_event_id}")
    
    headers = api.standard_headers.copy()
    headers.update({
        'Authorization': f'Bearer {api.get_bearer_token()}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{api.base_url}/action/Calendar'
    })
    
    # Try different deletion approaches
    deletion_endpoints = [
        '/api/calendar/events/delete',
        '/api/calendar/event/delete', 
        '/action/Calendar/deleteEvent',
        '/action/Calendar/removeEvent',
        '/action/EventPopup/delete',
    ]
    
    for endpoint in deletion_endpoints:
        print(f"\n🧪 Trying endpoint: {endpoint}")
        
        try:
            # Simple ID-based deletion
            data = {'eventId': str(test_event_id)}
            
            response = api.session.post(
                f"{api.base_url}{endpoint}",
                headers=headers,
                data=data
            )
            
            print(f"   Response: {response.status_code}")
            if response.status_code == 200:
                print(f"   Content: {response.text[:200]}")
            elif response.status_code == 404:
                print("   ❌ Endpoint not found")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Try DELETE method instead of POST
    print(f"\n🧪 Trying DELETE method on API endpoint")
    try:
        response = api.session.delete(
            f"{api.base_url}/api/calendar/events/{test_event_id}",
            headers=headers
        )
        print(f"   DELETE response: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ DELETE Error: {str(e)}")
        
else:
    print("❌ Authentication failed")
