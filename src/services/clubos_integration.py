#!/usr/bin/env python3
"""
ClubOS Integration Service
Handles all ClubOS API interactions including authentication, calendar events, and training data
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class ClubOSIntegration:
    """Integration class to connect dashboard with working ClubOS API"""
    
    def __init__(self):
        # Prefer secrets module, then legacy config, then environment variables
        self.username = None
        self.password = None
        try:
            from config.secrets_local import get_secret
            self.username = get_secret('clubos-username')
            self.password = get_secret('clubos-password')
            if self.username and self.password:
                logger.info("🔐 ClubOS credentials loaded from secrets")
        except Exception:
            pass

        if not (self.username and self.password):
            try:
                from config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
                self.username = CLUBOS_USERNAME
                self.password = CLUBOS_PASSWORD
                logger.info("🔐 ClubOS credentials loaded from legacy config")
            except Exception:
                self.username = os.getenv('CLUBOS_USERNAME')
                self.password = os.getenv('CLUBOS_PASSWORD')
                if self.username and self.password:
                    logger.info("🔐 ClubOS credentials loaded from environment variables")
                else:
                    logger.warning("⚠️ ClubOS credentials not configured")
        
        # Initialize API instances
        self.api = None
        self.training_api = None
        self.event_manager = None
        self.authenticated = False
        
    def authenticate(self):
        """Authenticate with ClubOS"""
        try:
            # Import APIs here to avoid circular imports
            from src.clubos_real_calendar_api import ClubOSRealCalendarAPI
            from clubos_training_api_fixed import ClubOSTrainingPackageAPI
            from src.gym_bot_clean import ClubOSEventDeletion
            
            # Initialize APIs
            self.api = ClubOSRealCalendarAPI(self.username, self.password)
            self.training_api = ClubOSTrainingPackageAPI()
            self.event_manager = ClubOSEventDeletion()
            
            # Set credentials for training API
            if self.username and self.password:
                self.training_api.username = self.username
                self.training_api.password = self.password
            
            # Authenticate both calendar and training APIs
            calendar_auth = self.api.authenticate()
            training_auth = self.training_api.authenticate() if self.username and self.password else False
            
            # Consider authentication successful if at least calendar works
            self.authenticated = calendar_auth
            
            if calendar_auth:
                # Also authenticate the event manager
                self.event_manager.authenticated = True
                if training_auth:
                    logger.info("✅ ClubOS authentication successful (calendar + training)")
                else:
                    logger.info("✅ ClubOS calendar authentication successful (training API unavailable)")
            else:
                logger.warning("⚠️ ClubOS authentication failed")
                
            return self.authenticated
            
        except Exception as e:
            logger.error(f"❌ ClubOS authentication failed: {e}")
            return False
    
    def get_live_events(self):
        """Get live calendar events with REAL dates, times, and participant names using iCal"""
        try:
            logger.info("📅 Using iCAL METHOD FOR REAL EVENT DATA...")
            
            # Use the iCal calendar sync URL found in ClubOS
            calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
            
            from src.ical_calendar_parser import iCalClubOSParser
            ical_parser = iCalClubOSParser(calendar_sync_url)
            
            # Get real events from iCal feed
            real_events = ical_parser.get_real_events()
            
            formatted_events = []
            for event in real_events:
                # Format the real event data for display
                attendee_names = [attendee['name'] for attendee in event.attendees if attendee['name']]
                attendee_emails = [attendee['email'] for attendee in event.attendees if attendee['email']]
                
                # Check if this event contains training clients (not just appointments)
                # Simplified logic to avoid Flask context issues
                is_training_session = len(attendee_names) > 0 and attendee_names[0] != ''
                
                formatted_event = {
                    'id': event.uid,
                    'title': event.summary,
                    'start': event.start_time.isoformat() if event.start_time else None,
                    'end': event.end_time.isoformat() if event.end_time else None,
                    'description': event.description,
                    'location': '',  # iCal doesn't provide location
                    'participants': attendee_names,
                    'participant_emails': attendee_emails,
                    'is_training_session': is_training_session,
                    'all_day': False  # iCal doesn't provide all_day
                }
                
                formatted_events.append(formatted_event)
            
            logger.info(f"✅ Retrieved {len(formatted_events)} live events from iCal")
            return formatted_events
            
        except Exception as e:
            logger.error(f"❌ Error getting live events: {e}")
            return []
    
    def get_todays_events_lightweight(self, target_date=None):
        """Get events for a specific date without funding checks (lightweight)"""
        try:
            if target_date is None:
                target_date = datetime.now().date()
            
            logger.info(f"📅 Getting events for {target_date} (lightweight)")
            
            # Use the iCal calendar sync URL found in ClubOS
            calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
            
            from src.ical_calendar_parser import iCalClubOSParser
            ical_parser = iCalClubOSParser(calendar_sync_url)
            
            # Get real events from iCal feed
            real_events = ical_parser.get_real_events()
            
            # Filter for target date events
            target_events = []
            
            for event in real_events:
                if event.start_time and event.start_time.date() == target_date:
                    attendee_names = [attendee['name'] for attendee in event.attendees if attendee['name']]
                    
                    formatted_event = {
                        'id': event.uid,
                        'title': event.summary,
                        'start': event.start_time.isoformat() if event.start_time else None,
                        'end': event.end_time.isoformat() if event.end_time else None,
                        'description': event.description,
                        'location': '',  # iCal doesn't provide location
                        'participants': attendee_names,
                        'all_day': False  # iCal events are time-based
                    }
                    
                    target_events.append(formatted_event)
            
            logger.info(f"✅ Retrieved {len(target_events)} events for {target_date} (lightweight)")
            return target_events
            
        except Exception as e:
            logger.error(f"❌ Error getting today's events: {e}")
            return []
    
    def _is_training_session(self, attendee_names: List[str]) -> bool:
        """Determine if an event is a training session based on attendee names"""
        if not attendee_names:
            return False
        
        # Check if any attendee is a known training client
        try:
            for name in attendee_names:
                if name and name.strip():
                    # Check if this person exists in our training clients
                    conn = current_app.db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM training_clients 
                        WHERE LOWER(full_name) LIKE LOWER(?)
                    """, (f"%{name.strip()}%",))
                    
                    count = cursor.fetchone()[0]
                    conn.close()
                    
                    if count > 0:
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking if event is training session: {e}")
            return False
    
    def get_training_package_details(self, member_id: str) -> Optional[Dict]:
        """Get training package details for a member"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            if not self.authenticated:
                logger.error("❌ Cannot get training package details - not authenticated")
                return None
            
            # Get package details from training API
            package_details = self.training_api.get_member_training_payment_details(member_id)
            
            if package_details:
                logger.info(f"✅ Retrieved training package details for member {member_id}")
                return package_details
            else:
                logger.warning(f"⚠️ No training package details found for member {member_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting training package details for member {member_id}: {e}")
            return None
    
    def get_member_agreements(self, member_id: str) -> List[Dict]:
        """Get all agreements for a member"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            if not self.authenticated:
                logger.error("❌ Cannot get member agreements - not authenticated")
                return []
            
            # Get agreements from training API
            agreements = self.training_api.get_member_agreements(member_id)
            
            if agreements:
                logger.info(f"✅ Retrieved {len(agreements)} agreements for member {member_id}")
                return agreements
            else:
                logger.info(f"ℹ️ No agreements found for member {member_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting agreements for member {member_id}: {e}")
            return []
    
    def get_agreement_invoices(self, agreement_id: str) -> List[Dict]:
        """Get invoices for a specific agreement"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            if not self.authenticated:
                logger.error("❌ Cannot get agreement invoices - not authenticated")
                return []
            
            # Get invoices from training API
            invoices = self.training_api.get_agreement_invoices(agreement_id)
            
            if invoices:
                logger.info(f"✅ Retrieved {len(invoices)} invoices for agreement {agreement_id}")
                return invoices
            else:
                logger.info(f"ℹ️ No invoices found for agreement {agreement_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting invoices for agreement {agreement_id}: {e}")
            return []
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            if not self.authenticated:
                logger.error("❌ Cannot delete event - not authenticated")
                return False
            
            # Delete event using event manager
            success = self.event_manager.delete_event(event_id)
            
            if success:
                logger.info(f"✅ Successfully deleted event {event_id}")
            else:
                logger.warning(f"⚠️ Failed to delete event {event_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error deleting event {event_id}: {e}")
            return False
    
    def get_calendar_summary(self) -> Dict[str, Any]:
        """Get a summary of calendar activity"""
        try:
            events = self.get_todays_events_lightweight()
            
            # Categorize events
            training_sessions_count = 0
            appointments_count = 0
            
            appointment_keywords = ['consult', 'meeting', 'appointment', 'tour', 'assessment', 'savannah']
            
            for event in events:
                title = event.get('title', '').lower()
                participants = event.get('participants', [])
                participant_name = participants[0].lower() if participants and participants[0] else ''
                
                # Check if it's an appointment based on multiple criteria
                is_appointment = (
                    any(keyword in title for keyword in appointment_keywords) or
                    'savannah' in participant_name or
                    'savannah' in title or
                    not participants or participants[0] == ''
                )
                
                if is_appointment:
                    appointments_count += 1
                else:
                    training_sessions_count += 1
            
            return {
                'total_events': len(events),
                'training_sessions': training_sessions_count,
                'appointments': appointments_count,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting calendar summary: {e}")
            return {
                'total_events': 0,
                'training_sessions': 0,
                'appointments': 0,
                'last_updated': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get ClubOS connection status"""
        return {
            'authenticated': self.authenticated,
            'username': self.username if self.username else 'Not configured',
            'last_check': datetime.now().isoformat(),
            'apis_available': {
                'calendar': self.api is not None,
                'training': self.training_api is not None,
                'event_manager': self.event_manager is not None
            }
        }
    
    def get_members(self) -> List[Dict[str, Any]]:
        """Get all members from ClubHub API using direct API calls (same as clean_dashboard.py for prospects)"""
        try:
            logger.info("👥 Fetching members from ClubHub API...")
            
            # Use the same approach as clean_dashboard.py for prospects, but for members endpoint
            import requests
            
            # ClubHub credentials - direct definition to avoid import issues
            CLUBHUB_EMAIL = "mayo.jeremy2212@gmail.com"
            CLUBHUB_PASSWORD = "SruLEqp464_GLrF"
            
            CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
            USERNAME = CLUBHUB_EMAIL
            PASSWORD = CLUBHUB_PASSWORD
            
            headers = {
                "Content-Type": "application/json",
                "API-version": "1",
                "Accept": "application/json",
                "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            # Login to get bearer token
            login_data = {"username": USERNAME, "password": PASSWORD}
            login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
            
            if login_response.status_code != 200:
                logger.error("❌ Failed to authenticate with ClubHub API for members")
                return []
                
            login_result = login_response.json()
            bearer_token = login_result.get('accessToken')
            
            if not bearer_token:
                logger.error("❌ No access token received from ClubHub for members")
                return []
                
            session.headers.update({"Authorization": f"Bearer {bearer_token}"})
            
            # Get members from ClubHub API (similar to prospects but different endpoint)
            club_id = "1156"
            all_members = []
            page = 1
            
            while True:
                members_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/members?page={page}&pageSize=100"
                members_response = session.get(members_url)
                
                if members_response.status_code != 200:
                    break
                    
                members_data = members_response.json()
                
                if len(members_data) == 0:
                    break
                
                # Convert to our format
                for member in members_data:
                    formatted_member = {
                        'id': member.get('id') or member.get('prospectId'),
                        'prospect_id': member.get('id') or member.get('prospectId'),
                        'prospectId': member.get('id') or member.get('prospectId'),
                        'first_name': member.get('firstName', ''),
                        'last_name': member.get('lastName', ''),
                        'full_name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                        'name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                        'email': member.get('email', ''),
                        'mobile_phone': member.get('mobilePhone', ''),
                        'mobilePhone': member.get('mobilePhone', ''),
                        'phone': member.get('homePhone', ''),
                        'status': member.get('status', 'Active'),
                        'status_message': member.get('statusMessage', ''),
                        'member_since': member.get('memberSince', ''),
                        'membership_type': member.get('membershipType', ''),
                        'payment_status': member.get('paymentStatus', ''),
                        'amount_past_due': member.get('amountPastDue', 0),
                        'next_payment_date': member.get('nextPaymentDate', ''),
                        'next_payment_amount': member.get('nextPaymentAmount', 0),
                        'address1': member.get('address1', ''),
                        'city': member.get('city', ''),
                        'state': member.get('state', ''),
                        'zip': member.get('zipCode', ''),
                        'created_at': member.get('createdAt', ''),
                        'source': 'clubhub_api',
                        'last_updated': member.get('lastUpdated', '')
                    }
                    all_members.append(formatted_member)
                    
                page += 1
                
                # Limit to prevent infinite loops
                if page > 50:
                    break
            
            logger.info(f"✅ Retrieved {len(all_members)} members from ClubHub API")
            return all_members
            
        except Exception as e:
            logger.error(f"❌ Error getting members from ClubHub: {e}")
            return []
    
    def get_prospects(self) -> List[Dict[str, Any]]:
        """Get ALL prospects from ClubHub API using the correct v1.0 endpoint with extended history"""
        try:
            logger.info("📈 Fetching ALL prospects from ClubHub API...")
            
            # Use the same approach as clean_dashboard.py but with CORRECT API endpoint
            import requests
            
            # ClubHub credentials - direct definition to avoid import issues
            CLUBHUB_EMAIL = "mayo.jeremy2212@gmail.com"
            CLUBHUB_PASSWORD = "SruLEqp464_GLrF"
            
            CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
            USERNAME = CLUBHUB_EMAIL
            PASSWORD = CLUBHUB_PASSWORD
            
            headers = {
                "Content-Type": "application/json",
                "API-version": "1",
                "Accept": "application/json",
                "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            # Login to get bearer token
            login_data = {"username": USERNAME, "password": PASSWORD}
            login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
            
            if login_response.status_code != 200:
                logger.error("❌ Failed to authenticate with ClubHub API")
                return []
                
            login_result = login_response.json()
            bearer_token = login_result.get('accessToken')
            
            if not bearer_token:
                logger.error("❌ No access token received from ClubHub")
                return []
                
            session.headers.update({"Authorization": f"Bearer {bearer_token}"})
            
            # Get prospects from ClubHub API using CORRECT v1.0 endpoint with extended history
            club_id = "1156"
            all_prospects = []
            page = 1
            page_size = 100
            
            logger.info("📊 Using v1.0 API endpoint with extended history parameters to get ALL prospects...")
            
            while True:
                # Use the CORRECT v1.0 API endpoint with the right parameters for comprehensive data
                prospects_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/prospects"
                params = {
                    "page": str(page),
                    "pageSize": str(page_size),
                    "days": "10000",  # Go back 10,000 days (27 years) to get ALL historical prospects
                    "includeInactive": "true",
                    "includeAll": "true",
                    "status": "all"
                }
                
                logger.info(f"📄 Fetching prospects page {page} with extended history parameters...")
                prospects_response = session.get(prospects_url, params=params)
                
                if prospects_response.status_code != 200:
                    logger.warning(f"📄 Prospects API error on page {page}: {prospects_response.status_code}")
                    if page == 1:  # If first page fails, return empty to avoid infinite loop
                        logger.error("❌ First page of prospects failed, aborting")
                        break
                    else:
                        break  # End of data
                
                prospects_data = prospects_response.json()
                
                # Handle both dictionary and direct list responses
                if isinstance(prospects_data, list):
                    page_prospects = prospects_data
                elif isinstance(prospects_data, dict):
                    page_prospects = prospects_data.get('prospects', [])
                    if not page_prospects:
                        # Try other possible key names
                        for key in ['data', 'results', 'items', 'content']:
                            if key in prospects_data:
                                page_prospects = prospects_data[key]
                                break
                else:
                    page_prospects = []
                
                if not page_prospects or len(page_prospects) == 0:
                    logger.info(f"📄 No more prospects found on page {page}")
                    break
                
                # Convert to our format using the correct variable (page_prospects, not prospects_data)
                for prospect in page_prospects:
                    formatted_prospect = {
                        'prospect_id': prospect.get('id') or prospect.get('prospectId'),
                        'id': prospect.get('id') or prospect.get('prospectId'),
                        'prospectId': prospect.get('id') or prospect.get('prospectId'),
                        'firstName': prospect.get('firstName', ''),
                        'lastName': prospect.get('lastName', ''),
                        'first_name': prospect.get('firstName', ''),
                        'last_name': prospect.get('lastName', ''),
                        'full_name': f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip(),
                        'email': prospect.get('email', ''),
                        'mobile_phone': prospect.get('mobilePhone', ''),
                        'mobilePhone': prospect.get('mobilePhone', ''),
                        'homePhone': prospect.get('homePhone', ''),
                        'phone': prospect.get('homePhone', ''),
                        'status': prospect.get('status', 'New Lead'),
                        'status_message': prospect.get('statusMessage', ''),
                        'lead_source': prospect.get('leadSource', ''),
                        'leadSource': prospect.get('leadSource', ''),
                        'interest_level': prospect.get('interestLevel', ''),
                        'interestLevel': prospect.get('interestLevel', ''),
                        'follow_up_date': prospect.get('followUpDate', ''),
                        'followUpDate': prospect.get('followUpDate', ''),
                        'address1': prospect.get('address1', ''),
                        'city': prospect.get('city', ''),
                        'state': prospect.get('state', ''),
                        'zip': prospect.get('zipCode', ''),
                        'zipCode': prospect.get('zipCode', ''),
                        'created_at': prospect.get('createdAt', ''),
                        'createdAt': prospect.get('createdAt', ''),
                        'source': 'clubhub_api',
                        'last_updated': prospect.get('lastUpdated', ''),
                        'lastUpdated': prospect.get('lastUpdated', ''),
                        'guid': prospect.get('guid', ''),
                        'clubId': prospect.get('clubId', club_id)
                    }
                    all_prospects.append(formatted_prospect)
                
                logger.info(f"📄 Page {page}: Found {len(page_prospects)} prospects (Total so far: {len(all_prospects)})")
                
                # If we got less than the page size, we've reached the end
                if len(page_prospects) < page_size:
                    logger.info(f"📄 Received less than full page size ({len(page_prospects)} < {page_size}). Reached end of data.")
                    break
                    
                page += 1
                
                # REMOVED PAGE LIMIT TO GET ALL 9000+ PROSPECTS
                # Safety check to prevent truly infinite loops (set very high)
                if page > 200:  # Allow up to 200 pages * 100 = 20,000 prospects
                    logger.warning(f"📄 Reached safety limit of {page-1} pages")
                    break
            
            logger.info(f"✅ Retrieved {len(all_prospects)} total prospects from ClubHub API")
            return all_prospects
            
        except Exception as e:
            logger.error(f"❌ Error getting prospects from ClubHub: {e}")
            return []
    
    def get_training_clients(self) -> List[Dict[str, Any]]:
        """Get all training clients from ClubOS assignees list"""
        try:
            if not self.authenticated:
                self.authenticate()
            
            if not self.authenticated:
                logger.error("❌ Cannot get training clients - not authenticated")
                return []
            
            if not self.training_api:
                logger.error("❌ Training API not available")
                return []
            
            logger.info("📋 Fetching training clients from ClubOS assignees...")
            
            # Get assignees from the training API
            assignees = self.training_api.fetch_assignees()
            
            if not assignees:
                logger.warning("⚠️ No assignees found from ClubOS")
                return []
            
            logger.info(f"✅ Found {len(assignees)} assignees from ClubOS")
            
            # Convert assignees to training clients format
            training_clients = []
            for assignee in assignees:
                # Extract the real member information from assignee data
                member_id = assignee.get('tfoUserId') or assignee.get('id') or assignee.get('memberId')
                
                # FIXED: Use the name field directly from HTML parsing instead of trying to construct from firstName/lastName
                full_name = assignee.get('name', '').strip()
                first_name = assignee.get('firstName', '')
                last_name = assignee.get('lastName', '')
                
                # If we don't have firstName/lastName but have a full name, try to split it
                if full_name and not (first_name and last_name):
                    name_parts = full_name.split(' ', 1)  # Split on first space only
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = name_parts[1]
                    elif len(name_parts) == 1:
                        first_name = name_parts[0]
                        last_name = ''
                
                # Final name determination
                if not full_name:
                    full_name = f"{first_name} {last_name}".strip()
                
                training_client = {
                    'id': member_id,
                    'clubos_member_id': member_id,  # This is the key field for API calls
                    'member_id': member_id,
                    'member_name': full_name or f"Training Client #{str(member_id)[-4:]}" if member_id else "Unknown Client",
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_name': full_name,
                    'email': assignee.get('email', ''),
                    'phone': assignee.get('mobilePhone', assignee.get('phone', '')),
                    'status': 'Active',  # Assume active if in assignees list
                    'trainer_name': assignee.get('assignedTrainer', 'Jeremy Mayo'),
                    'membership_type': 'Personal Training',
                    'source': 'clubos_assignees',
                    'last_updated': assignee.get('lastUpdated', ''),
                    # Set default values for required fields
                    'active_packages': ['Training Package'],
                    'past_due_amount': 0.0,
                    'total_past_due': 0.0,
                    'payment_status': 'Current',
                    'sessions_remaining': 0,
                    'last_session': 'Never'
                }
                
                logger.info(f"✅ Created training client: {training_client['member_name']} (ID: {member_id})")
                training_clients.append(training_client)
            
            logger.info(f"✅ Retrieved {len(training_clients)} training clients from ClubOS assignees")
            return training_clients
            
        except Exception as e:
            logger.error(f"❌ Error getting training clients: {e}")
            return []
    
    def get_todays_events_lightweight(self) -> List[Dict[str, Any]]:
        """Get today's calendar events WITHOUT funding status checks for fast dashboard loading"""
        try:
            from datetime import datetime, date
            today = date.today()
            logger.info(f"🌟 GETTING TODAY'S EVENTS ONLY ({today}) (LIGHTWEIGHT)...")
            
            # Use the iCal calendar sync URL (same as clean_dashboard.py)
            from src.ical_calendar_parser import iCalClubOSParser
            calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
            ical_parser = iCalClubOSParser(calendar_sync_url)
            
            # Get real events from iCal feed
            real_events = ical_parser.get_real_events()
            
            todays_events = []
            for event in real_events:
                # FILTER: Only include events for TODAY
                if event.start_time and event.start_time.date() == today:
                    # Format the real event data for display
                    attendee_names = [attendee['name'] for attendee in event.attendees if attendee['name']]
                    attendee_emails = [attendee['email'] for attendee in event.attendees if attendee['email']]
                    
                    # Check if this event contains training clients (not just appointments)
                    is_training_session = len(attendee_names) > 0 and attendee_names[0] != ''
                    
                    formatted_event = {
                        'id': event.uid,
                        'title': event.summary,
                        'start': event.start_time.isoformat() if event.start_time else None,
                        'end': event.end_time.isoformat() if event.end_time else None,
                        'description': event.description,
                        'location': '',  # iCal doesn't provide location
                        'participants': attendee_names,
                        'participant_emails': attendee_emails,
                        'is_training_session': is_training_session,
                        'all_day': False,  # iCal doesn't provide all_day
                        'start_time_obj': event.start_time  # Keep for sorting
                    }
                    todays_events.append(formatted_event)
            
            # SORT: Sort events by start time (earliest first)
            todays_events.sort(key=lambda x: x['start_time_obj'] if x['start_time_obj'] else datetime.min)
            
            # Remove the sorting helper field
            for event in todays_events:
                del event['start_time_obj']
            
            logger.info(f"✅ Retrieved {len(todays_events)} events for TODAY ({today}) from iCal (filtered from {len(real_events)} total events)")
            return todays_events
            
        except Exception as e:
            logger.error(f"❌ Error getting today's events: {e}")
            return []
    
    def get_calendar_summary(self) -> Dict[str, Any]:
        """Get calendar summary statistics"""
        try:
            events = self.get_todays_events_lightweight()
            training_sessions = [e for e in events if e.get('is_training_session', False)]
            
            return {
                'total_events': len(events),
                'training_sessions': len(training_sessions),
                'classes': len(events) - len(training_sessions),
                'updated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error getting calendar summary: {e}")
            return {
                'total_events': 0,
                'training_sessions': 0,
                'classes': 0,
                'updated_at': None
            }
