#!/usr/bin/env python3
"""
Use our calendar functions to find and delete Monday's group training events
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
from datetime import datetime, timedelta
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def delete_monday_events():
    """Use calendar functions to find and delete Monday events"""
    
    print("🗑️ FINDING AND DELETING MONDAY EVENTS")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Get Monday's date (7/28/25)
        monday_date = datetime(2025, 7, 28)
        print(f"\n📅 Looking for events on Monday {monday_date.strftime('%m/%d/%Y')}")
        
        # Get current calendar events using our date range method
        events = api.get_current_calendar_events(limit=100)
        print(f"Found {len(events)} events in date range")
        
        if len(events) == 0:
            # Try the HAR method instead
            print("No events found with date range, trying HAR method...")
            events = api.get_jeremy_mayo_events()
            print(f"Found {len(events)} events with HAR method")
        
        # Look for Monday events (or recent events that could be Monday)
        monday_candidates = []
        
        for event in events:
            # Check if event has Monday time characteristics
            # Since we created them today for Monday 9am, they're likely recent
            if (event.funding_status in ['NOT_FUNDED', 'FUNDED'] and 
                len(event.attendees) <= 3):
                monday_candidates.append(event)
        
        print(f"\n🎯 Found {len(monday_candidates)} potential Monday events:")
        
        for i, event in enumerate(monday_candidates[-10:]):  # Show last 10 candidates
            print(f"{i+1:2d}. ID: {event.id} | Status: {event.funding_status} | Attendees: {len(event.attendees)}")
        
        # Delete the most recent ones (likely our duplicates)
        print(f"\n🗑️ Deleting the last 4 events (the Monday duplicates)...")
        deleted_count = 0
        
        for event in monday_candidates[-4:]:  # Delete last 4
            print(f"\nDeleting event ID: {event.id}")
            
            if api.remove_event_popup(event.id):
                print(f"✅ Event {event.id} deleted successfully!")
                deleted_count += 1
            else:
                print(f"❌ Failed to delete event {event.id}")
        
        print(f"\n🎯 DELETION SUMMARY: {deleted_count}/4 Monday events deleted")
        
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    delete_monday_events()
