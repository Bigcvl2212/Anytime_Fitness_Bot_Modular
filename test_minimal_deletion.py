#!/usr/bin/env python3
"""
Test minimal deletion approach - sometimes simple is better than complex
"""
import sys
import os
import time
from clubos_real_calendar_api import ClubOSRealCalendarAPI

def test_minimal_deletion():
    """Test if minimal deletion actually works vs complex form replication"""
    api = ClubOSRealCalendarAPI(username="mayoj5", password="L@ndon99!")
    
    print("🔐 Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("📅 Getting calendar events...")
    events = api.get_calendar_events()
    
    if not events:
        print("❌ No events found")
        return False
    
    print(f"✅ Found {len(events)} events total")
    
    # Find ANY event to test deletion with
    test_event = None
    for event in events:
        if event.get('id'):
            test_event = event
            break
    
    if not test_event:
        print("❌ No events with ID found for testing")
        return False
    
    test_id = test_event['id']
    print(f"🎯 Testing minimal deletion on event {test_id}")
    print(f"   Event: {test_event.get('title', 'N/A')} at {test_event.get('start_time', 'N/A')}")
    
    # Count events before deletion
    events_before = len(events)
    print(f"📊 Events before deletion: {events_before}")
    
    # Attempt deletion with minimal approach
    print("🗑️  Attempting minimal deletion...")
    success = api.remove_event_popup(test_id)
    
    if success:
        print("✅ Deletion returned success")
        
        # Wait a moment for backend to process
        time.sleep(2)
        
        # Get events again to see if it actually worked
        print("🔍 Checking if event was actually deleted...")
        events_after = api.get_calendar_events()
        
        if events_after is None:
            print("❌ Failed to get events after deletion")
            return False
            
        events_after_count = len(events_after)
        print(f"📊 Events after deletion: {events_after_count}")
        
        if events_after_count < events_before:
            print("🎉 SUCCESS! Event was actually deleted!")
            print(f"   Reduced from {events_before} to {events_after_count} events")
            return True
        else:
            print("💀 FAKE DELETION CONFIRMED - event count unchanged")
            print("   The API returned success but didn't actually delete anything")
            return False
    else:
        print("❌ Deletion returned failure")
        return False

if __name__ == "__main__":
    print("=== TESTING MINIMAL DELETION APPROACH ===")
    print("Goal: See if simple form data works better than complex replication")
    print()
    
    success = test_minimal_deletion()
    
    print()
    if success:
        print("✅ MINIMAL DELETION WORKS!")
    else:
        print("❌ Even minimal deletion is fake")
        print("🔍 Need to find the REAL deletion endpoint or method")
