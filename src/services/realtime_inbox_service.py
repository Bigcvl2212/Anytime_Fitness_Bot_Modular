#!/usr/bin/env python3
"""
Real-Time Inbox Service
Main orchestration service that integrates all components:
- ClubOS inbox polling
- HTML parsing
- Database storage
- WebSocket broadcasting
- AI auto-responses
"""

import logging
import asyncio
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealtimeInboxService:
    """
    Orchestrates real-time inbox synchronization and AI auto-responses
    This is the main service that brings all components together
    """

    def __init__(self,
                 database_manager,
                 clubos_messaging_client,
                 ai_service_manager):
        """
        Initialize the real-time inbox service

        Args:
            database_manager: DatabaseManager instance
            clubos_messaging_client: ClubOSMessagingClient instance
            ai_service_manager: AIServiceManager instance
        """
        self.db_manager = database_manager
        self.clubos_client = clubos_messaging_client
        self.ai_service = ai_service_manager

        # Initialize components
        self._initialize_components()

        # Service state
        self.is_running = False
        self.owner_id = None

        logger.info("✅ Real-Time Inbox Service initialized")

    def _initialize_components(self):
        """Initialize all service components"""
        from .clubos_inbox_parser import ClubOSInboxParser
        from .inbox_database_schema import InboxDatabaseSchema
        from .clubos_inbox_poller import ClubOSInboxPoller
        from .ai.inbox_ai_agent import InboxAIAgent

        # Initialize inbox parser
        self.inbox_parser = ClubOSInboxParser()
        logger.info("✅ Inbox parser initialized")

        # Initialize database schema
        self.inbox_db = InboxDatabaseSchema(self.db_manager)
        self.inbox_db.create_inbox_tables()
        logger.info("✅ Inbox database schema initialized")

        # Initialize AI agent
        self.ai_agent = InboxAIAgent(
            self.ai_service,
            self.clubos_client,
            self.inbox_db
        )
        logger.info("✅ AI agent initialized")

        # Initialize poller (default 10 second interval)
        self.poller = ClubOSInboxPoller(
            self.clubos_client,
            self.inbox_parser,
            self.inbox_db,
            poll_interval=10
        )
        logger.info("✅ Inbox poller initialized")

        # Register callbacks
        self._register_callbacks()

    def _register_callbacks(self):
        """Register callbacks for poller events"""
        # When new messages are found, trigger AI processing and WebSocket broadcast
        self.poller.register_new_messages_callback(self._on_new_messages)

        # When poll completes, broadcast stats
        self.poller.register_poll_complete_callback(self._on_poll_complete)

        # When errors occur, broadcast error
        self.poller.register_error_callback(self._on_error)

        logger.info("✅ Callbacks registered")

    def _on_new_messages(self, new_messages: list):
        """
        Callback when new messages are found

        Args:
            new_messages: List of new message dictionaries
        """
        try:
            logger.info(f"📬 Processing {len(new_messages)} new messages")

            # Broadcast to WebSocket clients
            self._broadcast_new_messages(new_messages)

            # Process with AI agent (async)
            asyncio.create_task(self.ai_agent.process_new_messages(new_messages))

        except Exception as e:
            logger.error(f"❌ Error in _on_new_messages callback: {e}")

    def _on_poll_complete(self, poll_stats: dict):
        """
        Callback when poll completes

        Args:
            poll_stats: Poll statistics dictionary
        """
        try:
            logger.debug(f"📊 Poll complete: {poll_stats}")

            # Broadcast poll update to WebSocket clients
            self._broadcast_poll_update(poll_stats)

        except Exception as e:
            logger.error(f"❌ Error in _on_poll_complete callback: {e}")

    def _on_error(self, error: Exception):
        """
        Callback when polling error occurs

        Args:
            error: Exception that occurred
        """
        try:
            logger.error(f"❌ Polling error: {error}")

            # Broadcast error to WebSocket clients
            self._broadcast_error(str(error))

        except Exception as e:
            logger.error(f"❌ Error in _on_error callback: {e}")

    def _broadcast_new_messages(self, messages: list):
        """Broadcast new messages via WebSocket"""
        try:
            # Import here to avoid circular dependency
            from ..routes.inbox_websocket import broadcast_new_messages

            broadcast_new_messages(messages, self.owner_id)

        except Exception as e:
            logger.error(f"❌ Error broadcasting new messages: {e}")

    def _broadcast_poll_update(self, poll_stats: dict):
        """Broadcast poll update via WebSocket"""
        try:
            from ..routes.inbox_websocket import broadcast_poll_update

            broadcast_poll_update(poll_stats, self.owner_id)

        except Exception as e:
            logger.error(f"❌ Error broadcasting poll update: {e}")

    def _broadcast_error(self, error_message: str):
        """Broadcast error via WebSocket"""
        try:
            from ..routes.inbox_websocket import broadcast_error

            broadcast_error(error_message, self.owner_id)

        except Exception as e:
            logger.error(f"❌ Error broadcasting error: {e}")

    def start(self, owner_id: str = None):
        """
        Start the real-time inbox service

        Args:
            owner_id: Optional owner ID to track messages for
        """
        if self.is_running:
            logger.warning("⚠️ Real-time inbox service already running")
            return

        logger.info("🚀 Starting Real-Time Inbox Service...")

        self.owner_id = owner_id
        self.is_running = True

        # Authenticate ClubOS client if needed
        if not self.clubos_client.authenticated:
            logger.info("🔐 Authenticating ClubOS client...")
            if not self.clubos_client.authenticate():
                logger.error("❌ ClubOS authentication failed")
                self.is_running = False
                return

        # Start polling
        self.poller.start(owner_id)

        logger.info("✅ Real-Time Inbox Service started successfully")

    def stop(self):
        """Stop the real-time inbox service"""
        if not self.is_running:
            logger.warning("⚠️ Real-time inbox service not running")
            return

        logger.info("🛑 Stopping Real-Time Inbox Service...")

        # Stop polling
        self.poller.stop()

        self.is_running = False

        logger.info("✅ Real-Time Inbox Service stopped")

    def manual_sync(self, owner_id: str = None):
        """
        Perform manual inbox sync

        Args:
            owner_id: Optional owner ID

        Returns:
            List of new messages found
        """
        logger.info("⚡ Manual sync triggered")

        # Authenticate if needed
        if not self.clubos_client.authenticated:
            logger.info("🔐 Authenticating ClubOS client...")
            if not self.clubos_client.authenticate():
                logger.error("❌ ClubOS authentication failed")
                return []

        # Perform immediate poll
        return self.poller.poll_now(owner_id or self.owner_id)

    def get_unread_messages(self, owner_id: str = None, limit: int = 100):
        """
        Get unread messages from database

        Args:
            owner_id: Optional owner ID
            limit: Maximum number of messages to return

        Returns:
            List of unread message dictionaries
        """
        return self.inbox_db.get_unread_messages(owner_id, limit)

    def get_conversation(self, conversation_id: str):
        """
        Get all messages in a conversation

        Args:
            conversation_id: Conversation ID

        Returns:
            List of message dictionaries
        """
        return self.inbox_db.get_conversation(conversation_id)

    def mark_message_read(self, message_id: str):
        """
        Mark a message as read

        Args:
            message_id: Message ID

        Returns:
            True if successful, False otherwise
        """
        return self.inbox_db.mark_message_read(message_id)

    def enable_ai_auto_response(self, enabled: bool = True):
        """
        Enable or disable AI auto-responses

        Args:
            enabled: True to enable, False to disable
        """
        self.ai_agent.set_auto_response_enabled(enabled)

    def set_ai_confidence_threshold(self, threshold: float):
        """
        Set AI confidence threshold for auto-responses

        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        self.ai_agent.set_confidence_threshold(threshold)

    def get_service_stats(self):
        """
        Get comprehensive service statistics

        Returns:
            Dictionary with service stats
        """
        return {
            'is_running': self.is_running,
            'owner_id': self.owner_id,
            'poller_stats': self.poller.get_stats(),
            'ai_stats': self.ai_agent.get_ai_stats(),
            'service_started_at': None
        }


# Global service instance (initialized by main app)
_realtime_inbox_service = None


def get_realtime_inbox_service():
    """Get the global real-time inbox service instance"""
    global _realtime_inbox_service
    if _realtime_inbox_service is None:
        logger.warning("⚠️ Real-time inbox service not initialized")
    return _realtime_inbox_service


def initialize_realtime_inbox_service(database_manager,
                                       clubos_messaging_client,
                                       ai_service_manager):
    """
    Initialize the global real-time inbox service

    Args:
        database_manager: DatabaseManager instance
        clubos_messaging_client: ClubOSMessagingClient instance
        ai_service_manager: AIServiceManager instance

    Returns:
        RealtimeInboxService instance
    """
    global _realtime_inbox_service

    if _realtime_inbox_service is not None:
        logger.warning("⚠️ Real-time inbox service already initialized")
        return _realtime_inbox_service

    _realtime_inbox_service = RealtimeInboxService(
        database_manager,
        clubos_messaging_client,
        ai_service_manager
    )

    logger.info("✅ Global real-time inbox service initialized")
    return _realtime_inbox_service
