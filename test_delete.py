#!/usr/bin/env python3
"""
Test delete functionality with a known event ID
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_delete():
    """Test delete functionality"""
    
    print("🗑️ Testing Delete Functionality")
    print("=" * 40)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Get all events
        events = api.get_jeremy_mayo_events()
        print(f"📅 Found {len(events)} events")
        
        if events:
            # Try to delete the first event (just as a test)
            first_event = events[0]
            print(f"\n🎯 Testing delete on event ID: {first_event.id}")
            print(f"   Event funding status: {first_event.funding_status}")
            print(f"   Event attendees: {len(first_event.attendees)}")
            
            # Test the delete method
            if api.delete_event_clubos_way(first_event.id):
                print("✅ Delete method executed successfully!")
            else:
                print("❌ Delete method failed")
        else:
            print("❌ No events found")
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    test_delete()
