#!/usr/bin/env python3
"""
Message History Service
Fetches member message history from ClubOS for AI context
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
from src.services.authentication.unified_auth_service import get_unified_auth_service

logger = logging.getLogger(__name__)

class MessageHistoryService:
    """
    Service to fetch member message history from ClubOS FollowUp endpoint
    """
    
    def __init__(self):
        self.base_url = "https://anytime.club-os.com"
        self.auth_service = get_unified_auth_service()
        self.secrets_manager = SecureSecretsManager()
        
    def get_member_message_history(self, member_id: str, follow_up_type: str = "3") -> List[Dict[str, Any]]:
        """
        Fetch message history for a specific member from ClubOS
        
        Args:
            member_id: The ClubOS internal member ID (e.g., "125814441")
            follow_up_type: Type of follow-up (3 = general messaging thread)
            
        Returns:
            List of message dictionaries with timestamp, sender, content, type
        """
        try:
            # Get authenticated session from unified auth service
            auth_session = self.auth_service.get_session('clubos')
            if not auth_session:
                logger.error("❌ No authenticated session available")
                return []
            
            # Prepare headers with Bearer token and session cookies
            headers = {
                "Authorization": f"Bearer {auth_session.bearer_token}",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"{self.base_url}/action/Dashboard/view"
            }
            
            # Prepare session cookies
            cookies = {
                "JSESSIONID": auth_session.session_id,
                "loggedInUserId": auth_session.logged_in_user_id,
                "delegatedUserId": auth_session.delegated_user_id or auth_session.logged_in_user_id
            }
            
            # Prepare payload
            payload = {
                "followUpUserId": member_id,
                "followUpType": follow_up_type
            }
            
            logger.info(f"🔍 Fetching message history for member {member_id}")
            
            # Send POST request to ClubOS FollowUp endpoint
            response = requests.post(
                f"{self.base_url}/action/FollowUp",
                headers=headers,
                cookies=cookies,
                data=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch message history: {response.status_code}")
                return []
            
            # Parse HTML response
            messages = self._parse_message_history_html(response.text)
            
            logger.info(f"✅ Retrieved {len(messages)} messages for member {member_id}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error fetching message history for member {member_id}: {e}")
            return []
    
    def _parse_message_history_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse ClubOS HTML response to extract message history
        
        Args:
            html_content: Raw HTML from ClubOS FollowUp endpoint
            
        Returns:
            List of parsed message dictionaries
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            messages = []
            
            # ClubOS typically returns messages in divs or table rows
            # We need to inspect the actual HTML structure, but here's a common pattern
            
            # Look for message containers - adjust selectors based on actual ClubOS HTML
            message_containers = soup.find_all(['div', 'tr'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['message', 'followup', 'thread', 'item']
            ))
            
            if not message_containers:
                # Fallback: look for any divs that might contain message data
                message_containers = soup.find_all('div', string=lambda text: text and len(text.strip()) > 10)
            
            for container in message_containers:
                message_data = self._extract_message_data(container)
                if message_data:
                    messages.append(message_data)
            
            # If no structured messages found, try to extract from raw text
            if not messages:
                messages = self._extract_messages_from_text(html_content)
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error parsing message history HTML: {e}")
            return []
    
    def _extract_message_data(self, container) -> Optional[Dict[str, Any]]:
        """
        Extract message data from a single container element
        
        Args:
            container: BeautifulSoup element containing message data
            
        Returns:
            Dictionary with message data or None if invalid
        """
        try:
            text_content = container.get_text(strip=True)
            
            # Skip empty or very short content
            if len(text_content) < 10:
                return None
            
            # Try to extract timestamp (common patterns)
            timestamp = None
            sender = "Unknown"
            message_type = "Unknown"
            content = text_content
            
            # Look for timestamp patterns
            import re
            timestamp_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2})', text_content)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
            
            # Look for sender patterns
            sender_match = re.search(r'by\s+([A-Za-z\s.]+)', text_content)
            if sender_match:
                sender = sender_match.group(1).strip()
            
            # Look for message type patterns
            if 'Auto-SMS' in text_content:
                message_type = 'Auto-SMS'
            elif 'Text' in text_content:
                message_type = 'Text'
            elif 'Email' in text_content:
                message_type = 'Email'
            elif 'Gym Bot' in text_content:
                message_type = 'Bot'
            
            return {
                'timestamp': timestamp,
                'sender': sender,
                'type': message_type,
                'content': content,
                'raw_html': str(container)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting message data: {e}")
            return None
    
    def _extract_messages_from_text(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Fallback method to extract messages from raw HTML text
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            List of message dictionaries
        """
        try:
            messages = []
            
            # Split content by common delimiters and extract meaningful chunks
            lines = html_content.split('\n')
            current_message = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # If line looks like a message (contains common patterns)
                if any(keyword in line.lower() for keyword in ['by ', 'message', 'sms', 'email', 'bot']):
                    if current_message:
                        messages.append({
                            'timestamp': None,
                            'sender': 'Unknown',
                            'type': 'Unknown',
                            'content': current_message.strip(),
                            'raw_html': current_message
                        })
                    current_message = line
                else:
                    current_message += " " + line
            
            # Add final message
            if current_message:
                messages.append({
                    'timestamp': None,
                    'sender': 'Unknown',
                    'type': 'Unknown',
                    'content': current_message.strip(),
                    'raw_html': current_message
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Error extracting messages from text: {e}")
            return []
    
    def get_formatted_message_history(self, member_id: str) -> Dict[str, Any]:
        """
        Get formatted message history for display in dashboard
        
        Args:
            member_id: ClubOS member ID
            
        Returns:
            Formatted data for dashboard display
        """
        try:
            messages = self.get_member_message_history(member_id)
            
            # Format for dashboard display
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    'id': f"{member_id}_{len(formatted_messages)}",
                    'timestamp': msg.get('timestamp', 'Unknown'),
                    'sender': msg.get('sender', 'Unknown'),
                    'type': msg.get('type', 'Unknown'),
                    'content': msg.get('content', ''),
                    'is_bot': 'bot' in msg.get('type', '').lower(),
                    'is_system': 'system' in msg.get('sender', '').lower()
                }
                formatted_messages.append(formatted_msg)
            
            return {
                'member_id': member_id,
                'total_messages': len(formatted_messages),
                'messages': formatted_messages,
                'last_updated': datetime.now().isoformat(),
                'has_messages': len(formatted_messages) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error formatting message history for member {member_id}: {e}")
            return {
                'member_id': member_id,
                'total_messages': 0,
                'messages': [],
                'last_updated': datetime.now().isoformat(),
                'has_messages': False,
                'error': str(e)
            }
