#!/usr/bin/env python3
"""
ClubOS Leads API - Fetches new leads from ClubOS for real-time prospect outreach.

This module enables the bot to detect new leads as they come in through ClubOS,
allowing immediate outreach messaging.

Uses the proven authentication from ClubOSTrainingPackageAPI.
"""

import os
import sys
import re
import requests
import logging
import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubOSLeadsAPI:
    """
    ClubOS Leads API client for fetching new leads in real-time.
    
    This integrates with the ClubOS location leads endpoint to detect new prospects
    as they are created in ClubOS's system.
    
    CORRECT ENDPOINT: /api/locations/{location_id}/leads
    NOT /api/staff/{staff_id}/leads (that returns 500)
    
    Reuses proven authentication from ClubOSTrainingPackageAPI.
    """
    
    def __init__(self):
        """Initialize using ClubOSTrainingPackageAPI for authentication."""
        # Reuse the working training API for auth
        from clubos_training_api import ClubOSTrainingPackageAPI
        self._training_api = ClubOSTrainingPackageAPI()
        
        self.base_url = "https://anytime.club-os.com"
        
        # Location ID for the gym (NOT staff user ID!)
        self.location_id = "3586"  # Anytime Fitness West De Pere location ID
    
    @property
    def session(self) -> requests.Session:
        """Return the authenticated session from training API."""
        return self._training_api.session
    
    @property
    def authenticated(self) -> bool:
        """Check if authenticated."""
        return self._training_api.authenticated
    
    @property
    def logged_in_user_id(self) -> Optional[str]:
        """Get logged in user ID."""
        return self._training_api.session_data.get('loggedInUserId')
    
    @property
    def api_v3_access_token(self) -> Optional[str]:
        """Get bearer token."""
        return self._training_api.access_token or self._training_api.session_data.get('apiV3AccessToken')
    
    def authenticate(self, force: bool = False) -> bool:
        """
        Authenticate with ClubOS using the proven training API auth.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        logger.info("🔐 Authenticating with ClubOS for leads access...")
        result = self._training_api.authenticate(force=force)
        if result:
            logger.info(f"✅ Authentication successful!")
            logger.info(f"   User ID: {self.logged_in_user_id or 'Not found'}")
            logger.info(f"   Bearer token: {'Present' if self.api_v3_access_token else 'Not found'}")
        else:
            logger.error("❌ Authentication failed")
        return result
    
    def get_leads(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch leads from ClubOS location leads API.
        
        CORRECT ENDPOINT: /api/locations/{location_id}/leads
        
        Args:
            limit: Maximum number of leads to return
            
        Returns:
            List of lead dictionaries with prospect information
        """
        if not self.authenticated:
            if not self.authenticate():
                logger.error("❌ Cannot fetch leads - authentication failed")
                return []
        
        try:
            logger.info(f"📥 Fetching leads for location ID: {self.location_id}")
            
            # Build request - CORRECT ENDPOINT using location ID
            timestamp = int(time.time() * 1000)
            leads_url = f"{self.base_url}/api/locations/{self.location_id}/leads"
            
            # NOTE: Do NOT send Bearer token - session cookies handle auth
            # The authorization header causes 500 errors on this endpoint
            headers = {
                "accept": "*/*",
                "x-requested-with": "XMLHttpRequest"
            }
            
            response = self.session.get(
                leads_url,
                headers=headers,
                params={"_": timestamp},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Response format is {"data": [leads...]}
                if isinstance(data, dict) and 'data' in data:
                    leads = data['data']
                    logger.info(f"✅ Retrieved {len(leads)} leads from ClubOS")
                    return leads[:limit]
                elif isinstance(data, list):
                    logger.info(f"✅ Retrieved {len(data)} leads from ClubOS")
                    return data[:limit]
                else:
                    logger.warning(f"⚠️ Unexpected response format: {type(data)}")
                    return []
            else:
                logger.error(f"❌ Leads API failed: {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching leads: {e}")
            return []
    
    def get_new_leads_since(self, since_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get leads created within the last N minutes.
        
        Args:
            since_minutes: Number of minutes to look back
            
        Returns:
            List of recently created leads
        """
        all_leads = self.get_leads()
        
        if not all_leads:
            return []
        
        new_leads = []
        cutoff_time = datetime.now(timezone.utc)  # Use UTC since ClubOS returns UTC times
        
        for lead in all_leads:
            # ClubOS uses 'createdDateTime' field in ISO format with UTC
            created_str = lead.get('createdDateTime') or lead.get('createdDate') or lead.get('created_date')
            if created_str:
                try:
                    # ClubOS returns ISO format: "2025-11-28T10:58:50.000Z"
                    if 'T' in created_str:
                        # Remove Z and parse as UTC
                        created_str_clean = created_str.replace('Z', '')
                        if '.' in created_str_clean:
                            created = datetime.strptime(created_str_clean, '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=timezone.utc)
                        else:
                            created = datetime.strptime(created_str_clean, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
                    else:
                        created = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                    
                    # Check if within time window
                    diff_minutes = (cutoff_time - created).total_seconds() / 60
                    if diff_minutes <= since_minutes:
                        new_leads.append(lead)
                except Exception as e:
                    logger.debug(f"Could not parse date {created_str}: {e}")
                    continue
        
        logger.info(f"📊 Found {len(new_leads)} leads created in last {since_minutes} minutes")
        return new_leads
    
    def format_lead_for_outreach(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a lead dict for outreach messaging.
        
        ClubOS lead fields from /api/locations/{id}/leads:
        - tfoUserId: unique ID
        - firstName, lastName, fullName
        - email
        - mobilePhone
        - createdDateTime: ISO format UTC
        - source: e.g. "Web-1day-1"
        - userOrigin: e.g. "Web"
        - role: {name: "Prospect", id: 99, prospect: true}
        
        Args:
            lead: Raw lead data from ClubOS
            
        Returns:
            Formatted lead dict with standardized fields
        """
        return {
            'id': lead.get('tfoUserId') or lead.get('id') or lead.get('prospectId'),
            'first_name': lead.get('firstName', ''),
            'last_name': lead.get('lastName', ''),
            'full_name': lead.get('fullName') or f"{lead.get('firstName', '')} {lead.get('lastName', '')}".strip(),
            'email': lead.get('email') or lead.get('emailAddress'),
            'phone': lead.get('mobilePhone') or lead.get('phone') or lead.get('phoneNumber'),
            'created_date': lead.get('createdDateTime') or lead.get('createdDate'),
            'source': lead.get('source') or lead.get('leadSource'),
            'user_origin': lead.get('userOrigin'),
            'role': lead.get('role', {}).get('name', 'Prospect'),
            'location_id': lead.get('locationId'),
            'raw_data': lead
        }


def test_leads_api():
    """Test the ClubOS Leads API."""
    print("=" * 60)
    print("ClubOS Leads API Test")
    print("=" * 60)
    
    api = ClubOSLeadsAPI()
    
    if api.authenticate():
        print("\n📥 Fetching leads...")
        leads = api.get_leads(limit=10)
        
        if leads:
            print(f"\n✅ Found {len(leads)} leads:")
            print("-" * 40)
            
            for i, lead in enumerate(leads[:5], 1):
                formatted = api.format_lead_for_outreach(lead)
                print(f"\n{i}. {formatted['full_name']}")
                print(f"   Email: {formatted['email'] or 'N/A'}")
                print(f"   Phone: {formatted['phone'] or 'N/A'}")
                print(f"   Created: {formatted['created_date'] or 'N/A'}")
                print(f"   Source: {formatted['source'] or 'N/A'}")
            
            if len(leads) > 5:
                print(f"\n... and {len(leads) - 5} more leads")
        else:
            print("\n⚠️ No leads found or API call failed")
            
        # Test new leads detection
        print("\n" + "-" * 40)
        print("Testing new leads detection (last 60 minutes)...")
        new_leads = api.get_new_leads_since(60)
        if new_leads:
            print(f"✅ Found {len(new_leads)} new leads in last hour")
        else:
            print("📭 No new leads in last hour")
    else:
        print("\n❌ Authentication failed - cannot fetch leads")


if __name__ == "__main__":
    test_leads_api()
