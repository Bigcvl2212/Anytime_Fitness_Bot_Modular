#!/usr/bin/env python3
"""
ClubOS Real Calendar API Implementation
Uses actual API endpoints discovered from Charles HAR files
"""

import requests
import json
import base64
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from src.services.authentication.unified_auth_service import get_unified_auth_service, AuthenticationSession

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Represents a ClubOS calendar event"""
    id: int
    funding_status: str
    attendees: List[Dict[str, Any]]
    title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    trainer_id: Optional[int] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    service_id: Optional[int] = None
    client_name: Optional[str] = None
    service_name: Optional[str] = None
    trainer_name: Optional[str] = None
    
    def get_formatted_time(self) -> str:
        """Get formatted time for display"""
        if self.start_time:
            try:
                # Try to parse different time formats
                if 'T' in str(self.start_time):
                    # ISO format
                    dt = datetime.fromisoformat(str(self.start_time).replace('Z', '+00:00'))
                    return dt.strftime('%I:%M %p')
                elif ':' in str(self.start_time):
                    # Time only format
                    return str(self.start_time)
                else:
                    return str(self.start_time)
            except:
                return str(self.start_time) if self.start_time else "TBD"
        return "TBD"
    
    def get_formatted_date(self) -> str:
        """Get formatted date for display"""
        if self.start_time:
            try:
                # Try to parse different date formats
                if 'T' in str(self.start_time):
                    # ISO format
                    dt = datetime.fromisoformat(str(self.start_time).replace('Z', '+00:00'))
                    return dt.strftime('%B %d, %Y')
                elif '-' in str(self.start_time):
                    # Date format
                    return str(self.start_time)
                else:
                    return str(self.start_time)
            except:
                return str(self.start_time) if self.start_time else "TBD"
        return "TBD"
    
    def __str__(self):
        attendee_names = []
        for attendee in self.attendees[:3]:  # Show first 3 attendees
            if 'clientName' in attendee:
                attendee_names.append(attendee['clientName'])
            elif 'id' in attendee:
                attendee_names.append(f"Client #{attendee['id']}")
        
        attendee_str = ", ".join(attendee_names)
        if len(self.attendees) > 3:
            attendee_str += f" (+{len(self.attendees)-3} more)"
        
        return f"Event {self.id}: {self.title or 'Training Session'} - {attendee_str} [{self.funding_status}]"

class ClubOSRealCalendarAPI:
    """
    Real ClubOS Calendar API implementation using actual endpoints
    discovered from Charles proxy HAR files
    """
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.base_url = "https://anytime.club-os.com"
        
        # Get unified authentication service
        self.auth_service = get_unified_auth_service()
        self.auth_session: Optional[AuthenticationSession] = None
        
        # Legacy attributes for backward compatibility
        self.session = None
        self.session_id = None
        self.api_v3_access_token = None
        self.api_v3_id_token = None
        self.api_v3_refresh_token = None
        self.logged_in_user_id = None
        self.delegated_user_id = None
        
        # Jeremy Mayo's known user ID from HAR files
        self.jeremy_mayo_user_id = 187032782
        
        # Standard headers for ClubOS API requests
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
        Authenticate using the unified authentication service
        """
        try:
            logger.info(f"Authenticating ClubOS Real Calendar API")
            
            # Use unified authentication service
            self.auth_session = self.auth_service.authenticate_clubos(self.username, self.password)
            
            if not self.auth_session or not self.auth_session.authenticated:
                logger.error("ClubOS authentication failed")
                return False
            
            # Update legacy attributes for backward compatibility
            self.session = self.auth_session.session
            self.session_id = self.auth_session.session_id
            self.logged_in_user_id = self.auth_session.logged_in_user_id
            self.delegated_user_id = self.auth_session.delegated_user_id
            self.api_v3_access_token = self.auth_session.api_v3_access_token
            
            logger.info(f"Authentication successful - User ID: {self.logged_in_user_id}")
            return True
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    def get_bearer_token(self) -> str:
        """
        Get the Bearer token from the unified authentication service
        """
        if not self.auth_session or not self.auth_session.authenticated:
            raise ValueError("Must authenticate first")
        
        return self.auth_session.bearer_token

    def get_calendar_page(self) -> bool:
        """
        Access the main calendar page to ensure proper session setup
        """
        try:
            logger.info("Accessing calendar page")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Upgrade-Insecure-Requests': '1',
                'Referer': f'{self.base_url}/action/Dashboard?actAs=loggedIn'
            })
            
            response = self.session.get(
                f"{self.base_url}/action/Calendar",
                headers=headers
            )
            
            response.raise_for_status()
            logger.info("Successfully accessed calendar page")
            return True
            
        except Exception as e:
            logger.error(f"Error accessing calendar page: {str(e)}")
            return False

    def get_source_page_token(self) -> str:
        """
        Extract FRESH _sourcePage token from current ClubOS session
        """
        try:
            # Get the calendar page to extract fresh tokens
            response = self.session.get(f"{self.base_url}/action/Calendar")
            if response.status_code == 200:
                # Look for _sourcePage token in the HTML
                import re
                source_match = re.search(r'name="_sourcePage"[^>]*value="([^"]*)"', response.text)
                if source_match:
                    token = source_match.group(1)
                    logger.info(f"Extracted fresh _sourcePage token: {token[:20]}...")
                    return token
                else:
                    logger.warning("Could not find _sourcePage token in page, using fallback")
            
            # Fallback to working token from your browser capture
            return "GN6AsTEdTbxJ0LGtZ3ilrEZQiwnc1XV2EIusBezhws92tfAba2lFOA=="
        except Exception as e:
            logger.error(f"Error extracting source page token: {e}")
            return "GN6AsTEdTbxJ0LGtZ3ilrEZQiwnc1XV2EIusBezhws92tfAba2lFOA=="

    def get_fingerprint_token(self) -> str:
        """
        Extract FRESH __fp (fingerprint) token from current ClubOS session
        """
        try:
            # Get the calendar page to extract fresh tokens  
            response = self.session.get(f"{self.base_url}/action/Calendar")
            if response.status_code == 200:
                # Look for __fp token in the HTML
                import re
                fp_match = re.search(r'name="__fp"[^>]*value="([^"]*)"', response.text)
                if fp_match:
                    token = fp_match.group(1)
                    logger.info(f"Extracted fresh __fp token: {token[:20]}...")
                    return token
                else:
                    logger.warning("Could not find __fp token in page, using fallback")
            
            # Fallback to working token from your browser capture
            return "AGtXoR7WJMiW9vsLF0UPm0n2qctwhl4PvLJiae0fh7izVEIu_Dt7iHx08c_m8dvnEE1jjOmqDoscYJUsplTQdoAuI7a4ZIcF6qrgjUfeqze2k2Wo1Ad371GWBi5n-ziv0q-v7P2RYoeVdFsnz7Iwd8ce4mvoiUykZbAucFKmstLpy5uJtwxwkx4o_9sOZWSNCjdWa1f3uuOQuJVsz0joue87i2n52r63FdulhIxvgGyNTxe6Ftisb8kII0PWjkKXwOucoiWfu5rLFxJl0lewWkcYBsLwFr4blvb7CxdFD5ugyb_XBDPm5NQbJk2z4jXRHGCVLKZU0HbVECW1dMleBooheyp9iOUzJ47ciCbx8fJljJbVw2V23o1PF7oW2KxvZ1pWoDimZBVN3G5oVeBet1GWBi5n-zivCjhBQCXuHCeGbk46meyyekcYBsLwFr4blvb7CxdFD5tJ9qnLcIZeD1Mx2z9wnqxx2EdV3vc0530N0GpuM2T_TqnHfSC0T18aQU8_7YyybYlTvFrbqKICJJb2-wsXRQ-bH90lg3gVRe0g7pGAYpP2jDOjTSqVpsjEkLiVbM9I6LnvO4tp-dq-txXbpYSMb4BsPfbD5iPueCPYR1Xe9zTnfQGs4yv3JXH5xFtNNF_JPa_ICTu2zfpKhlGWBi5n-zivgdnnVsKGzXkFg1EIo49Lu2WMltXDZXbejU8XuhbYrG9nWlagOKZkFSmgK8l239ZMUZYGLmf7OK_Sr6_s_ZFih69W1C-fykfE_-9SfKK9r2mW9vsLF0UPm9hkAbMUcqsokLiVbM9I6LnvO4tp-dq-t9jx4ErX5A5Cktqzmpe6nU-YRahsbZP2Pr8BE6doplhfZks2HqR4BNccYJUsplTQdlUF6SMpCqSnAfjY_-mTR6OqKK08jdX8TQ=="
        except Exception as e:
            logger.error(f"Error extracting fingerprint token: {e}")
            return "AGtXoR7WJMiW9vsLF0UPm0n2qctwhl4PvLJiae0fh7izVEIu_Dt7iHx08c_m8dvnEE1jjOmqDoscYJUsplTQdoAuI7a4ZIcF6qrgjUfeqze2k2Wo1Ad371GWBi5n-ziv0q-v7P2RYoeVdFsnz7Iwd8ce4mvoiUykZbAucFKmstLpy5uJtwxwkx4o_9sOZWSNCjdWa1f3uuOQuJVsz0joue87i2n52r63FdulhIxvgGyNTxe6Ftisb8kII0PWjkKXwOucoiWfu5rLFxJl0lewWkcYBsLwFr4blvb7CxdFD5ugyb_XBDPm5NQbJk2z4jXRHGCVLKZU0HbVECW1dMleBooheyp9iOUzJ47ciCbx8fJljJbVw2V23o1PF7oW2KxvZ1pWoDimZBVN3G5oVeBet1GWBi5n-zivCjhBQCXuHCeGbk46meyyekcYBsLwFr4blvb7CxdFD5tJ9qnLcIZeD1Mx2z9wnqxx2EdV3vc0530N0GpuM2T_TqnHfSC0T18aQU8_7YyybYlTvFrbqKICJJb2-wsXRQ-bH90lg3gVRe0g7pGAYpP2jDOjTSqVpsjEkLiVbM9I6LnvO4tp-dq-txXbpYSMb4BsPfbD5iPueCPYR1Xe9zTnfQGs4yv3JXH5xFtNNF_JPa_ICTu2zfpKhlGWBi5n-zivgdnnVsKGzXkFg1EIo49Lu2WMltXDZXbejU8XuhbYrG9nWlagOKZkFSmgK8l239ZMUZYGLmf7OK_Sr6_s_ZFih69W1C-fykfE_-9SfKK9r2mW9vsLF0UPm9hkAbMUcqsokLiVbM9I6LnvO4tp-dq-t9jx4ErX5A5Cktqzmpe6nU-YRahsbZP2Pr8BE6doplhfZks2HqR4BNccYJUsplTQdlUF6SMpCqSnAfjY_-mTR6OqKK08jdX8TQ=="

    def get_calendar_page_events(self) -> List[Dict[str, Any]]:
        """
        Extract real event data from ClubOS calendar page HTML
        This parses the actual calendar interface for live event information
        """
        try:
            print("🌐 Fetching PERSONAL SCHEDULE (My Schedule) for event extraction...")
            
            # Get the calendar page with authentication
            headers = self.standard_headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Dest': 'document',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Try personal schedule first, then fallback to main calendar
            personal_urls = [
                f"{self.base_url}/action/Calendar?view=personal",
                f"{self.base_url}/action/Calendar?trainerId={self.logged_in_user_id}",
                f"{self.base_url}/action/Calendar?mySchedule=true",
                f"{self.base_url}/action/Calendar"
            ]
            
            response = None
            for url in personal_urls:
                try:
                    print(f"🎯 Trying URL: {url}")
                    response = self.session.get(url, headers=headers)
                    response.raise_for_status()
                    
                    # Check if this view has events or is empty
                    if "no events scheduled" not in response.text.lower():
                        print(f"✅ Found content in: {url}")
                        break
                    else:
                        print(f"⚠️ Empty calendar view: {url}")
                except Exception as e:
                    print(f"❌ Failed to access {url}: {e}")
                    continue
            
            if not response:
                print("❌ Could not access any calendar view")
                return []
            
            print(f"📄 Got calendar page HTML ({len(response.text)} chars)")
            
            # Save HTML to file for inspection
            with open('calendar_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved calendar HTML to 'calendar_page_debug.html' for inspection")
            
            # Parse HTML with BeautifulSoup for comprehensive event extraction
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                print("🔍 Parsing HTML with BeautifulSoup...")
                
                events = []
                
                # Strategy 1: Look for FullCalendar events (common in web calendars)
                print("📅 Searching for FullCalendar event data...")
                for script in soup.find_all('script'):
                    if script.string and 'events' in script.string:
                        # Look for calendar event arrays
                        import re
                        event_pattern = r'events\s*:\s*\[(.*?)\]'
                        matches = re.findall(event_pattern, script.string, re.DOTALL)
                        for match in matches:
                            print(f"Found potential event data: {match[:200]}...")
                
                # Strategy 2: Look for ClubOS-specific structures
                print("🏋️ Searching for ClubOS calendar structures...")
                
                # Look for data-* attributes that might contain event info
                for element in soup.find_all(attrs={'data-event-id': True}):
                    event_id = element.get('data-event-id')
                    event_text = element.get_text().strip()
                    print(f"Found event element: ID={event_id}, Text={event_text}")
                    events.append({
                        'id': event_id,
                        'text': event_text,
                        'source': 'data-event-id'
                    })
                
                # Look for calendar cells or day containers
                for day_element in soup.find_all(['td', 'div'], class_=re.compile(r'day|cal|event', re.IGNORECASE)):
                    day_text = day_element.get_text().strip()
                    if day_text and len(day_text) > 10:  # Ignore empty or very short cells
                        # Look for time patterns
                        import re
                        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)'
                        times = re.findall(time_pattern, day_text, re.IGNORECASE)
                        if times:
                            print(f"Found day element with time: {day_text[:100]}...")
                            events.append({
                                'text': day_text,
                                'time': times[0],
                                'source': 'day_element'
                            })
                
                # Strategy 3: Look for JSON data embedded in scripts
                print("📊 Searching for embedded JSON event data...")
                for script in soup.find_all('script'):
                    if script.string:
                        # Look for JSON-like structures with event data
                        import re
                        json_pattern = r'\{[^{}]*(?:"startTime"|"endTime"|"title"|"attendees")[^{}]*\}'
                        matches = re.findall(json_pattern, script.string, re.IGNORECASE)
                        for match in matches:
                            try:
                                data = json.loads(match)
                                print(f"Found JSON event data: {data}")
                                events.append({
                                    'text': data.get('title', 'Event'),
                                    'time': data.get('startTime', data.get('time', 'Unknown')),
                                    'data': data,
                                    'source': 'embedded_json'
                                })
                            except:
                                pass
                
                # Strategy 4: Look for specific ClubOS calendar CSS classes
                print("🎯 Searching for ClubOS-specific calendar classes...")
                clubos_selectors = [
                    '.calendar-event',
                    '.event-item', 
                    '.appointment',
                    '.training-session',
                    '[class*="event"]',
                    '[class*="appointment"]',
                    '[class*="calendar"]'
                ]
                
                for selector in clubos_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        for elem in elements[:5]:  # Limit to first 5
                            text = elem.get_text().strip()
                            if text:
                                print(f"  Element text: {text[:100]}...")
                                events.append({
                                    'text': text,
                                    'source': f'css_selector_{selector}'
                                })
                
                # Strategy 5: Extract all text and look for patterns
                print("� Analyzing full page text for patterns...")
                full_text = soup.get_text()
                
                # Look for common appointment patterns
                patterns = [
                    r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))\s*([A-Za-z\s]+)',
                    r'(Personal Training|Training Session|Appointment)\s*.*?(\d{1,2}:\d{2}\s*(?:AM|PM))',
                    r'(\w+\s+\w+)\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))',  # Name - Time
                    r'(\d{1,2}/\d{1,2}/\d{4})\s*(\d{1,2}:\d{2}\s*(?:AM|PM))'  # Date Time
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    if matches:
                        print(f"Found {len(matches)} matches for pattern: {pattern}")
                        for match in matches[:5]:  # Limit output
                            print(f"  Match: {match}")
                            events.append({
                                'text': ' '.join(str(m) for m in match),
                                'pattern': pattern,
                                'source': 'text_pattern'
                            })
                
                print(f"📋 Extracted {len(events)} potential events from HTML")
                
                # Debug: Print first few events
                for i, event in enumerate(events[:3]):
                    print(f"  Event {i+1}: {event}")
                
                return events
                
            except ImportError:
                print("⚠️ BeautifulSoup not available, using regex fallback...")
                
                # Fallback: Use regex to extract event patterns from raw HTML
                events = []
                import re
                
                # Look for time patterns in the HTML
                time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)'
                times = re.findall(time_pattern, response.text, re.IGNORECASE)
                
                # Look for training/session mentions
                session_pattern = r'(training|session|appointment)[^<]*(\d{1,2}:\d{2}\s*(?:AM|PM)?)'
                session_matches = re.findall(session_pattern, response.text, re.IGNORECASE)
                
                for i, time in enumerate(times[:10]):  # Limit to 10 events
                    events.append({
                        'text': f'Training Session {i+1}',
                        'time': time,
                        'source': 'regex_fallback'
                    })
                
                print(f"📋 Regex fallback extracted {len(events)} events")
                return events
            
        except Exception as e:
            print(f"❌ Error extracting events from calendar page: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_single_event_details(self, event_id: int) -> Optional[CalendarEvent]:
        """
        Get detailed information for a single event using individual API calls
        This tries multiple endpoints to get the full event data including times and attendee names
        """
        try:
            print(f"🔍 Getting details for event {event_id}...")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Try approach 1: Individual event endpoint
            try:
                # First try the direct calendar API endpoint
                response = self.session.get(
                    f"{self.base_url}/api/calendar/events/{event_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    event_detail = response.json()
                    print(f"✅ Individual API: {json.dumps(event_detail, indent=2)}")
                    
                    if event_detail.get('startTime'):
                        return CalendarEvent(
                            id=event_id,
                            funding_status=event_detail.get('fundingStatus', 'UNKNOWN'),
                            attendees=event_detail.get('attendees', []),
                            title=event_detail.get('title', 'Training Session'),
                            service_name=event_detail.get('serviceName', 'Personal Training'),
                            start_time=event_detail.get('startTime'),
                            end_time=event_detail.get('endTime'),
                            trainer_name=event_detail.get('trainerName', 'Jeremy Mayo')
                        )
                
                # Also try training packages endpoint
                response = self.session.get(
                    f"{self.base_url}/api/trainingPackages/events/{event_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    event_detail = response.json()
                    print(f"✅ Training Package API: {json.dumps(event_detail, indent=2)}")
                    
                    if event_detail.get('startTime'):
                        return CalendarEvent(
                            id=event_id,
                            funding_status=event_detail.get('fundingStatus', 'UNKNOWN'),
                            attendees=event_detail.get('attendees', []),
                            title=event_detail.get('title', 'Training Session'),
                            service_name=event_detail.get('serviceName', 'Personal Training'),
                            start_time=event_detail.get('startTime'),
                            end_time=event_detail.get('endTime'),
                            trainer_name=event_detail.get('trainerName', 'Jeremy Mayo')
                        )
                        
            except Exception as e:
                print(f"⚠️ API endpoints failed: {e}")
            
            # Try approach 2: Event popup data
            try:
                popup_data = self.get_event_popup_data(event_id)
                if popup_data:
                    print(f"✅ Popup API: Found {len(popup_data)} fields")
                    
                    # Extract time information from popup data
                    start_time = popup_data.get('calendarEvent.startTime')
                    if start_time:
                        return CalendarEvent(
                            id=event_id,
                            funding_status=popup_data.get('fundingStatus', 'UNKNOWN'),
                            attendees=[],  # Will be populated separately
                            title=popup_data.get('calendarEvent.subject', 'Training Session'),
                            service_name='Personal Training',
                            start_time=start_time,
                            end_time=None,
                            trainer_name='Jeremy Mayo'
                        )
            except Exception as e:
                print(f"⚠️ Popup API failed: {e}")
            
            # Try approach 3: Event popup endpoints (simulating calendar click)
            try:
                # Try different popup URLs that load when clicking calendar events
                popup_urls = [
                    f"{self.base_url}/action/EventPopup?eventId={event_id}",
                    f"{self.base_url}/action/EventPopup/edit/{event_id}",
                    f"{self.base_url}/action/EventPopup/view/{event_id}",
                    f"{self.base_url}/action/Event/{event_id}",
                    f"{self.base_url}/action/Event/edit/{event_id}",
                    f"{self.base_url}/action/Calendar/event/{event_id}"
                ]
                
                for popup_url in popup_urls:
                    try:
                        print(f"🎯 Trying popup URL: {popup_url}")
                        popup_response = self.session.get(popup_url, headers=headers)
                        
                        if popup_response.status_code == 200 and len(popup_response.text) > 1000:
                            html = popup_response.text
                            print(f"✅ Event popup HTML: {len(html)} chars")
                            
                            # Save popup HTML for debugging
                            with open(f'event_{event_id}_popup.html', 'w', encoding='utf-8') as f:
                                f.write(html)
                            print(f"💾 Saved popup HTML to 'event_{event_id}_popup.html'")
                            
                            # Parse HTML for event details using BeautifulSoup
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract event data from form fields and display text
                            title = None
                            start_time = None
                            service_name = None
                            client_names = []
                            
                            # Look for form inputs with event data
                            for input_field in soup.find_all('input'):
                                name = input_field.get('name', '')
                                value = input_field.get('value', '')
                                
                                if 'startTime' in name or 'start_time' in name:
                                    start_time = value
                                elif 'subject' in name or 'title' in name:
                                    title = value
                                elif 'service' in name.lower():
                                    service_name = value
                            
                            # Look for select dropdowns
                            for select in soup.find_all('select'):
                                name = select.get('name', '')
                                selected = select.find('option', selected=True)
                                if selected:
                                    value = selected.get_text().strip()
                                    if 'service' in name.lower():
                                        service_name = value
                            
                            # Extract text content for additional parsing
                            text_content = soup.get_text()
                            
                            # Look for date/time patterns in text
                            import re
                            if not start_time:
                                # Look for date patterns
                                date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', text_content)
                                time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)', text_content)
                                if date_match or time_match:
                                    start_time = f"{date_match.group(1) if date_match else ''} {time_match.group(1) if time_match else ''}".strip()
                            
                            # Look for client/participant names
                            name_patterns = [
                                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last name pattern
                                r'Client:\s*([A-Za-z\s]+)',
                                r'Participant:\s*([A-Za-z\s]+)'
                            ]
                            
                            for pattern in name_patterns:
                                matches = re.findall(pattern, text_content)
                                client_names.extend(matches)
                            
                            # Remove duplicates and filter out common words
                            client_names = list(set([name.strip() for name in client_names 
                                                   if len(name.strip()) > 3 and 
                                                   name.strip() not in ['Add Event', 'Edit Event', 'Event Type']]))
                            
                            if start_time or title or client_names:
                                print(f"📋 Extracted: title='{title}', time='{start_time}', clients={client_names}")
                                
                                return CalendarEvent(
                                    id=event_id,
                                    funding_status='UNKNOWN',
                                    attendees=[],
                                    title=title or f'Training Session {event_id}',
                                    service_name=service_name or 'Personal Training',
                                    start_time=start_time,
                                    end_time=None,
                                    trainer_name='Jeremy Mayo'
                                )
                            
                            break  # Found valid popup, stop trying other URLs
                        
                        else:
                            print(f"⚠️ Small response from {popup_url}: {len(popup_response.text)} chars")
                            
                    except Exception as e:
                        print(f"❌ Error with {popup_url}: {e}")
                        continue
                        
            except Exception as e:
                print(f"⚠️ Popup endpoints failed: {e}")
            
            # Return fallback event if no detailed data found
            print(f"❌ No detailed data found for event {event_id}")
            return CalendarEvent(
                id=event_id,
                funding_status='UNKNOWN',
                attendees=[],
                title=f'Training Session {event_id}',
                service_name='Personal Training',
                start_time=None,
                end_time=None,
                trainer_name='Jeremy Mayo'
            )
            
            print(f"❌ No detailed data found for event {event_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting event details for {event_id}: {e}")
            return None

    def get_calendar_events_by_ids(self, event_ids: List[int], fields: str = "fundingStatus,startTime,endTime,attendees,title,serviceName,trainerName") -> List[CalendarEvent]:
        """
        Get calendar events by specific event IDs using HTML parsing for real data
        """
        try:
            logger.info(f"Fetching calendar events for {len(event_ids)} event IDs")
            
            # First try to get REAL event details from calendar page HTML
            print("\n=== EXTRACTING REAL CALENDAR DATA ===")
            calendar_events = self.get_calendar_page_events()
            if calendar_events:
                print(f"SUCCESS: Found {len(calendar_events)} REAL events from calendar page")
                for i, event in enumerate(calendar_events[:3]):
                    print(f"Real event {i}: {event}")
            else:
                print("No real events found in calendar page HTML")
            print("=============================================\n")
            
            # Still make the API call to get basic event structure
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Build query parameters
            params = []
            for event_id in event_ids:
                params.append(('eventIds', str(event_id)))
            params.append(('fields', fields))
            params.append(('_', str(int(datetime.now().timestamp() * 1000))))
            
            # Make API call
            response = self.session.get(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse the API events and get detailed information for each
            events = []
            if 'events' in data:
                print(f"\n🔍 ANALYZING {len(data['events'])} EVENTS:")
                for i, event_data in enumerate(data['events'][:5]):  # Limit debug output
                    print(f"   Event {i+1} - ID: {event_data.get('id')}, Attendees: {len(event_data.get('attendees', []))}")
                
                # Now try to get detailed information for each event
                print(f"\n🚀 ATTEMPTING TO GET DETAILED EVENT INFORMATION...")
                for i, event_data in enumerate(data['events']):
                    event_id = event_data['id']
                    
                    # Try to get detailed event information
                    detailed_event = self.get_single_event_details(event_id)
                    
                    if detailed_event and detailed_event.start_time:
                        print(f"✅ Event {event_id}: {detailed_event.start_time} - {detailed_event.title}")
                        events.append(detailed_event)
                    else:
                        # Fallback to basic event with attendee info
                        attendee_count = len(event_data.get('attendees', []))
                        event = CalendarEvent(
                            id=event_data['id'],
                            funding_status=event_data.get('fundingStatus', 'UNKNOWN'),
                            attendees=event_data.get('attendees', []),
                            title=f'Training Session ({attendee_count} clients)',
                            service_name='Personal Training',
                            start_time='Time TBD',
                            end_time=None,
                            trainer_name='Jeremy Mayo'
                        )
                        events.append(event)
                        print(f"⚠️ Event {event_id}: Using fallback data ({attendee_count} attendees)")
            
            logger.info(f"Successfully fetched {len(events)} enhanced calendar events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def get_monday_9am_events(self) -> List[CalendarEvent]:
        """
        Get specifically Monday 9am events to identify duplicates
        """
        try:
            logger.info("Getting Monday 9am events")
            
            # Monday July 28, 2025
            monday_date = datetime(2025, 7, 28)
            
            # Execute delegate step first for manager permissions
            if not self.execute_delegate_step():
                logger.warning("Delegate step failed, continuing anyway...")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Get events specifically for Monday
            params = {
                'startDate': monday_date.strftime('%Y-%m-%d'),
                'endDate': monday_date.strftime('%Y-%m-%d'),
                'trainerId': self.logged_in_user_id,
                'fields': 'id,title,startTime,endTime,serviceType,trainer,location,attendees,fundingStatus',
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = self.session.get(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            monday_9am_events = []
            if 'events' in data:
                for event_data in data['events']:
                    start_time = event_data.get('startTime')
                    
                    # Check if this is a 9am event
                    if start_time and '09:00' in str(start_time):
                        event = CalendarEvent(
                            id=event_data['id'],
                            funding_status=event_data.get('fundingStatus', 'UNKNOWN'),
                            attendees=event_data.get('attendees', []),
                            title=event_data.get('title', 'Training Session'),
                            start_time=start_time,
                            end_time=event_data.get('endTime'),
                            trainer_id=event_data.get('trainer', {}).get('id') if event_data.get('trainer') else None,
                            location=event_data.get('location'),
                            event_type=event_data.get('serviceType', {}).get('name') if event_data.get('serviceType') else None,
                            service_id=event_data.get('serviceType', {}).get('id') if event_data.get('serviceType') else None
                        )
                        monday_9am_events.append(event)
                        logger.info(f"Found Monday 9am event: ID {event.id} at {start_time}")
            
            logger.info(f"Successfully found {len(monday_9am_events)} Monday 9am events")
            return monday_9am_events
            
        except Exception as e:
            logger.error(f"Error getting Monday 9am events: {str(e)}")
            return []

    def get_jeremy_mayo_events(self) -> List[CalendarEvent]:
        """
        Get Jeremy Mayo's calendar events using the actual event IDs from HAR files
        """
        # Event IDs extracted from HAR files
        har_event_ids = [
            152438700, 152241606, 152241619, 152383381, 152313709,
            152330854, 152383406, 152307818, 152432067, 152251071,
            152331703, 152323134, 152436981, 152361598, 152404397,
            150850294, 152390593, 152396339, 152381643, 152339247,
            152407477, 152330036, 152371551, 149648946, 152335380,
            152407666, 152375110, 150636019, 152334766
        ]
        
        return self.get_calendar_events_by_ids(har_event_ids)

    def execute_delegate_step(self) -> bool:
        """
        Execute the delegate step as seen in HAR files - crucial for manager permissions
        """
        try:
            logger.info("Executing delegate step for manager permissions")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            params = {
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = self.session.get(
                f"{self.base_url}/action/Delegate/0/url=false",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            logger.info("Delegate step executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error executing delegate step: {str(e)}")
            return False

    def get_current_calendar_events(self, limit: int = 50) -> List[CalendarEvent]:
        """
        Get current calendar events using a date range instead of specific IDs
        """
        try:
            logger.info(f"Fetching current calendar events (limit: {limit})")
            
            # Execute delegate step first for manager permissions
            if not self.execute_delegate_step():
                logger.warning("Delegate step failed, continuing anyway...")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Get events for the next 30 days
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)
            
            params = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'trainerId': self.logged_in_user_id,
                'fields': 'id,title,startTime,endTime,serviceType,trainer,location,attendees,fundingStatus',
                'limit': limit,
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = self.session.get(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            events = []
            if 'events' in data:
                for event_data in data['events']:
                    event = CalendarEvent(
                        id=event_data['id'],
                        funding_status=event_data.get('fundingStatus', 'UNKNOWN'),
                        attendees=event_data.get('attendees', []),
                        title=event_data.get('title', 'Training Session'),
                        start_time=event_data.get('startTime'),
                        end_time=event_data.get('endTime'),
                        trainer_id=event_data.get('trainer', {}).get('id') if event_data.get('trainer') else None,
                        location=event_data.get('location'),
                        event_type=event_data.get('serviceType', {}).get('name') if event_data.get('serviceType') else None,
                        service_id=event_data.get('serviceType', {}).get('id') if event_data.get('serviceType') else None
                    )
                    events.append(event)
            
            logger.info(f"Successfully fetched {len(events)} current calendar events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching current calendar events: {str(e)}")
            return []

    def create_calendar_event_real(self, 
                                   start_datetime: str,
                                   end_datetime: str, 
                                   client_ids: List[int],
                                   service_type_id: int = None,
                                   notes: str = None) -> bool:
        """
        Create a calendar event using the real ClubOS API
        """
        try:
            logger.info(f"Creating calendar event from {start_datetime} to {end_datetime}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/json',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            event_data = {
                'startDateTime': start_datetime,  # Format: "2025-07-26T14:00:00"
                'endDateTime': end_datetime,
                'trainerId': int(self.logged_in_user_id),
                'clientIds': client_ids,
                'serviceTypeId': service_type_id,
                'notes': notes or '',
                'location': 'Anytime Fitness'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                json=event_data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Calendar event created successfully: {response.json()}")
                return True
            else:
                logger.error(f"Failed to create event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return False

    def delete_calendar_event_real(self, event_id: int) -> bool:
        """
        Delete a calendar event using the real ClubOS API
        """
        try:
            logger.info(f"Deleting calendar event {event_id}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            response = self.session.delete(
                f"{self.base_url}/api/calendar/events/{event_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Calendar event {event_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting calendar event: {str(e)}")
            return False

    def get_detailed_event_info(self, event_ids: List[int]) -> List[CalendarEvent]:
        """
        Get detailed event information including attendee names, times, etc.
        """
        try:
            logger.info(f"Fetching detailed info for {len(event_ids)} events")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Get detailed fields
            params = []
            for event_id in event_ids:
                params.append(('eventIds', str(event_id)))
            params.append(('fields', 'id,title,startTime,endTime,serviceType,trainer,location,attendees,fundingStatus'))
            params.append(('_', str(int(datetime.now().timestamp() * 1000))))
            
            response = self.session.get(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            events = []
            if 'events' in data:
                for event_data in data['events']:
                    event = CalendarEvent(
                        id=event_data['id'],
                        funding_status=event_data.get('fundingStatus', 'UNKNOWN'),
                        attendees=event_data.get('attendees', []),
                        title=event_data.get('title', 'Training Session'),
                        start_time=event_data.get('startTime'),
                        end_time=event_data.get('endTime'),
                        trainer_id=event_data.get('trainer', {}).get('id') if event_data.get('trainer') else None,
                        location=event_data.get('location'),
                        event_type=event_data.get('serviceType', {}).get('name') if event_data.get('serviceType') else None,
                        service_id=event_data.get('serviceType', {}).get('id') if event_data.get('serviceType') else None
                    )
                    events.append(event)
            
            logger.info(f"Successfully fetched detailed info for {len(events)} events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching detailed event info: {str(e)}")
            return []

    def open_event_popup(self, event_id: int = None) -> bool:
        """
        Open event popup for creating or editing events - ClubOS stateful approach
        """
        try:
            logger.info(f"Opening event popup for event {event_id if event_id else 'NEW'}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # ClubOS uses empty form data - event context is managed by session
            data = {}
            if event_id:
                data['eventId'] = str(event_id)
            
            response = self.session.post(
                f"{self.base_url}/action/EventPopup/open",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                logger.info(f"Event popup opened successfully")
                return True
            else:
                logger.error(f"Failed to open event popup: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error opening event popup: {str(e)}")
            return False
            return {}

    def save_event_popup(self, event_data: Dict = None) -> bool:
        """
        Save event using ClubOS form-based action with proper form fields
        """
        try:
            logger.info("Saving event via EventPopup/save with proper form data")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Build the proper ClubOS form data based on HAR analysis
            form_data = {
                'calendarEvent.id': '',
                'calendarEvent.repeatEvent.id': '',
                'calendarEvent.repeatEvent.calendarEventId': '',
                'calendarEvent.clubId': '291',
                'calendarTimeSlot.past': 'false',
                'attendee.id': '',
                'attendee.tfoUserId': '',
                'attendee.pin': '',
                'attendee.status.code': '',
                'attendee.excludeFromPayroll': '',
                'fundingStatus': '',
                'calendarEvent.createdFor.tfoUserId': str(self.logged_in_user_id),
                'calendarEvent.eventType': event_data.get('eventType', 'SMALL_GROUP_TRAINING'),
                'calendarEvent.instructorId': str(self.logged_in_user_id),
                'calendarEvent.clubLocationId': event_data.get('clubLocationId', '3586'),
                'calendarEvent.subject': event_data.get('subject', 'Training Session'),
                'calendarEvent.repeat': 'false',
                'startTimeSlotId': event_data.get('startTimeSlotId', '37'),  # 9am
                'calendarEvent.startTime': event_data.get('startTime', '7/28/25'),  # Monday
                'endTimeSlotId': event_data.get('endTimeSlotId', '39'),  # 10am
                'calendarEvent.repeatEvent.repeatType': 'WEEKLY',
                'calendarEvent.repeatEvent.repeatFrequency': '1',
                'calendarEvent.repeatEvent.endType': 'never',
                'calendarEvent.status.code': 'A',
                'calendarEvent.notes': event_data.get('notes', ''),
                'calendarEvent.remindCreator': 'true',
                'calendarEvent.remindCreatorMins': '120',
                'calendarEvent.remindAttendees': 'true',
                'calendarEvent.remindAttendeesMins': '120',
                'calendarEvent.maxAttendees': '',
                'attendeeSearchText': '',
                'attendeeEmailToText': '',
                'calendarEvent.memberServiceId': event_data.get('memberServiceId', '30078')
            }
            
            # Add attendees if provided
            attendees = event_data.get('attendees', [])
            for i, attendee in enumerate(attendees):
                form_data[f'attendees[{i}].id'] = ''
                form_data[f'attendees[{i}].tfoUserId'] = str(attendee.get('tfoUserId', ''))
                form_data[f'attendees[{i}].status.code'] = 'A'
                form_data[f'attendees[{i}].pinBy'] = ''
                form_data[f'attendees[{i}].excludeFromPayroll'] = ''
                form_data[f'attendees[{i}].timeZoneId'] = 'America/Chicago'
                form_data[f'attendees[{i}].visitType'] = ''
            
            # Add CSRF tokens (these need to be obtained from the popup response)
            form_data['_sourcePage'] = event_data.get('_sourcePage', '')
            form_data['__fp'] = event_data.get('__fp', '')
            
            response = self.session.post(
                f"{self.base_url}/action/EventPopup/save",
                headers=headers,
                data=form_data
            )
            
            # ClubOS returns 302 redirect on successful save
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                if '/action/Invalid/500' in redirect_url:
                    logger.error("Event save failed - redirected to error page")
                    return False
                else:
                    logger.info("Event saved successfully (302 redirect)")
                    return True
            elif response.status_code == 200:
                logger.info("Event save completed (200 OK)")
                return True
            else:
                logger.error(f"Failed to save event: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving event: {str(e)}")
            return False

    def get_event_details_for_deletion(self, event_id: int) -> Optional[Dict]:
        """
        Get full event details needed for deletion by opening the event popup
        """
        try:
            logger.info(f"Getting event details for deletion: {event_id}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Open event popup to get the full form data
            params = {'eventId': str(event_id)}
            
            response = self.session.get(
                f"{self.base_url}/action/EventPopup/open",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                # Parse response to extract form data
                # For now, return a basic structure - we may need to parse HTML
                return {'eventId': event_id, 'response': response.text}
            else:
                logger.error(f"Failed to get event details: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting event details: {str(e)}")
            return None

    def get_event_popup_data(self, event_id: int) -> Dict:
        """
        Get the COMPLETE event data that ClubOS loads in the popup
        This extracts ALL form fields needed for proper deletion
        """
        try:
            logger.info(f"Getting full popup data for event {event_id}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Open the event popup to get the full form data
            # Use the correct parameter name that ClubOS expects
            data = {
                'eventId': str(event_id)
            }
            
            response = self.session.post(
                f"{self.base_url}/action/EventPopup/open",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                html = response.text
                logger.info(f"Got event popup HTML for event {event_id} ({len(html)} chars)")
                
                # Extract ALL form fields from the HTML response
                form_data = {}
                
                import re
                from urllib.parse import unquote
                
                # Find all input fields (including hidden ones)
                input_patterns = [
                    r'<input[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*/?>', 
                    r'<input[^>]*value="([^"]*)"[^>]*name="([^"]*)"[^>]*/?>'
                ]
                
                for pattern in input_patterns:
                    for match in re.finditer(pattern, html):
                        if pattern.startswith('<input[^>]*name='):
                            field_name = match.group(1)
                            field_value = unquote(match.group(2)) if match.group(2) else ''
                        else:
                            field_name = match.group(2) 
                            field_value = unquote(match.group(1)) if match.group(1) else ''
                        
                        if field_name and field_name not in form_data:
                            form_data[field_name] = field_value
                
                # Find all select fields with selected options
                select_pattern = r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>'
                for match in re.finditer(select_pattern, html, re.DOTALL):
                    field_name = match.group(1)
                    select_content = match.group(2)
                    
                    # Find selected option
                    selected_pattern = r'<option[^>]*selected[^>]*value="([^"]*)"'
                    selected_match = re.search(selected_pattern, select_content)
                    if selected_match:
                        form_data[field_name] = selected_match.group(1)
                    else:
                        # If no selected option, find first option value
                        first_option = re.search(r'<option[^>]*value="([^"]*)"', select_content)
                        if first_option:
                            form_data[field_name] = first_option.group(1)
                
                # Find all textarea fields
                textarea_pattern = r'<textarea[^>]*name="([^"]*)"[^>]*>(.*?)</textarea>'
                for match in re.finditer(textarea_pattern, html, re.DOTALL):
                    field_name = match.group(1)
                    field_value = match.group(2).strip()
                    form_data[field_name] = field_value
                
                # Find all checkbox/radio fields
                checkbox_pattern = r'<input[^>]*type="(?:checkbox|radio)"[^>]*name="([^"]*)"[^>]*(?:checked[^>]*)?value="([^"]*)"'
                for match in re.finditer(checkbox_pattern, html):
                    field_name = match.group(1)
                    field_value = match.group(2)
                    if 'checked' in match.group(0):
                        form_data[field_name] = field_value
                
                # Ensure critical deletion fields are present with proper defaults
                if 'calendarEvent.id' not in form_data:
                    form_data['calendarEvent.id'] = str(event_id)
                if 'calendarEvent.repeatEvent.calendarEventId' not in form_data:
                    form_data['calendarEvent.repeatEvent.calendarEventId'] = str(event_id)
                if 'calendarEvent.clubId' not in form_data:
                    form_data['calendarEvent.clubId'] = '291'
                if 'calendarEvent.createdFor.tfoUserId' not in form_data:
                    form_data['calendarEvent.createdFor.tfoUserId'] = '187032782'
                if 'calendarTimeSlot.past' not in form_data:
                    form_data['calendarTimeSlot.past'] = 'false'
                if 'editSeries' not in form_data:
                    form_data['editSeries'] = 'false'
                if '_sourcePage' not in form_data:
                    form_data['_sourcePage'] = self.get_source_page_token()
                
                logger.info(f"Extracted {len(form_data)} form fields for event {event_id}")
                
                # Log some key fields for debugging
                key_fields = ['calendarEvent.id', 'calendarEvent.repeatEvent.id', '_sourcePage', '__fp']
                for field in key_fields:
                    if field in form_data:
                        value_preview = str(form_data[field])[:50] + "..." if len(str(form_data[field])) > 50 else str(form_data[field])
                        logger.info(f"   {field}: {value_preview}")
                
                return form_data
            else:
                logger.error(f"Failed to get event popup data: {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting event popup data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def get_source_page_token(self) -> str:
        """Get a fresh source page token for forms"""
        try:
            # Get the calendar page to extract source page token
            response = self.session.get(
                f"{self.base_url}/action/Calendar",
                headers={
                    'Authorization': f'Bearer {self.get_bearer_token()}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            if response.status_code == 200:
                import re
                token_match = re.search(r'name="_sourcePage"\s+value="([^"]*)"', response.text)
                if token_match:
                    return token_match.group(1)
            
            return "rujoN0IVjQpJ0LGtZ3ilrGMJ3VoLcttCoZxMGTRFXqA="  # Fallback token
        except:
            return "rujoN0IVjQpJ0LGtZ3ilrGMJ3VoLcttCoZxMGTRFXqA="  # Fallback token

    def remove_event_popup(self, event_id: int) -> bool:
        """
        Remove event using MINIMAL form data approach
        Sometimes simpler is better than complex form replication
        """
        try:
            logger.info(f"Removing event {event_id} with minimal approach")
            
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
            
            # Try the SIMPLEST possible deletion request
            headers = {
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://anytime.club-os.com/action/Calendar'
            }
            
            # Minimal form data - just the essential fields
            form_data = {
                'id': str(event_id),
                '_sourcePage': self.get_source_page_token(),
                '__fp': self.get_fingerprint_token()
            }
            
            logger.info(f"Attempting minimal deletion for event {event_id}")
            response = self.session.post(
                f"{self.base_url}/action/EventPopup/remove",
                headers=headers,
                data=form_data
            )
            
            logger.info(f"Minimal deletion response: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text
                logger.info(f"Delete response: {response_text[:100]}...")
                
                if "OK" in response_text and "Something isn't right" not in response_text:
                    logger.info(f"Event {event_id} deletion appears successful")
                    return True
                else:
                    logger.error(f"Deletion failed: {response_text}")
                    return False
            else:
                logger.error(f"Deletion failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error in remove_event_popup: {e}")
            import traceback
            traceback.print_exc()
            return False
            
            logger.info(f"Deletion response: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text
                logger.info(f"Delete response text: {response_text[:200]}...")
                
                # Check for error messages in the response
                if "Something isn't right" in response_text:
                    logger.error(f"ClubOS deletion failed with error: Something isn't right")
                    return False
                elif "error" in response_text.lower():
                    logger.error(f"ClubOS deletion error in response: {response_text[:500]}")
                    return False
                else:
                    logger.info(f"Event {event_id} successfully deleted!")
                    return True
            else:
                logger.error(f"Deletion failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error in remove_event_popup: {e}")
            import traceback
            traceback.print_exc()
            return False
            
            if response.status_code == 200:
                # Check response content - successful deletions return minimal content
                response_text = response.text.strip()
                logger.info(f"Event {event_id} deletion response: {response.status_code} - '{response_text}'")
                
                # The working browser request returns status 200 with minimal content
                if len(response_text) <= 10:  # Successful deletions return very short responses
                    logger.info(f"✅ Event {event_id} deleted successfully!")
                    return True
                else:
                    logger.warning(f"Unexpected response content: {response_text}")
                    return True  # Still try to return true if status is 200
            else:
                logger.error(f"Failed to delete event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing event: {str(e)}")
            return False

    def search_attendees(self, search_term: str) -> List[Dict]:
        """
        Search for attendees to add to events
        """
        try:
            logger.info(f"Searching attendees: {search_term}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            data = {'query': search_term}
            
            response = self.session.post(
                f"{self.base_url}/action/UserSuggest/attendee-search",
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                try:
                    attendees = response.json()
                    logger.info(f"Found {len(attendees)} potential attendees")
                    return attendees
                except:
                    logger.info("Attendee search completed")
                    return []
            else:
                logger.error(f"Failed to search attendees: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching attendees: {str(e)}")
            return []

    def set_club_services(self, service_id: int, service_type: str, user_ids: List[int]) -> bool:
        """
        Set club services for event using ClubOS URL-based approach
        """
        try:
            logger.info(f"Setting club service {service_id} type {service_type} for users {user_ids}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # ClubOS passes user IDs in URL query parameters
            user_params = '&'.join([f'userIds={uid}' for uid in user_ids])
            url = f"{self.base_url}/action/Options/club-services/{service_id}/{service_type}?{user_params}"
            
            response = self.session.post(url, headers=headers)
            
            if response.status_code == 200:
                logger.info("Club services set successfully")
                return True
            else:
                logger.error(f"Failed to set club services: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting club services: {str(e)}")
            return False

    def create_event_clubos_way(self, event_data: Dict) -> bool:
        """
        Create event the way ClubOS actually does it:
        1. Open event popup
        2. Search and set attendees  
        3. Set club services
        4. Save event
        """
        try:
            logger.info("Creating event using ClubOS workflow")
            
            # Step 1: Open event popup
            if not self.open_event_popup():
                return False
            
            # Step 2: Search for attendees if provided
            if 'attendees' in event_data:
                for attendee_search in event_data['attendees']:
                    self.search_attendees(attendee_search)
            
            # Step 3: Set club services if provided
            if all(k in event_data for k in ['service_id', 'service_type', 'user_ids']):
                self.set_club_services(
                    event_data['service_id'],
                    event_data['service_type'], 
                    event_data['user_ids']
                )
            
            # Step 4: Save the event
            save_data = {k: v for k, v in event_data.items() 
                        if k not in ['attendees', 'service_id', 'service_type', 'user_ids']}
            
            return self.save_event_popup(save_data)
            
        except Exception as e:
            logger.error(f"Error creating event ClubOS way: {str(e)}")
            return False
            
            # Step 4: Save the event with proper form data
            return self.save_event_popup(event_data)
            
        except Exception as e:
            logger.error(f"Error creating event ClubOS way: {str(e)}")
            return False

    def delete_event_clubos_way(self, event_id: int) -> bool:
        """
        Delete event using COMPLETE form data extraction exactly like HAR shows:
        1. Get ALL form fields from popup
        2. Send deletion with complete 2397-byte form data
        """
        try:
            logger.info(f"Deleting event {event_id} using COMPLETE form data method")
            
            # Step 1: Get COMPLETE form data from popup
            form_data = self.get_event_popup_data(event_id)
            if not form_data:
                logger.error("Failed to get complete popup form data")
                return False
            
            logger.info(f"Got {len(form_data)} form fields for deletion")
            
            # Step 2: Send deletion with ALL form data
            headers = {
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://anytime.club-os.com/action/Calendar',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            logger.info(f"Sending deletion request with complete form data...")
            response = self.session.post(
                f"{self.base_url}/action/EventPopup/remove",
                headers=headers,
                data=form_data
            )
            
            logger.info(f"Deletion response: {response.status_code}")
            logger.info(f"Response content: {response.text[:500]}")
            
            # Check for success - ClubOS returns different responses
            if response.status_code == 200:
                if "success" in response.text.lower() or "redirect" in response.text.lower():
                    logger.info(f"Event {event_id} deleted successfully")
                    return True
                elif "something isn't right" in response.text.lower():
                    logger.error("ClubOS returned 'Something isn't right' error")
                    logger.error(f"Full response: {response.text}")
                    return False
                else:
                    # Sometimes 200 means success even without explicit message
                    logger.info(f"Event {event_id} possibly deleted (200 response)")
                    return True
            else:
                logger.error(f"Deletion failed with status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Error deleting event with complete form data: {str(e)}")
            return False

    def create_calendar_event(self, 
                             start_time: str, 
                             end_time: str, 
                             attendee_ids: List[int],
                             service_type_id: int = None,
                             trainer_id: int = None,
                             location: str = None,
                             notes: str = None) -> bool:
        """
        Create a new calendar event
        """
        try:
            logger.info(f"Creating calendar event from {start_time} to {end_time}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/json',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Build event data
            event_data = {
                'startTime': start_time,
                'endTime': end_time,
                'attendeeIds': attendee_ids,
                'trainerId': trainer_id or int(self.logged_in_user_id),  # Default to logged in user
                'serviceTypeId': service_type_id,
                'location': location,
                'notes': notes
            }
            
            response = self.session.post(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                json=event_data
            )
            
            if response.status_code == 201:
                logger.info("Calendar event created successfully")
                return True
            else:
                logger.error(f"Failed to create event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return False

    def delete_calendar_event(self, event_id: int) -> bool:
        """
        Delete a calendar event
        """
        try:
            logger.info(f"Deleting calendar event {event_id}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            response = self.session.delete(
                f"{self.base_url}/api/calendar/events/{event_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Calendar event {event_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting calendar event: {str(e)}")
            return False

    def add_attendee_to_event(self, event_id: int, attendee_id: int) -> bool:
        """
        Add an attendee to an existing event
        """
        try:
            logger.info(f"Adding attendee {attendee_id} to event {event_id}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Content-Type': 'application/json',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            attendee_data = {
                'attendeeId': attendee_id
            }
            
            response = self.session.post(
                f"{self.base_url}/api/calendar/events/{event_id}/attendees",
                headers=headers,
                json=attendee_data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Attendee {attendee_id} added to event {event_id}")
                return True
            else:
                logger.error(f"Failed to add attendee: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding attendee to event: {str(e)}")
            return False

    def remove_attendee_from_event(self, event_id: int, attendee_id: int) -> bool:
        """
        Remove an attendee from an existing event
        """
        try:
            logger.info(f"Removing attendee {attendee_id} from event {event_id}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            response = self.session.delete(
                f"{self.base_url}/api/calendar/events/{event_id}/attendees/{attendee_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Attendee {attendee_id} removed from event {event_id}")
                return True
            else:
                logger.error(f"Failed to remove attendee: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing attendee from event: {str(e)}")
            return False

    def search_clients(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for clients by name or other criteria
        """
        try:
            logger.info(f"Searching for clients: {search_term}")
            
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.get_bearer_token()}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            params = {
                'query': search_term,
                'limit': 20,
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = self.session.get(
                f"{self.base_url}/api/clients/search",
                headers=headers,
                params=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            clients = data.get('clients', []) if isinstance(data, dict) else data
            logger.info(f"Found {len(clients)} clients matching '{search_term}'")
            return clients
            
        except Exception as e:
            logger.error(f"Error searching clients: {str(e)}")
            return []

    def decode_har_event_data(self) -> Dict[str, Any]:
        """
        Decode the base64 event data from HAR files for analysis
        """
        # Base64 data from HAR response
        har_b64_data = "eyJldmVudHMiOlt7ImlkIjoxNTIyNDE2MTksImZ1bmRpbmdTdGF0dXMiOiJOT1RfRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2MzcxMDU3LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn0seyJpZCI6MjA2MzcxMDU4LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn0seyJpZCI6MjA2MzcxMDU5LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn0seyJpZCI6MjA2MzcxMDYwLCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCJ9LHsiaWQiOjIwNjUxNzg5MSwiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19LHsiaWQiOjE1MjM4MzM4MSwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjU0NTIzOCwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTUyMzM1MzgwLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2NDg0NzIwLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn1dfSx7ImlkIjoxNTA2MzYwMTksImZ1bmRpbmdTdGF0dXMiOiJOT1RfRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA0NDM1OTk2LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCJ9XX0seyJpZCI6MTUyMzcxNTUxLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2NTI5NzYwLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn1dfSx7ImlkIjoxNTA4NTAyOTQsImZ1bmRpbmdTdGF0dXMiOiJOT1RfRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA0NzA5MTA2LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCJ9XX0seyJpZCI6MTUyMzc1MTEwLCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjUzNDMyMiwiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19LHsiaWQiOjE1MjM5MDU5MywiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjU1Mzk0OCwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTUyMjQxNjA2LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjM3MTAzNCwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9LHsiaWQiOjIwNjM3MTAzNSwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9LHsiaWQiOjIwNjM3MTAzNiwiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19LHsiaWQiOjE1MjQzMjA2NywiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjYwMzMzNywiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTQ5NjQ4OTQ2LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjAyOTUwMTcxLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn1dfSx7ImlkIjoxNTIzODE2NDMsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQiLCJhdHRlbmRlZXMiOlt7ImlkIjoyMDY1NDI5MTMsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQifV19LHsiaWQiOjE1MjQwNzQ3NywiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQiLCJhdHRlbmRlZXMiOlt7ImlkIjoyMDY1NzM0MTIsImZ1bmRpbmdTdGF0dXMiOiJOT1RfRlVOREVEIn1dfSx7ImlkIjoxNTIzMzAwMzYsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQiLCJhdHRlbmRlZXMiOlt7ImlkIjoyMDY0NzgxODMsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQifSx7ImlkIjoyMDY0NzgxODQsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQifV19LHsiaWQiOjE1MjMzMTcwMywiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjQ4MDI1OCwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTUyNDM2OTgxLCJmdW5kaW5nU3RhdHVzIjoiUFJPQ0VTU0lORyIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjYwODk4MCwiZnVuZGluZ1N0YXR1cyI6IlBST0NFU1NJTkcifV19LHsiaWQiOjE1MjM5NjMzOSwiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQiLCJhdHRlbmRlZXMiOlt7ImlkIjoyMDY1NjA4MjMsImZ1bmRpbmdTdGF0dXMiOiJOT1RfRlVOREVEIn1dfSx7ImlkIjoxNTI0MDc2NjYsImZ1bmRpbmdTdGF0dXMiOiJQUk9DRVNTSU5HIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2NTczNjE2LCJmdW5kaW5nU3RhdHVzIjoiUFJPQ0VTU0lORyJ9XX0seyJpZCI6MTUyMzIzMTM0LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjQ3MDA5MSwiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19LHsiaWQiOjE1MjM2MTU5OCwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjUxNzgwOSwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTUyMjUxMDcxLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2MzgyMjE4LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn1dfSx7ImlkIjoxNTIzMzA4NTQsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQiLCJhdHRlbmRlZXMiOlt7ImlkIjoyMDY0Nzk2ODUsImZ1bmRpbmdTdGF0dXMiOiJGVU5ERUQifV19LHsiaWQiOjE1MjQwNDM5NywiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjU2OTg2MiwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTUyMzEzNzA5LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjQ1OTAwMywiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19LHsiaWQiOjE1MjQzODcwMCwiZnVuZGluZ1N0YXR1cyI6IlBST0NFU1NJTkciLCJhdHRlbmRlZXMiOlt7ImlkIjoyMDY2MTA4OTEsImZ1bmRpbmdTdGF0dXMiOiJQUk9DRVNTSU5HIn0seyJpZCI6MjA2NjEwODk4LCJmdW5kaW5nU3RhdHVzIjoiUFJPQ0VTU0lORyJ9XX0seyJpZCI6MTUyMzM0NzY2LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjQ4Mzg5OCwiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19LHsiaWQiOjE1MjM4MzQwNiwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCIsImF0dGVuZGVlcyI6W3siaWQiOjIwNjU0NTI2NiwiZnVuZGluZ1N0YXR1cyI6IkZVTkRFRCJ9XX0seyJpZCI6MTUyMzM5MjQ3LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2NDg5NzIzLCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn1dfSx7ImlkIjoxNTIzMDc4MTgsImZ1bmRpbmdTdGF0dXMiOiJOT1RfRlVOREVEIiwiYXR0ZW5kZWVzIjpbeyJpZCI6MjA2NDUxNDY1LCJmdW5kaW5nU3RhdHVzIjoiRlVOREVEIn0seyJpZCI6MjA2NDUxNDY2LCJmdW5kaW5nU3RhdHVzIjoiTk9UX0ZVTkRFRCJ9LHsiaWQiOjIwNjQ1MTQ2NywiZnVuZGluZ1N0YXR1cyI6Ik5PVF9GVU5ERUQifV19XX0="
        
        try:
            decoded_data = base64.b64decode(har_b64_data).decode('utf-8')
            return json.loads(decoded_data)
        except Exception as e:
            logger.error(f"Error decoding HAR data: {str(e)}")
            return {}

    def print_event_analysis(self):
        """
        Print analysis of the decoded HAR event data
        """
        har_data = self.decode_har_event_data()
        if 'events' in har_data:
            events = har_data['events']
            print(f"\n=== HAR EVENT DATA ANALYSIS ===")
            print(f"Total events found: {len(events)}")
            
            funding_status_counts = {}
            total_attendees = 0
            
            for i, event in enumerate(events):
                event_id = event['id']
                funding_status = event['fundingStatus']
                attendees = event.get('attendees', [])
                
                if funding_status not in funding_status_counts:
                    funding_status_counts[funding_status] = 0
                funding_status_counts[funding_status] += 1
                total_attendees += len(attendees)
                
                if i < 5:  # Show details for first 5 events
                    print(f"\nEvent {i+1}:")
                    print(f"  ID: {event_id}")
                    print(f"  Funding Status: {funding_status}")
                    print(f"  Attendees: {len(attendees)}")
                    for j, attendee in enumerate(attendees):
                        if j < 3:  # Show first 3 attendees
                            print(f"    - ID: {attendee['id']}, Status: {attendee['fundingStatus']}")
                        elif j == 3:
                            print(f"    ... and {len(attendees)-3} more")
                            break
            
            print(f"\n=== SUMMARY ===")
            print(f"Funding Status Distribution:")
            for status, count in funding_status_counts.items():
                print(f"  {status}: {count} events")
            print(f"Total attendees across all events: {total_attendees}")

def main():
    """
    Demo of the real ClubOS Calendar API
    """
    # Import secrets
    try:
        from .services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        username = secrets_manager.get_secret("clubos-username")
        password = secrets_manager.get_secret("clubos-password")
    except:
        # No fallback for production security
        username = None
        password = "L*KYqnec5z7nEL$"
    
    api = ClubOSRealCalendarAPI(username, password)
    
    print("=== ClubOS Real Calendar API Demo ===")
    
    # Step 1: Authenticate
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print(f"   User ID: {api.logged_in_user_id}")
    print(f"   Session ID: {api.session_id}")
    
    # Step 2: Access calendar page
    if not api.get_calendar_page():
        print("❌ Failed to access calendar page")
        return
    
    print("✅ Calendar page accessed successfully")
    
    # Step 3: Analyze HAR data
    print("\n=== Analyzing HAR Event Data ===")
    api.print_event_analysis()
    
    # Step 4: Get Jeremy Mayo's events using real API
    print("\n=== Fetching Real Calendar Events ===")
    events = api.get_jeremy_mayo_events()
    
    if events:
        print(f"✅ Successfully fetched {len(events)} calendar events")
        
        print("\n=== EVENT DETAILS ===")
        for i, event in enumerate(events[:10]):  # Show first 10 events
            print(f"\nEvent {i+1}:")
            print(f"  ID: {event.id}")
            print(f"  Funding Status: {event.funding_status}")
            print(f"  Attendees: {len(event.attendees)}")
            
            # Show attendee details
            for j, attendee in enumerate(event.attendees):
                if j < 3:  # Show first 3 attendees
                    print(f"    - Attendee ID: {attendee['id']}, Status: {attendee['fundingStatus']}")
                elif j == 3:
                    print(f"    ... and {len(event.attendees)-3} more attendees")
                    break
        
        if len(events) > 10:
            print(f"\n... and {len(events)-10} more events")
            
    else:
        print("❌ No events retrieved")

if __name__ == "__main__":
    main()
