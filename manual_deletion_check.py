#!/usr/bin/env python3
"""
Manual deletion approach - check the ClubOS web interface for actual deletion
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

def manual_check():
    """Manual check of what we're dealing with"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("📅 CURRENT CALENDAR STATE:")
        print("=" * 50)
        
        events = api.get_jeremy_mayo_events()
        print(f"Total events found: {len(events)}")
        
        # Get detailed info for all events to see what we're really dealing with
        detailed_events = api.get_detailed_event_info([e.id for e in events])
        
        training_events = []
        for event in detailed_events:
            title = getattr(event, 'title', 'No Title')
            if 'Training' in str(title):
                training_events.append(event)
        
        print(f"Training Session events found: {len(training_events)}")
        print()
        
        print("🎯 TRAINING EVENTS TO DELETE:")
        print("-" * 30)
        for i, event in enumerate(training_events):
            print(f"{i+1:2d}. ID: {event.id} | Title: {event.title}")
        
        print()
        print("💡 NEXT STEPS:")
        print("1. Open ClubOS calendar in browser")
        print("2. Manually delete ONE event while monitoring network traffic")
        print("3. Find the REAL deletion request that actually works")
        print("4. Copy that exact request pattern")
        print()
        print("The current deletion method returns 'OK' but is FAKE!")

if __name__ == "__main__":
    manual_check()
