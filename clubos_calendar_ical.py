#!/usr/bin/env python3
"""
ClubOS Calendar iCal Integration

This module attempts to extract real calendar data from ClubOS using the iCal sync endpoint
that was discovered in the calendar page HTML.
"""

import requests
import re
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ClubOSiCalExtractor:
    """Extract real calendar events from ClubOS iCal sync endpoint"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        # The calendar sync URL discovered in the HTML output
        self.ical_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
        
    def get_ical_calendar_data(self) -> Optional[str]:
        """
        Get the full iCal calendar data from ClubOS sync endpoint
        """
        try:
            print("🔄 Fetching iCal calendar data from ClubOS sync endpoint...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/calendar,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache'
            }
            
            response = self.session.get(self.ical_sync_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                ical_data = response.text
                print(f"✅ Successfully retrieved iCal data: {len(ical_data)} characters")
                
                # Save for debugging
                with open('clubos_ical_calendar.ics', 'w', encoding='utf-8') as f:
                    f.write(ical_data)
                print("💾 Saved iCal data to 'clubos_ical_calendar.ics'")
                
                return ical_data
            else:
                print(f"❌ Failed to fetch iCal data: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching iCal data: {e}")
            return None
    
    def parse_ical_events(self, ical_data: str) -> List[Dict]:
        """
        Parse iCal format to extract individual events with real times and details
        """
        try:
            events = []
            
            # Split into event blocks
            event_blocks = re.findall(r'BEGIN:VEVENT.*?END:VEVENT', ical_data, re.DOTALL)
            
            print(f"🎯 Found {len(event_blocks)} events in iCal data")
            
            for event_block in event_blocks:
                event = self.parse_single_ical_event(event_block)
                if event:
                    events.append(event)
            
            return events
            
        except Exception as e:
            print(f"❌ Error parsing iCal events: {e}")
            return []
    
    def parse_single_ical_event(self, event_block: str) -> Optional[Dict]:
        """
        Parse a single iCal event block to extract event details
        """
        try:
            event = {}
            
            # Parse each line in the event block
            for line in event_block.split('\n'):
                line = line.strip()
                if ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                
                if key == 'UID':
                    # Extract event ID from UID if possible
                    uid_match = re.search(r'(\d+)', value)
                    if uid_match:
                        event['id'] = int(uid_match.group(1))
                    event['uid'] = value
                    
                elif key == 'SUMMARY':
                    event['title'] = value.strip()
                    
                elif key == 'DESCRIPTION':
                    event['description'] = value.strip()
                    
                elif key == 'DTSTART':
                    event['start_time'] = self.parse_ical_datetime(value)
                    event['start_time_raw'] = value
                    
                elif key == 'DTEND':
                    event['end_time'] = self.parse_ical_datetime(value)
                    event['end_time_raw'] = value
                    
                elif key == 'LOCATION':
                    event['location'] = value.strip()
                    
                elif key.startswith('DTSTART;'):
                    # Handle timezone-specific dates
                    event['start_time'] = self.parse_ical_datetime(value)
                    event['start_time_raw'] = value
                    
                elif key.startswith('DTEND;'):
                    # Handle timezone-specific dates  
                    event['end_time'] = self.parse_ical_datetime(value)
                    event['end_time_raw'] = value
            
            # Only return events that have meaningful data
            if event.get('title') or event.get('start_time'):
                return event
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error parsing single iCal event: {e}")
            return None
    
    def parse_ical_datetime(self, datetime_str: str) -> Optional[str]:
        """
        Parse iCal datetime format to readable format
        Examples:
        - 20250729T143000Z -> "July 29, 2025 2:30 PM"
        - 20250729T143000 -> "July 29, 2025 2:30 PM"
        """
        try:
            # Remove timezone indicator
            clean_dt = datetime_str.replace('Z', '').replace('T', '')
            
            # Parse different formats
            if len(clean_dt) >= 14:  # YYYYMMDDHHMMSS
                dt = datetime.strptime(clean_dt[:14], '%Y%m%d%H%M%S')
                return dt.strftime('%B %d, %Y at %I:%M %p')
            elif len(clean_dt) >= 8:  # YYYYMMDD
                dt = datetime.strptime(clean_dt[:8], '%Y%m%d')
                return dt.strftime('%B %d, %Y')
            else:
                return datetime_str
                
        except Exception as e:
            print(f"❌ Error parsing datetime {datetime_str}: {e}")
            return datetime_str
    
    def find_event_by_id(self, event_id: int, ical_data: str) -> Optional[Dict]:
        """
        Find a specific event by ID in the iCal data
        """
        try:
            events = self.parse_ical_events(ical_data)
            
            for event in events:
                if event.get('id') == event_id:
                    return event
                    
            return None
            
        except Exception as e:
            print(f"❌ Error finding event {event_id}: {e}")
            return None
    
    def extract_real_calendar_events(self, target_event_ids: List[int] = None) -> List[Dict]:
        """
        Main method to extract real calendar events with actual times and details
        """
        try:
            print("\n🌟 === EXTRACTING REAL CALENDAR DATA FROM ICAL SYNC ===")
            
            # Get iCal data
            ical_data = self.get_ical_calendar_data()
            if not ical_data:
                print("❌ Failed to get iCal data")
                return []
            
            # Parse events
            events = self.parse_ical_events(ical_data)
            
            if target_event_ids:
                # Filter to only target events
                target_events = []
                for event_id in target_event_ids:
                    found_event = self.find_event_by_id(event_id, ical_data)
                    if found_event:
                        target_events.append(found_event)
                        print(f"✅ Found target event {event_id}: {found_event.get('title', 'No title')} at {found_event.get('start_time', 'No time')}")
                    else:
                        print(f"❌ Target event {event_id} not found in iCal data")
                
                events = target_events
            
            print(f"\n📊 SUMMARY: Extracted {len(events)} real events from iCal sync")
            for i, event in enumerate(events[:5]):  # Show first 5
                print(f"   Event {i+1}: {event.get('title', 'No title')} - {event.get('start_time', 'No time')}")
            
            print("🌟 ========================================\n")
            
            return events
            
        except Exception as e:
            print(f"❌ Error extracting calendar events: {e}")
            return []

def test_ical_extraction():
    """Test the iCal extraction functionality"""
    import sys
    import os
    
    # Add the parent directory to sys.path to import clubos_real_calendar_api
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from clubos_real_calendar_api import ClubOSRealCalendarAPI
        
        # Create API instance and authenticate with Jeremy's credentials
        api = ClubOSRealCalendarAPI("j.mayo", "Jeremy2024!")
        if api.authenticate():
            print("✅ ClubOS authentication successful")
            
            # Create iCal extractor with authenticated session
            ical_extractor = ClubOSiCalExtractor(api.session)
            
            # Test with a few known event IDs
            test_event_ids = [152241619, 152383381, 150636019]
            
            # Extract real calendar events
            events = ical_extractor.extract_real_calendar_events(test_event_ids)
            
            if events:
                print(f"\n🎉 SUCCESS: Found {len(events)} real events with actual times!")
                for event in events:
                    print(f"📅 {event.get('title', 'Unknown')} - {event.get('start_time', 'No time')}")
            else:
                print("❌ No events found in iCal data")
        else:
            print("❌ ClubOS authentication failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ical_extraction()
