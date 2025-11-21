"""Test if messaging client can now authenticate and sync messages from ClubOS"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src'))

import logging
from services.clubos_messaging_client_simple import ClubOSMessagingClient
from services.authentication.secure_secrets_manager import SecureSecretsManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("TESTING CLUBOS MESSAGING CLIENT AUTHENTICATION & SYNC")
logger.info("=" * 80)

# Get credentials from SecureSecretsManager
logger.info("\n1. Getting ClubOS credentials from SecureSecretsManager...")
secrets_manager = SecureSecretsManager()
username = secrets_manager.get_secret('clubos-username')
password = secrets_manager.get_secret('clubos-password')

if not username or not password:
    logger.error("❌ Failed to get ClubOS credentials!")
    sys.exit(1)

logger.info(f"✅ Got credentials - Username: {username}")

# Initialize messaging client
logger.info("\n2. Initializing ClubOS messaging client...")
try:
    client = ClubOSMessagingClient(username, password)
    logger.info("✅ Messaging client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize messaging client: {e}")
    sys.exit(1)

# Test authentication
logger.info("\n3. Testing ClubOS authentication...")
try:
    if client.authenticate():
        logger.info("✅ ClubOS authentication successful!")
        logger.info(f"   User ID: {client.logged_in_user_id}")
        logger.info(f"   Delegated ID: {client.delegated_user_id}")
        logger.info(f"   Club ID: {getattr(client, 'club_id', 'N/A')}")
    else:
        logger.error("❌ ClubOS authentication failed!")
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Authentication error: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Test message sync
logger.info("\n4. Testing message sync from ClubOS...")
try:
    # Use the logged in user ID as owner_id
    owner_id = client.logged_in_user_id
    logger.info(f"   Fetching messages for owner_id: {owner_id}")

    messages = client.get_messages(owner_id=owner_id)

    if messages is not None:
        logger.info(f"✅ Successfully fetched {len(messages)} messages from ClubOS!")

        if len(messages) > 0:
            logger.info(f"\n   Sample message:")
            sample = messages[0]
            logger.info(f"   - From: {sample.get('from_user', 'N/A')}")
            logger.info(f"   - To: {sample.get('to_user', 'N/A')}")
            logger.info(f"   - Content: {sample.get('content', 'N/A')[:50]}...")
            logger.info(f"   - Created: {sample.get('created_at', 'N/A')}")
    else:
        logger.error("❌ Failed to fetch messages (returned None)")
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Message sync error: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

logger.info("\n" + "=" * 80)
logger.info("✅ ALL TESTS PASSED!")
logger.info("=" * 80)
logger.info("\nRECOMMENDATION:")
logger.info("The messaging client can now authenticate and sync messages.")
logger.info("The messaging page should now be able to pull messages from ClubOS.")
logger.info("\nNext step: Test the messaging page in the dashboard to verify the fix works end-to-end.")
