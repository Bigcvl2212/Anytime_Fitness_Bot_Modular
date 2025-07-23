import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from config.secrets import get_clubos_credentials

CLUBOS_LOGIN_URL = "https://anytime.club-os.com/action/Login/view"
CALENDAR_URL = "https://anytime.club-os.com/action/Calendar"
SCHEDULE_NAME = "My schedule"

async def main():
    creds = get_clubos_credentials()
    username = creds["username"]
    password = creds["password"]
    today_str = datetime.now().strftime('%A')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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
        time_rows = await schedule_table.query_selector_all('tbody > tr:not(.calendar-head):not(.am-pm)')
        calendar_data = {}
        for row in time_rows:
            day_cells = await row.query_selector_all('td')
            for day_name, col_idx in day_columns.items():
                if day_name not in calendar_data:
                    calendar_data[day_name] = []
                cell = day_cells[col_idx+1]  # skip first col
                time_text_elem = await cell.query_selector('span:not(.avail-location)')
                time_text = (await time_text_elem.inner_text()).strip() if time_text_elem else ''
                if not time_text:
                    continue
                slot_details = {"time": time_text, "status": "Unknown"}
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
                calendar_data[day_name].append(slot_details)
        await page.evaluate("document.body.style.zoom='100%'")
        print(f"\nAvailable slots for today ({today_str}):")
        slots_today = calendar_data.get(today_str, [])
        available_slots = [slot for slot in slots_today if slot.get('status') == 'Available']
        if available_slots:
            for slot in available_slots:
                print(f"  - {slot['time']}")
        else:
            print("  No available slots for today.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 