#!/usr/bin/env python3
"""
Test REAL event deletion with proper ClubOS form data
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_real_deletion():
    """Test the corrected deletion method"""
    
    print("🧪 Testing REAL ClubOS Event Deletion")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Test 1: Authentication
    print("\n1. Testing Authentication...")
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Test 2: Get current events to see what we have
        print("\n2. Getting current events...")
        events = api.get_jeremy_mayo_events()
        print(f"📅 Found {len(events)} total events")
        
        # Show recent events (potential test targets)
        print("\n   Recent events (showing first 10):")
        test_candidates = []
        for i, event in enumerate(events[:10]):
            print(f"     {i+1}. ID {event.id}: {event.title} - {len(event.attendees)} attendees")
            if event.title and ('Group Training' in event.title or 'Session' in event.title):
                test_candidates.append(event)
                print(f"        ⭐ Potential test candidate")
        
        if test_candidates:
            print(f"\n🎯 Found {len(test_candidates)} test candidates")
            target_event = test_candidates[0]
            print(f"   Testing deletion of: ID {target_event.id} - {target_event.title}")
            
            # Test 3: Try the new deletion method
            print(f"\n3. Testing deletion of event {target_event.id}...")
            if api.remove_event_popup(target_event.id):
                print("✅ Event deletion returned success!")
                
                # Test 4: Verify it's actually gone
                print("\n4. Verifying deletion...")
                updated_events = api.get_jeremy_mayo_events()
                print(f"📅 Now have {len(updated_events)} events (was {len(events)})")
                
                # Check if the specific event is gone
                found_deleted_event = False
                for event in updated_events:
                    if event.id == target_event.id:
                        found_deleted_event = True
                        break
                
                if found_deleted_event:
                    print("❌ Event still exists - deletion failed")
                else:
                    print("✅ Event successfully deleted from calendar!")
                    
            else:
                print("❌ Deletion returned failure")
        else:
            print("❌ No test candidate events found")
            print("   Try creating a test event first")
            
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    test_real_deletion()
