#!/usr/bin/env python3
"""
Find the 7 Monday 9am duplicate events by checking their actual start times
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

def find_monday_9am_duplicates():
    """Find the actual Monday 9am duplicate events by start time"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("📅 Finding Monday 9am Duplicate Events")
        print("=" * 50)
        
        events = api.get_jeremy_mayo_events()
        print(f"Total events found: {len(events)}")
        
        # Get detailed info for all events to see their actual start times
        detailed_events = api.get_detailed_event_info([e.id for e in events])
        
        print("\n🕒 ALL EVENTS WITH START TIMES:")
        print("-" * 60)
        
        monday_9am_duplicates = []
        
        for i, event in enumerate(detailed_events):
            title = getattr(event, 'title', 'No Title')
            start_time = getattr(event, 'start_time', 'No Time')
            
            print(f"{i+1:2d}. ID: {event.id} | {title} | Start: {start_time}")
            
            # Look for Monday 9am events specifically
            # Check if start_time contains Monday and 9:00 AM or similar
            if start_time and isinstance(start_time, str):
                start_lower = start_time.lower()
                # Look for patterns like "monday" and "9" and "am"
                if ('monday' in start_lower or 'mon' in start_lower) and '9' in start_time and ('am' in start_lower or '09:00' in start_time):
                    monday_9am_duplicates.append(event)
                    print(f"     🎯 MONDAY 9AM DUPLICATE!")
        
        print(f"\n🎯 Found {len(monday_9am_duplicates)} Monday 9am duplicates")
        
        if monday_9am_duplicates:
            print("\n📋 MONDAY 9AM EVENTS TO DELETE:")
            print("-" * 40)
            for i, event in enumerate(monday_9am_duplicates):
                print(f"{i+1}. ID: {event.id} | Start: {getattr(event, 'start_time', 'Unknown')}")
                
            print(f"\nReady to delete {len(monday_9am_duplicates)} Monday 9am duplicates")
            return monday_9am_duplicates
        else:
            print("❌ No Monday 9am duplicates found by start time")
            print("\n💡 Manual inspection needed - check the start times above")
            print("   and identify which 7 events are the Monday 9am duplicates")
            return []

if __name__ == "__main__":
    duplicates = find_monday_9am_duplicates()
