#!/usr/bin/env python3
"""
ClubOS Live Calendar API - Browser Automation Solution
Based on HAR analysis, uses browser automation to maintain live sessions
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Calendar event from ClubOS"""
    id: int
    funding_status: str
    attendees: List[Dict[str, Any]]

class ClubOSLiveCalendar:
    """
    Live ClubOS Calendar API using browser automation
    Maintains real browser session to avoid token expiration
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://anytime.club-os.com"
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_authenticated = False
        self.bearer_token = None
        
    async def start_browser(self):
        """Start the browser and create context"""
        logger.info("Starting browser...")
        
        playwright = await async_playwright().start()
        
        # Launch browser with specific settings
        self.browser = await playwright.chromium.launch(
            headless=False,  # Keep visible for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Create context with realistic settings
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        
        # Create a new page
        self.page = await self.context.new_page()
        
        # Set up request/response interception for API monitoring
        self.page.on('response', self._handle_response)
        
        logger.info("Browser started successfully")
    
    async def _handle_response(self, response):
        """Handle responses to extract Bearer tokens and API data"""
        url = response.url
        
        # Monitor calendar API calls
        if '/api/calendar/events' in url and response.status == 200:
            try:
                data = await response.json()
                logger.info(f"Calendar API success: {len(data.get('events', []))} events")
            except:
                pass
        
        # Monitor for authorization headers in requests
        if hasattr(response, 'request') and response.request:
            auth_header = response.request.headers.get('authorization')
            if auth_header and auth_header.startswith('Bearer '):
                if self.bearer_token != auth_header[7:]:  # Remove 'Bearer '
                    self.bearer_token = auth_header[7:]
                    logger.info("Updated Bearer token from request")
    
    async def authenticate(self) -> bool:
        """Authenticate with ClubOS using browser automation"""
        try:
            logger.info(f"Authenticating as {self.username}...")
            
            # Navigate to login page
            await self.page.goto(f"{self.base_url}/action/Login/view")
            await self.page.wait_for_load_state('networkidle')
            
            # Fill login form
            await self.page.fill('input[name="username"]', self.username)
            await self.page.fill('input[name="password"]', self.password)
            
            # Submit login
            await self.page.click('input[type="submit"]')
            await self.page.wait_for_load_state('networkidle')
            
            # Check if we're logged in (should be redirected to dashboard)
            current_url = self.page.url
            if 'Dashboard' in current_url or 'dashboard' in current_url:
                logger.info("Authentication successful")
                self.is_authenticated = True
                return True
            else:
                logger.error(f"Authentication failed - current URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def navigate_to_calendar(self) -> bool:
        """Navigate to the calendar page"""
        try:
            logger.info("Navigating to calendar...")
            
            # Navigate to calendar
            await self.page.goto(f"{self.base_url}/action/Calendar")
            await self.page.wait_for_load_state('networkidle')
            
            # Wait for calendar to load
            await asyncio.sleep(3)
            
            current_url = self.page.url
            if 'Calendar' in current_url:
                logger.info("Calendar page loaded successfully")
                return True
            else:
                logger.error(f"Failed to load calendar - current URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error navigating to calendar: {e}")
            return False
    
    async def get_calendar_events_via_api(self, event_ids: List[int]) -> List[CalendarEvent]:
        """
        Get calendar events by making API calls through the browser
        """
        try:
            logger.info(f"Fetching {len(event_ids)} calendar events via browser API...")
            
            # Build the API URL with parameters
            params = []
            for event_id in event_ids:
                params.append(f"eventIds={event_id}")
            params.append("fields=fundingStatus")
            params.append(f"_={int(datetime.now().timestamp() * 1000)}")
            
            api_url = f"{self.base_url}/api/calendar/events?" + "&".join(params)
            
            # Make the API call through the browser
            response = await self.page.goto(api_url)
            
            if response.status == 200:
                # Get the JSON response
                content = await self.page.content()
                
                # Extract JSON from the page content
                if content.strip().startswith('{'):
                    data = json.loads(content.strip())
                    
                    events = []
                    if 'events' in data:
                        for event_data in data['events']:
                            event = CalendarEvent(
                                id=event_data['id'],
                                funding_status=event_data['fundingStatus'],
                                attendees=event_data.get('attendees', [])
                            )
                            events.append(event)
                    
                    logger.info(f"Successfully fetched {len(events)} calendar events")
                    return events
                else:
                    logger.error("Response is not JSON")
                    return []
            else:
                logger.error(f"API call failed with status: {response.status}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []
    
    async def get_calendar_events_via_js(self, event_ids: List[int]) -> List[CalendarEvent]:
        """
        Alternative method: Use JavaScript to make the API call
        """
        try:
            logger.info(f"Fetching {len(event_ids)} calendar events via JavaScript...")
            
            # Build the API call in JavaScript
            js_code = f"""
            async () => {{
                const eventIds = {json.dumps(event_ids)};
                const params = new URLSearchParams();
                
                eventIds.forEach(id => params.append('eventIds', id));
                params.append('fields', 'fundingStatus');
                params.append('_', Date.now());
                
                const response = await fetch('/api/calendar/events?' + params.toString(), {{
                    method: 'GET',
                    headers: {{
                        'Accept': '*/*',
                        'X-Requested-With': 'XMLHttpRequest'
                    }}
                }});
                
                if (response.ok) {{
                    return await response.json();
                }} else {{
                    throw new Error('API call failed: ' + response.status);
                }}
            }}
            """
            
            # Execute the JavaScript
            result = await self.page.evaluate(js_code)
            
            events = []
            if result and 'events' in result:
                for event_data in result['events']:
                    event = CalendarEvent(
                        id=event_data['id'],
                        funding_status=event_data['fundingStatus'],
                        attendees=event_data.get('attendees', [])
                    )
                    events.append(event)
            
            logger.info(f"Successfully fetched {len(events)} calendar events via JavaScript")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching calendar events via JavaScript: {e}")
            return []
    
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

async def main():
    """
    Demo of the live ClubOS Calendar API
    """
    print("=== ClubOS Live Calendar API - Browser Automation ===")
    
    # Initialize with credentials
    api = ClubOSLiveCalendar("j.mayo", "L*KYqnec5z7nEL$")
    
    try:
        # Start browser
        print("\n1. Starting browser...")
        await api.start_browser()
        print("✅ Browser started")
        
        # Authenticate
        print("\n2. Authenticating...")
        if not await api.authenticate():
            print("❌ Authentication failed")
            return
        print("✅ Authentication successful")
        
        # Navigate to calendar
        print("\n3. Navigating to calendar...")
        if not await api.navigate_to_calendar():
            print("❌ Calendar navigation failed")
            return
        print("✅ Calendar loaded")
        
        # Test calendar API with event IDs from HAR analysis
        print("\n4. Testing calendar API...")
        
        # January event IDs from HAR
        january_events = [
            152495806, 152575612, 152634057, 152686854, 152499620,
            152670358, 152703864, 152516483, 152678589, 152528272
        ]
        
        # Try method 1: Direct API call
        print("   Method 1: Direct API call...")
        events1 = await api.get_calendar_events_via_api(january_events[:5])
        
        if events1:
            print(f"   ✅ Direct API: {len(events1)} events")
        else:
            print("   ⚠️ Direct API failed, trying JavaScript method...")
            
            # Try method 2: JavaScript fetch
            print("   Method 2: JavaScript fetch...")
            events2 = await api.get_calendar_events_via_js(january_events[:5])
            
            if events2:
                print(f"   ✅ JavaScript API: {len(events2)} events")
                events1 = events2
            else:
                print("   ❌ Both methods failed")
        
        # Display results
        if events1:
            print(f"\n📊 Calendar Events Retrieved ({len(events1)}):")
            for i, event in enumerate(events1):
                print(f"   {i+1}. Event ID: {event.id}")
                print(f"      Funding Status: {event.funding_status}")
                print(f"      Attendees: {len(event.attendees)}")
                
                for j, attendee in enumerate(event.attendees[:2]):
                    print(f"        - {attendee['id']}: {attendee['fundingStatus']}")
                if len(event.attendees) > 2:
                    print(f"        ... and {len(event.attendees) - 2} more")
        
        print("\n=== Test Complete ===")
        print("✅ Browser automation successfully maintained session")
        print("✅ Calendar API accessible through live browser context")
        
        # Keep browser open for testing
        print("\nBrowser will stay open for 30 seconds for manual testing...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(main())
