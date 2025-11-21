#!/usr/bin/env python3
"""
ClubOS Working Messaging Implementation
Based on HAR analysis of successful messaging flow
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional
import os

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
        """Authenticate with ClubOS using working HAR token pattern and relaxed TLS verification"""
        try:
            logger.info(f"🔐 Authenticating {self.username}...")
            # Browser-like headers
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            # Step 1: View login page to collect form tokens
            login_view_url = f"{self.base_url}/action/Login/view"
            logger.info("📄 Getting login page...")
            login_page = self.session.get(login_view_url, timeout=30, verify=False)
            logger.info(f"✅ Login page status: {login_page.status_code}")
            if login_page.status_code != 200:
                logger.error(f"❌ Failed to get login page: {login_page.status_code}")
                return False
            soup = BeautifulSoup(login_page.text, 'html.parser')
            source_page = soup.find('input', {'name': '_sourcePage'})
            fp_token = soup.find('input', {'name': '__fp'})
            # Step 2: Submit login
            login_data = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': source_page.get('value') if source_page else '',
                '__fp': fp_token.get('value') if fp_token else ''
            }
            login_post_url = f"{self.base_url}/action/Login"
            logger.info("🔐 Submitting login credentials...")
            login_response = self.session.post(
                login_post_url,
                data=login_data,
                allow_redirects=True,
                timeout=30,
                verify=False,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': login_view_url,
                    'Origin': self.base_url
                }
            )
            logger.info(f"🔍 Login response status: {login_response.status_code}")
            # Validate by cookies
            session_id = self.session.cookies.get('JSESSIONID')
            logged_in_user_id = self.session.cookies.get('loggedInUserId')
            if not session_id or not logged_in_user_id:
                logger.error("❌ Authentication failed - missing session cookies")
                return False
            self.staff_id = logged_in_user_id
            self.authenticated = True
            logger.info("✅ Authentication successful")
            return True
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
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': self.base_url,
                    'Referer': f"{self.base_url}/action/Dashboard"
                },
                verify=False,
                timeout=30
            )
            
            if popup_response.status_code != 200:
                logger.error(f"❌ Failed to open FollowUp popup: {popup_response.status_code}")
                return False
            
            logger.info("✅ FollowUp popup opened successfully")

            # Optional debug dump of popup HTML
            if os.environ.get('CLUBOS_DEBUG') == '1':
                try:
                    with open('followup_popup_debug.html', 'w', encoding='utf-8') as f:
                        f.write(popup_response.text)
                    logger.info("📝 Saved FollowUp popup HTML to followup_popup_debug.html")
                except Exception as e:
                    logger.warning(f"⚠️ Could not write followup_popup_debug.html: {e}")
            
            # Extract all inputs/textareas/selects across the entire popup (multiple forms)
            soup = BeautifulSoup(popup_response.text, 'html.parser')
            message_data: Dict[str, str] = {}

            # Inputs (document order, later duplicates win)
            for inp in soup.find_all('input'):
                name = inp.get('name')
                if not name:
                    continue
                itype = (inp.get('type') or '').lower()
                if itype in ('submit', 'button', 'image', 'file'):
                    continue
                if itype in ('checkbox', 'radio'):
                    if inp.has_attr('checked'):
                        message_data[name] = inp.get('value') or 'on'
                    continue
                message_data[name] = inp.get('value') or ''

            # Textareas
            for ta in soup.find_all('textarea'):
                name = ta.get('name')
                if not name:
                    continue
                message_data[name] = ta.text or ta.get('value') or ''

            # Selects
            for sel in soup.find_all('select'):
                name = sel.get('name')
                if not name:
                    continue
                selected = sel.find('option', selected=True)
                if selected is None:
                    # take first option if exists
                    opt = sel.find('option')
                    if opt is not None:
                        message_data[name] = opt.get('value') or opt.text or ''
                else:
                    message_data[name] = selected.get('value') or selected.text or ''

            # Now enforce required values from working pattern
            message_data['textMessage'] = message_text
            message_data['followUpType'] = '3'
            # Outcome: choose a valid option value; '2' is "Left message"
            outcome_val = (message_data.get('followUpLog.outcome') or '').strip()
            if outcome_val.lower().startswith('choose') or outcome_val == '':
                message_data['followUpLog.outcome'] = '2'
            else:
                message_data['followUpLog.outcome'] = outcome_val
            message_data['followUpLog.followUpAction'] = '3'
            # Ensure target id present/overridden
            message_data['followUpLog.tfoUserId'] = str(member_id)
            # Fill common defaults if missing
            if not message_data.get('followUpSequence'):
                message_data['followUpSequence'] = ''
            if not message_data.get('memberSalesFollowUpStatus'):
                message_data['memberSalesFollowUpStatus'] = '6'

            # Remove scheduling-related fields and any 'Choose...' placeholders
            remove_keys = []
            for k, v in list(message_data.items()):
                if isinstance(v, str) and v.strip().lower().startswith('choose'):
                    remove_keys.append(k)
            # Always remove scheduling fields when sending text
            remove_keys += [
                'event.id', 'event.startTime', 'event.createdFor.tfoUserId', 'event.eventType',
                'event.remindAttendeesMins', 'startTimeSlotId', 'duration'
            ]
            # Optional ancillary fields that aren't required for a text outcome
            remove_keys += [
                'followUpLog.followUpWith', 'followUpLog.followUpWithOrig', 'followUpLog.followUpDate'
            ]
            for k in set(remove_keys):
                if k in message_data:
                    message_data.pop(k, None)

            # Optional: dump outgoing payload for debugging
            if os.environ.get('CLUBOS_DEBUG') == '1':
                try:
                    import json
                    with open('followup_payload_debug.json', 'w', encoding='utf-8') as f:
                        json.dump({k: message_data[k] for k in sorted(message_data.keys())}, f, ensure_ascii=False, indent=2)
                    logger.info("📝 Saved FollowUp payload to followup_payload_debug.json")
                except Exception as e:
                    logger.warning(f"⚠️ Could not write followup_payload_debug.json: {e}")
            
            # Submit message
            send_response = self.session.post(
                f"{self.base_url}/action/FollowUp/save",
                data=message_data,
                headers={
                    'Accept': 'text/html, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Origin': self.base_url,
                    'Referer': f"{self.base_url}/action/FollowUp"
                },
                verify=False,
                timeout=30
            )
            
            # Check response for success
            if send_response.status_code == 200:
                response_text = send_response.text
                # Optional debug dump of save response
                if os.environ.get('CLUBOS_DEBUG') == '1':
                    try:
                        with open('followup_save_debug.html', 'w', encoding='utf-8') as f:
                            f.write(response_text)
                        logger.info("📝 Saved FollowUp save response to followup_save_debug.html")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not write followup_save_debug.html: {e}")
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
    test_message = 'Automated test via working client'
    
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
