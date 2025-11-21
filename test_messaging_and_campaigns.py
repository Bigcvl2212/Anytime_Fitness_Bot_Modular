"""
Test Messaging and Campaign Functionality
Tests that messages are being pulled from ClubOS and campaigns can access members
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.services.database_manager import DatabaseManager
from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_clubos_message_pulling():
    """Test if messages can be pulled from ClubOS"""
    try:
        logger.info("=" * 80)
        logger.info("TEST 1: ClubOS Message Pulling")
        logger.info("=" * 80)

        # Get credentials
        secrets_manager = SecureSecretsManager()
        clubos_username = secrets_manager.get_secret('clubos-username')
        clubos_password = secrets_manager.get_secret('clubos-password')

        if not clubos_username or not clubos_password:
            logger.error("❌ ClubOS credentials not found!")
            logger.info("Looking for: clubos-username and clubos-password")
            return False

        logger.info(f"✅ Found ClubOS credentials (username: {clubos_username[:10]}...)")

        # Create messaging client
        messaging = ClubOSMessagingClient()

        # Authenticate
        logger.info("🔐 Authenticating with ClubOS...")
        if not messaging.authenticate(clubos_username, clubos_password):
            logger.error("❌ ClubOS authentication failed!")
            return False

        logger.info("✅ ClubOS authentication successful")

        # Get messages
        logger.info("📥 Fetching messages from ClubOS...")
        messages = messaging.get_recent_messages(limit=10)

        if messages:
            logger.info(f"✅ Successfully fetched {len(messages)} messages from ClubOS")
            logger.info("\n📋 Recent Messages:")
            logger.info("-" * 80)
            for i, msg in enumerate(messages[:5], 1):
                logger.info(f"{i}. From: {msg.get('from_user', 'Unknown')}")
                logger.info(f"   Type: {msg.get('message_type', 'Unknown')}")
                logger.info(f"   Content: {msg.get('content', '')[:50]}...")
                logger.info(f"   Timestamp: {msg.get('timestamp', 'Unknown')}")
                logger.info("-" * 80)
            return True
        else:
            logger.warning("⚠️ No messages returned from ClubOS")
            logger.info("This could mean:")
            logger.info("  1. You have no messages in ClubOS")
            logger.info("  2. The messaging client needs updating")
            logger.info("  3. There's an API issue")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing ClubOS message pulling: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_campaign_categories():
    """Test if campaign categories can access members"""
    try:
        logger.info("=" * 80)
        logger.info("TEST 2: Campaign Categories")
        logger.info("=" * 80)

        db = DatabaseManager()

        # Test each category
        categories = ['green', 'past_due', 'yellow', 'comp', 'ppv', 'staff', 'collections', 'inactive']

        logger.info("\n📊 Testing member counts by category:")
        logger.info("-" * 80)

        total_members_found = 0
        for category in categories:
            members = db.get_members_by_category(category)
            count = len(members) if members else 0
            total_members_found += count

            status = "✅" if count > 0 else "⚠️"
            logger.info(f"{status} {category:15s}: {count:5d} members")

            # Show first 3 members
            if members and count > 0:
                for i, member in enumerate(members[:3], 1):
                    name = member.get('full_name', 'Unknown')
                    status_msg = member.get('status_message', 'Unknown')
                    logger.info(f"     {i}. {name} - {status_msg}")

        logger.info("-" * 80)
        logger.info(f"Total members found across all categories: {total_members_found}")

        if total_members_found == 0:
            logger.error("❌ No members found in any category!")
            logger.info("This means the database has no members or they need to be synced")
            return False
        else:
            logger.info("✅ Campaign categories are working and have members")
            return True

    except Exception as e:
        logger.error(f"❌ Error testing campaign categories: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_message_storage():
    """Test if messages can be stored and retrieved from database"""
    try:
        logger.info("=" * 80)
        logger.info("TEST 3: Database Message Storage")
        logger.info("=" * 80)

        db = DatabaseManager()

        # Check if messages table exists and has data
        try:
            messages = db.execute_query("SELECT * FROM messages LIMIT 10", fetch_all=True)

            if messages:
                logger.info(f"✅ Found {len(messages)} messages in database")
                logger.info("\n📋 Messages in Database:")
                logger.info("-" * 80)
                for i, msg in enumerate(messages, 1):
                    msg_dict = dict(msg)
                    logger.info(f"{i}. Type: {msg_dict.get('message_type', 'Unknown')}")
                    logger.info(f"   From: {msg_dict.get('from_user', 'Unknown')}")
                    logger.info(f"   Content: {msg_dict.get('content', '')[:50]}...")
                    logger.info("-" * 80)
                return True
            else:
                logger.warning("⚠️ Messages table exists but is empty")
                logger.info("You may need to:")
                logger.info("  1. Click 'Sync Messages' in the messaging page")
                logger.info("  2. Or messages table hasn't been populated yet")
                return False

        except Exception as e:
            logger.warning(f"⚠️ Messages table may not exist: {e}")
            logger.info("The table will be created when you first use the messaging feature")
            return False

    except Exception as e:
        logger.error(f"❌ Error testing database message storage: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_member_categories_table():
    """Check if member_categories table exists and has data"""
    try:
        logger.info("=" * 80)
        logger.info("TEST 4: Member Categories Table")
        logger.info("=" * 80)

        db = DatabaseManager()

        try:
            # Check if table exists
            categories = db.execute_query("SELECT * FROM member_categories LIMIT 10", fetch_all=True)

            if categories:
                logger.info(f"✅ Found {len(categories)} entries in member_categories table")
                logger.info("\n📋 Member Category Assignments:")
                logger.info("-" * 80)
                for i, cat in enumerate(categories, 1):
                    cat_dict = dict(cat)
                    logger.info(f"{i}. Member ID: {cat_dict.get('member_id', 'Unknown')}")
                    logger.info(f"   Category: {cat_dict.get('category', 'Unknown')}")
                logger.info("-" * 80)
                return True
            else:
                logger.warning("⚠️ member_categories table exists but is empty")
                logger.info("This is OK - the app uses status_message for categorization")
                return True

        except Exception as e:
            logger.info("ℹ️ member_categories table doesn't exist (this is OK)")
            logger.info("The app uses status_message field for categorization instead")
            return True

    except Exception as e:
        logger.error(f"❌ Error checking member_categories table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("MESSAGING & CAMPAIGN FUNCTIONALITY TESTS")
    logger.info("=" * 80)

    # Test 1: ClubOS message pulling
    test1_success = test_clubos_message_pulling()

    # Test 2: Campaign categories
    test2_success = test_campaign_categories()

    # Test 3: Database message storage
    test3_success = test_database_message_storage()

    # Test 4: Member categories table
    test4_success = test_member_categories_table()

    logger.info("=" * 80)
    logger.info("TEST RESULTS")
    logger.info("=" * 80)
    logger.info(f"Test 1 (ClubOS Message Pulling): {'✅ PASS' if test1_success else '❌ FAIL'}")
    logger.info(f"Test 2 (Campaign Categories): {'✅ PASS' if test2_success else '❌ FAIL'}")
    logger.info(f"Test 3 (Database Messages): {'✅ PASS' if test3_success else '❌ FAIL'}")
    logger.info(f"Test 4 (Member Categories): {'✅ PASS' if test4_success else '❌ FAIL'}")

    if test1_success and test2_success:
        logger.info("\n🎉 Core messaging and campaign functionality is working!")
    else:
        logger.error("\n⚠️ Some tests failed. See details above")

    logger.info("\n📝 RECOMMENDATIONS:")
    if not test1_success:
        logger.info("  - Check ClubOS credentials in secure secrets")
        logger.info("  - Verify ClubOS API is accessible")
    if not test2_success:
        logger.info("  - Run 'python fix_addresses_and_sync.py' to sync members")
        logger.info("  - Check that members have proper status_message values")
    if not test3_success:
        logger.info("  - Click 'Sync Messages' button in the messaging page")
        logger.info("  - Or wait for the first message to populate the table")
