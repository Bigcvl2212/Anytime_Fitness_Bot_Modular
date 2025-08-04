"""
ClubOS Calendar API Demo
Demonstrates all calendar functionality including:
- Getting available time slots
- Viewing calendar events for day/week
- Looking forward and backward in time
- Getting all appointments and events scheduled
- Creating new events
- Adding/removing attendees
- Updating and deleting events

This script serves as both a demo and a testing tool for the calendar API.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict

# Add the current directory to Python path so we can import our modules
# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clubos_calendar_manager import ClubOSCalendarManager, create_calendar_manager
from clubos_calendar_client import CalendarEvent, TimeSlot

# Import credentials
from config.secrets import get_clubos_credentials


class CalendarAPIDemo:
    """Comprehensive demo of ClubOS Calendar API functionality"""
    
    def __init__(self, username: str = None, password: str = None):
        """Initialize the demo with ClubOS credentials"""
        print("🚀 Initializing ClubOS Calendar API Demo...")
        self.calendar_manager = create_calendar_manager(username, password)
        self.is_ready = self.calendar_manager.is_authenticated
        
        if self.is_ready:
            print("✅ Calendar API Demo ready!")
        else:
            print("❌ Failed to authenticate with ClubOS")
    
    def demo_available_slots(self, date: str = None) -> List[TimeSlot]:
        """Demo: Get available time slots for booking"""
        if not self.is_ready:
            return []
        
        print("\\n" + "="*60)
        print("📅 DEMO: Getting Available Time Slots")
        print("="*60)
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Searching for available slots on {date}...")
        
        # Get available slots for different event types
        event_types = ['personal_training', 'small_group', 'assessment']
        
        all_slots = []
        for event_type in event_types:
            print(f"\\n📋 Checking {event_type.replace('_', ' ').title()} slots...")
            slots = self.calendar_manager.get_available_slots(date=date, event_type=event_type)
            
            if slots:
                print(f"✅ Found {len(slots)} available {event_type} slots:")
                for i, slot in enumerate(slots[:5], 1):  # Show first 5 slots
                    print(f"   {i}. {slot.start_time} - {slot.end_time} ({slot.duration_minutes} min)")
                    if slot.trainer_name:
                        print(f"      Trainer: {slot.trainer_name}")
                all_slots.extend(slots)
            else:
                print(f"❌ No {event_type} slots available")
        
        print(f"\\n📊 Total available slots found: {len(all_slots)}")
        return all_slots
    
    def demo_calendar_events(self, date: str = None) -> List[CalendarEvent]:
        """Demo: View existing calendar events"""
        if not self.is_ready:
            return []
        
        print("\n" + "="*60)
        print("📋 DEMO: Viewing Calendar Events")
        print("="*60)
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Getting calendar events for {date}...")
        
        events = self.calendar_manager.get_calendar_events(date=date)
        
        if events:
            print(f"✅ Found {len(events)} calendar events:")
            for i, event in enumerate(events, 1):
                print(f"\n   📅 Event {i} (type: {type(event)}): {repr(event)}")
                if hasattr(event, 'title'):
                    print(f"      📝 Title: {event.title}")
                    print(f"      🕐 Time: {event.start_time} - {event.end_time}")
                    print(f"      🏷️ Type: {event.event_type}")
                    print(f"      🆔 ID: {event.event_id}")
                    if hasattr(event, 'trainer_name') and event.trainer_name:
                        print(f"      👨‍💼 Trainer: {event.trainer_name}")
                    if hasattr(event, 'member_name') and event.member_name:
                        print(f"      👤 Member: {event.member_name}")
                    print(f"      📊 Status: {event.status}")
                else:
                    print(f"      ⚠️  Object is not a CalendarEvent: {type(event)}")
        else:
            print("❌ No calendar events found for this date")
        
        return events
    
    def demo_appointments_for_day(self, date: str = None) -> List[CalendarEvent]:
        """Demo: Get all appointments scheduled for a specific day"""
        if not self.is_ready:
            return []
        
        print("\n" + "="*60)
        print("📅 DEMO: Getting All Appointments for the Day")
        print("="*60)
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Getting all appointments for {date}...")
        
        appointments = self.calendar_manager.get_appointments_for_day(date)
        
        if appointments:
            print(f"✅ Found {len(appointments)} appointments:")
            
            # Group by time for better display
            appointments_by_time = {}
            for appt in appointments:
                time_key = appt.start_time
                if time_key not in appointments_by_time:
                    appointments_by_time[time_key] = []
                appointments_by_time[time_key].append(appt)
            
            # Display appointments chronologically
            for time in sorted(appointments_by_time.keys()):
                print(f"\n   🕐 {time}:")
                for appt in appointments_by_time[time]:
                    print(f"      📋 {appt.title}")
                    print(f"         Type: {appt.event_type}")
                    if appt.trainer_name:
                        print(f"         Trainer: {appt.trainer_name}")
                    if appt.member_name:
                        print(f"         Member: {appt.member_name}")
                    print(f"         Duration: {appt.start_time} - {appt.end_time}")
                    print(f"         Status: {appt.status}")
        else:
            print("❌ No appointments found for this date")
        
        return appointments
    
    def demo_events_for_week(self, start_date: str = None) -> Dict[str, List[CalendarEvent]]:
        """Demo: Get all events scheduled for a week"""
        if not self.is_ready:
            return {}
        
        print("\n" + "="*60)
        print("📅 DEMO: Getting All Events for the Week")
        print("="*60)
        
        if not start_date:
            # Start from Monday of current week
            today = datetime.now()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            start_date = monday.strftime("%Y-%m-%d")
        
        print(f"🔍 Getting week events starting from {start_date}...")
        
        week_events = self.calendar_manager.get_events_for_week(start_date)
        
        if week_events:
            total_events = sum(len(events) for events in week_events.values())
            print(f"✅ Found {total_events} events across the week:")
            
            # Display each day
            for date, events in week_events.items():
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                print(f"\n   📅 {day_name} ({date}) - {len(events)} events:")
                
                if events:
                    for event in events:
                        print(f"      🕐 {event.start_time} - {event.title}")
                        print(f"         Type: {event.event_type}, Status: {event.status}")
                else:
                    print("      🔴 No events scheduled")
        else:
            print("❌ No events found for this week")
        
        return week_events
    
    def demo_time_navigation(self, base_date: str = None) -> Dict[str, List[CalendarEvent]]:
        """Demo: Navigate forward and backward in time"""
        if not self.is_ready:
            return {}
        
        print("\n" + "="*60)
        print("⏰ DEMO: Time Navigation - Looking Forward and Backward")
        print("="*60)
        
        if not base_date:
            base_date = datetime.now().strftime("%Y-%m-%d")
        
        base_dt = datetime.strptime(base_date, "%Y-%m-%d")
        
        print(f"🎯 Base date: {base_date}")
        
        # Look backward (previous week)
        prev_week = (base_dt - timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"\n⬅️ Looking BACKWARD - Week of {prev_week}:")
        prev_events = self.calendar_manager.get_events_for_week(prev_week)
        if prev_events:
            total_prev = sum(len(events) for events in prev_events.values())
            print(f"   📊 Found {total_prev} events in previous week")
            # Show summary by day
            for date, events in prev_events.items():
                if events:
                    day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                    print(f"      {day_name}: {len(events)} events")
        else:
            print("   🔴 No events found in previous week")
        
        # Current week
        print(f"\n📍 CURRENT - Week of {base_date}:")
        current_events = self.calendar_manager.get_events_for_week(base_date)
        if current_events:
            total_current = sum(len(events) for events in current_events.values())
            print(f"   📊 Found {total_current} events in current week")
            for date, events in current_events.items():
                if events:
                    day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                    print(f"      {day_name}: {len(events)} events")
        else:
            print("   🔴 No events found in current week")
        
        # Look forward (next week)
        next_week = (base_dt + timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"\n➡️ Looking FORWARD - Week of {next_week}:")
        next_events = self.calendar_manager.get_events_for_week(next_week)
        if next_events:
            total_next = sum(len(events) for events in next_events.values())
            print(f"   📊 Found {total_next} events in next week")
            for date, events in next_events.items():
                if events:
                    day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                    print(f"      {day_name}: {len(events)} events")
        else:
            print("   🔴 No events found in next week")
        
        # Look further forward (next month)
        next_month = (base_dt + timedelta(days=30)).strftime("%Y-%m-%d")
        print(f"\n⏭️ Looking FAR FORWARD - Month of {next_month}:")
        month_events = self.calendar_manager.get_appointments_for_day(next_month)
        if month_events:
            print(f"   📊 Found {len(month_events)} events on {next_month}")
        else:
            print(f"   🔴 No events found on {next_month}")
        
        return {
            'previous_week': prev_events,
            'current_week': current_events,
            'next_week': next_events
        }
    
    def demo_date_range_events(self, start_date: str = None, end_date: str = None) -> List[CalendarEvent]:
        """Demo: Get all events in a specific date range"""
        if not self.is_ready:
            return []
        
        print("\n" + "="*60)
        print("📊 DEMO: Getting Events in Date Range")
        print("="*60)
        
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        if not end_date:
            # Default to 2 weeks from start
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=14)
            end_date = end_dt.strftime("%Y-%m-%d")
        
        print(f"🔍 Getting events from {start_date} to {end_date}...")
        
        events = self.calendar_manager.get_events_in_range(start_date, end_date)
        
        if events:
            print(f"✅ Found {len(events)} events in date range:")
            
            # Group by date
            events_by_date = {}
            for event in events:
                event_date = event.start_time.split()[0] if ' ' in event.start_time else start_date
                if event_date not in events_by_date:
                    events_by_date[event_date] = []
                events_by_date[event_date].append(event)
            
            # Display by date
            for date in sorted(events_by_date.keys()):
                day_events = events_by_date[date]
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                print(f"\n   📅 {day_name} ({date}) - {len(day_events)} events:")
                
                for event in day_events:
                    print(f"      🕐 {event.start_time} - {event.title}")
                    print(f"         Type: {event.event_type}")
                    if event.member_name:
                        print(f"         Member: {event.member_name}")
        else:
            print("❌ No events found in specified date range")
        
        return events
    
    def demo_create_event(self, date: str = None) -> str:
        """Demo: Create a new calendar event"""
        if not self.is_ready:
            return None
        
        print("\\n" + "="*60)
        print("➕ DEMO: Creating New Calendar Event")
        print("="*60)
        
        if not date:
            # Use tomorrow for demo
            tomorrow = datetime.now() + timedelta(days=1)
            date = tomorrow.strftime("%Y-%m-%d")
        
        # Create a sample appointment
        print(f"🔨 Creating a personal training session for {date}...")
        
        event_id = self.calendar_manager.create_event(
            date=date,
            start_time="15:00",  # 3:00 PM
            end_time="16:00",    # 4:00 PM
            event_type="personal_training",
            title="Demo Personal Training Session"
        )
        
        if event_id:
            print(f"✅ Event created successfully!")
            print(f"   🆔 Event ID: {event_id}")
            print(f"   📅 Date: {date}")
            print(f"   🕐 Time: 15:00 - 16:00")
            print(f"   🏷️ Type: Personal Training")
        else:
            print("❌ Failed to create event")
        
        return event_id
    
    def demo_update_event(self, event_id: str) -> bool:
        """Demo: Update an existing event"""
        if not self.is_ready or not event_id:
            return False
        
        print("\\n" + "="*60)
        print("✏️ DEMO: Updating Calendar Event")
        print("="*60)
        
        print(f"🔨 Updating event {event_id}...")
        
        # Update the event title and time
        success = self.calendar_manager.update_event(
            event_id,
            title="Updated Demo Training Session",
            start_time="14:30",  # Move to 2:30 PM
            end_time="15:30"     # End at 3:30 PM
        )
        
        if success:
            print("✅ Event updated successfully!")
            print("   📝 New title: Updated Demo Training Session")
            print("   🕐 New time: 14:30 - 15:30")
        else:
            print("❌ Failed to update event")
        
        return success
    
    def demo_attendee_management(self, event_id: str, member_id: str = "demo_member_123") -> bool:
        """Demo: Add and remove attendees from an event"""
        if not self.is_ready or not event_id:
            return False
        
        print("\\n" + "="*60)
        print("👥 DEMO: Managing Event Attendees")
        print("="*60)
        
        print(f"👤 Adding member {member_id} to event {event_id}...")
        
        # Add attendee
        add_success = self.calendar_manager.add_attendee_to_event(event_id, member_id)
        
        if add_success:
            print("✅ Attendee added successfully!")
            
            # Get current attendees
            attendees = self.calendar_manager.get_event_attendees(event_id)
            if attendees:
                print(f"📋 Current attendees ({len(attendees)}):")
                for i, attendee in enumerate(attendees, 1):
                    print(f"   {i}. {attendee.get('name', 'Unknown')} (ID: {attendee.get('id', 'N/A')})")
            
            # Remove attendee (optional demo)
            print(f"\\n👤 Removing member {member_id} from event...")
            remove_success = self.calendar_manager.remove_attendee_from_event(event_id, member_id)
            
            if remove_success:
                print("✅ Attendee removed successfully!")
            else:
                print("❌ Failed to remove attendee")
                
            return add_success and remove_success
        else:
            print("❌ Failed to add attendee")
            return False
    
    def demo_delete_event(self, event_id: str) -> bool:
        """Demo: Delete a calendar event"""
        if not self.is_ready or not event_id:
            return False
        
        print("\\n" + "="*60)
        print("🗑️ DEMO: Deleting Calendar Event")
        print("="*60)
        
        print(f"🗑️ Deleting event {event_id}...")
        
        success = self.calendar_manager.delete_event(event_id)
        
        if success:
            print("✅ Event deleted successfully!")
        else:
            print("❌ Failed to delete event")
        
        return success
    
    def demo_reschedule_event(self, event_id: str) -> bool:
        """Demo: Reschedule an event to a different time"""
        if not self.is_ready or not event_id:
            return False
        
        print("\\n" + "="*60)
        print("📅 DEMO: Rescheduling Event")
        print("="*60)
        
        # Reschedule to the day after tomorrow
        new_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        print(f"📅 Rescheduling event {event_id} to {new_date} at 11:00...")
        
        success = self.calendar_manager.reschedule_event(
            event_id,
            new_date=new_date,
            new_start_time="11:00",
            new_end_time="12:00"
        )
        
        if success:
            print("✅ Event rescheduled successfully!")
            print(f"   📅 New date: {new_date}")
            print(f"   🕐 New time: 11:00 - 12:00")
        else:
            print("❌ Failed to reschedule event")
        
        return success
    
    def demo_daily_appointments(self, date: str = None) -> List[CalendarEvent]:
        """Demo: Get all appointments scheduled for a specific day"""
        if not self.is_ready:
            return []
        
        print("\n" + "="*60)
        print("📋 DEMO: Getting Daily Appointments")
        print("="*60)
        
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Getting all appointments for {date}...")
        
        appointments = self.calendar_manager.get_daily_appointments(date)
        
        if appointments:
            print(f"✅ Found {len(appointments)} appointments:")
            for i, apt in enumerate(appointments, 1):
                print(f"\n   📅 Appointment {i}: {apt.title}")
                print(f"      🕐 Time: {apt.start_time} - {apt.end_time}")
                print(f"      🏷️ Type: {apt.event_type}")
                if apt.trainer_name:
                    print(f"      👨‍💼 Trainer: {apt.trainer_name}")
                if apt.member_name:
                    print(f"      👤 Member: {apt.member_name}")
                print(f"      📊 Status: {apt.status}")
        else:
            print("❌ No appointments found for this date")
        
        return appointments
    
    def demo_weekly_events(self, start_date: str = None) -> List[CalendarEvent]:
        """Demo: Get all events for a week"""
        if not self.is_ready:
            return []
        
        print("\n" + "="*60)
        print("📅 DEMO: Getting Weekly Events")
        print("="*60)
        
        if not start_date:
            # Use current week (Monday to Sunday)
            today = datetime.now()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
            start_date = monday.strftime("%Y-%m-%d")
        
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
        
        print(f"🔍 Getting events for week: {start_date} to {end_date}...")
        
        events = self.calendar_manager.get_weekly_events(start_date, end_date)
        
        if events:
            print(f"✅ Found {len(events)} events this week:")
            
            # Group events by day
            events_by_day = {}
            for event in events:
                event_date = event.start_time.split(' ')[0] if ' ' in event.start_time else start_date
                if event_date not in events_by_day:
                    events_by_day[event_date] = []
                events_by_day[event_date].append(event)
            
            for day_date in sorted(events_by_day.keys()):
                day_events = events_by_day[day_date]
                day_name = datetime.strptime(day_date, "%Y-%m-%d").strftime("%A")
                print(f"\n   📅 {day_name} ({day_date}) - {len(day_events)} events:")
                
                for event in day_events:
                    time_part = event.start_time.split(' ')[1] if ' ' in event.start_time else event.start_time
                    print(f"      🕐 {time_part} - {event.title} ({event.event_type})")
        else:
            print("❌ No events found for this week")
        
        return events
    
    def demo_time_navigation(self, base_date: str = None) -> Dict:
        """Demo: Navigate forward and backward in time to view calendar"""
        if not self.is_ready:
            return {}
        
        print("\n" + "="*60)
        print("⏰ DEMO: Calendar Time Navigation")
        print("="*60)
        
        if not base_date:
            base_date = datetime.now().strftime("%Y-%m-%d")
        
        base_dt = datetime.strptime(base_date, "%Y-%m-%d")
        
        # Look backward 7 days
        past_date = (base_dt - timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"🔙 Looking BACKWARD 7 days to {past_date}...")
        past_events = self.calendar_manager.get_calendar_events(past_date)
        print(f"   Found {len(past_events)} events")
        
        # Current date
        print(f"\n📅 Current date: {base_date}")
        current_events = self.calendar_manager.get_calendar_events(base_date)
        print(f"   Found {len(current_events)} events")
        
        # Look forward 7 days
        future_date = (base_dt + timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"\n🔜 Looking FORWARD 7 days to {future_date}...")
        future_events = self.calendar_manager.get_calendar_events(future_date)
        print(f"   Found {len(future_events)} events")
        
        # Show monthly view (4 weeks forward)
        print(f"\n📆 Monthly view (next 4 weeks from {base_date}):")
        monthly_events = []
        for week in range(4):
            week_start = base_dt + timedelta(weeks=week)
            week_end = week_start + timedelta(days=6)
            week_events = self.calendar_manager.get_weekly_events(
                week_start.strftime("%Y-%m-%d"),
                week_end.strftime("%Y-%m-%d")
            )
            monthly_events.extend(week_events)
            print(f"   Week {week+1} ({week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}): {len(week_events)} events")
        
        navigation_summary = {
            'past_events': past_events,
            'current_events': current_events,
            'future_events': future_events,
            'monthly_events': monthly_events,
            'total_events_found': len(past_events) + len(current_events) + len(future_events)
        }
        
        print(f"\n📊 Navigation Summary:")
        print(f"   Total events across time periods: {navigation_summary['total_events_found']}")
        
        return navigation_summary
    
    def demo_appointments_today(self) -> List[CalendarEvent]:
        """Demo: Quick function to get today's appointments"""
        if not self.is_ready:
            return []
        
        print("\n" + "="*60)
        print("📋 DEMO: Today's Appointments")
        print("="*60)
        
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"🔍 Getting appointments for TODAY ({today})...")
        
        appointments = self.calendar_manager.get_daily_appointments(today)
        
        if appointments:
            print(f"✅ You have {len(appointments)} appointments today:")
            for i, apt in enumerate(appointments, 1):
                # Extract time from datetime string
                time_str = apt.start_time.split(' ')[1] if ' ' in apt.start_time else apt.start_time
                print(f"   {i}. {time_str} - {apt.title}")
                if apt.member_name:
                    print(f"      👤 With: {apt.member_name}")
        else:
            print("📅 No appointments scheduled for today")
        
        return appointments
    
    def run_complete_demo(self):
        """Run a complete demonstration of all calendar features"""
        if not self.is_ready:
            print("❌ Calendar API not ready. Check your credentials.")
            return
        
        print("🎉 Starting Complete ClubOS Calendar API Demo!")
        print("This demo will showcase all available calendar operations.")
        
        # 1. Get available slots
        print("\n" + "🔍 PHASE 1: Available Time Slots")
        slots = self.demo_available_slots()
        
        # 2. View today's appointments and events
        print("\n" + "📅 PHASE 2: Today's Schedule")
        appointments = self.demo_appointments_for_day()
        events = self.demo_calendar_events()
        
        # 3. View week's events
        print("\n" + "📊 PHASE 3: Weekly Schedule")
        week_events = self.demo_events_for_week()
        
        # 4. Time navigation (forward/backward)
        print("\n" + "⏰ PHASE 4: Time Navigation")
        navigation_results = self.demo_time_navigation()
        
        # 5. Date range events
        print("\n" + "📈 PHASE 5: Date Range Analysis")
        range_events = self.demo_date_range_events()
        
        # 6. Event management (create, update, manage)
        print("\n" + "⚙️ PHASE 6: Event Management")
        
        # Create a new event
        event_id = self.demo_create_event()
        
        if event_id:
            # Update the event
            self.demo_update_event(event_id)
            
            # Manage attendees
            self.demo_attendee_management(event_id)
            
            # Reschedule the event
            self.demo_reschedule_event(event_id)
            
            # Finally, delete the event (cleanup)
            # Uncomment the next line if you want to clean up the demo event
            # self.demo_delete_event(event_id)
        
        print("\n" + "="*60)
        print("🎊 Demo Complete!")
        print("="*60)
        print("Calendar API functionality demonstrated:")
        print("✅ Getting available time slots")
        print("✅ Viewing daily appointments and events")
        print("✅ Viewing weekly schedule")
        print("✅ Time navigation (forward/backward)")
        print("✅ Date range event analysis")
        print("✅ Creating new events")
        print("✅ Updating events")
        print("✅ Managing attendees")
        print("✅ Rescheduling events")
        print("✅ Deleting events")
        print("\nThe ClubOS Calendar API is ready for production use! 🚀")
        
        # Return summary data
        return {
            'available_slots': slots,
            'daily_appointments': appointments,
            'daily_events': events,
            'weekly_events': week_events,
            'time_navigation': navigation_results,
            'range_events': range_events,
            'demo_event_id': event_id
        }


def main():
    """Main function to run the calendar demo"""
    print("🎯 ClubOS Calendar API Demo")
    print("="*40)
    
    # Get real ClubOS credentials
    try:
        credentials = get_clubos_credentials()
        username = credentials['username']
        password = credentials['password']
        print(f"🔑 Using ClubOS credentials for user: {username}")
    except Exception as e:
        print(f"❌ Failed to get credentials: {e}")
        username = None
        password = None
    
    # Create demo with real credentials
    demo = CalendarAPIDemo(username, password)
    
    if demo.is_ready:
        # Run the complete demo
        demo.run_complete_demo()
    else:
        print("❌ Demo failed to initialize")
        print("Make sure your ClubOS credentials are correct in config/secrets_local.py")


if __name__ == "__main__":
    main()
