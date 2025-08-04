#!/usr/bin/env python3
"""
Find tomorrow's 8am session for deletion
"""

import json
import logging
from datetime import datetime, timedelta
from clubos_real_calendar_api import ClubOSRealCalendarAPI

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_8am_session():
    """Find tomorrow's 8am session"""
    api = ClubOSRealCalendarAPI("j.mayo", "j@SD4fjhANK5WNA")
    
    logger.info("🔐 Authenticating...")
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return None
    
    logger.info("📅 Fetching all events...")
    events = api.get_jeremy_mayo_events()
    
    if not events:
        logger.error("❌ No events found")
        return None
    
    logger.info(f"📅 Found {len(events)} total events")
    
    # Tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    logger.info(f"🔍 Looking for events on {tomorrow_str} at 8am...")
    
    # Look for 8am events
    potential_8am_events = []
    
    for event in events:
        # Get detailed event data to check start time
        logger.info(f"📋 Checking event {event.id}...")
        
        try:
            # Make direct API call to get event details with start time
            response = api.session.get(
                f"{api.base_url}/action/Calendar/calendarEvent/{event.id}",
                headers={
                    'Authorization': f'Bearer {api.get_bearer_token()}',
                    'Content-Type': 'application/json'
                },
                params={
                    'fields': 'id,title,startTime,endTime,serviceType,trainer,location,attendees,fundingStatus'
                }
            )
            
            if response.status_code == 200:
                event_details = response.json()
                start_time = event_details.get('startTime', '')
                
                logger.info(f"   Event {event.id}: {start_time}")
                
                # Check if this is an 8am session on tomorrow
                if start_time and ('08:00' in str(start_time) or '8:00' in str(start_time)):
                    if tomorrow_str in str(start_time) or tomorrow.strftime('%m/%d') in str(start_time):
                        potential_8am_events.append({
                            'event': event,
                            'start_time': start_time,
                            'details': event_details
                        })
                        logger.info(f"🎯 FOUND 8AM SESSION: Event {event.id} at {start_time}")
            
        except Exception as e:
            logger.warning(f"   ⚠️  Could not get details for event {event.id}: {e}")
            continue
    
    if potential_8am_events:
        logger.info(f"\n🎯 FOUND {len(potential_8am_events)} POTENTIAL 8AM SESSIONS:")
        for i, session in enumerate(potential_8am_events, 1):
            logger.info(f"   {i}. Event {session['event'].id}: {session['start_time']}")
            logger.info(f"      Details: {session['event']}")
        
        return potential_8am_events
    else:
        logger.info(f"❌ No 8am sessions found for {tomorrow_str}")
        return None

if __name__ == "__main__":
    sessions = find_8am_session()
    
    if sessions:
        print(f"\n🎯 Found {len(sessions)} potential 8am sessions:")
        for i, session in enumerate(sessions, 1):
            print(f"   {i}. Event ID: {session['event'].id}")
            print(f"      Start Time: {session['start_time']}")
            print(f"      Description: {session['event']}")
        
        print(f"\nTo delete one of these sessions, run:")
        for session in sessions:
            print(f"   python gym_bot_clean.py  # Then choose option 4 and enter: {session['event'].id}")
    else:
        print("❌ No 8am sessions found for tomorrow")
