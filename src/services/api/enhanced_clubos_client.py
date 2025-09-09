"""
Enhanced ClubOS API Client with specific endpoint implementations for messaging, calendar, and training packages.
Based on captured Charles Proxy endpoints and existing infrastructure.
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.constants import (
    CLUBOS_DASHBOARD_URL, 
    CLUBOS_MESSAGES_URL,
    CLUBOS_CALENDAR_URL
)
from config.secrets_local import get_secret


class EnhancedClubOSAPIClient(ClubOSAPIClient):
    """
    Enhanced ClubOS API client with specific implementations for messaging, calendar, and training packages.
    Extends the base ClubOSAPIClient with targeted endpoint support.
    """
    
    def __init__(self, auth_service: ClubOSAPIAuthentication):
        super().__init__(auth_service)
        
        # Enhanced endpoint mappings based on Charles Proxy captures
        self.api_endpoints = {
            # Calendar endpoints
            "calendar": {
                "events": "/api/calendar/events",
                "sessions": "/ajax/calendar/sessions", 
                "create_session": "/action/Calendar/createSession",
                "update_session": "/action/Calendar/updateSession",
                "delete_session": "/action/Calendar/deleteSession",
                "view": "/action/Calendar"
            },
            
            # Messaging endpoints  
            "messaging": {
                "send_text": "/action/Dashboard/sendText",
                "send_email": "/action/Dashboard/sendEmail", 
                "messages_view": "/action/Dashboard/messages",
                "message_history": "/ajax/messages/history"
            },
            
            # Training package endpoints
            "training": {
                "clients": "/api/training/clients",
                "packages": "/api/training/packages", 
                "sessions": "/api/training/sessions",
                "client_packages": "/api/members/{member_id}/training/packages"
            },
            
            # Member search and data endpoints
            "members": {
                "search": "/action/UserSearch/",
                "details": "/api/members/{member_id}",
                "agreements": "/api/members/{member_id}/agreement",
                "activities": "/api/members/{member_id}/activities"
            }
        }
    
    # =============================================================================
    # MESSAGING API ENDPOINTS
    # =============================================================================
    
    def send_individual_message(self, member_id: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send individual message to a member via ClubOS API.
        
        Args:
            member_id: Target member ID
            message: Message content
            message_type: 'text' or 'email'
            
        Returns:
            Dict containing success status and response details
        """
        print(f"📱 Sending {message_type} message to member {member_id}")
        
        try:
            if message_type.lower() == "text":
                return self._send_text_message(member_id, message)
            elif message_type.lower() == "email":
                return self._send_email_message(member_id, message, "ClubOS Message")
            else:
                return {"success": False, "error": f"Unsupported message type: {message_type}"}
                
        except Exception as e:
            print(f"   ❌ Error sending message: {e}")
            return {"success": False, "error": str(e)}
    
    def send_group_message(self, member_ids: List[str], message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send group message to multiple members.
        
        Args:
            member_ids: List of member IDs
            message: Message content
            message_type: 'text' or 'email'
            
        Returns:
            Dict containing success status and detailed results
        """
        print(f"📢 Sending {message_type} group message to {len(member_ids)} members")
        
        results = {
            "success": True,
            "total_members": len(member_ids),
            "successful_sends": 0,
            "failed_sends": 0,
            "details": []
        }
        
        for member_id in member_ids:
            try:
                result = self.send_individual_message(member_id, message, message_type)
                if result.get("success"):
                    results["successful_sends"] += 1
                else:
                    results["failed_sends"] += 1
                    results["success"] = False
                
                results["details"].append({
                    "member_id": member_id,
                    "status": "success" if result.get("success") else "failed",
                    "error": result.get("error")
                })
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                results["failed_sends"] += 1
                results["success"] = False
                results["details"].append({
                    "member_id": member_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        print(f"   ✅ Group message complete: {results['successful_sends']}/{results['total_members']} successful")
        return results
    
    def _send_text_message(self, member_id: str, message: str) -> Dict[str, Any]:
        """Send text message via ClubOS form submission to working endpoint"""
        try:
            # Use working /action/FollowUp/save endpoint instead of failing API
            endpoint = "/action/FollowUp/save"
            url = f"{self.base_url}{endpoint}"
            
            # Form data structure based on working scripts
            form_data = {
                "followUpStatus": "1",
                "followUpType": "3",
                "memberSalesFollowUpStatus": "6",
                "followUpLog.tfoUserId": member_id,
                "followUpLog.outcome": "3",  # 3 for SMS
                "textMessage": message,
                "event.createdFor.tfoUserId": member_id,
                "event.eventType": "ORIENTATION",
                "duration": "2",
                "event.remindAttendeesMins": "120",
                "followUpUser.tfoUserId": member_id,
                "followUpUser.role.id": "7",
                "followUpUser.clubId": "291",
                "followUpUser.clubLocationId": "3586",
                "followUpLog.followUpAction": "3",  # 3 for SMS
                "memberStudioSalesDefaultAccount": member_id,
                "memberStudioSupportDefaultAccount": member_id,
                "ptSalesDefaultAccount": member_id,
                "ptSupportDefaultAccount": member_id,
                # Add required tokens for form submission
                "__fp": self.get_fingerprint_token(),
                "_sourcePage": self.get_source_page_token()
            }
            
            # Prepare headers for form submission
            headers = self.auth.get_headers()
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view"
            })
            
            response = self.session.post(url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "response": response.text}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _send_email_message(self, member_id: str, message: str, subject: str) -> Dict[str, Any]:
        """Send email message via ClubOS form submission to working endpoint"""
        try:
            # Use working /action/FollowUp/save endpoint instead of failing API
            endpoint = "/action/FollowUp/save"
            url = f"{self.base_url}{endpoint}"
            
            # Form data structure based on working scripts
            form_data = {
                "followUpStatus": "1",
                "followUpType": "3",
                "memberSalesFollowUpStatus": "6",
                "followUpLog.tfoUserId": member_id,
                "followUpLog.outcome": "2",  # 2 for Email
                "emailSubject": subject,
                "emailMessage": f"<p>{message}</p>",  # Wrap in HTML
                "event.createdFor.tfoUserId": member_id,
                "event.eventType": "ORIENTATION",
                "duration": "2",
                "event.remindAttendeesMins": "120",
                "followUpUser.tfoUserId": member_id,
                "followUpUser.role.id": "7",
                "followUpUser.clubId": "291",
                "followUpUser.clubLocationId": "3586",
                "followUpLog.followUpAction": "2",  # 2 for Email
                "memberStudioSalesDefaultAccount": member_id,
                "memberStudioSupportDefaultAccount": member_id,
                "ptSalesDefaultAccount": member_id,
                "ptSupportDefaultAccount": member_id,
                # Add required tokens for form submission
                "__fp": self.get_fingerprint_token(),
                "_sourcePage": self.get_source_page_token()
            }
            
            # Prepare headers for form submission
            headers = self.auth.get_headers()
            headers.update({
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Referer": f"{self.base_url}/action/Dashboard/view"
            })
            
            response = self.session.post(url, data=form_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "response": response.text}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =============================================================================
    # CALENDAR API ENDPOINTS  
    # =============================================================================
    
    def get_calendar_sessions(self, date: str = None, schedule_name: str = "My schedule") -> List[Dict[str, Any]]:
        """
        Get calendar sessions for a specific date and schedule.
        
        Args:
            date: Date in YYYY-MM-DD format, defaults to today
            schedule_name: Name of the schedule to view
            
        Returns:
            List of session dictionaries
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        print(f"📅 Fetching calendar sessions for {date} on '{schedule_name}'")
        
        try:
            # Try API endpoint first
            endpoint = self.api_endpoints["calendar"]["events"]
            url = f"{self.base_url}{endpoint}"
            
            params = {
                "date": date,
                "schedule": schedule_name
            }
            
            response = self.session.get(
                url,
                params=params,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    sessions = response.json()
                    print(f"   ✅ Found {len(sessions)} sessions via API")
                    return sessions
                except json.JSONDecodeError:
                    # Fallback to HTML parsing
                    return self._parse_calendar_html(date, schedule_name)
            else:
                print(f"   ⚠️ API failed ({response.status_code}), trying HTML parsing...")
                return self._parse_calendar_html(date, schedule_name)
                
        except Exception as e:
            print(f"   ❌ Error fetching calendar sessions: {e}")
            return []
    
    def create_calendar_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new calendar session.
        
        Args:
            session_data: Session details {
                'title': str,
                'date': str (YYYY-MM-DD),
                'start_time': str (HH:MM),
                'end_time': str (HH:MM),
                'description': str (optional),
                'schedule': str (optional)
            }
            
        Returns:
            Dict containing success status and session details
        """
        print(f"📝 Creating calendar session: {session_data.get('title', 'Unknown')}")
        
        try:
            endpoint = self.api_endpoints["calendar"]["create_session"]
            url = f"{self.base_url}{endpoint}"
            
            # Prepare form data for session creation
            form_data = {
                "title": session_data.get("title", ""),
                "date": session_data.get("date", ""),
                "startTime": session_data.get("start_time", ""),
                "endTime": session_data.get("end_time", ""),
                "description": session_data.get("description", ""),
                "schedule": session_data.get("schedule", "My schedule")
            }
            
            response = self.session.post(
                url,
                data=form_data,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "session_data": session_data,
                    "response": response.text[:200] + "..." if len(response.text) > 200 else response.text
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_calendar_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing calendar session.
        
        Args:
            session_id: ID of the session to update
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing success status
        """
        print(f"✏️ Updating calendar session {session_id}")
        
        try:
            endpoint = self.api_endpoints["calendar"]["update_session"]
            url = f"{self.base_url}{endpoint}"
            
            form_data = {"sessionId": session_id}
            form_data.update(updates)
            
            response = self.session.post(
                url,
                data=form_data,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "response": response.text if response.status_code == 200 else f"HTTP {response.status_code}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_calendar_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a calendar session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            Dict containing success status
        """
        print(f"🗑️ Deleting calendar session {session_id}")
        
        try:
            endpoint = self.api_endpoints["calendar"]["delete_session"]
            url = f"{self.base_url}{endpoint}"
            
            data = {"sessionId": session_id}
            
            response = self.session.post(
                url,
                data=data,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            return {
                "success": response.status_code == 200,
                "response": response.text if response.status_code == 200 else f"HTTP {response.status_code}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_member_to_session(self, session_id: str, member_id: str) -> Dict[str, Any]:
        """
        Add a member to an existing calendar session.
        
        Args:
            session_id: ID of the session
            member_id: ID of the member to add
            
        Returns:
            Dict containing success status
        """
        print(f"👥 Adding member {member_id} to session {session_id}")
        
        try:
            # This may require a specific endpoint or update to the session
            updates = {
                "addMember": member_id,
                "action": "add_attendee"
            }
            
            return self.update_calendar_session(session_id, updates)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_calendar_html(self, date: str, schedule_name: str) -> List[Dict[str, Any]]:
        """Parse calendar sessions from HTML page (fallback method)"""
        try:
            url = f"{self.base_url}{self.api_endpoints['calendar']['view']}"
            params = {"date": date, "schedule": schedule_name}
            
            response = self.session.get(url, params=params, headers=self.auth.get_headers())
            
            if response.status_code != 200:
                return []
            
            # Basic HTML parsing for sessions (would need BeautifulSoup for production)
            import re
            sessions = []
            
            # Look for session patterns in HTML
            session_patterns = [
                r'data-session-id="([^"]+)"[^>]*>([^<]+)</.*?data-start-time="([^"]+)"',
                r'<div[^>]*class="[^"]*session[^"]*"[^>]*>([^<]+)</div>'
            ]
            
            for pattern in session_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        sessions.append({
                            "id": match[0] if len(match) > 2 else None,
                            "title": match[1] if len(match) > 1 else match[0],
                            "start_time": match[2] if len(match) > 2 else None,
                            "date": date
                        })
            
            print(f"   📄 Parsed {len(sessions)} sessions from HTML")
            return sessions
            
        except Exception as e:
            print(f"   ❌ Error parsing HTML: {e}")
            return []
    
    # =============================================================================
    # TOKEN EXTRACTION METHODS (REQUIRED FOR FORM SUBMISSIONS)
    # =============================================================================
    
    def get_fingerprint_token(self) -> str:
        """
        Extract FRESH __fp (fingerprint) token from current ClubOS session
        Required for all form submissions to ClubOS
        """
        try:
            # Get the calendar page to extract fresh tokens  
            response = self.session.get(f"{self.base_url}/action/Calendar")
            if response.status_code == 200:
                # Look for __fp token in the HTML
                import re
                fp_match = re.search(r'name="__fp"[^>]*value="([^"]*)"', response.text)
                if fp_match:
                    token = fp_match.group(1)
                    print(f"   ✅ Extracted fresh __fp token: {token[:20]}...")
                    return token
                else:
                    print("   ⚠️ Could not find __fp token in page, using fallback")
            
            # Fallback to working token from browser capture
            return "AGtXoR7WJMiW9vsLF0UPm0n2qctwhl4PvLJiae0fh7izVEIu_Dt7iHx08c_m8dvnEE1jjOmqDoscYJUsplTQdoAuI7a4ZIcF6qrgjUfeqze2k2Wo1Ad371GWBi5n-ziv0q-v7P2RYoeVdFsnz7Iwd8ce4mvoiUykZbAucFKmstLpy5uJtwxwkx4o_9sOZWSNCjdWa1f3uuOQuJVsz0joue87i2n52r63FdulhIxvgGyNTxe6Ftisb8kII0PWjkKXwOucoiWfu5rLFxJl0lewWkcYBsLwFr4blvb7CxdFD5ugyb_XBDPm5NQbJk2z4jXRHGCVLKZU0HbVECW1dMleBooheyp9iOUzJ47ciCbx8fJljJbVw2V23o1PF7oW2KxvZ1pWoDimZBVN3G5oVeBet1GWBi5n-zivCjhBQCXuHCeGbk46meyyekcYBsLwFr4blvb7CxdFD5tJ9qnLcIZeD1Mx2z9wnqxx2EdV3vc0530N0GpuM2T_TqnHfSC0T18aQU8_7YyybYlTvFrbqKICJJb2-wsXRQ-bH90lg3gVRe0g7pGAYpP2jDOjTSqVpsjEkLiVbM9I6LnvO4tp-dq-txXbpYSMb4BsPfbD5iPueCPYR1Xe9zTnfQGs4yv3JXH5xFtNNF_JPa_ICTu2zfpKhlGWBi5n-zivgdnnVsKGzXkFg1EIo49Lu2WMltXDZXbejU8XuhbYrG9nWlagOKZkFSmgK8l239ZMUZYGLmf7OK_Sr6_s_ZFih69W1C-fykfE_-9SfKK9r2mW9vsLF0UPm9hkAbMUcqsokLiVbM9I6LnvO4tp-dq-t9jx4ErX5A5Cktqzmpe6nU-YRahsbZP2Pr8BE6doplhfZks2HqR4BNccYJUsplTQdlUF6SMpCqSnAfjY_-mTR6OqKK08jdX8TQ=="
        except Exception as e:
            print(f"   ❌ Error extracting fingerprint token: {e}")
            return "AGtXoR7WJMiW9vsLF0UPm0n2qctwhl4PvLJiae0fh7izVEIu_Dt7iHx08c_m8dvnEE1jjOmqDoscYJUsplTQdoAuI7a4ZIcF6qrgjUfeqze2k2Wo1Ad371GWBi5n-ziv0q-v7P2RYoeVdFsnz7Iwd8ce4mvoiUykZbAucFKmstLpy5uJtwxwkx4o_9sOZWSNCjdWa1f3uuOQuJVsz0joue87i2n52r63FdulhIxvgGyNTxe6Ftisb8kII0PWjkKXwOucoiWfu5rLFxJl0lewWkcYBsLwFr4blvb7CxdFD5ugyb_XBDPm5NQbJk2z4jXRHGCVLKZU0HbVECW1dMleBooheyp9iOUzJ47ciCbx8fJljJbVw2V23o1PF7oW2KxvZ1pWoDimZBVN3G5oVeBet1GWBi5n-zivCjhBQCXuHCeGbk46meyyekcYBsLwFr4blvb7CxdFD5tJ9qnLcIZeD1Mx2z9wnqxx2EdV3vc0530N0GpuM2T_TqnHfSC0T18aQU8_7YyybYlTvFrbqKICJJb2-wsXRQ-bH90lg3gVRe0g7pGAYpP2jDOjTSqVpsjEkLiVbM9I6LnvO4tp-dq-txXbpYSMb4BsPfbD5iPueCPYR1Xe9zTnfQGs4yv3JXH5xFtNNF_JPa_ICTu2zfpKhlGWBi5n-zivgdnnVsKGzXkFg1EIo49Lu2WMltXDZXbejU8XuhbYrG9nWlagOKZkFSmgK8l239ZMUZYGLmf7OK_Sr6_s_ZFih69W1C-fykfE_-9SfKK9r2mW9vsLF0UPm9hkAbMUcqsokLiVbM9I6LnvO4tp-dq-t9jx4ErX5A5Cktqzmpe6nU-YRahsbZP2Pr8BE6doplhfZks2HqR4BNccYJUsplTQdlUF6SMpCqSnAfjY_-mTR6OqKK08jdX8TQ=="

    def get_source_page_token(self) -> str:
        """
        Extract FRESH _sourcePage token from current ClubOS session
        Required for all form submissions to ClubOS
        """
        try:
            # Get the calendar page to extract fresh tokens
            response = self.session.get(f"{self.base_url}/action/Calendar")
            if response.status_code == 200:
                # Look for _sourcePage token in the HTML
                import re
                source_match = re.search(r'name="_sourcePage"[^>]*value="([^"]*)"', response.text)
                if source_match:
                    token = source_match.group(1)
                    print(f"   ✅ Extracted fresh _sourcePage token: {token[:20]}...")
                    return token
                else:
                    print("   ⚠️ Could not find _sourcePage token in page, using fallback")
            
            # Fallback to working token from browser capture
            return "GN6AsTEdTbxJ0LGtZ3ilrEZQiwnc1XV2EIusBezhws92tfAba2lFOA=="
        except Exception as e:
            print(f"   ❌ Error extracting source page token: {e}")
            return "GN6AsTEdTbxJ0LGtZ3ilrEZQiwnc1XV2EIusBezhws92tfAba2lFOA=="

    # =============================================================================
    # TRAINING PACKAGE ENDPOINTS
    # =============================================================================
    
    def get_training_packages_for_client(self, member_id: str) -> Dict[str, Any]:
        """
        Get training package data for a specific training client.
        
        Args:
            member_id: ID of the training client
            
        Returns:
            Dict containing training package information
        """
        print(f"🏋️ Fetching training packages for client {member_id}")
        
        try:
            endpoint = self.api_endpoints["training"]["client_packages"].format(member_id=member_id)
            url = f"{self.base_url}{endpoint}"
            
            response = self.session.get(
                url,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    packages = response.json()
                    print(f"   ✅ Found {len(packages)} training packages")
                    return {
                        "success": True,
                        "member_id": member_id,
                        "packages": packages,
                        "total_packages": len(packages)
                    }
                except json.JSONDecodeError:
                    return self._parse_training_packages_html(member_id)
            else:
                print(f"   ⚠️ API failed ({response.status_code}), trying fallback...")
                return self._parse_training_packages_html(member_id)
                
        except Exception as e:
            print(f"   ❌ Error fetching training packages: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_training_clients(self) -> List[Dict[str, Any]]:
        """
        Get list of all training clients and their package data.
        
        Returns:
            List of training client dictionaries
        """
        print("🏋️‍♀️ Fetching all training clients")
        
        try:
            endpoint = self.api_endpoints["training"]["clients"]
            url = f"{self.base_url}{endpoint}"
            
            response = self.session.get(
                url,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    clients = response.json()
                    print(f"   ✅ Found {len(clients)} training clients")
                    return clients
                except json.JSONDecodeError:
                    return self._parse_training_clients_html()
            else:
                print(f"   ⚠️ API failed ({response.status_code}), trying fallback...")
                return self._parse_training_clients_html()
                
        except Exception as e:
            print(f"   ❌ Error fetching training clients: {e}")
            return []
    
    def get_single_club_member_packages(self, member_id: str) -> Dict[str, Any]:
        """
        Get training package data for a single club member (non-training client).
        
        Args:
            member_id: ID of the club member
            
        Returns:
            Dict containing member's training package information
        """
        print(f"🤸 Fetching training packages for club member {member_id}")
        
        # For single club members, we may need to check their agreements and activities
        try:
            # First get member details
            member_details = self.get_member_details(member_id)
            if not member_details.get("success"):
                return member_details
            
            # Then get their training packages
            packages_result = self.get_training_packages_for_client(member_id)
            
            return {
                "success": True,
                "member_id": member_id,
                "member_type": "single_club_member",
                "member_details": member_details.get("member", {}),
                "training_packages": packages_result.get("packages", []),
                "total_packages": len(packages_result.get("packages", []))
            }
            
        except Exception as e:
            print(f"   ❌ Error fetching member packages: {e}")
            return {"success": False, "error": str(e)}
    
    def get_member_details(self, member_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a member.
        
        Args:
            member_id: ID of the member
            
        Returns:
            Dict containing member details
        """
        try:
            endpoint = self.api_endpoints["members"]["details"].format(member_id=member_id)
            url = f"{self.base_url}{endpoint}"
            
            response = self.session.get(
                url,
                headers=self.auth.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    member_data = response.json()
                    return {"success": True, "member": member_data}
                except json.JSONDecodeError:
                    return {"success": False, "error": "Invalid JSON response"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_training_packages_html(self, member_id: str) -> Dict[str, Any]:
        """Parse training packages from HTML (fallback method)"""
        try:
            # This would involve navigating to the member's training page and parsing HTML
            print("   📄 Parsing training packages from HTML...")
            return {
                "success": False,
                "error": "HTML parsing fallback not yet implemented",
                "note": "Would parse member's training page HTML"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_training_clients_html(self) -> List[Dict[str, Any]]:
        """Parse training clients list from HTML (fallback method)"""
        try:
            # This would involve navigating to training clients page and parsing HTML
            print("   📄 Parsing training clients from HTML...")
            return []
        except Exception as e:
            print(f"   ❌ HTML parsing error: {e}")
            return []


def create_enhanced_clubos_client(username: str = None, password: str = None) -> Optional[EnhancedClubOSAPIClient]:
    """
    Create and authenticate enhanced ClubOS API client.
    
    Args:
        username: ClubOS username (defaults to config)
        password: ClubOS password (defaults to config)
        
    Returns:
        EnhancedClubOSAPIClient instance if authentication successful, None otherwise
    """
    try:
        # Use provided credentials or get from config
        if not username:
            username = get_secret("clubos-username")
        if not password:
            password = get_secret("clubos-password")
        
        if not username or not password:
            print("❌ ClubOS credentials not found in configuration")
            return None
        
        # Create authentication service
        auth_service = ClubOSAPIAuthentication()
        
        if auth_service.login(username, password):
            client = EnhancedClubOSAPIClient(auth_service)
            print("✅ Enhanced ClubOS API client created successfully")
            return client
        else:
            print("❌ Failed to authenticate with ClubOS")
            return None
            
    except Exception as e:
        print(f"❌ Error creating enhanced ClubOS API client: {e}")
        return None