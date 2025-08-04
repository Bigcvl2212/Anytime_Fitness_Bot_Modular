#!/usr/bin/env python3
"""
ClubOS Calendar API - Replicating EXACT HAR Sequence
No browser automation, just pure API calls based on working HAR data
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any
import time

class ClubOSCalendarHAR:
    """
    Replicate the exact ClubOS calendar API sequence from HAR file
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        
        # Exact cookies from working HAR session
        self.session_cookies = {
            'JSESSIONID': '54327877EC48CA798FC1F8D3E36ED453',
            'loggedInUserId': '187032782',
            'delegatedUserId': '187032782',
            'apiV3AccessToken': 'eyJraWQiOiIzWlwvN3R1TEYrZzBVMEdQSW10QjhCZHY3Q3RWWlwvek1HekxnKzc4SGZNbVk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiIzMDhiMWExMi00YzkzLTRhYjctYThlNC0yNGZlZDY2YzUyNzUiLCJldmVudF9pZCI6Ijc3ZGMzZDk2LWViZTEtNGQ4My05Mzg3LTNkZWQ5MTZjNjBiZiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NTM1NTQxMjIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX2hDWElUdVNpZCIsImV4cCI6MTc1MzU1NzcyMiwiaWF0IjoxNzUzNTU0MTIyLCJqdGkiOiIwNTdkYzJlOS1mNmM1LTRlMDctYjkwZS04NGIxYTYzZDFjOWQiLCJjbGllbnRfaWQiOiI2cTdzNGFsZ3R0NzJvbWlvdmJqOW1hcmloayIsInVzZXJuYW1lIjoiMTg3MDMyNzgyIn0.Yks-B3SNLfM2E-FvTB0TI0wnOBm2wEHH9V21w3Hvp_ljHHH1yl4FacafbweddYAVuQucqFivtuMhHXcWEt0XtUN4nWlfR-irEeDNUm4o0ekFRp6Q3Uyb1hVBcYwXgZCnaIEkaQSzMxpFZgf9D6nhf5ABfYGCTaNuUbD1LxczYpT7vW1BBXTYi8x5ppyswO9yNjQReK8tGon8UI2LsfBYKfQ1U8MzuVqDsSIJw_beFbF4GExE97Je8BJd_1uLcBdLa0gSzqQ6thxOuCNpYNfrPLkGvYn-C_nQl3-cz4tOB0JqiucoaREE8ztffIXG41XKZSKkxvfVKfp6RlR1Fl3P2VA'
        }
        
        # Exact Bearer token from working HAR session
        self.bearer_token = 'eyJhbGciOiJIUzI1NiJ9.eyJkZWxlZ2F0ZVVzZXJJZCI6MTg3MDMyNzgyLCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9uSWQiOiI1NDMyNzg3N0VDNDhDQTc5OEZGMUY4RDNFMDZFRDQ1MyJ9.xgXI5ZdpWH1czSf2aIzzZmK7r8siUsV59MeeqZF0PNM'
        
        # Event IDs from HAR file - these are real events that worked
        self.working_event_ids = [
            152495806, 152575612, 152634057, 152686854, 152499620, 152670358,
            152703864, 152516483, 152678589, 152528272, 152683478, 152537400,
            152636853, 152686863, 152612245, 152656849, 152684560, 152619516,
            152686867, 152656845, 152549188, 152657524, 152544543, 152619520,
            149648946, 152552298
        ]
        
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
    
    def setup_session(self):
        """Setup session with exact cookies from HAR"""
        print("Setting up session with HAR cookies...")
        
        for name, value in self.session_cookies.items():
            self.session.cookies.set(name, value, domain='anytime.club-os.com')
        
        print(f"✅ Session setup complete")
        print(f"   JSESSIONID: {self.session_cookies['JSESSIONID']}")
        print(f"   User ID: {self.session_cookies['loggedInUserId']}")
        print(f"   Delegated User ID: {self.session_cookies['delegatedUserId']}")
    
    def access_calendar_page(self) -> bool:
        """Step 1: Access calendar page (as seen in HAR)"""
        print("\n🗓️ Step 1: Accessing calendar page...")
        
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
        """Step 2: Filter calendar (as seen in HAR)"""
        print("\n🔍 Step 2: Filtering calendar...")
        
        try:
            headers = self.standard_headers.copy()
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # This data structure comes from the HAR file
            data = {
                'trainerId': '187032782',  # Jeremy Mayo's ID
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
    
    def get_calendar_events(self) -> List[Dict[str, Any]]:
        """Step 3: Get calendar events using exact HAR API call"""
        print("\n📅 Step 3: Getting calendar events...")
        
        try:
            headers = self.standard_headers.copy()
            headers.update({
                'Authorization': f'Bearer {self.bearer_token}',
                'Referer': f'{self.base_url}/action/Calendar'
            })
            
            # Build exact URL parameters from HAR
            params = []
            for event_id in self.working_event_ids:
                params.append(('eventIds', str(event_id)))
            params.append(('fields', 'fundingStatus'))
            params.append(('_', str(int(time.time() * 1000))))  # Timestamp
            
            print(f"   Requesting {len(self.working_event_ids)} events...")
            print(f"   Bearer token: {self.bearer_token[:50]}...")
            
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
                
                # Show sample events
                for i, event in enumerate(events[:5]):
                    print(f"   Event {i+1}: ID={event['id']}, Status={event['fundingStatus']}, Attendees={len(event.get('attendees', []))}")
                
                if len(events) > 5:
                    print(f"   ... and {len(events)-5} more events")
                
                return events
            else:
                print(f"   ❌ Failed to get events: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return []
                
        except Exception as e:
            print(f"   ❌ Error getting calendar events: {e}")
            return []
    
    def test_sequence(self):
        """Test the complete sequence from HAR"""
        print("🚀 Testing ClubOS Calendar API - HAR Replication")
        print("="*60)
        
        # Setup session
        self.setup_session()
        
        # Step 1: Access calendar page
        if not self.access_calendar_page():
            print("❌ Failed at step 1 - calendar page access")
            return False
        
        # Step 2: Filter calendar  
        if not self.filter_calendar():
            print("❌ Failed at step 2 - calendar filter")
            return False
        
        # Step 3: Get calendar events
        events = self.get_calendar_events()
        
        if events:
            print(f"\n🎉 SUCCESS! Retrieved {len(events)} calendar events")
            
            # Analyze the events
            funded_events = [e for e in events if e['fundingStatus'] == 'FUNDED']
            not_funded_events = [e for e in events if e['fundingStatus'] == 'NOT_FUNDED']
            processing_events = [e for e in events if e['fundingStatus'] == 'PROCESSING']
            
            print(f"\n📊 Event Analysis:")
            print(f"   FUNDED: {len(funded_events)} events")
            print(f"   NOT_FUNDED: {len(not_funded_events)} events")
            print(f"   PROCESSING: {len(processing_events)} events")
            
            total_attendees = sum(len(e.get('attendees', [])) for e in events)
            print(f"   Total attendees: {total_attendees}")
            
            return True
        else:
            print("❌ Failed to retrieve calendar events")
            return False

def main():
    """Test the HAR-based calendar API"""
    
    api = ClubOSCalendarHAR()
    success = api.test_sequence()
    
    if success:
        print("\n🎯 CONCLUSION: HAR sequence replication SUCCESSFUL!")
        print("The calendar API is working with the exact HAR data.")
    else:
        print("\n❌ CONCLUSION: HAR sequence replication FAILED!")
        print("The tokens from HAR may have expired or the sequence needs adjustment.")

if __name__ == "__main__":
    main()
