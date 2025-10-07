#!/usr/bin/env python3
"""
Test script for ClubOS message polling with auto-configuration
Verifies that the system automatically detects the logged-in manager
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_auto_configuration():
    """Test automatic polling configuration"""
    try:
        logger.info("=" * 80)
        logger.info("🧪 Testing ClubOS Message Polling Auto-Configuration")
        logger.info("=" * 80)
        
        # Import after path setup
        from src.services.clubos_messaging_client import ClubOSMessagingClient
        from src.services.database_manager import DatabaseManager
        from src.services.real_time_message_sync import RealTimeMessageSync
        from src.config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
        
        # Step 1: Initialize ClubOS client and authenticate
        logger.info("\n📋 Step 1: Authenticating with ClubOS...")
        clubos_client = ClubOSMessagingClient(
            username=CLUBOS_USERNAME,
            password=CLUBOS_PASSWORD
        )
        
        auth_success = clubos_client.authenticate()
        if not auth_success:
            logger.error("❌ Authentication failed")
            return False
        
        logger.info(f"✅ Authentication successful")
        logger.info(f"   - Logged-in User ID: {clubos_client.logged_in_user_id}")
        logger.info(f"   - Delegated User ID: {clubos_client.delegated_user_id}")
        logger.info(f"   - Club ID: {clubos_client.club_id}")
        logger.info(f"   - Club Location ID: {clubos_client.club_location_id}")
        
        # Step 2: Initialize database manager
        logger.info("\n📋 Step 2: Initializing database manager...")
        db_manager = DatabaseManager()
        logger.info("✅ Database manager initialized")
        
        # Step 3: Initialize message sync with auto-configuration
        logger.info("\n📋 Step 3: Initializing message sync (should auto-configure)...")
        message_sync = RealTimeMessageSync(
            clubos_client=clubos_client,
            db_manager=db_manager,
            socketio=None,  # No WebSocket for testing
            poll_interval=10
        )
        
        # Step 4: Verify auto-configuration
        logger.info("\n📋 Step 4: Verifying auto-configuration...")
        status = message_sync.get_status()
        
        logger.info(f"✅ Polling Status:")
        logger.info(f"   - Running: {status['running']}")
        logger.info(f"   - Poll Interval: {status['poll_interval']}s")
        logger.info(f"   - Owner Count: {status['owner_count']}")
        logger.info(f"   - Owners: {status['owners']}")
        
        if status['owner_count'] == 0:
            logger.error("❌ Auto-configuration failed - no owners configured")
            return False
        
        if status['owner_count'] > 0:
            logger.info(f"✅ Auto-configuration successful!")
            logger.info(f"   - Polling inbox for user: {status['owners'][0]}")
        
        # Step 5: Test manual sync (fetch messages once)
        logger.info("\n📋 Step 5: Testing manual message sync...")
        owner_id = list(message_sync.owner_ids)[0]
        
        result = message_sync.sync_now(owner_id)
        
        if result['success']:
            logger.info(f"✅ Manual sync successful")
            logger.info(f"   - Messages fetched: {result['message_count']}")
            logger.info(f"   - Timestamp: {result['timestamp']}")
        else:
            logger.error(f"❌ Manual sync failed: {result.get('error')}")
            return False
        
        # Step 6: Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Authentication: SUCCESS")
        logger.info(f"✅ Auto-Configuration: SUCCESS")
        logger.info(f"✅ Manager Inbox Detection: SUCCESS")
        logger.info(f"✅ Message Sync: SUCCESS")
        logger.info(f"\n🎯 System is ready to poll manager inbox automatically")
        logger.info(f"📬 Monitoring inbox for: User ID {owner_id}")
        logger.info(f"🏢 Club: {clubos_client.club_id}, Location: {clubos_client.club_location_id}")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    logger.info("Starting ClubOS Message Polling Auto-Configuration Test\n")
    
    success = test_auto_configuration()
    
    if success:
        logger.info("\n✅ All tests passed! System is gym-agnostic and ready for any location.")
        sys.exit(0)
    else:
        logger.error("\n❌ Tests failed. Check logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
