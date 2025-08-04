#!/usr/bin/env python3
"""
Force delete the specific Monday morning events
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def force_delete_monday_events():
    """Force delete the specific Monday morning duplicate events"""
    
    print("🗑️ FORCE DELETING MONDAY MORNING DUPLICATES")
    print("=" * 50)
    
    # These are the specific event IDs that need to be deleted
    target_event_ids = [152334766, 152383406, 152339247, 152307818]
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    if api.authenticate():
        print("✅ Authentication successful!")
        
        deleted_count = 0
        
        for event_id in target_event_ids:
            print(f"\n🎯 Force deleting event ID: {event_id}")
            
            try:
                # Try both delete methods
                if api.remove_event_popup(event_id):
                    print(f"✅ Event {event_id} deleted via remove_event_popup!")
                    deleted_count += 1
                elif api.delete_event_clubos_way(event_id):
                    print(f"✅ Event {event_id} deleted via delete_event_clubos_way!")
                    deleted_count += 1
                else:
                    print(f"❌ Failed to delete event {event_id}")
                    
            except Exception as e:
                print(f"❌ Error deleting event {event_id}: {e}")
        
        print(f"\n🎯 FORCE DELETE SUMMARY: {deleted_count}/{len(target_event_ids)} events deleted")
        
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    force_delete_monday_events()
