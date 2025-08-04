"""
ClubOS Calendar Manager
Provides high-level calendar management functionality including:
- Getting appointments for specific days
- Managing available time slots
- Creating, updating, and deleting events
- Managing event attendees

Built on top of the proven ClubOS authentication system.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Import the working ClubOS integration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clubos_integration_fixed import ClubOSIntegration
from clubos_calendar_client import ClubOSCalendarClient, CalendarEvent, TimeSlot, Appointment


class ClubOSCalendarManager:
    """High-level calendar management interface"""
    
    def __init__(self, clubos_client: ClubOSIntegration):
        """Initialize with an authenticated ClubOS client"""
        self.clubos_client = clubos_client
        self.calendar_client = ClubOSCalendarClient(clubos_client)
        self.is_authenticated = clubos_client.is_connected
        
        if self.is_authenticated:
            print("✅ ClubOS Calendar Manager initialized successfully")
        else:
            print("❌ ClubOS Calendar Manager failed to initialize - not authenticated")
    
    def get_appointments_for_day(self, date: str = None, trainer_id: str = None) -> List[Appointment]:
        """
        Get all appointments for a specific day.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            trainer_id: Optional trainer ID to filter appointments
            
        Returns:
            List of Appointment objects
        """
        if not self.is_authenticated:
            print("❌ Cannot get appointments - not authenticated")
            return []
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"📅 Getting appointments for {date}...")
        
        try:
            # Get all calendar events first
            all_events = self.get_calendar_events(date)
            
            # Filter for appointments only
            appointments = []
            for event in all_events:
                if hasattr(event, 'event_type') and event.event_type.lower() in ['appointment', 'training', 'session']:
                    if not trainer_id or (hasattr(event, 'trainer_id') and event.trainer_id == trainer_id):
                        appointments.append(event)
            
            if appointments:
                print(f"✅ Found {len(appointments)} appointments for {date}")
                
                # Sort appointments by start time
                appointments.sort(key=lambda apt: apt.start_time)
                
                return appointments
            else:
                print(f"❌ No appointments found for {date}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting appointments: {e}")
            return []
    
    def get_available_slots(self, date: str = None, trainer_id: str = None, 
                           event_type: str = None, duration_minutes: int = 60) -> List[TimeSlot]:
        """Get available time slots for booking"""
        if not self.is_authenticated:
            print("❌ Cannot get available slots - not authenticated")
            return []
            
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        print(f"🔍 Getting available {event_type or 'all'} slots for {date}...")
        
        try:
            # Use the calendar client to get available slots
            raw_data = self.calendar_client.get_available_slots_raw(date, trainer_id, event_type)
            slots = self.calendar_client.parse_available_slots(raw_data)
            
            # Filter by duration if specified
            if duration_minutes != 60:
                slots = [slot for slot in slots if slot.duration_minutes >= duration_minutes]
                
            print(f"✅ Found {len(slots)} available slots")
            return slots
            
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []
    
    def get_calendar_events(self, date: str = None) -> List[CalendarEvent]:
        """Get calendar events for a specific date using real ClubOS format"""
        if not self.is_authenticated:
            print("❌ Cannot get calendar events - not authenticated")
            return []
            
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        print(f"📋 Getting calendar events for {date}...")
        
        try:
            events = []
            
            # Get the calendar page HTML
            if not self.calendar_client.session:
                print("❌ No authenticated session available")
                return []
                
            # Convert YYYY-MM-DD to MM/DD/YYYY format that ClubOS expects
            from datetime import datetime
            try:
                # Parse the input date and convert to ClubOS format
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                clubos_date = date_obj.strftime('%m/%d/%Y')
                print(f"📅 Converting date {date} to ClubOS format: {clubos_date}")
            except ValueError:
                # If input is already in MM/DD/YYYY format, use as-is
                clubos_date = date
                print(f"📅 Using date as-is: {clubos_date}")
            
            params = {'date': clubos_date, 'view': 'day'}
            print(f"📋 Requesting calendar for date: {clubos_date} with params: {params}")
            
            response = self.calendar_client.session.get(f"{self.calendar_client.base_url}/action/Calendar", params=params)
            
            # Save debug response for analysis
            debug_file = f"data/debug_outputs/debug_calendar_response_{date.replace('-', '')}.html"
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"📝 Saved debug response to: {debug_file}")
            except Exception as e:
                print(f"⚠️ Could not save debug file: {e}")
            
            print(f"📄 Received HTML response ({len(response.text)} characters)")
            
            # Check if response contains expected calendar structure
            if 'cal-event-container' in response.text:
                print(f"✅ Found cal-event-container in HTML")
            else:
                print(f"❌ No cal-event-container found in HTML")
                
            if 'slot-info' in response.text:
                print(f"✅ Found slot-info in HTML")
            else:
                print(f"❌ No slot-info found in HTML")
            
            if response.ok:
                # Parse HTML for events using BeautifulSoup
                from bs4 import BeautifulSoup
                import json
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for calendar event containers based on real ClubOS structure
                event_containers = soup.find_all('div', class_='cal-event-container')
                print(f"🔍 Found {len(event_containers)} event containers")
                
                if not event_containers:
                    # Also look for individual cal-event divs
                    event_containers = soup.find_all('div', class_='cal-event')
                    print(f"🔍 Found {len(event_containers)} cal-event divs")
                
                for container in event_containers:
                    try:
                        print(f"🔍 Processing container: {container.get('class', [])}")
                        
                        # Look for hidden input with JSON data
                        hidden_input = container.find('input', type='hidden')
                        if hidden_input and hidden_input.get('value'):
                            print(f"🔍 Found hidden input with value: {hidden_input.get('value')[:100]}...")
                            
                            try:
                                event_data = json.loads(hidden_input['value'])
                                print(f"🔍 Parsed JSON data: {event_data}")
                                
                                # Extract time from slot-info div
                                slot_info = container.find('div', class_='slot-info')
                                time_text = "09:00 - 10:00"  # default
                                if slot_info:
                                    # Look for the first div within slot-info
                                    time_div = slot_info.find('div')
                                    if time_div:
                                        time_text = time_div.get_text(strip=True)
                                        print(f"🔍 Found time text: {time_text}")
                                    else:
                                        time_text = slot_info.get_text(strip=True)
                                        print(f"🔍 Found time text (direct): {time_text}")
                                
                                # Parse start and end times
                                start_time = "09:00"
                                end_time = "10:00"
                                if ' - ' in time_text:
                                    times = time_text.split(' - ')
                                    if len(times) == 2:
                                        start_time = times[0].strip()
                                        end_time = times[1].strip()
                                
                                # Create CalendarEvent object
                                event = CalendarEvent(
                                    event_id=str(event_data.get('eventId', event_data.get('timeSlotId', f"event_{len(events)}"))),
                                    title=event_data.get('title', 'Training Session'),
                                    start_time=f"{date} {start_time}",
                                    end_time=f"{date} {end_time}",
                                    event_type=event_data.get('eventType', 'session'),
                                    status='scheduled'
                                )
                                events.append(event)
                                print(f"✅ Created event: {event.title} at {start_time}-{end_time} (ID: {event.event_id})")
                                
                            except json.JSONDecodeError as je:
                                print(f"⚠️ JSON decode error: {je}")
                                # If JSON parsing fails, use text content
                                title = container.get_text(strip=True)[:50]
                                if title and len(title) > 3:
                                    event = CalendarEvent(
                                        event_id=f"event_{len(events)}",
                                        title=title,
                                        start_time=f"{date} 09:00",
                                        end_time=f"{date} 10:00",
                                        event_type="appointment",
                                        status="scheduled"
                                    )
                                    events.append(event)
                        else:
                            print(f"🔍 No hidden input found in container")
                                    
                    except Exception as e:
                        print(f"⚠️ Error parsing individual event: {e}")
                        continue
            
            print(f"✅ Found {len(events)} calendar events")
            return events
            
        except Exception as e:
            print(f"❌ Error getting calendar events: {e}")
            return []
    
    def get_events_for_week(self, start_date: str = None) -> Dict[str, List[CalendarEvent]]:
        """Get all events for a week"""
        if not self.is_authenticated:
            print("❌ Cannot get weekly events - not authenticated")
            return {}
            
        if not start_date:
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            start_date = monday.strftime("%Y-%m-%d")
            
        print(f"📊 Getting weekly events starting {start_date}...")
        
        try:
            # Get events for each day of the week
            week_events = {}
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            
            for i in range(7):
                current_date = start_dt + timedelta(days=i)
                date_str = current_date.strftime("%Y-%m-%d")
                events = self.get_calendar_events(date_str)
                week_events[date_str] = events
                
            total_events = sum(len(events) for events in week_events.values())
            print(f"✅ Found {total_events} events for the week")
            return week_events
            
        except Exception as e:
            print(f"❌ Error getting weekly events: {e}")
            return {}
    
    def get_events_in_range(self, start_date: str, end_date: str) -> List[CalendarEvent]:
        """Get all events in a date range"""
        if not self.is_authenticated:
            print("❌ Cannot get range events - not authenticated")
            return []
            
        print(f"📊 Getting events from {start_date} to {end_date}...")
        
        try:
            all_events = []
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            current_dt = start_dt
            
            while current_dt <= end_dt:
                date_str = current_dt.strftime("%Y-%m-%d")
                events = self.get_calendar_events(date_str)
                all_events.extend(events)
                current_dt += timedelta(days=1)
                
            print(f"✅ Found {len(all_events)} events in range")
            return all_events
            
        except Exception as e:
            print(f"❌ Error getting range events: {e}")
            return []
    
    def create_event(self, date: str, start_time: str, end_time: str, 
                    event_type: str, title: str, **kwargs) -> str:
        """Create a new calendar event"""
        if not self.is_authenticated:
            print("❌ Cannot create event - not authenticated")
            return None
            
        print(f"➕ Creating {event_type} event: {title}")
        
        try:
            # Combine date and time
            start_datetime = f"{date} {start_time}"
            end_datetime = f"{date} {end_time}"
            
            event_data = {
                'title': title,
                'start_time': start_datetime,
                'end_time': end_datetime,
                'type': event_type,
                **kwargs
            }
            
            result = self.calendar_client.create_event_raw(event_data)
            
            if result.get('success'):
                event_id = result.get('event_id', f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                print(f"✅ Event created successfully - ID: {event_id}")
                return event_id
            else:
                print(f"❌ Failed to create event: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def update_event(self, event_id: str, **update_data) -> bool:
        """Update an existing event"""
        if not self.is_authenticated:
            print("❌ Cannot update event - not authenticated")
            return False
            
        print(f"✏️ Updating event {event_id}")
        
        try:
            result = self.calendar_client.update_event_raw(event_id, update_data)
            
            if result.get('success'):
                print(f"✅ Event updated successfully")
                return True
            else:
                print(f"❌ Failed to update event: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        if not self.is_authenticated:
            print("❌ Cannot delete event - not authenticated")
            return False
            
        print(f"🗑️ Deleting event {event_id}")
        
        try:
            result = self.calendar_client.delete_event_raw(event_id)
            
            if result.get('success'):
                print(f"✅ Event deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete event: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting event: {e}")
            return False
    
    def add_attendee_to_event(self, event_id: str, member_id: str) -> bool:
        """Add attendee to event"""
        if not self.is_authenticated:
            print("❌ Cannot add attendee - not authenticated")
            return False
            
        print(f"👥 Adding attendee {member_id} to event {event_id}")
        
        try:
            result = self.calendar_client.add_attendee_raw(event_id, member_id)
            
            if result.get('success'):
                print(f"✅ Attendee added successfully")
                return True
            else:
                print(f"❌ Failed to add attendee: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding attendee: {e}")
            return False
    
    def remove_attendee_from_event(self, event_id: str, member_id: str) -> bool:
        """Remove attendee from event"""
        if not self.is_authenticated:
            print("❌ Cannot remove attendee - not authenticated")
            return False
            
        print(f"👥 Removing attendee {member_id} from event {event_id}")
        
        try:
            result = self.calendar_client.remove_attendee_raw(event_id, member_id)
            
            if result.get('success'):
                print(f"✅ Attendee removed successfully")
                return True
            else:
                print(f"❌ Failed to remove attendee: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error removing attendee: {e}")
            return False
    
    def get_event_attendees(self, event_id: str) -> List[Dict]:
        """Get list of attendees for an event"""
        if not self.is_authenticated:
            print("❌ Cannot get attendees - not authenticated")
            return []
            
        print(f"👥 Getting attendees for event {event_id}")
        
        try:
            event_details = self.calendar_client.get_event_details_raw(event_id)
            return event_details.get('attendees', [])
            
        except Exception as e:
            print(f"❌ Error getting attendees: {e}")
            return []
    
    def reschedule_event(self, event_id: str, new_date: str, new_start_time: str, new_end_time: str) -> bool:
        """Reschedule an event to a new date and time"""
        if not self.is_authenticated:
            print("❌ Cannot reschedule event - not authenticated")
            return False
            
        print(f"📅 Rescheduling event {event_id} to {new_date} {new_start_time}-{new_end_time}")
        
        try:
            update_data = {
                'date': new_date,
                'start_time': f"{new_date} {new_start_time}",
                'end_time': f"{new_date} {new_end_time}"
            }
            
            return self.update_event(event_id, **update_data)
            
        except Exception as e:
            print(f"❌ Error rescheduling event: {e}")
            return False
    
    def get_daily_appointments(self, date: str = None) -> List[CalendarEvent]:
        """Get daily appointments (wrapper for get_appointments_for_day)"""
        return self.get_appointments_for_day(date)
    
    def get_weekly_events(self, start_date: str, end_date: str = None) -> List[CalendarEvent]:
        """Get weekly events as a flat list"""
        if not end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=6)
            end_date = end_dt.strftime("%Y-%m-%d")
            
        return self.get_events_in_range(start_date, end_date)
    
    def get_available_slots(self, date: str = None, event_type: str = "personal_training", 
                          trainer_id: str = None, duration_minutes: int = 60) -> List[TimeSlot]:
        """
        Get available time slots for booking.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            event_type: Type of event (personal_training, small_group, assessment)
            trainer_id: Optional specific trainer ID
            duration_minutes: Duration of the slot in minutes
            
        Returns:
            List of available TimeSlot objects
        """
        if not self.is_authenticated:
            print("❌ Cannot get available slots - not authenticated")
            return []
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Getting available {event_type} slots for {date}...")
        
        try:
            slots = self.calendar_client.get_available_time_slots(
                date, event_type, trainer_id, duration_minutes
            )
            
            if slots:
                print(f"✅ Found {len(slots)} available slots")
                return slots
            else:
                print(f"❌ No available slots found for {date}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []
    
    def create_event(self, date: str, start_time: str, end_time: str, 
                    event_type: str = "personal_training", title: str = None,
                    trainer_id: str = None, member_id: str = None) -> str:
        """
        Create a new calendar event.
        
        Args:
            date: Date in YYYY-MM-DD format
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            event_type: Type of event
            title: Optional event title
            trainer_id: Optional trainer ID
            member_id: Optional member ID
            
        Returns:
            Event ID if successful, None if failed
        """
        if not self.is_authenticated:
            print("❌ Cannot create event - not authenticated")
            return None
        
        print(f"➕ Creating {event_type} event for {date} {start_time}-{end_time}...")
        
        try:
            event_id = self.calendar_client.create_calendar_event(
                date, start_time, end_time, event_type, title, trainer_id, member_id
            )
            
            if event_id:
                print(f"✅ Event created successfully with ID: {event_id}")
                return event_id
            else:
                print("❌ Failed to create event")
                return None
                
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """
        Update an existing calendar event.
        
        Args:
            event_id: ID of the event to update
            **kwargs: Fields to update (title, start_time, end_time, etc.)
            
        Returns:
            True if successful, False if failed
        """
        if not self.is_authenticated:
            print("❌ Cannot update event - not authenticated")
            return False
        
        print(f"✏️ Updating event {event_id}...")
        
        try:
            success = self.calendar_client.update_calendar_event(event_id, **kwargs)
            
            if success:
                print("✅ Event updated successfully")
                return True
            else:
                print("❌ Failed to update event")
                return False
                
        except Exception as e:
            print(f"❌ Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if successful, False if failed
        """
        if not self.is_authenticated:
            print("❌ Cannot delete event - not authenticated")
            return False
        
        print(f"🗑️ Deleting event {event_id}...")
        
        try:
            success = self.calendar_client.delete_calendar_event(event_id)
            
            if success:
                print("✅ Event deleted successfully")
                return True
            else:
                print("❌ Failed to delete event")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting event: {e}")
            return False
    
    def add_attendee_to_event(self, event_id: str, member_id: str) -> bool:
        """
        Add an attendee to a calendar event.
        
        Args:
            event_id: ID of the event
            member_id: ID of the member to add
            
        Returns:
            True if successful, False if failed
        """
        if not self.is_authenticated:
            print("❌ Cannot add attendee - not authenticated")
            return False
        
        print(f"👤 Adding member {member_id} to event {event_id}...")
        
        try:
            success = self.calendar_client.add_event_attendee(event_id, member_id)
            
            if success:
                print("✅ Attendee added successfully")
                return True
            else:
                print("❌ Failed to add attendee")
                return False
                
        except Exception as e:
            print(f"❌ Error adding attendee: {e}")
            return False
    
    def remove_attendee_from_event(self, event_id: str, member_id: str) -> bool:
        """
        Remove an attendee from a calendar event.
        
        Args:
            event_id: ID of the event
            member_id: ID of the member to remove
            
        Returns:
            True if successful, False if failed
        """
        if not self.is_authenticated:
            print("❌ Cannot remove attendee - not authenticated")
            return False
        
        print(f"👤 Removing member {member_id} from event {event_id}...")
        
        try:
            success = self.calendar_client.remove_event_attendee(event_id, member_id)
            
            if success:
                print("✅ Attendee removed successfully")
                return True
            else:
                print("❌ Failed to remove attendee")
                return False
                
        except Exception as e:
            print(f"❌ Error removing attendee: {e}")
            return False
    
    def get_event_attendees(self, event_id: str) -> List[Dict]:
        """
        Get the list of attendees for an event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of attendee dictionaries
        """
        if not self.is_authenticated:
            print("❌ Cannot get attendees - not authenticated")
            return []
        
        try:
            attendees = self.calendar_client.get_event_attendees(event_id)
            return attendees or []
            
        except Exception as e:
            print(f"❌ Error getting attendees: {e}")
            return []
    
    def reschedule_event(self, event_id: str, new_date: str, new_start_time: str, new_end_time: str) -> bool:
        """
        Reschedule an event to a different date/time.
        
        Args:
            event_id: ID of the event to reschedule
            new_date: New date in YYYY-MM-DD format
            new_start_time: New start time in HH:MM format
            new_end_time: New end time in HH:MM format
            
        Returns:
            True if successful, False if failed
        """
        return self.update_event(
            event_id,
            date=new_date,
            start_time=new_start_time,
            end_time=new_end_time
        )
    
    def get_trainer_schedule(self, trainer_id: str, date: str = None) -> Dict:
        """
        Get a trainer's complete schedule for a day.
        
        Args:
            trainer_id: ID of the trainer
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary with appointments and available slots
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        appointments = self.get_appointments_for_day(date, trainer_id)
        available_slots = self.get_available_slots(date, trainer_id=trainer_id)
        
        return {
            'date': date,
            'trainer_id': trainer_id,
            'appointments': appointments,
            'available_slots': available_slots,
            'total_appointments': len(appointments),
            'total_available_slots': len(available_slots)
        }


def create_calendar_manager(username: str = None, password: str = None) -> ClubOSCalendarManager:
    """
    Factory function to create a ClubOS Calendar Manager.
    
    Args:
        username: ClubOS username (optional, will use environment variable if not provided)
        password: ClubOS password (optional, will use environment variable if not provided)
        
    Returns:
        Initialized ClubOSCalendarManager instance
    """
    print("🔧 Creating ClubOS Calendar Manager...")
    
    # Authenticate
    if username and password:
        clubos_client = ClubOSIntegration(username, password)
    else:
        # Use credentials from environment or config
        clubos_client = ClubOSIntegration()
    
    success = clubos_client.connect()
    
    if success:
        print("✅ ClubOS authentication successful")
        return ClubOSCalendarManager(clubos_client)
    else:
        print("❌ ClubOS authentication failed")
        return ClubOSCalendarManager(clubos_client)  # Return anyway but it won't be authenticated
