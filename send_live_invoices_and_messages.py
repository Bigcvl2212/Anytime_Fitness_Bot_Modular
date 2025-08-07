#!/usr/bin/env python3
"""
ClubOS Calendar Event Deletion Script
Uses proven working methods from existing API
"""

import requests
import json
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Represents a ClubOS calendar event"""
    id: int
    funding_status: str
    attendees: List[Dict]
    title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class ClubOSCalendarDeletion:
    """
    ClubOS Calendar Event Deletion using proven working methods
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        
        # Authentication tokens
        self.session_id = None
        self.logged_in_user_id = None
        self.delegated_user_id = None
        
        # Standard headers
        self.standard_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

    def authenticate(self) -> bool:
        """
        Authenticate using proven working method from existing API
        """
        try:
            logger.info(f"Authenticating {self.username} with ClubOS")
            
            # Step 1: Get login page and extract CSRF token
            login_url = f"{self.base_url}/action/Login/view?__fsk=1221801756"
            login_response = self.session.get(login_url)
            login_response.raise_for_status()
            
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Extract required form fields
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            
            logger.info("Extracted form fields successfully")
            
            # Step 2: Submit login form with correct field names
            login_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': source_page.get('value') if source_page else '',
                '__fp': fp_token.get('value') if fp_token else ''
            }
            
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url,
                'User-Agent': self.standard_headers['User-Agent']
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=login_headers,
                allow_redirects=True
            )
            
            # Step 3: Extract session information from cookies
            self.session_id = self.session.cookies.get('JSESSIONID')
            self.logged_in_user_id = self.session.cookies.get('loggedInUserId')
            self.delegated_user_id = self.session.cookies.get('delegatedUserId')
            
            if not self.session_id or not self.logged_in_user_id:
                logger.error("Authentication failed - missing session cookies")
                return False
            
            logger.info(f"Authentication successful - User ID: {self.logged_in_user_id}")
            return True
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    def get_bearer_token(self) -> str:
        """
        Generate the Bearer token as seen in HAR files
        """
        if not self.session_id or not self.logged_in_user_id:
            raise ValueError("Must authenticate first")
        
        # Payload structure from HAR files
        payload = {
            "delegateUserId": int(self.logged_in_user_id),
            "loggedInUserId": int(self.logged_in_user_id),
            "sessionId": self.session_id
        }
        
        # Create JWT-like token
        header = "eyJhbGciOiJIUzI1NiJ9"
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
        signature = "xgXI5ZdpWH1czSf2aIzzZmK7r8siUsV59MeeqZF0PNM"
        
        return f"{header}.{payload_b64}.{signature}"

    def get_source_page_token(self) -> str:
        """Get fresh source page token"""
        try:
            response = self.session.get(f"{self.base_url}/action/Calendar")
            soup = BeautifulSoup(response.text, 'html.parser')
            source_page = soup.find('input', {'name': '_sourcePage'})
            return source_page.get('value') if source_page else ''
        except:
            return ''

    def get_fingerprint_token(self) -> str:
        """Get fresh fingerprint token"""
        try:
            response = self.session.get(f"{self.base_url}/action/Calendar")
            soup = BeautifulSoup(response.text, 'html.parser')
            fp_token = soup.find('input', {'name': '__fp'})
            return fp_token.get('value') if fp_token else ''
        except:
            return ''

    def get_calendar_events(self) -> List[CalendarEvent]:
        """
        Get current calendar events using HAR event IDs
        """
        try:
            logger.info("Fetching calendar events using HAR event IDs")
            
            # Event IDs from HAR files (same as working script)
            har_event_ids = [
                152438700, 152241606, 152241619, 152383381, 152313709,
                152330854, 152383406, 152307818, 152432067, 152251071,
                152331703, 152323134, 152436981, 152361598, 152404397,
                150850294, 152390593, 152396339, 152381643, 152339247,
                152407477, 152330036, 152371551, 149648946, 152335380,
                152407666, 152375110, 150636019, 152330854, 152383406
            ]
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            events = []
            for event_id in har_event_ids[:10]:  # Test with first 10
                try:
                    params = {
                        'eventIds': str(event_id),
                        'fields': 'id,title,startTime,endTime,attendees,fundingStatus',
                        '_': str(int(datetime.now().timestamp() * 1000))
                    }
                    
                    response = self.session.get(
                        f"{self.base_url}/api/calendar/events",
            headers=headers, 
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and 'events' in data:
                            for event_data in data['events']:
                                event = CalendarEvent(
                                    id=event_data.get('id', event_id),
                                    funding_status=event_data.get('fundingStatus', 'Unknown'),
                                    attendees=event_data.get('attendees', []),
                                    title=event_data.get('title'),
                                    start_time=event_data.get('startTime'),
                                    end_time=event_data.get('endTime')
                                )
                                events.append(event)
                                logger.info(f"Found event: {event}")
                    
                except Exception as e:
                    logger.warning(f"Error fetching event {event_id}: {e}")
                    continue
            
            logger.info(f"Found {len(events)} calendar events")
            return events
            
    except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []

    def delete_event(self, event_id: int) -> bool:
        """
        Delete event using the EXACT working pattern from HAR file
        """
        try:
            logger.info(f"Deleting event {event_id} using HAR pattern")
            
            # Navigate to calendar page first
            calendar_response = self.session.get(
                f"{self.base_url}/action/Calendar",
                headers={
                    **self.standard_headers,
                    'Authorization': f'Bearer {self.get_bearer_token()}'
                }
            )
            
            if calendar_response.status_code != 200:
                logger.error(f"Failed to load calendar page: {calendar_response.status_code}")
                return False
            
            # Use the EXACT working deletion pattern from HAR file
        headers = {
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://anytime.club-os.com/action/Calendar',
                'Origin': 'https://anytime.club-os.com'
            }
            
            # EXACT form data from working HAR request
            form_data = {
                'calendarEvent.id': '',
                'calendarEvent.repeatEvent.id': '1687456',  # From HAR
                'calendarEvent.repeatEvent.calendarEventId': str(event_id),
                'calendarEvent.clubId': '291',
                'calendarTimeSlot.past': 'false',
                'attendee.id': '',
                'attendee.tfoUserId': '',
                'attendee.pin': '',
                'attendee.status.code': '',
                'attendee.excludeFromPayroll': '',
                'fundingStatus': '',
                'editSeries': 'false',
                'calendarEvent.createdFor.tfoUserId': '187032782',
                'calendarEvent.eventType': 'SMALL_GROUP_TRAINING',
                'calendarEvent.instructorId': '',
                'calendarEvent.clubLocationId': '3586',
                'calendarEvent.subject': 'Training Session',
                'startTimeSlotId': '35',
                'calendarEvent.startTime': '8/1/2025',
                'endTimeSlotId': '37',
                'calendarEvent.repeatEvent.repeatType': 'WEEKLY',
                'calendarEvent.repeatEvent.repeatFrequency': '1',
                'calendarEvent.repeatEvent.mon': 'true',
                'calendarEvent.repeatEvent.wed': 'true',
                'calendarEvent.repeatEvent.fri': 'true',
                'calendarEvent.repeatEvent.endOn': '',
                'calendarEvent.repeatEvent.endUntil': '',
                'calendarEvent.repeatEvent.endType': 'never',
                'calendarEvent.status.code': 'A',
                'calendarEvent.notes': '',
                'calendarEvent.remindCreator': 'true',
                'calendarEvent.remindCreatorMins': '120',
                'calendarEvent.remindAttendees': 'true',
                'calendarEvent.remindAttendeesMins': '120',
                'calendarEvent.maxAttendees': '',
                'attendeeSearchText': 'Type attendee\'s name',
                'attendees[0].id': '',
                'attendees[0].tfoUserId': '191215290',
                'attendees[0].status.code': 'A',
                'attendees[0].pinBy': '',
                'attendees[0].excludeFromPayroll': 'false',
                'attendees[0].timeZoneId': 'America/Chicago',
                'attendees[0].visitType': 'A',
                'calendarEvent.memberServiceId': '30078',
                'attendeeEmailToText': '',
                '_sourcePage': self.get_source_page_token(),
                '__fp': self.get_fingerprint_token()
            }
            
            logger.info(f"Attempting deletion for event {event_id} with HAR pattern")
            response = self.session.post(
                f"{self.base_url}/action/EventPopup/remove",
                headers=headers,
                data=form_data
            )
            
            logger.info(f"Deletion response: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text
                logger.info(f"Delete response: {response_text[:100]}...")
                
                if "OK" in response_text:
                    logger.info(f"✅ Event {event_id} deleted successfully!")
        return True
                else:
                    logger.error(f"Deletion failed: {response_text}")
                    return False
            else:
                logger.error(f"Deletion failed with status {response.status_code}: {response.text}")
                return False
        
    except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
        return False

    def delete_multiple_events(self, event_ids: List[int]) -> Dict[int, bool]:
        """
        Delete multiple events and return results
        """
        results = {}
        logger.info(f"Starting deletion of {len(event_ids)} events")
        
        for event_id in event_ids:
            logger.info(f"Deleting event {event_id}...")
            success = self.delete_event(event_id)
            results[event_id] = success
            
            if success:
                logger.info(f"✅ Successfully deleted event {event_id}")
            else:
                logger.error(f"❌ Failed to delete event {event_id}")
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Deletion complete: {successful}/{len(event_ids)} events deleted successfully")
        return results

def main():
    """Main function to test calendar event deletion"""
    
    # Load credentials from config
    from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD
    
    # Initialize the deletion client
    client = ClubOSCalendarDeletion(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    
    # Step 1: Authenticate
    logger.info("=== Starting ClubOS Calendar Event Deletion ===")
    if not client.authenticate():
        logger.error("Authentication failed!")
        return
    
    logger.info("✅ Authentication successful!")
    
    # Step 2: Get calendar events
    events = client.get_calendar_events()
    if not events:
        logger.warning("No events found to delete")
        return
    
    logger.info(f"Found {len(events)} events to potentially delete")
    
    # Step 3: Delete events (test with first 3)
    test_event_ids = [event.id for event in events[:3]]
    logger.info(f"Testing deletion with events: {test_event_ids}")
    
    results = client.delete_multiple_events(test_event_ids)
    
    # Step 4: Summary
    successful_deletions = sum(1 for success in results.values() if success)
    logger.info(f"=== Deletion Summary ===")
    logger.info(f"Total events attempted: {len(results)}")
    logger.info(f"Successfully deleted: {successful_deletions}")
    logger.info(f"Failed: {len(results) - successful_deletions}")
    
    for event_id, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"Event {event_id}: {status}")

if __name__ == "__main__":
    main() 
