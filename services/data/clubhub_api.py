"""
Enhanced ClubHub API Service - IMPROVED FROM EXPERIMENTAL CODE
Uses the experimental API integration from master_script.py but enhanced with verified patterns.
"""

import time
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...config.constants import CLUBHUB_API_URL_MEMBERS, CLUBHUB_API_URL_PROSPECTS
from ...utils.debug_helpers import debug_page_state


class EnhancedClubHubAPIService:
    """
    Enhanced ClubHub API service with improved error handling and data processing.
    Based on experimental code from master_script.py but enhanced with verified patterns.
    """
    
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        """Initialize ClubHub API service with headers"""
        self.headers = headers or self._get_fresh_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _get_fresh_headers(self) -> Dict[str, str]:
        """Get fresh ClubHub API headers using automated token system"""
        try:
            from ..authentication.clubhub_token_capture import get_valid_clubhub_tokens
            
            print("🔄 Getting fresh ClubHub tokens for API service...")
            
            # Try to get valid tokens from automated system
            tokens = get_valid_clubhub_tokens()
            
            if tokens and tokens.get('bearer_token') and tokens.get('session_cookie'):
                print("✅ Using fresh tokens from automated system")
                
                # Build headers with fresh tokens
                headers = {
                    "Authorization": f"Bearer {tokens['bearer_token']}",
                    "API-version": "1",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Cookie": f"incap_ses_132_434694={tokens['session_cookie']}"
                }
                
                return headers
            else:
                print("⚠️ No valid tokens from automation, using fallback headers")
                return self._get_default_headers()
                
        except Exception as e:
            print(f"⚠️ Error getting fresh tokens: {e}, using fallback headers")
            return self._get_default_headers()
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default ClubHub API headers (fallback)"""
        from ...config.constants import CLUBHUB_HEADERS
        return CLUBHUB_HEADERS
    
    def set_authentication(self, cookie_string: str, bearer_token: str):
        """Set authentication credentials for ClubHub API"""
        try:
            self.session.headers.update({
                "Cookie": cookie_string,
                "Authorization": f"Bearer {bearer_token}"
            })
            print("✅ ClubHub API authentication configured")
            return True
        except Exception as e:
            print(f"❌ Error setting ClubHub authentication: {e}")
            return False
    
    def refresh_headers(self):
        """Refresh headers with latest tokens"""
        try:
            fresh_headers = self._get_fresh_headers()
            self.session.headers.update(fresh_headers)
            print("✅ ClubHub API headers refreshed")
            return True
        except Exception as e:
            print(f"❌ Error refreshing headers: {e}")
            return False
    
    def fetch_clubhub_data(self, api_url: str, params: Dict[str, str], 
                          data_type_name: str = "data") -> List[Dict[str, Any]]:
        """
        Fetch data from ClubHub API with enhanced error handling and pagination.
        
        IMPROVED FROM EXPERIMENTAL CODE IN MASTER_SCRIPT.PY
        """
        print(f"📡 Attempting to fetch {data_type_name} from ClubHub API...")
        print(f"   URL: {api_url}")
        print(f"   Params: {params}")
        
        all_items_data = []
        current_page = 1
        max_pages_to_fetch = self._calculate_max_pages(params)
        
        try:
            while True:
                params["page"] = str(current_page)
                print(f"   📄 Fetching page {current_page} for {data_type_name}...")
                
                try:
                    response = self.session.get(api_url, params=params, timeout=120)
                    print(f"   📊 ClubHub API Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        page_data = response.json()
                        
                        # Debug: Print first record structure
                        if current_page == 1 and page_data:
                            print(f"   🔍 RAW JSON RESPONSE ({data_type_name} Page 1 - First Record):")
                            items_for_print = self._extract_first_record(page_data)
                            if items_for_print:
                                print(json.dumps(items_for_print[0], indent=2))
                            print("   " + "-" * 50)
                        
                        # Extract items from response
                        items_on_page = self._extract_items_from_response(page_data)
                        
                        if not items_on_page and current_page == 1:
                            print(f"   ⚠️ Warning: No {data_type_name} on page 1 or JSON structure not recognized.")
                        
                        if not items_on_page:
                            print(f"   ✅ No more {data_type_name} found. Stopping pagination.")
                            break
                        
                        all_items_data.extend(items_on_page)
                        print(f"   ✅ Found {len(items_on_page)} {data_type_name} on page {current_page}. Total: {len(all_items_data)}")
                        
                        # Check if we've reached the last page
                        if len(items_on_page) < int(params.get("pageSize", 50)):
                            print(f"   ✅ Reached last page of {data_type_name}.")
                            break
                        
                        current_page += 1
                        if max_pages_to_fetch and current_page > max_pages_to_fetch:
                            print(f"   ⚠️ Reached max_pages limit for {data_type_name}.")
                            break
                        
                        time.sleep(1.5)  # Rate limiting
                        
                    elif response.status_code in [401, 403]:
                        print(f"   ❌ Error: API Auth failed for {data_type_name}.")
                        return []
                    else:
                        print(f"   ❌ Error: API request failed for {data_type_name} (Status: {response.status_code}).")
                        return []
                        
                except requests.exceptions.Timeout:
                    print(f"   ❌ Error: API timeout for {data_type_name} page {current_page}.")
                    return all_items_data
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Error: API request exception for {data_type_name}: {e}")
                    return all_items_data
                except json.JSONDecodeError:
                    print(f"   ❌ Error: Could not decode JSON for {data_type_name}.")
                    return all_items_data if current_page > 1 else []
                    
        except Exception as e:
            print(f"   ❌ Unexpected error fetching {data_type_name}: {e}")
            return all_items_data
        
        print(f"   ✅ Fetched total {len(all_items_data)} raw {data_type_name} items.")
        return all_items_data
    
    def _calculate_max_pages(self, params: Dict[str, str]) -> Optional[int]:
        """Calculate maximum pages to fetch based on parameters"""
        try:
            days_param = int(str(params.get("days", 0)))
            if days_param <= 365 and days_param not in [2705, 4000]:
                return 50
            return None
        except ValueError:
            return 50
    
    def _extract_first_record(self, page_data: Any) -> List[Dict]:
        """Extract first record for debugging"""
        items_for_print = []
        if isinstance(page_data, list) and page_data:
            items_for_print = [page_data[0]]
        elif isinstance(page_data, dict):
            for key in ['prospects', 'members', 'data', 'items', 'results', 'leads', 'pageItems']:
                if key in page_data and isinstance(page_data[key], list) and page_data[key]:
                    items_for_print = [page_data[key][0]]
                    break
        return items_for_print
    
    def _extract_items_from_response(self, page_data: Any) -> List[Dict]:
        """Extract items from various response structures"""
        if isinstance(page_data, list):
            return page_data
        elif isinstance(page_data, dict):
            # Try common response keys
            for key in ['prospects', 'members', 'data', 'items', 'results', 'leads', 'pageItems', 'payload', 'list']:
                if key in page_data and isinstance(page_data[key], list):
                    return page_data[key]
                elif key in page_data and isinstance(page_data[key], dict):
                    # Check nested structures
                    for sub_key in ['items', 'list', 'data']:
                        if sub_key in page_data[key] and isinstance(page_data[key][sub_key], list):
                            return page_data[key][sub_key]
        return []
    
    def fetch_and_process_all_data(self, include_historical: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch and process all ClubHub data with enhanced error handling.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("🔄 Fetching and processing all ClubHub data...")
        
        try:
            # Fetch members data
            members_data = self.fetch_members_data()
            print(f"   ✅ Fetched {len(members_data)} members")
            
            # Fetch prospects data
            prospects_data = self.fetch_prospects_data()
            print(f"   ✅ Fetched {len(prospects_data)} prospects")
            
            # Fetch historical data if requested
            historical_data = []
            if include_historical:
                historical_data = self.fetch_historical_data()
                print(f"   ✅ Fetched {len(historical_data)} historical records")
            
            # Process all data
            processed_members = []
            for item in members_data:
                processed_item = self.process_api_item(item, "MembersAPI")
                if processed_item:
                    processed_members.append(processed_item)
            
            processed_prospects = []
            for item in prospects_data:
                processed_item = self.process_api_item(item, "ProspectsAPI")
                if processed_item:
                    processed_prospects.append(processed_item)
            
            processed_historical = []
            for item in historical_data:
                processed_item = self.process_api_item(item, "HistoricalAPI")
                if processed_item:
                    processed_historical.append(processed_item)
            
            result = {
                "members": processed_members,
                "prospects": processed_prospects,
                "historical": processed_historical,
                "fetch_timestamp": datetime.now().isoformat(),
                "total_records": len(processed_members) + len(processed_prospects) + len(processed_historical)
            }
            
            print(f"   ✅ Successfully processed {result['total_records']} total records")
            return result
            
        except Exception as e:
            print(f"   ❌ Error fetching and processing ClubHub data: {e}")
            return {
                "members": [],
                "prospects": [],
                "historical": [],
                "fetch_timestamp": datetime.now().isoformat(),
                "total_records": 0,
                "error": str(e)
            }


# Convenience functions for backward compatibility
def fetch_clubhub_data(api_url: str, headers: Dict[str, str], params: Dict[str, str], 
                      data_type_name: str = "data") -> List[Dict[str, Any]]:
    """Fetch data from ClubHub API"""
    service = EnhancedClubHubAPIService(headers)
    return service.fetch_clubhub_data(api_url, params, data_type_name)


def fetch_and_process_all_data(headers: Optional[Dict[str, str]] = None, 
                             include_historical: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch and process all ClubHub data"""
    service = EnhancedClubHubAPIService(headers)
    return service.fetch_and_process_all_data(include_historical) 