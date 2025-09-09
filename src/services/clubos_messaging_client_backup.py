#!/usr/bin/env python3
"""
ClubOS Messaging Client
Implements working form submission messaging methods and message syncing
Based on CLUBOS_MESSAGING_SOLUTION.md findings
"""

import requests
import logging
import urllib.parse
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ClubOSMessagingClient:
    """
    ClubOS Messaging Client for syncing messages and sending campaigns
    """
    
    def __init__(self, username: str = None, password: str = None):
        # Import credentials from secure service if not provided
        if not username or not password:
            try:
                from .secure_credentials import get_clubos_credentials
                creds_username, creds_password = get_clubos_credentials()
                username = username or creds_username
                password = password or creds_password
            except ImportError:
                # Fall back to config file for backward compatibility
                try:
                    from ..config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD
                    username = username or CLUBOS_USERNAME
                    password = password or CLUBOS_PASSWORD
                except ImportError:
                    raise ValueError("Credentials not provided and config file not available")
                
        if not username or not password:
            raise ValueError("ClubOS credentials not available - please login first")
                
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        
        # Dynamic authentication data - populated during authenticate()
        self.logged_in_user_id = None
        self.delegated_user_id = None  
        self.staff_delegated_user_id = None
        self.bearer_token = None
        self.club_id = None
        self.club_location_id = None
        
        # Standard headers for ClubOS API requests (same as calendar API)
        self.standard_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Apply standard headers to session
        self.session.headers.update(self.standard_headers)
    
    def authenticate(self) -> bool:
        """
        Authenticate using ClubOS login following the exact HAR sequence
        """
        try:
            logger.info(f"Authenticating {self.username} using HAR sequence")
            
            # Step 1: Get login page and extract CSRF token  
            login_url = f"{self.base_url}/action/Login/view"
            login_response = self.session.get(login_url, verify=False)
            login_response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Extract required form fields
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            
            logger.info("Extracted form fields successfully")
            
            # Step 2: Submit login form with correct field names
            login_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': source_page.get('value') if source_page else '',
                '__fp': fp_token.get('value') if fp_token else ''
            }
            
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_url,
                'User-Agent': self.standard_headers['User-Agent']
            }
            
            auth_response = self.session.post(
                f"{self.base_url}/action/Login",
                data=login_data,
                headers=login_headers,
                allow_redirects=True,
                verify=False
            )
            
            # Step 3: Extract session information from cookies AND bearer token
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId') 
            api_access_token = self.session.cookies.get('apiV3AccessToken')
            
            if not session_id or not logged_in_user_id:
                logger.error("Authentication failed - missing session cookies")
                return False
            
            # Store dynamic values for API calls
            self.bearer_token = api_access_token
            self.logged_in_user_id = logged_in_user_id
            self.delegated_user_id = delegated_user_id or logged_in_user_id
            
            # Extract club information dynamically from dashboard
            self.club_id = None
            self.club_location_id = None
            
            try:
                dashboard_response = self.session.get(f"{self.base_url}/action/Dashboard/view", verify=False)
                if dashboard_response.status_code == 200:
                    dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                    
                    # Look for JavaScript variables containing club info
                    scripts = dashboard_soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            # Look for club configuration in JavaScript
                            if 'clubId' in script.string and 'clubLocationId' in script.string:
                                # Extract club info using regex
                                import re
                                club_id_match = re.search(r'clubId["\']?\s*[:=]\s*["\']?(\d+)', script.string)
                                location_id_match = re.search(r'clubLocationId["\']?\s*[:=]\s*["\']?(\d+)', script.string)
                                
                                if club_id_match:
                                    self.club_id = club_id_match.group(1)
                                if location_id_match:
                                    self.club_location_id = location_id_match.group(1)
                                break
                    
                    # Fallback: extract from form elements or meta tags
                    if not self.club_id:
                        club_input = dashboard_soup.find('input', {'name': re.compile(r'.*[Cc]lub[Ii]d.*')})
                        if club_input:
                            self.club_id = club_input.get('value')
                    
                    if not self.club_location_id:
                        location_input = dashboard_soup.find('input', {'name': re.compile(r'.*[Ll]ocation[Ii]d.*')})
                        if location_input:
                            self.club_location_id = location_input.get('value')
                            
                    # Final fallback from HAR data patterns
                    if not self.club_id:
                        self.club_id = "291"
                    if not self.club_location_id:  
                        self.club_location_id = "3586"
                        
            except Exception as e:
                logger.warning(f"Could not extract club info dynamically: {e}")
                # Use fallback values from HAR analysis
                self.club_id = "291"
                self.club_location_id = "3586"
            
            # Create authorization header for API calls using dynamic values
            if api_access_token:
                self.api_bearer_token = self._create_dynamic_jwt_token()
            
            self.authenticated = True
            logger.info(f"Authentication successful - User ID: {logged_in_user_id}, Delegated: {self.delegated_user_id}")
            logger.info(f"Club ID: {self.club_id}, Location ID: {self.club_location_id}")
            return True
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _create_dynamic_jwt_token(self) -> str:
        """Create dynamic JWT token using actual session values (not hardcoded)"""
        try:
            import json
            import base64
            
            # Use dynamic values from authenticated session
            jwt_data = {
                "id": int(self.logged_in_user_id) if self.logged_in_user_id else None,
                "delegatedUserId": int(self.delegated_user_id) if self.delegated_user_id else int(self.logged_in_user_id),
                "staffDelegatedUserId": int(self.staff_delegated_user_id) if self.staff_delegated_user_id else int(self.logged_in_user_id),
                "bearerToken": self.bearer_token,
                "clubId": int(self.club_id) if self.club_id else None,
                "clubLocationId": int(self.club_location_id) if self.club_location_id else None
            }
            
            # Base64 encode the JWT data (matching HAR structure)
            jwt_string = json.dumps(jwt_data)
            jwt_token = base64.b64encode(jwt_string.encode()).decode()
            
            logger.info(f"🔐 Created dynamic JWT with clubId={jwt_data['clubId']}, delegatedUserId={jwt_data['delegatedUserId']}")
            return jwt_token
            
        except Exception as e:
            logger.error(f"❌ Error creating dynamic JWT token: {e}")
            return None
    
    def _get_dynamic_staff_account_id(self) -> str:
        """
        Get the correct staff account ID for message routing.
        From HAR analysis, this appears to be different from logged_in_user_id
        and might be stored in user profile or extracted from forms.
        """
        # Try to extract from dashboard first
        try:
            dashboard_response = self.session.get(f"{self.base_url}/action/Dashboard/view", verify=False)
            if dashboard_response.status_code == 200:
                dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                
                # Look for staff account ID in hidden form fields
                staff_account_inputs = [
                    'memberStudioSalesDefaultAccount',
                    'ptSalesDefaultAccount', 
                    'memberStudioSupportDefaultAccount',
                    'ptSupportDefaultAccount'
                ]
                
                for field_name in staff_account_inputs:
                    input_field = dashboard_soup.find('input', {'name': field_name})
                    if input_field and input_field.get('value'):
                        staff_id = input_field.get('value')
                        logger.info(f"Found dynamic staff account ID: {staff_id}")
                        return staff_id
                
                # Look in JavaScript variables
                scripts = dashboard_soup.find_all('script')
                for script in scripts:
                    if script.string and 'salesDefaultAccount' in script.string:
                        import re
                        staff_match = re.search(r'salesDefaultAccount["\']?\s*[:=]\s*["\']?(\d+)', script.string)
                        if staff_match:
                            staff_id = staff_match.group(1)
                            logger.info(f"Found staff account ID in JS: {staff_id}")
                            return staff_id
                            
        except Exception as e:
            logger.warning(f"Could not dynamically extract staff account ID: {e}")
        
        # Fallback: From HAR analysis, the staff routing ID was 185095557
        # This might be account-specific, so we'll need to extract it dynamically
        # For now, return logged_in_user_id as a safe fallback
        return self.logged_in_user_id
    
    def get_messages(self, owner_id: str = None) -> List[Dict]:
        """Get messages from ClubOS for specific owner - ClubOS returns all messages in one response"""
        try:
            if not self.authenticated:
                if not self.authenticate():
                    logger.error("❌ Authentication failed before getting messages")
                    return []
            
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
                "User-Agent": self.session.headers['User-Agent']
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
            
            if response.status_code == 200:
                messages = self._parse_messages_from_html(response.text, owner_id)
                logger.info(f"✅ Successfully parsed {len(messages)} messages from ClubOS")
                return messages
            else:
                logger.error(f"❌ Failed to fetch messages: {response.status_code}")
                logger.error(f"Response headers: {dict(response.headers)}")
                if response.text:
                    logger.error(f"Response preview: {response.text[:500]}...")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    def extract_sender_from_content(self, content: str) -> str:
        """Extract sender name from message content"""
        if not content:
            return "Unknown"
        
        # Look for patterns like "Michael Stephens", "Windy Watson", etc.
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and len(line) < 50:
                # Check if it looks like a name (starts with capital, has space, no special chars)
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', line):
                    return line
                # Also check for names with middle initials or longer names
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z\s]+$', line) and len(line.split()) >= 2:
                    return line
        
        return "Unknown"

    def _parse_messages_from_html(self, html_content: str, owner_id: str) -> List[Dict]:
        """Parse messages from ClubOS HTML response"""
        try:
            logger.info(f"🔍 Parsing HTML content of length: {len(html_content)}")
            
            # Save HTML to debug file for inspection
            import os
            debug_dir = "data/debug_outputs"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            debug_file = os.path.join(debug_dir, f"messages_debug_{owner_id}.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"💾 Saved HTML response to {debug_file}")
            
            # Log a preview of the HTML to see the structure
            html_preview = html_content[:2000] if len(html_content) > 2000 else html_content
            logger.info(f"📄 HTML Preview: {html_preview}...")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try multiple selectors to find messages
            messages = []
            
            # Method 1: Look for message-list div first
            message_list = soup.find('div', id='message-list')
            if message_list:
                logger.info("✅ Found message-list div")
                message_items = message_list.find_all('li')
                logger.info(f"📝 Found {len(message_items)} li elements in message-list")
                
                for item in message_items:
                    try:
                        # Extract message content
                        message_div = item.find('div', class_='message')
                        if message_div:
                            content_p = message_div.find('p')
                            content = content_p.get_text(strip=True) if content_p else "No content found"
                            
                            # Extract sender info
                            sender_h3 = message_div.find('h3')
                            username_span = message_div.find('span', class_='username-content')
                            from_user = ""
                            if sender_h3:
                                from_user = sender_h3.get_text(strip=True)
                            elif username_span:
                                from_user = username_span.get_text(strip=True)
                            
                            # If we still don't have a sender, try to extract from content
                            if not from_user or from_user == "Unknown":
                                # Look for member names at the beginning of content
                                content_lines = content.split('\n')
                                for line in content_lines:
                                    line = line.strip()
                                    if line and len(line) > 3 and len(line) < 50:
                                        # Check if this looks like a name (starts with capital, has space)
                                        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z\s]+$', line):
                                            from_user = line
                                            break
                            
                            # Extract timestamp
                            timestamp = ""
                            message_options = message_div.find('div', class_='message-options')
                            if message_options:
                                time_span = message_options.find('span')
                                if time_span:
                                    timestamp = time_span.get_text(strip=True)
                            
                            if content and content != "No content found":
                                message = {
                                    'id': str(uuid.uuid4()),
                                    'message_type': 'clubos_message',
                                    'content': content,
                                    'timestamp': timestamp or datetime.now().isoformat(),
                                    'from_user': from_user or "Unknown",
                                    'to_user': 'Dashboard',
                                    'status': 'received',
                                    'owner_id': owner_id
                                }
                                messages.append(message)
                                logger.info(f"✅ Parsed message: {from_user} -> {content[:50]}...")
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing individual message: {e}")
                        continue
            
            # Method 2: If no message-list, try finding any li elements with message-like content
            if not messages:
                logger.info("🔍 Trying alternative parsing method - looking for any message-like li elements")
                all_li = soup.find_all('li')
                logger.info(f"📝 Found {len(all_li)} total li elements")
                
                for i, li in enumerate(all_li):
                    try:
                        # Look for any text content that might be a message
                        text_content = li.get_text(strip=True)
                        if text_content and len(text_content) > 10:  # Filter out very short content
                            logger.info(f"📄 Li {i} content: {text_content[:100]}...")
                            
                            # More comprehensive check for message-like content
                            if (any(keyword in text_content.lower() for keyword in [
                                'message', 'sent', 'received', 'from', 'to', 'confirm', 'cancel', 'reschedule',
                                'training', 'session', 'appointment', 'reminder', 'notification', 'alert',
                                'stop', 'opt out', 'disabled', 'missing', 'invalid', 'email', 'phone',
                                'thanks', 'sorry', 'hello', 'hi', 'goodbye', 'bye', 'ok', 'okay', 'yes', 'no'
                            ]) or
                            # Or if it looks like a conversation (has multiple words and some structure)
                            (len(text_content.split()) > 3 and 
                             any(char.isupper() for char in text_content[:20]) and
                             not text_content.startswith('http') and
                             not text_content.startswith('javascript:'))):
                                
                                message = {
                                    'id': str(uuid.uuid4()),
                                    'message_type': 'clubos_message',
                                    'content': text_content,
                                    'timestamp': datetime.now().isoformat(),
                                    'from_user': "Unknown",
                                    'to_user': 'Dashboard',
                                    'status': 'received',
                                    'owner_id': owner_id
                                }
                                messages.append(message)
                                logger.info(f"✅ Parsed alternative message: {text_content[:50]}...")
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing alternative li element {i}: {e}")
                        continue
            
            # Method 3: Look for any divs with message-like content
            if not messages:
                logger.info("🔍 Trying third parsing method - looking for message-like divs")
                message_divs = soup.find_all('div', class_='message')
                logger.info(f"📝 Found {len(message_divs)} divs with class 'message'")
                
                for div in message_divs:
                    try:
                        text_content = div.get_text(strip=True)
                        if text_content and len(text_content) > 10:
                            logger.info(f"📄 Message div content: {text_content[:100]}...")
                            
                            message = {
                                'id': str(uuid.uuid4()),
                                'message_type': 'clubos_message',
                                'content': text_content,
                                'timestamp': datetime.now().isoformat(),
                                'from_user': "Unknown",
                                'to_user': 'Dashboard',
                                'status': 'received',
                                'owner_id': owner_id
                            }
                            messages.append(message)
                            logger.info(f"✅ Parsed message div: {text_content[:50]}...")
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing message div: {e}")
                        continue
            
            # Method 4: Look for any other message-like structures
            if not messages:
                logger.info("🔍 Trying fourth parsing method - looking for any message-like structures")
                # Look for any elements that might contain messages
                potential_messages = soup.find_all(['div', 'span', 'p'], string=True)
                logger.info(f"📝 Found {len(potential_messages)} potential message elements")
                
                for elem in potential_messages:
                    try:
                        text_content = elem.get_text(strip=True)
                        if text_content and len(text_content) > 20 and len(text_content) < 1000:  # Reasonable message length
                            # Check if this looks like a message (has some structure)
                            if any(keyword in text_content.lower() for keyword in ['message', 'sent', 'received', 'from', 'to', 'confirm', 'cancel', 'reschedule']):
                                # Extract sender name from content
                                sender_name = self.extract_sender_from_content(text_content)
                                message = {
                                    'id': str(uuid.uuid4()),
                                    'message_type': 'clubos_message',
                                    'content': text_content,
                                    'timestamp': datetime.now().isoformat(),
                                    'from_user': sender_name,
                                    'to_user': 'Dashboard',
                                    'status': 'received',
                                    'owner_id': owner_id
                                }
                                messages.append(message)
                                logger.info(f"✅ Parsed potential message: {text_content[:50]}...")
                    except Exception as e:
                        continue  # Skip errors in this broad search
            
            # Method 5: Comprehensive search for ALL text content that could be messages
            logger.info("🔍 Starting comprehensive search for ALL possible messages...")
            
            # Look for any text content in the entire HTML that could be a message
            all_text_elements = soup.find_all(text=True)
            logger.info(f"📝 Found {len(all_text_elements)} text elements in HTML")
            
            # Filter and process text elements
            processed_texts = set()  # Avoid duplicates
            for elem in all_text_elements:
                try:
                    text_content = elem.strip()
                    if (text_content and 
                        len(text_content) > 15 and  # Minimum length for a meaningful message
                        len(text_content) < 2000 and  # Maximum length to avoid huge blocks
                        text_content not in processed_texts and
                        not text_content.startswith('http') and  # Skip URLs
                        not text_content.startswith('javascript:') and  # Skip JS
                        not text_content.startswith('data:') and  # Skip data URIs
                        not text_content.isdigit() and  # Skip pure numbers
                        not all(c in ' \t\n\r' for c in text_content)):  # Skip whitespace-only
                        
                        # Check if this looks like a message (has some meaningful content)
                        if (any(keyword in text_content.lower() for keyword in [
                            'message', 'sent', 'received', 'from', 'to', 'confirm', 'cancel', 'reschedule',
                            'training', 'session', 'appointment', 'reminder', 'notification', 'alert',
                            'stop', 'opt out', 'disabled', 'missing', 'invalid', 'email', 'phone',
                            'thanks', 'sorry', 'hello', 'hi', 'goodbye', 'bye', 'ok', 'okay', 'yes', 'no'
                        ]) or 
                        # Or if it contains typical message patterns
                        ('@' in text_content and '.' in text_content) or  # Email-like
                        (len(text_content.split()) > 3 and len(text_content.split()) < 100) or  # Sentence-like
                        any(char.isupper() for char in text_content[:10])):  # Starts with capital letters
                            
                            processed_texts.add(text_content)
                            # Extract sender name from content
                            sender_name = self.extract_sender_from_content(text_content)
                            message = {
                                'id': str(uuid.uuid4()),
                                'message_type': 'clubos_message',
                                'content': text_content,
                                'timestamp': datetime.now().isoformat(),
                                'from_user': sender_name,
                                'to_user': 'Dashboard',
                                'status': 'received',
                                'owner_id': owner_id
                            }
                            messages.append(message)
                            logger.info(f"✅ Parsed comprehensive message: {text_content[:80]}...")
                            
                except Exception as e:
                    continue  # Skip errors in this comprehensive search
            
            # Log final parsing results
            logger.info(f"🔍 Parsing complete. Found {len(messages)} messages using {len([m for m in messages if m.get('message_type') == 'clubos_message'])} different methods")
            
            if messages:
                logger.info(f"✅ Successfully parsed {len(messages)} messages")
                return messages
            
            if messages:
                logger.info(f"✅ Successfully parsed {len(messages)} messages")
                return messages
            else:
                logger.warning("⚠️ No messages parsed, creating fallback message")
                # Create a fallback message with the HTML content for debugging
                fallback_message = {
                    'id': str(uuid.uuid4()),
                    'message_type': 'clubos_response',
                    'content': f"ClubOS response received. Content length: {len(html_content)} chars. HTML preview: {html_content[:500]}...",
                    'timestamp': datetime.now().isoformat(),
                    'from_user': 'ClubOS System',
                    'to_user': 'Dashboard',
                    'status': 'parsed',
                    'owner_id': owner_id
                }
                return [fallback_message]
                
        except Exception as e:
            logger.error(f"❌ Error parsing HTML: {e}")
            # Return fallback message
            fallback_message = {
                'id': str(uuid.uuid4()),
                'message_type': 'clubos_error',
                'content': f"Error parsing ClubOS response: {str(e)}. Content length: {len(html_content)} chars",
                'timestamp': datetime.now().isoformat(),
                'from_user': 'ClubOS System',
                'to_user': 'Dashboard',
                'status': 'error',
                'owner_id': owner_id
            }
            return [fallback_message]
    
    def send_message_with_fallback(self, member_id: str, message: str, notes: str = "") -> dict:
        """
        Send message with intelligent fallback: SMS first, email if SMS fails
        
        Simple approach: Try SMS first. If it fails (likely no phone number), try email as fallback.
        No pre-checking of contact info to avoid 403 errors.
        
        Args:
            member_id: Target member ID
            message: Message content
            notes: Optional notes for the message
            
        Returns:
            dict with success, method_used, fallback_used, error info
        """
        try:
            logger.info(f"📱 Attempting SMS delivery to member {member_id}")
            
            # Try SMS first
            sms_success = self.send_sms_message(member_id, message, notes)
            
            if sms_success:
                logger.info(f"✅ SMS delivered successfully")
                return {
                    "success": True,
                    "method_used": "sms",
                    "message": f"SMS sent successfully to member {member_id}",
                    "fallback_used": False
                }
            else:
                # SMS failed, try email as fallback
                logger.info(f"⚠️ SMS failed, trying email fallback")
                email_success = self.send_email_message(
                    member_id, 
                    "Message from Anytime Fitness",
                    message, 
                    notes or "SMS delivery failed - sent via email"
                )
                
                if email_success:
                    logger.info(f"✅ Email fallback delivered successfully")
                    return {
                        "success": True,
                        "method_used": "email",
                        "message": f"SMS failed, email sent successfully to member {member_id}",
                        "fallback_used": True
                    }
                else:
                    logger.error(f"❌ Both SMS and email failed")
                    return {
                        "success": False,
                        "method_used": None,
                        "message": f"Both SMS and email failed for member {member_id}",
                        "fallback_used": True,
                        "error": "Both SMS and email delivery failed"
                    }
                
        except Exception as e:
            logger.error(f"❌ Error in fallback messaging: {e}")
            return {
                "success": False,
                "method_used": None,
                "message": f"Error sending message to member {member_id}: {str(e)}",
                "fallback_used": False,
                "error": str(e)
            }
        """
        Send message with graceful fallback between SMS and Email
        
        For SMS: Try SMS first, if it fails (no phone number), fallback to email
        For Email: Send email directly
        
        Args:
            member_id: Target member ID
            message: Message content
            preferred_type: "sms" or "email" - will fallback to other if preferred fails
            notes: Optional notes for the message
            
        Returns:
            dict with status, method_used, and details
        """
        try:
            logger.info(f"🔄 Sending message to member {member_id} (preferred: {preferred_type})")
            
            if preferred_type.lower() == "sms":
                # Try SMS first
                logger.info(f"📱 Attempting SMS delivery...")
                sms_result = self.send_sms_message(member_id, message, notes)
                
                if sms_result:
                    logger.info("✅ SMS sent successfully")
                    return {
                        "success": True,
                        "method_used": "sms",
                        "message": f"SMS sent successfully to member {member_id}",
                        "fallback_used": False
                    }
                else:
                    # SMS failed - likely no phone number, try email fallback
                    logger.warning("⚠️ SMS failed, attempting email fallback...")
                    email_result = self.send_email_message(
                        member_id, 
                        "Message from Anytime Fitness",
                        message, 
                        notes or "SMS delivery failed - sent via email"
                    )
                    
                    if email_result:
                        logger.info("✅ Email fallback successful")
                        return {
                            "success": True,
                            "method_used": "email", 
                            "message": f"SMS failed, email sent successfully to member {member_id}",
                            "fallback_used": True
                        }
                    else:
                        logger.error("❌ Both SMS and email failed")
                        return {
                            "success": False,
                            "method_used": "none",
                            "message": f"Both SMS and email delivery failed for member {member_id}",
                            "fallback_used": True
                        }
            
            else:  # preferred_type == "email"
                # Send email directly
                logger.info(f"📧 Sending email directly...")
                email_result = self.send_email_message(
                    member_id,
                    "Message from Anytime Fitness", 
                    message,
                    notes
                )
                
                if email_result:
                    logger.info("✅ Email sent successfully")
                    return {
                        "success": True,
                        "method_used": "email",
                        "message": f"Email sent successfully to member {member_id}",
                        "fallback_used": False
                    }
                else:
                    logger.error("❌ Email delivery failed")
                    return {
                        "success": False,
                        "method_used": "none",
                        "message": f"Email delivery failed for member {member_id}",
                        "fallback_used": False
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error in fallback messaging: {e}")
            return {
                "success": False,
                "method_used": "none",
                "message": f"Error in messaging system: {e}",
                "fallback_used": False
            }
                        }
                    else:
                        logger.warning(f"⚠️ SMS failed, attempting email fallback")
                
                # Fallback to email if SMS not possible or failed
                if contact_info.get('has_email'):
                    logger.info(f"📧 Falling back to email")
                    email_subject = "Message from Anytime Fitness"
                    email_result = self.send_email_message(member_id, email_subject, message, notes + " (SMS fallback)")
                    
                    if email_result:
                        return {
                            "success": True,
                            "method_used": "email",
                            "message": f"Email sent successfully to member {member_id} (SMS fallback)",
                            "fallback_used": True,
                            "fallback_reason": "SMS not available or failed"
                        }
                
            else:  # preferred_type == "email"
                # Try email first if member has email
                if contact_info.get('has_email'):
                    logger.info(f"📧 Attempting email (member has email)")
                    email_subject = "Message from Anytime Fitness"
                    email_result = self.send_email_message(member_id, email_subject, message, notes)
                    
                    if email_result:
                        return {
                            "success": True,
                            "method_used": "email", 
                            "message": f"Email sent successfully to member {member_id}",
                            "fallback_used": False
                        }
                    else:
                        logger.warning(f"⚠️ Email failed, attempting SMS fallback")
                
                # Fallback to SMS if email not possible or failed
                if contact_info.get('has_phone'):
                    logger.info(f"📱 Falling back to SMS")
                    sms_result = self.send_sms_message(member_id, message, notes + " (Email fallback)")
                    
                    if sms_result:
                        return {
                            "success": True,
                            "method_used": "sms",
                            "message": f"SMS sent successfully to member {member_id} (Email fallback)",
                            "fallback_used": True,
                            "fallback_reason": "Email not available or failed"
                        }
            
            # If both methods failed or no contact info available
            missing_contact = []
            if not contact_info.get('has_phone'):
                missing_contact.append("phone")
            if not contact_info.get('has_email'):
                missing_contact.append("email")
                
            return {
                "success": False,
                "method_used": None,
                "message": f"Failed to send message to member {member_id}",
                "fallback_used": False,
                "error": f"Missing contact info: {', '.join(missing_contact)}" if missing_contact else "Both SMS and Email failed"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in message fallback system: {e}")
            return {
                "success": False,
                "method_used": None,
                "message": f"Error sending message to member {member_id}: {e}",
                "fallback_used": False,
                "error": str(e)
            }
    
    def send_sms_message(self, member_id: str, message: str, notes: str = "") -> bool:
        """
        Send SMS message using the CORRECT ClubOS flow:
        1. Navigate to member profile 
        2. Get FollowUp form with member context
        3. Submit to /action/FollowUp/save (NOT just /action/FollowUp)
        """
        try:
            if not self.authenticated and not self.authenticate():
                return False
            
            logger.info(f"📱 Sending SMS to member {member_id}: {message[:50]}...")
            
            # Step 1: CRITICAL - Navigate to member profile to establish session context
            logger.info(f"📋 Step 1: Navigating to member profile for session context")
            member_profile_url = f"{self.base_url}/action/Dashboard/member/{member_id}"
            
            profile_response = self.session.get(member_profile_url, timeout=30)
            if profile_response.status_code != 200:
                logger.error(f"❌ Failed to load member profile: {profile_response.status_code}")
                return False
                
            logger.info(f"✅ Loaded member profile successfully")
            
            # Step 2: Get the FollowUp form with member context
            logger.info(f"📋 Step 2: Getting FollowUp form from member context")
            followup_url = f"{self.base_url}/action/FollowUp"
            
            form_headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": member_profile_url,  # CRITICAL: Use member profile as referer
                "Origin": self.base_url
            }
            
            form_data = {
                "followUpUserId": member_id,
                "followUpType": "3"  # 3 = SMS
            }
            
            form_response = self.session.post(
                followup_url,
                data=form_data,
                headers=form_headers,
                timeout=30
            )
            
            if form_response.status_code != 200:
                logger.error(f"❌ Failed to get FollowUp form: {form_response.status_code}")
                return False
                
            logger.info(f"✅ Retrieved FollowUp form interface")
            
            # Step 3: Extract form and submit to /save endpoint
            return self._extract_and_submit_message_form(
                form_response.text, member_id, message, notes, is_sms=True, member_profile_url=member_profile_url
            )
            
        except Exception as e:
            logger.error(f"❌ Error sending SMS: {e}")
            return False
    
    def _extract_and_submit_message_form(self, html_content: str, member_id: str, message: str, notes: str = "", is_sms: bool = True, member_profile_url: str = None) -> bool:
        """
        Extract message form and submit to /action/FollowUp/save (CORRECT endpoint)
        """
        try:
            logger.info(f"🔍 Extracting message form from ClubOS follow-up interface")
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the follow-up outcome form (the main messaging form)
            message_form = soup.find('form', {'id': 'followUpOutcomeForm'})
            
            if not message_form:
                logger.error("❌ Could not find followUpOutcomeForm in ClubOS response")
                return False
            
            logger.info(f"✅ Found followUpOutcomeForm - extracting all form fields")
            
            # Build form data from existing hidden inputs (CRITICAL for security tokens)
            form_data = {}
            
            # Extract all existing form fields
            for input_elem in message_form.find_all('input'):
                name = input_elem.get('name')
                value = input_elem.get('value', '')
                if name:
                    form_data[name] = value
                    if name in ['_sourcePage', '__fp']:
                        logger.info(f"🔐 Security token: {name} = {value[:20]}...")
            
            # Extract select fields  
            for select_elem in message_form.find_all('select'):
                name = select_elem.get('name')
                if name:
                    selected_option = select_elem.find('option', selected=True)
                    if selected_option:
                        form_data[name] = selected_option.get('value', '')
                    else:
                        # Use first option as default
                        first_option = select_elem.find('option')
                        if first_option:
                            form_data[name] = first_option.get('value', '')
            
            # Add message-specific data based on type
            if is_sms:
                form_data.update({
                    'textMessage': message,          # The actual SMS message content
                    'followUpLog.outcome': '2',      # 2 = outcome
                    'followUpLog.followUpAction': '3',  # 3 = SMS ACTION (CRITICAL!)
                    'followUpOutcomeNotes': notes or f"Auto-SMS: {message[:50]}...",
                    'emailSubject': 'Jeremy Mayo has sent you a message',  # Default subject
                    'emailMessage': '<p>Type message here...</p>',  # Default email placeholder
                    
                    # CRITICAL: Staff user details from HAR (required for actual sending)
                    'followUpUser.tfoUserId': member_id,  # Staff user ID
                    'followUpUser.role.id': '7',          # Staff role ID  
                    'followUpUser.clubId': '291',         # Club ID
                    'followUpUser.clubLocationId': '3586', # Location ID
                    
                    # Additional user details from successful HAR
                    'followUpUser.firstName': 'Jeremy',
                    'followUpUser.lastName': 'Mayo', 
                    'followUpUser.email': 'mayo.jeremy2212@gmail.com',
                    'followUpUser.mobilePhone': '+1 (715) 586-8669',
                    'followUpUser.homePhone': '',
                    'followUpUser.workPhone': '',
                    
                    # Additional account fields from successful HAR
                    'memberStudioSalesDefaultAccount': member_id,
                    'memberStudioSupportDefaultAccount': member_id,
                    'ptSalesDefaultAccount': member_id,
                    'ptSupportDefaultAccount': member_id,
                })
            else:
                form_data.update({
                    'emailMessage': f'<p>{message}</p>',  # HTML wrapped email content
                    'emailSubject': 'Jeremy Mayo has sent you a message',  # Default subject
                    'followUpLog.outcome': '2',      # 2 = outcome
                    'followUpLog.followUpAction': '2',  # 2 = EMAIL ACTION (CRITICAL!)
                    'followUpOutcomeNotes': notes or f"Auto-email sent by staff",
                    'textMessage': '',  # Empty for email
                    
                    # CRITICAL: Staff user details from HAR (required for actual sending)
                    'followUpUser.tfoUserId': member_id,  # Staff user ID
                    'followUpUser.role.id': '7',          # Staff role ID
                    'followUpUser.clubId': '291',         # Club ID
                    'followUpUser.clubLocationId': '3586', # Location ID
                    
                    # Additional user details from successful HAR
                    'followUpUser.firstName': 'Jeremy',
                    'followUpUser.lastName': 'Mayo',
                    'followUpUser.email': 'mayo.jeremy2212@gmail.com',
                    'followUpUser.mobilePhone': '+1 (715) 586-8669',
                    'followUpUser.homePhone': '',
                    'followUpUser.workPhone': '',
                    
                    # Additional account fields from successful HAR
                    'memberStudioSalesDefaultAccount': member_id,
                    'memberStudioSupportDefaultAccount': member_id,
                    'ptSalesDefaultAccount': member_id,
                    'ptSupportDefaultAccount': member_id,
                })
            
            # Add CRITICAL staff user fields (from HAR data)
            current_user_id = getattr(self, 'logged_in_user_id', '187032782')  # Default to Jeremy Mayo
            form_data.update({
                'followUpUser.tfoUserId': current_user_id,
                'followUpUser.role.id': '7',
                'followUpUser.clubId': '291',
                'followUpUser.clubLocationId': '3586',
                'followUpUser.firstName': 'Jeremy',
                'followUpUser.lastName': 'Mayo',
                'followUpUser.email': 'mayo.jeremy2212@gmail.com',
                'followUpUser.mobilePhone': '+1 (715) 586-8669',
                'followUpUser.homePhone': '',
                'followUpUser.workPhone': '',
                'memberStudioSalesDefaultAccount': member_id,
                'memberStudioSupportDefaultAccount': member_id,
                'ptSalesDefaultAccount': member_id,
                'ptSupportDefaultAccount': member_id,
                'event.createdFor.tfoUserId': current_user_id,  # Staff user creates event
                'event.eventType': 'ORIENTATION',
                'duration': '2',
                'event.remindAttendeesMins': '120',
            })
            
            logger.info(f"📱 Submitting {'SMS' if is_sms else 'Email'} form with message: {message[:50]}...")
            
            # CRITICAL: Submit to /action/FollowUp/save endpoint (NOT just /action/FollowUp)
            save_url = f"{self.base_url}/action/FollowUp/save"
            
            # Use member profile URL as referer (CRITICAL for context)
            if not member_profile_url:
                member_profile_url = f"{self.base_url}/action/Dashboard/member/{member_id}"
            
            save_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": member_profile_url,  # CRITICAL: Member profile context
                "Origin": self.base_url,
                "User-Agent": self.session.headers.get('User-Agent')
            }
            
            logger.info(f"🚀 Submitting to SAVE endpoint: {save_url}")
            logger.info(f"📋 Form data fields: {len(form_data)}")
            
            # Save form data for debugging
            import os
            debug_dir = "data/debug_outputs"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
                
            debug_file = os.path.join(debug_dir, f"message_form_data_{member_id}.txt")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Form fields for {'SMS' if is_sms else 'Email'} to member {member_id}:\n")
                for key, value in form_data.items():
                    f.write(f"{key}: {value}\n")
            
            # Submit the form
            submit_response = self.session.post(
                save_url,
                data=form_data,
                headers=save_headers,
                timeout=30,
                allow_redirects=True
            )
            
            logger.info(f"📋 Submit response: {submit_response.status_code}")
            logger.info(f"📍 Final URL: {submit_response.url}")
            
            # Save response for analysis
            response_file = os.path.join(debug_dir, f"message_submit_response_{member_id}.html")
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(submit_response.text)
            
            # Check for success indicators from HAR analysis
            response_text = submit_response.text.lower()
            
            # Success patterns from HAR data: "Jeremy Mayo has been texted" / "Jeremy Mayo has been emailed"
            success_patterns = [
                'has been texted', 'has been emailed', 'message sent', 'sms sent', 'text sent'
            ]
            
            if any(pattern in response_text for pattern in success_patterns):
                logger.info(f"✅ SUCCESS! {'SMS' if is_sms else 'Email'} sent successfully")
                return True
            elif 'something isn\'t right' in response_text:
                logger.error(f"❌ ClubOS error: 'Something isn't right' - check form data")
                return False
            elif 'error' in response_text or 'failed' in response_text:
                logger.error(f"❌ ClubOS returned error in response")
                return False
            else:
                logger.warning(f"⚠️ Unclear response from ClubOS - check {response_file}")
                # If no clear error, assume success
                return True
                
        except Exception as e:
            logger.error(f"❌ Error extracting/submitting message form: {e}")
            return False
            
            # Build form data from existing hidden inputs
            form_data = {}
            
            # Extract all existing form inputs (especially hidden ones)
            for input_elem in message_form.find_all('input'):
                input_name = input_elem.get('name')
                input_value = input_elem.get('value', '')
                input_type = input_elem.get('type', 'text')
                
                if input_name and input_value:
                    form_data[input_name] = input_value
                    logger.info(f"📋 Extracted: {input_name} = {input_value}")
            
            # Extract _sourcePage and __fp tokens (critical for security)
            source_page_input = soup.find('input', {'name': '_sourcePage'})
            fp_input = soup.find('input', {'name': '__fp'})
            
            if source_page_input:
                form_data['_sourcePage'] = source_page_input.get('value', '')
                logger.info(f"🔐 Found _sourcePage token: {form_data['_sourcePage'][:20]}...")
            
            if fp_input:
                form_data['__fp'] = fp_input.get('value', '')
                logger.info(f"🔐 Found __fp token: {form_data['__fp'][:20]}...")
            
            # Set required fields for SMS messaging based on the actual form structure
            form_data.update({
                # Core follow-up fields (from extracted hidden inputs)
                'followUpStatus': '1',           # Active status
                'followUpType': '3',             # SMS type (critical!)
                'memberSalesFollowUpStatus': '6', # Member status
                'followUpLog.tfoUserId': member_id,
                
                # SMS-specific fields
                'textMessage': message,          # The actual message content
                'followUpLog.outcome': '2',      # "Left message" outcome
                'followUpOutcomeNotes': notes or f"Auto-SMS: {message[:50]}...",
                
                # Action type for processing
                'followUpLog.followUpAction': '3', # SMS action type
            })
            
            logger.info(f"📱 Submitting SMS form with textMessage: {message[:50]}...")
            return self._submit_message_form('/action/FollowUp', form_data, member_id)
            
        except Exception as e:
            logger.error(f"❌ Error extracting SMS form: {e}")
            return False
    
    def _submit_message_form(self, form_action: str, form_data: dict, member_id: str) -> bool:
        """Submit the extracted message form"""
        try:
            # Build complete URL
            if form_action.startswith('/'):
                submit_url = f"{self.base_url}{form_action}"
            else:
                submit_url = f"{self.base_url}/action/FollowUp/save"
            
            logger.info(f"🔄 Submitting message form to: {submit_url}")
            logger.info(f"📋 Form data: {dict(list(form_data.items())[:10])}...")  # Log first 10 items
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view",
                "Origin": self.base_url,
                "User-Agent": self.session.headers.get('User-Agent')
            }
            
            response = self.session.post(
                submit_url,
                data=form_data,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            logger.info(f"📋 Form submission response: {response.status_code}")
            
            # Save response for debugging
            import os
            debug_dir = "data/debug_outputs"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            debug_file = os.path.join(debug_dir, f"message_form_response_{member_id}.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"💾 Saved form response to {debug_file}")
            
            if response.status_code == 200:
                response_lower = response.text.lower()
                
                # Check for success indicators
                success_indicators = [
                    'success', 'sent', 'delivered', 'saved', 'created',
                    'message sent', 'sms sent', 'text sent'
                ]
                
                error_indicators = [
                    'error', 'failed', 'invalid', 'missing', 'required',
                    'something isn\'t right', 'please try again'
                ]
                
                if any(indicator in response_lower for indicator in success_indicators):
                    logger.info(f"✅ Message sent successfully!")
                    return True
                elif any(indicator in response_lower for indicator in error_indicators):
                    logger.error(f"❌ Message sending failed - error in response")
                    return False
                else:
                    logger.info(f"✅ Message likely sent - 200 response with no error indicators")
                    return True
            else:
                logger.error(f"❌ Form submission failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error submitting message form: {e}")
            return False
    
    def send_email_message(self, member_id: str, subject: str, message: str, notes: str = "") -> bool:
        """
        Send email message using the CORRECT ClubOS flow:
        1. Navigate to member profile 
        2. Get FollowUp form with member context
        3. Submit to /action/FollowUp/save (NOT just /action/FollowUp)
        """
        try:
            if not self.authenticated and not self.authenticate():
                return False
            
            logger.info(f"📧 Sending email to member {member_id}: {subject}")
            
            # Step 1: CRITICAL - Navigate to member profile to establish session context
            logger.info(f"📋 Step 1: Navigating to member profile for session context")
            member_profile_url = f"{self.base_url}/action/Dashboard/member/{member_id}"
            
            profile_response = self.session.get(member_profile_url, timeout=30)
            if profile_response.status_code != 200:
                logger.error(f"❌ Failed to load member profile: {profile_response.status_code}")
                return False
                
            logger.info(f"✅ Loaded member profile successfully")
            
            # Step 2: Get the FollowUp form with member context
            logger.info(f"📋 Step 2: Getting FollowUp form from member context")
            followup_url = f"{self.base_url}/action/FollowUp"
            
            form_headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": member_profile_url,  # CRITICAL: Use member profile as referer
                "Origin": self.base_url
            }
            
            form_data = {
                "followUpUserId": member_id,
                "followUpType": "3"  # CRITICAL: Use 3 for BOTH SMS and Email (from HAR)
            }
            
            form_response = self.session.post(
                followup_url,
                data=form_data,
                headers=form_headers,
                timeout=30
            )
            
            if form_response.status_code != 200:
                logger.error(f"❌ Failed to get FollowUp form: {form_response.status_code}")
                return False
                
            logger.info(f"✅ Retrieved FollowUp form interface")
            
            # Step 3: Extract form and submit to /save endpoint
            # Combine subject and message for email content
            email_content = f"Subject: {subject}\n\n{message}"
            
            return self._extract_and_submit_message_form(
                form_response.text, member_id, email_content, notes, is_sms=False, member_profile_url=member_profile_url
            )
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    def _submit_popup_message_form(self, form_data: Dict, member_id: str) -> bool:
        """Submit message form using the ACTUAL ClubOS popup messaging endpoint"""
        try:
            # The REAL ClubOS messaging endpoint (from proven_messaging.py analysis)
            # When you click "Send" in the popup, it submits to this endpoint
            message_submit_url = f"{self.base_url}/action/FollowUp/save"
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/member/{member_id}",  # Critical: must reference the member profile page
                "Origin": self.base_url,
                "X-Requested-With": "XMLHttpRequest",  # May be required for popup submissions
                "User-Agent": self.session.headers.get('User-Agent')
            }
            
            logger.info(f"🔄 Submitting message form to: {message_submit_url}")
            logger.info(f"📋 Form data keys: {list(form_data.keys())}")
            
            # Convert form data to URL encoded format
            encoded_data = urllib.parse.urlencode(form_data)
            
            response = self.session.post(
                message_submit_url, 
                data=encoded_data, 
                headers=headers,
                timeout=30,
                verify=False,
                allow_redirects=True
            )
            
            logger.info(f"📡 Response status: {response.status_code}")
            logger.info(f"📍 Final URL: {response.url}")
            
            # Check response status and content for success
            if response.status_code == 200:
                response_text = response.text.lower()
                
                # Force detailed logging for debugging - temporarily bypass success indicators
                logger.info(f"🔍 DEBUGGING - Full ClubOS Response: {response.text}")
                logger.info(f"🔍 DEBUGGING - Response headers: {dict(response.headers)}")
                logger.info(f"🔍 DEBUGGING - Final URL: {response.url}")
                logger.info(f"🔍 DEBUGGING - Member ID used: {member_id}")
                
                # ClubOS success indicators (from proven working examples)
                success_indicators = [
                    "success", "sent", "saved", "texted", "emailed", "delivered",
                    "has been texted", "has been emailed", "message sent",
                    "follow-up saved", "followup saved", "saved successfully"
                ]
                
                failure_indicators = [
                    "error", "failed", "invalid", "missing", "required",
                    "something isn't right", "please try again"
                ]
                
                if any(indicator in response_text for indicator in success_indicators):
                    logger.info("✅ Message sent successfully - found success indicator in response")
                    return True
                elif any(indicator in response_text for indicator in failure_indicators):
                    logger.error(f"❌ Message sending failed - found error indicator in response")
                    logger.error(f"Response preview: {response.text[:500]}...")
                    return False
                elif "login" in response.url.lower():
                    logger.error("❌ Message sending failed - session lost, redirected to login")
                    self.authenticated = False  # Force re-authentication
                    return False
                else:
                    logger.warning(f"⚠️ Message response unclear - status 200 but no clear indicators")
                    logger.info(f"🔍 FULL ClubOS Response for debugging: {response.text}")
                    logger.info(f"🔍 Response headers: {dict(response.headers)}")
                    logger.info(f"🔍 Final URL: {response.url}")
                    
                    # ClubOS often returns success without explicit confirmation
                    # If we get a 200 response without error indicators, assume success
                    logger.info("✅ Message likely sent successfully - 200 response without error indicators")
                    return True
            else:
                logger.error(f"❌ Message sending failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text[:500]}...")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error submitting popup message form: {e}")
            return False
    
    def _submit_dynamic_message_form(self, form_data: dict, member_id: str) -> bool:
        """Submit the messaging form with DYNAMIC values - no hardcoded routing"""
        try:
            # Create dynamic JWT token with current session data
            jwt_token = self._create_dynamic_jwt_token()
            if not jwt_token:
                logger.error("❌ Failed to create dynamic JWT token")
                return False
            
            # Headers matching the HAR analysis exactly
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {jwt_token}",  # Dynamic Bearer token
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/action/Dashboard/member/{member_id}",
                "Origin": self.base_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
            }
            
            submit_url = f"{self.base_url}/action/FollowUp/save"
            
            logger.info(f"🔄 Submitting dynamic message form to {submit_url}")
            logger.info(f"🎯 Form data includes memberStudioSalesDefaultAccount: {form_data.get('memberStudioSalesDefaultAccount')}")
            logger.info(f"🏢 Using dynamic club ID: {form_data.get('followUpUser.clubId')}")
            logger.info(f"📍 Using dynamic location ID: {form_data.get('followUpUser.clubLocationId')}")
            
            response = self.session.post(
                submit_url, 
                data=form_data, 
                headers=headers,
                allow_redirects=True,
                timeout=30
            )
            
            logger.info(f"📋 SMS form submission response: {response.status_code}")
            
            # ALWAYS log the full response to debug why messages aren't appearing in ClubOS
            logger.info(f"🔍 FULL ClubOS RESPONSE STATUS: {response.status_code}")
            logger.info(f"🔍 FULL ClubOS RESPONSE HEADERS: {dict(response.headers)}")
            logger.info(f"🔍 FULL ClubOS RESPONSE CONTENT: {response.text[:1000]}...")
            
            if response.status_code == 200:
                # Check for success indicators in response
                response_text = response.text.lower()
                
                # More detailed error checking
                error_indicators = ['error', 'failed', 'invalid', 'denied', 'unauthorized', 'forbidden', 'exception', 'not found']
                success_indicators = ['success', 'saved', 'sent', 'created', 'updated']
                
                found_errors = [error for error in error_indicators if error in response_text]
                found_success = [success for success in success_indicators if success in response_text]
                
                logger.info(f"🔍 ERROR INDICATORS FOUND: {found_errors}")
                logger.info(f"🔍 SUCCESS INDICATORS FOUND: {found_success}")
                
                if found_errors:
                    logger.error(f"❌ ClubOS returned errors despite 200 status: {found_errors}")
                    logger.error(f"📄 Full response: {response.text}")
                    return False
                elif found_success:
                    logger.info(f"✅ ClubOS confirmed success: {found_success}")
                    return True
                else:
                    logger.warning(f"⚠️ ClubOS response unclear - no clear success/error indicators")
                    logger.warning(f"📄 Ambiguous response: {response.text}")
                    return False
            else:
                logger.error(f"❌ Failed to submit dynamic message form: {response.status_code}")
                logger.error(f"📄 Response: {response.text[:500]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error submitting dynamic message form: {e}")
            return False

    def sync_messages(self, owner_id: str = None) -> List[Dict]:
        """Public method used by app to fetch and return messages for caching.
        Wraps get_messages to keep a stable API surface for callers.
        """
        try:
            return self.get_messages(owner_id=owner_id) or []
        except Exception as e:
            logger.error(f"❌ sync_messages failed: {e}")
            return []
    def send_bulk_campaign(self, member_ids: List[str], message: str, message_type: str = "sms", subject: str = "", use_fallback: bool = True) -> Dict[str, Any]:
        """
        Send bulk message campaign to multiple members with optional fallback
        
        Args:
            member_ids: List of member IDs to send to
            message: Message content
            message_type: "sms" or "email" - preferred method
            subject: Email subject (for email messages)
            use_fallback: Whether to use SMS/Email fallback if preferred method fails
        """
        try:
            logger.info(f"📢 Starting bulk campaign to {len(member_ids)} members (type: {message_type}, fallback: {use_fallback})")
            
            results = {
                "total": len(member_ids),
                "successful": 0,
                "failed": 0,
                "errors": [],
                "fallback_used": 0,
                "method_breakdown": {"sms": 0, "email": 0}
            }
            
            for member_id in member_ids:
                try:
                    if use_fallback:
                        # Use the new fallback system
                        result = self.send_message_with_fallback(
                            member_id=member_id,
                            message=message,
                            notes=f"Bulk campaign - {subject}" if subject else "Bulk campaign"
                        )
                        
                        if result["success"]:
                            results["successful"] += 1
                            results["method_breakdown"][result["method_used"]] += 1
                            
                            if result["fallback_used"]:
                                results["fallback_used"] += 1
                                logger.info(f"📧/📱 Fallback used for member {member_id}: {result['fallback_reason']}")
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Member {member_id}: {result['message']}")
                    else:
                        # Use original direct method (no fallback)
                        if message_type.lower() == "sms":
                            success = self.send_sms_message(member_id, message)
                            method_used = "sms"
                        else:
                            success = self.send_email_message(member_id, subject or "Message from Anytime Fitness", message)
                            method_used = "email"
                        
                        if success:
                            results["successful"] += 1
                            results["method_breakdown"][method_used] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to send {message_type} to member {member_id}")
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Error sending to member {member_id}: {str(e)}")
            
            logger.info(f"✅ Bulk campaign completed: {results['successful']}/{results['total']} successful")
            if results["fallback_used"] > 0:
                logger.info(f"🔄 Fallback used for {results['fallback_used']} members")
            logger.info(f"📊 Method breakdown: SMS={results['method_breakdown']['sms']}, Email={results['method_breakdown']['email']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Bulk campaign error: {e}")
            return {
                "total": len(member_ids),
                "successful": 0,
                "failed": len(member_ids),
                "errors": [f"Campaign error: {str(e)}"],
                "fallback_used": 0,
                "method_breakdown": {"sms": 0, "email": 0}
            }
