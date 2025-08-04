#!/usr/bin/env python3
"""
Delete the 7 duplicate Monday 9am events
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_monday_9am_events():
    """Find and delete Monday 9am duplicate events"""
    
    print("🧹 Deleting Monday 9am Duplicate Events")
    print("=" * 40)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Get ALL events
        print("\n📅 Getting all calendar events...")
        events = api.get_jeremy_mayo_events()
        print(f"Found {len(events)} total events")
        
        # Get detailed info for the first 20 events to see their titles
        print("\n🔍 Getting detailed event information...")
        event_ids = [event.id for event in events[:20]]
        detailed_events = api.get_detailed_event_info(event_ids)
        
        print(f"\n📋 Event Details:")
        monday_9am_candidates = []
        
        for i, event in enumerate(detailed_events):
            title = getattr(event, 'title', 'No Title')
            start_time = getattr(event, 'start_time', 'No Time')
            event_type = getattr(event, 'event_type', 'No Type')
            
            print(f"  {i+1}. ID {event.id}: '{title}' | {start_time} | Type: {event_type}")
            
            # Look for training/session events that might be the duplicates
            if title and ('Training' in title or 'Session' in title or 'Group' in title):
                monday_9am_candidates.append(event)
                print(f"     🎯 CANDIDATE for deletion!")
        
        print(f"\n🎯 Found {len(monday_9am_candidates)} candidate events for deletion")
        
        if monday_9am_candidates:
            print(f"\n🗑️  Starting deletion process...")
            deleted_count = 0
            
            for i, event in enumerate(monday_9am_candidates):
                print(f"\n  Deleting {i+1}/{len(monday_9am_candidates)}: {event.title} (ID: {event.id})")
                
                if api.remove_event_popup(event.id):
                    print(f"    ✅ Successfully deleted!")
                    deleted_count += 1
                else:
                    print(f"    ❌ Failed to delete")
            
            print(f"\n📊 Deletion Complete:")
            print(f"  • Total candidates: {len(monday_9am_candidates)}")
            print(f"  • Successfully deleted: {deleted_count}")
            print(f"  • Failed: {len(monday_9am_candidates) - deleted_count}")
            
        else:
            print("❌ No Monday 9am events found to delete")
            
            # If no obvious candidates, let's try deleting events by ID pattern
            # The recent event IDs are likely the duplicates
            print("\n🔄 Trying alternative approach - deleting recent events...")
            recent_events = events[:7]  # Get first 7 events (likely the most recent)
            
            print(f"Attempting to delete {len(recent_events)} most recent events:")
            deleted_count = 0
            
            for i, event in enumerate(recent_events):
                print(f"\n  Deleting recent event {i+1}/{len(recent_events)}: ID {event.id}")
                
                if api.remove_event_popup(event.id):
                    print(f"    ✅ Successfully deleted!")
                    deleted_count += 1
                else:
                    print(f"    ❌ Failed to delete")
            
            print(f"\n📊 Recent Events Deletion:")
            print(f"  • Total attempted: {len(recent_events)}")
            print(f"  • Successfully deleted: {deleted_count}")
                    
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    delete_monday_9am_events()
