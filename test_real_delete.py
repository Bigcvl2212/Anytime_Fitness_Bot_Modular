#!/usr/bin/env python3
"""
Test the REAL deletion method that's already in the API
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_real_deletion():
    """Test the delete_calendar_event_real method that's already implemented"""
    
    print("🎯 TESTING REAL DELETION METHOD")
    print("=" * 40)
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Get current events
    events_before = api.get_jeremy_mayo_events()
    print(f"📅 Events before deletion: {len(events_before)}")
    
    if len(events_before) == 0:
        print("❌ No events to test deletion on")
        return
    
    # Pick the first event to test with
    test_event = events_before[0]
    test_id = test_event.id
    
    print(f"🎯 Testing deletion of event ID: {test_id}")
    
    # Use the EXISTING delete_calendar_event_real method
    success = api.delete_calendar_event_real(test_id)
    
    if success:
        print("✅ Deletion method returned success")
        
        # Check if it actually worked
        events_after = api.get_jeremy_mayo_events()
        print(f"📅 Events after deletion: {len(events_after)}")
        
        if len(events_after) < len(events_before):
            print("🎉 SUCCESS! Event actually deleted!")
            print(f"   Reduced from {len(events_before)} to {len(events_after)} events")
            
            # Now we can proceed to delete the 7 Monday 9am events
            print("\n🚀 READY TO DELETE MONDAY 9AM EVENTS!")
            return True
        else:
            print("❌ Event count unchanged - deletion was fake")
            return False
    else:
        print("❌ Deletion method returned failure")
        return False

if __name__ == "__main__":
    test_real_deletion()
