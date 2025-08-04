#!/usr/bin/env python3
"""
Check what date range actually has events to find the Monday 9am duplicates
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging
from datetime import datetime, timedelta

def find_events_date_range():
    """Find what date range actually has events"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("🗓️  Finding Events in Date Range")
        print("=" * 40)
        
        api.execute_delegate_step()
        
        headers = api.standard_headers.copy()
        headers.update({
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Referer': f'{api.base_url}/action/Calendar'
        })
        
        # Check different date ranges to find where events actually are
        today = datetime.now()
        date_ranges = [
            (today - timedelta(days=7), today + timedelta(days=7)),   # This week
            (today, today + timedelta(days=30)),                      # Next 30 days
            (today - timedelta(days=30), today),                      # Last 30 days
            (datetime(2025, 1, 1), datetime(2025, 12, 31))           # All of 2025
        ]
        
        for start_date, end_date in date_ranges:
            print(f"\n📅 Checking: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
            params = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'trainerId': api.logged_in_user_id,
                'fields': 'id,title,startTime,endTime',
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = api.session.get(
                f"{api.base_url}/api/calendar/events",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"   Found {len(events)} events")
                
                if events:
                    print("   First 5 events:")
                    for i, event in enumerate(events[:5]):
                        start_time = event.get('startTime', 'No time')
                        title = event.get('title', 'No title')
                        print(f"     {i+1}. {title} - {start_time}")
                    
                    # Look for Monday events specifically
                    monday_events = []
                    for event in events:
                        start_time = str(event.get('startTime', ''))
                        # Check if it's a Monday (assuming date format includes day info)
                        if 'monday' in start_time.lower() or 'mon' in start_time.lower():
                            monday_events.append(event)
                    
                    if monday_events:
                        print(f"   🎯 Found {len(monday_events)} Monday events!")
                        for event in monday_events[:3]:
                            print(f"      - {event.get('title')} at {event.get('startTime')}")
                        break
            else:
                print(f"   Error: {response.status_code}")
        
        # Also check the hardcoded event IDs we know about
        print(f"\n🔍 Checking known event IDs from HAR files:")
        events = api.get_jeremy_mayo_events()
        print(f"Found {len(events)} events from HAR file IDs")
        
        if events:
            # Get detailed info to see start times
            detailed_events = api.get_detailed_event_info([e.id for e in events[:10]])
            for event in detailed_events:
                start_time = getattr(event, 'start_time', 'No time')
                title = getattr(event, 'title', 'No title')
                print(f"   {title} - {start_time}")

if __name__ == "__main__":
    find_events_date_range()
