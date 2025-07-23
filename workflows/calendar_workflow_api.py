#!/usr/bin/env python3
"""
Calendar Workflow API - API-based calendar management
Replaces Selenium-based calendar workflow with direct API calls.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from services.api.calendar_api_service import ClubOSCalendarAPIService
from config.constants import CLUBOS_CALENDAR_URL, CLUBOS_USERNAME_SECRET, CLUBOS_PASSWORD_SECRET
from config.secrets import get_secret

class CalendarWorkflowAPI:
    """
    API-based calendar workflow that replaces Selenium calendar operations.
    Handles calendar navigation, session booking, and appointment management.
    """
    def __init__(self):
        # Initialize calendar workflow with API authentication
        username = get_secret(CLUBOS_USERNAME_SECRET)
        password = get_secret(CLUBOS_PASSWORD_SECRET)
        if not username or not password:
            raise Exception("ClubOS credentials not available")
        self.calendar_service = ClubOSCalendarAPIService(username, password)
        print("✅ Calendar API service initialized")

    def navigate_calendar_week(self, direction: str = 'next') -> bool:
        """
        Navigate calendar forward or backward by one week.
        Args:
            direction: 'next' or 'previous'
        Returns:
            bool: True if navigation successful
        """
        print(f"📅 CALENDAR NAVIGATION: {direction.upper()}")
        print("=" * 40)
        try:
            success = self.calendar_service.navigate_calendar_week(direction)
            if success:
                print(f"✅ Successfully navigated calendar {direction}")
            else:
                print(f"❌ Failed to navigate calendar {direction}")
            return success
        except Exception as e:
            print(f"❌ Error in calendar navigation: {e}")
            return False

    def get_calendar_view_details(self, schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
        """
        Get detailed calendar view with available slots and booked sessions.
        Args:
            schedule_name: Name of the schedule to view
        Returns:
            Dict with calendar data organized by day
        """
        print(f"📅 CALENDAR VIEW: {schedule_name.upper()}")
        print("=" * 40)
        try:
            calendar_data = self.calendar_service.get_calendar_view_details(schedule_name)
            if calendar_data:
                print(f"✅ Retrieved calendar data for {len(calendar_data)} days")
                for day, slots in calendar_data.items():
                    available_count = sum(1 for slot in slots if slot.get('status') == 'Available')
                    booked_count = len(slots) - available_count
                    print(f"   📅 {day}: {available_count} available, {booked_count} booked")
            else:
                print("❌ No calendar data retrieved")
            return calendar_data
        except Exception as e:
            print(f"❌ Error getting calendar view: {e}")
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
        print(f"📅 BOOKING APPOINTMENT")
        print("=" * 30)
        print(f"   Member: {details.get('member_name')}")
        print(f"   Date: {details.get('date', 'N/A')}")
        print(f"   Time: {details.get('time', 'N/A')}")
        print(f"   Type: {details.get('event_type', 'N/A')}")
        try:
            success = self.calendar_service.book_appointment(details)
            if success:
                print("✅ Appointment booked successfully")
            else:
                print("❌ Failed to book appointment")
            return success
        except Exception as e:
            print(f"❌ Error booking appointment: {e}")
            return False

    def add_to_group_session(self, details: Dict[str, Any]) -> bool:
        """
        Add a member to an existing group session.
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
        print(f"📅 ADDING TO GROUP SESSION")
        print("=" * 35)
        print(f"   Member: {details.get('member_name_to_add')}")
        print(f"   Date: {details.get('session_day_xpath_part', 'N/A')}")
        print(f"   Time: {details.get('session_time_str', 'N/A')}")
        print(f"   Schedule: {details.get('target_schedule_name', 'N/A')}")
        try:
            success = self.calendar_service.add_to_group_session(details)
            if success:
                print("✅ Member added to group session successfully")
            else:
                print("❌ Failed to add member to group session")
            return success
        except Exception as e:
            print(f"❌ Error adding to group session: {e}")
            return False

    def get_available_slots(self, schedule_name: str = "My schedule") -> List[str]:
        """
        Get available time slots for a schedule.
        Args:
            schedule_name: Name of the schedule
        Returns:
            List of available time slots
        """
        print(f"📅 GETTING AVAILABLE SLOTS: {schedule_name.upper()}")
        print("=" * 45)
        try:
            available_slots = self.calendar_service.get_available_slots(schedule_name)
            if available_slots:
                print(f"✅ Found {len(available_slots)} available slots:")
                for slot in available_slots[:10]:  # Show first 10
                    print(f"   ⏰ {slot}")
                if len(available_slots) > 10:
                    print(f"   ... and {len(available_slots) - 10} more")
            else:
                print("❌ No available slots found")
            return available_slots
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []

    def comprehensive_calendar_workflow(self, schedule_name: str = "My schedule") -> Dict[str, Any]:
        """
        Run comprehensive calendar workflow including navigation, view details, and available slots.
        Args:
            schedule_name: Name of the schedule to analyze
        Returns:
            Dict with comprehensive calendar information
        """
        print("📅 COMPREHENSIVE CALENDAR WORKFLOW")
        print("=" * 50)
        workflow_results = {
            "schedule_name": schedule_name,
            "available_slots": [],
            "calendar_data": {},
            "navigation_success": False,
            "errors": []
        }
        try:
            # Step 1: Get calendar view details
            print("🔄 Step 1: Getting calendar view details...")
            calendar_data = self.get_calendar_view_details(schedule_name)
            workflow_results["calendar_data"] = calendar_data
            # Step 2: Get available slots
            print("🔄 Step 2: Getting available slots...")
            available_slots = self.get_available_slots(schedule_name)
            workflow_results["available_slots"] = available_slots
            # Step 3: Test navigation
            print("🔄 Step 3: Testing calendar navigation...")
            nav_success = self.navigate_calendar_week('next')
            workflow_results["navigation_success"] = nav_success
            # Navigate back
            if nav_success:
                self.navigate_calendar_week('previous')
            print("✅ Comprehensive calendar workflow completed")
            return workflow_results
        except Exception as e:
            error_msg = f"Error in comprehensive calendar workflow: {e}"
            print(f"❌ {error_msg}")
            workflow_results["errors"].append(error_msg)
            return workflow_results

# Convenience functions for backward compatibility
def navigate_calendar_week_api(direction: str = 'next') -> bool:
    """API version of navigate_calendar_week"""
    try:
        workflow = CalendarWorkflowAPI()
        return workflow.navigate_calendar_week(direction)
    except Exception as e:
        print(f"❌ Error in navigate_calendar_week_api: {e}")
        return False

def get_calendar_view_details_api(schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
    """API version of get_calendar_view_details"""
    try:
        workflow = CalendarWorkflowAPI()
        return workflow.get_calendar_view_details(schedule_name)
    except Exception as e:
        print(f"❌ Error in get_calendar_view_details_api: {e}")
        return {}

def book_appointment_api(details: Dict[str, Any]) -> bool:
    """API version of book_appointment"""
    try:
        workflow = CalendarWorkflowAPI()
        return workflow.book_appointment(details)
    except Exception as e:
        print(f"❌ Error in book_appointment_api: {e}")
        return False

def add_to_group_session_api(details: Dict[str, Any]) -> bool:
    """API version of add_to_group_session"""
    try:
        workflow = CalendarWorkflowAPI()
        return workflow.add_to_group_session(details)
    except Exception as e:
        print(f"❌ Error in add_to_group_session_api: {e}")
        return False

def get_available_slots_api(schedule_name: str = "My schedule") -> List[str]:
    """API version of get_available_slots"""
    try:
        workflow = CalendarWorkflowAPI()
        return workflow.get_available_slots(schedule_name)
    except Exception as e:
        print(f"❌ Error in get_available_slots_api: {e}")
        return []

def run_comprehensive_calendar_workflow(schedule_name: str = "My schedule") -> Dict[str, Any]:
    """Run comprehensive calendar workflow"""
    try:
        workflow = CalendarWorkflowAPI()
        return workflow.comprehensive_calendar_workflow(schedule_name)
    except Exception as e:
        print(f"❌ Error in comprehensive calendar workflow: {e}")
        return {"errors": [str(e)]}

if __name__ == "__main__":
    print("[DEBUG] Entered __main__ block of calendar_workflow_api.py")
    import argparse
    parser = argparse.ArgumentParser(description="API-based calendar workflow CLI")
    parser.add_argument('--today-slots', action='store_true', help='Print all available slots for today (legacy)')
    parser.add_argument('--today-available-times', action='store_true', help='Print all available times for today using /api/calendar/events')
    parser.add_argument('--schedule', type=str, default='My schedule', help='Schedule name (default: My schedule)')
    args = parser.parse_args()

    if args.today_available_times:
        from services.api.calendar_api_service import ClubOSCalendarAPIService
        from config.secrets import get_clubos_credentials
        creds = get_clubos_credentials()
        service = ClubOSCalendarAPIService(creds['username'], creds['password'])
        available = service.get_available_times_for_today()
        print("\nAvailable times for today:")
        if not available:
            print("No available times found.")
        else:
            for slot in available:
                print(f"- {slot.get('time', slot)} | {slot}")
        exit(0)

    if args.today_slots:
        import json
        from datetime import datetime
        har_path = "charles_session.chls/Calendar_Endpoints.har"
        print(f"[DEBUG] Attempting to extract all headers from the most recent /api/calendar/events request in {har_path}...")
        try:
            with open(har_path, "r", encoding="utf-8") as f:
                har_data = json.load(f)
            headers = None
            # Find the last /api/calendar/events request and extract all headers
            for entry in reversed(har_data.get("log", {}).get("entries", [])):
                req = entry.get("request", {})
                url = req.get("url", "")
                if "/api/calendar/events" in url:
                    headers = {h["name"]: h["value"] for h in req.get("headers", [])}
                    break
            if not headers:
                print("❌ No /api/calendar/events request with headers found in HAR file. Cannot authenticate.")
                exit(1)
            print(f"[DEBUG] Using headers: {json.dumps({k: (v[:40]+'...') if len(v)>40 else v for k,v in headers.items()}, indent=2)}")
            today = datetime.now().strftime('%Y-%m-%d')
            import requests
            url = "https://anytime.club-os.com/api/calendar/events"
            # Remove headers that requests will set automatically or that could cause issues
            for h in list(headers.keys()):
                if h.startswith(":") or h in ["Content-Length", "Host"]:
                    headers.pop(h, None)
            response = requests.get(url, params={"date": today}, headers=headers, timeout=15)
            if response.status_code == 200:
                events = response.json()
                available_slots = [e for e in events if e.get('status', '').lower() == 'available']
                print(f"\nAvailable slots for today ({today}):")
                if available_slots:
                    for slot in available_slots:
                        print(f"  - {slot.get('time')} | {slot}")
                else:
                    print("  No available slots for today.")
            else:
                print(f"❌ Failed to fetch events: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error reading HAR file or fetching slots: {e}")
            exit(1)
    else:
        # Default: run the original test workflow
        print("\n🧪 TESTING CALENDAR WORKFLOW API")
        print("=" * 40)
        try:
            workflow = CalendarWorkflowAPI()
            # Test 1: Get calendar view details
            print("\n📅 Test 1: Getting calendar view details...")
            calendar_data = workflow.get_calendar_view_details("My schedule")
            # Test 2: Get available slots
            print("\n📅 Test 2: Getting available slots...")
            available_slots = workflow.get_available_slots("My schedule")
            # Test 3: Test navigation
            print("\n📅 Test 3: Testing navigation...")
            nav_success = workflow.navigate_calendar_week('next')
            if nav_success:
                workflow.navigate_calendar_week('previous')
            print("\n✅ All calendar workflow tests completed!")
        except Exception as e:
            print(f"❌ Calendar workflow test failed: {e}")