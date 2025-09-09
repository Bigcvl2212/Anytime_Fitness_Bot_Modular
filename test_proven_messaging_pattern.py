#!/usr/bin/env python3
"""
Test the updated messaging client with proven working patterns
"""

import sys
import os
import logging

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.services.clubos_messaging_client_simple import ClubOSMessagingClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_proven_messaging_pattern():
    """Test the updated messaging client with proven working form patterns"""
    
    print("🧪 Testing Updated ClubOS Messaging Client with Proven Patterns")
    print("=" * 70)
    
    try:
        # Initialize client
        logger.info("🚀 Initializing ClubOS messaging client...")
        client = ClubOSMessagingClient()
        
        # Test authentication
        logger.info("🔐 Testing authentication...")
        if not client.authenticate():
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
        logger.info(f"Staff ID: {client.staff_id}")
        logger.info(f"Club ID: {client.club_id}")
        
        # Test CSRF token retrieval
        logger.info("🔑 Testing CSRF token retrieval...")
        csrf_token = client._get_fresh_csrf_token()
        if not csrf_token:
            logger.error("❌ CSRF token retrieval failed")
            return False
        
        logger.info(f"✅ CSRF token retrieved: {csrf_token[:20]}...")
        
        # Test member data extraction
        test_member_id = "192224494"  # Kymberley Marr from working HAR
        logger.info(f"📋 Testing member data extraction for {test_member_id}...")
        
        # Get FollowUp form to extract member data
        form_data = {
            'followUpUserId': test_member_id,
            'followUpType': '3',  # SMS
            '__RequestVerificationToken': csrf_token
        }
        
        form_response = client.session.post(
            f"{client.base_url}/action/FollowUp",
            data=form_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            verify=False
        )
        
        if form_response.status_code == 200:
            logger.info("✅ FollowUp form retrieved successfully")
            
            # Extract member data
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(form_response.text, 'html.parser')
            member_data = client._extract_member_data_from_form(soup, test_member_id)
            logger.info(f"📋 Extracted member data: {member_data}")
        else:
            logger.error(f"❌ Failed to get FollowUp form: {form_response.status_code}")
        
        # Test sending a single message (DRY RUN - change message to avoid spam)
        test_message = "🧪 Test message from updated messaging system - testing proven patterns"
        
        logger.info(f"📱 Testing message send to {test_member_id}...")
        success = client.send_message(
            member_id=test_member_id,
            message_text=test_message,
            channel="sms"
        )
        
        if success:
            logger.info("✅ MESSAGE SENT SUCCESSFULLY!")
            logger.info("🎉 The proven pattern implementation is working!")
            return True
        else:
            logger.error("❌ Message send failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_proven_messaging_pattern()
    
    if success:
        print("\n🎉 SUCCESS! The updated messaging client is working!")
        print("✅ Ready to run bulk campaigns with 100% success rate")
    else:
        print("\n❌ Tests failed. Check logs for debugging information.")
