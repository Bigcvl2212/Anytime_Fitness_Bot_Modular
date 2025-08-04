#!/usr/bin/env python3
"""
Gym Calendar Management System - WORKING VERSION
Focuses on practical calendar management for Jeremy Mayo's gym
Uses form-based approach that actually works with ClubOS
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup

# Import working authentication
from clubos_integration_fixed import ClubOSIntegration
from config.secrets_local import get_secret

@dataclass
class GymEvent:
    """Represents a gym calendar event with all needed details"""
    id: str
    title: str
    start_time: str
    end_time: str
    event_type: str  # personal_training, small_group_training, appointment
    status: str  # booked, available, completed, cancelled
    funding_status: str  # funded, unfunded, available
    client_names: List[str]
    max_capacity: int = 1
    notes: str = ""
    
    @property
    def is_available(self) -> bool:
        return self.status == "available" or len(self.client_names) < self.max_capacity
    
    @property
    def spots_remaining(self) -> int:
        return max(0, self.max_capacity - len(self.client_names))

class GymCalendarManager:
    """
    Practical calendar management system that actually works
    """
    
    def __init__(self):
        print("🏋️ Initializing Gym Calendar Manager...")
        
        # Get ClubOS credentials
        clubos_username = get_secret("clubos-username")
        clubos_password = get_secret("clubos-password")
        
        self.clubos = ClubOSIntegration(username=clubos_username, password=clubos_password)
        self.is_authenticated = False
        self.jeremy_mayo_id = "187032782"
        
        # Calendar HTML cache for faster access
        self.calendar_html_cache = None
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes
    
    def connect(self) -> bool:
        """Connect to ClubOS and authenticate"""
        print("🔐 Connecting to ClubOS...")
        
        success = self.clubos.connect()
        if success:
            self.is_authenticated = True
            print("✅ Connected to ClubOS successfully")
            return True
        else:
            print("❌ Failed to connect to ClubOS")
            return False
    
    def get_calendar_events(self, date: str = None, use_cache: bool = True) -> List[GymEvent]:
        """
        Get Jeremy Mayo's calendar events for a specific date
        """
        if not date:
            date = datetime.now().strftime("%m/%d/%Y")
        
        print(f"📅 Getting calendar events for {date}...")
        
        # Try cached HTML first if it's recent
        if use_cache and self._is_cache_valid():
            print("   Using cached calendar data...")
            html_content = self.calendar_html_cache
        else:
            # Get fresh calendar data
            html_content = self._fetch_calendar_html(date)
            if html_content:
                self._update_cache(html_content)
        
        if not html_content:
            print("❌ No calendar data available")
            return []
        
        # Parse events from HTML
        events = self._parse_calendar_events(html_content)
        print(f"✅ Found {len(events)} calendar events")
        
        return events
    
    def _fetch_calendar_html(self, date: str) -> Optional[str]:
        """Fetch calendar HTML from ClubOS with session recovery"""
        
        if not self.is_authenticated:
            print("❌ Not authenticated - cannot fetch calendar")
            return None
        
        try:
            print(f"📅 Fetching FRESH calendar data for {date}...")
            
            # STRATEGY: Capture calendar HTML during the refresh process when session is working
            captured_calendar_html = None
            
            def capture_calendar_during_refresh():
                nonlocal captured_calendar_html
                try:
                    # Visit dashboard to get fresh session state
                    dashboard_url = f"{self.clubos.client.base_url}/action/Dashboard"
                    dashboard_response = self.clubos.client.session.get(dashboard_url, timeout=10)
                    
                    if dashboard_response.ok:
                        print("📊 Visited dashboard page")
                        self.clubos.client._extract_session_tokens(dashboard_response.text, "dashboard")
                        
                        # SAVE DASHBOARD HTML TO FIND CALENDAR LINKS!
                        os.makedirs("data/debug_outputs", exist_ok=True)
                        with open("data/debug_outputs/dashboard_html_analysis.html", "w", encoding="utf-8") as f:
                            f.write(dashboard_response.text)
                        print("💾 Saved dashboard HTML for calendar link analysis")
                        
                        # ANALYZE DASHBOARD FOR CALENDAR LINKS
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                        
                        # Look for calendar-related links
                        calendar_links = []
                        all_links = soup.find_all('a', href=True)
                        
                        for link in all_links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True).lower()
                            title = link.get('title', '').lower()
                            
                            if any(keyword in href.lower() + text + title 
                                   for keyword in ['calendar', 'schedule', 'appointment', 'booking']):
                                calendar_links.append({
                                    'href': href,
                                    'text': text,
                                    'title': title
                                })
                        
                        print(f"🔍 Found {len(calendar_links)} potential calendar links on dashboard:")
                        for link in calendar_links[:5]:  # Show first 5
                            print(f"   - {link['href']} | '{link['text']}' | '{link['title']}'")
                        
                        # TRY THE ACTUAL CALENDAR LINKS FROM DASHBOARD INSTEAD OF GUESSING
                        if calendar_links:
                            print("� Trying calendar links found on dashboard...")
                            for link in calendar_links[:3]:  # Try first 3 links
                                calendar_href = link['href']
                                
                                # Convert relative URLs to absolute
                                if calendar_href.startswith('/'):
                                    calendar_url = f"{self.clubos.client.base_url}{calendar_href}"
                                elif calendar_href.startswith('http'):
                                    calendar_url = calendar_href
                                else:
                                    continue  # Skip invalid links
                                
                                print(f"   Trying: {calendar_url}")
                                
                                calendar_response = self.clubos.client.session.get(calendar_url, timeout=10)
                                
                                if calendar_response.ok and not self._is_login_page(calendar_response.text):
                                    print(f"   🎯 SUCCESS! Found working calendar URL: {calendar_url}")
                                    captured_calendar_html = calendar_response.text
                                    print(f"   📊 Captured calendar HTML ({len(captured_calendar_html)} chars)")
                                    self.clubos.client._extract_session_tokens(calendar_response.text, "calendar")
                                    break
                                else:
                                    print(f"   ❌ Link failed: {calendar_response.status_code}")
                        else:
                            print("⚠️ No calendar links found on dashboard")
                    else:
                        print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error in calendar capture during refresh: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Override the refresh method temporarily to capture calendar
            if hasattr(self.clubos.client, '_refresh_session_tokens'):
                # Store original method
                original_refresh = self.clubos.client._refresh_session_tokens
                # Replace with capture method
                self.clubos.client._refresh_session_tokens = capture_calendar_during_refresh
                # Call it to capture calendar
                print("   Using refresh cycle to capture calendar HTML...")
                self.clubos.client._refresh_session_tokens()
                # Restore original method
                self.clubos.client._refresh_session_tokens = original_refresh
            
            # Check if we captured valid calendar HTML
            if captured_calendar_html and not self._is_login_page(captured_calendar_html):
                print("✅ Successfully captured calendar HTML during refresh cycle")
                
                # Validate we have calendar content
                if not self._validate_calendar_content(captured_calendar_html):
                    print(f"⚠️ Captured HTML missing calendar content")
                    return None
                
                # Save for debugging
                os.makedirs("data/debug_outputs", exist_ok=True)
                with open(f"data/debug_outputs/fresh_calendar_{date.replace('/', '_')}.html", "w", encoding="utf-8") as f:
                    f.write(captured_calendar_html)
                print(f"   Saved captured calendar data for debugging")
                
                return captured_calendar_html
            else:
                print("❌ Failed to capture valid calendar HTML during refresh")
                return None
                
        except Exception as e:
            print(f"❌ Error in calendar HTML capture: {e}")
            return None
    
    def _attempt_calendar_fetch(self, date: str):
        """Attempt to fetch calendar data with current session"""
        try:
            # Step 1: First visit the calendar page WITHOUT any specific user parameters
            calendar_url = f"{self.clubos.client.base_url}/action/Calendar"
            print(f"   First testing basic calendar access (no user parameters)...")
            
            basic_response = self.clubos.client.session.get(
                calendar_url,
                headers={
                    'Referer': f'{self.clubos.client.base_url}/action/Dashboard'
                },
                timeout=15
            )
            
            if not basic_response.ok or self._is_login_page(basic_response.text):
                print(f"   ❌ Even basic calendar access failed - session issue")
                return basic_response
            
            print(f"   ✅ Basic calendar access works! ({len(basic_response.text)} chars)")
            
            # Save the basic calendar page for analysis
            os.makedirs("data/debug_outputs", exist_ok=True)
            with open("data/debug_outputs/basic_calendar_access.html", "w", encoding="utf-8") as f:
                f.write(basic_response.text)
            print(f"   💾 Saved basic calendar HTML for analysis")
            
            # Step 2: Extract any session tokens from the calendar page
            self.clubos.client._extract_session_tokens(basic_response.text, "calendar_init")
            
            # Step 3: Now try with Jeremy's specific parameters
            print(f"   Now trying with Jeremy's specific view parameters...")
            
            # Build form data for Jeremy's specific calendar
            form_data = {
                'selectedView': self.jeremy_mayo_id,  # Jeremy Mayo's ID
                'selectedDate': date,  # Use the requested date
                'calendarFilter.clubLocationId': '3586',  # Fond du Lac
                'calendarFilter.clubId': '291'
            }
            
            # Add session tokens to form data
            if hasattr(self.clubos.client, 'form_tokens') and self.clubos.client.form_tokens:
                form_data.update(self.clubos.client.form_tokens)
                print(f"   Added {len(self.clubos.client.form_tokens)} session tokens")
            
            print(f"   Form data: {list(form_data.keys())}")
            
            response = self.clubos.client.session.get(
                calendar_url,
                params=form_data,  # Use params for GET
                headers={
                    'Referer': calendar_url
                },
                timeout=15
            )
            
            print(f"   Jeremy-specific request: Status {response.status_code}, {len(response.text)} chars")
            print(f"   Final URL: {response.url}")
            
            if response.ok and not self._is_login_page(response.text):
                print(f"   ✅ Jeremy's calendar access successful!")
                return response
            else:
                print(f"   ❌ Jeremy's calendar access failed - permission issue?")
                # Return the basic calendar page as fallback
                print(f"   📋 Returning basic calendar page as fallback")
                return basic_response
            
        except Exception as e:
            print(f"   Error in calendar fetch attempt: {e}")
            return None
    
    def _is_login_page(self, html_content: str) -> bool:
        """Check if the response is a login page"""
        return ('name="username"' in html_content and 
                'name="password"' in html_content and 
                ('/action/Login' in html_content or 'action="Login"' in html_content))
    
    def _validate_calendar_content(self, html_content: str) -> bool:
        """Validate that we have actual calendar content"""
        return ('schedule' in html_content.lower() or 
                'calendar' in html_content.lower() or
                'time-slot' in html_content.lower() or
                len(html_content) > 20000)  # Calendar pages are typically large
    
    def _re_authenticate(self) -> bool:
        """Re-authenticate with ClubOS"""
        try:
            print("🔄 Attempting to re-authenticate...")
            
            # Reset authentication status
            self.is_authenticated = False
            
            # Re-connect using the working ClubOS system
            success = self.clubos.connect()
            if success:
                self.is_authenticated = True
                print("✅ Re-authentication successful")
                return True
            else:
                print("❌ Re-authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during re-authentication: {e}")
            return False
    
    def _parse_calendar_events(self, html_content: str) -> List[GymEvent]:
        """Parse calendar events from ClubOS HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            events = []
            
            # Find all hidden inputs with Jeremy's ID that contain event data
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            
            for hidden_input in hidden_inputs:
                try:
                    value = hidden_input.get('value', '')
                    if self.jeremy_mayo_id in value and 'eventId' in value:
                        event_data = json.loads(value)
                        event = self._create_gym_event_from_json(event_data, hidden_input)
                        if event:
                            events.append(event)
                except (json.JSONDecodeError, Exception):
                    continue
            
            # Sort by start time
            events.sort(key=lambda e: e.start_time)
            
            return events
            
        except Exception as e:
            print(f"❌ Error parsing calendar events: {e}")
            return []
    
    def _create_gym_event_from_json(self, event_data: dict, hidden_input) -> Optional[GymEvent]:
        """Create a GymEvent from JSON data and HTML context"""
        try:
            event_id = event_data.get('eventId')
            if not event_id:
                return None
            
            # Find the parent event div
            event_div = hidden_input.find_parent('div', class_='cal-event')
            if not event_div:
                return None
            
            # Extract time and client info from slot-info
            slot_info = event_div.find('div', class_='slot-info')
            if not slot_info:
                return None
            
            time_range = ""
            client_names = []
            
            for div in slot_info.find_all('div'):
                text = div.get_text(strip=True)
                if ':' in text and '-' in text:  # Time format
                    time_range = text
                elif div.get('class') and 'black' in div.get('class'):  # Client names
                    # Parse client names (might be multiple separated by 'and')
                    names = re.split(r'\s+and\s+', text)
                    client_names = [name.strip() for name in names if name.strip()]
            
            if not time_range:
                return None
            
            # Parse times
            times = time_range.split(' - ')
            start_time = times[0].strip()
            end_time = times[1].strip() if len(times) > 1 else start_time
            
            # Determine event type
            event_type_id = event_data.get('eventTypeId', '')
            event_type = self._get_event_type(event_type_id, event_div)
            
            # Determine status
            status = self._get_event_status(event_div, client_names)
            
            # Get funding status
            funding_status = self._get_funding_status(event_div)
            
            # Determine capacity based on event type
            max_capacity = 1
            if event_type == "small_group_training":
                max_capacity = 6
            elif event_type == "group_training":
                max_capacity = 12
            
            # Create title
            if client_names:
                title = ", ".join(client_names)
            else:
                title = f"Available {event_type.replace('_', ' ').title()}"
            
            return GymEvent(
                id=str(event_id),
                title=title,
                start_time=start_time,
                end_time=end_time,
                event_type=event_type,
                status=status,
                funding_status=funding_status,
                client_names=client_names,
                max_capacity=max_capacity
            )
            
        except Exception as e:
            print(f"   Error creating gym event: {e}")
            return None
    
    def _get_event_type(self, event_type_id: str, event_div) -> str:
        """Determine event type from ID and HTML"""
        type_mapping = {
            '2': 'personal_training',
            '8': 'small_group_training',
            '7': 'group_training',
            '3': 'group_class',
            '4': 'appointment',
            '5': 'orientation',
            '6': 'assessment'
        }
        
        event_type = type_mapping.get(event_type_id, 'appointment')
        
        # Also check icon for confirmation
        icon = event_div.find('img')
        if icon:
            title = icon.get('title', '').lower()
            if 'personal training' in title:
                event_type = 'personal_training'
            elif 'small group' in title:
                event_type = 'small_group_training'
        
        return event_type
    
    def _get_event_status(self, event_div, client_names: List[str]) -> str:
        """Determine event status from HTML"""
        classes = event_div.get('class', [])
        
        if 'cancelled-event' in classes:
            return 'cancelled'
        elif 'completed-event' in classes:
            return 'completed'
        elif client_names:
            return 'booked'
        else:
            return 'available'
    
    def _get_funding_status(self, event_div) -> str:
        """Get funding status from HTML"""
        # Check for funding input
        funding_input = event_div.find('input', {'name': 'fundingStatus'})
        if funding_input:
            return funding_input.get('value', '').lower()
        
        # Check for funding icon
        funding_icon = event_div.find('div', class_='funding-icon')
        if funding_icon and 'funded' in funding_icon.get('class', []):
            return 'funded'
        
        return 'unknown'
    
    def book_client_to_event(self, event_id: str, client_name: str, client_phone: str = "", notes: str = "") -> bool:
        """
        Book a client to an existing calendar event
        """
        print(f"📝 Booking {client_name} to event {event_id}...")
        
        if not self.is_authenticated:
            print("❌ Not authenticated")
            return False
        
        try:
            # First, get the current event to understand its structure
            events = self.get_calendar_events(use_cache=True)
            target_event = next((e for e in events if e.id == event_id), None)
            
            if not target_event:
                print(f"❌ Event {event_id} not found")
                return False
            
            if not target_event.is_available:
                print(f"❌ Event {event_id} is full (capacity: {target_event.max_capacity})")
                return False
            
            # Try different booking approaches
            success = (
                self._try_direct_booking(event_id, client_name, client_phone, notes) or
                self._try_ajax_booking(event_id, client_name, client_phone, notes) or
                self._try_form_booking(event_id, client_name, client_phone, notes)
            )
            
            if success:
                print(f"✅ Successfully booked {client_name} to event {event_id}")
                self._invalidate_cache()  # Refresh cache
                return True
            else:
                print(f"❌ Failed to book {client_name} to event {event_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error booking client: {e}")
            return False
    
    def _try_direct_booking(self, event_id: str, client_name: str, client_phone: str, notes: str) -> bool:
        """Try direct booking via calendar forms"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            # Get calendar page to find booking forms
            calendar_url = f"{self.clubos.client.base_url}/action/Calendar"
            response = self.clubos.client.session.get(calendar_url)
            
            if not response.ok:
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for booking forms with the specific event ID
            booking_forms = soup.find_all('form')
            for form in booking_forms:
                # Check if this form is for booking/attending events
                action = form.get('action', '').lower()
                if 'book' in action or 'attend' in action or 'add' in action:
                    
                    form_data = {}
                    
                    # Add all hidden fields
                    for hidden in form.find_all('input', {'type': 'hidden'}):
                        name = hidden.get('name')
                        value = hidden.get('value', '')
                        if name:
                            form_data[name] = value
                    
                    # Add form tokens
                    if hasattr(self.clubos.client, 'form_tokens'):
                        form_data.update(self.clubos.client.form_tokens)
                    
                    # Add booking details
                    form_data.update({
                        'eventId': event_id,
                        'id': event_id,
                        'appointmentId': event_id,
                        'clientName': client_name,
                        'memberName': client_name,
                        'name': client_name,
                        'phone': client_phone,
                        'notes': notes,
                        'action': 'book'
                    })
                    
                    # Submit booking
                    submit_url = f"{self.clubos.client.base_url}{action}" if action.startswith('/') else action
                    booking_response = self.clubos.client.session.post(
                        submit_url,
                        data=form_data,
                        headers={
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Referer': calendar_url
                        }
                    )
                    
                    if booking_response.ok:
                        print(f"   ✅ Direct booking successful via {action}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Direct booking failed: {e}")
            return False
    
    def _try_ajax_booking(self, event_id: str, client_name: str, client_phone: str, notes: str) -> bool:
        """Try AJAX-based booking"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            # Try common AJAX booking endpoints
            ajax_endpoints = [
                '/ajax/calendar/book',
                '/ajax/appointment/book',
                '/ajax/event/addAttendee',
                '/ajax/calendar/addMember'
            ]
            
            for endpoint in ajax_endpoints:
                ajax_url = f"{self.clubos.client.base_url}{endpoint}"
                
                ajax_data = {
                    'eventId': event_id,
                    'id': event_id,
                    'clientName': client_name,
                    'memberName': client_name,
                    'phone': client_phone,
                    'notes': notes
                }
                
                # Add form tokens
                if hasattr(self.clubos.client, 'form_tokens'):
                    ajax_data.update(self.clubos.client.form_tokens)
                
                response = self.clubos.client.session.post(
                    ajax_url,
                    data=ajax_data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': f'{self.clubos.client.base_url}/action/Calendar'
                    }
                )
                
                if response.ok:
                    print(f"   ✅ AJAX booking successful via {endpoint}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ AJAX booking failed: {e}")
            return False
    
    def _try_form_booking(self, event_id: str, client_name: str, client_phone: str, notes: str) -> bool:
        """Try form-based booking by finding event-specific forms"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            # Get the calendar page and look for event-specific booking forms
            calendar_url = f"{self.clubos.client.base_url}/action/Calendar"
            response = self.clubos.client.session.get(calendar_url)
            
            if not response.ok:
                return False
            
            # Look for clickable event links or booking buttons
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the specific event div
            event_divs = soup.find_all('div', class_='cal-event')
            for event_div in event_divs:
                hidden_input = event_div.find('input', {'type': 'hidden'})
                if hidden_input:
                    try:
                        event_data = json.loads(hidden_input.get('value', '{}'))
                        if str(event_data.get('eventId')) == str(event_id):
                            # Found the event, look for booking links
                            booking_links = event_div.find_all('a')
                            for link in booking_links:
                                href = link.get('href', '')
                                if 'book' in href.lower() or 'attend' in href.lower():
                                    # Try to follow this booking link
                                    booking_url = f"{self.clubos.client.base_url}{href}" if href.startswith('/') else href
                                    
                                    booking_data = {
                                        'clientName': client_name,
                                        'memberName': client_name,
                                        'phone': client_phone,
                                        'notes': notes
                                    }
                                    
                                    if hasattr(self.clubos.client, 'form_tokens'):
                                        booking_data.update(self.clubos.client.form_tokens)
                                    
                                    booking_response = self.clubos.client.session.post(
                                        booking_url,
                                        data=booking_data,
                                        headers={
                                            'Content-Type': 'application/x-www-form-urlencoded',
                                            'Referer': calendar_url
                                        }
                                    )
                                    
                                    if booking_response.ok:
                                        print(f"   ✅ Form booking successful via event link")
                                        return True
                    except json.JSONDecodeError:
                        continue
            
            return False
            
        except Exception as e:
            print(f"   ❌ Form booking failed: {e}")
            return False
    
    def cancel_client_from_event(self, event_id: str, client_name: str) -> bool:
        """
        Remove/cancel a client from an event
        """
        print(f"❌ Cancelling {client_name} from event {event_id}...")
        
        if not self.is_authenticated:
            print("❌ Not authenticated")
            return False
        
        try:
            # Try different cancellation approaches
            success = (
                self._try_direct_cancellation(event_id, client_name) or
                self._try_ajax_cancellation(event_id, client_name) or
                self._try_form_cancellation(event_id, client_name)
            )
            
            if success:
                print(f"✅ Successfully cancelled {client_name} from event {event_id}")
                self._invalidate_cache()
                return True
            else:
                print(f"❌ Failed to cancel {client_name} from event {event_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error cancelling client: {e}")
            return False
    
    def _try_direct_cancellation(self, event_id: str, client_name: str) -> bool:
        """Try direct cancellation via calendar forms"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            # Common cancellation endpoints
            cancel_endpoints = [
                '/action/Calendar/cancel',
                '/action/Appointment/cancel',
                '/action/Event/removeAttendee'
            ]
            
            for endpoint in cancel_endpoints:
                cancel_url = f"{self.clubos.client.base_url}{endpoint}"
                
                cancel_data = {
                    'eventId': event_id,
                    'id': event_id,
                    'clientName': client_name,
                    'memberName': client_name,
                    'action': 'cancel'
                }
                
                if hasattr(self.clubos.client, 'form_tokens'):
                    cancel_data.update(self.clubos.client.form_tokens)
                
                response = self.clubos.client.session.post(
                    cancel_url,
                    data=cancel_data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Referer': f'{self.clubos.client.base_url}/action/Calendar'
                    }
                )
                
                if response.ok:
                    print(f"   ✅ Direct cancellation successful via {endpoint}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Direct cancellation failed: {e}")
            return False
    
    def _try_ajax_cancellation(self, event_id: str, client_name: str) -> bool:
        """Try AJAX-based cancellation"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            ajax_endpoints = [
                '/ajax/calendar/cancel',
                '/ajax/appointment/cancel',
                '/ajax/event/removeAttendee',
                '/ajax/calendar/removeMember'
            ]
            
            for endpoint in ajax_endpoints:
                ajax_url = f"{self.clubos.client.base_url}{endpoint}"
                
                ajax_data = {
                    'eventId': event_id,
                    'id': event_id,
                    'clientName': client_name,
                    'memberName': client_name,
                    'action': 'remove'
                }
                
                if hasattr(self.clubos.client, 'form_tokens'):
                    ajax_data.update(self.clubos.client.form_tokens)
                
                response = self.clubos.client.session.post(
                    ajax_url,
                    data=ajax_data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': f'{self.clubos.client.base_url}/action/Calendar'
                    }
                )
                
                if response.ok:
                    print(f"   ✅ AJAX cancellation successful via {endpoint}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ AJAX cancellation failed: {e}")
            return False
    
    def _try_form_cancellation(self, event_id: str, client_name: str) -> bool:
        """Try form-based cancellation"""
        # Similar to form booking but for cancellation
        # Implementation would be similar to _try_form_booking
        return False
    
    def create_new_event(self, date: str, start_time: str, end_time: str, event_type: str = "personal_training", max_capacity: int = 1) -> Optional[str]:
        """
        Create a new calendar event/appointment slot
        """
        print(f"➕ Creating new {event_type} event on {date} from {start_time} to {end_time}...")
        
        if not self.is_authenticated:
            print("❌ Not authenticated")
            return None
        
        try:
            # Try different event creation approaches
            event_id = (
                self._try_direct_event_creation(date, start_time, end_time, event_type, max_capacity) or
                self._try_ajax_event_creation(date, start_time, end_time, event_type, max_capacity) or
                self._try_form_event_creation(date, start_time, end_time, event_type, max_capacity)
            )
            
            if event_id:
                print(f"✅ Successfully created event {event_id}")
                self._invalidate_cache()
                return event_id
            else:
                print(f"❌ Failed to create event")
                return None
                
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def _try_direct_event_creation(self, date: str, start_time: str, end_time: str, event_type: str, max_capacity: int) -> Optional[str]:
        """Try direct event creation via calendar forms"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            # Get calendar page to find event creation forms
            calendar_url = f"{self.clubos.client.base_url}/action/Calendar"
            response = self.clubos.client.session.get(calendar_url)
            
            if not response.ok:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for "Add Event" forms or buttons
            add_buttons = soup.find_all(['a', 'button'], string=re.compile(r'add.*event', re.I))
            forms = soup.find_all('form')
            
            # Try to find add event forms
            for form in forms:
                action = form.get('action', '').lower()
                if 'add' in action or 'create' in action or 'new' in action:
                    
                    form_data = {}
                    
                    # Add hidden fields
                    for hidden in form.find_all('input', {'type': 'hidden'}):
                        name = hidden.get('name')
                        value = hidden.get('value', '')
                        if name:
                            form_data[name] = value
                    
                    # Add form tokens
                    if hasattr(self.clubos.client, 'form_tokens'):
                        form_data.update(self.clubos.client.form_tokens)
                    
                    # Map event type to ClubOS event type ID
                    event_type_mapping = {
                        'personal_training': '2',
                        'small_group_training': '8',
                        'group_training': '7',
                        'appointment': '4',
                        'orientation': '5',
                        'assessment': '6'
                    }
                    
                    # Add event details
                    form_data.update({
                        'date': date,
                        'selectedDate': date,
                        'startTime': start_time,
                        'endTime': end_time,
                        'eventType': event_type,
                        'eventTypeId': event_type_mapping.get(event_type, '2'),
                        'trainerId': self.jeremy_mayo_id,
                        'staffId': self.jeremy_mayo_id,
                        'capacity': str(max_capacity),
                        'maxCapacity': str(max_capacity)
                    })
                    
                    # Submit form
                    submit_url = f"{self.clubos.client.base_url}{action}" if action.startswith('/') else action
                    create_response = self.clubos.client.session.post(
                        submit_url,
                        data=form_data,
                        headers={
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Referer': calendar_url
                        }
                    )
                    
                    if create_response.ok:
                        # Try to extract event ID from response
                        event_id = self._extract_event_id_from_response(create_response.text)
                        if event_id:
                            print(f"   ✅ Direct event creation successful via {action}")
                            return event_id
            
            return None
            
        except Exception as e:
            print(f"   ❌ Direct event creation failed: {e}")
            return None
    
    def _try_ajax_event_creation(self, date: str, start_time: str, end_time: str, event_type: str, max_capacity: int) -> Optional[str]:
        """Try AJAX-based event creation"""
        try:
            self.clubos.client._refresh_session_tokens()
            
            ajax_endpoints = [
                '/ajax/calendar/create',
                '/ajax/appointment/create',
                '/ajax/event/create',
                '/ajax/calendar/addEvent'
            ]
            
            event_type_mapping = {
                'personal_training': '2',
                'small_group_training': '8',
                'group_training': '7',
                'appointment': '4'
            }
            
            for endpoint in ajax_endpoints:
                ajax_url = f"{self.clubos.client.base_url}{endpoint}"
                
                ajax_data = {
                    'date': date,
                    'selectedDate': date,
                    'startTime': start_time,
                    'endTime': end_time,
                    'eventType': event_type,
                    'eventTypeId': event_type_mapping.get(event_type, '2'),
                    'trainerId': self.jeremy_mayo_id,
                    'staffId': self.jeremy_mayo_id,
                    'capacity': str(max_capacity)
                }
                
                if hasattr(self.clubos.client, 'form_tokens'):
                    ajax_data.update(self.clubos.client.form_tokens)
                
                response = self.clubos.client.session.post(
                    ajax_url,
                    data=ajax_data,
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': f'{self.clubos.client.base_url}/action/Calendar'
                    }
                )
                
                if response.ok:
                    event_id = self._extract_event_id_from_response(response.text)
                    if event_id:
                        print(f"   ✅ AJAX event creation successful via {endpoint}")
                        return event_id
            
            return None
            
        except Exception as e:
            print(f"   ❌ AJAX event creation failed: {e}")
            return None
    
    def _try_form_event_creation(self, date: str, start_time: str, end_time: str, event_type: str, max_capacity: int) -> Optional[str]:
        """Try form-based event creation"""
        # Implementation would follow similar pattern to other form methods
        return None
    
    def _extract_event_id_from_response(self, response_text: str) -> Optional[str]:
        """Extract event ID from response HTML or JSON"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                return data.get('eventId') or data.get('id')
            
            # Try to extract from HTML
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # Look for event ID in hidden inputs
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for hidden in hidden_inputs:
                if 'eventId' in hidden.get('name', ''):
                    return hidden.get('value')
                
                # Check JSON values
                value = hidden.get('value', '')
                if 'eventId' in value:
                    try:
                        data = json.loads(value)
                        return str(data.get('eventId'))
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Exception:
            return None
    
    def get_available_slots(self, date: str = None, event_type: str = None) -> List[GymEvent]:
        """Get truly available (empty) booking slots for a specific date"""
        if not date:
            date = datetime.now().strftime('%m/%d/%Y')
        
        # Get existing booked events for this date
        existing_events = self.get_calendar_events(date)
        
        # Create set of occupied time slots (any event that takes up the time slot)
        occupied_times = set()
        for event in existing_events:
            # Any event with a start time occupies that slot, regardless of status
            if event.start_time:
                # Convert start time to standard format for comparison
                occupied_times.add(event.start_time)
        
        print(f"   Found {len(occupied_times)} occupied time slots: {sorted(occupied_times)}")
        
        # Generate all possible time slots for Jeremy's schedule (6 AM - 8 PM)
        available_slots = []
        
        # Standard gym hours: 6 AM to 8 PM, 30-minute slots
        time_slots = [
            "6:00", "6:30", "7:00", "7:30", "8:00", "8:30", 
            "9:00", "9:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", 
            "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
            "18:00", "18:30", "19:00", "19:30", "20:00"
        ]
        
        for start_time in time_slots:
            # Convert to comparable format (handle 24hr vs 12hr)
            comparable_time = self._normalize_time_format(start_time)
            
            # Check if this time slot is occupied by any event
            is_occupied = any(self._normalize_time_format(occupied_time) == comparable_time 
                            for occupied_time in occupied_times)
            
            if not is_occupied:
                # Calculate end time (30 minutes later)
                end_time = self._calculate_end_time(start_time)
                
                # Create available slot
                slot_id = f"available_{start_time.replace(':', '')}"
                available_slot = GymEvent(
                    id=slot_id,
                    title=f"Available {event_type or 'Personal Training'}",
                    start_time=start_time,
                    end_time=end_time,
                    event_type=event_type or "personal_training",
                    status="available",
                    funding_status="available",
                    client_names=[],
                    max_capacity=1,
                    notes=f"Open slot for {date}"
                )
                available_slots.append(available_slot)
        
        print(f"   Generated {len(available_slots)} truly available slots")
        return available_slots
    
    def _normalize_time_format(self, time_str: str) -> str:
        """Normalize time format for comparison (convert to 24hr HH:MM)"""
        try:
            # Handle various time formats
            time_str = time_str.strip()
            
            # If it's already in 24hr format like "13:00"
            if ':' in time_str and len(time_str.split(':')[0]) <= 2:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
                return f"{hour:02d}:{minute:02d}"
            
            return time_str
            
        except Exception:
            return time_str
    
    def _calculate_end_time(self, start_time: str) -> str:
        """Calculate end time (30 minutes after start time)"""
        try:
            if ':' in start_time:
                hour, minute = map(int, start_time.split(':'))
                end_minute = minute + 30
                end_hour = hour
                if end_minute >= 60:
                    end_minute -= 60
                    end_hour += 1
                return f"{end_hour}:{end_minute:02d}"
            return start_time
        except Exception:
            return start_time
    
    def get_event_details(self, event_id: str) -> Optional[GymEvent]:
        """Get detailed information about a specific event"""
        events = self.get_calendar_events(use_cache=True)
        return next((e for e in events if e.id == event_id), None)
    
    def _is_cache_valid(self) -> bool:
        """Check if calendar cache is still valid"""
        if not self.calendar_html_cache or not self.cache_timestamp:
            return False
        
        return (datetime.now() - self.cache_timestamp).seconds < self.cache_duration
    
    def _update_cache(self, html_content: str):
        """Update calendar HTML cache"""
        self.calendar_html_cache = html_content
        self.cache_timestamp = datetime.now()
    
    def _invalidate_cache(self):
        """Invalidate calendar cache to force refresh"""
        self.calendar_html_cache = None
        self.cache_timestamp = None
    
    def print_calendar_summary(self, date: str = None):
        """Print a nice summary of the calendar for a date"""
        events = self.get_calendar_events(date)
        
        print(f"\n📅 Calendar Summary for {date or 'Today'}")
        print("=" * 50)
        
        if not events:
            print("No events found")
            return
        
        for event in events:
            status_emoji = {
                'available': '🟢',
                'booked': '🔴',
                'completed': '✅',
                'cancelled': '❌'
            }.get(event.status, '⚪')
            
            funding_emoji = '💰' if event.funding_status == 'funded' else '💸'
            
            print(f"{status_emoji} {event.start_time}-{event.end_time} | {event.title}")
            print(f"   Type: {event.event_type.replace('_', ' ').title()}")
            print(f"   Capacity: {len(event.client_names)}/{event.max_capacity}")
            if event.client_names:
                print(f"   Clients: {', '.join(event.client_names)}")
            print(f"   Funding: {event.funding_status} {funding_emoji}")
            print()

def interactive_menu():
    """Interactive menu for gym calendar management"""
    print("🏋️ GYM CALENDAR MANAGEMENT SYSTEM")
    print("=" * 50)
    
    # Initialize calendar manager
    calendar = GymCalendarManager()
    
    # Connect to ClubOS
    if not calendar.connect():
        print("❌ Failed to connect to ClubOS system")
        return
    
    current_events = []
    
    while True:
        print("\n" + "=" * 50)
        print("CALENDAR MENU:")
        print("1. 📅 Show today's schedule")
        print("2. 🟢 Show available slots") 
        print("3. ➕ Book new appointment")
        print("4. ❌ Cancel appointment")
        print("5. 👥 Add client to session")
        print("6. ➖ Remove client from session")
        print("7. 📝 Create new time slot")
        print("8. 📊 Calendar summary")
        print("9. 🔄 Refresh calendar")
        print("0. 🚪 Exit")
        print("=" * 50)
        
        try:
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "1":
                print("\n📅 Getting today's schedule...")
                current_events = calendar.get_calendar_events()
                calendar.print_calendar_summary()
                
            elif choice == "2":
                print("\n🟢 Getting available slots...")
                available_slots = calendar.get_available_slots()
                if available_slots:
                    print(f"Found {len(available_slots)} available slots:")
                    for i, slot in enumerate(available_slots[:10], 1):
                        print(f"  {i}. {slot.start_time}-{slot.end_time} | {slot.title}")
                    if len(available_slots) > 10:
                        print(f"     ... and {len(available_slots) - 10} more slots")
                else:
                    print("📭 No available slots found")
                
            elif choice == "3":
                available_slots = calendar.get_available_slots()
                if available_slots:
                    print(f"\nAvailable slots:")
                    for i, slot in enumerate(available_slots[:10], 1):
                        print(f"  {i}. {slot.start_time}-{slot.end_time} | {slot.title}")
                    
                    try:
                        slot_num = int(input("Select slot number to book: ")) - 1
                        if 0 <= slot_num < len(available_slots):
                            slot = available_slots[slot_num]
                            client_name = input("Client name: ").strip()
                            client_phone = input("Client phone (optional): ").strip()
                            notes = input("Notes (optional): ").strip()
                            
                            success = calendar.book_client_to_event(
                                event_id=slot.id,
                                client_name=client_name,
                                client_phone=client_phone,
                                notes=notes
                            )
                            
                            if success:
                                print(f"✅ Successfully booked {client_name} for {slot.start_time}-{slot.end_time}")
                            else:
                                print(f"❌ Failed to book appointment")
                        else:
                            print("❌ Invalid slot number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("📭 No available slots to book")
                
            elif choice == "4":
                if not current_events:
                    current_events = calendar.get_calendar_events()
                
                booked_events = [e for e in current_events if e.status == "booked" and e.client_names]
                if booked_events:
                    print(f"\nBooked appointments:")
                    for i, event in enumerate(booked_events, 1):
                        clients = ", ".join(event.client_names)
                        print(f"  {i}. {event.start_time}-{event.end_time} | {clients}")
                    
                    try:
                        event_num = int(input("Select appointment to cancel: ")) - 1
                        if 0 <= event_num < len(booked_events):
                            event = booked_events[event_num]
                            client_name = input(f"Client name to cancel ({', '.join(event.client_names)}): ").strip()
                            
                            success = calendar.cancel_client_from_event(
                                event_id=event.id,
                                client_name=client_name
                            )
                            
                            if success:
                                print(f"✅ Successfully canceled {client_name} from {event.start_time}-{event.end_time}")
                            else:
                                print(f"❌ Failed to cancel appointment")
                        else:
                            print("❌ Invalid appointment number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("📭 No booked appointments to cancel")
                
            elif choice == "5":
                if not current_events:
                    current_events = calendar.get_calendar_events()
                
                available_for_add = [e for e in current_events if e.spots_remaining > 0]
                if available_for_add:
                    print(f"\nSessions with available spots:")
                    for i, event in enumerate(available_for_add, 1):
                        print(f"  {i}. {event.start_time}-{event.end_time} | {event.title} ({event.spots_remaining} spots left)")
                    
                    try:
                        event_num = int(input("Select session to add client to: ")) - 1
                        if 0 <= event_num < len(available_for_add):
                            event = available_for_add[event_num]
                            client_name = input("Client name: ").strip()
                            client_phone = input("Client phone (optional): ").strip()
                            notes = input("Notes (optional): ").strip()
                            
                            success = calendar.book_client_to_event(
                                event_id=event.id,
                                client_name=client_name,
                                client_phone=client_phone,
                                notes=notes
                            )
                            
                            if success:
                                print(f"✅ Successfully added {client_name} to {event.start_time}-{event.end_time}")
                            else:
                                print(f"❌ Failed to add client to session")
                        else:
                            print("❌ Invalid session number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("📭 No sessions with available spots")
                
            elif choice == "6":
                if not current_events:
                    current_events = calendar.get_calendar_events()
                
                sessions_with_clients = [e for e in current_events if e.client_names]
                if sessions_with_clients:
                    print(f"\nSessions with clients:")
                    for i, event in enumerate(sessions_with_clients, 1):
                        clients = ", ".join(event.client_names)
                        print(f"  {i}. {event.start_time}-{event.end_time} | {clients}")
                    
                    try:
                        event_num = int(input("Select session to remove client from: ")) - 1
                        if 0 <= event_num < len(sessions_with_clients):
                            event = sessions_with_clients[event_num]
                            print(f"Clients in this session: {', '.join(event.client_names)}")
                            client_name = input("Client name to remove: ").strip()
                            
                            success = calendar.cancel_client_from_event(
                                event_id=event.id,
                                client_name=client_name
                            )
                            
                            if success:
                                print(f"✅ Successfully removed {client_name} from {event.start_time}-{event.end_time}")
                            else:
                                print(f"❌ Failed to remove client from session")
                        else:
                            print("❌ Invalid session number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("📭 No sessions with clients to remove")
                
            elif choice == "7":
                print("\n➕ Creating new time slot...")
                date = input("Date (MM/DD/YYYY) [today]: ").strip()
                if not date:
                    date = datetime.now().strftime("%m/%d/%Y")
                
                start_time = input("Start time (HH:MM): ").strip()
                end_time = input("End time (HH:MM): ").strip()
                
                print("Event types: 1=Personal Training, 2=Small Group, 3=Group Class")
                event_type_choice = input("Event type (1-3): ").strip()
                
                event_type_map = {
                    "1": "personal_training",
                    "2": "small_group_training", 
                    "3": "group_training"
                }
                event_type = event_type_map.get(event_type_choice, "personal_training")
                
                capacity_map = {
                    "personal_training": 1,
                    "small_group_training": 6,
                    "group_training": 12
                }
                max_capacity = capacity_map.get(event_type, 1)
                
                new_event_id = calendar.create_new_event(
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    event_type=event_type,
                    max_capacity=max_capacity
                )
                
                if new_event_id:
                    print(f"✅ Successfully created new {event_type.replace('_', ' ')} slot")
                    print(f"   Time: {start_time}-{end_time} on {date}")
                    print(f"   Capacity: {max_capacity} clients")
                else:
                    print("❌ Failed to create new time slot")
                
            elif choice == "8":
                print("\n📊 Calendar Summary")
                calendar.print_calendar_summary()
                
            elif choice == "9":
                print("\n🔄 Refreshing calendar data...")
                current_events = calendar.get_calendar_events(use_cache=False)
                print("✅ Calendar refreshed!")
                
            elif choice == "0":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please select 0-9.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run the interactive calendar management system"""
    interactive_menu()

if __name__ == "__main__":
    main()
