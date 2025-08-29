#!/usr/bin/env python3
"""
ClubHub API Client - Comprehensive implementation based on discovered endpoints
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode

class ClubHubAPIClient:
    """ClubHub API Client with all discovered endpoints"""
    
    def __init__(self):
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        self.club_id = "1156"
        self.api_version = "1"
        self.auth_token = None
        self.headers = {
            "Host": "clubhub-ios-api.anytimefitness.com",
            "API-version": "1",
            "Accept": "application/json",
            "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
            "Accept-Language": "en-US",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            # Updated Cookie header from the successful HAR login:
            "Cookie": "dtCookie=v_4_srv_4_sn_6B9DB1AE4D6E658C76B74A6BCD41DC44_perc_100000_ol_0_mul_1_app-3A4b32026d63ce75ab_0_rcs-3Acss_0; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
        }
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with ClubHub API using exact format from HAR file"""
        url = f"{self.base_url}/api/login"
        
        # Use the exact payload format from the successful HAR login
        data = {
            "username": email,
            "password": password
        }
        
        try:
            print(f"🔐 Attempting ClubHub authentication with {email}...")
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            print(f"📥 Login response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get('accessToken')  # Use accessToken instead of token
                if self.auth_token:
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    print("✅ ClubHub authentication successful")
                    print(f"🔑 Bearer token: {self.auth_token[:50]}...")
                    return True
                else:
                    print("❌ No accessToken in response")
                    print(f"Response data: {auth_data}")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    print(f"Response text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def set_auth_token(self, token: str):
        """Set authentication token manually"""
        self.auth_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        print("✅ ClubHub auth token set")
    
    def get_club_features(self) -> Optional[Dict[str, Any]]:
        """Get club features"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/features"
        return self._make_request("GET", url)
    
    def get_club_doors(self, page: int = 1, page_size: int = 100) -> Optional[Dict[str, Any]]:
        """Get club doors"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/Doors"
        params = {"page": page, "pageSize": page_size}
        return self._make_request("GET", url, params=params)
    
    def get_club_topic_types(self, page: int = 1, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Get club topic types"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/TopicTypes"
        params = {"page": page, "pageSize": page_size}
        return self._make_request("GET", url, params=params)
    
    def get_club_usages(self, page: int = 1, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Get club usages"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/usages"
        params = {"page": page, "pageSize": page_size}
        return self._make_request("GET", url, params=params)
    
    def get_club_schedule(self, start_date: str = None, end_date: str = None, 
                         page: int = 1, page_size: int = 200) -> Optional[Dict[str, Any]]:
        """Get club schedule"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/schedule"
        params = {"page": page, "pageSize": page_size}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self._make_request("GET", url, params=params)
    
    def get_club_door_status(self) -> Optional[Dict[str, Any]]:
        """Get club door status"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/DoorStatus"
        return self._make_request("GET", url)
    
    def open_club_doors(self) -> Optional[Dict[str, Any]]:
        """Open club doors"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/opendoors"
        return self._make_request("POST", url)
    
    def get_club_bans(self, page: int = 1, page_size: int = 50) -> Optional[Dict[str, Any]]:
        """Get club bans"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/Bans"
        params = {"page": page, "pageSize": page_size}
        return self._make_request("GET", url, params=params)
    
    def get_all_members(self, page: int = 1, page_size: int = 100, extra_params=None, club_id: str = None) -> Optional[Dict[str, Any]]:
        """Get all members (ClubHub API, v1.0)"""
        target_club_id = club_id or self.club_id
        url = f"{self.base_url}/api/v1.0/clubs/{target_club_id}/members"
        params = {
            "page": str(page),
            "pageSize": str(page_size),
            "includeInactive": "true",
            "includeAll": "true",
            "status": "all",
            "days": "10000"
        }
        if extra_params:
            params.update(extra_params)
        return self._make_request("GET", url, params=params)
    
    def get_all_prospects(self, page: int = 1, page_size: int = 100, extra_params=None, club_id: str = None) -> Optional[Dict[str, Any]]:
        """Get all prospects (ClubHub API, v1.0) with extended history (10k days) - EXACT COPY from working script"""
        target_club_id = club_id or self.club_id
        url = f"{self.base_url}/api/v1.0/clubs/{target_club_id}/prospects"
        
        # Use the EXACT SAME parameters as the working script that got 9000+ prospects
        params = {
            "days": "10000", 
            "page": str(page), 
            "pageSize": str(page_size),
            "includeInactive": "true",
            "includeAll": "true", 
            "status": "all"
        }
        if extra_params:
            params.update(extra_params)
        return self._make_request("GET", url, params=params)
    
    def get_member_details(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get specific member details"""
        url = f"{self.base_url}/api/members/{member_id}"
        return self._make_request("GET", url)
    
    def get_prospect_details(self, prospect_id: str) -> Optional[Dict[str, Any]]:
        """Get specific prospect details"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/prospects/{prospect_id}"
        return self._make_request("GET", url)
    
    def get_member_usages(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member usages"""
        url = f"{self.base_url}/api/members/{member_id}/usages"
        return self._make_request("GET", url)
    
    def get_member_activities(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member activities"""
        url = f"{self.base_url}/api/members/{member_id}/activities"
        return self._make_request("GET", url)
    
    def get_member_bans(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member bans"""
        url = f"{self.base_url}/api/members/{member_id}/bans"
        return self._make_request("GET", url)
    
    def get_member_agreement(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member agreement"""
        url = f"{self.base_url}/api/members/{member_id}/agreement"
        return self._make_request("GET", url)
    
    def get_member_tanning(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member tanning info"""
        url = f"{self.base_url}/api/members/{member_id}/tanning"
        return self._make_request("GET", url)
    
    def get_member_digital_key_status(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member digital key status"""
        url = f"{self.base_url}/api/members/{member_id}/digital-key-status"
        return self._make_request("GET", url)
    
    def get_member_pending_actions(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member pending actions"""
        url = f"{self.base_url}/api/members/{member_id}/pendingActions"
        return self._make_request("GET", url)
    
    def get_member_agreement_history(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member agreement history"""
        url = f"{self.base_url}/api/members/{member_id}/agreementHistory"
        return self._make_request("GET", url)
    
    def get_member_agreement_token_query(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get member agreement token query"""
        url = f"{self.base_url}/api/members/{member_id}/agreementTokenQuery"
        return self._make_request("GET", url)
    
    def post_member_usage(self, member_id: str, usage_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Post member usage"""
        url = f"{self.base_url}/api/members/{member_id}/usages"
        return self._make_request("POST", url, json_data=usage_data)
    
    def get_member_usages_by_date_range(self, member_id: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """Get member usages by date range"""
        url = f"{self.base_url}/api/members/{member_id}/usages/by-date-range"
        params = {"startDate": start_date, "endDate": end_date}
        return self._make_request("GET", url, params=params)
    
    def put_member_bans(self, member_id: str, ban_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update member bans"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/members/{member_id}/bans"
        return self._make_request("PUT", url, json_data=ban_data)
    
    def delete_member_bans(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Delete member bans"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/members/{member_id}/bans"
        return self._make_request("DELETE", url)
    
    def post_club_notes(self, note_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Post club notes"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/notes"
        return self._make_request("POST", url, json_data=note_data)
    
    def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user details"""
        url = f"{self.base_url}/api/users/{user_id}"
        return self._make_request("GET", url)
    
    def get_user_clubs(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user clubs"""
        url = f"{self.base_url}/api/users/{user_id}/clubs"
        return self._make_request("GET", url)
    
    def get_club_details(self) -> Optional[Dict[str, Any]]:
        """Get club details"""
        url = f"{self.base_url}/api/clubs/{self.club_id}"
        return self._make_request("GET", url)
    
    def get_club_settings(self) -> Optional[Dict[str, Any]]:
        """Get club settings"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/settings"
        return self._make_request("GET", url)
    
    def get_club_sources(self) -> Optional[Dict[str, Any]]:
        """Get club sources"""
        url = f"{self.base_url}/api/clubs/{self.club_id}/Sources"
        return self._make_request("GET", url)
    
    def _make_request(self, method: str, url: str, params: Dict[str, Any] = None, 
                     json_data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with error handling"""
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, params=params, json=json_data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, params=params, json=json_data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            else:
                print(f"❌ Unsupported HTTP method: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ {method} {url} failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    def get_all_members_paginated(self) -> List[Dict[str, Any]]:
        """Get all members with pagination"""
        all_members = []
        page = 1
        max_pages = 100  # Safety limit
        
        while page <= max_pages:
            print(f"🔍 Fetching members page {page}...")
            response = self.get_all_members(page=page, page_size=100)
            
            if not response:
                print(f"❌ Failed to fetch page {page}")
                break
            
            # Handle both cases: response is a dict with 'members' key, or response is a list directly
            if isinstance(response, list):
                members = response
            else:
                members = response.get('members', [])
            
            if not members:
                print(f"✅ No more members found on page {page}")
                break
            
            all_members.extend(members)
            print(f"✅ Page {page}: {len(members)} members (Total: {len(all_members)})")
            
            if len(members) < 100:
                print("✅ Reached end of members list")
                break
            
            page += 1
            time.sleep(0.1)  # Rate limiting
        
        return all_members
    
    def get_all_prospects_paginated(self) -> List[Dict[str, Any]]:
        """Get all prospects with pagination - NO PAGE LIMIT to get all 9000+ prospects"""
        all_prospects = []
        page = 1
        start_time = time.time()
        
        while True:  # NO MAX PAGE LIMIT - just keep going until no more data
            print(f"🔍 Fetching prospects page {page}...")
            response = self.get_all_prospects(page=page, page_size=100)
            
            if not response:
                print(f"❌ Failed to fetch page {page}")
                break
            
            # Handle both direct list response AND dict response formats
            if isinstance(response, list):
                prospects = response
            elif isinstance(response, dict):
                prospects = response.get('prospects', [])
                if not prospects:
                    # Try other possible key names
                    for key in ['data', 'results', 'items', 'content']:
                        if key in response:
                            prospects = response[key]
                            break
            else:
                prospects = []
            
            if not prospects or len(prospects) == 0:
                print(f"✅ No more prospects found on page {page}")
                break
            
            all_prospects.extend(prospects)
            print(f"✅ Page {page}: {len(prospects)} prospects (Total: {len(all_prospects)})")
            
            # If we got less than the page size, we've reached the end
            if len(prospects) < 100:
                print("✅ Reached end of prospects list")
                break
            
            page += 1
            
            # Progress update every 10 pages
            if page % 10 == 0:
                elapsed = time.time() - start_time
                print(f"⏱️ Progress: {len(all_prospects)} prospects after {elapsed:.2f} seconds")
                
            time.sleep(0.1)  # Rate limiting
        
        elapsed = time.time() - start_time
        print(f"🎉 FINAL RESULT: {len(all_prospects)} prospects fetched in {elapsed:.2f} seconds")
        return all_prospects

if __name__ == "__main__":
    # Test the ClubHub API client
    client = ClubHubAPIClient()
    
    # You would need to authenticate first
    # success = client.authenticate("your_email@example.com", "your_password")
    # if success:
    #     members = client.get_all_members_paginated()
    #     print(f"Total members: {len(members)}")
    
    print("ClubHub API Client ready!") 