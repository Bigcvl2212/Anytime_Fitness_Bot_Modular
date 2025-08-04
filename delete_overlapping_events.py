#!/usr/bin/env python3
"""
Delete the overlapping Monday morning events we just created
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_overlapping_events():
    """Delete the overlapping Monday morning events"""
    
    print("🗑️ DELETING OVERLAPPING MONDAY MORNING EVENTS")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Get all events
        events = api.get_jeremy_mayo_events()
        print(f"📅 Found {len(events)} total events")
        
        deleted_count = 0
        
        # Look for recent events (likely the ones we just created)
        # Since the events have None titles, let's delete the most recent ones
        print(f"\n🎯 Deleting the last 4 events (the overlapping ones)...")
        
        for i, event in enumerate(events[-4:]):  # Get last 4 events
            event_index = len(events) - 4 + i
            print(f"\nDeleting event #{event_index + 1}: ID {event.id}")
            print(f"   Funding Status: {event.funding_status}")
            print(f"   Attendees: {len(event.attendees)}")
            
            if api.delete_event_clubos_way(event.id):
                print(f"✅ Event {event.id} deleted successfully!")
                deleted_count += 1
            else:
                print(f"❌ Failed to delete event {event.id}")
        
        print(f"\n🎯 DELETION SUMMARY: {deleted_count}/4 events deleted")
        
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    delete_overlapping_events()
