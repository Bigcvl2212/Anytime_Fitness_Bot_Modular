#!/usr/bin/env python3
"""
ClubOS Inbox Parser Service
Parses HTML responses from ClubOS /action/Dashboard/messages endpoint
Extracts message metadata for real-time inbox synchronization
"""

import logging
import re
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ClubOSInboxParser:
    """
    Parses ClubOS inbox HTML to extract message metadata
    Designed to work with the /action/Dashboard/messages endpoint
    """

    def __init__(self):
        """Initialize the inbox parser"""
        self.logger = logging.getLogger(__name__)

    def parse_inbox_html(self, html_content: str, owner_id: str = None) -> List[Dict]:
        """
        Parse inbox list HTML from ClubOS /action/Dashboard/messages endpoint

        Args:
            html_content: Raw HTML response from ClubOS
            owner_id: Optional owner ID for tracking

        Returns:
            List of message dictionaries with metadata
        """
        try:
            self.logger.info(f"🔍 Parsing inbox HTML (length: {len(html_content)})")

            soup = BeautifulSoup(html_content, 'html.parser')
            messages = []

            # Method 1: Look for message-list div (most common structure)
            message_list = soup.find('div', id='message-list')
            if message_list:
                messages.extend(self._parse_message_list(message_list, owner_id))

            # Method 2: Look for individual message containers
            if not messages:
                message_containers = soup.find_all('div', class_='message-container')
                if message_containers:
                    messages.extend(self._parse_message_containers(message_containers, owner_id))

            # Method 3: Look for list items that contain messages
            if not messages:
                message_items = soup.find_all('li', class_='message-item')
                if message_items:
                    messages.extend(self._parse_message_items(message_items, owner_id))

            # Method 4: Fallback - look for any message-like structure
            if not messages:
                messages.extend(self._parse_generic_messages(soup, owner_id))

            self.logger.info(f"✅ Parsed {len(messages)} messages from inbox HTML")
            return messages

        except Exception as e:
            self.logger.error(f"❌ Error parsing inbox HTML: {e}")
            return []

    def _parse_message_list(self, message_list_element, owner_id: str = None) -> List[Dict]:
        """Parse messages from message-list div structure"""
        messages = []

        try:
            message_items = message_list_element.find_all('li')
            self.logger.info(f"📝 Found {len(message_items)} message items in message-list")

            for item in message_items:
                try:
                    message_data = self._extract_message_data(item)
                    if message_data:
                        message_data['owner_id'] = owner_id
                        messages.append(message_data)
                except Exception as e:
                    self.logger.warning(f"⚠️ Error parsing message item: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"❌ Error parsing message list: {e}")

        return messages

    def _parse_message_containers(self, containers, owner_id: str = None) -> List[Dict]:
        """Parse messages from message-container div structure"""
        messages = []

        for container in containers:
            try:
                message_data = self._extract_message_data(container)
                if message_data:
                    message_data['owner_id'] = owner_id
                    messages.append(message_data)
            except Exception as e:
                self.logger.warning(f"⚠️ Error parsing message container: {e}")
                continue

        return messages

    def _parse_message_items(self, items, owner_id: str = None) -> List[Dict]:
        """Parse messages from li.message-item structure"""
        messages = []

        for item in items:
            try:
                message_data = self._extract_message_data(item)
                if message_data:
                    message_data['owner_id'] = owner_id
                    messages.append(message_data)
            except Exception as e:
                self.logger.warning(f"⚠️ Error parsing message item: {e}")
                continue

        return messages

    def _parse_generic_messages(self, soup, owner_id: str = None) -> List[Dict]:
        """Fallback: Parse any message-like structures"""
        messages = []

        try:
            # Look for elements with message-related classes or IDs
            potential_messages = soup.find_all(['div', 'li'],
                                              class_=re.compile(r'message|inbox|conversation', re.I))

            for element in potential_messages:
                try:
                    message_data = self._extract_message_data(element)
                    if message_data:
                        message_data['owner_id'] = owner_id
                        messages.append(message_data)
                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"⚠️ Error in generic message parsing: {e}")

        return messages

    def _extract_message_data(self, element) -> Optional[Dict]:
        """
        Extract message metadata from a BeautifulSoup element

        Returns:
            Dictionary with message metadata or None if extraction fails
        """
        try:
            # Extract sender name
            sender_name = self._extract_sender(element)
            if not sender_name or sender_name == "Unknown":
                return None

            # Extract message snippet/preview
            message_snippet = self._extract_snippet(element)
            if not message_snippet:
                return None

            # Extract timestamp
            timestamp = self._extract_timestamp(element)

            # Extract member/user ID if available
            member_id = self._extract_member_id(element)

            # Extract read/unread status
            is_read = self._extract_read_status(element)

            # Generate unique message ID
            message_id = self._generate_message_id(sender_name, message_snippet, timestamp)

            return {
                'id': message_id,
                'message_type': 'inbox_message',
                'sender_name': sender_name,
                'sender_id': member_id,
                'snippet': message_snippet,
                'timestamp': timestamp,
                'is_read': is_read,
                'status': 'received',
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.debug(f"Could not extract message data from element: {e}")
            return None

    def _extract_sender(self, element) -> str:
        """Extract sender name from message element"""
        # Try multiple selector patterns
        selectors = [
            ('h3', None),
            ('span', 'sender-name'),
            ('div', 'message-sender'),
            ('span', 'username-content'),
            ('strong', None),
        ]

        for tag, class_name in selectors:
            if class_name:
                sender_elem = element.find(tag, class_=class_name)
            else:
                sender_elem = element.find(tag)

            if sender_elem:
                sender_name = sender_elem.get_text(strip=True)
                if sender_name and len(sender_name) > 0:
                    return sender_name

        # Try to extract from data attributes
        if element.has_attr('data-sender'):
            return element['data-sender']

        return "Unknown"

    def _extract_snippet(self, element) -> str:
        """Extract message snippet/preview from element"""
        # Try multiple selector patterns
        selectors = [
            ('p', 'message-snippet'),
            ('div', 'message-preview'),
            ('span', 'message-content'),
            ('p', None),
        ]

        for tag, class_name in selectors:
            if class_name:
                snippet_elem = element.find(tag, class_=class_name)
            else:
                # For generic tags, try to find them within message divs
                snippet_elem = element.find(tag)

            if snippet_elem:
                snippet = snippet_elem.get_text(strip=True)
                if snippet and len(snippet) > 0:
                    return snippet[:500]  # Limit snippet length

        # Fallback: get all text content
        text_content = element.get_text(strip=True)
        if text_content and len(text_content) > 10:
            return text_content[:500]

        return ""

    def _extract_timestamp(self, element) -> str:
        """Extract timestamp from message element"""
        # Try multiple selector patterns
        selectors = [
            ('span', 'timestamp'),
            ('span', 'message-time'),
            ('div', 'message-date'),
            ('time', None),
        ]

        for tag, class_name in selectors:
            if class_name:
                time_elem = element.find(tag, class_=class_name)
            else:
                time_elem = element.find(tag)

            if time_elem:
                timestamp = time_elem.get_text(strip=True)
                if timestamp:
                    return timestamp

        # Try data attributes
        if element.has_attr('data-timestamp'):
            return element['data-timestamp']

        # Default to current time
        return datetime.now().isoformat()

    def _extract_member_id(self, element) -> Optional[str]:
        """Extract member/user ID from message element"""
        # Try data attributes
        data_attrs = ['data-member-id', 'data-user-id', 'data-followup-user-id']
        for attr in data_attrs:
            if element.has_attr(attr):
                return element[attr]

        # Try to extract from onclick or href attributes
        if element.has_attr('onclick'):
            match = re.search(r'member[/:](\d+)', element['onclick'])
            if match:
                return match.group(1)

        # Check for links to member profiles
        links = element.find_all('a', href=True)
        for link in links:
            match = re.search(r'member[/:](\d+)', link['href'])
            if match:
                return match.group(1)

        return None

    def _extract_read_status(self, element) -> bool:
        """Extract read/unread status from message element"""
        # Check for unread class
        if element.has_attr('class'):
            classes = ' '.join(element['class'])
            if 'unread' in classes.lower():
                return False
            if 'read' in classes.lower():
                return True

        # Check for read indicator elements
        if element.find(class_='unread-indicator'):
            return False

        # Default to read
        return True

    def _generate_message_id(self, sender: str, snippet: str, timestamp: str) -> str:
        """Generate unique message ID based on content"""
        # Create a unique hash based on sender + snippet + timestamp
        content = f"{sender}:{snippet[:50]}:{timestamp}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, content))

    def parse_conversation_html(self, html_content: str, member_id: str) -> List[Dict]:
        """
        Parse full conversation thread from /action/FollowUp response

        Args:
            html_content: HTML response from /action/FollowUp endpoint
            member_id: Member ID for the conversation

        Returns:
            List of message dictionaries in conversation order
        """
        try:
            self.logger.info(f"🔍 Parsing conversation HTML for member {member_id}")

            soup = BeautifulSoup(html_content, 'html.parser')
            messages = []

            # Look for conversation container
            conversation_container = soup.find('div', class_='conversation-history')
            if not conversation_container:
                conversation_container = soup.find('div', id='message-history')

            if conversation_container:
                message_elements = conversation_container.find_all('div', class_='message')

                for msg_elem in message_elements:
                    try:
                        message_data = self._extract_conversation_message(msg_elem, member_id)
                        if message_data:
                            messages.append(message_data)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error parsing conversation message: {e}")
                        continue

            self.logger.info(f"✅ Parsed {len(messages)} messages from conversation")
            return messages

        except Exception as e:
            self.logger.error(f"❌ Error parsing conversation HTML: {e}")
            return []

    def _extract_conversation_message(self, element, member_id: str) -> Optional[Dict]:
        """Extract individual message from conversation thread"""
        try:
            # Extract message content
            content_elem = element.find('p') or element.find('div', class_='message-content')
            if not content_elem:
                return None

            content = content_elem.get_text(strip=True)
            if not content:
                return None

            # Extract sender
            sender_elem = element.find('strong') or element.find('span', class_='sender')
            sender = sender_elem.get_text(strip=True) if sender_elem else "Unknown"

            # Extract timestamp
            time_elem = element.find('span', class_='timestamp') or element.find('time')
            timestamp = time_elem.get_text(strip=True) if time_elem else datetime.now().isoformat()

            # Determine direction (incoming vs outgoing)
            direction = 'incoming'
            if element.has_attr('class'):
                classes = ' '.join(element['class'])
                if 'outgoing' in classes or 'sent' in classes:
                    direction = 'outgoing'

            return {
                'id': str(uuid.uuid4()),
                'message_type': 'conversation_message',
                'member_id': member_id,
                'sender_name': sender,
                'content': content,
                'timestamp': timestamp,
                'direction': direction,
                'status': 'received',
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.debug(f"Could not extract conversation message: {e}")
            return None
