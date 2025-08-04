#!/usr/bin/env python3
"""
Test the new ClubOS calendar        # Test 5: Actually delete the Monday 9am events
        print(f"\n5. DELETING MONDAY 9AM EVENTS:")
        print("   🎯 Using existing delete_monday_9am_events script...")
        
        # Import and run the existing deletion script
        import subprocess
        result = subprocess.run(["python", "delete_monday_9am_events.py"], 
                              capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("   ✅ Monday 9am deletion script completed!")
            print("   📝 Output:")
            for line in result.stdout.split('\n')[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"      {line}")
        else:
            print("   ❌ Deletion script failed")
            print(f"   Error: {result.stderr}")
        
        print("\n✅ All tests completed!")ement methods
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_clubos_methods():
    """Test the new ClubOS event management methods"""
    
    print("🧪 Testing ClubOS Calendar Event Management")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Test 1: Authentication
    print("\n1. Testing Authentication...")
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Test 2: Open event popup
        print("\n2. Testing Event Popup...")
        if api.open_event_popup():
            print("✅ Event popup opened successfully!")
        else:
            print("❌ Failed to open event popup")
        
        # Test 3: Attendee search
        print("\n3. Testing Attendee Search...")
        attendees = api.search_attendees("test")
        print(f"📋 Found {len(attendees)} potential attendees")
        
        # Test 4: Get all events and let user identify Monday 9am duplicates  
        print("\n4. Finding Events to Delete...")
        events = api.get_jeremy_mayo_events()
        print(f"📅 Found {len(events)} total events")
        
        # Since we can't identify Monday 9am events by time, show all events
        # and let user specify which ones to delete
        print("\n📋 All Events (you need to identify which 7 are Monday 9am duplicates):")
        for i, event in enumerate(events):
            print(f"   {i+1:2d}. ID {event.id}: {getattr(event, 'title', 'Unknown')}")
        
        # For now, just identify that we found events but can't auto-detect Monday 9am
        print(f"\n⚠️  Found {len(events)} events but CANNOT identify Monday 9am duplicates automatically")
        print("   ➤ The date-based API returns 0 events")  
        print("   ➤ Event start times are all 'None'")
        print("   ➤ Need manual identification of which 7 events are Monday 9am duplicates")
        
        # Don't attempt deletion since we can't identify the right events
        monday_9am_events = []
        
        # Test 5: Show deletion status
        print(f"\n5. Deletion Status:")
        print("   ❌ Current deletion method is BROKEN")
        print("   ➤ Returns 'OK' but doesn't actually delete events") 
        print("   ➤ Need real deletion endpoint from browser capture")
        print("\n� Next Steps:")
        print("   1. Manually delete ONE event in ClubOS browser")
        print("   2. Capture the network request") 
        print("   3. Implement the REAL deletion method")
        print("   4. Then delete the 7 Monday 9am duplicates")
        
        print("\n✅ All basic tests completed!")
        
    else:
        print("❌ Authentication failed - cannot test other methods")

if __name__ == "__main__":
    test_clubos_methods()
