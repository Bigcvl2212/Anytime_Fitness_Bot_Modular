#!/usr/bin/env python3
"""
Database Cleanup Script for Messages
Clears old corrupted message data so startup sync can repopulate with correct data
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_message_database():
    """Clear messages table to allow fresh sync with correct data"""
    try:
        logger.info("🔧 Starting message database cleanup...")

        # Initialize database manager
        db_manager = DatabaseManager()

        # Get current message count
        current_messages = db_manager.execute_query('''
            SELECT COUNT(*) as count FROM messages
        ''')

        if current_messages and len(current_messages) > 0:
            count = current_messages[0].get('count', 0)
            logger.info(f"📊 Found {count} messages in database")

            if count > 0:
                # Ask for confirmation
                response = input(f"\n⚠️  This will DELETE all {count} messages from the database.\n"
                               "They will be re-synced from ClubOS on next app startup.\n"
                               "Continue? (yes/no): ")

                if response.lower() != 'yes':
                    logger.info("❌ Operation cancelled by user")
                    return

                # Clear messages table
                db_manager.execute_query('DELETE FROM messages')
                logger.info("✅ Cleared all messages from database")

                # Verify
                remaining = db_manager.execute_query('SELECT COUNT(*) as count FROM messages')
                if remaining and len(remaining) > 0:
                    final_count = remaining[0].get('count', 0)
                    logger.info(f"📊 Messages remaining: {final_count}")

                logger.info("\n✅ Database cleanup complete!")
                logger.info("📋 Next steps:")
                logger.info("   1. Restart the dashboard app")
                logger.info("   2. Wait for startup sync to complete")
                logger.info("   3. Check messaging inbox - should show correct dates (2025) and full history")
            else:
                logger.info("📭 No messages found in database - nothing to clean")

    except Exception as e:
        logger.error(f"❌ Error during database cleanup: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    fix_message_database()
