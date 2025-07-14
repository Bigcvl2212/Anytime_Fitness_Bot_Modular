"""
Enhanced ClubOS API Service

Direct API replacements for Selenium-based ClubOS operations.
Provides the same interfaces as Selenium functions but uses direct API calls.
"""

import time
import json
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import re
from urllib.parse import urljoin, quote

from .clubos_api_client import ClubOSAPIClient, create_clubos_api_client
from ...config.constants import (
    CLUBOS_DASHBOARD_URL, CLUBOS_MESSAGES_URL, TEXT_MESSAGE_CHARACTER_LIMIT,
    NOTE_AUTHOR_NAME, STAFF_NAMES
)


class ClubOSAPIService:
    """
    Enhanced ClubOS API service that replaces Selenium functionality.
    Maintains the same interfaces as the original Selenium functions.
    """
    
    def __init__(self, username: str, password: str):
        """Initialize ClubOS API service with authentication"""
        self.api_client = create_clubos_api_client(username, password)
        if not self.api_client:
            raise Exception("Failed to authenticate with ClubOS API")
        
        self.session = self.api_client.session
        self.auth = self.api_client.auth
        self.base_url = "https://anytime.club-os.com"
        
        # Track API endpoints
        self.endpoints = {
            "member_search": "/ajax/members/search",
            "send_message": "/ajax/messages/send",
            "message_history": "/ajax/messages/history",
            "member_profile": "/action/Members/profile",
            "dashboard": "/action/Dashboard/view"
        }
    
    def send_clubos_message(self, member_name: str, subject: str, body: str) -> Union[bool, str]:
        """
        API replacement for send_clubos_message Selenium function.
        
        Args:
            member_name: Name of the member to send message to
            subject: Message subject (for email)
            body: Message content
            
        Returns:
            True if successful, False if failed, "OPTED_OUT" if member opted out
        """
        print(f"📡 API: Sending message to '{member_name}' via ClubOS API...")
        
        try:
            # Step 1: Search for member
            member_info = self._api_search_member(member_name)
            if not member_info:
                print(f"   ❌ Member '{member_name}' not found")
                return False
            
            member_id = member_info.get("id")
            if not member_id:
                print(f"   ❌ No member ID found for '{member_name}'")
                return False
            
            print(f"   ✅ Found member: {member_name} (ID: {member_id})")
            
            # Step 2: Check member communication preferences
            comm_prefs = self._get_member_communication_preferences(member_id)
            if not comm_prefs["text_enabled"] and not comm_prefs["email_enabled"]:
                print(f"   ⚠️ Member {member_name} has opted out of all communications")
                return "OPTED_OUT"
            
            # Step 3: Determine sending method
            use_email = False
            fallback_reason = ""
            
            if len(body) >= TEXT_MESSAGE_CHARACTER_LIMIT:
                use_email = True
                fallback_reason = f"Message too long for SMS ({len(body)} chars)"
            elif not comm_prefs["text_enabled"]:
                use_email = True
                fallback_reason = "SMS not available (member opted out)"
            
            # Step 4: Send message
            if not use_email and comm_prefs["text_enabled"]:
                # Try SMS first
                success = self._send_sms_via_api(member_id, body, member_name)
                if success:
                    print(f"   ✅ SMS sent successfully to {member_name}")
                    return True
                else:
                    print(f"   ⚠️ SMS failed, trying email fallback...")
                    use_email = True
                    fallback_reason = "SMS API failed"
            
            # Email fallback or primary method
            if use_email and comm_prefs["email_enabled"]:
                success = self._send_email_via_api(member_id, subject, body, member_name, fallback_reason)
                if success:
                    print(f"   ✅ Email sent successfully to {member_name}")
                    return True
                else:
                    print(f"   ❌ Email sending failed for {member_name}")
                    return False
            
            # If we get here, no communication method worked
            if not comm_prefs["email_enabled"]:
                print(f"   ❌ No email option available for {member_name}")
                return "OPTED_OUT"
            else:
                print(f"   ❌ All communication methods failed for {member_name}")
                return False
                
        except Exception as e:
            print(f"   ❌ API error sending message to {member_name}: {e}")
            
            # Fallback to Selenium if API fails
            print(f"   🔄 Falling back to Selenium method...")
            return self._fallback_to_selenium(member_name, subject, body)
    
    def _api_search_member(self, member_name: str) -> Optional[Dict[str, Any]]:
        """Search for member using ClubOS API"""
        try:
            search_url = urljoin(self.base_url, self.endpoints["member_search"])
            
            # Try different search parameters
            search_params = [
                {"q": member_name, "type": "member"},
                {"search": member_name},
                {"member_name": member_name},
                {"query": member_name}
            ]
            
            for params in search_params:
                try:
                    response = self.session.get(
                        search_url,
                        params=params,
                        headers=self.auth.get_headers(),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract member information from response
                        member_info = self._extract_member_from_search_results(data, member_name)
                        if member_info:
                            return member_info
                            
                except Exception as e:
                    print(f"   🔍 Search attempt failed: {e}")
                    continue
            
            # If API search fails, try HTML scraping
            return self._scrape_member_search(member_name)
            
        except Exception as e:
            print(f"   ❌ Error searching for member: {e}")
            return None
    
    def _extract_member_from_search_results(self, data: Any, member_name: str) -> Optional[Dict[str, Any]]:
        """Extract member information from search results"""
        try:
            # Handle different response formats
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict):
                results = data.get("results", data.get("members", data.get("data", [])))
            else:
                return None
            
            # Find matching member
            for result in results:
                if isinstance(result, dict):
                    name_fields = ["name", "full_name", "member_name", "display_name"]
                    result_name = ""
                    
                    for field in name_fields:
                        if field in result:
                            result_name = str(result[field]).strip()
                            break
                    
                    # Check if names match (case-insensitive)
                    if result_name.lower() == member_name.lower():
                        return {
                            "id": result.get("id", result.get("member_id")),
                            "name": result_name,
                            "email": result.get("email"),
                            "phone": result.get("phone"),
                            "raw_data": result
                        }
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error extracting member from results: {e}")
            return None
    
    def _scrape_member_search(self, member_name: str) -> Optional[Dict[str, Any]]:
        """Fallback to HTML scraping if API search fails"""
        try:
            # Navigate to dashboard and search
            dashboard_response = self.session.get(
                CLUBOS_DASHBOARD_URL,
                headers=self.auth.get_headers()
            )
            
            if dashboard_response.status_code != 200:
                return None
            
            # Look for search functionality in the page
            html_content = dashboard_response.text
            
            # Extract member information from HTML if search form is present
            # This is a simplified version - would need to be enhanced based on actual HTML structure
            member_pattern = rf'data-member-name="{re.escape(member_name)}"[^>]*data-member-id="([^"]+)"'
            match = re.search(member_pattern, html_content, re.IGNORECASE)
            
            if match:
                return {
                    "id": match.group(1),
                    "name": member_name,
                    "source": "html_scraping"
                }
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error in HTML scraping fallback: {e}")
            return None
    
    def _get_member_communication_preferences(self, member_id: str) -> Dict[str, bool]:
        """Get member's communication preferences"""
        try:
            # Try to get preferences via API
            prefs_url = urljoin(self.base_url, f"/api/members/{member_id}/preferences")
            
            response = self.session.get(
                prefs_url,
                headers=self.auth.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                prefs_data = response.json()
                return {
                    "text_enabled": prefs_data.get("sms_enabled", True),
                    "email_enabled": prefs_data.get("email_enabled", True)
                }
            
            # Default to both enabled if we can't determine preferences
            return {"text_enabled": True, "email_enabled": True}
            
        except Exception as e:
            print(f"   ⚠️ Could not determine communication preferences: {e}")
            # Default to both enabled if we can't determine
            return {"text_enabled": True, "email_enabled": True}
    
    def _send_sms_via_api(self, member_id: str, message: str, member_name: str) -> bool:
        """Send SMS message via ClubOS API"""
        try:
            sms_url = urljoin(self.base_url, "/api/messages/sms")
            
            sms_data = {
                "member_id": member_id,
                "message": message,
                "notes": f"Auto-SMS sent by {NOTE_AUTHOR_NAME}",
                "type": "sms"
            }
            
            response = self.session.post(
                sms_url,
                json=sms_data,
                headers=self.auth.get_headers(),
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"   ⚠️ SMS API returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ SMS API error: {e}")
            return False
    
    def _send_email_via_api(self, member_id: str, subject: str, body: str, 
                           member_name: str, fallback_reason: str = "") -> bool:
        """Send email message via ClubOS API"""
        try:
            email_url = urljoin(self.base_url, "/api/messages/email")
            
            notes = f"Auto-email sent by {NOTE_AUTHOR_NAME}"
            if fallback_reason:
                notes += f" ({fallback_reason})"
            
            email_data = {
                "member_id": member_id,
                "subject": subject,
                "body": body,
                "notes": notes,
                "type": "email"
            }
            
            response = self.session.post(
                email_url,
                json=email_data,
                headers=self.auth.get_headers(),
                timeout=20
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"   ⚠️ Email API returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ Email API error: {e}")
            return False
    
    def _fallback_to_selenium(self, member_name: str, subject: str, body: str) -> Union[bool, str]:
        """Fallback to original Selenium implementation if API fails"""
        try:
            print(f"   🔄 Using Selenium fallback for {member_name}")
            
            # Import here to avoid circular imports
            from ...core.driver import setup_driver_and_login
            from ...services.clubos.messaging import send_clubos_message
            
            # Setup driver and login
            driver = setup_driver_and_login()
            if not driver:
                print(f"   ❌ Failed to setup Selenium driver")
                return False
            
            try:
                # Use original Selenium function
                result = send_clubos_message(driver, member_name, subject, body)
                print(f"   ✅ Selenium fallback completed for {member_name}")
                return result
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"   ❌ Selenium fallback failed: {e}")
            return False
    
    def get_last_message_sender(self) -> Optional[str]:
        """
        API replacement for get_last_message_sender Selenium function.
        
        Returns:
            Member name of the most recent message sender, or None if failed
        """
        print("📡 API: Getting last message sender via ClubOS API...")
        
        try:
            # Try API approach first
            messages_url = urljoin(self.base_url, "/api/messages/recent")
            
            response = self.session.get(
                messages_url,
                headers=self.auth.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract most recent message sender
                sender = self._extract_latest_sender_from_api(data)
                if sender:
                    print(f"   ✅ Found recent message from: {sender}")
                    return sender
            
            # Fallback to HTML scraping
            return self._scrape_message_page_for_sender()
            
        except Exception as e:
            print(f"   ❌ API error getting last message sender: {e}")
            return self._scrape_message_page_for_sender()
    
    def _extract_latest_sender_from_api(self, data: Any) -> Optional[str]:
        """Extract latest message sender from API response"""
        try:
            # Handle different response formats
            if isinstance(data, list):
                messages = data
            elif isinstance(data, dict):
                messages = data.get("messages", data.get("data", []))
            else:
                return None
            
            if not messages:
                return None
            
            # Get the first (most recent) message
            latest_message = messages[0]
            
            # Extract sender name
            sender_fields = ["sender", "from", "member_name", "name"]
            for field in sender_fields:
                if field in latest_message:
                    sender = str(latest_message[field]).strip()
                    if sender and sender not in STAFF_NAMES:
                        return sender
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error extracting sender from API data: {e}")
            return None
    
    def _scrape_message_page_for_sender(self) -> Optional[str]:
        """Fallback to HTML scraping for message sender"""
        try:
            print("   🔄 Falling back to HTML scraping for message sender...")
            
            response = self.session.get(
                CLUBOS_MESSAGES_URL,
                headers=self.auth.get_headers()
            )
            
            if response.status_code != 200:
                return None
            
            html_content = response.text
            
            # Look for message elements (this would need to be customized based on actual HTML structure)
            patterns = [
                r'<a[^>]*class="[^"]*username-content[^"]*"[^>]*>([^<]+)</a>',
                r'<div[^>]*class="[^"]*message[^"]*"[^>]*data-sender="([^"]+)"',
                r'<span[^>]*class="[^"]*sender[^"]*"[^>]*>([^<]+)</span>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    # Return the first match that's not a staff member
                    for match in matches:
                        sender = match.strip()
                        if sender and sender not in STAFF_NAMES:
                            print(f"   ✅ Found sender via HTML scraping: {sender}")
                            return sender
            
            return None
            
        except Exception as e:
            print(f"   ⚠️ Error in HTML scraping for sender: {e}")
            return None
    
    def scrape_conversation_for_contact(self, member_name: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a specific member.
        
        Args:
            member_name: Name of the member
            
        Returns:
            List of conversation messages
        """
        print(f"📡 API: Getting conversation history for {member_name}...")
        
        try:
            # First get member ID
            member_info = self._api_search_member(member_name)
            if not member_info:
                print(f"   ❌ Could not find member {member_name}")
                return []
            
            member_id = member_info.get("id")
            
            # Get conversation via API
            conversation_url = urljoin(self.base_url, f"/api/messages/conversation/{member_id}")
            
            response = self.session.get(
                conversation_url,
                headers=self.auth.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                conversation = self._process_conversation_data(data)
                print(f"   ✅ Retrieved {len(conversation)} messages for {member_name}")
                return conversation
            
            # Fallback to HTML scraping
            return self._scrape_conversation_html(member_name)
            
        except Exception as e:
            print(f"   ❌ Error getting conversation for {member_name}: {e}")
            return []
    
    def _process_conversation_data(self, data: Any) -> List[Dict[str, Any]]:
        """Process conversation data from API response"""
        try:
            if isinstance(data, list):
                messages = data
            elif isinstance(data, dict):
                messages = data.get("messages", data.get("conversation", data.get("data", [])))
            else:
                return []
            
            processed_messages = []
            for message in messages:
                if isinstance(message, dict):
                    processed_message = {
                        "sender": message.get("sender", message.get("from", "Unknown")),
                        "content": message.get("content", message.get("message", "")),
                        "timestamp": message.get("timestamp", message.get("created_at", "")),
                        "type": message.get("type", "unknown")
                    }
                    processed_messages.append(processed_message)
            
            return processed_messages
            
        except Exception as e:
            print(f"   ⚠️ Error processing conversation data: {e}")
            return []
    
    def _scrape_conversation_html(self, member_name: str) -> List[Dict[str, Any]]:
        """Fallback to HTML scraping for conversation"""
        try:
            print(f"   🔄 Using HTML scraping fallback for {member_name} conversation")
            
            # This would need to be implemented based on the actual ClubOS HTML structure
            # For now, return empty list
            print(f"   ⚠️ HTML conversation scraping not yet implemented")
            return []
            
        except Exception as e:
            print(f"   ⚠️ Error in conversation HTML scraping: {e}")
            return []


# Convenience functions that maintain the same interface as the original Selenium functions
def send_clubos_message_api(username: str, password: str, member_name: str, 
                           subject: str, body: str) -> Union[bool, str]:
    """
    API replacement for send_clubos_message that maintains the same interface.
    
    Args:
        username: ClubOS username
        password: ClubOS password
        member_name: Name of the member to send message to
        subject: Message subject
        body: Message content
        
    Returns:
        True if successful, False if failed, "OPTED_OUT" if member opted out
    """
    try:
        service = ClubOSAPIService(username, password)
        return service.send_clubos_message(member_name, subject, body)
    except Exception as e:
        print(f"❌ Error in API message service: {e}")
        return False


def get_last_message_sender_api(username: str, password: str) -> Optional[str]:
    """
    API replacement for get_last_message_sender that maintains the same interface.
    
    Args:
        username: ClubOS username
        password: ClubOS password
        
    Returns:
        Member name of the most recent message sender, or None if failed
    """
    try:
        service = ClubOSAPIService(username, password)
        return service.get_last_message_sender()
    except Exception as e:
        print(f"❌ Error in API message service: {e}")
        return None


def get_member_conversation_api(username: str, password: str, member_name: str) -> List[Dict[str, Any]]:
    """
    API replacement for scraping member conversation.
    
    Args:
        username: ClubOS username
        password: ClubOS password
        member_name: Name of the member
        
    Returns:
        List of conversation messages
    """
    try:
        service = ClubOSAPIService(username, password)
        return service.scrape_conversation_for_contact(member_name)
    except Exception as e:
        print(f"❌ Error in API conversation service: {e}")
        return []