#!/usr/bin/env python3
"""
FIXED ClubOS Messaging Client - Implements EXACT working cURL flow
Key fix: Proper delegation to get delegated Bearer token before messaging
"""

import requests
import logging
import re
import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from bs4 import BeautifulSoup
import urllib3
import time
import hashlib
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from .authentication.unified_auth_service import get_unified_auth_service, AuthenticationSession

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ClubOSMessagingClient:
    """
    FIXED ClubOS Messaging Client that implements the EXACT working cURL flow:
    1. Authenticate to get initial Bearer token
    2. Delegate to member to get DELEGATED Bearer token (critical!)
    3. Use delegated token and exact payload structure from working cURL
    """
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.base_url = "https://anytime.club-os.com"
        
        # Get unified authentication service
        self.auth_service = get_unified_auth_service()
        self.auth_session: Optional[AuthenticationSession] = None
        
        # Legacy attributes for backward compatibility
        self.session = None
        self.authenticated = False
        self.staff_id = None
        self.logged_in_user_id = None
        self.delegated_user_id = None
        self.delegated_bearer_token = None
        
        # Thread safety for parallel processing
        self._lock = Lock()

        # Message cache to prevent redundant syncs
        self._message_cache = {}
        self._cache_timestamps = {}

    def authenticate(self) -> bool:
        """Authenticate using the unified authentication service"""
        try:
            logger.info("Authenticating ClubOS Messaging Client Simple")

            # CRITICAL FIX: Invalidate any cached session to force fresh authentication
            # This prevents Flask from reusing corrupted/invalid cached sessions
            session_key = f"clubos_{self.username}"
            if session_key in self.auth_service._sessions:
                logger.info(f"🔄 Invalidating cached ClubOS session for {self.username} to force fresh auth")
                del self.auth_service._sessions[session_key]

            # Use unified authentication service
            self.auth_session = self.auth_service.authenticate_clubos(self.username, self.password)
            
            if not self.auth_session or not self.auth_session.authenticated:
                logger.error("ClubOS authentication failed")
                return False
            
            # Update legacy attributes for backward compatibility
            self.session = self.auth_session.session
            self.authenticated = True
            self.logged_in_user_id = self.auth_session.logged_in_user_id
            self.delegated_user_id = self.auth_session.delegated_user_id
            self.delegated_bearer_token = self.auth_session.bearer_token
            
            # Update username from session for legacy compatibility
            self.username = self.auth_session.username
            
            logger.info(f"✅ Authentication successful - User ID: {self.logged_in_user_id}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def delegate_to_member(self, member_id: str) -> bool:
        """
        CRITICAL: Delegate to member to get DELEGATED Bearer token
        This is what the working cURL has that we're missing!
        
        IMPORTANT: Always sets self.delegated_user_id to the member_id we're delegating to,
        not relying on cookies which may be stale from a previous delegation.
        """
        try:
            logger.info(f"🔄 Delegating to member {member_id} to get delegated Bearer token")
            
            # CRITICAL FIX: Set delegated_user_id BEFORE making API call
            # This ensures we use the correct member even if ClubOS doesn't return updated cookies
            self.delegated_user_id = member_id
            logger.info(f"📝 Set delegated_user_id to {member_id} for this message")
            
            # Step 1: Call delegation endpoint that should give us new Bearer token
            timestamp = int(time.time() * 1000)
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false?_={timestamp}"
            
            delegate_headers = {
                "X-Requested-With": "XMLHttpRequest", 
                "Referer": f"{self.base_url}/action/LeadProfile/view"
            }
            
            delegate_response = self.session.get(delegate_url, headers=delegate_headers, verify=False, timeout=15)
            delegate_response.raise_for_status()
            
            logger.info(f"✅ Delegation call successful - status: {delegate_response.status_code}")
            
            # Step 2: Check if we got new Bearer token or delegation cookies
            new_bearer_token = self.session.cookies.get('apiV3AccessToken')
            delegated_user_id_cookie = self.session.cookies.get('delegatedUserId')
            
            # Log if cookie differs from what we set (informational only)
            if delegated_user_id_cookie and delegated_user_id_cookie != member_id:
                logger.warning(f"⚠️ Cookie delegatedUserId={delegated_user_id_cookie} differs from target member_id={member_id}")
            
            if new_bearer_token:
                self.delegated_bearer_token = new_bearer_token
                # Update session to use delegated Bearer token
                self.session.headers["Authorization"] = f"Bearer {new_bearer_token}"
                logger.info(f"🔑 Updated to delegated Bearer token")
            
            # Step 3: Navigate to delegated member profile to establish context
            member_profile_url = f"{self.base_url}/action/LeadProfile/view"
            profile_response = self.session.get(member_profile_url, verify=False, timeout=30)
            
            if profile_response.status_code == 200:
                logger.info(f"✅ Established delegated context for member {member_id}")
                return True
            else:
                logger.error(f"❌ Failed to establish delegated context: {profile_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Delegation error: {e}")
            return False
    
    def get_delegated_form_data(self) -> Dict[str, str]:
        """
        CRITICAL: Get COMPLETE form data from ClubOS messaging popup
        This extracts the member's ACTUAL data to preserve it!
        """
        try:
            logger.info("📋 Getting messaging popup with member's ACTUAL data...")
            
            # Step 1: POST to /action/FollowUp to get the messaging popup
            followup_url = f"{self.base_url}/action/FollowUp"
            
            # Use EXACT payload from working cURL
            popup_payload = {
                "followUpUserId": self.delegated_user_id,
                "followUpType": "3"
            }
            
            popup_headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/action/LeadProfile/view"
            }
            
            popup_response = self.session.post(
                followup_url,
                data=popup_payload,
                headers=popup_headers,
                verify=False,
                timeout=30
            )
            
            if popup_response.status_code != 200:
                logger.error(f"❌ Failed to get messaging popup: {popup_response.status_code}")
                return {}
            
            # Debug logging without saving files
            logger.info(f"💾 Retrieved member popup data ({len(popup_response.text)} chars)")
            
            # Step 2: Extract ALL form data from the popup
            soup = BeautifulSoup(popup_response.text, 'html.parser')
            form_data = {}
            
            # Find the main form (usually the largest one)
            forms = soup.find_all("form")
            if not forms:
                logger.error("❌ No forms found in popup")
                return {}
            
            # Use the form with the most fields
            main_form = max(forms, key=lambda f: len(f.find_all(["input", "select", "textarea"])))
            
            # Extract all input fields
            for input_elem in main_form.find_all("input"):
                name = input_elem.get("name")
                if name:
                    value = input_elem.get("value", "")
                    input_type = input_elem.get("type", "text").lower()
                    
                    if input_type in ["checkbox", "radio"]:
                        if input_elem.has_attr("checked"):
                            form_data[name] = value or "on"
                    else:
                        form_data[name] = value
            
            # Extract all select fields
            for select_elem in main_form.find_all("select"):
                name = select_elem.get("name")
                if name:
                    selected = select_elem.find("option", selected=True)
                    if selected:
                        form_data[name] = selected.get("value", "")
                    else:
                        # Use first option as default
                        first_option = select_elem.find("option")
                        form_data[name] = first_option.get("value", "") if first_option else ""
            
            # Extract all textarea fields
            for textarea_elem in main_form.find_all("textarea"):
                name = textarea_elem.get("name")
                if name:
                    form_data[name] = textarea_elem.text.strip()
            
            # Log the extracted member data (safely)
            logger.info(f"✅ Extracted {len(form_data)} form fields from messaging popup")
            
            # Show member data that was preserved
            member_fields = ["followUpUser.firstName", "followUpUser.lastName", "followUpUser.email", "followUpUser.mobilePhone"]
            for field in member_fields:
                if field in form_data and form_data[field]:
                    logger.info(f"   Preserved: {field} = {form_data[field]}")
            
            return form_data
            
        except Exception as e:
            logger.error(f"❌ Error getting delegated form data: {e}")
            return {}
    
    def search_member_by_name(self, first_name: str, last_name: str, member_type: str = "member") -> Optional[str]:
        """
        Search for a member, prospect, or training client by first and last name
        Returns their ClubOS ID
        """
        try:
            logger.info(f"🔍 Searching ClubOS for {member_type}: {first_name} {last_name}")
            
            # Step 1: Get search page first
            search_page_url = f"{self.base_url}/action/Dashboard/search"
            search_response = self.session.get(search_page_url, verify=False, timeout=30)
            
            if search_response.status_code != 200:
                logger.error(f"❌ Failed to load search page: {search_response.status_code}")
                return None
            
            search_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': search_page_url,
                'Origin': self.base_url
            }
            
            search_url = f"{self.base_url}/action/UserSearch/"
            
            # Get form tokens from the search page
            soup = BeautifulSoup(search_response.text, 'html.parser')
            source_page_input = soup.find("input", {"name": "_sourcePage"})
            fp_input = soup.find("input", {"name": "__fp"})
            
            search_data = {
                'filter.keyword': f"{first_name} {last_name}",
                'actAs': 'loggedIn',
                '_sourcePage': source_page_input.get('value') if source_page_input else '',
                '__fp': fp_input.get('value') if fp_input else ''
            }
            
            search_result = self.session.post(
                search_url, 
                data=search_data, 
                headers=search_headers,
                verify=False, 
                timeout=30
            )
                
            if search_result.status_code != 200:
                logger.error(f"❌ Search failed: {search_result.status_code}")
                return None
            
            # Parse search results to extract ClubOS ID from data-id attribute
            result_soup = BeautifulSoup(search_result.text, 'html.parser')
            
            # Look for search-result divs with data-id and data-full-name attributes
            search_result_divs = result_soup.find_all('div', class_='search-result')
            
            for div in search_result_divs:
                data_id = div.get('data-id')
                data_full_name = div.get('data-full-name', '')
                
                # Check if this result matches our search criteria
                if data_id and data_full_name:
                    if (first_name.lower() in data_full_name.lower() and 
                        last_name.lower() in data_full_name.lower()):
                        logger.info(f"✅ Found '{data_full_name}' with ClubOS ID: {data_id}")
                        return data_id
            
            logger.warning(f"⚠️ No exact match found for '{first_name} {last_name}' in search results")
            return None
                
        except Exception as e:
            logger.error(f"❌ Error searching for {first_name} {last_name}: {e}")
            return None

    def send_message(self, member_id: str, message_text: str, channel: str = "sms", member_data: dict = None) -> bool:
        """
        FIXED: Send message using EXACT working cURL flow
        1. Authenticate
        2. Delegate to member (get delegated Bearer token)
        3. Extract member's ACTUAL data from ClubOS popup (preserves their profile!)
        4. Only modify message fields, keep all member data intact
        """
        try:
            if not self.authenticated and not self.authenticate():
                logger.error("❌ Authentication failed")
                return False
            
            # Search for ClubOS ID if we have member data with name
            clubos_member_id = member_id
            
            if member_data:
                first_name = None
                last_name = None
                
                # Try to get first/last name from multiple possible fields
                if member_data.get('first_name') and member_data.get('last_name'):
                    first_name = member_data['first_name']
                    last_name = member_data['last_name']
                elif member_data.get('full_name'):
                    # Parse full_name into first and last
                    full_name_parts = member_data['full_name'].strip().split()
                    if len(full_name_parts) >= 2:
                        first_name = full_name_parts[0]
                        last_name = ' '.join(full_name_parts[1:])
                elif member_data.get('name'):
                    # Parse name field into first and last
                    name_parts = member_data['name'].strip().split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = ' '.join(name_parts[1:])
                
                if first_name and last_name:
                    # Determine member type from data structure
                    member_type = "prospect"
                    if member_data.get('prospect_id'):
                        member_type = "prospect"
                    elif member_data.get('member_id'):
                        member_type = "member"
                    elif member_data.get('training_client_id'):
                        member_type = "training_client"
                    
                    logger.info(f"🔍 Searching ClubOS for {member_type}: {first_name} {last_name}")
                    found_id = self.search_member_by_name(first_name, last_name, member_type)
                    if found_id:
                        clubos_member_id = found_id
                        logger.info(f"✅ Found ClubOS ID {found_id} for {first_name} {last_name}")
                    else:
                        logger.warning(f"⚠️ Could not find ClubOS ID for {first_name} {last_name}, using provided ID {member_id}")
                
            # CRITICAL: Delegate to member first to get delegated Bearer token
            if not self.delegate_to_member(clubos_member_id):
                logger.error("❌ Failed to delegate to member")
                return False
            
            logger.info(f"📱 Sending {channel} message to member {clubos_member_id}: '{message_text[:50]}...'")
            
            # CRITICAL: Get the member's ACTUAL data from ClubOS popup
            member_form_data = self.get_delegated_form_data()
            if not member_form_data:
                logger.error("❌ Failed to get member's form data")
                return False
            
            # Verify we have required CSRF tokens
            if not member_form_data.get('_sourcePage') or not member_form_data.get('__fp'):
                logger.error("❌ Missing CSRF tokens in member form data")
                return False
            
            logger.info("✅ Successfully extracted member's actual data - preserving profile!")
            
            # Step 3: ONLY modify the message fields, keep everything else intact
            # Start with the member's complete form data
            final_payload = member_form_data.copy()
            
            # Override ONLY the message-related fields
            message_overrides = {
                # Action field - controls SMS vs Email
                "followUpLog.followUpAction": "3" if channel == "sms" else "2",
                
                # Message content based on channel
                "textMessage": message_text if channel == "sms" else "",
                "emailMessage": "<p></p>" if channel == "sms" else f"<p>{message_text}</p>",
                
                # Required status fields
                "followUpStatus": "1",
                "followUpType": "3",
                "followUpSequence": "",
                "memberSalesFollowUpStatus": "2",
                "followUpLog.outcome": "2",
                
                # Email subject
                "emailSubject": " has sent you a message",
                
                # Add professional bot note to existing notes (don't overwrite)
                "followUpOutcomeNotes": f"Message sent via Gym Bot on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                
                # Event fields
                "event.createdFor.tfoUserId": self.logged_in_user_id,
                "event.eventType": "LEAD",
                "duration": "2",
                "event.remindAttendeesMins": "120",
                
                # Default accounts
                "memberStudioSalesDefaultAccount": self.logged_in_user_id,
                "memberStudioSupportDefaultAccount": self.logged_in_user_id,
                "ptSalesDefaultAccount": self.logged_in_user_id,
                "ptSupportDefaultAccount": self.logged_in_user_id
            }
            
            # Apply message overrides to the member's data
            final_payload.update(message_overrides)
            
            # Convert to form data while preserving duplicates
            form_data = []
            for key, value in final_payload.items():
                form_data.append((key, str(value)))
            
            # Headers matching EXACT working cURL
            headers = {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://anytime.club-os.com",
                "priority": "u=1, i",
                "referer": "https://anytime.club-os.com/action/LeadProfile/view",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors", 
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest"
            }
            
            # Use delegated Bearer token with timeout optimization
            if self.delegated_bearer_token:
                headers["authorization"] = f"Bearer {self.delegated_bearer_token}"
            elif self.session.cookies.get('apiV3AccessToken'):
                headers["authorization"] = f"Bearer {self.session.cookies.get('apiV3AccessToken')}"
            
            # Submit to ClubOS with reduced timeout for faster processing
            submit_url = "https://anytime.club-os.com/action/FollowUp/save"
            
            logger.info(f"📤 Submitting message with PRESERVED member data...")
            logger.info(f"   Member ID: {clubos_member_id}")
            logger.info(f"   Member Name: {final_payload.get('followUpUser.firstName', '')} {final_payload.get('followUpUser.lastName', '')}")
            logger.info(f"   Member Email: {final_payload.get('followUpUser.email', '')}")
            logger.info(f"   Message: {message_text[:50]}...")
            logger.info(f"   Channel: {channel}")
            
            response = self.session.post(
                submit_url,
                data=form_data,
                headers=headers,
                timeout=15,  # Reduced timeout for faster processing
                verify=False,
                allow_redirects=False
            )
            
            logger.info(f"📋 Response status: {response.status_code}")
            
            # Log response without saving files
            logger.info(f"💾 Response received ({len(response.text)} chars)")
            
            # Check for success
            if 200 <= response.status_code < 400:
                if "something isn't right" in response.text.lower():
                    logger.error(f"❌ CSRF validation failed")
                    return False
                elif "has been texted" in response.text.lower() or "has been emailed" in response.text.lower():
                    logger.info(f"✅ Message sent successfully with PRESERVED member data!")
                    return True
                else:
                    logger.info(f"✅ Message submission successful (status {response.status_code})")
                    return True
            else:
                logger.error(f"❌ HTTP error {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception sending message: {e}")
            return False
    
    def send_bulk_campaign_parallel(self, member_data_list: List[Dict[str, Any]] = None, member_ids: List[str] = None, message: str = "", message_type: str = "sms", max_workers: int = 5) -> Dict[str, Any]:
        """Send bulk campaign using parallel processing for much faster execution"""
        # Handle both parameter styles
        if member_data_list:
            members_to_process = member_data_list
            total_count = len(member_data_list)
        elif member_ids:
            members_to_process = [{'member_id': mid} for mid in member_ids]
            total_count = len(member_ids)
        else:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'errors': ['No members provided']
            }
        
        results = {
            'total': total_count,
            'successful': 0,
            'failed': 0,
            'errors': [],
            'sent_messages': [],
            'last_processed_member_id': None,
            'last_processed_index': 0
        }
        
        logger.info(f"🚀 Starting PARALLEL bulk campaign to {total_count} members with {max_workers} workers")
        
        # Store reference to self for personalization
        parent_client = self
        
        def send_single_message(member_data):
            """Send a single message - designed for parallel execution"""
            try:
                member_id = member_data.get('member_id') or member_data.get('prospect_id') or str(member_data.get('id', ''))
                member_name = member_data.get('name') or member_data.get('full_name', f'Member {member_id}')
                
                if not member_id:
                    return {
                        'success': False,
                        'member_id': member_id,
                        'member_name': member_name,
                        'error': 'No member ID found'
                    }
                
                # Personalize the message with member-specific data
                personalized_message = parent_client._personalize_message(message, member_data)
                
                # Determine actual channel to use (SMS with email fallback)
                actual_channel = message_type
                if message_type == 'sms' and member_data.get('fallback_to_email'):
                    actual_channel = 'email'
                
                # Create a new session for this thread to avoid conflicts
                thread_client = ClubOSMessagingClient(self.username, self.password)
                if not thread_client.authenticate():
                    return {
                        'success': False,
                        'member_id': member_id,
                        'member_name': member_name,
                        'error': 'Authentication failed'
                    }
                
                success = thread_client.send_message(
                    member_id=member_id,
                    message_text=personalized_message,
                    channel=actual_channel,
                    member_data=member_data
                )
                
                if success:
                    return {
                        'success': True,
                        'member_id': member_id,
                        'member_name': member_name,
                        'message_text': personalized_message,
                        'timestamp': datetime.now().isoformat(),
                        'channel': message_type
                    }
                else:
                    return {
                        'success': False,
                        'member_id': member_id,
                        'member_name': member_name,
                        'error': 'Send message failed'
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'member_id': member_data.get('member_id', 'Unknown'),
                    'member_name': member_data.get('full_name', 'Unknown'),
                    'error': str(e)
                }
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_member = {
                executor.submit(send_single_message, member_data): member_data 
                for member_data in members_to_process
            }
            
            # Process completed tasks
            for future in as_completed(future_to_member):
                member_data = future_to_member[future]
                try:
                    result = future.result()
                    
                    if result['success']:
                        results['successful'] += 1
                        results['sent_messages'].append(result)
                        logger.info(f"✅ Parallel message sent to {result['member_name']}")
                    else:
                        results['failed'] += 1
                        error_msg = f"Failed to send to {result['member_name']}: {result.get('error', 'Unknown error')}"
                        results['errors'].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                        
                except Exception as e:
                    results['failed'] += 1
                    member_name = member_data.get('full_name', f'Member {member_data.get("member_id", "Unknown")}')
                    error_msg = f"Exception processing {member_name}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
        
        logger.info(f"📊 PARALLEL Campaign completed: {results['successful']}/{results['total']} successful")
        return results

    def _personalize_message(self, message_template: str, member_data: Dict[str, Any]) -> str:
        """
        Personalize message template with member data.
        
        Supports variables:
        - {first_name} - Member's first name
        - {name} - Full name
        - {amount} - Amount past due (base amount without late fees)
        - {late_fees} - Calculated late fees (missed_payments * 19.50)
        - {total} - Total amount owed (amount + late_fees)
        - {email} - Member email
        - {phone} - Member phone
        """
        personalized = message_template
        
        # Get member name
        full_name = member_data.get('full_name') or member_data.get('name', '')
        first_name = full_name.split()[0] if full_name else 'Member'
        
        # Get financial data
        amount_past_due = float(member_data.get('amount_past_due', 0) or 0)
        missed_payments = int(member_data.get('missed_payments', 0) or 0)
        late_fees = float(member_data.get('late_fees', 0) or 0)
        
        # Calculate late fees if not provided but missed_payments is available
        if late_fees == 0 and missed_payments > 0:
            late_fees = missed_payments * 19.50
        
        # Calculate total with late fees
        total_amount = amount_past_due + late_fees
        
        # Replace variables
        personalized = personalized.replace('{first_name}', first_name)
        personalized = personalized.replace('{name}', full_name)
        personalized = personalized.replace('{email}', str(member_data.get('email', '')))
        personalized = personalized.replace('{phone}', str(member_data.get('mobile_phone', member_data.get('phone', ''))))
        
        # Financial variables - format with 2 decimal places
        personalized = personalized.replace('{amount}', f'{amount_past_due:.2f}')
        personalized = personalized.replace('{late_fees}', f'{late_fees:.2f}')
        personalized = personalized.replace('{total}', f'{total_amount:.2f}')
        
        logger.debug(f"📝 Personalized message for {full_name}: {personalized[:100]}...")
        
        return personalized

    def send_bulk_campaign(self, member_data_list: List[Dict[str, Any]] = None, member_ids: List[str] = None, message: str = "", message_type: str = "sms") -> Dict[str, Any]:
        """Send bulk campaign using the corrected messaging workflow"""
        # Handle both parameter styles
        if member_data_list:
            members_to_process = member_data_list
            total_count = len(member_data_list)
        elif member_ids:
            members_to_process = [{'member_id': mid} for mid in member_ids]
            total_count = len(member_ids)
        else:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'errors': ['No members provided']
            }
        
        results = {
            'total': total_count,
            'successful': 0,
            'failed': 0,
            'errors': [],
            'sent_messages': [],
            'last_processed_member_id': None,
            'last_processed_index': 0
        }
        
        logger.info(f"📢 Starting bulk campaign to {total_count} members")
        
        consecutive_failures = 0
        max_consecutive_failures = 5  # Increased tolerance for faster processing
        
        for i, member_data in enumerate(members_to_process):
            try:
                member_id = member_data.get('member_id') or member_data.get('prospect_id') or str(member_data.get('id', ''))
                member_name = member_data.get('name') or member_data.get('full_name', f'Member {member_id}')
                
                if not member_id:
                    results['failed'] += 1
                    results['errors'].append(f"No member ID found for {member_name}")
                    continue
                
                # Personalize the message with member-specific data
                personalized_message = self._personalize_message(message, member_data)
                
                # Determine actual channel to use (SMS with email fallback)
                actual_channel = message_type
                if message_type == 'sms' and member_data.get('fallback_to_email'):
                    actual_channel = 'email'
                    logger.info(f"📧 Using email fallback for {member_name} (no phone number)")
                
                logger.info(f"📨 Sending {actual_channel} message {i+1}/{total_count} to {member_name} (ID: {member_id})")
                
                success = self.send_message(
                    member_id=member_id,
                    message_text=personalized_message,
                    channel=actual_channel,
                    member_data=member_data
                )
                
                if success:
                    results['successful'] += 1
                    consecutive_failures = 0
                    
                    results['sent_messages'].append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'message_text': personalized_message,  # Store the personalized message
                        'timestamp': datetime.now().isoformat(),
                        'channel': message_type
                    })
                    
                    results['last_processed_member_id'] = member_id
                    results['last_processed_index'] = i
                    
                    logger.info(f"✅ Message {i+1}/{total_count} sent successfully to {member_name}")
                else:
                    results['failed'] += 1
                    consecutive_failures += 1
                    error_msg = f"Failed to send to {member_name} (ID: {member_id})"
                    results['errors'].append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    
                    # Re-authenticate on consecutive failures
                    if consecutive_failures >= max_consecutive_failures:
                        logger.warning(f"⚠️ {consecutive_failures} consecutive failures,, re-authenticating...")
                        if self.authenticate():
                            logger.info("✅ Re-authentication successful")
                            consecutive_failures = 0
                        else:
                            logger.error("❌ Re-authentication failed, stopping campaign")
                            break
                
                # Reduced delay for faster sending
                time.sleep(0.1)
                
            except Exception as e:
                results['failed'] += 1
                member_name = member_data.get('full_name', f'Member {member_data.get("member_id", "Unknown")}')
                error_msg = f"Exception sending to {member_name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"📊 Campaign completed: {results['successful']}/{results['total']} successful")
        return results

    def _check_cache(self, key: str, ttl: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Check if cached messages are still valid (within TTL)"""
        if key in self._message_cache:
            age = time.time() - self._cache_timestamps.get(key, 0)
            if age < ttl:
                logger.info(f"✅ Using cached messages (age: {age:.1f}s, TTL: {ttl}s)")
                return self._message_cache[key]
            else:
                logger.debug(f"⏰ Cache expired (age: {age:.1f}s > TTL: {ttl}s)")
        return None

    def _store_cache(self, key: str, data: List[Dict[str, Any]]):
        """Store messages in cache with current timestamp"""
        self._message_cache[key] = data
        self._cache_timestamps[key] = time.time()
        logger.debug(f"💾 Cached {len(data)} messages for key: {key}")

    def clear_message_cache(self, owner_id: str = None):
        """Clear message cache for specific owner or all owners"""
        if owner_id:
            cache_key = f"messages_{owner_id}"
            if cache_key in self._message_cache:
                del self._message_cache[cache_key]
                del self._cache_timestamps[cache_key]
                logger.info(f"🗑️ Cleared message cache for owner {owner_id}")
        else:
            self._message_cache.clear()
            self._cache_timestamps.clear()
            logger.info("🗑️ Cleared all message caches")

    def get_messages(self, owner_id: str = None) -> List[Dict[str, Any]]:
        """Get messages from ClubOS for specific owner - ClubOS returns all messages in one response"""
        # CRITICAL PERFORMANCE FIX: Use lock to prevent concurrent syncs and cache to avoid redundant fetches
        with self._lock:
            try:
                if not self.authenticated:
                    if not self.authenticate():
                        logger.error("❌ Authentication failed before getting messages")
                        return None  # Return None instead of [] to indicate auth failure

                # Check cache first - avoid redundant syncs within TTL window
                cache_key = f"messages_{owner_id}"
                cached = self._check_cache(cache_key, ttl=10)
                if cached is not None:
                    return cached

                logger.info(f"📨 Fetching ALL messages for owner {owner_id}...")

                # First get the dashboard view to ensure proper session state
                dashboard_url = f"{self.base_url}/action/Dashboard/view"
                try:
                    dashboard_response = self.session.get(dashboard_url, timeout=10, verify=False)
                    logger.info(f"📋 Dashboard view status: {dashboard_response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ Dashboard view failed: {e}")

                # Now post to the messages endpoint
                messages_url = f"{self.base_url}/action/Dashboard/messages"
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Accept": "text/html, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"{self.base_url}/action/Dashboard/view",
                    "Origin": self.base_url,
                    "User-Agent": self.session.headers.get('User-Agent', 'Mozilla/5.0')
                }

                # ClubOS doesn't seem to support pagination, so just get all messages
                post_data = {
                    "userId": owner_id
                }

                logger.info(f"🔄 POST to {messages_url} with userId: {owner_id}")

                # Add timeout to prevent hanging
                response = self.session.post(
                    messages_url,
                    data=post_data,
                    headers=headers,
                    timeout=30,  # Increased timeout for large response
                    allow_redirects=False,
                    verify=False
                )

                logger.info(f"📡 Response status: {response.status_code}")
                logger.info(f"📏 Response length: {len(response.text) if response.text else 0}")

                # CRITICAL: Check for "Session Expired" in response (authentication failed)
                if response.text and ('Session Expired' in response.text or 'session expired' in response.text.lower()):
                    logger.error(f"❌ Session expired - authentication failed")
                    logger.error(f"❌ ClubOS rejected credentials or session is invalid")
                    self.authenticated = False  # Mark as not authenticated
                    return None  # Return None to indicate auth failure

                if response.status_code == 200:
                    messages = self._parse_messages_from_html(response.text, owner_id)
                    logger.info(f"✅ Successfully parsed {len(messages)} messages from ClubOS")

                    # Store in cache for future requests
                    self._store_cache(cache_key, messages)

                    return messages
                else:
                    logger.error(f"❌ Failed to fetch messages: {response.status_code}")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    if response.text:
                        logger.error(f"Response preview: {response.text[:500]}...")
                    return None  # Return None for error cases

            except Exception as e:
                logger.error(f"❌ Error getting messages: {e}")
                return None  # Return None for exceptions
    
    def _parse_messages_from_html(self, html_content: str, owner_id: str) -> List[Dict[str, Any]]:
        """Parse messages from ClubOS HTML response"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            logger.info(f"🔍 Parsing HTML content for messages (length: {len(html_content)})")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            messages = []
            
            # Look for message elements in the HTML
            # ClubOS structure: <div class="message"> followed by <div class="message-options"> with timestamp
            message_elements = soup.find_all('div', class_='message')
            
            for element in message_elements:
                try:
                    content_text = element.get_text(strip=True)
                    
                    # Extract sender name from <h3><a> tag inside message div
                    from_user = 'Unknown'
                    h3_tag = element.find('h3')
                    if h3_tag:
                        a_tag = h3_tag.find('a')
                        if a_tag:
                            from_user = a_tag.get_text(strip=True)
                    
                    # CRITICAL: Extract timestamp from next sibling <div class="message-options"><span>
                    timestamp_value = None
                    next_sibling = element.find_next_sibling('div', class_='message-options')
                    if next_sibling:
                        span_tag = next_sibling.find('span')
                        if span_tag:
                            timestamp_text = span_tag.get_text(strip=True)
                            # timestamp_text will be like "9:30 AM" or "Sep 4" or "Oct 13"

                            # CRITICAL FIX: Parse timestamp and add year for proper sorting
                            # ALL timestamps MUST be valid ISO format for correct sorting
                            try:
                                from datetime import timedelta
                                current_year = datetime.now().year
                                current_date = datetime.now().date()

                                # Check if it's a time only (e.g., "9:30 AM") - assume today
                                # These are the FRESHEST messages!
                                if 'AM' in timestamp_text or 'PM' in timestamp_text or ':' in timestamp_text:
                                    # Parse time and use today's date
                                    time_obj = datetime.strptime(timestamp_text.strip(), '%I:%M %p')
                                    dt_obj = datetime.now().replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)
                                    timestamp_value = dt_obj.isoformat()

                                # Check if it's a date (e.g., "Oct 13" or "Sep 4" or "Jan 24")
                                else:
                                    # Try parsing "Oct 13" format
                                    try:
                                        dt_obj = datetime.strptime(f"{timestamp_text} {current_year}", '%b %d %Y')

                                        # FIXED YEAR LOGIC:
                                        # 1. If the date is in the future, it's definitely from last year
                                        # 2. If the date is more than 6 months in the past, it might be from last year
                                        #    (ClubOS typically shows ~90 days of messages, so 6+ months old is likely last year)
                                        if dt_obj.date() > current_date:
                                            # Future date = definitely last year
                                            dt_obj = dt_obj.replace(year=current_year - 1)
                                        elif dt_obj.date() < (current_date - timedelta(days=180)):
                                            # More than 6 months ago = probably last year
                                            # This handles cases like "Jan 24" appearing in Dec 2025
                                            # which should be Jan 24, 2025 (11 months ago) not Jan 24, 2024
                                            pass  # Keep current year - it's a valid recent-ish date

                                        timestamp_value = dt_obj.isoformat()
                                    except ValueError:
                                        # CRITICAL: Parsing failed - use a past date in ISO format
                                        # that sorts BEFORE today's messages but is still valid
                                        # Use 1 year ago to sort these at the bottom
                                        fallback_date = datetime.now() - timedelta(days=365)
                                        timestamp_value = fallback_date.isoformat()
                                        logger.debug(f"⚠️ Using fallback timestamp for '{timestamp_text}'")

                            except Exception as parse_err:
                                # CRITICAL: Always use valid ISO format, never raw text
                                logger.debug(f"⚠️ Could not parse timestamp '{timestamp_text}': {parse_err}")
                                fallback_date = datetime.now() - timedelta(days=365)
                                timestamp_value = fallback_date.isoformat()

                    # If no timestamp found, use current time
                    if not timestamp_value:
                        timestamp_value = datetime.now().isoformat()

                    # CRITICAL FIX: Generate stable content-based message ID to prevent duplicates
                    # Include DATE (not time) so same message on different days gets unique ID
                    # but same message synced multiple times on same day doesn't create duplicates
                    
                    # Extract date portion from timestamp for stable ID generation
                    try:
                        # timestamp_value is ISO format like "2025-12-08T13:05:00"
                        date_part = timestamp_value[:10]  # Gets "2025-12-08"
                    except:
                        date_part = datetime.now().strftime('%Y-%m-%d')
                    
                    # Normalize content and sender for consistent hashing
                    normalized_content = content_text.strip().lower()[:200]  # First 200 chars, lowercased
                    normalized_sender = from_user.strip().lower()
                    
                    # Create stable ID string from content, sender, AND date
                    # This ensures: same person sending same message on different days = different IDs
                    id_string = f"{normalized_content}|{normalized_sender}|{date_part}"
                    message_hash = hashlib.md5(id_string.encode('utf-8')).hexdigest()[:16]
                    message_id = f"msg_{message_hash}"

                    # Extract message data from HTML element
                    message_data = {
                        'id': message_id,
                        'owner_id': owner_id,
                        'content': content_text,
                        'timestamp': timestamp_value,
                        'from_user': from_user,
                        'status': 'received',
                        'channel': 'clubos'
                    }
                    
                    # Skip empty messages
                    if message_data['content'] and len(message_data['content']) > 3:
                        messages.append(message_data)
                        
                except Exception as parse_error:
                    logger.warning(f"⚠️ Error parsing message element: {parse_error}")
                    continue
            
            # CRITICAL: Deduplicate messages by ID - ClubOS HTML may contain duplicates
            # Keep only the FIRST occurrence of each message ID (usually the most recent by position)
            seen_ids = set()
            unique_messages = []
            for msg in messages:
                if msg['id'] not in seen_ids:
                    seen_ids.add(msg['id'])
                    unique_messages.append(msg)
            
            if len(unique_messages) < len(messages):
                logger.info(f"🧹 Deduplicated: {len(messages)} → {len(unique_messages)} messages ({len(messages) - len(unique_messages)} duplicates removed)")
            
            logger.info(f"✅ Parsed {len(unique_messages)} unique messages from HTML")
            return unique_messages
            
        except Exception as e:
            logger.error(f"❌ Error parsing messages from HTML: {e}")
            return []
    

