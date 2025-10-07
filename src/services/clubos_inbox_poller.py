#!/usr/bin/env python3
"""
ClubOS Inbox Polling Service
Background service that polls ClubOS /action/Dashboard/messages endpoint
for real-time message synchronization
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
from threading import Thread, Event

logger = logging.getLogger(__name__)

class ClubOSInboxPoller:
    """
    Background polling service for ClubOS inbox
    Polls /action/Dashboard/messages endpoint at regular intervals
    """

    def __init__(self,
                 clubos_client,
                 inbox_parser,
                 inbox_db_schema,
                 poll_interval: int = 10):
        """
        Initialize inbox poller

        Args:
            clubos_client: ClubOSMessagingClient instance
            inbox_parser: ClubOSInboxParser instance
            inbox_db_schema: InboxDatabaseSchema instance
            poll_interval: Polling interval in seconds (default: 10)
        """
        self.clubos_client = clubos_client
        self.inbox_parser = inbox_parser
        self.inbox_db_schema = inbox_db_schema
        self.poll_interval = poll_interval

        # Polling state
        self.is_polling = False
        self.stop_event = Event()
        self.poll_thread = None
        self.last_sync_time = None
        self.last_message_count = 0

        # Callbacks for real-time notifications
        self.on_new_messages_callbacks: List[Callable] = []
        self.on_poll_complete_callbacks: List[Callable] = []
        self.on_error_callbacks: List[Callable] = []

        # Statistics
        self.stats = {
            'total_polls': 0,
            'successful_polls': 0,
            'failed_polls': 0,
            'messages_fetched': 0,
            'last_poll_time': None,
            'last_error': None
        }

    def start(self, owner_id: str = None):
        """
        Start the polling service in background thread

        Args:
            owner_id: Optional owner ID to poll messages for
        """
        if self.is_polling:
            logger.warning("⚠️ Polling service already running")
            return

        logger.info(f"🚀 Starting ClubOS inbox polling service (interval: {self.poll_interval}s)")
        self.is_polling = True
        self.stop_event.clear()

        # Start polling in background thread
        self.poll_thread = Thread(target=self._poll_loop, args=(owner_id,), daemon=True)
        self.poll_thread.start()

    def stop(self):
        """Stop the polling service"""
        if not self.is_polling:
            logger.warning("⚠️ Polling service not running")
            return

        logger.info("🛑 Stopping ClubOS inbox polling service...")
        self.is_polling = False
        self.stop_event.set()

        # Wait for thread to finish
        if self.poll_thread:
            self.poll_thread.join(timeout=5)

        logger.info("✅ Polling service stopped")

    def _poll_loop(self, owner_id: str = None):
        """
        Main polling loop (runs in background thread)

        Args:
            owner_id: Optional owner ID to poll messages for
        """
        logger.info("📡 Polling loop started")

        while self.is_polling and not self.stop_event.is_set():
            try:
                # Perform poll
                new_messages = self._poll_inbox(owner_id)

                # Update statistics
                self.stats['total_polls'] += 1
                self.stats['successful_polls'] += 1
                self.stats['messages_fetched'] += len(new_messages)
                self.stats['last_poll_time'] = datetime.now().isoformat()

                # Trigger callbacks if new messages found
                if new_messages:
                    logger.info(f"📬 Found {len(new_messages)} new messages")
                    self._trigger_new_messages_callbacks(new_messages)
                else:
                    logger.debug("📭 No new messages found")

                # Trigger poll complete callbacks
                self._trigger_poll_complete_callbacks({
                    'new_messages_count': len(new_messages),
                    'total_messages': self.last_message_count,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"❌ Error in polling loop: {e}")
                self.stats['failed_polls'] += 1
                self.stats['last_error'] = str(e)
                self._trigger_error_callbacks(e)

            # Wait for next poll interval
            self.stop_event.wait(self.poll_interval)

        logger.info("📡 Polling loop ended")

    def _poll_inbox(self, owner_id: str = None) -> List[Dict]:
        """
        Poll ClubOS inbox for new messages

        Args:
            owner_id: Optional owner ID

        Returns:
            List of new messages
        """
        try:
            # Add timestamp parameter to prevent caching (like ClubOS web interface)
            timestamp_ms = int(time.time() * 1000)

            # Fetch inbox HTML from ClubOS
            logger.debug(f"🔄 Polling ClubOS inbox (timestamp: {timestamp_ms})")

            # Use the existing messaging client's get_messages method
            # which internally calls /action/Dashboard/messages
            raw_html = self._fetch_inbox_html(owner_id, timestamp_ms)

            if not raw_html:
                logger.warning("⚠️ No HTML content received from ClubOS")
                return []

            # Parse HTML to extract messages
            messages = self.inbox_parser.parse_inbox_html(raw_html, owner_id)

            # Filter to only NEW messages (not already in database)
            new_messages = self._filter_new_messages(messages)

            # Save new messages to database
            for message in new_messages:
                self.inbox_db_schema.save_message(message)

            self.last_sync_time = datetime.now()
            self.last_message_count = len(messages)

            return new_messages

        except Exception as e:
            logger.error(f"❌ Error polling inbox: {e}")
            raise

    def _fetch_inbox_html(self, owner_id: str, timestamp_ms: int) -> str:
        """
        Fetch raw inbox HTML from ClubOS

        Args:
            owner_id: Owner ID
            timestamp_ms: Timestamp in milliseconds

        Returns:
            Raw HTML string
        """
        try:
            # Authenticate if needed
            if not self.clubos_client.authenticated:
                logger.info("🔐 Authenticating ClubOS client...")
                if not self.clubos_client.authenticate():
                    raise Exception("ClubOS authentication failed")

            # Build the inbox URL with timestamp parameter
            inbox_url = f"{self.clubos_client.base_url}/action/Dashboard/messages?_={timestamp_ms}"

            # Make GET request
            headers = {
                "Accept": "text/html, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.clubos_client.base_url}/action/Dashboard/view",
            }

            response = self.clubos_client.session.get(
                inbox_url,
                headers=headers,
                timeout=30,
                verify=False
            )

            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"❌ Failed to fetch inbox: HTTP {response.status_code}")
                return ""

        except Exception as e:
            logger.error(f"❌ Error fetching inbox HTML: {e}")
            raise

    def _filter_new_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Filter messages to only include NEW messages not in database

        Args:
            messages: List of parsed messages

        Returns:
            List of new messages
        """
        new_messages = []

        try:
            # Get existing message IDs from database
            with self.inbox_db_schema.db_manager.get_cursor() as cursor:
                cursor.execute("SELECT message_id FROM inbox_messages")
                existing_ids = {row[0] for row in cursor.fetchall()}

            # Filter to only messages not in database
            for message in messages:
                message_id = message.get('id') or message.get('message_id')
                if message_id and message_id not in existing_ids:
                    new_messages.append(message)

        except Exception as e:
            logger.error(f"❌ Error filtering new messages: {e}")
            # If error, return all messages as potentially new
            return messages

        return new_messages

    def register_new_messages_callback(self, callback: Callable):
        """
        Register callback to be called when new messages are found

        Args:
            callback: Function to call with new_messages list
        """
        self.on_new_messages_callbacks.append(callback)
        logger.info(f"✅ Registered new messages callback: {callback.__name__}")

    def register_poll_complete_callback(self, callback: Callable):
        """
        Register callback to be called after each poll completes

        Args:
            callback: Function to call with poll stats dict
        """
        self.on_poll_complete_callbacks.append(callback)
        logger.info(f"✅ Registered poll complete callback: {callback.__name__}")

    def register_error_callback(self, callback: Callable):
        """
        Register callback to be called when poll errors occur

        Args:
            callback: Function to call with exception
        """
        self.on_error_callbacks.append(callback)
        logger.info(f"✅ Registered error callback: {callback.__name__}")

    def _trigger_new_messages_callbacks(self, new_messages: List[Dict]):
        """Trigger all new messages callbacks"""
        for callback in self.on_new_messages_callbacks:
            try:
                callback(new_messages)
            except Exception as e:
                logger.error(f"❌ Error in new messages callback {callback.__name__}: {e}")

    def _trigger_poll_complete_callbacks(self, poll_stats: Dict):
        """Trigger all poll complete callbacks"""
        for callback in self.on_poll_complete_callbacks:
            try:
                callback(poll_stats)
            except Exception as e:
                logger.error(f"❌ Error in poll complete callback {callback.__name__}: {e}")

    def _trigger_error_callbacks(self, error: Exception):
        """Trigger all error callbacks"""
        for callback in self.on_error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"❌ Error in error callback {callback.__name__}: {e}")

    def get_stats(self) -> Dict:
        """Get polling statistics"""
        return {
            **self.stats,
            'is_polling': self.is_polling,
            'poll_interval': self.poll_interval,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'last_message_count': self.last_message_count
        }

    def poll_now(self, owner_id: str = None) -> List[Dict]:
        """
        Perform immediate poll (manual trigger)

        Args:
            owner_id: Optional owner ID

        Returns:
            List of new messages found
        """
        logger.info("⚡ Manual poll triggered")
        return self._poll_inbox(owner_id)
