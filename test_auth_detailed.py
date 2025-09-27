#!/usr/bin/env python3
"""
Test ClubOS authentication and session validation
"""
import os
import sys
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging with more detail
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('auth_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_clubos_auth_detailed():
    """Detailed test of ClubOS authentication with session validation"""
    try:
        logger.info("🔧 Detailed ClubOS authentication test...")
        
        # Import authentication service
        from src.services.authentication.unified_auth_service import get_unified_auth_service
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        
        # Get credentials
        secrets_manager = SecureSecretsManager()
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        
        if not username or not password:
            logger.error("❌ No ClubOS credentials found")
            return
            
        logger.info(f"✅ Found credentials for user: {username}")
        
        # Get authentication service
        auth_service = get_unified_auth_service()
        logger.info("✅ Got unified authentication service")
        
        # Attempt authentication
        logger.info("🔐 Attempting ClubOS authentication...")
        auth_session = auth_service.authenticate_clubos(username, password)
        
        if not auth_session:
            logger.error("❌ Authentication returned None")
            return
            
        if not auth_session.authenticated:
            logger.error("❌ Session not marked as authenticated")
            return
            
        logger.info("✅ Authentication successful!")
        logger.info(f"📊 Session details:")
        logger.info(f"  • Session ID: {auth_session.session_id}")
        logger.info(f"  • User ID: {auth_session.logged_in_user_id}")
        logger.info(f"  • Delegated ID: {auth_session.delegated_user_id}")
        logger.info(f"  • Bearer Token: {auth_session.bearer_token[:20] + '...' if auth_session.bearer_token else 'None'}")
        
        # Test session validation by making a simple request
        logger.info("🧪 Testing session validity with a simple request...")
        
        try:
            test_url = f"{auth_session.base_url}/action/Dashboard/view"
            test_response = auth_session.session.get(
                test_url,
                verify=False,
                timeout=10
            )
            
            logger.info(f"🧪 Test request status: {test_response.status_code}")
            logger.info(f"🧪 Test request URL: {test_response.url}")
            
            # Check if we got redirected back to login
            if 'login' in test_response.url.lower():
                logger.error("❌ CRITICAL: Session is invalid - redirected to login!")
                logger.error("🔍 This explains why members page redirects to login")
                logger.error("🔍 The authentication succeeded but session cookies are not working")
            else:
                logger.info("✅ Session is valid - no redirect to login")
                
        except Exception as e:
            logger.error(f"❌ Error testing session: {e}")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clubos_auth_detailed()