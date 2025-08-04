#!/usr/bin/env python3
"""
Simple test of the new deletion method
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("🗑️  TESTING NEW DELETION METHOD")
print("=" * 40)

# Initialize API
api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")

# Authenticate
print("1. Authenticating...")
if api.authenticate():
    print("✅ Authentication successful!")
    
    # Test with event 152375110 (NOT_FUNDED, 1 attendee)
    test_event_id = 152375110
    print(f"\n2. Testing deletion with event {test_event_id}")
    
    # Get current count
    before_events = api.get_jeremy_mayo_events()
    print(f"   Events before: {len(before_events)}")
    
    # Try to delete
    print(f"   Attempting to delete event {test_event_id}...")
    success = api.remove_event_popup(test_event_id)
    print(f"   Deletion method returned: {success}")
    
    # Check after
    after_events = api.get_jeremy_mayo_events()
    print(f"   Events after: {len(after_events)}")
    
    # Verify deletion
    still_exists = any(e.id == test_event_id for e in after_events)
    if not still_exists:
        print("✅ SUCCESS: Event actually deleted from calendar!")
    else:
        print("❌ FAILED: Event still exists on calendar")
        
else:
    print("❌ Authentication failed")
