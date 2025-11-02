#!/usr/bin/env python3
"""
ClubHub API Client - Comprehensive implementation based on discovered endpoints
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode
from ..authentication.unified_auth_service import get_unified_auth_service, AuthenticationSession

logger = logging.getLogger(__name__)

class ClubHubAPIClient:
    """ClubHub API Client with all discovered endpoints"""
    
    def __init__(self):
        import os
        self.base_url = os.getenv('CLUBHUB_BASE_URL', 'https://clubhub-ios-api.anytimefitness.com')
        self.club_id = os.getenv('DEFAULT_CLUB_ID', '1156')
        self.api_version = "1"
        
        # Get unified authentication service
        self.auth_service = get_unified_auth_service()
        self.auth_session: Optional[AuthenticationSession] = None
        
        # Legacy attributes for backward compatibility
        self.auth_token = None
        self.headers = {
            "Host": "clubhub-ios-api.anytimefitness.com",
            "API-version": "1",
            "Accept": "application/json",
            "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
            "Accept-Language": "en-US",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
    
    def authenticate(self, email: str = None, password: str = None) -> bool:
        """Authenticate using the unified authentication service"""
        try:
            print("Authenticating ClubHub API Client")
            
            # Use unified authentication service
            self.auth_session = self.auth_service.authenticate_clubhub(email, password)
            
            if not self.auth_session or not self.auth_session.authenticated:
                logger.info("ClubHub authentication failed")
                return False

            # Update legacy attributes for backward compatibility
            self.auth_token = self.auth_session.clubhub_bearer_token
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

            logger.info("ClubHub authentication successful")
            logger.debug(f"Bearer token: {self.auth_token[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def set_auth_token(self, token: str):
        """Set authentication token manually"""
        self.auth_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        logger.info("ClubHub auth token set")
    
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
                     json_data: Dict[str, Any] = None, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with error handling and retry logic"""
        import time

        for attempt in range(retries):
            try:
                if attempt > 0:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    logger.warning(f"🔄 Retrying request (attempt {attempt + 1}/{retries}) after {wait_time}s...")
                    time.sleep(wait_time)

                if method == "GET":
                    response = requests.get(url, headers=self.headers, params=params, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, params=params, json=json_data, timeout=30)
                elif method == "PUT":
                    response = requests.put(url, headers=self.headers, params=params, json=json_data, timeout=30)
                elif method == "DELETE":
                    response = requests.delete(url, headers=self.headers, params=params, timeout=30)
                else:
                    logger.error(f"❌ Unsupported HTTP method: {method}")
                    return None
            
                if response.status_code == 200:
                    # Handle empty responses (which can happen with DELETE requests)
                    if not response.text or response.text.strip() == '':
                        # Return success indicator for empty responses
                        return {'success': True, 'message': 'Operation completed successfully'}

                    try:
                        return response.json()
                    except ValueError as json_error:
                        # Handle malformed JSON responses
                        logger.error(f"❌ JSON parsing error for {method} {url}: {json_error}")
                        logger.error(f"Response text: {response.text[:500]}")
                        return {'error': f'Invalid JSON response: {json_error}', 'response_text': response.text[:500]}

                # Handle retryable errors (5xx server errors, timeouts, connection issues)
                elif response.status_code >= 500 and attempt < retries - 1:
                    logger.warning(f"⚠️ Server error {response.status_code} for {method} {url} - will retry")
                    continue
                else:
                    # Non-retryable error or final attempt
                    logger.error(f"❌ {method} {url} failed: {response.status_code}")
                    logger.error(f"Response: {response.text[:500]}")
                    return {'error': f'HTTP {response.status_code}', 'response_text': response.text[:500]}

            except Exception as e:
                # Handle connection errors, timeouts, etc.
                if attempt < retries - 1:
                    logger.warning(f"⚠️ Request error for {method} {url}: {e} - will retry")
                    continue
                else:
                    logger.error(f"❌ Final request error: {e}")
                    return {'error': f'Connection error: {e}'}

        # If we get here, all retries failed
        logger.error(f"❌ All retry attempts failed for {method} {url}")
        return {'error': 'All retry attempts failed'}
    
    def get_all_members_paginated(self) -> List[Dict[str, Any]]:
        """Get all members with pagination - OPTIMIZED with parallel page fetching"""
        start_time = time.time()
        
        # First, determine total number of pages by checking until we find the end
        print("🔍 Determining total pages for parallel fetching...")
        total_pages = 0
        page = 1
        max_pages = 100  # Safety limit to prevent infinite loops
        
        while page <= max_pages:
            response = self.get_all_members(page=page, page_size=100)
            if response:
                if isinstance(response, list):
                    members = response
                else:
                    members = response.get('members', [])
                
                if members and len(members) > 0:
                    total_pages += 1
                    print(f"📄 Found page {page} with {len(members)} members")
                    
                    # If we got less than 100 members, we've reached the end
                    if len(members) < 100:
                        print(f"✅ Reached end of members list on page {page}")
                        break
                else:
                    print(f"✅ No more members found on page {page}")
                    break
            else:
                print(f"❌ Failed to fetch page {page}")
                break
            
            page += 1
        
        if total_pages == 0:
            print("❌ Could not determine total pages")
            return []
        
        print(f"📊 Estimated {total_pages} pages to fetch, starting parallel processing...")
        
        # Fetch all pages in parallel
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def fetch_members_page(page_num):
            """Fetch a single members page"""
            try:
                response = self.get_all_members(page=page_num, page_size=100)
                if response:
                    if isinstance(response, list):
                        members = response
                    else:
                        members = response.get('members', [])
                    
                    if members:
                        print(f"✅ Page {page_num}: {len(members)} members")
                        return members
                return []
            except Exception as e:
                print(f"❌ Error fetching page {page_num}: {e}")
                return []
        
        all_members = []
        completed_pages = 0
        
        # Use ThreadPoolExecutor to fetch pages in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all page fetching tasks
            future_to_page = {executor.submit(fetch_members_page, page_num): page_num for page_num in range(1, total_pages + 1)}
            
            # Process completed tasks
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    members = future.result()
                    if members:
                        all_members.extend(members)
                        completed_pages += 1
                        
                        # Progress update
                        if completed_pages % 5 == 0:
                            elapsed = time.time() - start_time
                            print(f"⏱️ Progress: {completed_pages}/{total_pages} pages, {len(all_members)} members after {elapsed:.2f} seconds")
                            
                except Exception as e:
                    print(f"❌ Error processing page {page_num}: {e}")
        
        elapsed = time.time() - start_time
        print(f"🎉 FINAL RESULT: {len(all_members)} members fetched from {completed_pages} pages in {elapsed:.2f} seconds")
        return all_members
    
    def get_all_prospects_paginated(self) -> List[Dict[str, Any]]:
        """Get all prospects with pagination - OPTIMIZED with parallel page fetching"""
        start_time = time.time()
        
        # First, determine total number of pages by checking until we find the end
        print("🔍 Determining total pages for parallel fetching...")
        total_pages = 0
        page = 1
        max_pages = 200  # Safety limit to prevent infinite loops
        
        while page <= max_pages:
            response = self.get_all_prospects(page=page, page_size=100)
            if response:
                if isinstance(response, list):
                    prospects = response
                elif isinstance(response, dict):
                    prospects = response.get('prospects', [])
                    if not prospects:
                        for key in ['data', 'results', 'items', 'content']:
                            if key in response:
                                prospects = response[key]
                                break
                else:
                    prospects = []
                
                if prospects and len(prospects) > 0:
                    total_pages += 1
                    print(f"📄 Found page {page} with {len(prospects)} prospects")
                    
                    # If we got less than 100 prospects, we've reached the end
                    if len(prospects) < 100:
                        print(f"✅ Reached end of prospects list on page {page}")
                        break
                else:
                    print(f"✅ No more prospects found on page {page}")
                    break
            else:
                print(f"❌ Failed to fetch page {page}")
                break
            
            page += 1
        
        if total_pages == 0:
            print("❌ Could not determine total pages")
            return []
        
        print(f"📊 Estimated {total_pages} pages to fetch, starting parallel processing...")
        
        # Fetch all pages in parallel
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def fetch_prospects_page(page_num):
            """Fetch a single prospects page"""
            try:
                response = self.get_all_prospects(page=page_num, page_size=100)
                if response:
                    if isinstance(response, list):
                        prospects = response
                    elif isinstance(response, dict):
                        prospects = response.get('prospects', [])
                        if not prospects:
                            for key in ['data', 'results', 'items', 'content']:
                                if key in response:
                                    prospects = response[key]
                                    break
                    else:
                        prospects = []
                    
                    if prospects:
                        print(f"✅ Page {page_num}: {len(prospects)} prospects")
                        return prospects
                return []
            except Exception as e:
                print(f"❌ Error fetching page {page_num}: {e}")
                return []
        
        all_prospects = []
        completed_pages = 0
        
        # Use ThreadPoolExecutor to fetch pages in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all page fetching tasks
            future_to_page = {executor.submit(fetch_prospects_page, page_num): page_num for page_num in range(1, total_pages + 1)}
            
            # Process completed tasks
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    prospects = future.result()
                    if prospects:
                        all_prospects.extend(prospects)
                        completed_pages += 1
                        
                        # Progress update
                        if completed_pages % 5 == 0:
                            elapsed = time.time() - start_time
                            print(f"⏱️ Progress: {completed_pages}/{total_pages} pages, {len(all_prospects)} prospects after {elapsed:.2f} seconds")
                            
                except Exception as e:
                    print(f"❌ Error processing page {page_num}: {e}")
        
        elapsed = time.time() - start_time
        print(f"🎉 FINAL RESULT: {len(all_prospects)} prospects fetched from {completed_pages} pages in {elapsed:.2f} seconds")
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