#!/usr/bin/env python3
"""
Find Monday 9am event and its nested duplicates by navigating the calendar properly
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging
from datetime import datetime, timedelta

def find_monday_9am_nested_events():
    """Find the Monday 9am event and its nested duplicates"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("📅 Finding Monday 9am Event with Nested Duplicates")
        print("=" * 55)
        
        # Calculate Monday's date (tomorrow is July 28, 2025)
        monday_date = datetime(2025, 7, 28)  # Tomorrow is Monday
        print(f"Looking for events on Monday: {monday_date.strftime('%m/%d/%Y')}")
        
        # Try to get calendar events for a specific date range
        print("\n🔍 Searching calendar for Monday events...")
        
        # Method 1: Try to get calendar events filtered by date
        try:
            # Navigate to calendar page first to establish session
            calendar_response = api.session.get(
                f"{api.base_url}/action/Calendar",
                headers={
                    **api.standard_headers,
                    'Authorization': f'Bearer {api.get_bearer_token()}'
                }
            )
            
            if calendar_response.status_code == 200:
                print("✅ Calendar page loaded")
                
                # Try to get events for specific date
                date_str = "07/28/2025"  # Monday format
                
                # Try different calendar API endpoints to get events by date
                for endpoint in [
                    f"/action/Calendar/getEvents?date={date_str}",
                    f"/action/Calendar/events?startDate={date_str}&endDate={date_str}",
                    f"/calendar/events/{date_str}",
                    f"/action/Calendar/dayView?date={date_str}"
                ]:
                    try:
                        response = api.session.get(
                            f"{api.base_url}{endpoint}",
                            headers={
                                'Authorization': f'Bearer {api.get_bearer_token()}',
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        )
                        
                        if response.status_code == 200 and len(response.text) > 10:
                            print(f"✅ Found data at: {endpoint}")
                            print(f"Response length: {len(response.text)} characters")
                            
                            # Look for 9am events in the response
                            if '9:00' in response.text or '09:00' in response.text or '9 AM' in response.text:
                                print(f"🎯 Found 9am events in response!")
                                
                                # Save the response to examine
                                with open(f'monday_calendar_{endpoint.replace("/", "_").replace("?", "_")}.html', 'w') as f:
                                    f.write(response.text)
                                print(f"Saved calendar data for inspection")
                        else:
                            print(f"❌ No data at: {endpoint}")
                            
                    except Exception as e:
                        print(f"❌ Error trying {endpoint}: {e}")
            
        except Exception as e:
            print(f"❌ Error loading calendar: {e}")
        
        # Method 2: Look through existing events for Monday patterns
        print("\n📋 Checking existing events for Monday 9am patterns...")
        events = api.get_jeremy_mayo_events()
        
        # Look for events that might be grouped/nested
        # Often nested events have similar IDs or are returned in sequence
        consecutive_training_events = []
        
        print(f"All {len(events)} event IDs:")
        for i, event in enumerate(events):
            print(f"  {i+1:2d}. {event.id}")
            
            # Look for patterns in consecutive IDs that might indicate nested events
            if i > 0:
                prev_id = events[i-1].id
                current_id = event.id
                id_diff = abs(current_id - prev_id)
                
                # If IDs are very close together, they might be nested/duplicated events
                if id_diff < 100:  # Arbitrary threshold for "close" IDs
                    if len(consecutive_training_events) == 0:
                        consecutive_training_events.append(events[i-1])
                    consecutive_training_events.append(event)
        
        if consecutive_training_events:
            print(f"\n🎯 Found {len(consecutive_training_events)} events with consecutive IDs:")
            print("These might be the nested duplicates!")
            
            for i, event in enumerate(consecutive_training_events):
                print(f"  {i+1}. ID: {event.id}")
                
            if len(consecutive_training_events) >= 6:
                print(f"\n💡 Found {len(consecutive_training_events)} consecutive events - these could be the Monday 9am duplicates!")
                return consecutive_training_events[:6]  # Return first 6 as the duplicates
        
        print("\n❌ Could not identify Monday 9am nested events automatically")
        print("💡 Manual inspection needed:")
        print("   1. Open ClubOS calendar in browser")
        print("   2. Navigate to Monday July 28, 2025")
        print("   3. Look at 9:00 AM time slot")
        print("   4. Check if there are multiple overlapping events")
        print("   5. Note the event IDs of the duplicates")
        
        return []

if __name__ == "__main__":
    nested_events = find_monday_9am_nested_events()
    if nested_events:
        print(f"\n🎯 Ready to delete {len(nested_events)} nested duplicates!")
    else:
        print("\n❌ Need manual identification of nested events")
