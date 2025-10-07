#!/usr/bin/env python3
"""
Inbox Database Schema
Creates and manages inbox/message database tables for real-time messaging
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class InboxDatabaseSchema:
    """Manages inbox and messaging database tables"""

    def __init__(self, db_manager):
        """
        Initialize with database manager

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def create_inbox_tables(self):
        """Create all inbox-related database tables"""
        try:
            logger.info("🔧 Creating inbox database tables...")

            # Create inbox messages table
            self._create_inbox_messages_table()

            # Create conversations table
            self._create_conversations_table()

            # Create message sync status table
            self._create_message_sync_status_table()

            # Create AI auto-response log table
            self._create_ai_response_log_table()

            logger.info("✅ All inbox tables created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating inbox tables: {e}")
            return False

    def _create_inbox_messages_table(self):
        """Create inbox messages table for storing all ClubOS messages"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS inbox_messages (
                    id SERIAL PRIMARY KEY,
                    message_id TEXT UNIQUE NOT NULL,
                    conversation_id TEXT,
                    sender_id TEXT,
                    sender_name TEXT,
                    recipient_id TEXT,
                    recipient_name TEXT,
                    message_type TEXT DEFAULT 'inbox_message',
                    content TEXT,
                    snippet TEXT,
                    timestamp TIMESTAMP,
                    direction TEXT DEFAULT 'incoming',
                    is_read BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'received',
                    owner_id TEXT,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS inbox_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    conversation_id TEXT,
                    sender_id TEXT,
                    sender_name TEXT,
                    recipient_id TEXT,
                    recipient_name TEXT,
                    message_type TEXT DEFAULT 'inbox_message',
                    content TEXT,
                    snippet TEXT,
                    timestamp TIMESTAMP,
                    direction TEXT DEFAULT 'incoming',
                    is_read INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'received',
                    owner_id TEXT,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)

            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inbox_messages_conversation
                ON inbox_messages(conversation_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inbox_messages_sender
                ON inbox_messages(sender_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inbox_messages_timestamp
                ON inbox_messages(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_inbox_messages_is_read
                ON inbox_messages(is_read)
            """)

            cursor.connection.commit()
        logger.info("✅ Inbox messages table created")

    def _create_conversations_table(self):
        """Create conversations table for tracking message threads"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT UNIQUE NOT NULL,
                    member_id TEXT NOT NULL,
                    member_name TEXT,
                    last_message_id TEXT,
                    last_message_snippet TEXT,
                    last_message_timestamp TIMESTAMP,
                    unread_count INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    member_id TEXT NOT NULL,
                    member_name TEXT,
                    last_message_id TEXT,
                    last_message_snippet TEXT,
                    last_message_timestamp TIMESTAMP,
                    unread_count INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_member
                ON conversations(member_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated
                ON conversations(updated_at DESC)
            """)

            cursor.connection.commit()
        logger.info("✅ Conversations table created")

    def _create_message_sync_status_table(self):
        """Create table to track message sync status"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS message_sync_status (
                    id SERIAL PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    last_sync_timestamp TIMESTAMP,
                    last_message_id TEXT,
                    sync_status TEXT DEFAULT 'idle',
                    messages_synced INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS message_sync_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner_id TEXT NOT NULL,
                    last_sync_timestamp TIMESTAMP,
                    last_message_id TEXT,
                    sync_status TEXT DEFAULT 'idle',
                    messages_synced INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sync_status_owner
                ON message_sync_status(owner_id)
            """)
            cursor.connection.commit()
        logger.info("✅ Message sync status table created")

    def _create_ai_response_log_table(self):
        """Create table to log AI auto-responses"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS ai_response_log (
                    id SERIAL PRIMARY KEY,
                    original_message_id TEXT NOT NULL,
                    conversation_id TEXT,
                    member_id TEXT,
                    member_name TEXT,
                    ai_response TEXT,
                    ai_intent TEXT,
                    ai_confidence REAL,
                    sent_successfully BOOLEAN DEFAULT FALSE,
                    response_message_id TEXT,
                    error TEXT,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS ai_response_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_message_id TEXT NOT NULL,
                    conversation_id TEXT,
                    member_id TEXT,
                    member_name TEXT,
                    ai_response TEXT,
                    ai_intent TEXT,
                    ai_confidence REAL,
                    sent_successfully INTEGER DEFAULT 0,
                    response_message_id TEXT,
                    error TEXT,
                    metadata TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_response_member
                ON ai_response_log(member_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_response_conversation
                ON ai_response_log(conversation_id)
            """)
            cursor.connection.commit()
        logger.info("✅ AI response log table created")

    def save_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Save a message to the database

        Args:
            message_data: Dictionary containing message data

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_cursor() as cursor:
                if self.db_manager.db_type == 'postgresql':
                    sql = """
                        INSERT INTO inbox_messages (
                            message_id, conversation_id, sender_id, sender_name,
                            recipient_id, recipient_name, message_type, content,
                            snippet, timestamp, direction, is_read, status, owner_id, metadata
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (message_id) DO UPDATE SET
                            is_read = EXCLUDED.is_read,
                            status = EXCLUDED.status,
                            updated_at = CURRENT_TIMESTAMP
                    """
                else:  # SQLite
                    sql = """
                        INSERT OR REPLACE INTO inbox_messages (
                            message_id, conversation_id, sender_id, sender_name,
                            recipient_id, recipient_name, message_type, content,
                            snippet, timestamp, direction, is_read, status, owner_id, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

                params = (
                    message_data.get('id') or message_data.get('message_id'),
                    message_data.get('conversation_id'),
                    message_data.get('sender_id'),
                    message_data.get('sender_name'),
                    message_data.get('recipient_id'),
                    message_data.get('recipient_name'),
                    message_data.get('message_type', 'inbox_message'),
                    message_data.get('content'),
                    message_data.get('snippet'),
                    message_data.get('timestamp'),
                    message_data.get('direction', 'incoming'),
                    1 if message_data.get('is_read', False) else 0,
                    message_data.get('status', 'received'),
                    message_data.get('owner_id'),
                    str(message_data.get('metadata', {}))
                )

                cursor.execute(sql, params)
                cursor.connection.commit()
                return True

        except Exception as e:
            logger.error(f"❌ Error saving message: {e}")
            return False

    def get_unread_messages(self, owner_id: str = None, limit: int = 100) -> List[Dict]:
        """Get unread messages"""
        try:
            with self.db_manager.get_cursor() as cursor:
                if owner_id:
                    sql = """
                        SELECT * FROM inbox_messages
                        WHERE is_read = 0 AND owner_id = ?
                        ORDER BY timestamp DESC LIMIT ?
                    """
                    cursor.execute(sql, (owner_id, limit))
                else:
                    sql = """
                        SELECT * FROM inbox_messages
                        WHERE is_read = 0
                        ORDER BY timestamp DESC LIMIT ?
                    """
                    cursor.execute(sql, (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error getting unread messages: {e}")
            return []

    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get all messages in a conversation"""
        try:
            with self.db_manager.get_cursor() as cursor:
                sql = """
                    SELECT * FROM inbox_messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                """
                cursor.execute(sql, (conversation_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"❌ Error getting conversation: {e}")
            return []

    def mark_message_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            with self.db_manager.get_cursor() as cursor:
                sql = """
                    UPDATE inbox_messages
                    SET is_read = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE message_id = ?
                """
                cursor.execute(sql, (message_id,))
                cursor.connection.commit()
                return True

        except Exception as e:
            logger.error(f"❌ Error marking message read: {e}")
            return False
