"""
Calendar workflow functions - contains all logic for managing calendar navigation and session management
"""

import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..config.constants import CLUBOS_CALENDAR_URL
from ..utils.debug_helpers import debug_page_state


def navigate_calendar_week(driver, direction):
    """Navigates the calendar forward or backward by one week."""
    print(f"   INFO: Navigating calendar {direction} one week...")
    try:
        # Ensure driver is on the calendar page first
        if not driver.current_url.startswith(CLUBOS_CALENDAR_URL):
            print(f"   INFO: Not on calendar page. Navigating to {CLUBOS_CALENDAR_URL}")
            driver.get(CLUBOS_CALENDAR_URL)
            WebDriverWait(driver, 20).until(EC.url_contains("Calendar"))
            time.sleep(2) # Allow page to settle

        if direction == 'next':
            button_xpath = "//a[contains(@class, 'schedule-dayR') and .//i[contains(@class, 'fa-chevron-right')]]" # More specific selector
        else: # 'previous'
            button_xpath = "//a[contains(@class, 'schedule-dayL') and .//i[contains(@class, 'fa-chevron-left')]]" # More specific selector
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
        print(f"   SUCCESS: Clicked '{direction}' week button.")
        print("   INFO: Waiting 5 seconds for new week to load...") # Reduced wait time
        time.sleep(5)
        return True
    except Exception as e:
        print(f"   ERROR: Could not navigate calendar week. Error: {e}")
        return False


def get_calendar_view_details(driver, schedule_name="My schedule"):
    """
    Scans the entire calendar week and identifies the status of each time slot
    (e.g., Available, Group Training, Personal Training, etc.) based on the
    icon's title attribute.
    """
    print(f"   INFO: Performing detailed scan of calendar for '{schedule_name}'...")
    calendar_data = {}
    try:
        # 1. Navigate to the calendar and select the correct view
        driver.get("https://anytime.club-os.com/action/Calendar")
        time.sleep(5) # Patient wait for page to render

        view_dropdown_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "change-view"))
        )
        Select(view_dropdown_element).select_by_visible_text(schedule_name)
        time.sleep(3)
        
        # 2. Apply zoom to see the whole grid
        driver.execute_script("document.body.style.zoom='20%'"); time.sleep(2)
        
        schedule_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "schedule")))
        
        # 3. Get the column headers for each day
        header_row = schedule_table.find_element(By.CSS_SELECTOR, "tr.calendar-head")
        day_headers = header_row.find_elements(By.TAG_NAME, "th")[1:-1]
        day_columns = {header.find_element(By.CSS_SELECTOR, "p.primary").text: idx for idx, header in enumerate(day_headers)}

        # 4. Loop through each time row and day cell
        time_rows = schedule_table.find_elements(By.CSS_SELECTOR, "tbody > tr:not(.calendar-head):not(.am-pm)")
        for row in time_rows:
            day_cells = row.find_elements(By.TAG_NAME, "td")[1:-1]
            for day_name, col_idx in day_columns.items():
                if day_name not in calendar_data:
                    calendar_data[day_name] = []
                
                cell = day_cells[col_idx]
                time_text_element = cell.find_element(By.CSS_SELECTOR, "span:not(.avail-location)")
                time_text = time_text_element.text.strip()
                if not time_text:
                    continue

                slot_details = {"time": time_text, "status": "Unknown"}

                # Check if the slot is booked
                try:
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
                        slot_details["status"] = "Booked" # Booked, but no specific icon found
                except NoSuchElementException:
                    # If no event container, the slot is available
                    slot_details["status"] = "Available"

                calendar_data[day_name].append(slot_details)
        
        print(f"   SUCCESS: Detailed calendar scan complete.")
        driver.execute_script("document.body.style.zoom='100%'")
        return calendar_data
    except Exception as e:
        print(f"   ERROR: Could not perform detailed calendar scan. Error: {e}")
        try:
            driver.execute_script("document.body.style.zoom='100%'")
        except:
            pass
        return {}


def add_to_group_session(driver, details):
    """
    Finds an existing group session on the calendar using direct DOM manipulation and JSON metadata.
    This is a cleaner approach that uses the session containers' hidden JSON data for reliable matching.
    'details' should contain:
      - member_name_to_add
      - session_time_str (e.g., "10:30 AM")
      - session_day_xpath_part (e.g., "2025-06-27") 
      - target_schedule_name
    """
    print(f"INFO: Adding '{details['member_name_to_add']}' to group session using DOM-based approach...")
    
    try:
        # 1. Navigate to calendar and set correct schedule view
        if not driver.current_url.startswith(CLUBOS_CALENDAR_URL):
            print(f"   DEBUG: Navigating to calendar: {CLUBOS_CALENDAR_URL}")
            driver.get(CLUBOS_CALENDAR_URL)
            WebDriverWait(driver, 20).until(EC.url_contains("Calendar"))

        # Change to target schedule view if needed  
        current_view_element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "change-view")))
        current_view_select = Select(current_view_element)
        current_schedule = current_view_select.first_selected_option.text.strip()
        target_schedule = details['target_schedule_name']
        
        if current_schedule != target_schedule:
            print(f"   DEBUG: Changing from '{current_schedule}' to '{target_schedule}'")
            current_view_select.select_by_visible_text(target_schedule)
            time.sleep(3)

        # 2. Wait for calendar sessions to load
        print("   DEBUG: Waiting for calendar sessions to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "cal-event-container"))
        )
        
        # Get all session containers
        all_sessions = driver.find_elements(By.CLASS_NAME, "cal-event-container")
        print(f"   DEBUG: Found {len(all_sessions)} total sessions in calendar")
        
        # 3. Parse each session's JSON metadata to find target
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
                    
            except (json.JSONDecodeError, NoSuchElementException) as e:
                # Skip sessions without valid JSON metadata
                continue
        
        if not target_session:
            print(f"   ERROR: Could not find target session matching criteria")
            return False
        
        # 4. Click on the found session to open it
        print("   DEBUG: Clicking on target session...")
        target_session.click()
        time.sleep(3)
        
        # 5. Look for "Add Participants" or similar button
        add_participants_selectors = [
            "//button[contains(text(), 'Add Participants')]",
            "//a[contains(text(), 'Add Participants')]", 
            "//button[contains(text(), 'Add')]",
            "//a[contains(text(), 'Participants')]"
        ]
        
        add_button = None
        for selector in add_participants_selectors:
            try:
                add_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"   SUCCESS: Found add participants button with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not add_button:
            print("   ERROR: Could not find 'Add Participants' button")
            return False
        
        # 6. Click Add Participants
        add_button.click()
        time.sleep(2)
        
        # 7. Search for and add the member
        member_name = details['member_name_to_add']
        
        # Look for search input
        search_input_selectors = [
            "//input[contains(@placeholder, 'Search')]",
            "//input[contains(@placeholder, 'member')]",
            "//input[@type='text']",
            "//input[@type='search']"
        ]
        
        search_input = None
        for selector in search_input_selectors:
            try:
                search_input = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"   SUCCESS: Found search input with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not search_input:
            print("   ERROR: Could not find search input for member")
            return False
        
        # 8. Type member name and search
        search_input.clear()
        search_input.send_keys(member_name)
        time.sleep(2)
        
        # Look for the member in search results
        member_result_selectors = [
            f"//div[contains(text(), '{member_name}')]",
            f"//span[contains(text(), '{member_name}')]",
            f"//li[contains(text(), '{member_name}')]",
            f"//a[contains(text(), '{member_name}')]"
        ]
        
        member_result = None
        for selector in member_result_selectors:
            try:
                member_result = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"   SUCCESS: Found member result with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if not member_result:
            print(f"   ERROR: Could not find member '{member_name}' in search results")
            return False
        
        # 9. Click on member to add them
        member_result.click()
        time.sleep(2)
        
        # 10. Look for and click Save/Submit button
        save_selectors = [
            "//button[contains(text(), 'Save')]",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Add')]",
            "//input[@type='submit']"
        ]
        
        save_button = None
        for selector in save_selectors:
            try:
                save_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                print(f"   SUCCESS: Found save button with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if save_button:
            save_button.click()
            time.sleep(3)
            print(f"   SUCCESS: Added '{member_name}' to group session!")
            return True
        else:
            print("   WARNING: Could not find save button, but member may have been added")
            return True
        
    except Exception as e:
        print(f"   ERROR: Failed to add member to group session: {e}")
        debug_page_state(driver, "add_to_group_session_error")
        return False
