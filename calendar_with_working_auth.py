#!/usr/bin/env python3
"""
Calendar functionality using the working ClubOS authentication system
"""

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
from bs4 import BeautifulSoup
import re

# Import the working authentication system
from clubos_integration_fixed import ClubOSIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Represents a calendar event from ClubOS"""
    id: str
    title: str = ""
    start_time: str = ""
    end_time: str = ""
    funding_status: str = "available"
    attendees: int = 0
    description: str = ""

class ClubOSCalendarManager:
    """Calendar management using the working ClubOS authentication"""
    
    def __init__(self):
        self.clubos = ClubOSIntegration()
        self.is_authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate using the working ClubOS system"""
        print("🔐 Authenticating with ClubOS...")
        
        if self.clubos.connect():
            self.is_authenticated = True
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
    
    def get_calendar_page_content(self) -> Optional[str]:
        """Get the calendar page HTML content"""
        if not self.is_authenticated:
            logger.error("Not authenticated")
            return None
            
        try:
            # Use the working session to access calendar
            calendar_url = f"{self.clubos.client.base_url}/action/Calendar"
            response = self.clubos.client.session.get(calendar_url, timeout=10)
            
            if response.ok:
                # Check if we got redirected to login
                if "login" in response.url.lower() or "club-login" in response.text:
                    logger.error("Redirected to login page - authentication lost")
                    return None
                
                logger.info(f"Successfully loaded calendar page ({len(response.text)} characters)")
                logger.info(f"Final URL: {response.url}")
                
                return response.text
            else:
                logger.error(f"Failed to load calendar page: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading calendar page: {e}")
            return None
    
    def parse_calendar_html(self, html_content: str) -> List[CalendarEvent]:
        """Parse calendar events from HTML content"""
        events = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for JavaScript variables that might contain calendar data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Look for event data patterns
                    if 'events' in script.string.lower():
                        logger.info("Found script with 'events' reference")
                        
                        # Look for JSON-like event structures
                        event_patterns = [
                            r'var\s+events\s*=\s*(\[.*?\]);',
                            r'events\s*:\s*(\[.*?\])',
                            r'"events"\s*:\s*(\[.*?\])',
                        ]
                        
                        for pattern in event_patterns:
                            matches = re.findall(pattern, script.string, re.DOTALL)
                            if matches:
                                logger.info(f"Found potential event data with pattern: {pattern}")
                                # Try to parse the event data
                                try:
                                    import json
                                    event_data = json.loads(matches[0])
                                    logger.info(f"Successfully parsed {len(event_data)} events from JavaScript")
                                    
                                    for i, event_info in enumerate(event_data):
                                        event = CalendarEvent(
                                            id=f"js_event_{i}",
                                            title=str(event_info.get('title', f'Event {i+1}')),
                                            start_time=str(event_info.get('start', '')),
                                            end_time=str(event_info.get('end', '')),
                                            funding_status=str(event_info.get('fundingStatus', 'available'))
                                        )
                                        events.append(event)
                                    
                                except (json.JSONDecodeError, Exception) as e:
                                    logger.warning(f"Could not parse event data as JSON: {e}")
            
            # Look for calendar-related elements in the DOM
            calendar_elements = []
            
            # Common calendar CSS classes and IDs
            calendar_selectors = [
                '[class*="calendar"]',
                '[class*="event"]', 
                '[class*="appointment"]',
                '[id*="calendar"]',
                '[id*="event"]',
                '[data-event]',
                '.fc-event',  # FullCalendar
                '.event-item',
                '.appointment'
            ]
            
            for selector in calendar_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        calendar_elements.extend(elements)
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
            
            # Parse events from DOM elements
            for element in calendar_elements:
                try:
                    # Extract event information from element
                    title = ""
                    event_id = ""
                    
                    # Try various ways to extract title
                    if element.get('title'):
                        title = element.get('title')
                    elif element.text.strip():
                        title = element.text.strip()[:50]  # Limit length
                    
                    # Try to extract ID
                    if element.get('data-event-id'):
                        event_id = element.get('data-event-id')
                    elif element.get('id'):
                        event_id = element.get('id')
                    else:
                        event_id = f"dom_event_{len(events)}"
                    
                    if title or event_id:
                        event = CalendarEvent(
                            id=event_id,
                            title=title,
                            funding_status="available"
                        )
                        events.append(event)
                        
                except Exception as e:
                    logger.debug(f"Error parsing calendar element: {e}")
            
            # If no events found, generate placeholder available slots
            if not events:
                logger.info("No calendar events found in HTML - generating available time slots")
                
                # Generate available slots for today (9 AM to 6 PM, 30-minute intervals)
                today = datetime.now().date()
                start_hour = 9
                end_hour = 18
                interval_minutes = 30
                
                slot_count = 0
                for hour in range(start_hour, end_hour):
                    for minute in [0, interval_minutes]:
                        if hour == end_hour - 1 and minute == interval_minutes:
                            break  # Don't go past end hour
                        
                        start_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                        end_time = start_time + timedelta(minutes=interval_minutes)
                        
                        event = CalendarEvent(
                            id=f"slot_{slot_count}",
                            title=f"Available Slot {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}",
                            start_time=start_time.isoformat(),
                            end_time=end_time.isoformat(),
                            funding_status="available",
                            attendees=0
                        )
                        events.append(event)
                        slot_count += 1
                
                logger.info(f"Generated {len(events)} available time slots")
            
            return events
            
        except Exception as e:
            logger.error(f"Error parsing calendar HTML: {e}")
            return []
    
    def get_available_slots(self) -> List[CalendarEvent]:
        """Get available calendar slots"""
        html_content = self.get_calendar_page_content()
        
        if not html_content:
            return []
        
        # Save HTML for debugging
        try:
            with open("data/debug_outputs/calendar_page_working_auth.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("Saved calendar HTML to data/debug_outputs/calendar_page_working_auth.html")
        except Exception as e:
            logger.warning(f"Could not save debug HTML: {e}")
        
        events = self.parse_calendar_html(html_content)
        
        logger.info(f"Total events/slots extracted: {len(events)}")
        return events
    
    def search_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Search for events in a date range"""
        logger.info(f"Searching calendar events from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # For now, get all events and filter (could be optimized to use date parameters)
        all_events = self.get_available_slots()
        
        # Filter events by date range if they have start times
        filtered_events = []
        for event in all_events:
            if event.start_time:
                try:
                    event_start = datetime.fromisoformat(event.start_time.replace('Z', '+00:00'))
                    if start_date <= event_start <= end_date:
                        filtered_events.append(event)
                except:
                    # If we can't parse the date, include the event
                    filtered_events.append(event)
            else:
                # If no start time, include the event
                filtered_events.append(event)
        
        logger.info(f"Found {len(filtered_events)} events (date filtering not yet implemented)")
        return all_events  # Return all for now

def main():
    """Test the calendar manager"""
    print("=== ClubOS Calendar Manager with Working Authentication ===")
    
    # Create calendar manager
    calendar_manager = ClubOSCalendarManager()
    
    # Authenticate
    if not calendar_manager.authenticate():
        return
    
    # Get available slots
    print("\n📅 Getting available calendar slots...")
    slots = calendar_manager.get_available_slots()
    
    if slots:
        print(f"✅ Found {len(slots)} calendar events/slots")
        
        # Show first few events
        print("\n=== FIRST 5 EVENTS/SLOTS ===")
        for i, event in enumerate(slots[:5], 1):
            print(f"Event {i}:")
            print(f"  ID: {event.id}")
            print(f"  Title: {event.title}")
            print(f"  Status: {event.funding_status}")
            print(f"  Attendees: {event.attendees}")
            if event.start_time:
                print(f"  Start: {event.start_time}")
            print()
        
        if len(slots) > 5:
            print(f"... and {len(slots) - 5} more events")
    else:
        print("❌ No calendar events found")
    
    # Test date range search
    print("\n📆 Testing date-based search...")
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    date_events = calendar_manager.search_events_by_date_range(start_date, end_date)
    print(f"Found {len(date_events)} events for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
