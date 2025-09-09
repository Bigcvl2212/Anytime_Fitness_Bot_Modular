#!/usr/bin/env python3
"""
ClubOS Working Messaging Implementation
Based on HAR analysis of successful messaging flow
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ClubOSWorkingMessagingClient:
    """
    Working ClubOS messaging implementation based on HAR analysis
    Uses the exact pattern that works in the browser
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with ClubOS using the same pattern as the working client"""
        try:
            logger.info(f"🔐 Authenticating {self.username}...")
            
            # Set proper headers like a real browser
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Get login page first
            logger.info("📄 Getting login page...")
            login_page = self.session.get(f"{self.base_url}/action/Account/login", timeout=10)
            logger.info(f"✅ Login page status: {login_page.status_code}")
            
            if login_page.status_code != 200:
                logger.error(f"❌ Failed to get login page: {login_page.status_code}")
                return False
            
            # Extract CSRF token
            soup = BeautifulSoup(login_page.text, 'html.parser')
            csrf_input = soup.find('input', {'name': '__RequestVerificationToken'})
            
            if not csrf_input:
                logger.error("❌ No CSRF token found on login page")
                return False
            
            csrf_token = csrf_input.get('value', '')
            logger.info(f"🔑 CSRF token found: {csrf_token[:20]}...")
            
            # Submit login with proper headers
            login_data = {
                'username': self.username,
                'password': self.password,
                '__RequestVerificationToken': csrf_token
            }
            
            logger.info("🔐 Submitting login credentials...")
            login_response = self.session.post(
                f"{self.base_url}/action/Account/login",
                data=login_data,
                allow_redirects=True,
                timeout=10,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': f"{self.base_url}/action/Account/login"
                }
            )
            
            logger.info(f"🔍 Login response status: {login_response.status_code}")
            logger.info(f"🔍 Final URL: {login_response.url}")
            
            # Check for successful authentication
            if login_response.status_code == 200:
                if "dashboard" in login_response.url.lower() or "home" in login_response.url.lower():
                    logger.info("✅ Authentication successful - redirected to dashboard")
                    self.authenticated = True
                    return True
                elif "login" not in login_response.url.lower():
                    # Sometimes successful auth doesn't redirect to dashboard
                    logger.info("✅ Authentication appears successful - not on login page")
                    self.authenticated = True
                    return True
                else:
                    logger.error(f"❌ Authentication failed - still on login page: {login_response.url}")
                    return False
            else:
                logger.error(f"❌ Authentication failed with status code: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def send_message_working_pattern(self, member_id: str, message_text: str) -> bool:
        """
        Send message using the EXACT pattern from successful HAR analysis
        
        HAR Analysis shows this 2-step process:
        1. POST /action/FollowUp (opens popup with member info)
        2. POST /action/FollowUp/save (actually sends the message)
        """
        try:
            if not self.authenticated and not self.authenticate():
                return False
            
            logger.info(f"📱 Sending message to member {member_id}: '{message_text}'")
            
            # Step 1: Open FollowUp popup (as seen in HAR)
            popup_response = self.session.post(
                f"{self.base_url}/action/FollowUp",
                data={
                    'followUpUserId': member_id,
                    'followUpType': '3'  # SMS type from HAR
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            
            if popup_response.status_code != 200:
                logger.error(f"❌ Failed to open FollowUp popup: {popup_response.status_code}")
                return False
            
            logger.info("✅ FollowUp popup opened successfully")
            
            # Step 2: Submit the actual message (exact form from HAR)
            message_data = {
                # Core fields from HAR analysis
                'followUpStatus': '1',
                'followUpType': '3',  # SMS type
                'followUpSequence': '',
                'memberSalesFollowUpStatus': '6',
                
                # Member targeting
                'followUpLog.id': '',
                'followUpLog.tfoUserId': member_id,
                'followUpLog.outcome': '2',  # Important: outcome = 2 for SMS
                
                # Message content (HAR shows both email and text fields)
                'emailSubject': 'Jeremy Mayo has sent you a message',
                'emailMessage': '<p>Type message here...</p>',
                'textMessage': message_text,  # This is the actual SMS content
                
                # Additional fields that were in successful HAR requests
                'followUpLog.followUpAction': '3',  # SMS action
                'followUpUser.role.id': '7',
                'event.eventType': 'FOLLOWUP',
                'duration': '1'
            }
            
            # Submit message
            send_response = self.session.post(
                f"{self.base_url}/action/FollowUp/save",
                data=message_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            
            # Check response for success
            if send_response.status_code == 200:
                response_text = send_response.text
                if 'has been texted' in response_text:
                    logger.info(f"✅ Message sent successfully to member {member_id}")
                    return True
                else:
                    logger.error(f"❌ Unexpected response: {response_text[:200]}")
                    return False
            else:
                logger.error(f"❌ Failed to send message: {send_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False
    
    def send_bulk_messages_working(self, member_ids: list, message_text: str) -> Dict:
        """Send bulk messages using working pattern"""
        results = {
            'total': len(member_ids),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info(f"📢 Starting bulk messaging to {len(member_ids)} members using WORKING pattern")
        
        for i, member_id in enumerate(member_ids):
            try:
                logger.info(f"📨 Sending message {i+1}/{len(member_ids)} to member {member_id}")
                
                success = self.send_message_working_pattern(member_id, message_text)
                
                if success:
                    results['successful'] += 1
                    logger.info(f"✅ Message {i+1} sent successfully")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to send to member {member_id}")
                
                # Small delay between messages
                import time
                time.sleep(1)
                
            except Exception as e:
                results['failed'] += 1
                error_msg = f"Exception sending to member {member_id}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        logger.info(f"📊 Bulk messaging completed: {results['successful']}/{results['total']} successful")
        return results

def test_working_implementation():
    """Test the working implementation"""
    
    # Import credentials
    try:
        from src.config.secrets_local import get_secret
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
    except ImportError:
        print("❌ Could not import ClubOS credentials from secrets_local")
        # Try direct import as fallback
        try:
            from src.config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
            username = CLUBOS_USERNAME
            password = CLUBOS_PASSWORD
        except ImportError:
            print("❌ Could not import ClubOS credentials from clubos_credentials_clean either")
            return
    
    # Test with known working member IDs from HAR
    test_member_ids = ['192224494', '189425730']  # Kymberley Marr, Dennis Rost
    test_message = "This is a test message using the working HAR pattern."
    
    client = ClubOSWorkingMessagingClient(username, password)
    
    if client.authenticate():
        print("✅ Authentication successful, testing message sending...")
        
        # Test single message
        success = client.send_message_working_pattern(test_member_ids[0], test_message)
        if success:
            print("✅ Single message test successful!")
        else:
            print("❌ Single message test failed")
        
        # Test bulk messaging
        results = client.send_bulk_messages_working(test_member_ids, test_message)
        print(f"📊 Bulk test results: {results}")
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing ClubOS Working Messaging Implementation")
    print("=" * 60)
    test_working_implementation()
