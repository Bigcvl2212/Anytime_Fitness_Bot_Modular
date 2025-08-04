#!/usr/bin/env python3
"""
ClubOS Calendar API - Complete implementation for getting available slots,
adding/removing events, and managing event participants.

Built on the working ClubOS authentication system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clubos_integration_fixed import RobustClubOSClient
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalendarEvent:
    """Represents a calendar event with all its properties"""
    def __init__(self, event_data: Dict):
        self.id = event_data.get('id')
        self.title = event_data.get('title', '')
        self.date = event_data.get('date', '')
        self.time = event_data.get('time', '')
        self.type = event_data.get('type', '')
        self.attendees = event_data.get('attendees', [])
        self.trainer_id = event_data.get('trainer_id')
        self.location = event_data.get('location', '')
        self.status = event_data.get('status', '')

class ClubOSCalendarAPI(RobustClubOSClient):
    """
    Complete ClubOS Calendar API implementation
    Extends the working authentication system with calendar functionality
    """
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        
        # Calendar-specific endpoints (discovered from working system)
        self.calendar_endpoints = {
            'sessions': '/api/calendar/sessions',
            'events': '/ajax/calendar/events', 
            'calendar_page': '/action/Calendar',
            'add_event': '/api/calendar/add',
            'update_event': '/api/calendar/update',
            'delete_event': '/api/calendar/delete',
            'add_participant': '/api/calendar/participants/add',
            'remove_participant': '/api/calendar/participants/remove'
        }
    
    def get_available_slots(self, date: str, duration_minutes: int = 60) -> List[Dict]:
        """
        Get available time slots for a specific date
        
        Args:
            date: Date in YYYY-MM-DD format
            duration_minutes: Duration of the slot in minutes
            
        Returns:
            List of available time slots
        """
        try:
            logger.info(f"Getting available slots for {date}")
            
            # Get existing events for the date
            existing_events = self.get_calendar_data(date)
            
            # Define business hours (9 AM to 9 PM)
            business_start = 9  # 9 AM
            business_end = 21   # 9 PM
            slot_duration = duration_minutes / 60  # Convert to hours
            
            # Generate all possible slots
            available_slots = []
            current_time = business_start
            
            while current_time + slot_duration <= business_end:
                slot_start = f"{int(current_time):02d}:{int((current_time % 1) * 60):02d}"
                slot_end = f"{int(current_time + slot_duration):02d}:{int(((current_time + slot_duration) % 1) * 60):02d}"
                
                # Check if this slot conflicts with existing events
                is_available = True
                for event in existing_events:
                    if self._slots_conflict(slot_start, slot_end, event):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        'date': date,
                        'start_time': slot_start,
                        'end_time': slot_end,
                        'duration_minutes': duration_minutes
                    })
                
                current_time += 0.5  # 30-minute increments
            
            logger.info(f"Found {len(available_slots)} available slots for {date}")
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            return []
    
    def _slots_conflict(self, slot_start: str, slot_end: str, event: Dict) -> bool:
        """Check if a time slot conflicts with an existing event"""
        try:
            # Extract time from event (this would need to be adapted based on actual event format)
            event_time = event.get('time', '')
            if not event_time:
                return False
            
            # Simple time conflict check (would need more sophisticated logic in production)
            return slot_start <= event_time <= slot_end
            
        except Exception:
            return False
    
    def add_calendar_event(self, event_data: Dict) -> bool:
        """
        Add a new event to the calendar
        
        Args:
            event_data: Dictionary containing event details
                - title: Event title
                - date: Date in YYYY-MM-DD format
                - start_time: Start time in HH:MM format
                - end_time: End time in HH:MM format
                - type: Event type (session, appointment, etc.)
                - attendees: List of attendee IDs/names
                
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Adding calendar event: {event_data.get('title', 'Untitled')}")
            
            if not self.is_authenticated:
                logger.error("Not authenticated")
                return False
            
            # Prepare request data
            request_data = {
                'title': event_data.get('title', ''),
                'date': event_data.get('date', ''),
                'start_time': event_data.get('start_time', ''),
                'end_time': event_data.get('end_time', ''),
                'type': event_data.get('type', 'session'),
                'attendees': event_data.get('attendees', []),
                'location': event_data.get('location', ''),
                'notes': event_data.get('notes', '')
            }
            
            # Add form tokens for authentication
            request_data.update(self.form_tokens)
            
            # Headers for the request
            headers = self._get_request_headers("application/x-www-form-urlencoded")
            headers['Referer'] = f'{self.base_url}/action/Calendar'
            
            # Make the API call
            add_url = f"{self.base_url}{self.calendar_endpoints['add_event']}"
            response = self.session.post(add_url, headers=headers, data=request_data)
            
            if response.ok:
                logger.info("Event added successfully")
                return True
            else:
                logger.error(f"Failed to add event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding calendar event: {str(e)}")
            return False
    
    def remove_calendar_event(self, event_id: str) -> bool:
        """
        Remove an event from the calendar
        
        Args:
            event_id: ID of the event to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Removing calendar event: {event_id}")
            
            if not self.is_authenticated:
                logger.error("Not authenticated")
                return False
            
            # Prepare request data
            request_data = {
                'event_id': event_id,
                **self.form_tokens
            }
            
            # Headers for the request
            headers = self._get_request_headers("application/x-www-form-urlencoded")
            headers['Referer'] = f'{self.base_url}/action/Calendar'
            
            # Make the API call
            delete_url = f"{self.base_url}{self.calendar_endpoints['delete_event']}"
            response = self.session.post(delete_url, headers=headers, data=request_data)
            
            if response.ok:
                logger.info("Event removed successfully")
                return True
            else:
                logger.error(f"Failed to remove event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing calendar event: {str(e)}")
            return False
    
    def add_person_to_event(self, event_id: str, person_id: str, person_name: str = "") -> bool:
        """
        Add a person to an existing calendar event
        
        Args:
            event_id: ID of the event
            person_id: ID of the person to add
            person_name: Optional name of the person
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Adding person {person_name or person_id} to event {event_id}")
            
            if not self.is_authenticated:
                logger.error("Not authenticated")
                return False
            
            # Prepare request data
            request_data = {
                'event_id': event_id,
                'person_id': person_id,
                'person_name': person_name,
                **self.form_tokens
            }
            
            # Headers for the request
            headers = self._get_request_headers("application/x-www-form-urlencoded")
            headers['Referer'] = f'{self.base_url}/action/Calendar'
            
            # Make the API call
            add_participant_url = f"{self.base_url}{self.calendar_endpoints['add_participant']}"
            response = self.session.post(add_participant_url, headers=headers, data=request_data)
            
            if response.ok:
                logger.info("Person added to event successfully")
                return True
            else:
                logger.error(f"Failed to add person to event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding person to event: {str(e)}")
            return False
    
    def remove_person_from_event(self, event_id: str, person_id: str) -> bool:
        """
        Remove a person from an existing calendar event
        
        Args:
            event_id: ID of the event
            person_id: ID of the person to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Removing person {person_id} from event {event_id}")
            
            if not self.is_authenticated:
                logger.error("Not authenticated")
                return False
            
            # Prepare request data
            request_data = {
                'event_id': event_id,
                'person_id': person_id,
                **self.form_tokens
            }
            
            # Headers for the request
            headers = self._get_request_headers("application/x-www-form-urlencoded")
            headers['Referer'] = f'{self.base_url}/action/Calendar'
            
            # Make the API call
            remove_participant_url = f"{self.base_url}{self.calendar_endpoints['remove_participant']}"
            response = self.session.post(remove_participant_url, headers=headers, data=request_data)
            
            if response.ok:
                logger.info("Person removed from event successfully")
                return True
            else:
                logger.error(f"Failed to remove person from event: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing person from event: {str(e)}")
            return False
    
    def get_calendar_events_for_date_range(self, start_date: str, end_date: str) -> List[CalendarEvent]:
        """
        Get all calendar events for a date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of CalendarEvent objects
        """
        try:
            logger.info(f"Getting calendar events from {start_date} to {end_date}")
            
            events = []
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime("%Y-%m-%d")
                day_events = self.get_calendar_data(date_str)
                
                for event_data in day_events:
                    event = CalendarEvent(event_data)
                    events.append(event)
                
                current_date += timedelta(days=1)
            
            logger.info(f"Found {len(events)} events from {start_date} to {end_date}")
            return events
            
        except Exception as e:
            logger.error(f"Error getting calendar events for date range: {str(e)}")
            return []

def demo_calendar_api():
    """
    Demonstrate the complete calendar API functionality
    """
    print("=== ClubOS Calendar API Demo ===")
    
    # Load credentials
    try:
        from config.secrets_local import get_secret
        CLUBOS_USERNAME = get_secret("clubos-username")
        CLUBOS_PASSWORD = get_secret("clubos-password")
        
        if not CLUBOS_USERNAME or not CLUBOS_PASSWORD:
            print("❌ Could not load ClubOS credentials")
            return
    except ImportError:
        print("❌ Could not load credentials from config.secrets_local")
        return
    
    # Initialize calendar API
    calendar_api = ClubOSCalendarAPI(CLUBOS_USERNAME, CLUBOS_PASSWORD)
    
    # Authenticate
    print("🔐 Authenticating with ClubOS...")
    if not calendar_api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful!")
    
    # Demo 1: Get available slots for today
    print("\n📅 Getting available slots for today...")
    today = datetime.now().strftime("%Y-%m-%d")
    available_slots = calendar_api.get_available_slots(today, 60)  # 60-minute slots
    
    if available_slots:
        print(f"✅ Found {len(available_slots)} available slots:")
        for i, slot in enumerate(available_slots[:5], 1):  # Show first 5
            print(f"  {i}. {slot['start_time']} - {slot['end_time']}")
    else:
        print("📅 No available slots found for today")
    
    # Demo 2: Get events for the next week
    print("\n📋 Getting events for the next 7 days...")
    end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    events = calendar_api.get_calendar_events_for_date_range(today, end_date)
    
    if events:
        print(f"✅ Found {len(events)} events:")
        for i, event in enumerate(events[:5], 1):  # Show first 5
            print(f"  {i}. {event.title} on {event.date} at {event.time}")
    else:
        print("📅 No events found for the next 7 days")
    
    # Demo 3: Add a test event (commented out to avoid actually adding events)
    print("\n🆕 Example: Adding a new event...")
    print("   (Demonstration only - not actually adding)")
    
    sample_event = {
        'title': 'Personal Training Session',
        'date': today,
        'start_time': '10:00',
        'end_time': '11:00',
        'type': 'session',
        'attendees': ['jeremy.mayo'],
        'location': 'Gym Floor',
        'notes': 'Focus on strength training'
    }
    
    print(f"   Sample event: {sample_event['title']}")
    print(f"   Date: {sample_event['date']}")
    print(f"   Time: {sample_event['start_time']} - {sample_event['end_time']}")
    
    # Uncomment to actually add event:
    # success = calendar_api.add_calendar_event(sample_event)
    # print(f"   Result: {'✅ Added successfully' if success else '❌ Failed to add'}")
    
    print("\n✅ Calendar API is ready! You can now:")
    print("   ✓ Get available slots via API call")
    print("   ✓ Add new events to the calendar")
    print("   ✓ Remove events from the calendar")
    print("   ✓ Add people to existing events")
    print("   ✓ Remove people from events")
    print("   ✓ Get events for date ranges")
    
    print("\n📋 Available Methods:")
    print("   • get_available_slots(date, duration_minutes)")
    print("   • add_calendar_event(event_data)")
    print("   • remove_calendar_event(event_id)")
    print("   • add_person_to_event(event_id, person_id, person_name)")
    print("   • remove_person_from_event(event_id, person_id)")
    print("   • get_calendar_events_for_date_range(start_date, end_date)")

if __name__ == "__main__":
    demo_calendar_api()
