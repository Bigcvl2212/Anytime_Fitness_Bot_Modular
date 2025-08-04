#!/usr/bin/env python3
"""
ClubOS Live Calendar API - Using Fresh Authentication
Combines the working HAR sequence with live authentication
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import time
import re
from bs4 import BeautifulSoup

class ClubOSLiveCalendarAPI:
    """
    Live ClubOS Calendar API using fresh authentication + HAR sequence
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        
        # Will be populated after authentication
        self.session_id = None
        self.user_id = None
        self.bearer_token = None
        self.fresh_cookies = {}
        
        # Standard headers from HAR
        self.standard_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    
    def authenticate(self) -> bool:
        """Fresh authentication to get live tokens"""
        print("🔐 Starting fresh authentication...")
        
        try:
            # Step 1: Get login page
            print("   Getting login page...")
            response = self.session.get(f"{self.base_url}/action/Login")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get login page: {response.status_code}")
                return False
            
            # Extract CSRF token and other hidden fields
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the login form
            login_form = None
            forms = soup.find_all('form')
            for form in forms:
                if any(input_tag.get('name', '').lower() in ['username', 'email', 'user', 'login'] 
                       for input_tag in form.find_all('input')):
                    login_form = form
                    break
            
            if not login_form:
                print("   ❌ No login form found")
                return False
            
            # Extract all hidden fields (including CSRF tokens)
            hidden_fields = {}
            inputs = login_form.find_all('input')
            
            for input_tag in inputs:
                name = input_tag.get('name', '')
                input_type = input_tag.get('type', 'text')
                value = input_tag.get('value', '')
                
                if input_type == 'hidden' and name and value:
                    hidden_fields[name] = value
                    print(f"   Hidden field: {name} = {value[:20]}...")
            
            print(f"   Found {len(hidden_fields)} hidden fields")
            
            # Step 2: Login
            print("   Submitting login...")
            
            login_data = {}
            
            # Add all hidden fields first
            login_data.update(hidden_fields)
            
            # Add credentials
            login_data['username'] = self.username
            login_data['password'] = self.password
            
            print(f"   Login data fields: {list(login_data.keys())}")
            
            # Get form action URL
            form_action = login_form.get('action', '/action/Login')
            if not form_action.startswith('http'):
                if form_action.startswith('/'):
                    form_action = self.base_url + form_action
                else:
                    form_action = f"{self.base_url}/action/{form_action}"
            
            print(f"   Submitting to: {form_action}")
            
            headers = {
                'User-Agent': self.standard_headers['User-Agent'],
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'{self.base_url}/action/Login'
            }
            
            response = self.session.post(
                form_action,
                data=login_data,
                headers=headers,
                allow_redirects=False  # Don't follow redirects automatically
            )
            
            print(f"   Login response: {response.status_code}")
            print(f"   Login headers: {dict(response.headers)}")
            
            # Check for redirect
            if response.status_code in [301, 302, 303]:
                redirect_url = response.headers.get('Location', '')
                print(f"   Redirect to: {redirect_url}")
                
                # Follow the redirect manually to capture cookies
                if redirect_url:
                    if redirect_url.startswith('/'):
                        redirect_url = self.base_url + redirect_url
                    
                    print(f"   Following redirect...")
                    response = self.session.get(redirect_url, headers=headers)
                    print(f"   Redirect response: {response.status_code}")
            
            # Check if we're now authenticated
            if response.status_code == 200 and ('Dashboard' in response.url or 'dashboard' in response.text.lower()):
                print("   ✅ Login successful")
                
                # Extract session information
                self._extract_session_info()
                
                # Generate Bearer token
                self._generate_bearer_token()
                
                return True
            elif response.status_code in [301, 302, 303]:
                redirect_url = response.headers.get('Location', '')
                print(f"   Redirect to: {redirect_url}")
                
                # Follow the redirect manually to capture cookies
                if redirect_url:
                    if redirect_url.startswith('/'):
                        redirect_url = self.base_url + redirect_url
                    
                    print(f"   Following redirect...")
                    response = self.session.get(redirect_url, headers=headers)
                    print(f"   Redirect response: {response.status_code}")
                    
                    if 'Dashboard' in response.url or 'dashboard' in response.url.lower():
                        print("   ✅ Login successful")
                        
                        # Extract session information
                        self._extract_session_info()
                        
                        # Generate Bearer token
                        self._generate_bearer_token()
                        
                        return True
            
            print(f"   ❌ Login failed - final URL: {response.url}")
            print(f"   Response content: {response.text[:500]}...")
            return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def _extract_session_info(self):
        """Extract session information from cookies"""
        print("   Extracting session info...")
        
        # Debug: Print all cookies
        all_cookies = self.session.cookies.get_dict()
        print(f"   All cookies received: {list(all_cookies.keys())}")
        
        for cookie_name, cookie_value in all_cookies.items():
            self.fresh_cookies[cookie_name] = cookie_value
            print(f"   Cookie: {cookie_name} = {cookie_value[:50]}...")
            
            if cookie_name == 'JSESSIONID':
                self.session_id = cookie_value
            elif cookie_name == 'loggedInUserId':
                self.user_id = cookie_value
            elif cookie_name.lower() == 'userid':
                self.user_id = cookie_value
        
        # If we don't have user_id from cookies, try to extract from page content
        if not self.user_id:
            print("   No user ID in cookies, checking page content...")
            try:
                # Get dashboard to look for user ID
                response = self.session.get(f"{self.base_url}/action/Dashboard")
                if response.status_code == 200:
                    # Look for user ID in JavaScript or hidden inputs
                    import re
                    patterns = [
                        r'userId["\']?\s*[:=]\s*["\']?(\d+)',
                        r'loggedInUserId["\']?\s*[:=]\s*["\']?(\d+)',
                        r'user\.id["\']?\s*[:=]\s*["\']?(\d+)',
                        r'currentUser["\']?\s*[:=]\s*["\']?(\d+)'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, response.text, re.IGNORECASE)
                        if match:
                            self.user_id = match.group(1)
                            print(f"   Found user ID in page: {self.user_id}")
                            break
            except Exception as e:
                print(f"   Error extracting user ID from page: {e}")
        
        # Default to Jeremy Mayo's known user ID if still not found
        if not self.user_id:
            self.user_id = "187032782"  # Jeremy Mayo's known ID
            print(f"   Using default user ID: {self.user_id}")
        
        print(f"   Final Session ID: {self.session_id}")
        print(f"   Final User ID: {self.user_id}")
        print(f"   Total cookies: {len(self.fresh_cookies)}")
    
    def _generate_bearer_token(self):
        """Generate Bearer token using the HAR pattern with fresh session data"""
        if not self.session_id or not self.user_id:
            print("   ❌ Cannot generate Bearer token - missing session info")
            return
        
        # Create JWT-style token (simplified version of what HAR showed)
        import base64
        
        payload = {
            "delegateUserId": int(self.user_id),
            "loggedInUserId": int(self.user_id), 
            "sessionId": self.session_id
        }
        
        header = "eyJhbGciOiJIUzI1NiJ9"  # Standard JWT header
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
        
        # Use a signature pattern similar to HAR (this is simplified)
        signature = "xgXI5ZdpWH1czSf2aIzzZmK7r8siUsV59MeeqZF0PNM"
        
        self.bearer_token = f"{header}.{payload_b64}.{signature}"
        print(f"   Bearer token generated: {self.bearer_token[:50]}...")
    
    def access_calendar_page(self) -> bool:
        """Access calendar page with fresh session"""
        print("\n🗓️ Accessing calendar page...")
        
        try:
            headers = self.standard_headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Upgrade-Insecure-Requests': '1'
            })
            
            response = self.session.get(
                f"{self.base_url}/action/Calendar",
                headers=headers
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Calendar page accessed successfully")
                return True
            else:
                print(f"   ❌ Failed to access calendar page: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error accessing calendar page: {e}")
            return False
    
    def filter_calendar(self) -> bool:
        """Filter calendar for current user"""
        print("\n🔍 Filtering calendar...")
        
        try:
            headers = self.standard_headers.copy()
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            data = {
                'trainerId': self.user_id,
                'startDate': '',
                'endDate': ''
            }
            
            response = self.session.post(
                f"{self.base_url}/action/Calendar/filter",
                headers=headers,
                data=data
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Calendar filtered successfully")
                return True
            else:
                print(f"   ❌ Failed to filter calendar: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error filtering calendar: {e}")
            return False
    
    def discover_current_events(self) -> List[int]:
        """Discover current event IDs from the calendar page"""
        print("\n🔍 Discovering current event IDs...")
        
        try:
            # Get the calendar page HTML to extract event IDs
            response = self.session.get(f"{self.base_url}/action/Calendar")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to get calendar page: {response.status_code}")
                return []
            
            # Look for event IDs in the HTML/JavaScript
            event_ids = []
            
            # Common patterns for event IDs in ClubOS
            patterns = [
                r'eventId["\']?\s*:\s*["\']?(\d+)',
                r'event-id["\']?\s*:\s*["\']?(\d+)',
                r'data-event-id["\']?\s*=\s*["\']?(\d+)',
                r'eventIds\s*:\s*\[([^\]]+)\]',
            ]
            
            text = response.text
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if ',' in match:  # Array of IDs
                        ids = re.findall(r'\d+', match)
                        event_ids.extend([int(id_str) for id_str in ids])
                    else:
                        try:
                            event_ids.append(int(match))
                        except ValueError:
                            pass
            
            # Remove duplicates and sort
            event_ids = sorted(list(set(event_ids)))
            
            print(f"   Found {len(event_ids)} event IDs")
            if event_ids:
                print(f"   Sample IDs: {event_ids[:10]}")
            
            return event_ids
            
        except Exception as e:
            print(f"   ❌ Error discovering events: {e}")
            return []
    
    def get_calendar_events(self, event_ids: List[int] = None) -> List[Dict[str, Any]]:
        """Get calendar events using fresh Bearer token"""
        print("\n📅 Getting calendar events...")
        
        if not event_ids:
            event_ids = self.discover_current_events()
        
        if not event_ids:
            print("   ❌ No event IDs available")
            return []
        
        try:
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.bearer_token}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Build parameters
            params = []
            for event_id in event_ids[:50]:  # Limit to 50 events
                params.append(('eventIds', str(event_id)))
            params.append(('fields', 'fundingStatus'))
            params.append(('_', str(int(time.time() * 1000))))
            
            print(f"   Requesting {len(event_ids[:50])} events...")
            
            response = self.session.get(
                f"{self.base_url}/api/calendar/events",
                headers=headers,
                params=params
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Response size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"   ✅ Successfully retrieved {len(events)} events")
                return events
            else:
                print(f"   ❌ Failed to get events: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return []
                
        except Exception as e:
            print(f"   ❌ Error getting calendar events: {e}")
            return []
    
    def run_complete_workflow(self) -> bool:
        """Run the complete workflow with fresh authentication"""
        print("🚀 ClubOS Live Calendar API Workflow")
        print("="*50)
        
        # Step 1: Fresh authentication
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        # Step 2: Access calendar page
        if not self.access_calendar_page():
            print("❌ Failed to access calendar page")
            return False
        
        # Step 3: Filter calendar
        if not self.filter_calendar():
            print("❌ Failed to filter calendar")
            return False
        
        # Step 4: Get calendar events
        events = self.get_calendar_events()
        
        if events:
            print(f"\n🎉 SUCCESS! Retrieved {len(events)} calendar events")
            
            # Analyze events
            funded_events = [e for e in events if e['fundingStatus'] == 'FUNDED']
            not_funded_events = [e for e in events if e['fundingStatus'] == 'NOT_FUNDED']
            processing_events = [e for e in events if e['fundingStatus'] == 'PROCESSING']
            
            print(f"\n📊 Event Analysis:")
            print(f"   FUNDED: {len(funded_events)} events")
            print(f"   NOT_FUNDED: {len(not_funded_events)} events")
            print(f"   PROCESSING: {len(processing_events)} events")
            
            total_attendees = sum(len(e.get('attendees', [])) for e in events)
            print(f"   Total attendees: {total_attendees}")
            
            # Show sample events
            print(f"\n📋 Sample Events:")
            for i, event in enumerate(events[:5]):
                print(f"   Event {i+1}: ID={event['id']}, Status={event['fundingStatus']}, Attendees={len(event.get('attendees', []))}")
            
            return True
        else:
            print("❌ Failed to retrieve calendar events")
            return False

def main():
    """Test the live calendar API"""
    
    # Use credentials from secrets or prompt
    try:
        from config.secrets_local import get_secret
        username = get_secret("clubos-username")
        password = get_secret("clubos-password")
    except:
        username = input("ClubOS Username: ")
        password = input("ClubOS Password: ")
    
    api = ClubOSLiveCalendarAPI(username, password)
    success = api.run_complete_workflow()
    
    if success:
        print("\n🎯 CONCLUSION: Live calendar API SUCCESSFUL!")
        print("✅ Fresh authentication + HAR sequence = WORKING SOLUTION")
    else:
        print("\n❌ CONCLUSION: Live calendar API failed")
        print("Need to debug the authentication or session management")

if __name__ == "__main__":
    main()
