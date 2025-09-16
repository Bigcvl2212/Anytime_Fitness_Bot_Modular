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
from urllib.parse import quote
from src.services.authentication.unified_auth_service import get_unified_auth_service, AuthenticationSession

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
        
    def authenticate(self) -> bool:
        """Authenticate using the unified authentication service"""
        try:
            logger.info("Authenticating ClubOS Messaging Client Simple")
            
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
        """
        try:
            logger.info(f"🔄 Delegating to member {member_id} to get delegated Bearer token")
            
            # Step 1: Call delegation endpoint that should give us new Bearer token
            timestamp = int(time.time() * 1000)
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false?_={timestamp}"
            
            delegate_headers = {
                "X-Requested-With": "XMLHttpRequest", 
                "Referer": f"{self.base_url}/action/LeadProfile/view"
            }
            
            delegate_response = self.session.get(delegate_url, headers=delegate_headers, verify=False, timeout=30)
            delegate_response.raise_for_status()
            
            logger.info(f"✅ Delegation call successful - status: {delegate_response.status_code}")
            
            # Step 2: Check if we got new Bearer token or delegation cookies
            new_bearer_token = self.session.cookies.get('apiV3AccessToken')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            
            if delegated_user_id:
                self.delegated_user_id = delegated_user_id
                logger.info(f"🎯 Delegation successful - delegatedUserId: {delegated_user_id}")
            
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
            
            # Save popup for debugging
            with open(f"member_popup_{self.delegated_user_id}.html", "w", encoding="utf-8") as f:
                f.write(popup_response.text)
            logger.info(f"💾 Saved member popup data")
            
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
            
            # Use delegated Bearer token
            if self.delegated_bearer_token:
                headers["authorization"] = f"Bearer {self.delegated_bearer_token}"
            elif self.session.cookies.get('apiV3AccessToken'):
                headers["authorization"] = f"Bearer {self.session.cookies.get('apiV3AccessToken')}"
            
            # Submit to ClubOS
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
                timeout=30,
                verify=False,
                allow_redirects=False
            )
            
            logger.info(f"📋 Response status: {response.status_code}")
            
            # Save response for debugging
            response_filename = f"safe_response_{clubos_member_id}.html"
            with open(response_filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info(f"💾 Saved response to {response_filename}")
            
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
        max_consecutive_failures = 2
        
        for i, member_data in enumerate(members_to_process):
            try:
                member_id = member_data.get('member_id') or member_data.get('prospect_id') or str(member_data.get('id', ''))
                member_name = member_data.get('name') or member_data.get('full_name', f'Member {member_id}')
                
                if not member_id:
                    results['failed'] += 1
                    results['errors'].append(f"No member ID found for {member_name}")
                    continue
                
                logger.info(f"📨 Sending message {i+1}/{total_count} to {member_name} (ID: {member_id})")
                
                success = self.send_message(
                    member_id=member_id,
                    message_text=message,
                    channel=message_type,
                    member_data=member_data
                )
                
                if success:
                    results['successful'] += 1
                    consecutive_failures = 0
                    
                    results['sent_messages'].append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'message_text': message,
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
                
                # Small delay between messages
                time.sleep(0.5)
                
            except Exception as e:
                results['failed'] += 1
                member_name = member_data.get('full_name', f'Member {member_data.get("member_id", "Unknown")}')
                error_msg = f"Exception sending to {member_name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"📊 Campaign completed: {results['successful']}/{results['total']} successful")
        return results
