#!/usr/bin/env python3
"""
Simple script to identify and delete the 7 Monday 9am duplicate events
Based on the working patterns already established
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    print("🎯 IDENTIFYING MONDAY 9AM EVENTS FOR DELETION")
    print("=" * 50)
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Get the 29 events we know exist
    events = api.get_jeremy_mayo_events()
    print(f"📅 Found {len(events)} total events")
    
    print("\n📋 ALL EVENTS WITH IDs:")
    print("Please identify which 7 are Monday 9am duplicates:")
    
    for i, event in enumerate(events, 1):
        print(f"   {i:2d}. Event ID: {event.id}")
    
    print("\n🎯 BASED ON YOUR PREVIOUS FEEDBACK:")
    print("You mentioned 7 duplicate Monday 9am events need to be deleted.")
    print("Since we can't auto-identify them by time, please tell me:")
    print("- Which specific event IDs are the Monday 9am duplicates?")
    
    # Based on conversation history, the most recent events are likely duplicates
    # Let's show the first 7 events as candidates
    candidate_events = events[:7]
    print(f"\n💡 CANDIDATES (first 7 events - likely most recent):")
    for i, event in enumerate(candidate_events, 1):
        print(f"   {i}. Event ID: {event.id}")
    
    print(f"\n⚠️  DELETION STATUS:")
    print("- Current deletion methods are FAKE (return 'OK' but don't delete)")
    print("- Need your working browser capture deletion data")
    print("- All event retrieval and authentication is working perfectly")
    
    return events

if __name__ == "__main__":
    main()
