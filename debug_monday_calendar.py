#!/usr/bin/env python3
"""
Debug Monday calendar to see what events exist and their actual times
"""

from clubos_real_calendar_api import ClubOSRealCalendarAPI
import logging
from datetime import datetime

def debug_monday_calendar():
    """Debug what's actually on Monday's calendar"""
    
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("🔍 Debugging Monday Calendar")
        print("=" * 40)
        
        # Monday July 28, 2025
        monday_date = datetime(2025, 7, 28)
        print(f"Looking at Monday: {monday_date.strftime('%Y-%m-%d')}")
        
        # Execute delegate step first
        api.execute_delegate_step()
        
        headers = api.standard_headers.copy()
        headers.update({
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Referer': f'{api.base_url}/action/Calendar'
        })
        
        # Get ALL events for Monday (no time filter)
        params = {
            'startDate': monday_date.strftime('%Y-%m-%d'),
            'endDate': monday_date.strftime('%Y-%m-%d'),
            'trainerId': api.logged_in_user_id,
            'fields': 'id,title,startTime,endTime,serviceType,trainer,location,attendees,fundingStatus',
            '_': str(int(datetime.now().timestamp() * 1000))
        }
        
        print(f"\n📡 API Request:")
        print(f"   URL: {api.base_url}/api/calendar/events")
        print(f"   Params: {params}")
        
        response = api.session.get(
            f"{api.base_url}/api/calendar/events",
            headers=headers,
            params=params
        )
        
        print(f"\n📥 Response:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Data keys: {list(data.keys())}")
            
            if 'events' in data:
                events = data['events']
                print(f"\n📅 Found {len(events)} events on Monday:")
                
                for i, event in enumerate(events):
                    start_time = event.get('startTime', 'No start time')
                    title = event.get('title', 'No title')
                    event_id = event.get('id', 'No ID')
                    
                    print(f"   {i+1}. ID: {event_id}")
                    print(f"      Title: {title}")
                    print(f"      Start: {start_time}")
                    print(f"      Raw event data: {event}")
                    print()
                    
                # Look for 9am events specifically
                nine_am_events = []
                for event in events:
                    start_time = str(event.get('startTime', ''))
                    if '09:' in start_time or '9:' in start_time or '09' in start_time:
                        nine_am_events.append(event)
                
                print(f"🕘 Events that might be 9am: {len(nine_am_events)}")
                for event in nine_am_events:
                    print(f"   - ID {event.get('id')}: {event.get('startTime')}")
                    
            else:
                print("   No 'events' key in response")
                print(f"   Full response: {data}")
        else:
            print(f"   Error: {response.text}")

if __name__ == "__main__":
    debug_monday_calendar()
