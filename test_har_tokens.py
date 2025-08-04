#!/usr/bin/env python3
"""
ClubOS Calendar API - Direct HAR Token Implementation
Uses the exact Bearer token and session data from your successful HAR capture
"""

import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Calendar event from ClubOS"""
    id: int
    funding_status: str
    attendees: List[Dict[str, Any]]

class ClubOSDirectHAR:
    """
    Direct implementation using actual HAR tokens and session data
    This bypasses authentication and uses the working session from HAR
    """
    
    def __init__(self):
        self.base_url = "https://anytime.club-os.com"
        self.session = requests.Session()
        
        # Exact session data from your HAR file
        self.session_cookies = {
            'JSESSIONID': '54327877EC48CA798FC17D0E6CE1B7FB',
            'loggedInUserId': '187032782',
            'delegatedUserId': '187032782',
            'apiV3AccessToken': 'eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6IjQwNTU0OTNjLTViOTAtNDk0Yi04NTFjLTE3NGZlNzFkOGFhYyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTI3Njc2MzcsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1Mjc4NTY1MSwiaWF0IjoxNzUyNzgyMDUxLCJqdGkiOiJlYTUzNzEyMi0xNjNlLTQyMjAtYjBiZi04ZTViM2QxMjEyYTkiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.VOIJi4ZZZkO5yscgBc4ruZ1AaONT2btAyXuJVMC78-EsqLTh9cqFWrvC918Z9ydKmDzjsFT5vFmgT351fGYY2GTcIG01iP2uXpLOH8o2uusrAl0XYu9GCG8hjkbt1cfsDbGGYUBDAsThzfV4HnriW-CciV2H5Sr-PSAQyYl-UFPK8QQqCiZ8AyTF3zvD7Qdh2rYUXBILxUNQHKRC_6fv0kxMnXgo7N6slxzkzch3YIke0Oz0MAvUC_R1twxf_JOuAIH09MhwZ8dQv9Wn7cgQ4zaZWMKY8asaTmXGv1eKRKr454ZRLrQBMhp07kl-cyeIVxoXsqV0aYoILYsvF6N9Yw'
        }
        
        # Exact Bearer token from your HAR file
        self.bearer_token = 'eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg3MDMyNzgyLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiI1NDMyNzg3N0VDNDhDQTc5OEZDOMU3RDBFNKBFMUQ3RkIifQ.xgXI5ZdpWH1czSf2aIzzZmK7r8siUsV59MeeqZF0PNM'
        
        # Set up session cookies
        for name, value in self.session_cookies.items():
            self.session.cookies.set(name, value, domain='.club-os.com')
        
        # Standard headers from HAR
        self.headers = {
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
            'Pragma': 'no-cache',
            'Authorization': f'Bearer {self.bearer_token}',
            'Referer': f'{self.base_url}/action/Calendar'
        }
    
    def test_calendar_api(self, event_ids: List[int]) -> List[CalendarEvent]:
        """
        Test the calendar API with actual event IDs from HAR
        """
        try:
            logger.info(f"Testing calendar API with {len(event_ids)} event IDs...")
            
            # Build parameters exactly as in HAR
            params = []
            for event_id in event_ids:
                params.append(('eventIds', str(event_id)))
            params.append(('fields', 'fundingStatus'))
            params.append(('_', str(int(datetime.now().timestamp() * 1000))))
            
            # Make the API call
            response = self.session.get(
                f"{self.base_url}/api/calendar/events",
                headers=self.headers,
                params=params
            )
            
            logger.info(f"API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                events = []
                
                if 'events' in data:
                    for event_data in data['events']:
                        event = CalendarEvent(
                            id=event_data['id'],
                            funding_status=event_data['fundingStatus'],
                            attendees=event_data.get('attendees', [])
                        )
                        events.append(event)
                
                logger.info(f"Successfully parsed {len(events)} events")
                return events
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error testing calendar API: {e}")
            return []
    
    def test_staff_leads_api(self) -> Dict[str, Any]:
        """
        Test the staff leads API
        """
        try:
            logger.info("Testing staff leads API...")
            
            params = {
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            response = self.session.get(
                f"{self.base_url}/api/staff/187032782/leads",
                headers=self.headers,
                params=params
            )
            
            logger.info(f"Staff API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Staff leads API successful")
                return data
            else:
                logger.error(f"Staff API failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error testing staff API: {e}")
            return {}

def main():
    """
    Test the direct HAR implementation
    """
    print("=== ClubOS Direct HAR Token Test ===")
    
    # Initialize with HAR data
    api = ClubOSDirectHAR()
    
    print(f"Session cookies set: {len(api.session_cookies)}")
    print(f"Bearer token: {api.bearer_token[:50]}...")
    
    # Test with actual event IDs from your HAR file
    print("\n1. Testing Calendar API with January event IDs...")
    january_events = [
        152495806, 152575612, 152634057, 152686854, 152499620,
        152670358, 152703864, 152516483, 152678589, 152528272
    ]
    
    events = api.test_calendar_api(january_events)
    
    if events:
        print(f"✅ Calendar API working! Retrieved {len(events)} events")
        
        print("\nEvent Details:")
        for i, event in enumerate(events[:5]):
            print(f"  {i+1}. Event ID: {event.id}")
            print(f"     Funding Status: {event.funding_status}")
            print(f"     Attendees: {len(event.attendees)}")
            
            for j, attendee in enumerate(event.attendees[:2]):
                print(f"       - Attendee {attendee['id']}: {attendee['fundingStatus']}")
            
            if len(event.attendees) > 2:
                print(f"       ... and {len(event.attendees) - 2} more")
    else:
        print("❌ Calendar API failed")
    
    # Test staff leads API
    print("\n2. Testing Staff Leads API...")
    leads_data = api.test_staff_leads_api()
    
    if leads_data:
        print("✅ Staff Leads API working!")
        if isinstance(leads_data, dict):
            print(f"   Leads data keys: {list(leads_data.keys())}")
    else:
        print("❌ Staff Leads API failed")
    
    # Test with February event IDs
    print("\n3. Testing Calendar API with February event IDs...")
    february_events = [
        150192368, 152549212, 149991441, 152657258, 152735268,
        147447149, 150073576, 150468903, 150850294, 149893126
    ]
    
    feb_events = api.test_calendar_api(february_events)
    
    if feb_events:
        print(f"✅ February events retrieved: {len(feb_events)}")
    else:
        print("❌ February events failed")
    
    print("\n=== Summary ===")
    if events or feb_events:
        print("✅ ClubOS Calendar API is accessible with proper tokens!")
        print("✅ HAR analysis successful - we have working API access")
        print("🎯 Next step: Implement real-time token refresh mechanism")
    else:
        print("❌ API access failed - tokens may have expired")
        print("🔄 Need fresh session capture for new tokens")

if __name__ == "__main__":
    main()
