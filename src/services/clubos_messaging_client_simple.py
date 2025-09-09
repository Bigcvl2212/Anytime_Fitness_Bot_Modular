#!/usr/bin/env python3
"""
ClubOS Messaging Client - Based on documented working endpoints
Uses actual ClubOS REST API endpoints found in existing working implementations
"""

import requests
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from bs4 import BeautifulSoup
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ClubOSMessagingClient:
    """
    ClubOS Messaging Client using documented working endpoints
    Based on existing working implementation patterns
    """
    
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        
        if not username or not password:
            try:
                # Import with proper path handling
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                
                from src.services.authentication.secure_secrets_manager import SecureSecretsManager
                secrets_manager = SecureSecretsManager()
                
                clubos_username = secrets_manager.get_secret('clubos-username')
                clubos_password = secrets_manager.get_secret('clubos-password')
                
                if clubos_username and clubos_password:
                    self.username = self.username or clubos_username
                    self.password = self.password or clubos_password
                    logger.info("🔐 ClubOS credentials loaded from SecureSecretsManager")
                else:
                    logger.error("❌ ClubOS credentials not found in SecureSecretsManager")
                    raise ValueError("ClubOS credentials not available")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load ClubOS credentials: {e}")
                raise
                
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        
        # Core session data
        self.staff_id = None
        self.club_id = None
        self.logged_in_user_id = None
        
        # Set standard headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
    def authenticate(self) -> bool:
        """Authenticate using ClubOS login - based on working implementation"""
        try:
            logger.info(f"🔐 Authenticating {self.username} using documented login flow")
            
            # Step 1: Get login page
            login_url = f"{self.base_url}/action/Login/view?__fsk=1221801756"
            login_response = self.session.get(login_url, verify=False)
            login_response.raise_for_status()
            
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Extract required form fields
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            
            # Step 2: Submit login form
            login_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': source_page.get('value') if source_page else '',
                '__fp': fp_token.get('value') if fp_token else ''
            }
            
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=login_headers,
                allow_redirects=True,
                verify=False
            )
            
            # Step 3: Validate authentication
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            
            if not session_id or not logged_in_user_id:
                logger.error("❌ Authentication failed - missing session cookies")
                return False
            
            # Store authentication data
            self.staff_id = logged_in_user_id
            self.logged_in_user_id = logged_in_user_id
            self.authenticated = True
            
            # Extract club ID from dashboard
            try:
                dashboard_response = self.session.get(f"{self.base_url}/action/Dashboard/view", verify=False)
                if dashboard_response.status_code == 200:
                    club_match = re.search(r'clubId["\']?\s*[:=]\s*["\']?(\d+)', dashboard_response.text)
                    if club_match:
                        self.club_id = club_match.group(1)
                        logger.info(f"✅ Extracted club ID: {self.club_id}")
            except:
                pass
            
            logger.info(f"✅ Authentication successful - User ID: {self.logged_in_user_id}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def _get_fresh_csrf_token(self) -> Optional[str]:
        """Get fresh CSRF token from dashboard"""
        try:
            response = self.session.get(f"{self.base_url}/action/Dashboard", verify=False, timeout=30)
            if response.status_code != 200:
                logger.error(f"❌ Failed to get dashboard for CSRF token: {response.status_code}")
                return None
            
            return self._extract_csrf_token(response.text)
        except Exception as e:
            logger.error(f"❌ Error getting CSRF token: {e}")
            return None
    
    def _extract_csrf_token(self, html: str) -> Optional[str]:
        """Extract CSRF token from ClubOS HTML"""
        soup = BeautifulSoup(html, "html.parser")
        
        # Try different CSRF token patterns
        csrf_input = soup.find("input", {"name": "__RequestVerificationToken"})
        if csrf_input and csrf_input.get("value"):
            return csrf_input["value"]
        
        csrf_input = soup.find("input", {"name": "csrfToken"})
        if csrf_input and csrf_input.get("value"):
            return csrf_input["value"]
        
        # Try meta tag
        meta = soup.find("meta", {"name": "csrf-token"})
        if meta and meta.get("content"):
            return meta["content"]
        
        logger.warning("⚠️ No CSRF token found")
        return None
    
    def _extract_form_token(self, html: str, token_name: str) -> Optional[str]:
        """Extract specific form token by name"""
        soup = BeautifulSoup(html, "html.parser")
        token_input = soup.find("input", {"name": token_name})
        if token_input and token_input.get("value"):
            return token_input["value"]
        return None
    
    def _extract_member_data_from_form(self, soup: BeautifulSoup, member_id: str) -> Dict[str, str]:
        """Extract member data from FollowUp form"""
        member_data = {'member_id': member_id}
        
        # Map ClubOS form fields to our data structure
        form_fields = {
            'firstName': 'followUpUser.firstName',
            'lastName': 'followUpUser.lastName',
            'email': 'followUpUser.email',
            'mobilePhone': 'followUpUser.mobilePhone'
        }
        
        for data_key, field_name in form_fields.items():
            field_input = soup.find('input', {'name': field_name})
            if field_input and field_input.get('value'):
                value = field_input.get('value', '').strip()
                if value:
                    member_data[data_key] = value
        
        return member_data
    
    def send_message(self, member_id: str, message_text: str, channel: str = "sms", member_data: dict = None) -> bool:
        """
        Send SMS message using the EXACT working pattern from HAR analysis
        Two-step process: 1) Get form with member context, 2) Submit complete form data
        """
        try:
            if not self.authenticated and not self.authenticate():
                logger.error("❌ Not authenticated")
                return False
                
            logger.info(f"📱 Sending {channel} message to member {member_id}: '{message_text[:50]}...'")
            
            # Step 1: Get the FollowUp form for this specific member
            followup_url = f"{self.base_url}/action/FollowUp"
            
            # Get fresh CSRF token first
            csrf_token = self._get_fresh_csrf_token()
            if not csrf_token:
                logger.error("❌ Could not get CSRF token")
                return False
            
            # Get additional form tokens from dashboard
            dashboard_response = self.session.get(f"{self.base_url}/action/Dashboard", verify=False)
            fp_token = self._extract_form_token(dashboard_response.text, '__fp')
            source_page = self._extract_form_token(dashboard_response.text, '_sourcePage')
            
            # Open FollowUp popup with member context
            form_data = {
                'followUpUserId': member_id,
                'followUpType': '3' if channel == "sms" else '1',  # 3=SMS, 1=Email
                '__RequestVerificationToken': csrf_token,
                '__fp': fp_token or '',
                '_sourcePage': source_page or ''
            }
            
            form_response = self.session.post(
                followup_url,
                data=form_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f"{self.base_url}/action/Dashboard"
                },
                verify=False
            )
            
            if form_response.status_code != 200:
                logger.error(f"❌ Failed to get messaging form: {form_response.status_code}")
                return False
            
            logger.info("✅ FollowUp form opened successfully")
            
            # Step 2: Extract member data and fresh tokens from form response
            form_soup = BeautifulSoup(form_response.text, 'html.parser')
            fresh_csrf = self._extract_csrf_token(form_response.text) or csrf_token
            fresh_fp = self._extract_form_token(form_response.text, '__fp') or fp_token
            fresh_source = self._extract_form_token(form_response.text, '_sourcePage') or source_page
            
            # Extract member data from pre-filled form
            form_member_data = self._extract_member_data_from_form(form_soup, member_id)
            
            # Step 3: Submit message with COMPLETE ClubOS form structure
            save_url = f"{self.base_url}/action/FollowUp/save"
            
            # Build form data using EXACT working pattern from HAR analysis
            message_data = {
                # Core followup fields (from working implementation)
                'followUpStatus': '1',
                'followUpType': '3' if channel == "sms" else '1',  # 3=SMS, 1=Email
                'followUpSequence': '',
                'memberSalesFollowUpStatus': '6',
                'followUpLog.id': '',
                'followUpLog.tfoUserId': member_id,
                'followUpLog.outcome': '2' if channel == "sms" else '1',  # 2=SMS, 1=Email
                
                # Message content
                'emailSubject': 'Message from Anytime Fitness',
                'emailMessage': f'<p>{message_text}</p>',
                'textMessage': message_text,
                
                # Event fields (required by ClubOS)
                'event.id': '',
                'event.startTime': '',
                'event.createdFor.tfoUserId': self.staff_id or '',
                'event.eventType': 'ORIENTATION',
                'startTimeSlotId': '',
                'duration': '2',
                'event.remindAttendeesMins': '120',
                
                # Follow-up metadata
                'followUpLog.reason': '',
                'followUpOutcomeNotes': f'Message sent {datetime.now().strftime("%m/%d/%y %H:%M")}',
                'followUpLog.followUpWithOrig': '',
                'followUpLog.followUpWith': '',
                'followUpLog.followUpDate': '',
                
                # User information (CRITICAL: proper sender/recipient roles)
                'followUpUser.tfoUserId': member_id,  # TARGET (recipient)
                'followUpUser.role.id': '7',  # Member role
                'followUpUser.clubId': self.club_id or '291',
                'followUpUser.clubLocationId': '3586',
                'followUpLog.followUpAction': '3' if channel == "sms" else '1',  # SMS/Email action
                
                # Staff assignments (sender info)
                'memberStudioSalesDefaultAccount': self.staff_id or '',
                'memberStudioSupportDefaultAccount': self.staff_id or '',
                'ptSalesDefaultAccount': self.staff_id or '',
                'ptSupportDefaultAccount': self.staff_id or '',
                
                # Member contact details (from form)
                'followUpUser.firstName': form_member_data.get('firstName', ''),
                'followUpUser.lastName': form_member_data.get('lastName', ''),
                'followUpUser.email': form_member_data.get('email', ''),
                'followUpUser.mobilePhone': form_member_data.get('mobilePhone', ''),
                'followUpUser.homePhone': '',
                'followUpUser.workPhone': '',
                
                # Security tokens (FRESH from form response)
                '__RequestVerificationToken': fresh_csrf,
                '__fp': fresh_fp or '',
                '_sourcePage': fresh_source or ''
            }
            
            # Submit with proper headers
            response = self.session.post(
                save_url,
                data=message_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f"{self.base_url}/action/FollowUp"
                },
                verify=False
            )
            
            logger.info(f"📤 Message submission response: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text.lower()
                logger.info(f"📋 Response content: {response.text[:300]}")
                
                # Check for success indicators from working implementations
                success_indicators = [
                    'has been texted',
                    'has been emailed', 
                    'message sent',
                    'followup saved',
                    'follow-up saved'
                ]
                
                if any(indicator in response_text for indicator in success_indicators):
                    logger.info(f"✅ Message sent successfully to member {member_id}")
                    return True
                elif 'something isn\'t right' in response_text:
                    logger.error(f"❌ ClubOS error: Something isn't right - {response.text}")
                    return False
                else:
                    logger.warning(f"⚠️ Unclear response: {response.text}")
                    # Log the actual response for debugging
                    logger.info(f"Full response: {response.text}")
                    return False
            else:
                logger.error(f"❌ Failed to send message: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False
    
    def send_bulk_campaign(self, member_data_list: List[Dict[str, Any]] = None, member_ids: List[str] = None, message: str = "", message_type: str = "sms") -> Dict[str, Any]:
        """Send bulk campaign using documented endpoints"""
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
                member_name = member_data.get('full_name', f'Member {member_id}')
                
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
                        logger.warning(f"⚠️ {consecutive_failures} consecutive failures, re-authenticating...")
                        if self.authenticate():
                            logger.info("✅ Re-authentication successful")
                            consecutive_failures = 0
                        else:
                            logger.error("❌ Re-authentication failed, stopping campaign")
                            break
                
                # Small delay between messages
                import time
                time.sleep(0.5)
                
            except Exception as e:
                results['failed'] += 1
                member_name = member_data.get('full_name', f'Member {member_data.get("member_id", "Unknown")}')
                error_msg = f"Exception sending to {member_name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"📊 Campaign completed: {results['successful']}/{results['total']} successful")
        return results
