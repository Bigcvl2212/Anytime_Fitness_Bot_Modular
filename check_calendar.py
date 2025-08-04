#!/usr/bin/env python3
"""
Check current calendar status and find Monday morning events to delete
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_calendar():
    """Check what events are currently on the calendar"""
    
    print("📅 CHECKING CURRENT CALENDAR STATUS")
    print("=" * 50)
    
    # Initialize API
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    # Authenticate
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Get all events
        events = api.get_jeremy_mayo_events()
        print(f"📅 Found {len(events)} total events on calendar")
        
        print(f"\nCurrent events (showing all {len(events)}):")
        for i, event in enumerate(events):
            print(f"{i+1:2d}. ID: {event.id} | Title: {event.title} | Status: {event.funding_status} | Attendees: {len(event.attendees)}")
        
        # Look for potential Monday morning duplicates
        print(f"\n🔍 Looking for potential Monday morning duplicates...")
        potential_duplicates = []
        
        for i, event in enumerate(events):
            # Look for events that might be the Monday morning ones
            # They likely have similar characteristics
            if (event.funding_status in ['NOT_FUNDED', 'FUNDED'] and 
                len(event.attendees) <= 3 and 
                i >= len(events) - 10):  # Focus on recent events
                potential_duplicates.append(event)
                print(f"   🎯 Potential duplicate: ID {event.id} - {event.funding_status} - {len(event.attendees)} attendees")
        
        if potential_duplicates:
            print(f"\n❓ Found {len(potential_duplicates)} potential Monday morning events")
            print("Do you want me to delete these? (The script can be modified to delete them)")
        else:
            print("\n✅ No obvious duplicates found")
            
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    check_calendar()
