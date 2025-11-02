"""
ClubOS Calendar API Client
Provides comprehensive calendar management functionality including:
- Get available time slots
- Add/remove events from calendar
- Add/remove people from events
- Manage calendar appointments and sessions

Built on the existing clubos_integration_fixed.py authentication system.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import requests
from dataclasses import dataclass
from ..authentication.unified_auth_service import get_unified_auth_service, AuthenticationSession

# Import the existing ClubOS client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clubos_integration_fixed import RobustClubOSClient


@dataclass
class CalendarEvent:
    """Represents a calendar event/appointment"""
    event_id: str
    title: str
    start_time: str
    end_time: str
    date: str
    event_type: str
    trainer_id: Optional[str] = None
    trainer_name: Optional[str] = None
    member_id: Optional[str] = None
    member_name: Optional[str] = None
    location_id: Optional[str] = None
    status: str = "scheduled"
    max_attendees: int = 1
    current_attendees: int = 0
    is_available: bool = True


@dataclass
class TimeSlot:
    """Represents an available time slot"""
    date: str
    start_time: str
    end_time: str
    duration_minutes: int
    trainer_id: Optional[str] = None
    trainer_name: Optional[str] = None
    is_available: bool = True
    event_type: str = "training"


class ClubOSCalendarClient:
    """Enhanced ClubOS client specifically for calendar operations"""
    
    def __init__(self, username: str = None, password: str = None):
        """Initialize with ClubOS credentials"""
        self.username = username
        self.password = password
        
        # Get unified authentication service
        self.auth_service = get_unified_auth_service()
        self.auth_session: Optional[AuthenticationSession] = None
        
        # Legacy attributes
        self.client = None
        self.is_authenticated = False
        
        # Calendar-specific endpoints
        self.calendar_endpoints = {
            'events': '/api/calendar/events',
            'sessions': '/api/calendar/sessions', 
            'availability': '/api/calendar/availability',
            'book_session': '/api/calendar/book',
            'cancel_session': '/api/calendar/cancel',
            'add_attendee': '/api/calendar/attendee/add',
            'remove_attendee': '/api/calendar/attendee/remove',
            'create_event': '/api/calendar/create',
            'update_event': '/api/calendar/update',
            'delete_event': '/api/calendar/delete'
        }
        
        # Event types available in ClubOS
        self.event_types = {
            'personal_training': {'id': 2, 'name': 'Personal Training', 'icon': 'icon_trainer.png'},
            'small_group': {'id': 8, 'name': 'Small Group Training', 'icon': 'icon_smallgrouptraining.png'},
            'assessment': {'id': 5, 'name': 'Assessment', 'icon': 'icon_assessment.png'},
            'consultation': {'id': 1, 'name': 'Consultation', 'icon': 'icon_consultation.png'}
        }
    
    def authenticate(self) -> bool:
        """Authenticate using the unified authentication service"""
        try:
            print("🔐 Initializing ClubOS Calendar API...")
            
            # Use unified authentication service
            self.auth_session = self.auth_service.authenticate_clubos(self.username, self.password)
            
            if not self.auth_session or not self.auth_session.authenticated:
                print("❌ ClubOS Calendar API authentication failed")
                self.is_authenticated = False
                return False
            
            # Create legacy client wrapper for compatibility
            self.client = type('MockClient', (), {
                'session': self.auth_session.session,
                'base_url': self.auth_session.base_url,
                '_get_request_headers': lambda self, content_type: {'Content-Type': content_type}
            })()
            
            self.is_authenticated = True
            print("✅ ClubOS Calendar API ready!")
            return True
                
        except Exception as e:
            print(f"❌ Calendar API authentication error: {e}")
            self.is_authenticated = False
            return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication"""
        if not self.is_authenticated or not self.client:
            return self.authenticate()
        return True
    
    # ========================================
    # GET AVAILABLE SLOTS
    # ========================================
    
    def get_available_slots(self, date: str = None, trainer_id: str = None, 
                          event_type: str = 'personal_training') -> List[TimeSlot]:
        """
        Get available time slots for booking appointments.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            trainer_id: Specific trainer ID (optional)
            event_type: Type of appointment (personal_training, small_group, etc.)
            
        Returns:
            List of available TimeSlot objects
        """
        if not self.ensure_authenticated():
            return []
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"📅 Getting available slots for {date} (type: {event_type})")
        
        try:
            # Try multiple availability endpoints
            availability_endpoints = [
                f"/api/calendar/availability?date={date}&eventType={event_type}",
                f"/api/calendar/slots?date={date}&type={event_type}",
                f"/ajax/calendar/availability?date={date}",
                f"/action/Calendar/availability?date={date}"
            ]
            
            if trainer_id:
                availability_endpoints = [ep + f"&trainerId={trainer_id}" for ep in availability_endpoints]
            
            for endpoint in availability_endpoints:
                slots = self._fetch_availability_data(endpoint, date, event_type)
                if slots:
                    print(f"✅ Found {len(slots)} available slots from {endpoint}")
                    return slots
            
            # Fallback: parse from main calendar page
            slots = self._get_slots_from_calendar_page(date, trainer_id, event_type)
            if slots:
                print(f"✅ Parsed {len(slots)} slots from calendar HTML")
                return slots
            
            print("❌ No available slots found")
            return []
            
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []
    
    def _fetch_availability_data(self, endpoint: str, date: str, event_type: str) -> List[TimeSlot]:
        """Fetch availability data from a specific endpoint"""
        try:
            url = f"{self.client.base_url}{endpoint}"
            response = self.client.session.get(
                url,
                headers=self.client._get_request_headers("application/json")
            )
            
            if not response.ok:
                return []
            
            # Try to parse JSON response
            try:
                data = response.json()
                return self._parse_availability_json(data, date, event_type)
            except:
                # Try to parse HTML response
                return self._parse_availability_html(response.text, date, event_type)
                
        except Exception as e:
            print(f"❌ Error fetching from {endpoint}: {e}")
            return []
    
    def _parse_availability_json(self, data: Any, date: str, event_type: str) -> List[TimeSlot]:
        """Parse availability data from JSON response"""
        slots = []
        
        try:
            if isinstance(data, dict):
                # Handle different JSON structures
                if 'slots' in data:
                    slots_data = data['slots']
                elif 'availability' in data:
                    slots_data = data['availability']
                elif 'times' in data:
                    slots_data = data['times']
                else:
                    slots_data = [data]  # Single slot object
            elif isinstance(data, list):
                slots_data = data
            else:
                return []
            
            for slot_data in slots_data:
                if isinstance(slot_data, dict):
                    slot = TimeSlot(
                        date=date,
                        start_time=slot_data.get('startTime', slot_data.get('start', '')),
                        end_time=slot_data.get('endTime', slot_data.get('end', '')),
                        duration_minutes=slot_data.get('duration', 30),
                        trainer_id=str(slot_data.get('trainerId', '')),
                        trainer_name=slot_data.get('trainerName', ''),
                        is_available=slot_data.get('available', True),
                        event_type=event_type
                    )
                    slots.append(slot)
            
            return slots
            
        except Exception as e:
            print(f"❌ Error parsing availability JSON: {e}")
            return []
    
    def _parse_availability_html(self, html: str, date: str, event_type: str) -> List[TimeSlot]:
        """Parse availability data from HTML response"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            slots = []
            
            # Look for time slot elements
            slot_selectors = [
                '.time-slot', '.available-slot', '.appointment-slot',
                '[data-time]', '.calendar-slot', '.booking-slot'
            ]
            
            for selector in slot_selectors:
                elements = soup.select(selector)
                for element in elements:
                    # Extract time information
                    start_time = (element.get('data-start-time') or 
                                element.get('data-time') or 
                                element.select_one('.start-time, .time'))
                    
                    if start_time and hasattr(start_time, 'get_text'):
                        start_time = start_time.get_text(strip=True)
                    elif isinstance(start_time, str):
                        pass  # Already a string
                    else:
                        continue  # Skip if no valid time found
                    
                    # Create time slot
                    slot = TimeSlot(
                        date=date,
                        start_time=str(start_time),
                        end_time=self._calculate_end_time(str(start_time), 30),  # Default 30 min
                        duration_minutes=30,
                        trainer_id=element.get('data-trainer-id', ''),
                        trainer_name=element.get('data-trainer-name', ''),
                        is_available=not element.has_attr('disabled'),
                        event_type=event_type
                    )
                    slots.append(slot)
                
                if slots:  # If we found slots with this selector, use them
                    break
            
            return slots
            
        except Exception as e:
            print(f"❌ Error parsing availability HTML: {e}")
            return []
    
    def _get_slots_from_calendar_page(self, date: str, trainer_id: str, event_type: str) -> List[TimeSlot]:
        """Get available slots by parsing the main calendar page"""
        try:
            calendar_url = f"{self.client.base_url}/action/Calendar?date={date}"
            response = self.client.session.get(
                calendar_url,
                headers=self.client._get_request_headers()
            )
            
            if response.ok:
                return self._parse_availability_html(response.text, date, event_type)
            
            return []
            
        except Exception as e:
            print(f"❌ Error getting calendar page: {e}")
            return []
    
    def _calculate_end_time(self, start_time: str, duration_minutes: int) -> str:
        """Calculate end time based on start time and duration"""
        try:
            # Parse start time (assuming format like "09:00" or "9:00 AM")
            if 'AM' in start_time or 'PM' in start_time:
                start_dt = datetime.strptime(start_time, "%I:%M %p")
            else:
                start_dt = datetime.strptime(start_time, "%H:%M")
            
            # Add duration
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            # Return in same format as input
            if 'AM' in start_time or 'PM' in start_time:
                return end_dt.strftime("%I:%M %p")
            else:
                return end_dt.strftime("%H:%M")
                
        except:
            return start_time  # Return original if parsing fails
    
    # ========================================
    # GET CALENDAR EVENTS
    # ========================================
    
    def get_calendar_events(self, date: str = None, trainer_id: str = None) -> List[CalendarEvent]:
        """
        Get calendar events for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            trainer_id: Filter by specific trainer (optional)
            
        Returns:
            List of CalendarEvent objects
        """
        if not self.ensure_authenticated():
            return []
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"📅 Getting calendar events for {date}")
        
        try:
            # Try the documented calendar events endpoint first
            events_url = f"{self.client.base_url}/api/calendar/events?date={date}"
            if trainer_id:
                events_url += f"&trainerId={trainer_id}"
            
            response = self.client.session.get(
                events_url,
                headers=self.client._get_request_headers("application/json")
            )
            
            if response.ok:
                try:
                    data = response.json()
                    events = self._parse_events_json(data, date)
                    if events:
                        print(f"✅ Retrieved {len(events)} events from API")
                        return events
                except:
                    pass
            
            # Fallback to existing get_calendar_data method
            calendar_data = self.client.get_calendar_data(date)
            events = self._convert_calendar_data_to_events(calendar_data, date)
            
            if events:
                print(f"✅ Retrieved {len(events)} events from fallback method")
            
            return events
            
        except Exception as e:
            print(f"❌ Error getting calendar events: {e}")
            return []
    
    def _parse_events_json(self, data: Any, date: str) -> List[CalendarEvent]:
        """Parse calendar events from JSON response"""
        events = []
        
        try:
            if isinstance(data, dict):
                if 'events' in data:
                    events_data = data['events']
                elif 'sessions' in data:
                    events_data = data['sessions']
                else:
                    events_data = [data]  # Single event
            elif isinstance(data, list):
                events_data = data
            else:
                return []
            
            for event_data in events_data:
                if isinstance(event_data, dict):
                    event = CalendarEvent(
                        event_id=str(event_data.get('id', event_data.get('eventId', ''))),
                        title=event_data.get('title', event_data.get('name', 'Appointment')),
                        start_time=event_data.get('startTime', event_data.get('start', '')),
                        end_time=event_data.get('endTime', event_data.get('end', '')),
                        date=date,
                        event_type=event_data.get('type', event_data.get('eventType', 'session')),
                        trainer_id=str(event_data.get('trainerId', '')),
                        trainer_name=event_data.get('trainerName', ''),
                        member_id=str(event_data.get('memberId', '')),
                        member_name=event_data.get('memberName', ''),
                        status=event_data.get('status', 'scheduled'),
                        max_attendees=event_data.get('maxAttendees', 1),
                        current_attendees=event_data.get('currentAttendees', 0)
                    )
                    events.append(event)
            
            return events
            
        except Exception as e:
            print(f"❌ Error parsing events JSON: {e}")
            return []
    
    def _convert_calendar_data_to_events(self, calendar_data: List[Dict], date: str) -> List[CalendarEvent]:
        """Convert calendar data from existing method to CalendarEvent objects"""
        events = []
        
        try:
            for item in calendar_data:
                event = CalendarEvent(
                    event_id=str(item.get('id', '')),
                    title=item.get('title', 'Event'),
                    start_time=item.get('time', ''),
                    end_time='',  # Will need to calculate or extract
                    date=date,
                    event_type=item.get('type', 'session'),
                    status='scheduled'
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            print(f"❌ Error converting calendar data: {e}")
            return []


def create_calendar_client(username: str = None, password: str = None) -> ClubOSCalendarClient:
    """Factory function to create and authenticate a calendar client"""
    client = ClubOSCalendarClient(username, password)
    client.authenticate()
    return client


# Example usage and testing
if __name__ == "__main__":
    # Initialize calendar client
    calendar_client = create_calendar_client()
    
    if calendar_client.is_authenticated:
        print("🎉 Calendar client ready for testing!")
        
        # Test getting available slots
        print("\\n📅 Testing available slots...")
        slots = calendar_client.get_available_slots()
        print(f"Found {len(slots)} available slots")
        
        # Test getting calendar events
        print("\\n📅 Testing calendar events...")
        events = calendar_client.get_calendar_events()
        print(f"Found {len(events)} calendar events")
        
    else:
        print("❌ Calendar client authentication failed")
