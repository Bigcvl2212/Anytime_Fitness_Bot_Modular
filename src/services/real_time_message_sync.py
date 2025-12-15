#!/usr/bin/env python3
"""
Real-Time Message Sync Service
Continuously polls ClubOS for new messages and broadcasts to UI in real-time
Part of Phase 1: Inbox Foundation for Autonomous AI Agent
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Thread, Event

logger = logging.getLogger(__name__)

class RealTimeMessageSync:
    """
    Continuously polls ClubOS for new messages
    Similar to how ClubOS web interface works
    """
    
    def __init__(self, clubos_client, db_manager, socketio=None, poll_interval=10, unified_ai_agent=None):
        """
        Initialize real-time message sync service

        Args:
            clubos_client: ClubOS messaging client instance
            db_manager: Database manager instance
            socketio: Flask-SocketIO instance for broadcasting updates
            poll_interval: Polling interval in seconds (default: 10)
            unified_ai_agent: UnifiedGymAgent instance for AI processing (optional)
        """
        self.clubos_client = clubos_client
        self.db_manager = db_manager
        self.socketio = socketio
        self.poll_interval = poll_interval
        self.unified_ai_agent = unified_ai_agent
        
        self.running = False
        self.stop_event = Event()
        self.thread = None

        # AI Processing Control - DISABLED BY DEFAULT
        self.ai_enabled = False

        # Track last seen message IDs per owner to detect new messages
        self.last_message_ids = {}

        # Track owner IDs to poll - will be populated dynamically
        self.owner_ids = set()

        # Auto-detect and add logged-in manager's user ID
        self._auto_configure_polling()

        logger.info(f"🔄 Real-Time Message Sync initialized (poll interval: {poll_interval}s)")
        logger.info(f"🤖 AI Auto-Processing: {'ENABLED' if self.ai_enabled else 'DISABLED (use enable_ai() to activate)'}")
    
    def _auto_configure_polling(self) -> None:
        """
        Automatically configure polling based on authenticated user.
        Detects the logged-in manager and adds their inbox to polling.
        """
        try:
            # Get the logged-in user ID from the authenticated ClubOS client
            if hasattr(self.clubos_client, 'logged_in_user_id') and self.clubos_client.logged_in_user_id:
                manager_id = str(self.clubos_client.logged_in_user_id)
                self.owner_ids.add(manager_id)
                logger.info(f"✅ Auto-configured polling for logged-in manager: {manager_id}")
                
                # Log additional context if available
                if hasattr(self.clubos_client, 'club_id'):
                    logger.info(f"📍 Club ID: {self.clubos_client.club_id}")
                if hasattr(self.clubos_client, 'club_location_id'):
                    logger.info(f"📍 Location ID: {self.clubos_client.club_location_id}")
                
            else:
                logger.warning("⚠️ Could not auto-detect logged-in user - polling will need manual configuration")
                logger.warning("💡 Use add_owner(user_id) to manually configure polling")
                
        except Exception as e:
            logger.error(f"❌ Error auto-configuring polling: {e}")
            logger.warning("💡 Polling will need manual configuration via add_owner(user_id)")
    
    def add_owner(self, owner_id: str) -> None:
        """Add an owner ID to poll for messages"""
        self.owner_ids.add(owner_id)
        logger.info(f"📝 Added owner {owner_id} to message polling")
    
    def remove_owner(self, owner_id: str) -> None:
        """Remove an owner ID from polling"""
        self.owner_ids.discard(owner_id)
        logger.info(f"📝 Removed owner {owner_id} from message polling")
    
    def start_polling(self) -> None:
        """Start continuous background polling in a separate thread"""
        if self.running:
            logger.warning("⚠️ Polling already running")
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Start polling in background thread
        self.thread = Thread(target=self._polling_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Real-time message polling started")
    
    def stop_polling(self) -> None:
        """Stop background polling"""
        if not self.running:
            return
        
        logger.info("⏹️ Stopping real-time message polling...")
        self.running = False
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("✅ Real-time message polling stopped")
    
    def _polling_loop(self) -> None:
        """Main polling loop (runs in background thread)"""
        logger.info("🔄 Message polling loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Poll for each owner
                for owner_id in list(self.owner_ids):  # Create copy to avoid modification during iteration
                    if not self.running:
                        break
                    
                    try:
                        new_messages = self._fetch_new_messages(owner_id)
                        
                        if new_messages:
                            # Store in database
                            self._store_messages(new_messages)

                            # Broadcast to web UI
                            self._broadcast_to_ui(new_messages)

                            # PHASE 2: Trigger AI processing with Unified Agent
                            self._trigger_ai_processing(new_messages)

                            logger.info(f"📨 Processed {len(new_messages)} new messages for owner {owner_id}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error polling owner {owner_id}: {e}")
                
                # Also process any existing unprocessed messages (for retry/recovery)
                self._process_unprocessed_messages()
                
                # Wait for next poll interval
                self.stop_event.wait(self.poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Polling loop error: {e}")
                # Back off on error
                self.stop_event.wait(30)
        
        logger.info("🔄 Message polling loop stopped")
    
    def _fetch_new_messages(self, owner_id: str) -> List[Dict]:
        """
        Fetch only NEW messages since last check
        This is incremental sync, not full refresh
        """
        try:
            # Get all messages from ClubOS
            logger.info(f"🔄 Polling ClubOS for messages (owner: {owner_id})...")
            all_messages = self.clubos_client.get_messages(owner_id=owner_id)

            if not all_messages:
                logger.info(f"📭 No messages returned from ClubOS")
                return []

            logger.info(f"📬 ClubOS returned {len(all_messages)} total messages")

            # IMPROVED LOGIC: Check database for existing message IDs to avoid duplicates
            try:
                existing_rows = self.db_manager.execute_query("""
                    SELECT id FROM messages
                """, fetch_all=True)  # Get ALL message IDs, not just for this owner
                
                existing_ids = set()
                if existing_rows:
                    for row in existing_rows:
                        if isinstance(row, dict):
                            existing_ids.add(row.get('id'))
                        else:
                            existing_ids.add(row[0])
                logger.info(f"📊 Database has {len(existing_ids)} existing message IDs")
            except Exception as e:
                logger.warning(f"⚠️ Could not check existing messages: {e}")
                existing_ids = set()

            # Filter to only messages not yet in database
            new_messages = []
            
            # Debug: Log first few message IDs from ClubOS
            sample_clubos_ids = [m.get('id') or m.get('message_id') for m in all_messages[:3]]
            logger.info(f"📋 Sample ClubOS message IDs: {sample_clubos_ids}")
            
            # Debug: Log first few message IDs from DB
            sample_db_ids = list(existing_ids)[:3]
            logger.info(f"📋 Sample DB message IDs: {sample_db_ids}")

            for msg in all_messages:
                msg_id = msg.get('id') or msg.get('message_id')

                # If this message ID is not in our database, it's new
                if msg_id and msg_id not in existing_ids:
                    new_messages.append(msg)

            if new_messages:
                logger.info(f"📨 Found {len(new_messages)} NEW messages for owner {owner_id}")
                # Log first new message for debugging
                if new_messages:
                    first_msg = new_messages[0]
                    logger.info(f"   First new: {first_msg.get('from_user', 'Unknown')} - {first_msg.get('content', '')[:50]}...")
            else:
                # Debug: Check how many ClubOS IDs are actually in the existing_ids set
                clubos_ids_in_db = sum(1 for m in all_messages if (m.get('id') or m.get('message_id')) in existing_ids)
                logger.info(f"📭 No new messages - {clubos_ids_in_db}/{len(all_messages)} ClubOS IDs found in DB ({len(existing_ids)} total DB IDs)")

            return new_messages

        except Exception as e:
            logger.error(f"❌ Error fetching new messages for owner {owner_id}: {e}")
            return []
    
    def _store_messages(self, messages: List[Dict]) -> None:
        """Store new messages in database using the same schema as messaging.py"""
        try:
            for msg in messages:
                # Use the same ID from the message (already generated by clubos_messaging_client)
                message_id = msg.get('id') or msg.get('message_id')
                
                # Store in database with ai_processed = 0 (needs AI processing)
                # and status = 'unread' for genuinely new messages
                self.db_manager.execute_query('''
                    INSERT OR REPLACE INTO messages
                    (id, message_type, content, timestamp, from_user, to_user, status, owner_id,
                     delivery_status, channel, created_at, ai_processed, received_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                ''', (
                    message_id,
                    msg.get('message_type', 'clubos_message'),
                    msg.get('content', ''),
                    msg.get('timestamp', datetime.now().isoformat()),
                    msg.get('from_user', ''),
                    msg.get('to_user', ''),
                    'unread',  # New messages are always unread
                    msg.get('owner_id', ''),
                    'received',
                    'clubos',
                    datetime.now().isoformat(),
                    datetime.now().isoformat()  # received_at timestamp
                ))
            
            logger.info(f"💾 Stored {len(messages)} new messages (ai_processed=0, status=unread)")
            
        except Exception as e:
            logger.error(f"❌ Error storing messages: {e}")
    
    def _broadcast_to_ui(self, messages: List[Dict]) -> None:
        """Broadcast new messages to all connected clients via WebSocket"""
        try:
            if not self.socketio:
                return
            
            # Format messages for frontend
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    'id': msg.get('id') or msg.get('message_id'),
                    'content': msg.get('content', ''),
                    'from': msg.get('from_user', 'Unknown'),
                    'timestamp': msg.get('timestamp', ''),
                    'status': msg.get('status', 'unread'),
                    'type': msg.get('message_type', 'message')
                })
            
            # Broadcast to all connected clients
            self.socketio.emit('new_messages', {
                'messages': formatted_messages,
                'count': len(formatted_messages),
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"📡 Broadcast {len(formatted_messages)} messages to connected clients")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting to UI: {e}")
    
    def enable_ai(self) -> None:
        """Enable automatic AI processing of new messages"""
        self.ai_enabled = True
        logger.info("✅ AI Auto-Processing ENABLED")

    def disable_ai(self) -> None:
        """Disable automatic AI processing of new messages"""
        self.ai_enabled = False
        logger.info("⛔ AI Auto-Processing DISABLED")

    def _process_unprocessed_messages(self) -> None:
        """
        Process existing messages that have ai_processed = 0
        This handles retry/recovery for failed AI processing
        """
        if not self.ai_enabled:
            return
            
        if not hasattr(self, 'unified_ai_agent') or not self.unified_ai_agent:
            return
        
        try:
            # Get up to 5 unprocessed messages (rate limiting)
            # Only get recent messages (last 7 days) to avoid processing very old backlog
            unprocessed_rows = self.db_manager.execute_query("""
                SELECT id, from_user, content, member_id, timestamp
                FROM messages 
                WHERE ai_processed = 0 
                  AND from_user != 'Staff'
                  AND timestamp >= datetime('now', '-7 days')
                ORDER BY timestamp DESC
                LIMIT 5
            """, fetch_all=True)
            
            if not unprocessed_rows:
                return
                
            logger.info(f"🔄 Found {len(unprocessed_rows)} unprocessed messages to retry")
            
            # Convert rows to message dicts and process
            messages_to_process = []
            for row in unprocessed_rows:
                if isinstance(row, dict):
                    messages_to_process.append(row)
                else:
                    messages_to_process.append({
                        'id': row[0],
                        'from_user': row[1],
                        'content': row[2],
                        'member_id': row[3],
                        'timestamp': row[4]
                    })
            
            # Use existing AI processing logic
            self._trigger_ai_processing(messages_to_process)
            
        except Exception as e:
            logger.error(f"❌ Error processing unprocessed messages: {e}")

    def _trigger_ai_processing(self, messages: List[Dict]) -> None:
        """
        Automatically send new messages to Unified AI Agent
        PHASE 2 INTEGRATION - Now connected to unified_gym_agent.py
        """
        import time
        
        # Check if AI processing is enabled
        if not self.ai_enabled:
            logger.debug("⏸️ AI processing disabled - skipping")
            return

        if not hasattr(self, 'unified_ai_agent') or not self.unified_ai_agent:
            logger.debug("⚠️ No unified AI agent configured - skipping AI processing")
            return

        # Rate limiting: Only process up to 5 messages per batch to avoid API rate limits
        # Groq free tier is 30 RPM, so we need to be conservative
        messages_to_process = messages[:5]
        if len(messages) > 5:
            logger.info(f"⚠️ Rate limiting: Processing {len(messages_to_process)} of {len(messages)} messages")

        for i, msg in enumerate(messages_to_process):
            try:
                msg_id = msg.get('id') or msg.get('message_id')
                
                # Check if AI should process this message
                if not self._should_ai_respond(msg):
                    # Mark as processed even if AI shouldn't respond (avoid re-processing)
                    if msg_id:
                        self.db_manager.execute_query(
                            "UPDATE messages SET ai_processed = 1 WHERE id = ?",
                            (msg_id,)
                        )
                    continue

                logger.info(f"🤖 Triggering AI processing for message from {msg.get('from_user')}")

                # Process message asynchronously with unified AI agent
                import asyncio

                # Create event loop for async AI processing
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    self.unified_ai_agent.process_new_message(msg)
                )

                loop.close()

                # ONLY mark as processed if AI succeeded - leave unprocessed on failure so it can be retried
                if result.get('success'):
                    if msg_id:
                        ai_responded = 1 if result.get('responded') else 0
                        self.db_manager.execute_query(
                            "UPDATE messages SET ai_processed = 1, ai_responded = ? WHERE id = ?",
                            (ai_responded, msg_id)
                        )
                    
                    if result.get('responded'):
                        logger.info(f"✅ AI responded to {msg.get('from_user')}: {result.get('intent')}")
                    elif result.get('flagged_for_review'):
                        logger.info(f"🚩 Message flagged for human review: {result.get('reason')}")
                    if result.get('workflow_triggered'):
                        logger.info(f"🎯 Triggered workflow: {result.get('workflow_name')}")
                else:
                    # DON'T mark as processed on failure - message stays unread for retry
                    logger.error(f"❌ AI processing failed: {result.get('error')} - message will be retried")
                
                # Rate limiting delay between API calls (3 seconds = ~20 RPM, well under 30 RPM limit)
                if i < len(messages_to_process) - 1:
                    time.sleep(3)

            except Exception as e:
                # DON'T mark as processed on exception - message stays unread for retry
                logger.error(f"❌ AI processing error: {e} - message will be retried", exc_info=True)
    
    def _should_ai_respond(self, message: Dict) -> bool:
        """
        Determine if AI should process this message
        PHASE 2 INTEGRATION POINT - Currently basic logic
        """
        content = message.get('content', '').lower()
        from_user = message.get('from_user', '').lower()
        
        # Don't respond to system messages
        if message.get('message_type') in ['system', 'notification']:
            return False
        
        # Don't respond to messages from staff
        if from_user in ['staff', 'admin', 'system', 'j.mayo', 'jeremy mayo']:
            return False
        
        # CRITICAL: Don't respond to outbound/staff messages
        # These often show as from_user='Unknown' but contain staff name at START of content
        # ClubOS prepends sender name WITHOUT space before message: "Jeremy MayoCan I..."
        # So we need to check if content STARTS WITH staff name (case-insensitive)
        staff_names = ['jeremy mayo', 'j.mayo', 'j mayo', 'tyler']
        content_lower = content.lower()
        
        for staff_name in staff_names:
            # Check if message content STARTS with staff name
            # The name might be followed immediately by message text (no space)
            # e.g., "jeremy mayocan you help..." starts with "jeremy mayo"
            if content_lower.startswith(staff_name):
                logger.info(f"⏭️ Skipping staff outbound message (starts with '{staff_name}'): {content[:40]}...")
                return False
        
        # Don't respond to very short messages (likely incomplete)
        if len(content) < 5:
            return False
        
        # Respond to questions
        if any(q in content for q in ['?', 'how', 'when', 'what', 'where', 'why']):
            return True
        
        # Respond to common keywords
        if any(kw in content for kw in ['help', 'cancel', 'reschedule', 'confirm', 'change', 'appointment', 'schedule']):
            return True
        
        return False
    
    def sync_now(self, owner_id: str) -> Dict[str, Any]:
        """
        Manually trigger an immediate sync for an owner
        Returns sync results
        """
        try:
            logger.info(f"🔄 Manual sync requested for owner {owner_id}")
            
            new_messages = self._fetch_new_messages(owner_id)
            
            if new_messages:
                self._store_messages(new_messages)
                self._broadcast_to_ui(new_messages)
            
            return {
                'success': True,
                'message_count': len(new_messages),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Manual sync error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current polling status"""
        return {
            'running': self.running,
            'poll_interval': self.poll_interval,
            'owner_count': len(self.owner_ids),
            'owners': list(self.owner_ids),
            'last_message_ids': dict(self.last_message_ids)
        }
