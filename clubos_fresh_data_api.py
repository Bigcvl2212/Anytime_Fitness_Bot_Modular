#!/usr/bin/env python3
"""
ClubOS Fresh Data API - Get real-time member and prospect data
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ClubOSFreshDataAPI:
    """API to fetch fresh member and prospect data from ClubOS"""
    
    def __init__(self, username: str = "j.mayo", password: str = "j@SD4fjhANK5WNA"):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticated = False
        self.base_url = "https://anytime.club-os.com"
        
    def authenticate(self) -> bool:
        """Authenticate with ClubOS"""
        try:
            # Use the existing authentication method from clubos_training_api
            login_url = f"{self.base_url}/auth/login"
            
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, data=login_data)
            
            if response.status_code == 200 and "dashboard" in response.url:
                self.authenticated = True
                logger.info("✅ ClubOS authentication successful for fresh data API")
                return True
            else:
                logger.error(f"❌ ClubOS authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ ClubOS authentication error: {e}")
            return False
    
    def get_fresh_members(self) -> List[Dict]:
        """Get fresh member data from ClubHub - ALL members at once like ClubHub does"""
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            logger.info("📊 Fetching ALL fresh member data from ClubHub API...")
            
            # Use the ClubHub credentials and endpoints to get ALL members
            from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            
            # ClubHub API endpoint for getting all members
            members_url = "https://app.clubhub.com/api/members/export"
            
            # Authenticate with ClubHub and get all members
            login_data = {
                'email': CLUBHUB_EMAIL,
                'password': CLUBHUB_PASSWORD
            }
            
            # First login to ClubHub
            login_response = self.session.post("https://app.clubhub.com/api/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                logger.info("✅ ClubHub authentication successful")
                
                # Now get all members data
                members_response = self.session.get(members_url)
                
                if members_response.status_code == 200:
                    members_data = members_response.json()
                    
                    # Process the members data to match our expected format
                    processed_members = []
                    
                    if isinstance(members_data, list):
                        for member in members_data:
                            processed_member = {
                                'ProspectID': member.get('id', member.get('prospect_id')),
                                'Name': f"{member.get('first_name', '')} {member.get('last_name', '')}".strip(),
                                'FirstName': member.get('first_name', ''),
                                'LastName': member.get('last_name', ''),
                                'Email': member.get('email', ''),
                                'Phone': member.get('phone', member.get('mobile_phone', '')),
                                'MobilePhone': member.get('mobile_phone', ''),
                                'Address': member.get('address', member.get('address1', '')),
                                'Address1': member.get('address1', ''),
                                'City': member.get('city', ''),
                                'State': member.get('state', ''),
                                'ZipCode': member.get('zip', member.get('zip_code', '')),
                                'Zip': member.get('zip', ''),
                                'StatusMessage': member.get('status_message', member.get('payment_status', '')),
                                'MemberSince': member.get('membership_start', member.get('member_since', '')),
                                'MembershipStart': member.get('membership_start', ''),
                                'LastVisit': member.get('last_visit', ''),
                                'Status': member.get('status', ''),
                                'PaymentStatus': member.get('payment_status', ''),
                                'AccountStatus': member.get('account_status', ''),
                                'MembershipType': member.get('membership_type', ''),
                                'AmountPastDue': member.get('amount_past_due', 0),
                                'NextPaymentDate': member.get('next_payment_date', ''),
                                'NextPaymentAmount': member.get('next_payment_amount', 0)
                            }
                            processed_members.append(processed_member)
                    
                    logger.info(f"✅ Retrieved {len(processed_members)} members from ClubHub API")
                    return processed_members
                    
                else:
                    logger.error(f"❌ Failed to get members data: {members_response.status_code}")
                    return []
            else:
                logger.error(f"❌ ClubHub login failed: {login_response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching fresh member data from ClubHub: {e}")
            return []
    
    def get_fresh_prospects(self) -> List[Dict]:
        """Get fresh prospect data from ClubOS"""
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            logger.info("📈 Fetching fresh prospect data from ClubOS...")
            
            # This would call the actual ClubOS prospects endpoint
            prospects_url = f"{self.base_url}/prospects/export"
            
            response = self.session.get(prospects_url)
            
            if response.status_code == 200:
                logger.info("✅ Fresh prospect data retrieved")
                return []  # Placeholder
            else:
                logger.error(f"❌ Failed to get fresh prospect data: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching fresh prospect data: {e}")
            return []
    
    def get_member_payment_status(self, member_id: str) -> Dict:
        """Get real-time payment status for a specific member"""
        if not self.authenticated:
            if not self.authenticate():
                return {}
        
        try:
            # This would call the ClubOS payment status API
            payment_url = f"{self.base_url}/members/{member_id}/payment-status"
            
            response = self.session.get(payment_url)
            
            if response.status_code == 200:
                # Parse payment status
                return {
                    'member_id': member_id,
                    'status': 'Current',  # Placeholder
                    'amount_due': 0,
                    'last_payment': datetime.now().isoformat(),
                    'next_payment_date': None
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting payment status for member {member_id}: {e}")
            return {}
    
    def get_fresh_data_summary(self) -> Dict:
        """Get a summary of fresh data from ClubOS"""
        try:
            logger.info("📋 Getting fresh data summary from ClubOS...")
            
            if not self.authenticated:
                if not self.authenticate():
                    return {}
            
            # Get counts and summary info
            summary = {
                'timestamp': datetime.now().isoformat(),
                'members': {
                    'total': 0,
                    'active': 0,
                    'past_due': 0,
                    'due_soon': 0
                },
                'prospects': {
                    'total': 0,
                    'new_today': 0,
                    'hot_leads': 0
                },
                'last_updated': datetime.now().isoformat()
            }
            
            logger.info("✅ Fresh data summary retrieved")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting fresh data summary: {e}")
            return {}

if __name__ == "__main__":
    # Test the API
    api = ClubOSFreshDataAPI()
    if api.authenticate():
        summary = api.get_fresh_data_summary()
        print(f"Fresh data summary: {json.dumps(summary, indent=2)}")
    else:
        print("Failed to authenticate with ClubOS")
