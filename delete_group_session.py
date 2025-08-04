#!/usr/bin/env python3
"""
Delete the Group Training Session from the calendar
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_group_session():
    """Find and delete the Group Training Session"""
    
    print("🗑️ Deleting Group Training Session")
    print("=" * 40)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    print("\n1. Authenticating...")
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Get current events using HAR method
        print("\n2. Finding Group Training Session...")
        events = api.get_jeremy_mayo_events()
        print(f"📅 Found {len(events)} events to check")
        
        # Look for Group Training Session
        target_event = None
        for event in events:
            if event.title and 'Group Training' in event.title:
                target_event = event
                print(f"🎯 Found target event: ID {event.id} - {event.title}")
                break
        
        if target_event:
            # Delete the event
            print(f"\n3. Deleting event {target_event.id}...")
            if api.delete_event_clubos_way(target_event.id):
                print("✅ Group Training Session deleted successfully!")
            else:
                print("❌ Failed to delete Group Training Session")
        else:
            print("❌ No Group Training Session found in calendar")
            
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    delete_group_session()
