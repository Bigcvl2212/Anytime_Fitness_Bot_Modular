#!/usr/bin/env python3
"""
Simple event deletion - just delete the damn events
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI

def delete_events():
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Auth failed")
        return
    
    events = api.get_jeremy_mayo_events()
    print(f"📅 Found {len(events)} events")
    
    # Delete first 7 events
    for i, event in enumerate(events[:7]):
        print(f"🗑️ Deleting event {i+1}: {event.id}")
        
        # Try DELETE request to modern API
        response = api.session.delete(
            f'https://anytime.club-os.com/api/calendar/events/{event.id}',
            headers={
                'Authorization': f'Bearer {api.get_bearer_token()}',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 204, 404]:
            print(f"   ✅ Deleted!")
        else:
            print(f"   ❌ Failed: {response.text[:50]}")
    
    # Check final count
    final_events = api.get_jeremy_mayo_events()
    print(f"📊 Final count: {len(final_events)} (was {len(events)})")

if __name__ == "__main__":
    delete_events()
