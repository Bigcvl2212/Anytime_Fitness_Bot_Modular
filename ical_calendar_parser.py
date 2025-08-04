"""
iCal Calendar Parser for ClubOS Real Event Data
This module parses the ClubOS calendar sync iCal feed to extract real event times, 
participant names, and event details that the API doesn't provide.
"""

import requests
from datetime import datetime
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class RealCalendarEvent:
    uid: str
    start_time: datetime
    end_time: datetime
    summary: str
    attendees: List[Dict[str, str]]  # [{'name': 'John Doe', 'email': 'john@example.com'}]
    description: str = ""

class iCalClubOSParser:
    def __init__(self, calendar_sync_url: str):
        """
        Initialize with the ClubOS calendar sync URL
        Example: https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9
        """
        self.calendar_sync_url = calendar_sync_url
        
    def fetch_calendar_data(self) -> str:
        """Fetch the raw iCal data from ClubOS"""
        try:
            response = requests.get(self.calendar_sync_url, timeout=30)
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ Failed to fetch calendar: HTTP {response.status_code}")
                return ""
        except Exception as e:
            print(f"❌ Error fetching calendar: {e}")
            return ""
    
    def parse_ical_events(self, ical_content: str) -> List[RealCalendarEvent]:
        """Parse iCal content and extract event details"""
        events = []
        
        # Split content into individual events
        event_blocks = re.findall(r'BEGIN:VEVENT.*?END:VEVENT', ical_content, re.DOTALL)
        
        for block in event_blocks:
            try:
                event = self._parse_single_event(block)
                if event:
                    events.append(event)
            except Exception as e:
                print(f"⚠️ Error parsing event block: {e}")
                continue
        
        print(f"✅ Parsed {len(events)} real calendar events from iCal")
        return events
    
    def _parse_single_event(self, event_block: str) -> Optional[RealCalendarEvent]:
        """Parse a single VEVENT block"""
        lines = event_block.strip().split('\n')
        
        uid = None
        start_time = None
        end_time = None
        summary = ""
        description = ""
        attendees = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('UID:'):
                uid = line.split(':', 1)[1].strip()
                
            elif line.startswith('DTSTART:'):
                start_str = line.split(':', 1)[1].strip()
                start_time = self._parse_datetime(start_str)
                
            elif line.startswith('DTEND:'):
                end_str = line.split(':', 1)[1].strip()
                end_time = self._parse_datetime(end_str)
                
            elif line.startswith('SUMMARY:'):
                summary = line.split(':', 1)[1].strip()
                
            elif line.startswith('DESCRIPTION:'):
                description = line.split(':', 1)[1].strip()
                
            elif line.startswith('ATTENDEE;'):
                attendee = self._parse_attendee(line)
                if attendee:
                    attendees.append(attendee)
        
        if uid and start_time and end_time:
            return RealCalendarEvent(
                uid=uid,
                start_time=start_time,
                end_time=end_time,
                summary=summary,
                attendees=attendees,
                description=description
            )
        
        return None
    
    def _parse_datetime(self, dt_str: str) -> Optional[datetime]:
        """Parse iCal datetime format"""
        try:
            # Remove timezone info for now, focus on the datetime
            dt_str = dt_str.split('T')[0] + 'T' + dt_str.split('T')[1][:6]
            return datetime.strptime(dt_str, '%Y%m%dT%H%M%S')
        except Exception as e:
            print(f"⚠️ Error parsing datetime '{dt_str}': {e}")
            return None
    
    def _parse_attendee(self, attendee_line: str) -> Optional[Dict[str, str]]:
        """Parse ATTENDEE line to extract name and email"""
        try:
            # Example: ATTENDEE;ROLE=OPT-PARTICIPANT;CN=John Doe:mailto:john@example.com
            
            # Extract name from CN= parameter
            name_match = re.search(r'CN=([^:;]+)', attendee_line)
            name = name_match.group(1) if name_match else ""
            
            # Extract email from mailto:
            email_match = re.search(r'mailto:([^\s]+)', attendee_line)
            email = email_match.group(1) if email_match else ""
            
            if name or email:
                return {'name': name.strip(), 'email': email.strip()}
                
        except Exception as e:
            print(f"⚠️ Error parsing attendee '{attendee_line}': {e}")
            
        return None
    
    def get_real_events(self) -> List[RealCalendarEvent]:
        """Main method to fetch and parse all real calendar events"""
        print("🌐 Fetching real calendar data from ClubOS iCal sync...")
        
        ical_content = self.fetch_calendar_data()
        if not ical_content:
            return []
        
        print(f"📄 Downloaded {len(ical_content)} characters of iCal data")
        
        events = self.parse_ical_events(ical_content)
        
        # Print sample events for debugging
        for i, event in enumerate(events[:3]):
            print(f"📅 Event {i+1}: {event.summary}")
            print(f"   Time: {event.start_time} - {event.end_time}")
            print(f"   Attendees: {[a['name'] for a in event.attendees]}")
            print(f"   UID: {event.uid}")
        
        return events

def test_ical_parser():
    """Test function to verify the iCal parser works"""
    calendar_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
    parser = iCalClubOSParser(calendar_url)
    events = parser.get_real_events()
    
    print(f"\n🎯 SUMMARY: Found {len(events)} real events with actual times and names!")
    return events

if __name__ == "__main__":
    test_ical_parser()
