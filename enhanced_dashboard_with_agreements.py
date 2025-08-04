#!/usr/bin/env python3

import os
import sqlite3
import pandas as pd
import re
import random
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
import json
import sys
import requests
import time
from bs4 import BeautifulSoup

# Add the parent directory to sys.path to import the working ClubOS API
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clubos_real_calendar_api import ClubOSRealCalendarAPI
from ical_calendar_parser import iCalClubOSParser
from gym_bot_clean import ClubOSEventDeletion

# Import enhanced ClubOS client for training package data (deprecated - using working API now)
try:
    from services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
    ENHANCED_CLIENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced ClubOS client not available: {e}")
    ENHANCED_CLIENT_AVAILABLE = False

# ClubOS Training Package Integration
class ClubOSTrainingPackageAPI:
    """
    Integrated ClubOS Training Package API for dashboard use
    Uses the working authentication and token extraction from test_leisa_training_packages_clean.py
    """
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        self.session_data = {}
        self.access_token = None
        
        # Set headers to mimic working browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
    def authenticate(self):
        """Authenticate using the working HAR sequence"""
        try:
            print("🔐 Authenticating with ClubOS...")
            
            # Step 1: GET login page
            login_get_url = f"{self.base_url}/action/Login/view"
            get_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'DNT': '1',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            login_response = self.session.get(login_get_url, headers=get_headers, timeout=30)
            
            if not login_response.ok:
                print(f"   ❌ Failed to load login page: {login_response.status_code}")
                return False
            
            # Extract form fields dynamically
            soup = BeautifulSoup(login_response.text, 'html.parser')
            login_form = soup.find('form')
            if not login_form:
                print("   ❌ No login form found!")
                return False
            
            # Extract ALL hidden fields
            hidden_inputs = login_form.find_all('input', type='hidden')
            form_data = {}
            
            for hidden_input in hidden_inputs:
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    form_data[name] = value
            
            # Check for required tokens
            if '_sourcePage' not in form_data or '__fp' not in form_data:
                print("   ❌ Missing required CSRF tokens!")
                return False
            
            # Step 2: POST login with extracted CSRF tokens
            login_data = {
                'login': 'Submit',
                'username': 'j.mayo', 
                'password': 'j@SD4fjhANK5WNA',
                '_sourcePage': form_data['_sourcePage'],
                '__fp': form_data['__fp']
            }
            
            post_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Content-Type': 'application/x-www-form-urlencoded',
                'DNT': '1',
                'Cache-Control': 'max-age=0',
                'Origin': 'https://anytime.club-os.com',
                'Referer': login_get_url,
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=post_headers,
                allow_redirects=True,
                timeout=30
            )
            
            # Check for successful login
            if auth_response.status_code == 200 and "action/Login" in auth_response.url:
                print("   🚨 LOGIN FAILED - Still on login page")
                return False
            
            # Extract cookies
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            api_v3_access_token = self.session.cookies.get('apiV3AccessToken')
            
            if not api_v3_access_token or not logged_in_user_id:
                print("   ❌ Authentication failed - missing required tokens")
                return False
            
            # Store session data
            self.session_data = {
                'loggedInUserId': logged_in_user_id,
                'delegatedUserId': delegated_user_id,
                'JSESSIONID': session_id,
                'apiV3AccessToken': api_v3_access_token
            }
            
            self.access_token = api_v3_access_token
            self.authenticated = True
            
            print(f"   ✅ Authentication successful!")
            return True
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def get_member_payment_status(self, member_id):
        """Get payment status for a specific member"""
        if not self.authenticated:
            if not self.authenticate():
                return "Unknown"
        
        try:
            # Step 1: Set delegation to target member
            delegation_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false"
            delegate_params = {'_': int(datetime.now().timestamp() * 1000)}
            
            delegate_response = self.session.get(delegate_url, headers=delegation_headers, params=delegate_params)
            
            if delegate_response.status_code != 200:
                return "Unknown"
                
            # Step 2: Navigate to PackageAgreementUpdated/spa/ to get the delegated token
            package_agreement_url = f"{self.base_url}/action/PackageAgreementUpdated/spa/"
            package_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            
            package_response = self.session.get(package_agreement_url, headers=package_headers)
            
            if package_response.status_code != 200:
                return "Unknown"
            
            # Extract the delegated ACCESS_TOKEN from the page's JavaScript
            page_html = package_response.text
            token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', page_html)
            
            if not token_match:
                return "Unknown"
                
            delegated_token = token_match.group(1)
            
            # Step 3: Call billing_status API with the delegated token
            timestamp = int(time.time() * 1000)
            
            # First, discover active agreements for this member
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Authorization': f'Bearer {delegated_token}',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/'
            }
            
            # Try to find active agreements
            discovery_endpoints = [
                f"/api/agreements/package_agreements/list?memberId={member_id}",
                f"/api/agreements/package_agreements/active?memberId={member_id}",
                f"/api/members/{member_id}/active_agreements",
                f"/api/agreements/package_agreements?memberId={member_id}",
            ]
            
            for endpoint in discovery_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    params = {'_': timestamp}
                    
                    response = self.session.get(url, headers=api_headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and data:
                            # Filter for active agreements (status 2)
                            active_agreements = [agreement for agreement in data if agreement.get('id') and agreement.get('agreementStatus') == 2]
                            
                            if active_agreements:
                                # Get billing status for the first active agreement
                                agreement_id = active_agreements[0].get('id')
                                billing_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
                                billing_params = {'_': timestamp + 1}
                                
                                billing_response = self.session.get(billing_url, headers=api_headers, params=billing_params, timeout=10)
                                
                                if billing_response.status_code == 200:
                                    billing_data = billing_response.json()
                                    
                                    # Check if there are past due items
                                    past_due_items = billing_data.get('past', [])
                                    
                                    if past_due_items:
                                        return "Past Due"
                                    else:
                                        return "Current"
                                        
                except Exception as e:
                    continue
            
            return "Unknown"
            
        except Exception as e:
            print(f"Error getting payment status for member {member_id}: {e}")
            return "Unknown"

# Global instance for dashboard use
clubos_training_api = ClubOSTrainingPackageAPI()

app = Flask(__name__)
app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'

# Create templates directory if it doesn't exist
templates_dir = 'templates'
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Add regex filters for Jinja2 templates
@app.template_filter('regex_replace')
def regex_replace(s, find, replace):
    """Replace using regex in Jinja2 templates"""
    return re.sub(find, replace, str(s))

@app.template_filter('regex_findall')
def regex_findall(s, pattern):
    """Find all regex matches in Jinja2 templates"""
    return re.findall(pattern, str(s))

# Add moment function to fix the cursed template
class MomentJS:
    def format(self, format_string):
        return datetime.now().strftime('%B %d, %Y at %I:%M:%S %p')

def moment():
    return MomentJS()

@app.template_global()
def moment_global():
    return moment()

# Make moment available in templates
@app.context_processor
def inject_moment():
    return dict(moment=moment)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubOSIntegration:
    """Integration class to connect dashboard with working ClubOS API"""
    
    def __init__(self):
        self.api = ClubOSRealCalendarAPI("j.mayo", "j@SD4fjhANK5WNA")
        self.event_manager = ClubOSEventDeletion()
        self.authenticated = False
        
    def authenticate(self):
        """Authenticate with ClubOS"""
        try:
            self.authenticated = self.api.authenticate()
            if self.authenticated:
                # Also authenticate the event manager
                self.event_manager.authenticated = True
                logger.info("✅ ClubOS authentication successful")
            return self.authenticated
        except Exception as e:
            logger.error(f"❌ ClubOS authentication failed: {e}")
            return False
    
    def get_live_events(self):
        """Get live calendar events with REAL dates, times, and participant names using iCal"""
        try:
            print("🌟 USING NEW iCAL METHOD FOR REAL EVENT DATA...")
            
            # Use the iCal calendar sync URL found in ClubOS
            calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
            ical_parser = iCalClubOSParser(calendar_sync_url)
            
            # Get real events from iCal feed
            real_events = ical_parser.get_real_events()
            
            formatted_events = []
            for event in real_events:
                # Format the real event data for display
                attendee_names = [attendee['name'] for attendee in event.attendees if attendee['name']]
                attendee_emails = [attendee['email'] for attendee in event.attendees if attendee['email']]
                
                # Get training package status for each participant
                participant_funding_status = []
                for i, name in enumerate(attendee_names):
                    email = attendee_emails[i] if i < len(attendee_emails) else None
                    try:
                        # Use the training package cache to lookup funding status
                        funding_data = training_package_cache.lookup_participant_funding(name, email)
                        if funding_data:  # Only add if we have REAL data
                            participant_funding_status.append({
                                'name': name,
                                'email': email,
                                'status': funding_data.get('status', 'unknown'),
                                'status_text': funding_data.get('status_text', 'Unknown'),
                                'status_class': funding_data.get('status_class', 'secondary'),
                                'status_icon': funding_data.get('status_icon', 'fas fa-question-circle')
                            })
                        else:
                            # No real data available - don't show any status
                            participant_funding_status.append({
                                'name': name,
                                'email': email,
                                'status': None,
                                'status_text': None,
                                'status_class': None,
                                'status_icon': None
                            })
                    except Exception as e:
                        logger.warning(f"❌ Could not get funding status for {name}: {e}")
                        # No fallbacks - just don't show status
                        participant_funding_status.append({
                            'name': name,
                            'email': email,
                            'status': None,
                            'status_text': None,
                            'status_class': None,
                            'status_icon': None
                        })
                
                formatted_event = {
                    'id': event.uid,
                    'title': event.summary or 'Training Session',
                    'start_time': event.start_time.strftime('%B %d, %Y at %I:%M %p'),
                    'end_time': event.end_time.strftime('%I:%M %p'),
                    'participants': ', '.join(attendee_names) if attendee_names else 'No participants listed',
                    'participant_emails': ', '.join(attendee_emails) if attendee_emails else '',
                    'participant_funding': participant_funding_status,  # Add funding status data
                    'status': 'Scheduled',
                    'service_type': 'Personal Training',
                    'trainer': 'Jeremy Mayo',
                    'raw_start': event.start_time,
                    'raw_end': event.end_time
                }
                formatted_events.append(formatted_event)
            
            logger.info(f"✅ Successfully extracted {len(formatted_events)} REAL events with actual times and names!")
            
            # Sort events by start time
            formatted_events.sort(key=lambda x: x['raw_start'])
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"❌ Error getting live events via iCal: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_live_members(self):
        """Get live member data from ClubOS (placeholder for future implementation)"""
        # TODO: Implement live member data retrieval
        # For now, this would use the comprehensive data pull
        logger.info("📊 Live member data retrieval not yet implemented")
        return []
    
    def delete_event(self, event_id):
        """Delete an event using the working deletion method"""
        if not self.authenticated:
            if not self.authenticate():
                return False
        
        return self.event_manager.delete_event_properly(event_id)
    
    def send_message(self, contact_info, message_type, subject, message):
        """Send message via ClubOS (placeholder for future implementation)"""
        # TODO: Implement messaging via ClubOS
        logger.info(f"📧 Message sending not yet implemented: {message_type} to {contact_info}")
        return False


# =============================================================================
# TRAINING PACKAGE LOOKUP FUNCTIONALITY
# =============================================================================

class TrainingPackageCache:
    """Cache for training package data using the working ClubOS API"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.member_id_cache = {}  # Cache member name to ID mappings
        
    def lookup_participant_funding(self, participant_name: str, participant_email: str = None) -> dict:
        """
        Look up REAL funding status for a training session participant using ClubOS API.
        
        Args:
            participant_name: Name of the participant
            participant_email: Email of the participant (optional)
            
        Returns:
            Dict with funding status information from ClubOS training packages
        """
        cache_key = f"{participant_name}:{participant_email or 'no_email'}"
        current_time = datetime.now().timestamp()
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if current_time - cached_data['timestamp'] < self.cache_timeout:
                logger.info(f"📋 Using cached funding data for {participant_name}")
                return cached_data['data']
        
        try:
            logger.info(f"🔍 Looking up REAL funding for: {participant_name}")
            
            # Step 1: Get member ID from database (faster than API lookup)
            member_id = self._get_member_id_from_database(participant_name, participant_email)
            
            if not member_id:
                logger.warning(f"⚠️ Could not find member ID for {participant_name}")
                funding_data = {
                    'status': 'not_found',
                    'status_class': 'warning',
                    'status_text': 'Member Not Found',
                    'status_icon': 'fas fa-user-slash'
                }
                else:
                    # Step 2: Get payment status using our working ClubOS API
                    logger.info(f"📦 Getting payment status for member ID: {member_id}")
                    payment_status = clubos_training_api.get_member_payment_status(member_id)
                    
                    # Convert payment status to funding data format - REAL DATA ONLY
                    if payment_status == "Current":
                        funding_data = {
                            'status': 'current',
                            'status_class': 'success',
                            'status_text': 'Current',
                            'status_icon': 'fas fa-check-circle'
                        }
                    elif payment_status == "Past Due":
                        funding_data = {
                            'status': 'past_due',
                            'status_class': 'danger',
                            'status_text': 'Past Due',
                            'status_icon': 'fas fa-exclamation-triangle'
                        }
                    else:
                        # If we can't get real data, return None - NO FALLBACKS
                        logger.warning(f"⚠️ Could not get real payment status for {participant_name} - returning None")
                        return None
            
            # Cache the result only if we have real data
            if funding_data:
                self.cache[cache_key] = {
                    'data': funding_data,
                    'timestamp': current_time
                }
                
                logger.info(f"✅ REAL funding lookup complete for {participant_name}: {funding_data['status_text']}")
                return funding_data
            else:
                return None
            
        except Exception as e:
            logger.error(f"❌ Error looking up funding for {participant_name}: {e}")
            # NO FALLBACKS - return None if we can't get real data
            return None    def _get_member_id_from_database(self, participant_name: str, participant_email: str = None) -> str:
        """Get member ID from local database"""
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'anytime_fitness.db')
            if not os.path.exists(db_path):
                return None
                
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Split name into first and last parts
            name_parts = participant_name.strip().split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = ' '.join(name_parts[1:])
                
                # First try exact match
                cursor.execute("""
                    SELECT id FROM members 
                    WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)
                    LIMIT 1
                """, (first_name, last_name))
                
                result = cursor.fetchone()
                if result:
                    conn.close()
                    return str(result[0])
                
                # Try with email if provided
                if participant_email:
                    cursor.execute("""
                        SELECT id FROM members 
                        WHERE LOWER(email) = LOWER(?)
                        LIMIT 1
                    """, (participant_email,))
                    
                    result = cursor.fetchone()
                    if result:
                        conn.close()
                        return str(result[0])
                
                # Try partial name match
                cursor.execute("""
                    SELECT id FROM members 
                    WHERE LOWER(full_name) LIKE LOWER(?)
                    LIMIT 1
                """, (f"%{participant_name}%",))
                
                result = cursor.fetchone()
                if result:
                    conn.close()
                    return str(result[0])
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error looking up member ID for {participant_name}: {e}")
            return None

# Initialize training package cache
training_package_cache = TrainingPackageCache()
    
    def _search_member_by_name(self, client, participant_name: str) -> str:
        """
        Search for a member by name to get their member_id.
        
        Args:
            client: EnhancedClubOSAPIClient instance
            participant_name: Name to search for
            
        Returns:
            Member ID string if found, None otherwise
        """
        try:
            # Try the user search endpoint
            search_url = f"{client.base_url}/action/UserSearch/"
            
            # Search by name
            search_data = {
                'query': participant_name,
                'type': 'member'
            }
            
            response = client.session.post(
                search_url,
                data=search_data,
                headers=client.auth.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse response to extract member ID
                # This will need to be adjusted based on actual API response format
                search_results = response.json() if response.headers.get('content-type', '').startswith('application/json') else []
                
                if search_results and len(search_results) > 0:
                    # Look for exact name match first, then partial
                    for result in search_results:
                        if 'id' in result and 'name' in result:
                            if result['name'].lower() == participant_name.lower():
                                logger.info(f"✅ Found exact match: {result['name']} (ID: {result['id']})")
                                return str(result['id'])
                    
                    # If no exact match, take first result
                    first_result = search_results[0]
                    if 'id' in first_result:
                        logger.info(f"⚠️ Using partial match: {first_result.get('name', 'Unknown')} (ID: {first_result['id']})")
                        return str(first_result['id'])
            
            logger.warning(f"⚠️ No search results for {participant_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error searching for member {participant_name}: {e}")
            return None
    
    def _process_training_packages(self, packages: list, participant_name: str) -> dict:
        """
        Process training packages to determine funding status.
        
        Args:
            packages: List of training packages from ClubOS API
            participant_name: Name of the participant
            
        Returns:
            Dict with processed funding status
        """
        try:
            active_packages = []
            total_sessions = 0
            
            # Filter for ACTIVE packages only
            for package in packages:
                if isinstance(package, dict):
                    status = package.get('status', '').lower()
                    if status == 'active':
                        active_packages.append(package)
                        sessions_remaining = package.get('sessions_remaining', 0)
                        total_sessions += sessions_remaining
            
            if not active_packages:
                return {
                    'status': 'no_package',
                    'status_class': 'danger',
                    'status_text': 'No Active Package',
                    'status_icon': 'fas fa-times-circle'
                }
            
            # Determine overall status
            if total_sessions == 0:
                return {
                    'status': 'expired',
                    'status_class': 'warning',
                    'status_text': 'Package Expired',
                    'status_icon': 'fas fa-exclamation-triangle',
                    'sessions_remaining': 0,
                    'package_type': ', '.join([pkg.get('package_name', 'Unknown Package') for pkg in active_packages])
                }
            elif total_sessions <= 2:
                return {
                    'status': 'low',
                    'status_class': 'warning',
                    'status_text': 'Low Sessions',
                    'status_icon': 'fas fa-battery-quarter',
                    'sessions_remaining': total_sessions,
                    'package_type': ', '.join([pkg.get('package_name', 'Unknown Package') for pkg in active_packages])
                }
            else:
                return {
                    'status': 'funded',
                    'status_class': 'success',
                    'status_text': 'Funded - Active Package',
                    'status_icon': 'fas fa-check-circle',
                    'sessions_remaining': total_sessions,
                    'package_type': ', '.join([pkg.get('package_name', 'Unknown Package') for pkg in active_packages])
                }
            
        except Exception as e:
            logger.error(f"❌ Error processing training packages: {e}")
            return self._get_fallback_funding_status(participant_name)
    
    def _get_fallback_funding_status(self, participant_name: str) -> dict:
        """Fallback funding status when API is unavailable"""
        return {
            'status': 'unavailable',
            'status_class': 'secondary', 
            'status_text': 'Status Unavailable',
            'status_icon': 'fas fa-question-circle'
        }

# Initialize training package cache
training_package_cache = TrainingPackageCache()

# Initialize ClubOS integration
clubos = ClubOSIntegration()

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'current_year': datetime.now().year
    }

class DatabaseManager:
    def __init__(self, db_path='gym_bot.db'):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing tables to recreate with new schema
        cursor.execute('DROP TABLE IF EXISTS members')
        cursor.execute('DROP TABLE IF EXISTS prospects')
        cursor.execute('DROP TABLE IF EXISTS training_clients')
        
        # Enhanced members table with agreement fields
        cursor.execute('''
            CREATE TABLE members (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                club_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth DATE,
                gender TEXT,
                membership_start DATE,
                membership_end DATE,
                last_visit DATE,
                status TEXT,
                status_message TEXT,
                user_type TEXT,
                key_fob TEXT,
                photo_url TEXT,
                
                -- Home Club Information
                home_club_name TEXT,
                home_club_address TEXT,
                home_club_city TEXT,
                home_club_state TEXT,
                home_club_zip TEXT,
                home_club_af_number TEXT,
                
                -- Agreement Information
                agreement_id TEXT,
                agreement_guid TEXT,
                agreement_status TEXT,
                agreement_start_date DATE,
                agreement_end_date DATE,
                agreement_type TEXT,
                agreement_rate REAL,
                
                -- Agreement History
                agreement_history_count INTEGER DEFAULT 0,
                past_agreements TEXT, -- JSON format
                
                -- Payment Information
                payment_token TEXT,
                card_type TEXT,
                card_last4 TEXT,
                expiration_month TEXT,
                expiration_year TEXT,
                billing_name TEXT,
                billing_address TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_zip TEXT,
                account_type TEXT,
                routing_number TEXT,
                
                -- Additional Fields
                emergency_contact TEXT,
                emergency_phone TEXT,
                employer TEXT,
                occupation TEXT,
                has_app BOOLEAN DEFAULT 0,
                last_activity_timestamp TEXT,
                contract_types TEXT,
                bucket INTEGER,
                color INTEGER,
                rating INTEGER,
                source TEXT,
                trial BOOLEAN DEFAULT 0,
                originated_from TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced prospects table
        cursor.execute('''
            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                club_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth DATE,
                gender TEXT,
                status TEXT,
                status_message TEXT,
                
                -- Prospect-specific fields
                lead_source TEXT,
                interest_level INTEGER,
                follow_up_date DATE,
                notes TEXT,
                trial_session_date DATE,
                tour_completed BOOLEAN DEFAULT 0,
                
                -- Contact preferences
                preferred_contact_method TEXT,
                best_time_to_call TEXT,
                
                -- Additional tracking
                bucket INTEGER,
                color INTEGER,
                rating INTEGER,
                source TEXT,
                trial BOOLEAN DEFAULT 1,
                originated_from TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training clients table
        cursor.execute('''
            CREATE TABLE training_clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                trainer_name TEXT,
                session_type TEXT,
                sessions_remaining INTEGER DEFAULT 0,
                last_session DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def import_master_contact_list(self, csv_path):
        """Import master contact list from CSV with comprehensive data."""
        if not os.path.exists(csv_path):
            logger.warning(f"Master contact list not found: {csv_path}")
            return
            
        logger.info(f"Importing master contact list from: {csv_path}")
        
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM members')
        cursor.execute('DELETE FROM prospects')
        
        members_count = 0
        prospects_count = 0
        
        for _, row in df.iterrows():
            try:
                # Determine if this is a member or prospect
                is_prospect = str(row.get('prospect', 'False')).lower() == 'true'
                
                # Common fields
                common_data = {
                    'id': row.get('id'),
                    'guid': row.get('guid'),
                    'club_id': row.get('clubId'),
                    'first_name': row.get('firstName'),
                    'last_name': row.get('lastName'),
                    'full_name': f"{row.get('firstName', '')} {row.get('lastName', '')}".strip(),
                    'email': row.get('email'),
                    'mobile_phone': row.get('mobilePhone'),
                    'home_phone': row.get('homePhone'),
                    'work_phone': row.get('workPhone'),
                    'address1': row.get('address1'),
                    'address2': row.get('address2'),
                    'city': row.get('city'),
                    'state': row.get('state'),
                    'zip_code': row.get('zip'),
                    'country': row.get('country'),
                    'date_of_birth': row.get('dateOfBirth'),
                    'gender': 'Female' if str(row.get('female', '')).lower() == 'true' else 'Male' if str(row.get('female', '')).lower() == 'false' else 'Unknown',
                    'status': row.get('status'),
                    'status_message': row.get('statusMessage'),
                    'bucket': row.get('bucket'),
                    'color': row.get('color'),
                    'rating': row.get('rating'),
                    'source': row.get('source'),
                    'trial': str(row.get('trial', 'False')).lower() == 'true',
                    'originated_from': row.get('originatedFrom')
                }
                
                if is_prospect:
                    # Insert as prospect
                    prospect_data = {
                        **common_data,
                        'lead_source': row.get('source'),
                        'interest_level': row.get('rating', 0),
                        'notes': row.get('statusMessage', ''),
                    }
                    
                    columns = ', '.join(prospect_data.keys())
                    placeholders = ', '.join(['?' for _ in prospect_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO prospects ({columns})
                        VALUES ({placeholders})
                    ''', list(prospect_data.values()))
                    
                    prospects_count += 1
                    
                else:
                    # Insert as member with agreement data
                    member_data = {
                        **common_data,
                        'membership_start': row.get('membershipStart'),
                        'membership_end': row.get('membershipEnd'),
                        'last_visit': row.get('lastVisit'),
                        'user_type': row.get('userType'),
                        'key_fob': row.get('keyFob'),
                        'photo_url': row.get('photoUrl'),
                        
                        # Home Club Information
                        'home_club_name': row.get('homeClub_name'),
                        'home_club_address': row.get('homeClub_address1'),
                        'home_club_city': row.get('homeClub_city'),
                        'home_club_state': row.get('homeClub_state'),
                        'home_club_zip': row.get('homeClub_zip'),
                        'home_club_af_number': row.get('homeClub_afNumber'),
                        
                        # Agreement Information
                        'agreement_id': row.get('agreement_agreementID'),
                        'agreement_guid': row.get('agreement_agreementGuid'),
                        'agreement_status': row.get('agreement_status'),
                        'agreement_start_date': row.get('agreement_startDate'),
                        'agreement_end_date': row.get('agreement_endDate'),
                        'agreement_type': row.get('agreement_type'),
                        'agreement_rate': row.get('agreement_rate'),
                        
                        # Agreement History
                        'agreement_history_count': row.get('agreementHistory_count', 0),
                        
                        # Payment Information
                        'payment_token': row.get('agreementTokenQuery_paymentToken'),
                        'card_type': row.get('agreementTokenQuery_cardType'),
                        'card_last4': row.get('agreementTokenQuery_accountLast4'),
                        'expiration_month': row.get('agreementTokenQuery_expirationMonth'),
                        'expiration_year': row.get('agreementTokenQuery_expirationYear'),
                        'billing_name': row.get('agreementTokenQuery_holderName'),
                        'billing_address': row.get('agreementTokenQuery_holderStreet'),
                        'billing_city': row.get('agreementTokenQuery_holderCity'),
                        'billing_state': row.get('agreementTokenQuery_holderState'),
                        'billing_zip': row.get('agreementTokenQuery_holderZip'),
                        'account_type': row.get('agreementTokenQuery_accountType'),
                        'routing_number': row.get('agreementTokenQuery_routingNumber'),
                        
                        # Additional Fields
                        'emergency_contact': row.get('emergencyContact'),
                        'emergency_phone': row.get('emergencyPhone'),
                        'employer': row.get('employer'),
                        'occupation': row.get('occupation'),
                        'has_app': str(row.get('hasApp', 'False')).lower() == 'true',
                        'last_activity_timestamp': row.get('lastActivityTimestamp'),
                        'contract_types': row.get('contractTypes')
                    }
                    
                    columns = ', '.join(member_data.keys())
                    placeholders = ', '.join(['?' for _ in member_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO members ({columns})
                        VALUES ({placeholders})
                    ''', list(member_data.values()))
                    
                    members_count += 1
                    
            except Exception as e:
                logger.error(f"Error importing row {row.get('id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"Import complete: {members_count} members, {prospects_count} prospects")
        return members_count, prospects_count

# Initialize database manager
db_manager = DatabaseManager()

# Import the latest master contact list with agreements
latest_csv = "master_contact_list_with_agreements_20250722_180712.csv"
if os.path.exists(latest_csv):
    db_manager.import_master_contact_list(latest_csv)

@app.route('/')
def dashboard():
    """Main dashboard with overview."""
    print("=== DASHBOARD ROUTE TRIGGERED ===")
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prospects")
    total_prospects = cursor.fetchone()[0]
    
    # Get recent members
    cursor.execute("SELECT * FROM members ORDER BY created_at DESC LIMIT 5")
    recent_members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Get recent prospects
    cursor.execute("SELECT * FROM prospects ORDER BY created_at DESC LIMIT 5")
    recent_prospects = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Get training clients
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    total_training_clients = cursor.fetchone()[0]
    
    conn.close()
    
    # Get live data from ClubOS
    print("=== STARTING CLUBOS INTEGRATION ===")
    live_events = []
    today_events = []
    clubos_status = "Disconnected"
    try:
        print("=== ATTEMPTING CLUBOS AUTHENTICATION ===")
        if clubos.authenticate():
            print("=== CLUBOS AUTHENTICATED, GETTING EVENTS ===")
            live_events = clubos.get_live_events()
            print(f"=== GOT {len(live_events)} LIVE EVENTS ===")
            
            # Filter events for today only
            today_date = datetime.now().date()
            for event in live_events:
                if isinstance(event, dict) and 'raw_start' in event:
                    if event['raw_start'].date() == today_date:
                        today_events.append(event)
                        
            # Sort today's events chronologically (morning to evening)
            today_events.sort(key=lambda x: x['raw_start'] if 'raw_start' in x else datetime.min)
                        
            print(f"=== FILTERED TO {len(today_events)} TODAY'S EVENTS ===")
            print(f"=== SORTED CHRONOLOGICALLY FROM {today_events[0]['start_time'] if today_events else 'N/A'} ===")
            clubos_status = "Connected"
        else:
            print("=== CLUBOS AUTHENTICATION FAILED ===")
            clubos_status = "Authentication Failed"
    except Exception as e:
        print(f"=== CLUBOS ERROR: {e} ===")
        logger.error(f"ClubOS connection error: {e}")
        clubos_status = f"Error: {str(e)[:50]}..."
    
    # Get current sync time
    sync_time = datetime.now()
    
    # Categorize events for new metrics
    training_sessions_count = 0
    appointments_count = 0
    
    training_keywords = ['training', 'session', 'workout', 'pt', 'personal']
    appointment_keywords = ['consult', 'meeting', 'appointment', 'tour', 'assessment', 'savannah']
    
    for event in today_events:
        title = event.get('title', '').lower()
        participants = event.get('participants', [])
        participant_name = participants[0].lower() if participants and participants[0] else ''
        
        # Check if it's an appointment based on multiple criteria
        is_appointment = (
            # Check for appointment keywords in title
            any(keyword in title for keyword in appointment_keywords) or
            # Check for Savannah specifically
            'savannah' in participant_name or
            'savannah' in title or
            # Check for sessions with no participants (likely appointments)
            not participants or participants[0] == '' or
            # Check for specific appointment indicators
            'consult' in title or 'appointment' in title or 'tour' in title or 'assessment' in title
        )
        
        if is_appointment:
            appointments_count += 1
        else:
            training_sessions_count += 1
    
    # Mock bot activity data (will be replaced with real data)
    bot_activities = [
        {
            'id': 1,
            'action': 'Sent Welcome Message',
            'recipient': 'Sarah Johnson',
            'preview': 'Welcome to Anytime Fitness! Ready to start your journey?',
            'time': '2 minutes ago',
            'icon': 'paper-plane',
            'color': 'success',
            'status': 'Delivered',
            'status_color': 'success'
        },
        {
            'id': 2,
            'action': 'Payment Reminder',
            'recipient': 'Mike Chen',
            'preview': 'Your payment for this month is due tomorrow. Click here to pay...',
            'time': '15 minutes ago',
            'icon': 'credit-card',
            'color': 'warning',
            'status': 'Pending',
            'status_color': 'warning'
        },
        {
            'id': 3,
            'action': 'Follow-up Message',
            'recipient': 'Lisa Rodriguez',
            'preview': 'How was your workout yesterday? Ready to book your next session?',
            'time': '1 hour ago',
            'icon': 'comment',
            'color': 'primary',
            'status': 'Read',
            'status_color': 'success'
        }
    ]
    
    # Mock conversation data (will be replaced with real data)
    bot_conversations = [
        {
            'id': 'conv_001',
            'contact_name': 'Jessica Williams',
            'last_message': 'Yes, I would like to schedule a session for tomorrow',
            'last_time': '5 min ago',
            'last_sender': 'user',
            'unread': True,
            'status': 'Hot Lead',
            'status_color': 'success',
            'needs_attention': False
        },
        {
            'id': 'conv_002',
            'contact_name': 'David Thompson',
            'last_message': 'Can you help me with my payment plan?',
            'last_time': '1 hour ago',
            'last_sender': 'user',
            'unread': True,
            'status': 'Support',
            'status_color': 'warning',
            'needs_attention': True
        },
        {
            'id': 'conv_003',
            'contact_name': 'Emily Davis',
            'last_message': 'Thanks! I will see you next week.',
            'last_time': '3 hours ago',
            'last_sender': 'bot',
            'unread': False,
            'status': 'Scheduled',
            'status_color': 'purple',
            'needs_attention': False
        }
    ]
    
    # Create bot_stats dictionary for template
    bot_stats = {
        'messages_sent': len(bot_activities),
        'last_activity': f"{random.randint(1, 10)} minutes ago: {random.choice(['Responded to inquiry', 'Sent follow-up', 'Scheduled consultation', 'Updated notes'])}"
    }
    
    # Create stats dictionary for dashboard metrics
    stats = {
        'todays_events': len(today_events),
        'next_session_time': today_events[0].get('start_time', 'None scheduled') if today_events else 'None scheduled',
        'revenue': f"{random.randint(500, 2000):,}"  # Mock revenue data
    }
    
    return render_template('dashboard.html', 
                         total_members=total_members,
                         total_prospects=total_prospects,
                         total_training_clients=total_training_clients,
                         total_live_events=len(live_events),
                         today_events_count=len(today_events),
                         
                         # New bot supervision metrics
                         training_sessions_count=training_sessions_count,
                         appointments_count=appointments_count,
                         bot_messages_today=len(bot_activities),
                         active_conversations=len([c for c in bot_conversations if c['unread']]),
                         bot_activities=bot_activities,
                         bot_conversations=bot_conversations,
                         bot_stats=bot_stats,  # Add the missing bot_stats
                         stats=stats,  # Add the missing stats
                         
                         recent_members=recent_members,
                         recent_prospects=recent_prospects,
                         recent_events=today_events,  # Show today's events only
                         clubos_status=clubos_status,
                         clubos_connected=clubos.authenticated,
                         sync_time=sync_time)

@app.route('/api/check-funding', methods=['POST'])
def api_check_funding():
    """API endpoint to check funding status for a training session participant"""
    try:
        data = request.get_json()
        participant_name = data.get('participant', '').strip()
        participant_email = data.get('email', '').strip()
        
        if not participant_name:
            return jsonify({
                'success': False,
                'error': 'Participant name is required'
            }), 400
        
        logger.info(f"🔍 API call: Checking funding for {participant_name}")
        
        # Use the training package cache to lookup funding
        funding_data = training_package_cache.lookup_participant_funding(
            participant_name, 
            participant_email if participant_email else None
        )
        
        return jsonify({
            'success': True,
            'participant': participant_name,
            'funding': funding_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error in funding API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bot-activity')
def api_bot_activity():
    """API endpoint for real-time bot activity updates"""
    # This will be replaced with real bot activity data
    bot_activities = [
        {
            'id': 1,
            'action': 'Sent Welcome Message',
            'recipient': 'Sarah Johnson',
            'preview': 'Welcome to Anytime Fitness! Ready to start your journey?',
            'time': '2 minutes ago',
            'icon': 'paper-plane',
            'color': 'success',
            'status': 'Delivered',
            'status_color': 'success'
        },
        {
            'id': 2,
            'action': 'Payment Reminder',
            'recipient': 'Mike Chen',
            'preview': 'Your payment for this month is due tomorrow. Click here to pay...',
            'time': '15 minutes ago',
            'icon': 'credit-card',
            'color': 'warning',
            'status': 'Pending',
            'status_color': 'warning'
        }
    ]
    return jsonify({'activities': bot_activities})

@app.route('/api/refresh-inbox', methods=['POST'])
def api_refresh_inbox():
    """API endpoint to refresh bot inbox"""
    try:
        # This will trigger a real inbox refresh once implemented
        return jsonify({'success': True, 'message': 'Inbox refreshed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/conversation/<conversation_id>')
def view_conversation(conversation_id):
    """View individual conversation details"""
    # This will show the full conversation thread
    return f"<h1>Conversation {conversation_id}</h1><p>Full conversation view will be implemented here.</p>"

@app.route('/bot-settings')
def bot_settings():
    """Bot configuration and settings page"""
    return "<h1>Bot Settings</h1><p>Bot configuration interface will be implemented here.</p>"

@app.route('/bot-logs')
def bot_logs():
    """Full bot activity logs page"""
    return "<h1>Bot Activity Logs</h1><p>Complete bot activity history will be implemented here.</p>"

@app.route('/inbox')
def inbox():
    """Full inbox management page"""
    return "<h1>Inbox Management</h1><p>Complete inbox interface will be implemented here.</p>"
    """Calendar management page with live ClubOS integration"""
    try:
        print(f"\n=== CALENDAR PAGE ACCESSED ===")
        print(f"ClubOS authenticated: {clubos.authenticated}")
        
        # Get live events from ClubOS using the same method as dashboard
        if clubos.authenticated:
            print("Using existing authentication...")
            events = clubos.get_live_events()
            connection_status = 'Connected'
            sync_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            print("Attempting authentication...")
            events = clubos.get_live_events()  # This will auto-authenticate
            if clubos.authenticated:
                connection_status = 'Connected'
                sync_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                connection_status = 'Disconnected'
                sync_time = None
        
        print(f"Retrieved {len(events)} events")
        print(f"Connection status: {connection_status}")
        print("===============================\n")
            
        return render_template('calendar.html', 
                             events=events,
                             connection_status=connection_status,
                             sync_time=sync_time)
    except Exception as e:
        logger.error(f"Calendar error: {e}")
        flash(f'Error loading calendar: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/messaging')
def messaging():
    """Messaging page for member/prospect communication"""
    try:
        # Get recent members and prospects for messaging
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Get recent members
        cursor.execute('''
            SELECT first_name, last_name, email, mobile_phone 
            FROM members 
            WHERE status = 'ACTIVE' 
            ORDER BY created_date DESC 
            LIMIT 20
        ''')
        recent_members = cursor.fetchall()
        
        # Get recent prospects
        cursor.execute('''
            SELECT first_name, last_name, email, mobile_phone 
            FROM prospects 
            ORDER BY created_date DESC 
            LIMIT 20
        ''')
        recent_prospects = cursor.fetchall()
        
        conn.close()
        
        return render_template('messaging.html', 
                             recent_members=recent_members,
                             recent_prospects=recent_prospects)
    except Exception as e:
        logger.error(f"Messaging error: {e}")
        flash(f'Error loading messaging: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/send-message', methods=['POST'])
def send_message():
    """Send message to member or prospect"""
    try:
        recipient = request.form.get('recipient')
        message = request.form.get('message')
        method = request.form.get('method', 'email')  # email or sms
        
        # Here you would integrate with actual messaging service
        # For now, just log the message
        logger.info(f"Message sent to {recipient} via {method}: {message}")
        flash(f'Message sent to {recipient} via {method}', 'success')
        
        return redirect(url_for('messaging'))
    except Exception as e:
        logger.error(f"Send message error: {e}")
        flash(f'Error sending message: {str(e)}', 'error')
        return redirect(url_for('messaging'))

@app.route('/members')
def members_page():
    """Members page - Active paying members only."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get search parameters
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 25
    offset = (page - 1) * per_page
    
    # Build query
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR mobile_phone LIKE ?)"
        search_term = f"%{search}%"
        params = [search_term, search_term, search_term, search_term]
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM members {where_clause}", params)
    total_members = cursor.fetchone()[0]
    
    # Get members with pagination
    cursor.execute(f'''
        SELECT * FROM members {where_clause} 
        ORDER BY full_name 
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    
    members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total_members + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('members.html', 
                         members=members,
                         search=search,
                         page=page,
                         total_pages=total_pages,
                         total_members=total_members,
                         has_prev=has_prev,
                         has_next=has_next,
                         per_page=per_page)

@app.route('/prospects')
def prospects_page():
    """Prospects page - Potential members only."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get search parameters
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    # Build query
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR mobile_phone LIKE ?)"
        search_term = f"%{search}%"
        params = [search_term, search_term, search_term, search_term]
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM prospects {where_clause}", params)
    total_prospects = cursor.fetchone()[0]
    
    # Get prospects with pagination
    cursor.execute(f'''
        SELECT * FROM prospects {where_clause} 
        ORDER BY full_name 
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    
    prospects = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total_prospects + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('prospects.html', 
                         prospects=prospects,
                         search=search,
                         page=page,
                         total_pages=total_pages,
                         total_prospects=total_prospects,
                         has_prev=has_prev,
                         has_next=has_next,
                         per_page=per_page)

@app.route('/member/<int:member_id>')
def member_detail(member_id):
    """Detailed view of a specific member."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    row = cursor.fetchone()
    
    if not row:
        return redirect(url_for('members_page'))
    
    member = dict(zip([col[0] for col in cursor.description], row))
    
    # Get training sessions for this member
    cursor.execute('''
        SELECT * FROM training_clients 
        WHERE member_id = ? 
        ORDER BY created_at DESC
    ''', (member_id,))
    
    training_sessions = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('member_detail.html', member=member, training_sessions=training_sessions)

@app.route('/prospect/<int:prospect_id>')
def prospect_detail(prospect_id):
    """Detailed view of a specific prospect."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM prospects WHERE id = ?", (prospect_id,))
    row = cursor.fetchone()
    
    if not row:
        return redirect(url_for('prospects_page'))
    
    prospect = dict(zip([col[0] for col in cursor.description], row))
    
    conn.close()
    
    return render_template('prospect_detail.html', prospect=prospect)

@app.route('/training-clients')
def training_clients_page():
    """Training clients page."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tc.*, m.full_name as member_name 
        FROM training_clients tc 
        LEFT JOIN members m ON tc.member_id = m.id 
        ORDER BY tc.created_at DESC
    ''')
    clients = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('training_clients.html', clients=clients)

@app.route('/calendar')
def calendar_page():
    """Live calendar management page with ClubOS integration."""
    # Get live events from ClubOS
    events = clubos.get_live_events()
    
    # Process events for display
    processed_events = []
    for event in events:
        processed_events.append({
            'id': event.id,
            'title': str(event),
            'type': 'Training Session',  # Default type
            'status': 'Active',
            'date': datetime.now().strftime('%Y-%m-%d'),  # Placeholder
            'time': 'TBD',  # Placeholder
        })
    
    return render_template('calendar.html', 
                         events=processed_events,
                         total_events=len(processed_events),
                         clubos_connected=clubos.authenticated)

@app.route('/calendar/delete/<int:event_id>', methods=['POST'])
def delete_calendar_event(event_id):
    """Delete a calendar event via ClubOS API."""
    try:
        success = clubos.delete_event(event_id)
        if success:
            flash(f'Event {event_id} deleted successfully!', 'success')
        else:
            flash(f'Failed to delete event {event_id}', 'error')
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        flash(f'Error deleting event: {str(e)}', 'error')
    
    return redirect(url_for('calendar_page'))

@app.route('/calendar/sync', methods=['POST'])
def sync_calendar():
    """Manually sync calendar data from ClubOS."""
    try:
        if clubos.authenticate():
            events = clubos.get_live_events()
            flash(f'Calendar synced successfully! Found {len(events)} events.', 'success')
        else:
            flash('Failed to connect to ClubOS for sync.', 'error')
    except Exception as e:
        logger.error(f"Calendar sync error: {e}")
        flash(f'Sync error: {str(e)}', 'error')
    
    return redirect(url_for('calendar_page'))

@app.route('/messaging')
def messaging_page():
    """Messaging center for member communication."""
    # Get recent members for quick messaging
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM members ORDER BY created_at DESC LIMIT 20")
    recent_members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM prospects ORDER BY created_at DESC LIMIT 20")
    recent_prospects = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('messaging.html', 
                         recent_members=recent_members,
                         recent_prospects=recent_prospects,
                         clubos_connected=clubos.authenticated)

if __name__ == "__main__":
    # Templates already exist - don't overwrite our custom designs!
    # create_templates() function COMPLETELY REMOVED to prevent template overwrites
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Anytime Fitness Club Management{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <style>
        :root {
            --af-purple: #663399;
            --af-light-purple: #8A4FBE;
            --af-dark-purple: #4A2570;
            --af-white: #FFFFFF;
            --af-light-gray: #F8F9FA;
            --af-gray: #6C757D;
            --af-success: #28A745;
            --af-warning: #FFC107;
            --af-danger: #DC3545;
        }
        
        body {
            background-color: var(--af-light-gray);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-dark-purple) 100%);
            box-shadow: 0 2px 10px rgba(102, 51, 153, 0.3);
        }
        
        .navbar-brand {
            font-weight: bold;
            font-size: 1.5rem;
            color: var(--af-white) !important;
        }
        
        .nav-link {
            color: var(--af-white) !important;
            transition: all 0.3s ease;
            margin: 0 5px;
            border-radius: 5px;
        }
        
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .nav-link.active {
            background-color: var(--af-light-purple) !important;
        }
        
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-light-purple) 100%);
            color: var(--af-white);
            border-radius: 15px 15px 0 0 !important;
            border: none;
            padding: 1.5rem;
        }
        
        .btn-purple {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-light-purple) 100%);
            border: none;
            color: var(--af-white);
            border-radius: 25px;
            padding: 10px 25px;
            transition: all 0.3s ease;
        }
        
        .btn-purple:hover {
            background: linear-gradient(135deg, var(--af-dark-purple) 0%, var(--af-purple) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 51, 153, 0.4);
            color: var(--af-white);
        }
        
        .badge-purple {
            background-color: var(--af-purple);
            color: var(--af-white);
        }
        
        .text-purple { color: var(--af-purple) !important; }
        
        .member-card, .prospect-card {
            border-left: 5px solid var(--af-purple);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .member-card:hover, .prospect-card:hover {
            border-left-color: var(--af-light-purple);
            box-shadow: 0 8px 20px rgba(102, 51, 153, 0.2);
        }
        
        .agreement-info {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .payment-info {
            background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .contact-info {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .search-bar {
            border-radius: 25px;
            border: 2px solid var(--af-purple);
            padding: 10px 20px;
        }
        
        .search-bar:focus {
            border-color: var(--af-light-purple);
            box-shadow: 0 0 0 0.2rem rgba(102, 51, 153, 0.25);
        }
        
        .pagination .page-link {
            color: var(--af-purple);
            border-color: var(--af-purple);
        }
        
        .pagination .page-item.active .page-link {
            background-color: var(--af-purple);
            border-color: var(--af-purple);
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--af-white) 0%, var(--af-light-gray) 100%);
            border-left: 5px solid var(--af-purple);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: var(--af-purple);
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: var(--af-gray);
            font-size: 1.1rem;
        }
        
        .detail-section {
            margin-bottom: 2rem;
        }
        
        .detail-label {
            font-weight: bold;
            color: var(--af-purple);
            margin-right: 10px;
        }
        
        .detail-value {
            color: var(--af-gray);
        }
        
        .table-purple thead {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-light-purple) 100%);
            color: var(--af-white);
        }
        
        .status-active { color: var(--af-success); }
        .status-inactive { color: var(--af-danger); }
        .status-trial { color: var(--af-warning); }
        
        @media (max-width: 768px) {
            .stat-number { font-size: 2rem; }
            .card { margin-bottom: 1rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-dumbbell me-2"></i>
                Anytime Fitness Management
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/"><i class="fas fa-tachometer-alt me-1"></i>Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/members"><i class="fas fa-users me-1"></i>Members</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/prospects"><i class="fas fa-user-plus me-1"></i>Prospects</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/training-clients"><i class="fas fa-dumbbell me-1"></i>Training</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/calendar"><i class="fas fa-calendar me-1"></i>Calendar</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/messaging"><i class="fas fa-envelope me-1"></i>Messages</a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-1"></i>Admin
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>Settings</a></li>
                            <li><a class="dropdown-item" href="#"><i class="fas fa-download me-2"></i>Export Data</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(f'{templates_dir}/base.html', 'w') as f:
        f.write(base_template)
    
    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Dashboard - Anytime Fitness Management{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="text-purple mb-3">
            <i class="fas fa-tachometer-alt me-2"></i>
            Club Dashboard
        </h1>
        <p class="lead text-muted">Welcome to your Anytime Fitness club management system</p>
    </div>
</div>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_members }}</div>
            <div class="stat-label">Active Members</div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_prospects }}</div>
            <div class="stat-label">Prospects</div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_training_clients }}</div>
            <div class="stat-label">Training Clients</div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_live_events }}</div>
            <div class="stat-label">Live Events</div>
        </div>
    </div>
</div>

<!-- ClubOS Status Card -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-plug me-2"></i>ClubOS Integration Status
                </h5>
            </div>
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <p class="mb-1">
                            <strong>Status:</strong> 
                            <span class="badge bg-{{ 'success' if clubos_connected else 'danger' }}">
                                {{ clubos_status }}
                            </span>
                        </p>
                        <p class="mb-1">
                            <strong>Live Events:</strong> {{ total_live_events }} calendar events retrieved
                        </p>
                        <p class="mb-0">
                            <strong>Last Sync:</strong> {{ moment().format('MMMM Do YYYY, h:mm:ss a') }}
                        </p>
                    </div>
                    <div class="col-md-4 text-end">
                        <a href="/calendar" class="btn btn-purple me-2">
                            <i class="fas fa-calendar me-2"></i>Manage Calendar
                        </a>
                        <form method="POST" action="/calendar/sync" style="display: inline;">
                            <button type="submit" class="btn btn-outline-purple">
                                <i class="fas fa-sync me-2"></i>Sync Now
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Quick Access Cards -->
<div class="row mb-4">
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-users me-2"></i>Recent Members</h5>
            </div>
            <div class="card-body">
                {% if recent_members %}
                    {% for member in recent_members %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <strong>{{ member.full_name }}</strong><br>
                            <small class="text-muted">{{ member.email }}</small>
                        </div>
                        <a href="/member/{{ member.id }}" class="btn btn-sm btn-purple">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No recent members</p>
                {% endif %}
                <div class="text-center mt-3">
                    <a href="/members" class="btn btn-purple">
                        <i class="fas fa-users me-2"></i>View All Members
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-user-plus me-2"></i>Recent Prospects</h5>
            </div>
            <div class="card-body">
                {% if recent_prospects %}
                    {% for prospect in recent_prospects %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <strong>{{ prospect.full_name }}</strong><br>
                            <small class="text-muted">{{ prospect.email }}</small>
                        </div>
                        <a href="/prospect/{{ prospect.id }}" class="btn btn-sm btn-purple">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No recent prospects</p>
                {% endif %}
                <div class="text-center mt-3">
                    <a href="/prospects" class="btn btn-purple">
                        <i class="fas fa-user-plus me-2"></i>View All Prospects
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Live Events Section -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-calendar-alt me-2"></i>Live Calendar Events
                    {% if clubos_connected %}
                        <span class="badge bg-success ms-2">Connected</span>
                    {% else %}
                        <span class="badge bg-danger ms-2">Disconnected</span>
                    {% endif %}
                </h5>
            </div>
            <div class="card-body">
                {% if recent_events %}
                    {% for event in recent_events %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <strong>Event {{ event.id }}</strong><br>
                            <small class="text-muted">{{ event }}</small>
                        </div>
                        <div>
                            <a href="/calendar" class="btn btn-sm btn-outline-purple me-2">
                                <i class="fas fa-eye"></i>
                            </a>
                            <form method="POST" action="/calendar/delete/{{ event.id }}" style="display: inline;">
                                <button type="submit" class="btn btn-sm btn-outline-danger" 
                                        onclick="return confirm('Delete this event?')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="text-center py-4">
                        {% if clubos_connected %}
                            <p class="text-muted">No calendar events found</p>
                        {% else %}
                            <p class="text-warning">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                ClubOS not connected. Unable to retrieve live events.
                            </p>
                        {% endif %}
                    </div>
                {% endif %}
                <div class="text-center mt-3">
                    <a href="/calendar" class="btn btn-purple">
                        <i class="fas fa-calendar me-2"></i>Manage Calendar
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/dashboard.html', 'w') as f:
        f.write(dashboard_template)
    
    # Calendar template
    calendar_template = '''{% extends "base.html" %}
{% block title %}Calendar Management - {{ super() }}{% endblock %}
{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h3 class="mb-0">
                            <i class="fas fa-calendar-alt me-2"></i>Calendar Management
                        </h3>
                        <div>
                            Status: 
                            {% if connection_status == 'Connected' %}
                                <span class="badge bg-success">{{ connection_status }}</span>
                            {% else %}
                                <span class="badge bg-danger">{{ connection_status }}</span>
                            {% endif %}
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <form method="POST" action="/calendar/sync">
                                <button type="submit" class="btn btn-purple">
                                    <i class="fas fa-sync me-2"></i>Sync Events
                                </button>
                            </form>
                        </div>
                        <div class="col-md-6 text-end">
                            {% if sync_time %}
                                <small class="text-muted">Last sync: {{ sync_time }}</small>
                            {% endif %}
                        </div>
                    </div>
                    
                    {% if events %}
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Event ID</th>
                                        <th>Details</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for event in events %}
                                    <tr>
                                        <td>{{ event.id if event.id else 'N/A' }}</td>
                                        <td>{{ event }}</td>
                                        <td>
                                            {% if event.id %}
                                            <form method="POST" action="/calendar/delete/{{ event.id }}" 
                                                  style="display: inline;">
                                                <button type="submit" class="btn btn-sm btn-danger"
                                                        onclick="return confirm('Delete event {{ event.id }}?')">
                                                    <i class="fas fa-trash me-1"></i>Delete
                                                </button>
                                            </form>
                                            {% endif %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    {% else %}
                        <div class="text-center py-5">
                            {% if connection_status == 'Connected' %}
                                <i class="fas fa-calendar-check fa-3x text-muted mb-3"></i>
                                <h5>No Events Found</h5>
                                <p class="text-muted">No calendar events to display</p>
                            {% else %}
                                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                                <h5>ClubOS Disconnected</h5>
                                <p class="text-muted">Please authenticate to view calendar events</p>
                                <form method="POST" action="/calendar/sync">
                                    <button type="submit" class="btn btn-purple">
                                        <i class="fas fa-plug me-2"></i>Connect to ClubOS
                                    </button>
                                </form>
                            {% endif %}
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/calendar.html', 'w') as f:
        f.write(calendar_template)
    
    # Messaging template
    messaging_template = '''{% extends "base.html" %}
{% block title %}Messaging - {{ super() }}{% endblock %}
{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h3 class="mb-0">
                        <i class="fas fa-comments me-2"></i>Send Message
                    </h3>
                </div>
                <div class="card-body">
                    <form method="POST" action="/send-message">
                        <div class="mb-3">
                            <label for="recipient" class="form-label">Recipient</label>
                            <select class="form-select" id="recipient" name="recipient" required>
                                <option value="">Select recipient...</option>
                                <optgroup label="Members">
                                    {% for member in recent_members %}
                                    <option value="{{ member[2] }}">{{ member[0] }} {{ member[1] }} ({{ member[2] }})</option>
                                    {% endfor %}
                                </optgroup>
                                <optgroup label="Prospects">
                                    {% for prospect in recent_prospects %}
                                    <option value="{{ prospect[2] }}">{{ prospect[0] }} {{ prospect[1] }} ({{ prospect[2] }})</option>
                                    {% endfor %}
                                </optgroup>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="method" class="form-label">Method</label>
                            <select class="form-select" id="method" name="method" required>
                                <option value="email">Email</option>
                                <option value="sms">SMS</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="message" class="form-label">Message</label>
                            <textarea class="form-control" id="message" name="message" rows="5" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-purple">
                            <i class="fas fa-paper-plane me-2"></i>Send Message
                        </button>
                    </form>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Quick Templates</h5>
                </div>
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <button class="btn btn-outline-purple btn-sm" onclick="setMessage('Welcome to Anytime Fitness! We\\'re excited to have you as part of our fitness family.')">
                            Welcome Message
                        </button>
                        <button class="btn btn-outline-purple btn-sm" onclick="setMessage('Hi! Just checking in to see how your fitness journey is going. Let us know if you need any support!')">
                            Check-in Message
                        </button>
                        <button class="btn btn-outline-purple btn-sm" onclick="setMessage('Don\\'t forget about your upcoming training session. We\\'re here to help you reach your goals!')">
                            Reminder Message
                        </button>
                        <button class="btn btn-outline-purple btn-sm" onclick="setMessage('Thank you for being a valued member of Anytime Fitness. Your commitment to health and fitness inspires us!')">
                            Thank You Message
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function setMessage(text) {
    document.getElementById('message').value = text;
}
</script>
{% endblock %}'''
    
    with open(f'{templates_dir}/messaging.html', 'w') as f:
        f.write(messaging_template)
    
    # Members template with full agreement information
    members_template = '''{% extends "base.html" %}

{% block title %}Members - Anytime Fitness Management{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="text-purple mb-3">
            <i class="fas fa-users me-2"></i>
            Active Members
            <span class="badge badge-purple ms-3">{{ total_members }} Total</span>
        </h1>
        <p class="lead text-muted">Manage your active paying members with complete agreement information</p>
    </div>
</div>

<!-- Search and Controls -->
<div class="row mb-4">
    <div class="col-md-8">
        <form method="GET" class="d-flex">
            <input type="text" name="search" class="form-control search-bar me-2" 
                   placeholder="Search members by name, email, or phone..." 
                   value="{{ search }}">
            <button type="submit" class="btn btn-purple">
                <i class="fas fa-search"></i>
            </button>
        </form>
    </div>
    <div class="col-md-4 text-end">
        <a href="/member/new" class="btn btn-purple">
            <i class="fas fa-plus me-2"></i>Add New Member
        </a>
    </div>
</div>

<!-- Members List -->
<div class="row">
    {% for member in members %}
    <div class="col-12 mb-4">
        <div class="card member-card">
            <div class="card-body">
                <div class="row">
                    <!-- Basic Info -->
                    <div class="col-md-3">
                        <h5 class="text-purple mb-2">
                            <i class="fas fa-user me-2"></i>
                            {{ member.full_name }}
                        </h5>
                        <p class="mb-1">
                            <i class="fas fa-id-card me-2 text-muted"></i>
                            <strong>ID:</strong> {{ member.id }}
                        </p>
                        {% if member.email %}
                        <p class="mb-1">
                            <i class="fas fa-envelope me-2 text-muted"></i>
                            <a href="mailto:{{ member.email }}">{{ member.email }}</a>
                        </p>
                        {% endif %}
                        {% if member.mobile_phone %}
                        <p class="mb-1">
                            <i class="fas fa-phone me-2 text-muted"></i>
                            <a href="tel:{{ member.mobile_phone }}">{{ member.mobile_phone }}</a>
                        </p>
                        {% endif %}
                        <p class="mb-1">
                            <i class="fas fa-calendar me-2 text-muted"></i>
                            <strong>Since:</strong> {{ member.membership_start or 'N/A' }}
                        </p>
                    </div>
                    
                    <!-- Address & Club Info -->
                    <div class="col-md-3">
                        <h6 class="text-purple mb-2">
                            <i class="fas fa-map-marker-alt me-2"></i>Address
                        </h6>
                        <p class="mb-1">{{ member.address1 or 'N/A' }}</p>
                        {% if member.address2 %}
                        <p class="mb-1">{{ member.address2 }}</p>
                        {% endif %}
                        <p class="mb-1">{{ member.city or 'N/A' }}, {{ member.state or 'N/A' }} {{ member.zip_code or '' }}</p>
                        
                        {% if member.home_club_name %}
                        <h6 class="text-purple mb-2 mt-3">
                            <i class="fas fa-building me-2"></i>Home Club
                        </h6>
                        <p class="mb-1"><strong>{{ member.home_club_name }}</strong></p>
                        <p class="mb-1">{{ member.home_club_address or '' }}</p>
                        <p class="mb-1">{{ member.home_club_city or '' }}, {{ member.home_club_state or '' }} {{ member.home_club_zip or '' }}</p>
                        {% endif %}
                    </div>
                    
                    <!-- Agreement Info -->
                    <div class="col-md-3">
                        {% if member.agreement_id %}
                        <div class="agreement-info">
                            <h6 class="text-purple mb-2">
                                <i class="fas fa-file-contract me-2"></i>Agreement
                            </h6>
                            <p class="mb-1"><strong>ID:</strong> {{ member.agreement_id }}</p>
                            {% if member.agreement_status %}
                            <p class="mb-1"><strong>Status:</strong> 
                                <span class="badge bg-success">{{ member.agreement_status }}</span>
                            </p>
                            {% endif %}
                            {% if member.agreement_start_date %}
                            <p class="mb-1"><strong>Start:</strong> {{ member.agreement_start_date }}</p>
                            {% endif %}
                            {% if member.agreement_end_date %}
                            <p class="mb-1"><strong>End:</strong> {{ member.agreement_end_date }}</p>
                            {% endif %}
                            {% if member.agreement_rate %}
                            <p class="mb-1"><strong>Rate:</strong> ${{ member.agreement_rate }}</p>
                            {% endif %}
                            {% if member.agreement_history_count and member.agreement_history_count > 0 %}
                            <p class="mb-1"><strong>History:</strong> {{ member.agreement_history_count }} agreements</p>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>
                    
                    <!-- Payment Info -->
                    <div class="col-md-3">
                        {% if member.payment_token or member.card_type %}
                        <div class="payment-info">
                            <h6 class="text-purple mb-2">
                                <i class="fas fa-credit-card me-2"></i>Payment
                            </h6>
                            {% if member.card_type %}
                            <p class="mb-1"><strong>Card:</strong> {{ member.card_type }}</p>
                            {% endif %}
                            {% if member.card_last4 %}
                            <p class="mb-1"><strong>Last 4:</strong> ****{{ member.card_last4 }}</p>
                            {% endif %}
                            {% if member.expiration_month and member.expiration_year %}
                            <p class="mb-1"><strong>Expires:</strong> {{ member.expiration_month }}/{{ member.expiration_year }}</p>
                            {% endif %}
                            {% if member.billing_name %}
                            <p class="mb-1"><strong>Billing Name:</strong> {{ member.billing_name }}</p>
                            {% endif %}
                            {% if member.account_type %}
                            <p class="mb-1"><strong>Account Type:</strong> {{ member.account_type }}</p>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Expandable Details -->
                <div class="row mt-3">
                    <div class="col-12">
                        <button class="btn btn-outline-purple btn-sm" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#details-{{ member.id }}" 
                                aria-expanded="false">
                            <i class="fas fa-info-circle me-2"></i>More Details
                        </button>
                        <a href="/member/{{ member.id }}" class="btn btn-purple btn-sm ms-2">
                            <i class="fas fa-eye me-2"></i>Full Profile
                        </a>
                    </div>
                </div>
                
                <div class="collapse mt-3" id="details-{{ member.id }}">
                    <div class="row">
                        <!-- Personal Details -->
                        <div class="col-md-4">
                            <div class="contact-info">
                                <h6 class="text-purple mb-2">
                                    <i class="fas fa-user-circle me-2"></i>Personal Details
                                </h6>
                                {% if member.date_of_birth %}
                                <p class="mb-1"><strong>DOB:</strong> {{ member.date_of_birth }}</p>
                                {% endif %}
                                {% if member.gender %}
                                <p class="mb-1"><strong>Gender:</strong> {{ member.gender }}</p>
                                {% endif %}
                                {% if member.emergency_contact %}
                                <p class="mb-1"><strong>Emergency:</strong> {{ member.emergency_contact }}</p>
                                {% endif %}
                                {% if member.emergency_phone %}
                                <p class="mb-1"><strong>Emergency Phone:</strong> {{ member.emergency_phone }}</p>
                                {% endif %}
                                {% if member.employer %}
                                <p class="mb-1"><strong>Employer:</strong> {{ member.employer }}</p>
                                {% endif %}
                                {% if member.occupation %}
                                <p class="mb-1"><strong>Occupation:</strong> {{ member.occupation }}</p>
                                {% endif %}
                            </div>
                        </div>
                        
                        <!-- Membership Details -->
                        <div class="col-md-4">
                            <div class="agreement-info">
                                <h6 class="text-purple mb-2">
                                    <i class="fas fa-id-badge me-2"></i>Membership Details
                                </h6>
                                {% if member.key_fob %}
                                <p class="mb-1"><strong>Key Fob:</strong> {{ member.key_fob }}</p>
                                {% endif %}
                                {% if member.last_visit %}
                                <p class="mb-1"><strong>Last Visit:</strong> {{ member.last_visit }}</p>
                                {% endif %}
                                {% if member.user_type %}
                                <p class="mb-1"><strong>Type:</strong> {{ member.user_type }}</p>
                                {% endif %}
                                {% if member.status_message %}
                                <p class="mb-1"><strong>Status:</strong> {{ member.status_message }}</p>
                                {% endif %}
                                <p class="mb-1"><strong>Has App:</strong> 
                                    <span class="badge bg-{{ 'success' if member.has_app else 'secondary' }}">
                                        {{ 'Yes' if member.has_app else 'No' }}
                                    </span>
                                </p>
                                {% if member.trial %}
                                <p class="mb-1"><strong>Trial Member:</strong> 
                                    <span class="badge bg-warning">Yes</span>
                                </p>
                                {% endif %}
                            </div>
                        </div>
                        
                        <!-- System Info -->
                        <div class="col-md-4">
                            <div class="contact-info">
                                <h6 class="text-purple mb-2">
                                    <i class="fas fa-cogs me-2"></i>System Info
                                </h6>
                                {% if member.guid %}
                                <p class="mb-1"><strong>GUID:</strong> <small>{{ member.guid }}</small></p>
                                {% endif %}
                                {% if member.source %}
                                <p class="mb-1"><strong>Source:</strong> {{ member.source }}</p>
                                {% endif %}
                                {% if member.rating %}
                                <p class="mb-1"><strong>Rating:</strong> {{ member.rating }}/5</p>
                                {% endif %}
                                {% if member.bucket %}
                                <p class="mb-1"><strong>Bucket:</strong> {{ member.bucket }}</p>
                                {% endif %}
                                {% if member.last_activity_timestamp %}
                                <p class="mb-1"><strong>Last Activity:</strong> {{ member.last_activity_timestamp }}</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <div class="card">
            <div class="card-body text-center py-5">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No members found</h5>
                {% if search %}
                <p class="text-muted">Try adjusting your search criteria.</p>
                <a href="/members" class="btn btn-purple">Show All Members</a>
                {% else %}
                <p class="text-muted">Get started by adding your first member.</p>
                <a href="/member/new" class="btn btn-purple">Add Member</a>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Pagination -->
{% if total_pages > 1 %}
<div class="row mt-4">
    <div class="col-12">
        <nav aria-label="Members pagination">
            <ul class="pagination justify-content-center">
                {% if has_prev %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
                {% endif %}
                
                {% for p in range(1, total_pages + 1) %}
                    {% if p == page %}
                    <li class="page-item active">
                        <span class="page-link">{{ p }}</span>
                    </li>
                    {% elif p <= 5 or p > total_pages - 5 or (p >= page - 2 and p <= page + 2) %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ p }}{% if search %}&search={{ search }}{% endif %}">{{ p }}</a>
                    </li>
                    {% elif p == 6 or p == total_pages - 5 %}
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                    {% endif %}
                {% endfor %}
                
                {% if has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
                {% endif %}
            </ul>
        </nav>
        
        <div class="text-center text-muted">
            Showing {{ ((page - 1) * per_page) + 1 }} to {{ min(page * per_page, total_members) }} of {{ total_members }} members
        </div>
    </div>
</div>
{% endif %}
{% endblock %}'''
    
    with open(f'{templates_dir}/members.html', 'w') as f:
        f.write(members_template)
    
    # Prospects template
    prospects_template = '''{% extends "base.html" %}

{% block title %}Prospects - Anytime Fitness Management{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="text-purple mb-3">
            <i class="fas fa-user-plus me-2"></i>
            Prospects
            <span class="badge badge-purple ms-3">{{ total_prospects }} Total</span>
        </h1>
        <p class="lead text-muted">Manage your potential members and track their journey to membership</p>
    </div>
</div>

<!-- Search and Controls -->
<div class="row mb-4">
    <div class="col-md-8">
        <form method="GET" class="d-flex">
            <input type="text" name="search" class="form-control search-bar me-2" 
                   placeholder="Search prospects by name, email, or phone..." 
                   value="{{ search }}">
            <button type="submit" class="btn btn-purple">
                <i class="fas fa-search"></i>
            </button>
        </form>
    </div>
    <div class="col-md-4 text-end">
        <a href="/prospect/new" class="btn btn-purple">
            <i class="fas fa-plus me-2"></i>Add New Prospect
        </a>
    </div>
</div>

<!-- Prospects List -->
<div class="row">
    {% for prospect in prospects %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card prospect-card h-100">
            <div class="card-body">
                <h5 class="text-purple mb-2">
                    <i class="fas fa-user-plus me-2"></i>
                    {{ prospect.full_name }}
                </h5>
                
                <!-- Contact Info -->
                <div class="contact-info mb-3">
                    <p class="mb-1">
                        <i class="fas fa-id-card me-2 text-muted"></i>
                        <strong>ID:</strong> {{ prospect.id }}
                    </p>
                    {% if prospect.email %}
                    <p class="mb-1">
                        <i class="fas fa-envelope me-2 text-muted"></i>
                        <a href="mailto:{{ prospect.email }}">{{ prospect.email }}</a>
                    </p>
                    {% endif %}
                    {% if prospect.mobile_phone %}
                    <p class="mb-1">
                        <i class="fas fa-phone me-2 text-muted"></i>
                        <a href="tel:{{ prospect.mobile_phone }}">{{ prospect.mobile_phone }}</a>
                    </p>
                    {% endif %}
                    {% if prospect.address1 %}
                    <p class="mb-1">
                        <i class="fas fa-map-marker-alt me-2 text-muted"></i>
                        {{ prospect.address1 }}, {{ prospect.city or '' }}, {{ prospect.state or '' }}
                    </p>
                    {% endif %}
                </div>
                
                <!-- Prospect-specific Info -->
                <div class="agreement-info mb-3">
                    {% if prospect.lead_source %}
                    <p class="mb-1">
                        <i class="fas fa-source me-2 text-muted"></i>
                        <strong>Source:</strong> {{ prospect.lead_source }}
                    </p>
                    {% endif %}
                    {% if prospect.interest_level %}
                    <p class="mb-1">
                        <i class="fas fa-star me-2 text-muted"></i>
                        <strong>Interest:</strong> {{ prospect.interest_level }}/5
                    </p>
                    {% endif %}
                    {% if prospect.trial %}
                    <p class="mb-1">
                        <i class="fas fa-dumbbell me-2 text-muted"></i>
                        <span class="badge bg-warning">Trial Interested</span>
                    </p>
                    {% endif %}
                    {% if prospect.tour_completed %}
                    <p class="mb-1">
                        <i class="fas fa-check-circle me-2 text-success"></i>
                        <span class="badge bg-success">Tour Completed</span>
                    </p>
                    {% endif %}
                </div>
                
                <!-- Status and Actions -->
                <div class="d-flex justify-content-between align-items-center">
                    {% if prospect.status %}
                    <span class="badge bg-info">{{ prospect.status }}</span>
                    {% else %}
                    <span class="badge bg-secondary">New Lead</span>
                    {% endif %}
                    
                    <div>
                        <a href="/prospect/{{ prospect.id }}" class="btn btn-sm btn-purple">
                            <i class="fas fa-eye"></i>
                        </a>
                        <button class="btn btn-sm btn-outline-purple ms-1" 
                                data-bs-toggle="modal" 
                                data-bs-target="#followUpModal{{ prospect.id }}">
                            <i class="fas fa-calendar"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Follow-up info -->
                {% if prospect.follow_up_date %}
                <div class="mt-2">
                    <small class="text-muted">
                        <i class="fas fa-calendar-alt me-1"></i>
                        Follow-up: {{ prospect.follow_up_date }}
                    </small>
                </div>
                {% endif %}
                
                <!-- Expandable Details -->
                <div class="mt-3">
                    <button class="btn btn-outline-purple btn-sm w-100" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#details-{{ prospect.id }}" 
                            aria-expanded="false">
                        <i class="fas fa-info-circle me-2"></i>More Details
                    </button>
                </div>
                
                <div class="collapse mt-3" id="details-{{ prospect.id }}">
                    {% if prospect.date_of_birth %}
                    <p class="mb-1"><strong>DOB:</strong> {{ prospect.date_of_birth }}</p>
                    {% endif %}
                    {% if prospect.gender %}
                    <p class="mb-1"><strong>Gender:</strong> {{ prospect.gender }}</p>
                    {% endif %}
                    {% if prospect.preferred_contact_method %}
                    <p class="mb-1"><strong>Preferred Contact:</strong> {{ prospect.preferred_contact_method }}</p>
                    {% endif %}
                    {% if prospect.best_time_to_call %}
                    <p class="mb-1"><strong>Best Time to Call:</strong> {{ prospect.best_time_to_call }}</p>
                    {% endif %}
                    {% if prospect.trial_session_date %}
                    <p class="mb-1"><strong>Trial Session:</strong> {{ prospect.trial_session_date }}</p>
                    {% endif %}
                    {% if prospect.notes %}
                    <p class="mb-1"><strong>Notes:</strong> {{ prospect.notes }}</p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Follow-up Modal -->
        <div class="modal fade" id="followUpModal{{ prospect.id }}" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Schedule Follow-up for {{ prospect.full_name }}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form>
                            <div class="mb-3">
                                <label class="form-label">Follow-up Date</label>
                                <input type="date" class="form-control" name="follow_up_date">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Notes</label>
                                <textarea class="form-control" name="notes" rows="3"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-purple">Schedule</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <div class="card">
            <div class="card-body text-center py-5">
                <i class="fas fa-user-plus fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No prospects found</h5>
                {% if search %}
                <p class="text-muted">Try adjusting your search criteria.</p>
                <a href="/prospects" class="btn btn-purple">Show All Prospects</a>
                {% else %}
                <p class="text-muted">Get started by adding your first prospect.</p>
                <a href="/prospect/new" class="btn btn-purple">Add Prospect</a>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Pagination -->
{% if total_pages > 1 %}
<div class="row mt-4">
    <div class="col-12">
        <nav aria-label="Prospects pagination">
            <ul class="pagination justify-content-center">
                {% if has_prev %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
                {% endif %}
                
                {% for p in range(1, total_pages + 1) %}
                    {% if p == page %}
                    <li class="page-item active">
                        <span class="page-link">{{ p }}</span>
                    </li>
                    {% elif p <= 5 or p > total_pages - 5 or (p >= page - 2 and p <= page + 2) %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ p }}{% if search %}&search={{ search }}{% endif %}">{{ p }}</a>
                    </li>
                    {% elif p == 6 or p == total_pages - 5 %}
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                    {% endif %}
                {% endfor %}
                
                {% if has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
                {% endif %}
            </ul>
        </nav>
        
        <div class="text-center text-muted">
            Showing {{ ((page - 1) * per_page) + 1 }} to {{ min(page * per_page, total_prospects) }} of {{ total_prospects }} prospects
        </div>
    </div>
</div>
{% endif %}
{% endblock %}'''
    
    with open(f'{templates_dir}/prospects.html', 'w') as f:
        f.write(prospects_template)
    
    # Member detail template
    member_detail_template = '''{% extends "base.html" %}

{% block title %}{{ member.full_name }} - Member Details{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="text-purple">
                <i class="fas fa-user me-2"></i>
                {{ member.full_name }}
                <span class="badge badge-purple ms-3">Member ID: {{ member.id }}</span>
            </h1>
            <a href="/members" class="btn btn-outline-purple">
                <i class="fas fa-arrow-left me-2"></i>Back to Members
            </a>
        </div>
    </div>
</div>

<!-- Quick Stats -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-id-card fa-2x text-purple mb-2"></i>
                <h5>Member Status</h5>
                <span class="badge bg-success">{{ member.status or 'Active' }}</span>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-calendar fa-2x text-purple mb-2"></i>
                <h5>Join Date</h5>
                <p class="mb-0">{{ member.join_date or 'N/A' }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-credit-card fa-2x text-purple mb-2"></i>
                <h5>Payment Type</h5>
                <p class="mb-0">{{ member.card_type or 'N/A' }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-home fa-2x text-purple mb-2"></i>
                <h5>Home Club</h5>
                <p class="mb-0">{{ member.home_club_name or 'N/A' }}</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Contact Information -->
    <div class="col-md-6 mb-4">
        <div class="card h-100">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-address-book me-2"></i>Contact Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-12 mb-3">
                        <strong>Full Name:</strong> {{ member.full_name }}
                    </div>
                    {% if member.email %}
                    <div class="col-12 mb-3">
                        <strong>Email:</strong> 
                        <a href="mailto:{{ member.email }}">{{ member.email }}</a>
                    </div>
                    {% endif %}
                    {% if member.mobile_phone %}
                    <div class="col-12 mb-3">
                        <strong>Mobile:</strong> 
                        <a href="tel:{{ member.mobile_phone }}">{{ member.mobile_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.home_phone %}
                    <div class="col-12 mb-3">
                        <strong>Home Phone:</strong> 
                        <a href="tel:{{ member.home_phone }}">{{ member.home_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.work_phone %}
                    <div class="col-12 mb-3">
                        <strong>Work Phone:</strong> 
                        <a href="tel:{{ member.work_phone }}">{{ member.work_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.address1 %}
                    <div class="col-12 mb-3">
                        <strong>Address:</strong><br>
                        {{ member.address1 }}<br>
                        {% if member.address2 %}{{ member.address2 }}<br>{% endif %}
                        {{ member.city or '' }}, {{ member.state or '' }} {{ member.zip_code or '' }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- Personal Information -->
    <div class="col-md-6 mb-4">
        <div class="card h-100">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-user me-2"></i>Personal Information
                </h5>
            </div>
            <div class="card-body">
                {% if member.date_of_birth %}
                <div class="mb-3">
                    <strong>Date of Birth:</strong> {{ member.date_of_birth }}
                </div>
                {% endif %}
                {% if member.gender %}
                <div class="mb-3">
                    <strong>Gender:</strong> {{ member.gender }}
                </div>
                {% endif %}
                {% if member.emergency_contact_name %}
                <div class="mb-3">
                    <strong>Emergency Contact:</strong> {{ member.emergency_contact_name }}
                    {% if member.emergency_contact_phone %}
                    <br><small class="text-muted">{{ member.emergency_contact_phone }}</small>
                    {% endif %}
                </div>
                {% endif %}
                {% if member.preferred_contact_method %}
                <div class="mb-3">
                    <strong>Preferred Contact:</strong> {{ member.preferred_contact_method }}
                </div>
                {% endif %}
                {% if member.referral_source %}
                <div class="mb-3">
                    <strong>Referral Source:</strong> {{ member.referral_source }}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Agreement Information -->
{% if member.agreement_id %}
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-file-contract me-2"></i>Agreement Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <strong>Agreement ID:</strong> {{ member.agreement_id }}
                    </div>
                    {% if member.agreement_status %}
                    <div class="col-md-4 mb-3">
                        <strong>Status:</strong> 
                        <span class="badge bg-success">{{ member.agreement_status }}</span>
                    </div>
                    {% endif %}
                    {% if member.agreement_type %}
                    <div class="col-md-4 mb-3">
                        <strong>Type:</strong> {{ member.agreement_type }}
                    </div>
                    {% endif %}
                    {% if member.start_date %}
                    <div class="col-md-4 mb-3">
                        <strong>Start Date:</strong> {{ member.start_date }}
                    </div>
                    {% endif %}
                    {% if member.end_date %}
                    <div class="col-md-4 mb-3">
                        <strong>End Date:</strong> {{ member.end_date }}
                    </div>
                    {% endif %}
                    {% if member.monthly_amount %}
                    <div class="col-md-4 mb-3">
                        <strong>Monthly Amount:</strong> ${{ member.monthly_amount }}
                    </div>
                    {% endif %}
                    {% if member.billing_frequency %}
                    <div class="col-md-4 mb-3">
                        <strong>Billing Frequency:</strong> {{ member.billing_frequency }}
                    </div>
                    {% endif %}
                    {% if member.next_billing_date %}
                    <div class="col-md-4 mb-3">
                        <strong>Next Billing:</strong> {{ member.next_billing_date }}
                    </div>
                    {% endif %}
                    {% if member.auto_renew %}
                    <div class="col-md-4 mb-3">
                        <strong>Auto Renew:</strong> 
                        <span class="badge bg-{{ 'success' if member.auto_renew == 'true' else 'warning' }}">
                            {{ 'Yes' if member.auto_renew == 'true' else 'No' }}
                        </span>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Payment Information -->
{% if member.payment_token %}
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-credit-card me-2"></i>Payment Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% if member.card_type %}
                    <div class="col-md-3 mb-3">
                        <strong>Card Type:</strong> {{ member.card_type }}
                    </div>
                    {% endif %}
                    {% if member.card_last_four %}
                    <div class="col-md-3 mb-3">
                        <strong>Last 4 Digits:</strong> •••• {{ member.card_last_four }}
                    </div>
                    {% endif %}
                    {% if member.card_exp_month and member.card_exp_year %}
                    <div class="col-md-3 mb-3">
                        <strong>Expiration:</strong> {{ member.card_exp_month }}/{{ member.card_exp_year }}
                    </div>
                    {% endif %}
                    {% if member.billing_name %}
                    <div class="col-md-3 mb-3">
                        <strong>Billing Name:</strong> {{ member.billing_name }}
                    </div>
                    {% endif %}
                    {% if member.billing_address1 %}
                    <div class="col-12 mb-3">
                        <strong>Billing Address:</strong><br>
                        {{ member.billing_address1 }}<br>
                        {% if member.billing_address2 %}{{ member.billing_address2 }}<br>{% endif %}
                        {{ member.billing_city or '' }}, {{ member.billing_state or '' }} {{ member.billing_zip_code or '' }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Home Club Information -->
{% if member.home_club_name %}
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-home me-2"></i>Home Club Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <strong>Club Name:</strong> {{ member.home_club_name }}
                    </div>
                    {% if member.home_club_id %}
                    <div class="col-md-6 mb-3">
                        <strong>Club ID:</strong> {{ member.home_club_id }}
                    </div>
                    {% endif %}
                    {% if member.home_club_phone %}
                    <div class="col-md-6 mb-3">
                        <strong>Club Phone:</strong> 
                        <a href="tel:{{ member.home_club_phone }}">{{ member.home_club_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.home_club_address1 %}
                    <div class="col-12 mb-3">
                        <strong>Club Address:</strong><br>
                        {{ member.home_club_address1 }}<br>
                        {% if member.home_club_address2 %}{{ member.home_club_address2 }}<br>{% endif %}
                        {{ member.home_club_city or '' }}, {{ member.home_club_state or '' }} {{ member.home_club_zip_code or '' }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Action Buttons -->
<div class="row mt-4">
    <div class="col-12 text-center">
        <a href="/member/{{ member.id }}/edit" class="btn btn-purple me-2">
            <i class="fas fa-edit me-2"></i>Edit Member
        </a>
        <button class="btn btn-outline-purple me-2" data-bs-toggle="modal" data-bs-target="#messageModal">
            <i class="fas fa-envelope me-2"></i>Send Message
        </button>
        <a href="/member/{{ member.id }}/agreements" class="btn btn-outline-purple">
            <i class="fas fa-file-contract me-2"></i>View All Agreements
        </a>
    </div>
</div>

<!-- Message Modal -->
<div class="modal fade" id="messageModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Send Message to {{ member.full_name }}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form>
                    <div class="mb-3">
                        <label class="form-label">Message Type</label>
                        <select class="form-select" name="message_type">
                            <option value="email">Email</option>
                            <option value="sms">SMS</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Subject</label>
                        <input type="text" class="form-control" name="subject">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Message</label>
                        <textarea class="form-control" name="message" rows="5"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-purple">Send Message</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/member_detail.html', 'w') as f:
        f.write(member_detail_template)
    
    print(f"Enhanced dashboard created with complete member/prospect separation!")
    print(f"Templates created: base.html, index.html, members.html, prospects.html, member_detail.html")
    print(f"Database tables: members (with full agreement data), prospects")
    print(f"Features: Member agreement display, payment info, home club data, search, pagination")

if __name__ == "__main__":
    # Templates already exist - don't overwrite our custom designs!
    # create_templates()  # DISABLED - prevents overwriting our beautiful Outlook-inspired templates
    # Then run the app
    app.run(debug=True, host='0.0.0.0', port=5001)
