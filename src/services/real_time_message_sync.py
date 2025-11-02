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
    
    def __init__(self, clubos_client, db_manager, socketio=None, poll_interval=10):
        """
        Initialize real-time message sync service
        
        Args:
            clubos_client: ClubOS messaging client instance
            db_manager: Database manager instance  
            socketio: Flask-SocketIO instance for broadcasting updates
            poll_interval: Polling interval in seconds (default: 10)
        """
        self.clubos_client = clubos_client
        self.db_manager = db_manager
        self.socketio = socketio
        self.poll_interval = poll_interval
        
        self.running = False
        self.stop_event = Event()
        self.thread = None
        
        # Track last seen message IDs per owner to detect new messages
        self.last_message_ids = {}
        
        # Track owner IDs to poll - will be populated dynamically
        self.owner_ids = set()
        
        # Auto-detect and add logged-in manager's user ID
        self._auto_configure_polling()
        
        logger.info(f"🔄 Real-Time Message Sync initialized (poll interval: {poll_interval}s)")
    
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
                            
                            # Trigger AI processing (Phase 2 integration point)
                            # self._trigger_ai_processing(new_messages)
                            
                            logger.info(f"📨 Processed {len(new_messages)} new messages for owner {owner_id}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error polling owner {owner_id}: {e}")
                
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
            all_messages = self.clubos_client.get_messages(owner_id=owner_id)
            
            if not all_messages:
                return []
            
            # Get last seen message ID for this owner
            last_seen_id = self.last_message_ids.get(owner_id)
            
            # Filter to only new messages
            new_messages = []
            latest_message_id = None
            
            for msg in all_messages:
                msg_id = msg.get('id') or msg.get('message_id')
                
                # Track latest message ID
                if not latest_message_id:
                    latest_message_id = msg_id
                
                # If we haven't seen this message before, it's new
                if last_seen_id is None or msg_id != last_seen_id:
                    new_messages.append(msg)
                else:
                    # We've reached messages we've already seen
                    break
            
            # Update last seen message ID
            if latest_message_id:
                self.last_message_ids[owner_id] = latest_message_id
            
            return new_messages
            
        except Exception as e:
            logger.error(f"❌ Error fetching new messages for owner {owner_id}: {e}")
            return []
    
    def _store_messages(self, messages: List[Dict]) -> None:
        """Store new messages in database"""
        try:
            for msg in messages:
                # Convert message to database format
                db_message = {
                    'message_id': msg.get('id') or msg.get('message_id'),
                    'content': msg.get('content', ''),
                    'subject': msg.get('subject', ''),
                    'from_user': msg.get('from_user', ''),
                    'recipient_name': msg.get('to_user', ''),
                    'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                    'status': msg.get('status', 'unread'),
                    'message_type': msg.get('message_type', 'clubos_message'),
                    'owner_id': msg.get('owner_id', ''),
                    'member_id': msg.get('member_id', ''),
                    'conversation_id': msg.get('conversation_id', ''),
                    'channel': 'clubos',
                    'delivery_status': 'received',
                    'created_at': datetime.now().isoformat()
                }
                
                # Store in database (upsert)
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO messages (
                            clubos_message_id, content, subject, from_user, recipient_name,
                            timestamp, status, message_type, owner_id, member_id,
                            conversation_id, channel, delivery_status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        db_message['message_id'],
                        db_message['content'],
                        db_message['subject'],
                        db_message['from_user'],
                        db_message['recipient_name'],
                        db_message['timestamp'],
                        db_message['status'],
                        db_message['message_type'],
                        db_message['owner_id'],
                        db_message['member_id'],
                        db_message['conversation_id'],
                        db_message['channel'],
                        db_message['delivery_status'],
                        db_message['created_at']
                    ))
                    
                    conn.commit()
            
            logger.info(f"💾 Stored {len(messages)} messages in database")
            
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
            }, broadcast=True)
            
            logger.info(f"📡 Broadcast {len(formatted_messages)} messages to connected clients")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting to UI: {e}")
    
    def _trigger_ai_processing(self, messages: List[Dict]) -> None:
        """
        Automatically send new messages to AI agent
        PHASE 2 INTEGRATION POINT - Currently placeholder
        """
        # This will be implemented in Phase 2
        # For now, just log that we would process these
        for msg in messages:
            if self._should_ai_respond(msg):
                logger.info(f"🤖 [PHASE 2] Would process message with AI: {msg.get('from_user')} -> {msg.get('content', '')[:50]}...")
    
    def _should_ai_respond(self, message: Dict) -> bool:
        """
        Determine if AI should process this message
        PHASE 2 INTEGRATION POINT - Currently basic logic
        """
        # Basic logic for now - can be enhanced in Phase 2
        content = message.get('content', '').lower()
        
        # Don't respond to system messages
        if message.get('message_type') in ['system', 'notification']:
            return False
        
        # Don't respond to messages from staff
        if message.get('from_user', '').lower() in ['staff', 'admin', 'system']:
            return False
        
        # Respond to questions
        if any(q in content for q in ['?', 'how', 'when', 'what', 'where', 'why']):
            return True
        
        # Respond to common keywords
        if any(kw in content for kw in ['help', 'cancel', 'reschedule', 'confirm', 'change']):
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
