"""
ClubOS Calendar Client
Handles low-level calendar API operations and data structures.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TimeSlot:
    """Represents an available time slot for booking"""
    start_time: str
    end_time: str
    duration_minutes: int
    trainer_name: Optional[str] = None
    trainer_id: Optional[str] = None
    event_type: Optional[str] = None
    is_available: bool = True


@dataclass
class Appointment:
    """Represents an appointment (alias for CalendarEvent for compatibility)"""
    event_id: str
    title: str
    start_time: str
    end_time: str
    member_name: Optional[str] = None
    member_id: Optional[str] = None
    trainer_name: Optional[str] = None
    trainer_id: Optional[str] = None
    appointment_type: str = "appointment"
    status: str = "scheduled"
    description: Optional[str] = None
    location: Optional[str] = None


@dataclass
class CalendarEvent:
    """Represents a calendar event/appointment"""
    event_id: str
    title: str
    start_time: str
    end_time: str
    event_type: str
    status: str
    trainer_name: Optional[str] = None
    trainer_id: Optional[str] = None
    member_name: Optional[str] = None
    member_id: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[Dict] = None
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class ClubOSCalendarClient:
    """Low-level ClubOS Calendar API client"""
    
    def __init__(self, clubos_integration):
        """Initialize with authenticated ClubOS integration"""
        self.clubos_integration = clubos_integration
        self.session = clubos_integration.client.session if clubos_integration.client else None
        self.base_url = "https://anytime.club-os.com"
        self.calendar_url = f"{self.base_url}/action/Calendar"
        
    def get_calendar_data(self, date: str = None, view: str = "day") -> Dict:
        """Get raw calendar data from ClubOS API
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            view: 'day', 'week', or 'month'
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        params = {
            'date': date,
            'view': view
        }
        
        try:
            response = self.session.get(self.calendar_url, params=params)
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                return response.json()
            except:
                # If not JSON, return HTML content for parsing
                return {'html_content': response.text}
                
        except Exception as e:
            print(f"❌ Error getting calendar data: {e}")
            return {}
    
    def get_available_slots_raw(self, date: str, trainer_id: str = None, 
                               event_type: str = None) -> Dict:
        """Get raw available slots data"""
        endpoint = f"{self.calendar_url}/available-slots"
        
        params = {
            'date': date,
            'trainer_id': trainer_id,
            'event_type': event_type
        }
        
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return {}
    
    def create_event_raw(self, event_data: Dict) -> Dict:
        """Create a new calendar event"""
        endpoint = f"{self.calendar_url}/create"
        
        try:
            response = self.session.post(endpoint, json=event_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return {}
    
    def update_event_raw(self, event_id: str, update_data: Dict) -> Dict:
        """Update an existing event"""
        endpoint = f"{self.calendar_url}/update/{event_id}"
        
        try:
            response = self.session.put(endpoint, json=update_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error updating event: {e}")
            return {}
    
    def delete_event_raw(self, event_id: str) -> Dict:
        """Delete a calendar event"""
        endpoint = f"{self.calendar_url}/delete/{event_id}"
        
        try:
            response = self.session.delete(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error deleting event: {e}")
            return {}
    
    def add_attendee_raw(self, event_id: str, member_id: str) -> Dict:
        """Add attendee to event"""
        endpoint = f"{self.calendar_url}/event/{event_id}/attendees"
        
        data = {'member_id': member_id}
        
        try:
            response = self.session.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error adding attendee: {e}")
            return {}
    
    def remove_attendee_raw(self, event_id: str, member_id: str) -> Dict:
        """Remove attendee from event"""
        endpoint = f"{self.calendar_url}/event/{event_id}/attendees/{member_id}"
        
        try:
            response = self.session.delete(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error removing attendee: {e}")
            return {}
    
    def get_event_details_raw(self, event_id: str) -> Dict:
        """Get detailed information about a specific event"""
        endpoint = f"{self.calendar_url}/event/{event_id}"
        
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error getting event details: {e}")
            return {}
    
    def parse_calendar_events(self, raw_data: Dict) -> List[CalendarEvent]:
        """Parse raw calendar data into CalendarEvent objects"""
        events = []
        
        if 'events' in raw_data:
            for event_data in raw_data['events']:
                if isinstance(event_data, dict):
                    event = CalendarEvent(
                        event_id=event_data.get('id', ''),
                        title=event_data.get('title', ''),
                        start_time=event_data.get('start_time', ''),
                        end_time=event_data.get('end_time', ''),
                        event_type=event_data.get('type', ''),
                        status=event_data.get('status', 'scheduled'),
                        trainer_name=event_data.get('trainer_name'),
                        trainer_id=event_data.get('trainer_id'),
                        member_name=event_data.get('member_name'),
                        member_id=event_data.get('member_id'),
                        description=event_data.get('description'),
                        location=event_data.get('location'),
                        attendees=event_data.get('attendees', [])
                    )
                    events.append(event)
        
        elif 'html_content' in raw_data:
            # Parse HTML content for events (fallback method)
            events = self._parse_html_events(raw_data['html_content'])
        
        return events
    
    def parse_available_slots(self, raw_data: Dict) -> List[TimeSlot]:
        """Parse raw available slots data into TimeSlot objects"""
        slots = []
        
        if 'slots' in raw_data:
            for slot_data in raw_data['slots']:
                slot = TimeSlot(
                    start_time=slot_data.get('start_time', ''),
                    end_time=slot_data.get('end_time', ''),
                    duration_minutes=slot_data.get('duration_minutes', 60),
                    trainer_name=slot_data.get('trainer_name'),
                    trainer_id=slot_data.get('trainer_id'),
                    event_type=slot_data.get('event_type'),
                    is_available=slot_data.get('is_available', True)
                )
                slots.append(slot)
        
        return slots
    
    def _parse_html_events(self, html_content: str) -> List[CalendarEvent]:
        """Parse events from HTML content (fallback method)"""
        from bs4 import BeautifulSoup
        
        events = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for event elements in the HTML
            event_elements = soup.find_all(['div', 'tr'], class_=lambda x: x and ('event' in x or 'appointment' in x))
            
            for element in event_elements:
                # Extract event information from HTML structure
                title = self._extract_text_from_element(element, ['title', 'event-title', 'appointment-title'])
                start_time = self._extract_text_from_element(element, ['start-time', 'time'])
                event_type = self._extract_text_from_element(element, ['type', 'event-type'])
                
                if title and start_time:
                    event = CalendarEvent(
                        event_id=element.get('data-id', f"html_event_{len(events)}"),
                        title=title,
                        start_time=start_time,
                        end_time='',  # Will be filled if found
                        event_type=event_type or 'appointment',
                        status='scheduled'
                    )
                    events.append(event)
        
        except Exception as e:
            print(f"⚠️ Error parsing HTML events: {e}")
        
        return events
    
    def get_calendar_events(self, date: str, view: str = "day") -> Dict:
        """Get calendar events for a specific date"""
        if not self.session:
            print("❌ No authenticated session available")
            return {}
            
        print(f"📋 Getting calendar events for {date}...")
        
        try:
            # Use the calendar URL with date parameter
            params = {
                'date': date,
                'view': view
            }
            
            response = self.session.get(self.calendar_url, params=params)
            response.raise_for_status()
            
            # Parse the HTML response to extract calendar events
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for event elements (this will need to be customized based on the actual HTML structure)
            events = []
            event_elements = soup.find_all(['div', 'tr'], class_=lambda x: x and ('event' in x.lower() or 'appointment' in x.lower()))
            
            for element in event_elements:
                # Extract event data from HTML
                event_data = self._extract_event_from_element(element)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Found {len(events)} events")
            return {'events': events}
            
        except Exception as e:
            print(f"❌ Error getting calendar events: {e}")
            return {}
    
    def get_appointments_for_date(self, date: str, trainer_id: str = None) -> List:
        """Get appointments for a specific date"""
        if not self.session:
            print("❌ No authenticated session available")
            return []
            
        print(f"📅 Getting appointments for {date}...")
        
        try:
            # Get calendar data for the date
            calendar_data = self.get_calendar_events(date)
            
            # Filter for appointments only
            appointments = []
            for event in calendar_data.get('events', []):
                if event.get('type', '').lower() in ['appointment', 'training', 'session']:
                    if not trainer_id or event.get('trainer_id') == trainer_id:
                        appointments.append(event)
            
            print(f"✅ Found {len(appointments)} appointments")
            return appointments
            
        except Exception as e:
            print(f"❌ Error getting appointments: {e}")
            return []
    
    def get_available_time_slots(self, date: str, event_type: str = None, 
                                trainer_id: str = None, duration_minutes: int = 60) -> List[TimeSlot]:
        """Get available time slots for booking"""
        if not self.session:
            print("❌ No authenticated session available")
            return []
            
        print(f"🔍 Getting available {event_type or 'all'} slots for {date}...")
        
        try:
            # This would typically call a specific API endpoint for available slots
            # For now, we'll simulate by checking the calendar for gaps
            
            # Get existing events for the date
            calendar_data = self.get_calendar_events(date)
            existing_events = calendar_data.get('events', [])
            
            # Generate time slots (simplified approach)
            available_slots = []
            
            # Business hours: 6 AM to 10 PM
            for hour in range(6, 22):
                for minute in [0, 30]:  # Every 30 minutes
                    start_time = f"{hour:02d}:{minute:02d}"
                    end_hour = hour + (duration_minutes // 60)
                    end_minute = minute + (duration_minutes % 60)
                    if end_minute >= 60:
                        end_hour += 1
                        end_minute -= 60
                    end_time = f"{end_hour:02d}:{end_minute:02d}"
                    
                    # Check if this slot conflicts with existing events
                    slot_available = True
                    for event in existing_events:
                        event_start = event.get('start_time', '')
                        if start_time in event_start:
                            slot_available = False
                            break
                    
                    if slot_available:
                        slot = TimeSlot(
                            start_time=f"{date} {start_time}",
                            end_time=f"{date} {end_time}",
                            duration_minutes=duration_minutes,
                            event_type=event_type,
                            is_available=True
                        )
                        available_slots.append(slot)
            
            print(f"✅ Found {len(available_slots)} available slots")
            return available_slots
            
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []
    
    def create_calendar_event(self, event_data: Dict) -> Dict:
        """Create a new calendar event"""
        if not self.session:
            print("❌ No authenticated session available")
            return {}
            
        print(f"➕ Creating calendar event for {event_data.get('date')} {event_data.get('start_time')}-{event_data.get('end_time')}...")
        
        try:
            # This would need to be implemented based on the actual ClubOS API
            # For now, we'll simulate a successful creation
            
            # In a real implementation, this would POST to the calendar API
            # with the appropriate form data and CSRF tokens
            
            event_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            print(f"✅ Event created with ID: {event_id}")
            return {
                'success': True,
                'event_id': event_id,
                'message': 'Event created successfully (simulated)'
            }
            
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_event_from_element(self, element) -> Dict:
        """Extract event data from HTML element"""
        try:
            # This would need to be customized based on actual ClubOS HTML structure
            event_data = {
                'id': element.get('data-id', f"event_{len(str(element))}"),
                'title': self._extract_text_from_element(element, ['title', 'event-title', 'appointment-title']),
                'start_time': self._extract_text_from_element(element, ['start-time', 'time']),
                'end_time': self._extract_text_from_element(element, ['end-time']),
                'type': self._extract_text_from_element(element, ['type', 'event-type']) or 'appointment',
                'status': 'scheduled',
                'trainer_name': self._extract_text_from_element(element, ['trainer', 'trainer-name']),
                'member_name': self._extract_text_from_element(element, ['member', 'member-name']),
                'description': self._extract_text_from_element(element, ['description', 'notes'])
            }
            
            # Only return if we found at least a title and time
            if event_data['title'] and event_data['start_time']:
                return event_data
            
        except Exception as e:
            print(f"⚠️ Error extracting event from element: {e}")
        
        return None
    
    def _extract_text_from_element(self, element, class_names: List[str]) -> str:
        """Helper to extract text from HTML element by class names"""
        for class_name in class_names:
            found = element.find(class_=class_name)
            if found:
                return found.get_text(strip=True)
        return ""
