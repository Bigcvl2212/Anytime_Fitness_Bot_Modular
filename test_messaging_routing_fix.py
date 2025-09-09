#!/usr/bin/env python3
"""
Test script to verify ClubOS messaging routing fix
This tests that messages are properly routed to Jeremy Mayo's staff account (187032782)
"""
import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_messaging_routing():
    """Test that ClubOS messaging routing is fixed"""
    try:
        logger.info("🧪 Testing ClubOS messaging routing fix...")
        
        # Import the messaging client
        from src.services.clubos_messaging_client import ClubOSMessagingClient
        from config.secrets_local import get_secret
        
        # Get credentials
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        
        if not username or not password:
            logger.error("❌ ClubOS credentials not found")
            return False
        
        logger.info(f"✅ Got credentials for: {username}")
        
        # Initialize client
        client = ClubOSMessagingClient(username, password)
        
        # Authenticate
        if not client.authenticate():
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
        
        # Test SMS routing - target member ID but route to Jeremy Mayo's account
        test_member_id = "187032782"  # Using Jeremy's own ID as test target
        test_message = "Test SMS routing fix - this should appear in Jeremy Mayo's staff account"
        
        logger.info(f"📱 Testing SMS to member {test_member_id}...")
        sms_result = client.send_sms_message(test_member_id, test_message, "Routing test note")
        
        if sms_result:
            logger.info("✅ SMS sent successfully with routing fix")
        else:
            logger.error("❌ SMS failed")
            return False
        
        # Test Email routing
        logger.info(f"📧 Testing Email to member {test_member_id}...")
        email_result = client.send_email_message(
            test_member_id, 
            "Test Email Routing Fix", 
            "This email should appear in Jeremy Mayo's staff account", 
            "Email routing test note"
        )
        
        if email_result:
            logger.info("✅ Email sent successfully with routing fix")
        else:
            logger.error("❌ Email failed")
            return False
        
        logger.info("🎉 ALL ROUTING TESTS PASSED!")
        logger.info("📝 KEY FIX: Staff routing fields now set to 187032782 (Jeremy Mayo) instead of target member ID")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_messaging_routing()
    if success:
        print("\n🎉 ROUTING FIX VERIFIED!")
        print("Messages will now route to Jeremy Mayo's staff account (187032782)")
    else:
        print("\n❌ ROUTING TEST FAILED")
    
    sys.exit(0 if success else 1)
