import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from config.secrets import get_clubos_credentials
import re
from datetime import datetime as dt
import argparse
from twilio.rest import Client

CLUBOS_LOGIN_URL = "https://anytime.club-os.com/action/Login/view"
CALENDAR_URL = "https://anytime.club-os.com/action/Calendar"
SCHEDULE_NAME = "My schedule"

# Twilio notification function
async def notify_via_twilio(message):
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        to_number = os.getenv('TWILIO_TO_NUMBER')
        if not all([account_sid, auth_token, from_number, to_number]):
            print('[WARN] Twilio credentials not set, cannot send SMS notification.')
            return
        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_number, to=to_number)
        print('[INFO] Sent error notification via Twilio.')
    except Exception as e:
        print(f'[ERROR] Failed to send Twilio SMS: {e}')

async def main():
    parser = argparse.ArgumentParser(description='Automate ClubOS session creation.')
    parser.add_argument('--member', type=str, required=True, help='Member name (e.g., "Grace Sphatt")')
    parser.add_argument('--time', type=str, required=True, help='Session time (e.g., "10:00 AM")')
    parser.add_argument('--date', type=str, required=False, help='Session date (YYYY-MM-DD, default: tomorrow)')
    parser.add_argument('--debug', action='store_true', help='Enable debug prints and screenshots')
    args = parser.parse_args()

    member_name = args.member
    session_time = args.time
    session_date = args.date or (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    debug = args.debug

    try:
        creds = get_clubos_credentials()
        username = creds["username"]
        password = creds["password"]
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        day_str = tomorrow.strftime("%A")
        session_title = "Personal Training Session (API)"
        start_time = "09:00"
        end_time = "10:00"
        member_name = "Grace Sphatt"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            print("[INFO] Navigating to login page...")
            await page.goto(CLUBOS_LOGIN_URL)
            await page.wait_for_selector('input[name="username"]', timeout=20000)
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('.js-login')
            await page.wait_for_selector('#quick-search-text', timeout=60000)
            print("[INFO] Login successful.")
            print("[INFO] Navigating to calendar page...")
            await page.goto(CALENDAR_URL)
            await page.wait_for_load_state('networkidle')
            # Wait for calendar to load
            await page.wait_for_selector('#change-view', timeout=20000)
            await page.select_option('#change-view', label=SCHEDULE_NAME)
            await asyncio.sleep(3)
            await page.evaluate("document.body.style.zoom='20%'")
            await page.wait_for_selector('#schedule', timeout=20000)
            schedule_table = await page.query_selector('#schedule')
            header_row = await schedule_table.query_selector('tr.calendar-head')
            day_headers = await header_row.query_selector_all('th')
            day_columns = {}
            for idx, header in enumerate(day_headers[1:-1]):
                p_elem = await header.query_selector('p.primary')
                day_name = (await p_elem.inner_text()).strip()
                day_columns[day_name] = idx
            print(f"[DEBUG] Detected day columns: {list(day_columns.keys())}")
            # Try to match tomorrow's column by full date string, then by weekday name
            tomorrow_abbr = tomorrow.strftime('%a %b %d')
            tomorrow_full = tomorrow.strftime('%A')
            col_idx = None
            for day_name, idx in day_columns.items():
                if tomorrow_abbr in day_name:
                    col_idx = idx
                    print(f"[DEBUG] Matched tomorrow's column by abbr: {day_name}")
                    break
            if col_idx is None:
                for day_name, idx in day_columns.items():
                    if tomorrow_full == day_name:
                        col_idx = idx
                        print(f"[DEBUG] Matched tomorrow's column by weekday: {day_name}")
                        break
            if col_idx is None:
                print(f"[ERROR] Could not find column for {tomorrow_abbr} or {tomorrow_full} in calendar.")
                await browser.close()
                return
            time_rows = await schedule_table.query_selector_all('tbody > tr:not(.calendar-head):not(.am-pm)')
            # Parse all slots for tomorrow's column, print times and statuses
            slots = []
            for row in time_rows:
                day_cells = await row.query_selector_all('td')
                cell = day_cells[col_idx+1]  # skip first col
                time_text_elem = await cell.query_selector('span:not(.avail-location)')
                time_text = (await time_text_elem.inner_text()).strip() if time_text_elem else ''
                if not time_text:
                    continue
                slot_details = {"time": time_text, "status": "Unknown", "cell": cell}
                try:
                    event_container = await cell.query_selector('div.cal-event-container')
                    if event_container:
                        icon = await event_container.query_selector('img')
                        event_title = await icon.get_attribute('title') if icon else ''
                        if "Small Group Training" in event_title or "Group Training" in event_title:
                            slot_details["status"] = "Group Training"
                        elif "Personal Training" in event_title:
                            slot_details["status"] = "Personal Training"
                        elif "Appointment" in event_title:
                            slot_details["status"] = "Appointment"
                        else:
                            slot_details["status"] = "Booked"
                    else:
                        slot_details["status"] = "Available"
                except Exception:
                    slot_details["status"] = "Available"
                slots.append(slot_details)
            print(f"[DEBUG] All slots for {tomorrow_abbr}:")
            for slot in slots:
                print(f"  - {slot['time']} ({slot['status']})")
            # Find the first available slot at or after 9am
            target_time = dt.strptime(start_time, "%H:%M")
            slot_clicked = False
            for slot in slots:
                # Extract HH:MM from slot['time']
                match = re.search(r'(\d{2}:\d{2})', slot["time"])
                slot_time_str = match.group(1) if match else ''
                try:
                    slot_time = dt.strptime(slot_time_str, "%H:%M")
                except Exception:
                    continue
                if slot["status"] == "Available" and slot_time >= target_time:
                    print(f"[INFO] Clicking available slot at {slot['time']} (parsed {slot_time_str})...")
                    await slot["cell"].click()
                    slot_clicked = True
                    break
            if not slot_clicked:
                print(f"[ERROR] Could not find available slot at or after {start_time} for {tomorrow_abbr}.")
                await browser.close()
                return
            # Print all visible input and textarea fields after clicking the slot
            await asyncio.sleep(2)
            form_inputs = await page.query_selector_all('input, textarea')
            print("[DEBUG] Visible input/textarea fields after slot click:")
            for i, inp in enumerate(form_inputs):
                html = await inp.evaluate('(el) => el.outerHTML')
                print(f"  [{i}] {html}")
            # Wait for session form to appear
            # (Removed: await page.wait_for_selector('input[name="title"]', timeout=20000))
            await page.fill('input[name="calendarEvent.subject"]', session_title)
            await page.fill('textarea[name="calendarEvent.notes"]', f"PT session for {member_name}")
            # Add Grace Sphatt as attendee (robust: type full name, wait, then click dropdown)
            attendee_field = await page.query_selector('input[name="attendeeSearchText"]')
            if attendee_field:
                # Optionally set zoom to 100% for stability
                await page.evaluate("document.body.style.zoom='100%'")
                await attendee_field.click()
                await attendee_field.fill("")
                await attendee_field.type(member_name)  # Type full name, no delay
                print(f"[DEBUG] Typed '{member_name}' in attendee field. Waiting 20 seconds for dropdown...")
                await page.screenshot(path="after_typing_attendee.png")
                await asyncio.sleep(20)  # Wait 20 seconds for dropdown to populate and stabilize
                await page.screenshot(path="after_waiting_20s_for_dropdown.png")

                # Resize the modal to ensure dropdown is visible
                try:
                    await page.evaluate("""
                        var modal = document.getElementById('add-event-popup');
                        if (modal) {
                            modal.style.width = '900px';
                            modal.style.height = '700px';
                            modal.style.maxWidth = 'none';
                            modal.style.maxHeight = 'none';
                        }
                    """)
                    print("[DEBUG] Resized #add-event-popup modal to 900x700px.")
                except Exception as e:
                    print(f"[WARN] Could not resize modal: {e}")

                # Now try to click the correct <li> for Grace Sphatt
                try:
                    li = await page.wait_for_selector(
                        "div.quick-search.small-popup ul.search-results li.person >> text=Grace Sphatt",
                        timeout=3000,
                        state="visible"
                    )
                    print("[DEBUG] Found <li> for Grace Sphatt, clicking...")
                    await li.click()
                    print(f"[INFO] Clicked attendee: {member_name}")

                    # Reset zoom to 100% before saving
                    await page.evaluate("document.body.style.zoom='100%'")
                    print("[DEBUG] Reset zoom to 100% before saving.")

                    # Click the Save event button
                    save_btn = await page.wait_for_selector('#save-event', timeout=5000)
                    print("[DEBUG] Found Save event button, clicking...")
                    await save_btn.click()

                    # Wait for the modal to close (become hidden, not detached)
                    print("[DEBUG] Waiting for modal to become hidden (#add-event-popup)...")
                    await page.wait_for_selector('#add-event-popup', state='hidden', timeout=20000)
                    print(f"[SUCCESS] Appointment for '{member_name}' booked successfully.")
                except Exception as e:
                    print(f"[ERROR] Could not find or click attendee '{member_name}' or save event: {e}")
            else:
                print(f"[ERROR] Could not find attendee search field for {member_name}.")
            # Submit the form
            await page.click('.js-submit')
            await asyncio.sleep(3)
            print(f"[SUCCESS] Session for {member_name} at {start_time} on {tomorrow_abbr} created (if no errors above).")
            await browser.close()
    except Exception as e:
        await notify_via_twilio(f"ClubOS script error: {e}")
        raise

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 