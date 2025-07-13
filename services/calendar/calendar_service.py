"""
Enhanced Calendar Service - VERIFIED SELECTORS FROM EXPERIMENTAL CODE
Uses the proven, tested selectors and steps from worker2.0.py for reliable calendar operations.
"""

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ...config.constants import CLUBOS_CALENDAR_URL
from ...utils.debug_helpers import debug_page_state


class EnhancedCalendarService:
    """
    Enhanced calendar service using verified selectors and steps from experimental code.
    Based on VERIFIED WORKING CODE from worker2.0.py
    """
    
    def __init__(self, driver):
        """Initialize calendar service with driver"""
        self.driver = driver
    
    def get_available_slots(self, schedule_name: str = "My schedule") -> List[str]:
        """
        Navigates to the calendar and scrapes available time slots.
        
        VERIFIED WORKING CODE FROM WORKER2.0.PY
        """
        print(f"📅 Reading calendar for '{schedule_name}'...")
        try:
            self.driver.get(CLUBOS_CALENDAR_URL)
            
            print("   INFO: Selecting calendar view...")
            # VERIFIED SELECTOR: change-view dropdown
            view_dropdown = Select(WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "change-view"))
            ))
            view_dropdown.select_by_visible_text(schedule_name)
            print(f"   SUCCESS: Switched to '{schedule_name}'.")
            time.sleep(2)

            # VERIFIED SELECTOR: td.available for available slots
            available_slots = self.driver.find_elements(By.CSS_SELECTOR, "td.available")
            slot_times = [
                slot.find_element(By.CSS_SELECTOR, "span").text 
                for slot in available_slots 
                if slot.find_element(By.CSS_SELECTOR, "span").text
            ]
            print(f"   SUCCESS: Found {len(slot_times)} available slots: {slot_times}")
            return slot_times
            
        except Exception as e:
            print(f"   ERROR: Could not get available slots. Error: {e}")
            debug_page_state(self.driver, "calendar_available_slots_failed")
            return []
    
    def book_appointment(self, details: Dict[str, Any]) -> bool:
        """
        Books an appointment using the detailed blueprint from experimental code.
        
        VERIFIED WORKING CODE FROM WORKER2.0.PY
        """
        print(f"📅 Starting appointment booking for '{details['member_name']}'...")
        try:
            # STEP 1: Find and click the time slot
            # VERIFIED SELECTOR: XPath for available time slots
            time_slot_xpath = f"//td[contains(@class, 'available') and .//span[normalize-space(.)=\"{details['time']}\"]]"
            target_slot = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, time_slot_xpath))
            )
            target_slot.click()
            print(f"   SUCCESS: Clicked on the '{details['time']}' time slot.")

            # STEP 2: Wait for appointment popup
            # VERIFIED SELECTOR: add-edit-event-holder popup
            popup = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "add-edit-event-holder"))
            )
            print("   SUCCESS: Appointment popup is visible.")

            # STEP 3: Add attendee
            # VERIFIED SELECTOR: attendeeSearchText input
            attendee_search_box = popup.find_element(By.NAME, "attendeeSearchText")
            attendee_search_box.send_keys(details['member_name'])
            time.sleep(3)
            
            # VERIFIED SELECTOR: search-result div with case-insensitive matching
            member_name_lower = details['member_name'].lower()
            contact_result_xpath = f"//div[@class='search-result' and normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{member_name_lower}']"
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, contact_result_xpath))
            ).click()
            print(f"   SUCCESS: Added '{details['member_name']}' to event.")
            
            # STEP 4: Set event type
            # VERIFIED SELECTOR: calendarEvent.eventType dropdown
            Select(popup.find_element(By.NAME, "calendarEvent.eventType")).select_by_value(details['event_type'])
            print(f"   SUCCESS: Set event type to '{details['event_type']}'.")
            
            # STEP 5: Configure repeating schedule (if needed)
            if details.get("repeats", False):
                # VERIFIED SELECTOR: calendarEvent.repeat checkbox
                popup.find_element(By.NAME, "calendarEvent.repeat").click()
                
                # VERIFIED SELECTOR: Individual day checkboxes
                for day in details.get("repeat_days", []):
                    popup.find_element(By.NAME, f"calendarEvent.repeatEvent.{day}").click()
                
                # VERIFIED SELECTOR: End type radio button
                if details.get("ends", "never") == "never":
                    popup.find_element(By.CSS_SELECTOR, "input[name='calendarEvent.repeatEvent.endType'][value='never']").click()
                print("   INFO: Configured repeating schedule.")
            
            # STEP 6: Save the event
            # VERIFIED SELECTOR: save-event button
            popup.find_element(By.ID, "save-event").click()
            print("   ACTION: Clicked 'Save event'.")
            
            # VERIFIED SELECTOR: Wait for popup to disappear
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.ID, "add-edit-event-holder"))
            )
            print(f"SUCCESS: Appointment for '{details['member_name']}' booked successfully.")
            return True
            
        except Exception as e:
            print(f"   ERROR: Failed during appointment booking. Error: {e}")
            debug_page_state(self.driver, "calendar_booking_failed")
            return False
    
    def navigate_calendar_week(self, direction: str = 'next') -> bool:
        """
        Navigates the calendar forward or backward by one week.
        
        VERIFIED WORKING CODE FROM CURRENT SYSTEM
        """
        print(f"   INFO: Navigating calendar {direction} one week...")
        try:
            # Ensure driver is on the calendar page first
            if not self.driver.current_url.startswith(CLUBOS_CALENDAR_URL):
                print(f"   INFO: Not on calendar page. Navigating to {CLUBOS_CALENDAR_URL}")
                self.driver.get(CLUBOS_CALENDAR_URL)
                WebDriverWait(self.driver, 20).until(EC.url_contains("Calendar"))
                time.sleep(2)  # Allow page to settle

            # VERIFIED SELECTORS: Navigation buttons
            if direction == 'next':
                button_xpath = "//a[contains(@class, 'schedule-dayR') and .//i[contains(@class, 'fa-chevron-right')]]"
            else:  # 'previous'
                button_xpath = "//a[contains(@class, 'schedule-dayL') and .//i[contains(@class, 'fa-chevron-left')]]"
            
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            ).click()
            print(f"   SUCCESS: Clicked '{direction}' week button.")
            print("   INFO: Waiting 5 seconds for new week to load...")
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"   ERROR: Could not navigate calendar week. Error: {e}")
            return False
    
    def get_calendar_view_details(self, schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
        """
        Scans the entire calendar week and identifies the status of each time slot.
        
        VERIFIED WORKING CODE FROM CURRENT SYSTEM
        """
        print(f"   INFO: Performing detailed scan of calendar for '{schedule_name}'...")
        calendar_data = {}
        try:
            # STEP 1: Navigate to calendar and select view
            self.driver.get(CLUBOS_CALENDAR_URL)
            time.sleep(5)  # Patient wait for page to render

            # VERIFIED SELECTOR: change-view dropdown
            view_dropdown_element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "change-view"))
            )
            Select(view_dropdown_element).select_by_visible_text(schedule_name)
            time.sleep(3)
            
            # STEP 2: Apply zoom to see the whole grid
            self.driver.execute_script("document.body.style.zoom='20%'")
            time.sleep(2)
            
            # VERIFIED SELECTOR: schedule table
            schedule_table = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "schedule"))
            )
            
            # STEP 3: Get column headers for each day
            header_row = schedule_table.find_element(By.CSS_SELECTOR, "tr.calendar-head")
            day_headers = header_row.find_elements(By.TAG_NAME, "th")[1:-1]
            day_columns = {
                header.find_element(By.CSS_SELECTOR, "p.primary").text: idx 
                for idx, header in enumerate(day_headers)
            }

            # STEP 4: Loop through each time row and day cell
            time_rows = schedule_table.find_elements(By.CSS_SELECTOR, "tbody > tr:not(.calendar-head):not(.am-pm)")
            for row in time_rows:
                day_cells = row.find_elements(By.TAG_NAME, "td")[1:-1]
                for day_name, col_idx in day_columns.items():
                    if day_name not in calendar_data:
                        calendar_data[day_name] = []
                    
                    cell = day_cells[col_idx]
                    # VERIFIED SELECTOR: span:not(.avail-location) for time text
                    time_text_element = cell.find_element(By.CSS_SELECTOR, "span:not(.avail-location)")
                    time_text = time_text_element.text.strip()
                    if not time_text:
                        continue

                    slot_details = {"time": time_text, "status": "Unknown"}

                    # Check if the slot is booked
                    try:
                        # VERIFIED SELECTOR: cal-event-container for booked slots
                        event_container = cell.find_element(By.CSS_SELECTOR, "div.cal-event-container")
                        # If an event exists, check its type by the icon title
                        try:
                            icon = event_container.find_element(By.TAG_NAME, "img")
                            event_title = icon.get_attribute("title")
                            if "Small Group Training" in event_title or "Group Training" in event_title:
                                slot_details["status"] = "Group Training"
                            elif "Personal Training" in event_title:
                                slot_details["status"] = "Personal Training"
                            elif "Appointment" in event_title:
                                slot_details["status"] = "Appointment"
                            else:
                                slot_details["status"] = "Booked"
                        except NoSuchElementException:
                            slot_details["status"] = "Booked"  # Booked, but no specific icon found
                    except NoSuchElementException:
                        # If no event container, the slot is available
                        slot_details["status"] = "Available"

                    calendar_data[day_name].append(slot_details)
            
            print(f"   SUCCESS: Detailed calendar scan complete.")
            self.driver.execute_script("document.body.style.zoom='100%'")
            return calendar_data
            
        except Exception as e:
            print(f"   ERROR: Could not perform detailed calendar scan. Error: {e}")
            try:
                self.driver.execute_script("document.body.style.zoom='100%'")
            except:
                pass
            return {}
    
    def add_to_group_session(self, details: Dict[str, Any]) -> bool:
        """
        Adds a member to an existing group session using DOM-based approach.
        
        VERIFIED WORKING CODE FROM CURRENT SYSTEM
        """
        print(f"📅 Adding '{details['member_name_to_add']}' to group session using DOM-based approach...")
        
        try:
            # STEP 1: Navigate to calendar and set correct schedule view
            if not self.driver.current_url.startswith(CLUBOS_CALENDAR_URL):
                print(f"   DEBUG: Navigating to calendar: {CLUBOS_CALENDAR_URL}")
                self.driver.get(CLUBOS_CALENDAR_URL)
                WebDriverWait(self.driver, 20).until(EC.url_contains("Calendar"))

            # Change to target schedule view if needed  
            current_view_element = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "change-view"))
            )
            current_view_select = Select(current_view_element)
            current_schedule = current_view_select.first_selected_option.text.strip()
            target_schedule = details['target_schedule_name']
            
            if current_schedule != target_schedule:
                print(f"   DEBUG: Changing from '{current_schedule}' to '{target_schedule}'")
                current_view_select.select_by_visible_text(target_schedule)
                time.sleep(3)

            # STEP 2: Wait for calendar sessions to load
            print("   DEBUG: Waiting for calendar sessions to load...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "cal-event-container"))
            )
            
            # Get all session containers
            all_sessions = self.driver.find_elements(By.CLASS_NAME, "cal-event-container")
            print(f"   DEBUG: Found {len(all_sessions)} total sessions in calendar")
            
            # STEP 3: Parse each session's JSON metadata to find target
            target_session = None
            target_event_ids = ["2", "8"]  # Personal Training and Small Group Training
            
            # Parse the target date and time
            target_date_str = details['session_day_xpath_part']  # e.g., "2025-06-27"
            target_time_str = details['session_time_str']  # e.g., "10:30 AM"
            
            print(f"   DEBUG: Searching for sessions matching:")
            print(f"     - Event types: {target_event_ids} (Personal/Small Group Training)")
            print(f"     - Target time: {target_time_str}")
            print(f"     - Target date: {target_date_str}")
            
            for i, session in enumerate(all_sessions):
                try:
                    # Extract JSON metadata from hidden input
                    hidden_input = session.find_element(By.XPATH, ".//input[@type='hidden']")
                    session_json_str = hidden_input.get_attribute("value")
                    session_data = json.loads(session_json_str)
                    
                    # Check if this matches our criteria
                    session_event_type = str(session_data.get("eventTypeId", ""))
                    session_start_time = session_data.get("startTime", "")
                    session_date = session_data.get("startDate", "")
                    
                    # Debug output for first few sessions
                    if i < 3:
                        print(f"   DEBUG: Session {i}: Type={session_event_type}, Date={session_date}, Time={session_start_time}")
                    
                    # Match by event type, date, and time
                    if (session_event_type in target_event_ids and 
                        target_date_str in session_date and 
                        target_time_str in session_start_time):
                        
                        target_session = session
                        print(f"   SUCCESS: Found matching session!")
                        print(f"     - Event Type: {session_event_type}")
                        print(f"     - Date: {session_date}")
                        print(f"     - Time: {session_start_time}")
                        break
                        
                except Exception as e:
                    print(f"   WARN: Error parsing session {i}: {e}")
                    continue
            
            if not target_session:
                print(f"   ERROR: Could not find matching session for criteria")
                return False
            
            # STEP 4: Click on the session to open edit dialog
            target_session.click()
            print("   SUCCESS: Clicked on target session.")
            
            # STEP 5: Wait for edit dialog and add attendee
            edit_dialog = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "add-edit-event-holder"))
            )
            print("   SUCCESS: Edit dialog opened.")
            
            # Add the new attendee
            attendee_search = edit_dialog.find_element(By.NAME, "attendeeSearchText")
            attendee_search.send_keys(details['member_name_to_add'])
            time.sleep(3)
            
            # Click on the search result
            member_name_lower = details['member_name_to_add'].lower()
            attendee_result_xpath = f"//div[@class='search-result' and normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{member_name_lower}']"
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, attendee_result_xpath))
            ).click()
            print(f"   SUCCESS: Added '{details['member_name_to_add']}' to session.")
            
            # STEP 6: Save the changes
            save_button = edit_dialog.find_element(By.ID, "save-event")
            save_button.click()
            print("   SUCCESS: Saved session changes.")
            
            # Wait for dialog to close
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located((By.ID, "add-edit-event-holder"))
            )
            print(f"SUCCESS: '{details['member_name_to_add']}' added to group session.")
            return True
            
        except Exception as e:
            print(f"   ERROR: Failed to add member to group session. Error: {e}")
            debug_page_state(self.driver, "calendar_add_to_session_failed")
            return False


# Convenience functions for backward compatibility
def get_available_slots(driver, schedule_name: str = "My schedule") -> List[str]:
    """Get available calendar slots using verified selectors"""
    service = EnhancedCalendarService(driver)
    return service.get_available_slots(schedule_name)


def book_appointment(driver, details: Dict[str, Any]) -> bool:
    """Book appointment using verified selectors"""
    service = EnhancedCalendarService(driver)
    return service.book_appointment(details)


def navigate_calendar_week(driver, direction: str = 'next') -> bool:
    """Navigate calendar week using verified selectors"""
    service = EnhancedCalendarService(driver)
    return service.navigate_calendar_week(direction)


def get_calendar_view_details(driver, schedule_name: str = "My schedule") -> Dict[str, List[Dict]]:
    """Get calendar view details using verified selectors"""
    service = EnhancedCalendarService(driver)
    return service.get_calendar_view_details(schedule_name)


def add_to_group_session(driver, details: Dict[str, Any]) -> bool:
    """Add member to group session using verified selectors"""
    service = EnhancedCalendarService(driver)
    return service.add_to_group_session(details) 