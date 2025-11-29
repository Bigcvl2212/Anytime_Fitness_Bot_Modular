#!/usr/bin/env python3
"""
Inbox Database Schema
Wrapper for database operations related to AI inbox processing
"""

import logging

logger = logging.getLogger(__name__)


class InboxDatabaseSchema:
    """
    Database schema wrapper for inbox AI operations
    Provides access to database manager for AI response logging and statistics
    """

    def __init__(self, db_manager):
        """
        Initialize inbox database schema

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        logger.info("✅ Inbox Database Schema initialized")

    def ensure_tables(self):
        """
        Ensure all required tables exist for inbox AI operations
        This is typically handled by migrations, but we check here as well
        """
        try:
            with self.db_manager.get_cursor() as cursor:
                # Check if ai_response_log table exists
                if self.db_manager.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = 'ai_response_log'
                        )
                    """)
                else:
                    cursor.execute("""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name='ai_response_log'
                    """)

                table_exists = cursor.fetchone()

                if not table_exists or (isinstance(table_exists, tuple) and not table_exists[0]):
                    logger.warning("⚠️ ai_response_log table does not exist - AI logging will be limited")
                else:
                    logger.info("✅ AI response logging tables verified")

        except Exception as e:
            logger.warning(f"⚠️ Could not verify AI tables: {e}")
