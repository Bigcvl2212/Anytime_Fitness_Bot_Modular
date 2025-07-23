#!/usr/bin/env python3
"""
ClubOS Calendar API Service

API-based calendar management for booking training sessions and appointments.
Replaces Selenium-based calendar workflow with direct API calls.
"""

import time
import json
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, quote

from services.api.clubos_api_client import ClubOSAPIClient, create_clubos_api_client
from config.constants import CLUBOS_CALENDAR_URL


class ClubOSCalendarAPIService:
    """
    API-based calendar service that replaces Selenium calendar workflow.
    Handles calendar navigation, session booking, and appointment management.
    """
    
    def __init__(self, username: str, password: str):
        """Initialize ClubOS Calendar API service with authentication"""
        self.api_client = create_clubos_api_client(username, password)
        if not self.api_client:
            raise Exception("Failed to authenticate with ClubOS API")
        
        self.session = self.api_client.session
        self.auth = self.api_client.auth
        self.base_url = "https://anytime.club-os.com"
        
        # Calendar API endpoints
        self.endpoints = {
            "calendar": "/action/Calendar",
            "calendar_data": "/ajax/calendar/data",
            "calendar_events": "/ajax/calendar/events",
            "book_appointment": "/ajax/calendar/book",
            "add_participant": "/ajax/calendar/add-participant",
            "calendar_navigation": "/ajax/calendar/navigate",
            "schedule_views": "/ajax/calendar/schedules",
            "available_slots": "/ajax/calendar/available-slots"
        }
    
    def navigate_calendar_week(self, direction: str = 'next') -> bool:
        """
        Navigate calendar forward or backward by one week using API.
        
        Args:
            direction: 'next' or 'previous'
            
        Returns:
            bool: True if navigation successful
        """
        print(f"📅 API: Navigating calendar {direction} one week...")
        
        try:
            # Get current calendar state
            current_state = self._get_calendar_state()
            if not current_state:
                print("   ❌ Could not get current calendar state")
                return False
            
            # Calculate target date
            current_date = datetime.strptime(
                current_state.get("current_date", datetime.now().strftime("%Y-%m-%d")), 
                "%Y-%m-%d"
            )
            
            if direction == 'next':
                target_date = current_date + timedelta(weeks=1)
            else:
                target_date = current_date - timedelta(weeks=1)
            
            # Navigate to target week
            navigation_data = {
                "action": "navigate",
                "direction": direction,
                "target_date": target_date.strftime("%Y-%m-%d"),
                "view_type": current_state.get("view_type", "week")
            }
            
            response = self.session.post(
                urljoin(self.base_url, self.endpoints["calendar_navigation"]),
                data=navigation_data,
                headers=self.auth.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"   ✅ Successfully navigated calendar {direction}")
                return True
            else:
                print(f"   ❌ Navigation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error navigating calendar: {e}")
            return False
    
    def get_calendar_view_details(self, schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
        """
        Get detailed calendar view with available slots and booked sessions.
        
        Args:
            schedule_name: Name of the schedule to view
            
        Returns:
            Dict with calendar data organized by day
        """
        print(f"📅 API: Getting calendar details for '{schedule_name}'...")
        
        try:
            # Get available schedules
            schedules = self._get_available_schedules()
            if not schedules:
                print("[DEBUG] Schedules endpoint failed, falling back to /api/calendar/sessions for today...")
                today = datetime.now().strftime('%Y-%m-%d')
                sessions = self.api_client.get_calendar_sessions(today)
                fallback_data = {today: []}
                for session in sessions:
                    fallback_data[today].append({
                        'time': session.get('start_time', session.get('time', '')),
                        'status': session.get('type', 'Booked'),
                        'session_id': session.get('id'),
                        'member_name': session.get('member_name', ''),
                        'notes': session.get('notes', '')
                    })
                print(f"[DEBUG] Fallback: Found {len(fallback_data[today])} sessions for today.")
                return fallback_data
            
            # Find target schedule
            target_schedule_id = None
            for schedule in schedules:
                if schedule.get("name", "").lower() == schedule_name.lower():
                    target_schedule_id = schedule.get("id")
                    break
            
            if not target_schedule_id:
                print(f"   ❌ Schedule '{schedule_name}' not found")
                return {}
            
            # Get calendar data for the schedule
            calendar_data = self._get_calendar_data(target_schedule_id)
            if not calendar_data:
                print("   ❌ Could not get calendar data")
                return {}
            
            # Process and organize calendar data
            organized_data = self._organize_calendar_data(calendar_data)
            
            print(f"   ✅ Retrieved calendar data for {len(organized_data)} days")
            return organized_data
            
        except Exception as e:
            print(f"   ❌ Error getting calendar details: {e}")
            return {}
    
    def book_appointment(self, details: Dict[str, Any]) -> bool:
        """
        Book an appointment using API.
        
        Args:
            details: Dictionary containing booking details:
                - member_name: Name of member to book for
                - time: Time slot (e.g., "10:30 AM")
                - date: Date (e.g., "2025-01-15")
                - event_type: Type of appointment (e.g., "Personal Training")
                - schedule_name: Schedule to book on
                - duration: Duration in minutes (optional)
                - notes: Additional notes (optional)
                
        Returns:
            bool: True if booking successful
        """
        print(f"📅 API: Booking appointment for '{details['member_name']}'...")
        
        try:
            # Step 1: Find member
            member_info = self._find_member(details['member_name'])
            if not member_info:
                print(f"   ❌ Member '{details['member_name']}' not found")
                return False
            
            # Step 2: Get available time slots
            available_slots = self._get_available_slots(
                details.get('schedule_name', 'My schedule'),
                details.get('date')
            )
            
            if not available_slots:
                print(f"   ❌ No available slots found for {details['date']}")
                return False
            
            # Step 3: Find matching time slot
            target_slot = None
            for slot in available_slots:
                if slot.get('time') == details['time']:
                    target_slot = slot
                    break
            
            if not target_slot:
                print(f"   ❌ Time slot '{details['time']}' not available")
                return False
            
            # Step 4: Book the appointment
            booking_data = {
                "member_id": member_info['id'],
                "slot_id": target_slot['id'],
                "event_type": details.get('event_type', 'Personal Training'),
                "duration": details.get('duration', 60),
                "notes": details.get('notes', ''),
                "schedule_name": details.get('schedule_name', 'My schedule')
            }
            
            response = self.session.post(
                urljoin(self.base_url, self.endpoints["book_appointment"]),
                data=booking_data,
                headers=self.auth.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Successfully booked appointment for {details['member_name']}")
                    return True
                else:
                    print(f"   ❌ Booking failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Booking request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error booking appointment: {e}")
            return False
    
    def add_to_group_session(self, details: Dict[str, Any]) -> bool:
        """
        Add a member to an existing group session using API.
        
        Args:
            details: Dictionary containing session details:
                - member_name_to_add: Name of member to add
                - session_time_str: Time of session (e.g., "10:30 AM")
                - session_day_xpath_part: Date of session (e.g., "2025-01-15")
                - target_schedule_name: Schedule name
                - event_type: Type of session (e.g., "Group Training")
                
        Returns:
            bool: True if member added successfully
        """
        print(f"📅 API: Adding '{details['member_name_to_add']}' to group session...")
        
        try:
            # Step 1: Find member
            member_info = self._find_member(details['member_name_to_add'])
            if not member_info:
                print(f"   ❌ Member '{details['member_name_to_add']}' not found")
                return False
            
            # Step 2: Find existing session
            session_info = self._find_existing_session(
                details['session_day_xpath_part'],
                details['session_time_str'],
                details.get('event_type', 'Group Training'),
                details['target_schedule_name']
            )
            
            if not session_info:
                print(f"   ❌ Could not find matching session")
                return False
            
            # Step 3: Add member to session
            add_data = {
                "session_id": session_info['id'],
                "member_id": member_info['id'],
                "member_name": details['member_name_to_add']
            }
            
            response = self.session.post(
                urljoin(self.base_url, self.endpoints["add_participant"]),
                data=add_data,
                headers=self.auth.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Successfully added {details['member_name_to_add']} to group session")
                    return True
                else:
                    print(f"   ❌ Failed to add member: {result.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"   ❌ Add participant request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error adding member to session: {e}")
            return False
    
    def get_available_slots(self, schedule_name: str = "My schedule") -> List[str]:
        """
        Get available time slots for a schedule.
        
        Args:
            schedule_name: Name of the schedule
            
        Returns:
            List of available time slots
        """
        print(f"📅 API: Getting available slots for '{schedule_name}'...")
        
        try:
            # Get calendar data
            calendar_data = self.get_calendar_view_details(schedule_name)
            
            available_slots = []
            for day, slots in calendar_data.items():
                for slot in slots:
                    if slot.get('status') == 'Available':
                        available_slots.append(slot.get('time'))
            
            print(f"   ✅ Found {len(available_slots)} available slots")
            return available_slots
            
        except Exception as e:
            print(f"   ❌ Error getting available slots: {e}")
            return []
    
    def get_available_times_for_today(self) -> list:
        """
        Fetch all available time slots for today using /api/calendar/events.
        Returns a list of available time slots (dicts with time and details).
        """
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 Fetching available times for today ({today}) via /api/calendar/events...")
        # Debug: Show headers and token
        headers = self.auth.get_headers()
        print(f"[DEBUG] Authorization header: {headers.get('Authorization')}")
        print(f"[DEBUG] Cookies: {headers.get('Cookie')}")
        if not headers.get('Authorization'):
            print("[WARNING] No Bearer token found in headers! API may reject the request.")
        try:
            params = {"date": today}
            url = self.base_url + "/api/calendar/events"
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response text: {response.text[:500]}")
            if response.status_code == 200:
                events = response.json()
                available = [e for e in events if e.get('status', '').lower() == 'available']
                print(f"   ✅ Found {len(available)} available slots for today.")
                return available
            else:
                print(f"   ❌ Failed to fetch events: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
        except Exception as e:
            print(f"   ❌ Error fetching available times: {e}")
            return []
    
    # Helper methods
    def _get_calendar_state(self) -> Optional[Dict[str, Any]]:
        """Get current calendar state"""
        try:
            response = self.session.get(
                urljoin(self.base_url, self.endpoints["calendar"]),
                headers=self.auth.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                # Extract calendar state from HTML or JSON response
                return self._extract_calendar_state(response.text)
            return None
            
        except Exception as e:
            print(f"   ❌ Error getting calendar state: {e}")
            return None
    
    def _get_available_schedules(self) -> List[Dict[str, Any]]:
        """Get list of available schedules"""
        try:
            response = self.session.get(
                urljoin(self.base_url, self.endpoints["schedule_views"]),
                headers=self.auth.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('schedules', [])
            else:
                print(f"[DEBUG] Failed to fetch schedules: status {response.status_code}")
                print(f"[DEBUG] Response text: {response.text}")
            return []
            
        except Exception as e:
            print(f"   ❌ Error getting schedules: {e}")
            return []
    
    def _get_calendar_data(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get calendar data for a specific schedule"""
        try:
            response = self.session.get(
                urljoin(self.base_url, self.endpoints["calendar_data"]),
                params={"schedule_id": schedule_id},
                headers=self.auth.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"   ❌ Error getting calendar data: {e}")
            return None
    
    def _get_available_slots(self, schedule_name: str, date: str) -> List[Dict[str, Any]]:
        """Get available slots for a specific date"""
        try:
            response = self.session.get(
                urljoin(self.base_url, self.endpoints["available_slots"]),
                params={
                    "schedule_name": schedule_name,
                    "date": date
                },
                headers=self.auth.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('slots', [])
            return []
            
        except Exception as e:
            print(f"   ❌ Error getting available slots: {e}")
            return []
    
    def _find_member(self, member_name: str) -> Optional[Dict[str, Any]]:
        """Find member by name"""
        try:
            # Use existing member search functionality
            from services.api.enhanced_clubos_service import ClubOSAPIService
            service = ClubOSAPIService(self.api_client.username, self.api_client.password)
            return service._api_search_member(member_name)
            
        except Exception as e:
            print(f"   ❌ Error finding member: {e}")
            return None
    
    def _find_existing_session(self, date: str, time: str, event_type: str, schedule_name: str) -> Optional[Dict[str, Any]]:
        """Find existing session by date, time, and type"""
        try:
            # Get calendar data for the schedule
            calendar_data = self.get_calendar_view_details(schedule_name)
            
            # Look for matching session
            for day, slots in calendar_data.items():
                if day == date:
                    for slot in slots:
                        if (slot.get('time') == time and 
                            slot.get('status') == event_type):
                            return {
                                'id': slot.get('session_id'),
                                'date': date,
                                'time': time,
                                'type': event_type
                            }
            return None
            
        except Exception as e:
            print(f"   ❌ Error finding existing session: {e}")
            return None
    
    def _organize_calendar_data(self, calendar_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Organize calendar data by day"""
        organized = {}
        
        try:
            events = calendar_data.get('events', [])
            for event in events:
                date = event.get('date')
                if date not in organized:
                    organized[date] = []
                
                organized[date].append({
                    'time': event.get('time'),
                    'status': event.get('type', 'Booked'),
                    'session_id': event.get('id'),
                    'member_name': event.get('member_name'),
                    'notes': event.get('notes', '')
                })
            
            return organized
            
        except Exception as e:
            print(f"   ❌ Error organizing calendar data: {e}")
            return {}
    
    def _extract_calendar_state(self, html_content: str) -> Dict[str, Any]:
        """Extract calendar state from HTML content"""
        try:
            # Extract current date and view type from HTML
            import re
            
            # Look for current date
            date_match = re.search(r'data-current-date="([^"]+)"', html_content)
            current_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
            
            # Look for view type
            view_match = re.search(r'data-view-type="([^"]+)"', html_content)
            view_type = view_match.group(1) if view_match else "week"
            
            return {
                "current_date": current_date,
                "view_type": view_type
            }
            
        except Exception as e:
            print(f"   ❌ Error extracting calendar state: {e}")
            return {
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "view_type": "week"
            }


# Convenience functions for backward compatibility
def navigate_calendar_week_api(username: str, password: str, direction: str = 'next') -> bool:
    """API version of navigate_calendar_week"""
    try:
        service = ClubOSCalendarAPIService(username, password)
        return service.navigate_calendar_week(direction)
    except Exception as e:
        print(f"❌ Error in navigate_calendar_week_api: {e}")
        return False


def get_calendar_view_details_api(username: str, password: str, schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
    """API version of get_calendar_view_details"""
    try:
        service = ClubOSCalendarAPIService(username, password)
        return service.get_calendar_view_details(schedule_name)
    except Exception as e:
        print(f"❌ Error in get_calendar_view_details_api: {e}")
        return {}


def book_appointment_api(username: str, password: str, details: Dict[str, Any]) -> bool:
    """API version of book_appointment"""
    try:
        service = ClubOSCalendarAPIService(username, password)
        return service.book_appointment(details)
    except Exception as e:
        print(f"❌ Error in book_appointment_api: {e}")
        return False


def add_to_group_session_api(username: str, password: str, details: Dict[str, Any]) -> bool:
    """API version of add_to_group_session"""
    try:
        service = ClubOSCalendarAPIService(username, password)
        return service.add_to_group_session(details)
    except Exception as e:
        print(f"❌ Error in add_to_group_session_api: {e}")
        return False


def get_available_slots_api(username: str, password: str, schedule_name: str = "My schedule") -> List[str]:
    """API version of get_available_slots"""
    try:
        service = ClubOSCalendarAPIService(username, password)
        return service.get_available_slots(schedule_name)
    except Exception as e:
        print(f"❌ Error in get_available_slots_api: {e}")
        return []