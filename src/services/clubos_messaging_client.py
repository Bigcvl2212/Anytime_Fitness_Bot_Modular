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
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        
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
            login_url = f"{self.base_url}/action/Login/view?__fsk=1221801756"
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
            
            # Step 3: Extract session information from cookies
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            delegated_user_id = self.session.cookies.get('delegatedUserId')
            
            if not session_id or not logged_in_user_id:
                logger.error("Authentication failed - missing session cookies")
                return False
            
            self.authenticated = True
            logger.info(f"Authentication successful - User ID: {logged_in_user_id}")
            return True
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_messages(self, owner_id: str = "187032782") -> List[Dict]:
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
    
    def send_sms_message(self, member_id: str, message: str) -> bool:
        """Send SMS message using working form submission"""
        try:
            if not self.authenticated and not self.authenticate():
                return False
            
            logger.info(f"📱 Sending SMS to member {member_id}")
            
            form_data = {
                "followUpStatus": "1",
                "followUpType": "3", 
                "memberSalesFollowUpStatus": "6",
                "followUpLog.tfoUserId": member_id,
                "followUpLog.outcome": "3",
                "textMessage": message,
                "event.createdFor.tfoUserId": member_id,
                "event.eventType": "ORIENTATION",
                "duration": "2",
                "event.remindAttendeesMins": "120",
                "followUpUser.tfoUserId": member_id,
                "followUpUser.role.id": "7",
                "followUpUser.clubId": "291",
                "followUpUser.clubLocationId": "3586",
                "followUpLog.followUpAction": "3",
                "memberStudioSalesDefaultAccount": member_id,
                "memberStudioSupportDefaultAccount": member_id,
                "ptSalesDefaultAccount": member_id,
                "ptSupportDefaultAccount": member_id
            }
            
            return self._submit_message_form(form_data)
            
        except Exception as e:
            logger.error(f"❌ Error sending SMS: {e}")
            return False
    
    def send_email_message(self, member_id: str, subject: str, message: str) -> bool:
        """Send email message using working form submission"""
        try:
            if not self.authenticated and not self.authenticate():
                return False
            
            logger.info(f"📧 Sending email to member {member_id}")
            
            form_data = {
                "followUpStatus": "1",
                "followUpType": "3",
                "memberSalesFollowUpStatus": "6", 
                "followUpLog.tfoUserId": member_id,
                "followUpLog.outcome": "2",
                "emailSubject": subject,
                "emailMessage": f"<p>{message}</p>",
                "event.createdFor.tfoUserId": member_id,
                "event.eventType": "ORIENTATION",
                "duration": "2",
                "event.remindAttendeesMins": "120",
                "followUpUser.tfoUserId": member_id,
                "followUpUser.role.id": "7",
                "followUpUser.clubId": "291", 
                "followUpUser.clubLocationId": "3586",
                "followUpLog.followUpAction": "2",
                "memberStudioSalesDefaultAccount": member_id,
                "memberStudioSupportDefaultAccount": member_id,
                "ptSalesDefaultAccount": member_id,
                "ptSupportDefaultAccount": member_id
            }
            
            return self._submit_message_form(form_data)
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    def _submit_message_form(self, form_data: Dict) -> bool:
        """Submit message form to ClubOS using working endpoint"""
        try:
            follow_up_url = f"{self.base_url}/action/FollowUp/save"
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view",
                "Origin": self.base_url
            }
            
            # Convert form data to URL encoded format
            encoded_data = urllib.parse.urlencode(form_data)
            
            response = self.session.post(follow_up_url, data=encoded_data, headers=headers)
            
            if response.status_code == 200:
                logger.info("✅ Message sent successfully")
                return True
            else:
                logger.error(f"❌ Message sending failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error submitting message form: {e}")
            return False
    
    def sync_messages(self, owner_id: str = "187032782") -> List[Dict]:
        """Public method used by app to fetch and return messages for caching.
        Wraps get_messages to keep a stable API surface for callers.
        """
        try:
            return self.get_messages(owner_id=owner_id) or []
        except Exception as e:
            logger.error(f"❌ sync_messages failed: {e}")
            return []
    def send_bulk_campaign(self, member_ids: List[str], message: str, message_type: str = "sms", subject: str = "") -> Dict[str, Any]:
        """Send bulk message campaign to multiple members"""
        try:
            logger.info(f"📢 Starting bulk campaign to {len(member_ids)} members")
            
            results = {
                "total": len(member_ids),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for member_id in member_ids:
                try:
                    if message_type.lower() == "sms":
                        success = self.send_sms_message(member_id, message)
                    else:
                        success = self.send_email_message(member_id, subject, message)
                    
                    if success:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to send to member {member_id}")
                        
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Error sending to member {member_id}: {str(e)}")
            
            logger.info(f"✅ Bulk campaign completed: {results['successful']}/{results['total']} successful")
            return results
            
        except Exception as e:
            logger.error(f"❌ Bulk campaign error: {e}")
            return {"total": 0, "successful": 0, "failed": 0, "errors": [str(e)]}
