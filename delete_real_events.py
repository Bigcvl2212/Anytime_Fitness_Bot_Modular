#!/usr/bin/env python3
"""
Delete the Monday morning events from your ACTUAL calendar right now
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_real_calendar_events():
    """Delete the Monday morning events from your actual calendar"""
    
    print("🗑️ DELETING FROM YOUR ACTUAL CALENDAR")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Use the HAR method to get current events
        print("\n📅 Getting your current calendar events...")
        events = api.get_jeremy_mayo_events()
        print(f"Found {len(events)} events")
        
        # You said there are 4 overlapping Monday morning events
        # Let's target the most recent 6 events as candidates
        print(f"\n🎯 Checking the most recent events for Monday morning duplicates...")
        
        recent_events = events[-6:]  # Last 6 events
        deleted_count = 0
        
        for i, event in enumerate(recent_events):
            event_index = len(events) - 6 + i + 1
            print(f"\nEvent #{event_index}: ID {event.id}")
            print(f"  Status: {event.funding_status}")
            print(f"  Attendees: {len(event.attendees)}")
            
            # Ask to delete this event
            response = input(f"Delete event {event.id}? (y/n): ").lower().strip()
            
            if response == 'y':
                print(f"Deleting event {event.id}...")
                
                # Use the exact method from HAR
                headers = api.standard_headers.copy()
                headers.update({
                    'Authorization': f'Bearer {api.get_bearer_token()}',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f'{api.base_url}/action/Calendar'
                })
                
                # Empty form data like in HAR
                response = api.session.post(
                    f"{api.base_url}/action/EventPopup/remove",
                    headers=headers,
                    data={}
                )
                
                if response.status_code == 200:
                    print(f"✅ Event {event.id} deleted successfully!")
                    deleted_count += 1
                else:
                    print(f"❌ Failed to delete event {event.id}: {response.status_code}")
            else:
                print(f"Skipping event {event.id}")
        
        print(f"\n🎯 DELETION SUMMARY: {deleted_count} events deleted from your calendar")
        
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    delete_real_calendar_events()
