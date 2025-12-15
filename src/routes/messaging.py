#!/usr/bin/env python3
"""
Messaging Routes
ClubOS messaging integration, conversation management, and campaign functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from functools import wraps
from typing import Dict, List, Any
import logging
import time
import json
import re
import hashlib
import traceback
import requests
import datetime as dt
from datetime import datetime
from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
from .auth import require_auth

def extract_name_from_message_content(content):
    """Extract member name from ClubOS message content"""
    if not content:
        return 'Unknown'
    
    # Try to extract name from the beginning of the content
    # Pattern: 'Name Subject: ...' or 'Name [emoji] ...' 
    match = re.match(r'^([A-Za-z ]+?)(?:\s+Subject:|\s+🧪|\s+\[)', content)
    if match:
        name = match.group(1).strip()
        if len(name) > 2 and len(name) < 50:  # Reasonable name length
            return name
    
    # Fallback: try first few words that look like names
    words = content.split()[:3]
    potential_name = ' '.join(words)
    # Check if it contains typical name characters and reasonable length
    if len(potential_name) > 2 and len(potential_name) < 30 and not any(char in potential_name for char in ['@', ':', '🧪']):
        return potential_name
    
    return 'Unknown'

logger = logging.getLogger(__name__)
messaging_bp = Blueprint('messaging', __name__)

def get_clubos_credentials(owner_id: str) -> Dict[str, str]:
    """Get ClubOS credentials for a specific owner"""
    try:
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        base_url = 'https://anytime.club-os.com'  # Static base URL for Anytime Fitness
        
        if not username or not password:
            return None
            
        return {
            'username': username,
            'password': password,
            'base_url': base_url
        }
    except Exception as e:
        logger.error(f"❌ Error getting ClubOS credentials: {e}")
        return None

def store_messages_in_database(messages: List[Dict], owner_id: str) -> int:
    """Store ClubOS messages in the database with enhanced metadata"""
    try:
        # CRITICAL FIX: Create table only if it doesn't exist (don't drop!)
        current_app.db_manager.execute_query('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                message_type TEXT,
                content TEXT,
                timestamp TEXT,
                from_user TEXT,
                to_user TEXT,
                status TEXT,
                owner_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_status TEXT DEFAULT 'received',
                campaign_id TEXT,
                channel TEXT DEFAULT 'clubos',
                member_id TEXT,
                message_actions TEXT,
                is_confirmation BOOLEAN DEFAULT FALSE,
                is_opt_in BOOLEAN DEFAULT FALSE,
                is_opt_out BOOLEAN DEFAULT FALSE,
                has_emoji BOOLEAN DEFAULT FALSE,
                emoji_reactions TEXT,
                conversation_id TEXT,
                thread_id TEXT
            )
        ''')
        logger.info("✅ Messages table ready (created or already exists)")
        
        # Insert ClubOS messages with enhanced parsing
        stored_count = 0
        failed_count = 0
        for message in messages:
            try:
                # Parse message content for actions and metadata
                content = message.get('content', '')
                message_actions = parse_message_actions(content)
                member_id = extract_member_id_from_content(content)
                conversation_id = generate_conversation_id(member_id, owner_id)

                # Extract user information
                from_user = message.get('from_user', message.get('from'))
                to_user = message.get('to_user', message.get('to'))
                status = message.get('status')

                # Populate name fields for proper bidirectional queries
                # These fields are used by the member history query
                from_member_name = None
                to_staff_name = None
                recipient_name = None

                if status == 'sent':
                    # Staff sent TO member
                    to_staff_name = from_user  # Staff who sent
                    recipient_name = to_user    # Member who received
                else:
                    # Member sent FROM member
                    from_member_name = from_user  # Member who sent
                    recipient_name = from_user     # Same as from_user for member messages

                # Use database manager for cross-platform compatibility
                # CRITICAL: Use INSERT OR IGNORE to preserve existing ai_processed status
                # First check if message exists
                existing = current_app.db_manager.execute_query('''
                    SELECT id, ai_processed FROM messages WHERE id = ?
                ''', (message.get('id'),), fetch_one=True)
                
                if existing:
                    # Message exists - only update content/timestamp, preserve ai_processed
                    current_app.db_manager.execute_query('''
                        UPDATE messages SET
                            content = ?, timestamp = ?, from_user = ?, to_user = ?,
                            from_member_name = ?, to_staff_name = ?, recipient_name = ?
                        WHERE id = ?
                    ''', (
                        content,
                        message.get('timestamp'),
                        from_user,
                        to_user,
                        from_member_name,
                        to_staff_name,
                        recipient_name,
                        message.get('id')
                    ))
                else:
                    # New message - insert with ai_processed = 0
                    current_app.db_manager.execute_query('''
                        INSERT INTO messages
                        (id, message_type, content, timestamp, from_user, to_user, status, owner_id,
                         delivery_status, campaign_id, channel, member_id, message_actions,
                         is_confirmation, is_opt_in, is_opt_out, has_emoji, emoji_reactions,
                         conversation_id, thread_id, from_member_name, to_staff_name, recipient_name,
                         ai_processed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    ''', (
                        message.get('id'),
                        message.get('message_type', message.get('type')),
                        content,
                        message.get('timestamp'),
                        from_user,
                        to_user,
                        status,
                        owner_id,
                        message.get('delivery_status', 'received'),
                        message.get('campaign_id'),
                        'clubos',  # Always ClubOS channel
                        member_id,
                        json.dumps(message_actions),
                        message_actions.get('is_confirmation', False),
                        message_actions.get('is_opt_in', False),
                        message_actions.get('is_opt_out', False),
                        message_actions.get('has_emoji', False),
                        json.dumps(message_actions.get('emojis', [])),
                        conversation_id,
                        message.get('thread_id'),
                        from_member_name,
                        to_staff_name,
                        recipient_name
                    ))
                stored_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error inserting ClubOS message {message.get('id')}: {e}")
        
        if failed_count > 0:
            logger.warning(f"⚠️ Failed to store {failed_count} messages")
        logger.info(f"✅ Stored {stored_count}/{len(messages)} ClubOS messages in database with enhanced metadata")
        return stored_count

    except Exception as e:
        logger.error(f"❌ Error storing ClubOS messages in database: {e}")
        return 0

def cleanup_old_messages(owner_id: str, days: int = 90) -> int:
    """
    Remove messages older than specified days to keep database clean.
    CRITICAL: Only delete if we have WAY too many messages (e.g. > 10,000).
    We want to keep history for AI context.
    """
    try:
        # Check total count first
        count_result = current_app.db_manager.execute_query('''
            SELECT COUNT(*) as count FROM messages WHERE owner_id = ?
        ''', (owner_id,), fetch_one=True)
        
        total_count = count_result['count'] if count_result else 0
        
        # Only cleanup if we have excessive messages (e.g. > 5000)
        if total_count < 5000:
            logger.info(f"✅ Message count ({total_count}) is within limits, skipping cleanup to preserve history")
            return 0
            
        from datetime import datetime, timedelta
        # Calculate threshold date (very old messages only)
        # If we have too many, delete ones older than 1 year first
        threshold_date = datetime.now() - timedelta(days=365)
        date_threshold_iso = threshold_date.isoformat()

        # Count messages to be deleted
        count_result = current_app.db_manager.execute_query('''
            SELECT COUNT(*) as count FROM messages
            WHERE owner_id = ?
            AND (
                (timestamp IS NOT NULL AND timestamp < ?)
                OR 
                ((timestamp IS NULL OR timestamp = '') AND created_at < ?)
            )
        ''', (owner_id, date_threshold_iso, date_threshold_iso), fetch_one=True)

        old_count = count_result['count'] if count_result else 0

        if old_count > 0:
            # Delete old messages
            current_app.db_manager.execute_query('''
                DELETE FROM messages
                WHERE owner_id = ?
                AND (
                    (timestamp IS NOT NULL AND timestamp < ?)
                    OR 
                    ((timestamp IS NULL OR timestamp = '') AND created_at < ?)
                )
            ''', (owner_id, date_threshold_iso, date_threshold_iso))

            logger.info(f"🗑️ Cleaned up {old_count} messages older than 1 year for owner {owner_id}")
            return old_count
        else:
            logger.info(f"✅ No extremely old messages to clean up")
            return 0

    except Exception as e:
        logger.error(f"❌ Error cleaning up old messages: {e}")
        return 0

def parse_message_actions(content: str) -> Dict[str, Any]:
    """Parse ClubOS message content for actions, confirmations, emojis, etc."""
    if not content:
        return {}
    
    actions = {
        'is_confirmation': False,
        'is_opt_in': False,
        'is_opt_out': False,
        'has_emoji': False,
        'emojis': [],
        'keywords': []
    }
    
    content_lower = content.lower()
    
    # Check for confirmations (common in ClubOS messages)
    if any(word in content_lower for word in ['confirm', 'confirmar', 'yes', 'si']):
        actions['is_confirmation'] = True
        actions['keywords'].append('confirmation')
    
    # Check for opt-in/opt-out (ClubOS SMS keywords)
    if any(word in content_lower for word in ['start', 'begin', 'subscribe']):
        actions['is_opt_in'] = True
        actions['keywords'].append('opt_in')
    elif any(word in content_lower for word in ['stop', 'end', 'unsubscribe', 'cancel']):
        actions['is_opt_out'] = True
        actions['keywords'].append('opt_out')
    
    # Extract emojis from ClubOS messages
    emoji_pattern = r'[😀-🙏🌀-🗿🚀-🛿🦀-🧿]'
    emojis = re.findall(emoji_pattern, content)
    if emojis:
        actions['has_emoji'] = True
        actions['emojis'] = emojis
    
    return actions

def extract_member_id_from_content(content: str) -> str:
    """Extract member ID or name from ClubOS message content"""
    if not content:
        return None
    
    # Look for patterns like "Member Name" at the beginning (ClubOS format)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) > 3 and len(line) < 50:
            # Check if it looks like a name
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z\s]+$', line):
                return line
    
    return None

def generate_conversation_id(member_id: str, owner_id: str) -> str:
    """Generate a unique conversation ID for grouping ClubOS messages"""
    if not member_id:
        return f"system_{owner_id}"
    
    # Create a consistent conversation ID
    conversation_key = f"{member_id}_{owner_id}".lower().replace(' ', '_')
    return hashlib.md5(conversation_key.encode()).hexdigest()[:16]

@messaging_bp.route('/api/auth/refresh-clubos', methods=['POST'])
def refresh_clubos_auth():
    """Force refresh ClubOS authentication to resolve 403 errors"""
    try:
        logger.info("🔄 Manual ClubOS authentication refresh requested")

        # Try to use unified auth service if available
        try:
            from ..services.authentication.unified_auth_service import get_unified_auth_service

            auth_service = get_unified_auth_service()
            # Invalidate existing session
            auth_service.invalidate_session('clubos')
            logger.info("✅ Invalidated existing ClubOS session")

            # Create fresh session
            session = auth_service.authenticate_clubos()

            if session and session.authenticated:
                logger.info("✅ ClubOS authentication refreshed successfully")
                return jsonify({
                    'success': True,
                    'message': 'ClubOS authentication refreshed successfully',
                    'authenticated': True
                })
            else:
                logger.warning("⚠️ ClubOS authentication refresh failed")
                return jsonify({
                    'success': False,
                    'error': 'Authentication failed - please check credentials'
                }), 401
        except ImportError:
            # Fallback: try to re-create messaging client
            logger.info("📝 Using fallback authentication method")

            if hasattr(current_app, 'messaging_client'):
                del current_app.messaging_client

            # Get fresh credentials
            credentials = get_clubos_credentials('187032782')  # Default owner_id
            if not credentials:
                return jsonify({
                    'success': False,
                    'error': 'ClubOS credentials not configured'
                }), 500

            # Create new client
            client = ClubOSMessagingClient(
                credentials['base_url'],
                credentials['username'],
                credentials['password']
            )

            # Authenticate
            if client.authenticate():
                current_app.messaging_client = client
                logger.info("✅ ClubOS re-authenticated successfully (fallback method)")
                return jsonify({
                    'success': True,
                    'message': 'ClubOS authentication refreshed successfully',
                    'authenticated': True
                })
            else:
                logger.error("❌ ClubOS authentication failed (fallback method)")
                return jsonify({
                    'success': False,
                    'error': 'Authentication failed - please check credentials'
                }), 401

    except Exception as e:
        logger.error(f"❌ Error refreshing ClubOS authentication: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Authentication refresh error: {str(e)}'
        }), 500

@messaging_bp.route('/messaging')
# @require_auth  # Temporarily disabled for testing
def messaging_page():
    """Unified AI Sales & Messaging Center - State of the Art Dashboard

    Combines:
    - Sales AI Dashboard features (workflows, commands, agent chat)
    - Messaging/Inbox features (conversations, campaigns, real-time sync)
    - Complete backend integration with Unified AI Agent
    """
    try:
        from flask import session

        # Get user info
        user_email = session.get('user_email', 'Unknown')
        manager_id = session.get('manager_id', 'unknown')
        club_id = session.get('club_id')

        # Get AI service availability
        ai_available = hasattr(current_app, 'ai_agent') and current_app.ai_agent is not None
        unified_ai_available = hasattr(current_app, 'unified_ai_agent') and current_app.unified_ai_agent is not None
        inbox_ai_available = hasattr(current_app, 'inbox_ai_agent') and current_app.inbox_ai_agent is not None

        return render_template('messaging.html',
                             user_email=user_email,
                             manager_id=manager_id,
                             club_id=club_id,
                             ai_available=ai_available,
                             unified_ai_available=unified_ai_available,
                             inbox_ai_available=inbox_ai_available)

    except Exception as e:
        logger.error(f"❌ Error loading unified AI dashboard: {e}")
        return render_template('error.html', error='Failed to load unified AI dashboard')

@messaging_bp.route('/api/messages/sync', methods=['POST'])
def sync_clubos_messages():
    """Sync messages from ClubOS to local database - REUSES existing authenticated client"""
    try:
        logger.info("🔄 Starting ClubOS message sync...")
        
        # Get owner_id from request OR auto-detect from messaging client
        if request.is_json:
            owner_id = request.json.get('owner_id')
        else:
            owner_id = request.form.get('owner_id')

        # CRITICAL FIX: Auto-detect owner_id if not provided or if it's "default"
        if not owner_id or owner_id == 'default':
            if hasattr(current_app, 'messaging_client') and current_app.messaging_client:
                if hasattr(current_app.messaging_client, 'logged_in_user_id'):
                    owner_id = current_app.messaging_client.logged_in_user_id
                    logger.info(f"🔍 Auto-detected owner_id from messaging client: {owner_id}")
            
            # Final fallback to default manager
            if not owner_id:
                owner_id = '187032782'  # Default to Tyler's ID
                logger.info(f"⚠️ Using default owner_id: {owner_id}")
        
        logger.info(f"📨 Syncing messages for owner_id: {owner_id}")
        
        # CRITICAL FIX: Try to reuse existing authenticated messaging client first
        messaging_client = None
        if hasattr(current_app, 'messaging_client') and current_app.messaging_client:
            messaging_client = current_app.messaging_client
            logger.info("♻️ Reusing existing authenticated messaging client")

            # Clear message cache to force fresh fetch
            messaging_client.clear_message_cache(owner_id)
            logger.info("🗑️ Cleared message cache to fetch fresh messages from ClubOS")

            # Quick check if session is still valid
            try:
                test_messages = messaging_client.get_messages(owner_id)
                # CRITICAL FIX: None means auth failed, empty list means no messages
                if test_messages is None:
                    logger.error("❌ Authentication failed - ClubOS rejected credentials")
                    messaging_client = None
                    # Don't return here - fall through to re-authentication below
                elif len(test_messages) == 0:
                    logger.warning("⚠️ No messages found, but authentication succeeded")
                    return jsonify({
                        'success': True,
                        'message': 'No new messages from ClubOS',
                        'total_messages': 0,
                        'stored_count': 0,
                        'owner_id': owner_id,
                        'auth_warning': 'Authentication succeeded but no messages returned'
                    })
                else:
                    logger.info(f"✅ Session still valid! Fetched {len(test_messages)} messages")
                    stored_count = store_messages_in_database(test_messages, owner_id)

                    # Clean up old messages that ClubOS no longer returns (older than 90 days)
                    cleanup_old_messages(owner_id, days=90)

                    return jsonify({
                        'success': True,
                        'message': f'Synced {stored_count} messages from ClubOS (reused session)',
                        'total_messages': len(test_messages),
                        'stored_count': stored_count,
                        'owner_id': owner_id
                    })
            except Exception as e:
                logger.error(f"❌ Existing session check failed: {e}, will re-authenticate")
                messaging_client = None
        
        # If no valid client, create new one and authenticate
        if not messaging_client:
            credentials = get_clubos_credentials(owner_id)
            if not credentials:
                return jsonify({'error': 'ClubOS credentials not found'}), 400
            
            logger.info(f"🔐 Creating new authenticated session for {credentials['username']}...")
            
            # Initialize messaging client with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    messaging_client = ClubOSMessagingClient(
                        username=credentials['username'],
                        password=credentials['password']
                    )
                    
                    # Try to authenticate
                    if messaging_client.authenticate():
                        logger.info("✅ ClubOS authentication successful")
                        # Store the authenticated client for reuse
                        current_app.messaging_client = messaging_client
                        break
                    else:
                        logger.warning(f"⚠️ Authentication attempt {attempt + 1} failed")
                        if attempt < max_retries - 1:
                            time.sleep(2)  # Wait before retry
                            continue
                        else:
                            return jsonify({'error': 'ClubOS authentication failed after all retries'}), 401
                            
                except Exception as e:
                    logger.error(f"❌ Authentication attempt {attempt + 1} error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return jsonify({'error': f'ClubOS authentication error: {str(e)}'}), 401
        
        # Now try to get messages with retry logic
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Attempting to fetch messages (attempt {attempt + 1})...")
                messages = messaging_client.get_messages(owner_id)
                
                if messages is not None:
                    logger.info(f"✅ Successfully fetched {len(messages)} messages")

                    # Store messages in database
                    stored_count = store_messages_in_database(messages, owner_id)

                    # Clean up old messages that ClubOS no longer returns (older than 90 days)
                    cleanup_old_messages(owner_id, days=90)

                    return jsonify({
                        'success': True,
                        'message': f'Synced {stored_count} messages from ClubOS',
                        'total_messages': len(messages),
                        'stored_count': stored_count,
                        'owner_id': owner_id
                    })
                else:
                    logger.warning(f"⚠️ Message fetch attempt {attempt + 1} returned None")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return jsonify({'error': 'Failed to fetch messages after all retries'}), 500
                        
            except Exception as e:
                logger.error(f"❌ Message fetch attempt {attempt + 1} error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return jsonify({'error': f'Failed to fetch messages: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in sync_clubos_messages: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@messaging_bp.route('/api/messages/cleanup', methods=['POST'])
def cleanup_messages():
    """Manually cleanup old messages from database"""
    try:
        if request.is_json:
            owner_id = request.json.get('owner_id', '187032782')
            days = request.json.get('days', 90)
        else:
            owner_id = request.form.get('owner_id', '187032782')
            days = int(request.form.get('days', 90))

        logger.info(f"🗑️ Manual cleanup requested for owner {owner_id} (messages older than {days} days)")

        deleted_count = cleanup_old_messages(owner_id, days=days)

        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old messages',
            'deleted_count': deleted_count,
            'owner_id': owner_id,
            'days': days
        })

    except Exception as e:
        logger.error(f"❌ Error in manual cleanup: {e}")
        return jsonify({'error': f'Cleanup error: {str(e)}'}), 500

@messaging_bp.route('/api/messages/test-auth', methods=['POST'])
def test_clubos_auth():
    """Simple test for ClubOS authentication"""
    try:
        logger.info("🧪 Testing ClubOS authentication...")
        
        # Import here to avoid circular imports
        try:
            from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
            logger.info("✅ Successfully imported ClubOSMessagingClient")
        except Exception as e:
            logger.error(f"❌ Failed to import ClubOSMessagingClient: {e}")
            return jsonify({'success': False, 'error': f'Import error: {str(e)}'}), 500
        
        try:
            from ..services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            logger.info("✅ Successfully initialized SecureSecretsManager")
        except Exception as e:
            logger.error(f"❌ Failed to import SecureSecretsManager: {e}")
            return jsonify({'success': False, 'error': f'Secrets import error: {str(e)}'}), 500
        
        # Get credentials
        try:
            username = secrets_manager.get_secret('clubos-username')
            password = secrets_manager.get_secret('clubos-password')
            logger.info(f"✅ Got credentials: {username[:5] if username else 'None'}...")
        except Exception as e:
            logger.error(f"❌ Failed to get credentials: {e}")
            return jsonify({'success': False, 'error': f'Credentials error: {str(e)}'}), 500
        
        if not username or not password:
            logger.error("❌ ClubOS credentials are None/empty")
            return jsonify({'success': False, 'error': 'ClubOS credentials not found'}), 400
        
        # Initialize client
        try:
            client = ClubOSMessagingClient(username, password)
            logger.info("✅ ClubOSMessagingClient initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            return jsonify({'success': False, 'error': f'Client init error: {str(e)}'}), 500
        
        # Test authentication
        try:
            auth_result = client.authenticate()
            logger.info(f"🔐 Authentication result: {auth_result}")
            
            return jsonify({
                'success': True,
                'authenticated': auth_result,
                'message': f'Authentication {"successful" if auth_result else "failed"}'
            })
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return jsonify({'success': False, 'error': f'Auth error: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in test-auth: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/ai/enable', methods=['POST'])
def enable_ai():
    """Enable automatic AI processing of messages"""
    try:
        if hasattr(current_app, 'message_sync') and current_app.message_sync:
            current_app.message_sync.enable_ai()
            return jsonify({
                'success': True,
                'message': 'AI auto-processing enabled',
                'ai_enabled': True
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Message sync service not available'
            }), 503
    except Exception as e:
        logger.error(f"❌ Error enabling AI: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/ai/disable', methods=['POST'])
def disable_ai():
    """Disable automatic AI processing of messages"""
    try:
        if hasattr(current_app, 'message_sync') and current_app.message_sync:
            current_app.message_sync.disable_ai()
            return jsonify({
                'success': True,
                'message': 'AI auto-processing disabled',
                'ai_enabled': False
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Message sync service not available'
            }), 503
    except Exception as e:
        logger.error(f"❌ Error disabling AI: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/ai/status', methods=['GET'])
def get_ai_status():
    """Get current AI auto-processing status"""
    try:
        # Try multiple possible attribute names
        message_sync = None
        for attr in ['message_sync', 'message_poller', 'real_time_sync']:
            if hasattr(current_app, attr):
                message_sync = getattr(current_app, attr)
                if message_sync and hasattr(message_sync, 'ai_enabled'):
                    break

        if message_sync and hasattr(message_sync, 'ai_enabled'):
            return jsonify({
                'success': True,
                'ai_enabled': message_sync.ai_enabled,
                'polling_running': getattr(message_sync, 'running', False),
                'poll_interval': getattr(message_sync, 'poll_interval', None),
                'owner_ids': list(getattr(message_sync, 'owner_ids', [])),
                'has_unified_agent': hasattr(message_sync, 'unified_ai_agent') and message_sync.unified_ai_agent is not None
            })
        else:
            # Return default state instead of 503 error
            return jsonify({
                'success': True,
                'ai_enabled': False,
                'polling_running': False,
                'error': 'Message sync service not found'
            })
    except Exception as e:
        logger.error(f"❌ Error getting AI status: {e}")
        return jsonify({'success': True, 'ai_enabled': False, 'error': str(e)})

@messaging_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """Get messages from database - ALWAYS FRESH DATA"""
    try:
        owner_id = request.args.get('owner_id', '187032782')
        limit = request.args.get('limit')  # Make limit optional
        days = request.args.get('days', '90')  # Default to last 90 days

        # ALWAYS fetch fresh data from database (removed stale cache)
        logger.info(f"📬 Fetching fresh messages from database for owner_id: {owner_id} (last {days} days)")

        # Calculate date threshold (only get messages from last N days)
        from datetime import datetime, timedelta
        date_threshold = (datetime.now() - timedelta(days=int(days))).isoformat()

        # Fetch from database using database manager with date filter
        # IMPORTANT: Order by rowid DESC for proper chronological order (newest messages first)
        # ClubOS returns messages in reverse chronological order (newest first), and SQLite assigns
        # rowids in insertion order. So the highest rowid = most recently synced = newest message.
        # Note: timestamp field from ClubOS parsing is unreliable (wrong year/format)
        # Note: created_at doesn't help because bulk syncs insert thousands at same timestamp
        if limit:
            # If limit is specified, use it
            limit = int(limit)
            messages = current_app.db_manager.execute_query('''
                SELECT *, rowid FROM messages
                WHERE owner_id = ?
                AND created_at >= ?
                ORDER BY rowid DESC
                LIMIT ?
            ''', (owner_id, date_threshold, limit), fetch_all=True)
        else:
            # If no limit, get messages from last N days
            messages = current_app.db_manager.execute_query('''
                SELECT *, rowid FROM messages
                WHERE owner_id = ?
                AND created_at >= ?
                ORDER BY rowid DESC
            ''', (owner_id, date_threshold), fetch_all=True)
        
        # Handle None result and ensure we have dictionaries
        if messages is None:
            messages = []
        elif messages and not isinstance(messages[0], dict):
            messages = [dict(row) for row in messages]
        
        # Convert datetime objects to strings for template compatibility
        for message in messages:
            for key, value in message.items():
                if isinstance(value, (dt.datetime, dt.date)):
                    message[key] = value.isoformat()
        
        # Enhance messages with extracted names
        for message in messages:
            if message.get('from_user') == 'Unknown' or not message.get('from_user'):
                extracted_name = extract_name_from_message_content(message.get('content', ''))
                message['from_user'] = extracted_name
                message['display_name'] = extracted_name
        
        logger.info(f"✅ Retrieved {len(messages)} messages from database with name extraction")
        return jsonify({'success': True, 'messages': messages, 'source': 'database'})
        
    except Exception as e:
        logger.error(f"❌ Error getting messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/counts', methods=['GET'])
def get_campaign_counts():
    """Get member counts for each campaign category using status_message"""
    try:
        db_manager = current_app.db_manager

        counts = {}

        # Good Standing - members with "Member is in good standing" or "In good standing"
        good_standing = db_manager.execute_query(
            """SELECT COUNT(*) as count FROM members
               WHERE status_message IN ('Member is in good standing', 'In good standing')
               OR status_message LIKE '%good standing%'""",
            fetch_one=True
        )
        counts['good_standing'] = good_standing['count'] if good_standing else 0

        # Pay Per Visit
        pay_per_visit = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM members WHERE status_message = 'Pay Per Visit Member'",
            fetch_one=True
        )
        counts['pay_per_visit'] = pay_per_visit['count'] if pay_per_visit else 0

        # Past Due 6-30 days
        past_due_6_30 = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM members WHERE status_message = 'Past Due 6-30 days'",
            fetch_one=True
        )
        counts['past_due_6_30'] = past_due_6_30['count'] if past_due_6_30 else 0

        # Past Due 30+ days
        past_due_30_plus = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM members WHERE status_message = 'Past Due more than 30 days.'",
            fetch_one=True
        )
        counts['past_due_30_plus'] = past_due_30_plus['count'] if past_due_30_plus else 0

        # Past Due Training - members from training_clients table with past due amounts
        past_due_training = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM training_clients WHERE total_past_due > 0",
            fetch_one=True
        )
        counts['past_due_training'] = past_due_training['count'] if past_due_training else 0

        # Expiring Soon - memberships ending within 30 days
        expiring_soon = db_manager.execute_query(
            """SELECT COUNT(*) as count FROM members
               WHERE status_message LIKE '%expir%'
               OR status_message = 'Member is pending cancel'""",
            fetch_one=True
        )
        counts['expiring_soon'] = expiring_soon['count'] if expiring_soon else 0

        # Prospects
        prospects = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM prospects",
            fetch_one=True
        )
        counts['prospects'] = prospects['count'] if prospects else 0

        # Other Statuses - all other members not in above categories
        other_statuses = db_manager.execute_query(
            """SELECT COUNT(*) as count FROM members
               WHERE status_message NOT IN (
                   'Member is in good standing',
                   'In good standing',
                   'Pay Per Visit Member',
                   'Past Due 6-30 days',
                   'Past Due more than 30 days.'
               )
               AND (status_message NOT LIKE '%good standing%')
               AND (status_message NOT LIKE '%expir%')
               AND status_message != 'Member is pending cancel'
               AND status_message IS NOT NULL""",
            fetch_one=True
        )
        counts['other_statuses'] = other_statuses['count'] if other_statuses else 0

        logger.info(f"✅ Campaign counts: {counts}")
        return jsonify({'success': True, 'counts': counts})

    except Exception as e:
        logger.error(f"❌ Error getting campaign counts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/send', methods=['POST'])
def send_campaign():
    """Send bulk messaging campaign with improved timeout handling"""
    try:
        data = request.json
        logger.info(f"📨 Campaign send request received: {data}")
        
        if not data:
            logger.error("❌ No data provided in campaign request")
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Quick validation and immediate response to prevent frontend timeout
        message_text = data.get('message', '')
        if not message_text:
            return jsonify({'success': False, 'error': 'Message text is required'}), 400
        
        # Check if specific members were selected (takes priority over category selection)
        selected_member_ids = data.get('selected_member_ids', []) or data.get('member_ids', [])
        
        categories_raw = data.get('categories', [])
        single_category = data.get('category', '')
        
        if single_category and not categories_raw:
            member_categories = [single_category]
        elif categories_raw:
            member_categories = categories_raw
        else:
            member_categories = []
            
        # Either specific members OR categories must be provided
        if not selected_member_ids and not member_categories:
            return jsonify({'success': False, 'error': 'Either specific members or at least one category must be selected'}), 400
        
        # Extract remaining campaign parameters
        message_type = data.get('type', 'sms')  # 'sms' or 'email'
        subject = data.get('subject', '')
        max_recipients = data.get('max_recipients', 100)
        campaign_notes = data.get('notes', '')
        campaign_mode = data.get('mode', 'resume')  # 'fresh' or 'resume' (default)
        
        logger.info(f"📋 Campaign params - Message: '{message_text[:50]}...', Type: {message_type}, Categories: {member_categories}, Selected IDs: {len(selected_member_ids) if selected_member_ids else 0}, Max: {max_recipients}, Mode: {campaign_mode}")
        logger.info(f"📝 Campaign notes: '{campaign_notes[:100]}...'")  # Log notes for debugging
        
        # Get members - either from selected IDs or from categories
        member_ids = []
        validated_members = []
        
        if selected_member_ids:
            # User manually selected specific members - use those IDs directly
            logger.info(f"👥 Using {len(selected_member_ids)} manually selected member IDs")
            
            # Fetch member details for the selected IDs - INCLUDING FINANCIAL DATA
            for member_id in selected_member_ids:
                try:
                    member = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        WHERE prospect_id = ? OR id = ?
                        LIMIT 1
                    ''', (member_id, member_id), fetch_one=True)
                    
                    if member:
                        validated_members.append(dict(member))
                        logger.debug(f"  ✅ Found member: {member['full_name']} ({member_id})")
                    else:
                        logger.warning(f"  ⚠️ Member ID {member_id} not found in database")
                except Exception as e:
                    logger.error(f"  ❌ Error fetching member {member_id}: {e}")
            
            logger.info(f"📋 Validated {len(validated_members)} of {len(selected_member_ids)} selected members")
            
            # Extract member IDs from validated members for the rest of the code
            member_ids = [m['prospect_id'] or m['id'] for m in validated_members]
            
        else:
            # No specific members selected - query by category
            logger.info(f"📂 Querying members by categories: {member_categories}")
            
            for category in member_categories:
                logger.info(f"🔍 Processing category: '{category}'")
                
                # Map frontend category names to actual database status_message values
                category_mapping = {
                # Hyphen variants
                'past-due-6-30': 'Past Due 6-30 days',
                'past-due-30': 'Past Due more than 30 days.',  # Added missing mapping!
                'past-due-30-plus': 'Past Due more than 30 days.',  # Note the period!
                'past-due-6-30-days': 'Past Due 6-30 days',
                'past-due-more-than-30-days': 'Past Due more than 30 days.',
                # Underscore variants (API/backend format)
                'past_due_6_30': 'Past Due 6-30 days',
                'past_due_30': 'Past Due more than 30 days.',
                'past_due_30_plus': 'Past Due more than 30 days.',
                'past_due_more_than_30_days': 'Past Due more than 30 days.',
                'good_standing': 'Member is in good standing',
                # General status mappings
                'good-standing': 'Member is in good standing',
                'in-good-standing': 'In good standing',  # Fixed to handle both cases
                'green': 'Member is in good standing',  # Alternative for good standing
                'comp': 'Comp Member',
                'staff': 'Staff Member',
                'staff-member': 'Staff member',  # Added lowercase variant
                'pay-per-visit': 'Pay Per Visit Member',
                'sent-to-collections': 'Sent to Collections',
                'pending-cancel': 'Member is pending cancel',
                'expired': 'Expired',
                'cancelled': 'Account has been cancelled.',
                'yellow': 'Invalid Billing Information.',  # Added yellow category
                'inactive': 'Inactive',  # Added inactive category
                'member-will-expire-within-30-days': 'Member will expire within 30 days.',  # Added expiring members
                'expiring-soon': 'Member will expire within 30 days.',  # Alternative name
                'invalid-bad-address-information': 'Invalid/Bad Address information.',  # Added address issues
                'address-issues': 'Invalid/Bad Address information.',  # Alternative name
                # Training client categories (use training_clients table)
                'training-past-due': 'training_past_due',  # Special case - query training_clients table
                'training-current': 'training_current',  # Special case - query training_clients table  
                'training-clients-past-due': 'training_past_due',  # Alternative name
                'training-clients-current': 'training_current',  # Alternative name
                'past-due-training': 'training_past_due',  # Alternative name
                # Add more mappings as needed based on your actual status messages
                'all_members': 'all_members',  # Special case
                'prospects': 'prospects'      # Special case
            }
            
            # Convert category name to actual database status_message
            actual_status_message = category_mapping.get(category, category)
            if actual_status_message != category:
                logger.info(f"📝 Mapped category '{category}' to status_message '{actual_status_message}'")
            else:
                logger.info(f"📝 Using category '{category}' as direct status_message match")
            
            # Use the mapped status message for database queries
            category_to_use = actual_status_message
            
            # Ensure campaign_progress table exists with cross-database compatibility
            current_app.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS campaign_progress (
                    id INTEGER PRIMARY KEY,
                    category TEXT UNIQUE,
                    last_processed_member_id TEXT,
                    last_processed_index INTEGER,
                    last_campaign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_members_in_category INTEGER,
                    notes TEXT
                )
            ''')
            
            # If 'fresh' mode, clear any existing campaign progress for this category
            if campaign_mode == 'fresh':
                logger.info(f"🔄 Fresh mode enabled - clearing previous campaign progress for '{category}'")
                current_app.db_manager.execute_query('''
                    DELETE FROM campaign_progress WHERE category = ?
                ''', (category,))
            
            # Check campaign progress to see where we left off
            progress_results = current_app.db_manager.execute_query('''
                SELECT last_processed_member_id, last_processed_index, total_members_in_category
                FROM campaign_progress 
                WHERE category = ?
                ORDER BY last_campaign_date DESC 
                LIMIT 1
            ''', (category,), fetch_all=True)  # FIXED: Added fetch_all=True
            
            progress_row = progress_results[0] if progress_results and len(progress_results) > 0 else None
            start_after_member_id = None
            start_index = 0
            
            if progress_row:
                start_after_member_id = progress_row['last_processed_member_id']
                start_index = progress_row['last_processed_index'] + 1  # Start after last processed
                logger.info(f"📍 Resuming {category} from index {start_index} (after member {start_after_member_id})")
            else:
                logger.info(f"📍 Starting {category} from beginning (no previous progress)")
            
            if category_to_use == 'all_members':
                # Special case: get all members regardless of status
                logger.info("📊 Selecting all members from all categories")
                if start_after_member_id:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        WHERE id > (SELECT id FROM members WHERE prospect_id = ? OR id = ? LIMIT 1)
                        ORDER BY id
                        LIMIT ?
                    ''', (start_after_member_id, start_after_member_id, max_recipients), fetch_all=True)
                else:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        ORDER BY id
                        LIMIT ?
                    ''', (max_recipients,), fetch_all=True)
            elif category_to_use == 'prospects':
                # Special case: get prospects from prospects table (different column names)
                logger.info("📊 Selecting prospects")
                if start_after_member_id:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT prospect_id as id, prospect_id, email, phone as mobile_phone, full_name, status as status_message
                        FROM prospects 
                        WHERE prospect_id > ?
                        ORDER BY prospect_id
                        LIMIT ?
                    ''', (start_after_member_id, max_recipients), fetch_all=True)
                else:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT prospect_id as id, prospect_id, email, phone as mobile_phone, full_name, status as status_message
                        FROM prospects 
                        ORDER BY prospect_id
                        LIMIT ?
                    ''', (max_recipients,), fetch_all=True)
            elif category_to_use == 'training_past_due':
                # Special case: get past due training clients from training_clients table
                logger.info("📊 Selecting past due training clients")
                if start_after_member_id:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT 
                            tc.id as id,
                            tc.clubos_member_id as prospect_id,
                            COALESCE(tc.email, m.email) as email,
                            COALESCE(tc.phone, m.mobile_phone) as mobile_phone,
                            tc.full_name as full_name,
                            tc.payment_status as status_message
                        FROM training_clients tc
                        LEFT JOIN members m ON LOWER(TRIM(tc.full_name)) = LOWER(TRIM(m.full_name))
                        WHERE tc.payment_status = 'Past Due' AND tc.id > ?
                        AND (COALESCE(tc.email, m.email) IS NOT NULL AND COALESCE(tc.email, m.email) != '')
                        AND (COALESCE(tc.phone, m.mobile_phone) IS NOT NULL AND COALESCE(tc.phone, m.mobile_phone) != '')
                        ORDER BY tc.id
                        LIMIT ?
                    ''', (start_after_member_id, max_recipients), fetch_all=True)
                else:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT 
                            tc.id as id,
                            tc.clubos_member_id as prospect_id,
                            COALESCE(tc.email, m.email) as email,
                            COALESCE(tc.phone, m.mobile_phone) as mobile_phone,
                            tc.full_name as full_name,
                            tc.payment_status as status_message
                        FROM training_clients tc
                        LEFT JOIN members m ON LOWER(TRIM(tc.full_name)) = LOWER(TRIM(m.full_name))
                        WHERE tc.payment_status = 'Past Due'
                        AND (COALESCE(tc.email, m.email) IS NOT NULL AND COALESCE(tc.email, m.email) != '')
                        AND (COALESCE(tc.phone, m.mobile_phone) IS NOT NULL AND COALESCE(tc.phone, m.mobile_phone) != '')
                        ORDER BY tc.id
                        LIMIT ?
                    ''', (max_recipients,), fetch_all=True)
            elif category_to_use == 'training_current':
                # Special case: get current training clients from training_clients table
                logger.info("📊 Selecting current training clients")
                if start_after_member_id:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT member_id as id, clubos_member_id as prospect_id, email, phone as mobile_phone, member_name as full_name, payment_status as status_message
                        FROM training_clients 
                        WHERE payment_status = 'Current' AND member_id > ?
                        ORDER BY member_id
                        LIMIT ?
                    ''', (start_after_member_id, max_recipients), fetch_all=True)
                else:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT member_id as id, clubos_member_id as prospect_id, email, phone as mobile_phone, member_name as full_name, payment_status as status_message
                        FROM training_clients 
                        WHERE payment_status = 'Current'
                        ORDER BY member_id
                        LIMIT ?
                    ''', (max_recipients,), fetch_all=True)
            elif category in ['expiring-soon', 'expiring']:
                # Special case for expiring members: include multiple status patterns
                logger.info(f"📊 Selecting expiring members with multiple status patterns")
                
                if start_after_member_id:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        WHERE (status_message LIKE '%expire%' OR status_message = 'Expired') 
                        AND id > (SELECT id FROM members WHERE prospect_id = ? OR id = ? LIMIT 1)
                        ORDER BY id
                        LIMIT ?
                    ''', (start_after_member_id, start_after_member_id, max_recipients), fetch_all=True)
                else:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        WHERE status_message LIKE '%expire%' OR status_message = 'Expired'
                        ORDER BY id
                        LIMIT ?
                    ''', (max_recipients,), fetch_all=True)
            else:
                # Regular category: filter by status_message (members table only)
                logger.info(f"📊 Selecting members with status_message LIKE '%{category_to_use}%'")
                
                if start_after_member_id:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        WHERE status_message LIKE ? AND id > (SELECT id FROM members WHERE prospect_id = ? OR id = ? LIMIT 1)
                        ORDER BY id
                        LIMIT ?
                    ''', (f'%{category_to_use}%', start_after_member_id, start_after_member_id, max_recipients), fetch_all=True)
                else:
                    category_members = current_app.db_manager.execute_query('''
                        SELECT id, prospect_id, email, mobile_phone, full_name, status_message,
                               amount_past_due, late_fees, missed_payments
                        FROM members 
                        WHERE status_message LIKE ?
                        ORDER BY id
                        LIMIT ?
                    ''', (f'%{category_to_use}%', max_recipients), fetch_all=True)
            
            if not category_members:
                category_members = []
            logger.info(f"📋 Found {len(category_members)} members for category '{category}'")
            
            # Validate each member before adding
            for member in category_members:
                if len(member_ids) >= max_recipients:
                    break
                    
                # Convert row to dict for validation - INCLUDING FINANCIAL DATA
                member_dict = {
                    'member_id': member['prospect_id'] or str(member['id']),
                    'prospect_id': member['prospect_id'],
                    'email': member['email'],
                    'mobile_phone': member['mobile_phone'],
                    'full_name': member['full_name'],
                    'status_message': member['status_message'],
                    'amount_past_due': member.get('amount_past_due', 0),
                    'late_fees': member.get('late_fees', 0),
                    'missed_payments': member.get('missed_payments', 0)
                }
                
                # Basic validation for SMS campaigns with email fallback
                if message_type == 'sms':
                    phone = member_dict.get('mobile_phone')
                    phone = phone.strip() if phone else None
                    if not phone:
                        # Fallback to email if no phone number
                        email = member_dict.get('email')
                        email = email.strip() if email else None
                        if not email or '@' not in email:
                            logger.warning(f"⚠️ Skipping member {member_dict['full_name']} - no phone number and no valid email for fallback")
                            continue
                        else:
                            logger.info(f"📧 Member {member_dict['full_name']} has no phone, using email fallback")
                            # Update message type for this member to email
                            member_dict['fallback_to_email'] = True
                
                # Basic validation for email campaigns  
                if message_type == 'email':
                    email = member_dict.get('email')
                    email = email.strip() if email else None
                    if not email or '@' not in email:
                        logger.warning(f"⚠️ Skipping member {member_dict['full_name']} - no valid email")
                        continue
                
                member_id = member_dict['member_id']
                if member_id and member_id not in member_ids:  # Avoid duplicates
                    member_ids.append(member_id)
                    validated_members.append(member_dict)
        
        logger.info(f"📊 Total validated members selected: {len(member_ids)}")
        
        if not member_ids:
            logger.error("❌ No valid members found in selected categories")
            return jsonify({'success': False, 'error': 'No valid members found in selected categories (check phone/email data)'}), 400
        
        # Get ClubOS credentials and initialize messaging client
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'ClubOS credentials not configured'}), 400
        
        logger.info("🔄 Initializing ClubOS messaging client...")
        
        # Use the working implementation from clubos_messaging_client_simple.py
        client = ClubOSMessagingClient(username, password)
        
        logger.info("🔐 Authenticating with ClubOS...")
        if not client.authenticate():
            logger.error("❌ ClubOS authentication failed")
            return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 401
        
        logger.info("✅ ClubOS authentication successful, sending campaign...")
        
        # Process all validated members up to max_recipients
        batch_size = min(len(validated_members), max_recipients)
        batch_members = validated_members[:batch_size]
        
        logger.info(f"📤 Processing campaign for {len(batch_members)} members (up to {max_recipients} requested)")
        
        # Send the campaign using the simple client with limited batch to prevent timeout
        results = client.send_bulk_campaign(
            member_data_list=batch_members,
            message=message_text,
            message_type=message_type
        )
        
        results['method'] = 'simple_client'
        results['batch_processed'] = len(batch_members)
        results['total_selected'] = len(validated_members)
        results['remaining'] = len(validated_members) - len(batch_members)
        
        # Log campaign results
        logger.info(f"📢 Campaign completed: {results['successful']}/{results['total']} sent successfully")
        
        # Ensure campaigns table exists with cross-database compatibility
        current_app.db_manager.execute_query('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY,
                campaign_name TEXT,
                message_text TEXT,
                message_type TEXT,
                subject TEXT,
                categories TEXT,
                total_recipients INTEGER,
                successful_sends INTEGER,
                failed_sends INTEGER,
                errors TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Store campaign in database with cross-database compatibility
        current_app.db_manager.execute_query('''
            INSERT INTO campaigns 
            (campaign_name, message_text, message_type, subject, categories, total_recipients, successful_sends, failed_sends, errors, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', 'Untitled Campaign'),
            message_text,
            message_type,
            subject,
            ','.join(member_categories),
            results['total'],
            results['successful'],
            results['failed'],
            '\n'.join(results.get('errors', [])),
            campaign_notes
        ))

        # Save as reusable campaign template if successful and requested
        save_as_template = data.get('save_as_template', True)  # Default to True for all campaigns
        if results['successful'] > 0 and save_as_template:
            try:
                # Create campaign_templates table if it doesn't exist
                current_app.db_manager.execute_query('''
                    CREATE TABLE IF NOT EXISTS campaign_templates (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        message TEXT NOT NULL,
                        target_group TEXT NOT NULL,
                        category TEXT NOT NULL,
                        message_type TEXT DEFAULT 'sms',
                        max_recipients INTEGER DEFAULT 100,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP,
                        usage_count INTEGER DEFAULT 1,
                        active INTEGER DEFAULT 1
                    )
                ''')
                
                # Determine template category based on target groups
                template_category = 'general'
                if 'past_due' in str(member_categories).lower() or 'past-due' in str(member_categories).lower():
                    template_category = 'payment_due'
                elif 'good' in str(member_categories).lower() or 'standing' in str(member_categories).lower():
                    template_category = 'welcome'
                elif 'prospect' in str(member_categories).lower():
                    template_category = 'followup'
                elif any(cat in str(member_categories).lower() for cat in ['training', 'pt']):
                    template_category = 'followup'
                
                # Check if similar template already exists
                existing_template = current_app.db_manager.execute_query('''
                    SELECT id, usage_count FROM campaign_templates 
                    WHERE name = ? AND message = ? AND active = 1
                    LIMIT 1
                ''', (data.get('name', 'Untitled Campaign'), message_text))
                
                if existing_template:
                    # Update usage count for existing template
                    current_app.db_manager.execute_query('''
                        UPDATE campaign_templates 
                        SET usage_count = usage_count + 1, last_used = ?
                        WHERE id = ?
                    ''', (datetime.now().isoformat(), existing_template[0][0]))
                    logger.info(f"💾 Updated existing campaign template usage count")
                else:
                    # Insert new template
                    current_app.db_manager.execute_query('''
                        INSERT INTO campaign_templates 
                        (name, message, target_group, category, message_type, max_recipients, created_at, last_used, usage_count, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
                    ''', (
                        data.get('name', 'Untitled Campaign'),
                        message_text,
                        ','.join(member_categories),
                        template_category,
                        message_type,
                        max_recipients,
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    logger.info(f"💾 Saved campaign as reusable template: {data.get('name', 'Untitled Campaign')}")
                    
            except Exception as template_error:
                logger.warning(f"⚠️ Could not save campaign template: {template_error}")
                # Don't fail the campaign if template saving fails
        
        # Get the inserted campaign ID in a cross-database compatible way
        try:
            campaign_results = current_app.db_manager.execute_query('''
                SELECT id FROM campaigns 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
            campaign_id = campaign_results[0]['id'] if campaign_results else None
        except Exception as e:
            logger.warning(f"⚠️ Could not get campaign ID: {e}")
            campaign_id = None
        
        # Store individual messages sent in this campaign
        if 'sent_messages' in results and campaign_id:
            for msg_data in results['sent_messages']:
                current_app.db_manager.execute_query('''
                    INSERT INTO messages 
                    (id, message_type, content, timestamp, from_user, to_user, status, owner_id, 
                     delivery_status, campaign_id, channel, member_id, conversation_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"campaign_{campaign_id}_{msg_data['member_id']}_{int(time.time())}",
                    message_type,
                    message_text,
                    datetime.now().isoformat(),
                    'j.mayo',  # from staff
                    msg_data.get('member_name', msg_data['member_id']),
                    'sent',
                    '187032782',  # owner_id
                    'sent',
                    str(campaign_id),
                    'clubos_sms',
                    msg_data['member_id'],
                    f"campaign_{campaign_id}_{msg_data['member_id']}"
                ))
        
        # Update campaign progress for each category
        for category in member_categories:
            if results['successful'] > 0:
                # Get the last successfully processed member for this category
                last_member_id = results.get('last_processed_member_id', '')
                last_index = results.get('last_processed_index', 0)
                
                # Update or insert progress tracking with cross-database compatibility
                current_app.db_manager.execute_query('''
                    INSERT OR REPLACE INTO campaign_progress 
                    (category, last_processed_member_id, last_processed_index, last_campaign_date, total_members_in_category, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    category,
                    last_member_id,
                    last_index,
                    datetime.now().isoformat(),
                    len(validated_members),
                    f"Campaign: {data.get('name', 'Untitled')} - {results['successful']}/{results['total']} sent"
                ))
        
        # Create success message with batch information
        if results.get('remaining', 0) > 0:
            message = f"Initial batch: {results['successful']}/{results['total']} sent successfully. {results['remaining']} members remaining for future batches."
        else:
            message = f"Campaign completed: {results['successful']}/{results['total']} sent successfully."
        
        # Save campaign as template if requested
        try:
            if data.get('save_as_template', False) and results['successful'] > 0:
                from src.services.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                # Create campaign_templates table if it doesn't exist
                create_table_query = """
                    CREATE TABLE IF NOT EXISTS campaign_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        message TEXT NOT NULL,
                        target_group TEXT NOT NULL,
                        category TEXT NOT NULL,
                        max_recipients INTEGER DEFAULT 100,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP,
                        usage_count INTEGER DEFAULT 0,
                        active INTEGER DEFAULT 1
                    )
                """
                db_manager.execute_query(create_table_query)
                
                # Save the campaign as a template
                template_name = data.get('campaign_name', f"{category.replace('_', ' ').title()} Campaign")
                insert_query = """
                    INSERT INTO campaign_templates 
                    (name, message, target_group, category, max_recipients, created_at, usage_count, active)
                    VALUES (?, ?, ?, ?, ?, ?, 1, 1)
                """
                
                db_manager.execute_query(insert_query, (
                    template_name,
                    message_text,
                    category,
                    category,
                    max_recipients,
                    datetime.now().isoformat()
                ))
                
                logger.info(f"💾 Saved campaign as reusable template: {template_name}")
                message += f" Template '{template_name}' saved for reuse."
                
        except Exception as template_error:
            logger.error(f"⚠️ Error saving campaign template: {template_error}")
            # Don't fail the whole campaign if template saving fails
        
        return jsonify({
            'success': True,
            'campaign_results': results,
            'message': message,
            'batch_info': {
                'batch_processed': results.get('batch_processed', results['total']),
                'total_selected': results.get('total_selected', results['total']),
                'remaining': results.get('remaining', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error sending campaign: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/progress', methods=['GET'])
def get_campaign_progress():
    """Get campaign progress tracking for all categories"""
    try:
        # Ensure campaign_progress table exists with cross-database compatibility
        current_app.db_manager.execute_query('''
            CREATE TABLE IF NOT EXISTS campaign_progress (
                id INTEGER PRIMARY KEY,
                category TEXT UNIQUE,
                last_processed_member_id TEXT,
                last_processed_index INTEGER,
                last_campaign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_members_in_category INTEGER,
                notes TEXT
            )
        ''')
        
        progress = current_app.db_manager.execute_query('''
            SELECT category, last_processed_member_id, last_processed_index, 
                   last_campaign_date, total_members_in_category, notes
            FROM campaign_progress 
            ORDER BY last_campaign_date DESC
        ''')
        
        if not progress:
            progress = []
        
        return jsonify({'success': True, 'progress': progress})
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/reset-progress', methods=['POST'])
def reset_campaign_progress():
    """Reset campaign progress for a specific category or all categories"""
    try:
        data = request.json
        category = data.get('category', 'all')

        if category == 'all':
            current_app.db_manager.execute_query('DELETE FROM campaign_progress')
            logger.info("🔄 Reset campaign progress for all categories")
        else:
            current_app.db_manager.execute_query('DELETE FROM campaign_progress WHERE category = ?', (category,))
            logger.info(f"🔄 Reset campaign progress for category: {category}")

        return jsonify({'success': True, 'message': f'Campaign progress reset for {category}'})

    except Exception as e:
        logger.error(f"❌ Error resetting campaign progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/status/<categoryKey>', methods=['GET'])
def get_campaign_status(categoryKey):
    """Get campaign status for a specific category"""
    try:
        # Check if there's an active or recent campaign for this category
        progress = current_app.db_manager.execute_query('''
            SELECT category, last_processed_member_id, last_processed_index,
                   last_campaign_date, total_members_in_category, notes
            FROM campaign_progress
            WHERE category = ?
            ORDER BY last_campaign_date DESC
            LIMIT 1
        ''', (categoryKey,), fetch_one=True)

        if progress:
            # Convert to dict if needed
            if not isinstance(progress, dict):
                progress = dict(progress)

            # Calculate progress percentage
            if progress.get('total_members_in_category') and progress.get('last_processed_index'):
                percentage = (progress['last_processed_index'] / progress['total_members_in_category']) * 100
                progress['progress_percentage'] = round(percentage, 2)
            else:
                progress['progress_percentage'] = 0

            # Determine status based on progress
            if progress['progress_percentage'] >= 100:
                progress['status'] = 'completed'
            elif progress['last_processed_index'] > 0:
                progress['status'] = 'in_progress'
            else:
                progress['status'] = 'not_started'

            logger.info(f"✅ Campaign status for {categoryKey}: {progress['status']}")
            return jsonify({'success': True, 'campaign': progress, 'exists': True})
        else:
            return jsonify({'success': True, 'campaign': None, 'exists': False})

    except Exception as e:
        logger.error(f"❌ Error getting campaign status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/<int:campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause a running campaign"""
    try:
        # Update campaign status in campaigns table
        current_app.db_manager.execute_query('''
            UPDATE campaigns
            SET notes = COALESCE(notes, '') || ' [PAUSED]'
            WHERE id = ?
        ''', (campaign_id,))

        logger.info(f"⏸️ Campaign {campaign_id} paused")
        return jsonify({'success': True, 'message': 'Campaign paused', 'campaign_id': campaign_id})

    except Exception as e:
        logger.error(f"❌ Error pausing campaign: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/<int:campaign_id>/stop', methods=['POST'])
def stop_campaign(campaign_id):
    """Stop a campaign completely"""
    try:
        # Update campaign status
        current_app.db_manager.execute_query('''
            UPDATE campaigns
            SET notes = COALESCE(notes, '') || ' [STOPPED]'
            WHERE id = ?
        ''', (campaign_id,))

        logger.info(f"🛑 Campaign {campaign_id} stopped")
        return jsonify({'success': True, 'message': 'Campaign stopped', 'campaign_id': campaign_id})

    except Exception as e:
        logger.error(f"❌ Error stopping campaign: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/<int:campaign_id>/resume', methods=['POST'])
def resume_campaign(campaign_id):
    """Resume a paused campaign"""
    try:
        # Get campaign details
        campaign = current_app.db_manager.execute_query('''
            SELECT * FROM campaigns WHERE id = ?
        ''', (campaign_id,), fetch_one=True)

        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404

        # Update campaign notes to remove PAUSED status
        current_app.db_manager.execute_query('''
            UPDATE campaigns
            SET notes = REPLACE(notes, '[PAUSED]', '[RESUMED]')
            WHERE id = ?
        ''', (campaign_id,))

        logger.info(f"▶️ Campaign {campaign_id} resumed")
        return jsonify({'success': True, 'message': 'Campaign resumed', 'campaign_id': campaign_id})

    except Exception as e:
        logger.error(f"❌ Error resuming campaign: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/history', methods=['GET'])
def get_campaign_history():
    """Get campaign history"""
    try:
        limit = int(request.args.get('limit', 20))
        
        # Ensure campaigns table exists with cross-database compatibility
        current_app.db_manager.execute_query('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY,
                campaign_name TEXT,
                message_text TEXT,
                message_type TEXT,
                subject TEXT,
                categories TEXT,
                total_recipients INTEGER,
                successful_sends INTEGER,
                failed_sends INTEGER,
                errors TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        campaigns = current_app.db_manager.execute_query('''
            SELECT * FROM campaigns 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        if not campaigns:
            campaigns = []
        
        return jsonify({'success': True, 'campaigns': campaigns})
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/messages/member/<member_name>', methods=['GET'])
def get_member_messages(member_name):
    """Get all messages for a specific member (fallback endpoint for frontend)"""
    try:
        logger.info(f"📬 Fallback endpoint: Getting messages for member name: {member_name}")

        # ENHANCED: Search all possible name fields to capture FULL conversation (both directions)
        # This matches the main endpoint's comprehensive search including staff replies
        messages = current_app.db_manager.execute_query('''
            SELECT *, rowid FROM messages
            WHERE LOWER(from_user) = LOWER(?)
               OR LOWER(to_user) = LOWER(?)
               OR LOWER(recipient_name) = LOWER(?)
               OR LOWER(from_member_name) = LOWER(?)
               OR LOWER(to_staff_name) = LOWER(?)
               OR (LOWER(recipient_name) = LOWER(?) AND status = 'sent')
               OR (LOWER(recipient_name) = LOWER(?) AND delivery_status = 'sent')
               OR LOWER(content) LIKE LOWER(?)
            ORDER BY rowid DESC
            LIMIT 100
        ''', (member_name, member_name, member_name, member_name, member_name, member_name, member_name, f'%{member_name}%'), fetch_all=True)

        if not messages:
            messages = []

        # Convert Row objects to dicts if needed
        if messages and not isinstance(messages[0], dict):
            messages = [dict(row) for row in messages]

        # Convert datetime objects to strings for template compatibility
        for message in messages:
            for key, value in message.items():
                if isinstance(value, (dt.datetime, dt.date)):
                    message[key] = value.isoformat()

        logger.info(f"✅ Fallback endpoint retrieved {len(messages)} messages for member: {member_name}")
        return jsonify({'success': True, 'messages': messages, 'member_name': member_name})

    except Exception as e:
        logger.error(f"❌ Error getting member messages (fallback): {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/messages/search', methods=['GET'])
def search_messages():
    """Search ClubOS messages by content, member, or actions"""
    try:
        owner_id = request.args.get('owner_id', '187032782')
        query = request.args.get('q', '')
        action_type = request.args.get('action', '')  # confirmation, opt_in, opt_out, emoji
        limit = request.args.get('limit', 50)
        
        conn = current_app.db_manager.get_connection()
        cursor = current_app.db_manager.get_cursor(conn)
        
        # Build search query
        sql = '''
            SELECT * FROM messages 
            WHERE owner_id = ?
        '''
        params = [owner_id]
        
        if query:
            sql += ' AND (content LIKE ? OR member_id LIKE ? OR from_user LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
        if action_type:
            if action_type == 'confirmation':
                sql += ' AND is_confirmation = 1'
            elif action_type == 'opt_in':
                sql += ' AND is_opt_in = 1'
            elif action_type == 'opt_out':
                sql += ' AND is_opt_out = 1'
            elif action_type == 'emoji':
                sql += ' AND has_emoji = 1'
        
        sql += ' ORDER BY rowid DESC LIMIT ?'
        params.append(limit)
        
        messages = current_app.db_manager.execute_query(sql, params)
        if not messages:
            messages = []
        
        logger.info(f"✅ Search returned {len(messages)} ClubOS messages for query: {query}")
        return jsonify({'success': True, 'messages': messages, 'query': query})
        
    except Exception as e:
        logger.error(f"❌ Error searching ClubOS messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/members/categories', methods=['GET'])
def get_member_categories():
    """Get member categories for campaign targeting based on actual ClubHub statusMessage values"""
    try:
        # Debug: Check what database we're connected to with cross-database compatibility
        try:
            # Try to query the members table directly to check if it exists
            table_check = current_app.db_manager.execute_query("SELECT COUNT(*) FROM members LIMIT 1")
            table_exists = True
            logger.info(f"🔍 Database table check: members table exists = {table_exists}")
        except Exception as e:
            table_exists = False
            logger.info(f"🔍 Database table check: members table exists = {table_exists} (error: {e})")
        
        # Get actual status_message counts from ClubHub data
        raw_results = current_app.db_manager.execute_query('''
            SELECT 
                status_message,
                COUNT(*) as count
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message
            ORDER BY count DESC
        ''')
        
        if not raw_results:
            raw_results = []
            
        logger.info(f"🔍 Raw database query results: {len(raw_results)} rows")
        for i, row in enumerate(raw_results[:5]):  # Log first 5 results
            logger.info(f"  Row {i+1}: status_message='{row.get('status_message', 'N/A')}', count={row.get('count', 0)}")
        
        categories = []
        for row in raw_results:
            status_msg = row.get('status_message')
            count = row.get('count', 0)
            if status_msg:
                categories.append({
                    'name': status_msg,
                    'count': count,
                    'label': status_msg,  # Use the actual ClubHub status message as label
                    'value': status_msg   # For consistent API response
                })
        
        logger.info(f"✅ Retrieved {len(categories)} real ClubHub status categories")
        return jsonify({'success': True, 'categories': categories})
        
    except Exception as e:
        logger.error(f"❌ Error getting member categories: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/members/all', methods=['GET'])
def get_all_members():
    """Get all members with optional category filtering"""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)

        if category:
            # Map category to status_message values (must match database exactly!)
            category_mapping = {
                'good_standing': ['Member is in good standing', 'In good standing'],
                'pay_per_visit': ['Pay Per Visit Member'],
                'past_due_6_30': ['Past Due 6-30 days'],
                'past_due_30_plus': ['Past Due more than 30 days.'],
                'expiring_soon': ['Member is pending cancel', 'Expiring Soon'],
                'past_due_training': [],  # Will query training_clients table separately
                'other_statuses': []  # Will use NOT IN query
            }

            # Special handling for past_due_training - query training_clients table
            if category == 'past_due_training':
                query = '''
                    SELECT clubos_member_id as prospect_id, first_name, last_name,
                           member_name as full_name, email, mobile_phone,
                           payment_status as status, payment_status as status_message,
                           total_past_due as amount_past_due, 0 as membership_fee
                    FROM training_clients
                    WHERE total_past_due > 0
                '''
                if limit:
                    query += f' LIMIT {limit}'
                members = current_app.db_manager.execute_query(query, fetch_all=True)

            # Special handling for other_statuses - all members NOT in main categories
            elif category == 'other_statuses':
                excluded_statuses = [
                    'Member is in good standing', 'In good standing',
                    'Pay Per Visit Member',
                    'Past Due 6-30 days',
                    'Past Due more than 30 days.',
                    'Member is pending cancel', 'Expiring Soon'
                ]
                placeholders = ','.join(['?' for _ in excluded_statuses])
                query = f'''
                    SELECT prospect_id, first_name, last_name, full_name, email, mobile_phone,
                           status, status_message, amount_past_due, membership_fee
                    FROM members
                    WHERE status_message IS NOT NULL
                    AND status_message NOT IN ({placeholders})
                    AND status_message NOT LIKE '%good standing%'
                    AND status_message NOT LIKE '%expir%'
                '''
                if limit:
                    query += f' LIMIT {limit}'
                members = current_app.db_manager.execute_query(query, tuple(excluded_statuses), fetch_all=True)

            else:
                # Regular category - filter by status_message
                status_messages = category_mapping.get(category, [])

                if status_messages:
                    placeholders = ','.join(['?' for _ in status_messages])
                    query = f'''
                        SELECT prospect_id, first_name, last_name, full_name, email, mobile_phone,
                               status, status_message, amount_past_due, membership_fee
                        FROM members
                        WHERE status_message IN ({placeholders})
                    '''
                    if limit:
                        query += f' LIMIT {limit}'
                    members = current_app.db_manager.execute_query(query, tuple(status_messages), fetch_all=True)
                else:
                    # Unknown category - return empty list instead of all members
                    logger.warning(f"⚠️ Unknown category: {category}")
                    members = []
        else:
            # No category filter - return all members
            query = '''
                SELECT prospect_id, first_name, last_name, full_name, email, mobile_phone,
                       status, status_message, amount_past_due, membership_fee
                FROM members
            '''
            if limit:
                query += f' LIMIT {limit}'

            members = current_app.db_manager.execute_query(query, fetch_all=True)

        # Convert to list of dicts if needed
        if members and not isinstance(members[0], dict):
            members = [dict(m) for m in members]

        logger.info(f"✅ Retrieved {len(members) if members else 0} members")
        return jsonify({'success': True, 'members': members or []})

    except Exception as e:
        logger.error(f"❌ Error getting all members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/prospects/all', methods=['GET'])
def get_all_prospects():
    """Get all prospects with optional filtering"""
    try:
        limit = request.args.get('limit', type=int)
        status = request.args.get('status')

        query = '''
            SELECT prospect_id, first_name, last_name, email, mobile_phone,
                   status, source, interest_level, created_date
            FROM prospects
        '''

        params = []
        if status:
            query += ' WHERE status = ?'
            params.append(status)

        if limit:
            query += f' LIMIT {limit}'

        prospects = current_app.db_manager.execute_query(query, tuple(params) if params else None, fetch_all=True)

        # Convert to list of dicts if needed
        if prospects and not isinstance(prospects[0], dict):
            prospects = [dict(p) for p in prospects]

        logger.info(f"✅ Retrieved {len(prospects) if prospects else 0} prospects")
        return jsonify({'success': True, 'prospects': prospects or []})

    except Exception as e:
        logger.error(f"❌ Error getting all prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/messages/send', methods=['POST'])
def send_message_route():
    """Single message sending using EXACT same logic as working campaign system"""
    try:
        data = request.get_json()
        logger.info(f"📨 Single message request (using campaign logic): {data}")
        
        # Validate required fields
        message_text = data.get('message', '').strip()
        if not message_text:
            return jsonify({
                'success': False,
                'error': 'Message text is required'
            }), 400
        
        # Get member identification - support both member_id and member_name
        member_id = data.get('member_id')
        member_name = data.get('member_name')
        
        if not member_id and not member_name:
            return jsonify({
                'success': False,
                'error': 'Either member_id or member_name must be provided'
            }), 400
        
        # Get message type
        channel = data.get('channel', 'sms')  # 'sms' or 'email'
        
        logger.info(f"📱 Single message - Member: {member_name or member_id}, Channel: {channel}")
        
        # Get member data using EXACT SAME LOGIC as campaigns
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        member_data = None
        person_type = 'member'  # Track if this is a member or prospect
        
        # If member_name is provided, look up the full member data (same as campaign logic)
        if member_name:
            logger.info(f"🔍 Looking up member by name: {member_name}")
            
            # First search members table
            all_members = db_manager.get_all_members()
            logger.info(f"📋 Searching through {len(all_members)} members for '{member_name}'")
            
            for member in all_members:
                # EXACT same name matching logic as campaigns
                full_name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                if full_name == member_name or member.get('full_name', '') == member_name or member.get('name', '') == member_name:
                    member_data = member
                    member_id = member.get('member_id') or member.get('id') or member.get('guid') or member.get('prospect_id')
                    logger.info(f"✅ Found member {member_name} with ID: {member_id}")
                    logger.info(f"📋 Member data: email={member.get('email')}, phone={member.get('mobile_phone')}")
                    break
            
            # If not found in members, search prospects table
            if not member_data:
                logger.info(f"🔍 Not found in members, searching prospects for '{member_name}'")
                all_prospects = db_manager.get_prospects()
                prospects_list = [dict(p) for p in all_prospects] if all_prospects else []
                logger.info(f"📋 Searching through {len(prospects_list)} prospects for '{member_name}'")
                
                for prospect in prospects_list:
                    full_name = f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip()
                    if full_name == member_name or prospect.get('full_name', '') == member_name:
                        member_data = prospect
                        member_id = prospect.get('prospect_id') or prospect.get('id')
                        person_type = 'prospect'
                        logger.info(f"✅ Found prospect {member_name} with ID: {member_id}")
                        logger.info(f"📋 Prospect data: email={prospect.get('email')}, phone={prospect.get('mobile_phone')}")
                        break
            
            if not member_data:
                logger.error(f"❌ '{member_name}' not found in members or prospects database")
                return jsonify({
                    'success': False,
                    'error': f'"{member_name}" not found in members or prospects database'
                }), 404
                
        elif member_id:
            # Look up member data by ID (same as campaign logic)
            logger.info(f"🔍 Looking up member by ID: {member_id}")
            
            # First search members table
            all_members = db_manager.get_all_members()
            for member in all_members:
                if (str(member.get('member_id')) == str(member_id) or 
                    str(member.get('id')) == str(member_id) or 
                    str(member.get('guid')) == str(member_id) or
                    str(member.get('prospect_id')) == str(member_id)):
                    member_data = member
                    member_name = member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                    logger.info(f"✅ Found member ID {member_id}: {member_name}")
                    logger.info(f"📋 Member data: email={member.get('email')}, phone={member.get('mobile_phone')}")
                    break
            
            # If not found in members, search prospects table
            if not member_data:
                logger.info(f"🔍 Not found in members, searching prospects by ID: {member_id}")
                all_prospects = db_manager.get_prospects()
                prospects_list = [dict(p) for p in all_prospects] if all_prospects else []
                
                for prospect in prospects_list:
                    if (str(prospect.get('prospect_id')) == str(member_id) or 
                        str(prospect.get('id')) == str(member_id)):
                        member_data = prospect
                        member_name = prospect.get('full_name') or f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip()
                        person_type = 'prospect'
                        logger.info(f"✅ Found prospect ID {member_id}: {member_name}")
                        logger.info(f"📋 Prospect data: email={prospect.get('email')}, phone={prospect.get('mobile_phone')}")
                        break
            
            if not member_data:
                logger.error(f"❌ ID '{member_id}' not found in members or prospects database")
                return jsonify({
                    'success': False,
                    'error': f'ID "{member_id}" not found in members or prospects database'
                }), 404
        
        # Initialize ClubOS messaging client EXACTLY like campaigns do
        from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        
        secrets_manager = SecureSecretsManager()
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        
        if not username or not password:
            logger.error("❌ ClubOS credentials not configured")
            return jsonify({
                'success': False,
                'error': 'ClubOS credentials not configured'
            }), 500
        
        logger.info("🔄 Initializing ClubOS messaging client...")
        client = ClubOSMessagingClient(username, password)
        
        logger.info("🔐 Authenticating with ClubOS...")
        if not client.authenticate():
            logger.error("❌ ClubOS authentication failed")
            return jsonify({
                'success': False,
                'error': 'ClubOS authentication failed'
            }), 401
        
        logger.info("✅ ClubOS authentication successful")
        
        # CRITICAL: Log the exact member data being used for messaging
        logger.info(f"📨 FINAL CHECK - Sending to {person_type}: Name='{member_name}', ID='{member_id}', Email='{member_data.get('email') if member_data else 'None'}', Phone='{member_data.get('mobile_phone') if member_data else 'None'}'")
        
        # Send message using EXACT SAME method as campaigns
        logger.info(f"📤 Sending {channel} message to {person_type} using campaign-tested method...")
        
        success = client.send_message(
            member_id=member_id,
            message_text=message_text,
            channel=channel,
            member_data=member_data  # CRITICAL: Use the exact same parameter as campaigns
        )
        
        if success:
            logger.info(f"✅ Single message sent successfully to {person_type} {member_name} (ID: {member_id})")
            return jsonify({
                'success': True,
                'message': f'Message sent successfully to {member_name}',
                'member_id': member_id,
                'member_name': member_name,
                'channel': channel
            })
        else:
            logger.error(f"❌ Failed to send message to {member_name} (ID: {member_id})")
            return jsonify({
                'success': False,
                'error': f'Failed to send {channel} message through ClubOS'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error in single message sending: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messaging_bp.route('/api/messages/send_bulk', methods=['POST'])
# @require_auth  # Temporarily disabled for testing
def send_bulk_message_route():
    """Route to send a message to a member."""
    if request.method == 'POST':
        data = request.get_json()
        member_ids = data.get('member_ids')
        message = data.get('message')

        if not member_ids or not message:
            return jsonify({'status': 'error', 'message': 'Member IDs and message are required.'}), 400

        try:
            from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
            messaging_client = ClubOSMessagingClient()
            success_count = 0
            failure_count = 0
            failed_members = []
            
            # Send message to each member ID
            for member_id in member_ids:
                try:
                    success = messaging_client.send_message(member_id, message)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1
                        failed_members.append(member_id)
                except Exception as e:
                    failure_count += 1
                    failed_members.append(member_id)
                    current_app.logger.error(f"Error sending message to {member_id}: {e}")
            
            return jsonify({
                'success': True,
                'sent': success_count,
                'failed': failure_count,
                'failed_members': failed_members
            })
        except Exception as e:
            current_app.logger.error(f"Error in send_bulk_message_route: {e}")
            return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

@messaging_bp.route('/api/messages/templates', methods=['GET'])
# @require_auth  # Temporarily disabled for testing
def get_message_templates():
    try:
        from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
        messaging_client = ClubOSMessagingClient()
        templates = messaging_client.get_message_templates()
        if templates is not None:
            return jsonify({'status': 'success', 'templates': templates})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to retrieve message templates.'}), 500
    except Exception as e:
        current_app.logger.error(f"Error getting message templates: {e}")
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

@messaging_bp.route('/api/messaging/inbox/recent', methods=['GET'])
# @require_auth  # Temporarily disabled for testing
def get_recent_inbox():
    """Get recent messages from database - Real-time service handles ClubOS sync"""
    try:
        limit = request.args.get('limit', 50, type=int)

        # Get total message count for debug info
        count_result = current_app.db_manager.execute_query('''
            SELECT COUNT(*) as count FROM messages
        ''', fetch_one=True)
        total_in_db = count_result['count'] if count_result else 0

        # SIMPLIFIED QUERY: Get recent messages ordered by timestamp (message time)
        # ClubOS timestamp parsing WORKS for today's messages (9:03 AM → 2025-12-05T09:03:00)
        # For older messages with dates like "Nov 21", the year may be wrong but order is still correct
        # Use timestamp DESC to show most recent messages first (today's messages at top)
        # Also fetch ai_processed and read_at for read/unread status
        messages = current_app.db_manager.execute_query('''
            SELECT
                m.id,
                m.content,
                m.from_user,
                m.owner_id,
                m.created_at,
                m.channel,
                m.timestamp,
                m.status,
                m.message_type,
                m.rowid,
                COALESCE(m.ai_processed, 0) as ai_processed,
                m.read_at
            FROM messages m
            WHERE m.channel = 'clubos'
            ORDER BY m.timestamp DESC
            LIMIT ?
        ''', (limit * 3,), fetch_all=True)  # Get extra to account for duplicates after grouping

        # Handle None result from execute_query
        if messages is None:
            messages = []

        # Convert to list of dicts if needed
        if messages and hasattr(messages[0], 'keys'):
            messages = [dict(row) for row in messages]

        # PERFORMANCE OPTIMIZATION: Batch lookup sender names (with safety limits)
        # Collect unique sender names (limit to avoid SQL query size issues)
        sender_names = set()
        for message in messages:
            sender_name = message.get('from_user', '').strip()
            if sender_name:
                sender_names.add(sender_name)

        # Build lookup dictionaries
        member_lookup = {}
        prospect_lookup = {}

        # IMPROVED: Use flexible name matching to handle variations (Angela vs Angela L vs Angela Louise)
        if sender_names and len(sender_names) < 100:
            try:
                # Query ALL members and prospects ONCE, then match in Python (faster for small datasets)
                all_members = current_app.db_manager.execute_query('''
                    SELECT guid, prospect_id, full_name, first_name, last_name
                    FROM members
                ''', fetch_all=True)

                if all_members:
                    for member in all_members:
                        if not isinstance(member, dict):
                            member = dict(member)
                        full_name = member.get('full_name', '').strip()
                        first_name = member.get('first_name', '').strip()
                        last_name = member.get('last_name', '').strip()
                        guid = member.get('guid') or member.get('prospect_id')

                        if full_name and guid:
                            # Match against all sender names using flexible matching
                            for sender_name in sender_names:
                                sender_lower = sender_name.lower()
                                full_lower = full_name.lower()

                                # Match if:
                                # 1. Exact match: "Angela Franke" == "Angela Franke"
                                # 2. Partial match: "Angela Franke" in "Angela L Franke"
                                # 3. First+Last match: "Angela" + "Franke" both in full name
                                if (sender_lower == full_lower or
                                    sender_lower in full_lower or
                                    (first_name and last_name and
                                     first_name.lower() in sender_lower and
                                     last_name.lower() in sender_lower)):
                                    member_lookup[sender_name.lower()] = guid
                                    break

                # Query ALL prospects ONCE (only if not already found as member)
                all_prospects = current_app.db_manager.execute_query('''
                    SELECT prospect_id, full_name
                    FROM prospects
                ''', fetch_all=True)

                if all_prospects:
                    for prospect in all_prospects:
                        if not isinstance(prospect, dict):
                            prospect = dict(prospect)
                        full_name = prospect.get('full_name', '').strip()
                        prospect_id = prospect.get('prospect_id')

                        if full_name and prospect_id:
                            for sender_name in sender_names:
                                # Skip if already found as member
                                if sender_name.lower() in member_lookup:
                                    continue

                                sender_lower = sender_name.lower()
                                full_lower = full_name.lower()

                                # Same flexible matching for prospects
                                if sender_lower == full_lower or sender_lower in full_lower:
                                    prospect_lookup[sender_name.lower()] = f"prospect:{prospect_id}"
                                    break

                logger.info(f"📋 Batch lookup: {len(member_lookup)} members, {len(prospect_lookup)} prospects from {len(sender_names)} senders")

            except Exception as lookup_err:
                logger.warning(f"⚠️ Batch lookup failed, will use fallback: {lookup_err}")
                # Clear lookups on error so we fall back to name search
                member_lookup = {}
                prospect_lookup = {}

        # Build set of known full names for content extraction
        known_names = set()
        try:
            all_members = current_app.db_manager.execute_query('''
                SELECT full_name FROM members WHERE full_name IS NOT NULL
            ''', fetch_all=True)
            if all_members:
                for m in all_members:
                    name = m.get('full_name', '').strip().lower() if isinstance(m, dict) else str(m[0]).strip().lower()
                    if name:
                        known_names.add(name)
            
            all_prospects = current_app.db_manager.execute_query('''
                SELECT full_name FROM prospects WHERE full_name IS NOT NULL  
            ''', fetch_all=True)
            if all_prospects:
                for p in all_prospects:
                    name = p.get('full_name', '').strip().lower() if isinstance(p, dict) else str(p[0]).strip().lower()
                    if name:
                        known_names.add(name)
            logger.debug(f"📋 Loaded {len(known_names)} known names for content extraction")
        except Exception as e:
            logger.warning(f"⚠️ Could not load known names: {e}")

        # Convert messages to individual message items using prebuilt lookups (FAST!)
        # Also extract sender name from content for 'Unknown' messages
        message_items = []
        seen_senders = set()  # Track senders to show only latest message per sender
        
        import re
        for message in messages:
            sender_name = message.get('from_user', 'Unknown')
            content = message.get('content', '')

            # CRITICAL FIX: For 'Unknown' senders, try to extract name from content
            # ClubOS prefixes the sender name to the message content like "Jeremy MayoHello there"
            if sender_name == 'Unknown' and content:
                # Strategy: Check progressively shorter prefixes against known names database
                best_match = None
                for end_pos in range(min(40, len(content)), 5, -1):
                    prefix = content[:end_pos].strip()
                    words = prefix.split()
                    if len(words) >= 2:
                        potential_name = ' '.join(words[:2])
                        if potential_name.lower() in known_names:
                            best_match = potential_name
                            break
                
                if best_match:
                    sender_name = best_match
                    logger.debug(f"📧 Matched known name from content: '{sender_name}'")
                else:
                    # Fallback: Just extract first two capitalized words
                    name_match = re.match(r'^([A-Z][a-z]+)\s+([A-Z][a-z]+)', content)
                    if name_match:
                        sender_name = f"{name_match.group(1)} {name_match.group(2)}"
                        logger.debug(f"📧 Extracted name pattern from content: '{sender_name}'")

            # Skip completely invalid senders
            if not sender_name or sender_name.strip() == '' or sender_name == 'Unknown':
                continue

            sender_name = sender_name.strip()
            
            # Group by sender - only show the most recent message per sender
            sender_key = sender_name.lower()
            if sender_key in seen_senders:
                continue  # Skip older messages from same sender
            seen_senders.add(sender_key)

            # Use prebuilt lookup dictionaries (instant lookup, no database query)
            member_id = member_lookup.get(sender_name.lower())
            if not member_id:
                member_id = prospect_lookup.get(sender_name.lower())

            # Fallback: If no member/prospect found in lookup, use name search
            if not member_id:
                member_id = f"search:{sender_name.replace(' ', '_')}"

            owner_id = message.get('owner_id', '')

            # Use the actual message timestamp for display, fallback to created_at
            display_time = message.get('timestamp') or message.get('created_at')

            # Determine read/unread status
            # Message is READ if: ai_processed=1 OR read_at is set
            ai_processed = message.get('ai_processed', 0)
            read_at = message.get('read_at')
            is_read = (ai_processed == 1) or (read_at is not None)

            # Create individual message item
            message_item = {
                'id': message.get('id'),
                'member_id': member_id,
                'owner_id': owner_id,
                'member_name': sender_name,
                'message_content': message.get('content', ''),
                'created_at': display_time,
                'channel': message.get('channel', 'ClubOS'),
                'status': 'read' if is_read else 'unread',
                'message_type': message.get('message_type', 'text'),
                'is_new': not is_read  # Convenience flag for UI
            }

            message_items.append(message_item)

        return jsonify({
            'success': True,
            'messages': message_items,  # Return individual messages, not threads
            'count': len(message_items),
            'total_in_database': total_in_db,
            'debug_info': {
                'total_messages_in_db': total_in_db,
                'conversations_returned': len(message_items),
                'query_limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting recent inbox: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messaging_bp.route('/api/messaging/mark-all-read', methods=['POST'])
def mark_all_messages_read():
    """
    Mark all existing messages as read/processed.
    This is used to prevent AI from responding to historical messages
    when first enabling auto-reply.
    """
    try:
        # Mark all messages as ai_processed = 1 and set read_at
        current_app.db_manager.execute_query('''
            UPDATE messages
            SET ai_processed = 1, read_at = ?
            WHERE ai_processed IS NULL OR ai_processed = 0
        ''', (datetime.now().isoformat(),))

        # Get count of all read messages
        affected = current_app.db_manager.execute_query('''
            SELECT COUNT(*) as count FROM messages WHERE ai_processed = 1
        ''', fetch_one=True)

        # Handle both dict and Row objects
        if affected:
            if isinstance(affected, dict):
                count = affected.get('count', 0)
            else:
                count = affected[0] if affected else 0
        else:
            count = 0

        logger.info(f"✅ Marked all existing messages as read ({count} total)")

        return jsonify({
            'success': True,
            'message': f'Marked {count} messages as read',
            'count': count
        })

    except Exception as e:
        logger.error(f"❌ Error marking messages as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messaging_bp.route('/api/messaging/message/<message_id>/read', methods=['POST'])
def mark_message_read(message_id: str):
    """Mark a specific message as read"""
    try:
        current_app.db_manager.execute_query('''
            UPDATE messages
            SET read_at = ?, status = 'read'
            WHERE id = ?
        ''', (datetime.now().isoformat(), message_id))

        logger.info(f"✅ Marked message {message_id} as read")

        return jsonify({
            'success': True,
            'message_id': message_id,
            'status': 'read'
        })

    except Exception as e:
        logger.error(f"❌ Error marking message as read: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messaging_bp.route('/api/debug/raw-messages', methods=['GET'])
def debug_raw_messages():
    """Debug endpoint to see raw messages in database"""
    try:
        limit = request.args.get('limit', 20, type=int)

        # Get raw messages from database
        messages = current_app.db_manager.execute_query('''
            SELECT id, content, from_user, owner_id, created_at, channel, status
            FROM messages
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))

        if messages is None:
            messages = []

        # Convert to list of dicts if needed
        if messages and not isinstance(messages[0], dict):
            messages = [dict(row) for row in messages]

        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })

    except Exception as e:
        logger.error(f"❌ Error getting raw messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/contact/<contact_name>')
def contact_profile(contact_name):
    """Contact profile page for external contacts (not in members database)"""
    try:
        # Clean up the contact name
        contact_name = contact_name.replace('_', ' ').strip()

        # Get message history for this contact
        messages = current_app.db_manager.execute_query('''
            SELECT id, content, from_user, created_at, channel, status, message_type
            FROM messages
            WHERE LOWER(from_user) = LOWER(?)
            ORDER BY created_at DESC
            LIMIT 100
        ''', (contact_name,))

        if messages is None:
            messages = []

        # Convert to list of dicts if needed
        if messages and not isinstance(messages[0], dict):
            messages = [dict(row) for row in messages]

        # Format messages for display
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'content': msg.get('content', ''),
                'created_at': msg.get('created_at', ''),
                'channel': msg.get('channel', 'ClubOS'),
                'status': msg.get('status', 'received'),
                'sender_type': 'contact'
            })

        # Create contact data
        contact_data = {
            'name': contact_name,
            'type': 'external_contact',
            'message_count': len(formatted_messages),
            'last_message': formatted_messages[0] if formatted_messages else None
        }

        return render_template('contact_profile.html',
                             contact_name=contact_name,
                             contact_info=contact_data,
                             message_count=len(formatted_messages),
                             last_message_date=formatted_messages[0]['created_at'] if formatted_messages else None,
                             messages=formatted_messages)

    except Exception as e:
        logger.error(f"❌ Error loading contact profile for {contact_name}: {e}")
        return render_template('error.html', error=str(e))

@messaging_bp.route('/api/messaging/thread', methods=['GET'])
# @require_auth  # Temporarily disabled for testing
def get_thread_messages():
    """Get all messages for a specific member"""
    try:
        member_id = request.args.get('memberId', type=str)
        limit = request.args.get('limit', 50, type=int)
        
        if not member_id:
            return jsonify({
                'success': False,
                'error': 'Missing memberId parameter'
            }), 400
        
        # Get messages for this member using DatabaseManager for cross-database compatibility
        messages = current_app.db_manager.execute_query('''
            SELECT * FROM messages 
            WHERE owner_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (member_id, limit))
        
        # Handle None result from execute_query
        if messages is None:
            messages = []
        
        # Convert to list of dicts if needed
        if messages and not isinstance(messages[0], dict):
            messages = [dict(row) for row in messages]
        
        # Enhance messages with extracted names
        for message in messages:
            if message.get('from_user') == 'Unknown' or not message.get('from_user'):
                extracted_name = extract_name_from_message_content(message.get('content', ''))
                message['from_user'] = extracted_name
                message['display_name'] = extracted_name
        
        # Create thread structure
        threads = [{
            'thread_type': 'clubos',
            'messages': [
                {
                    'message_content': msg.get('content', ''),
                    'created_at': msg.get('created_at'),
                    'sender_name': msg.get('from_user', 'Unknown'),
                    'direction': 'inbound' if msg.get('from_user') != 'System' else 'outbound',
                    'status': msg.get('status', 'received')
                }
                for msg in messages
            ]
        }]
        
        return jsonify({
            'success': True,
            'threads': threads,
            'member_id': member_id
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting thread messages: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/api/campaigns/debug-validation', methods=['POST'])
def debug_campaign_validation():
    """Debug campaign validation pipeline without sending any messages"""
    try:
        data = request.json
        logger.info(f"🔍 DEBUG: Campaign validation request: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract parameters
        categories_raw = data.get('categories', [])
        single_category = data.get('category', '')
        
        if single_category and not categories_raw:
            member_categories = [single_category]
        elif categories_raw:
            member_categories = categories_raw
        else:
            member_categories = []
            
        if not member_categories:
            return jsonify({'success': False, 'error': 'At least one member category must be selected'}), 400
        
        message_type = data.get('type', 'sms')
        max_recipients = data.get('max_recipients', 100)
        
        debug_results = {
            'input_categories': member_categories,
            'message_type': message_type,
            'max_recipients': max_recipients,
            'category_results': [],
            'total_validated_members': 0,
            'validation_summary': {}
        }
        
        # Process each category with detailed logging
        for category in member_categories:
            category_debug = {
                'original_category': category,
                'mapped_status_message': None,
                'query_executed': None,
                'query_parameters': None,
                'raw_query_results': 0,
                'validation_results': {},
                'sample_members': []
            }
            
            logger.info(f"🔍 DEBUG: Processing category: '{category}'")
            
            # Map frontend category names to database status_message values
            category_mapping = {
                # Hyphen variants
                'past-due-6-30': 'Past Due 6-30 days',
                'past-due-30': 'Past Due more than 30 days.',  # Added missing mapping!
                'past-due-30-plus': 'Past Due more than 30 days.',  # Note the period!
                'past-due-6-30-days': 'Past Due 6-30 days',
                'past-due-more-than-30-days': 'Past Due more than 30 days.',
                # Underscore variants (API/backend format)
                'past_due_6_30': 'Past Due 6-30 days',
                'past_due_30': 'Past Due more than 30 days.',
                'past_due_30_plus': 'Past Due more than 30 days.',
                'past_due_more_than_30_days': 'Past Due more than 30 days.',
                'good_standing': 'Member is in good standing',
                # General status mappings
                'good-standing': 'Member is in good standing',
                'in-good-standing': 'In good standing',  # Fixed to handle both cases
                'green': 'Member is in good standing',  # Alternative for good standing
                'comp': 'Comp Member',
                'staff': 'Staff Member',
                'staff-member': 'Staff member',  # Added lowercase variant
                'pay-per-visit': 'Pay Per Visit Member',
                'sent-to-collections': 'Sent to Collections',
                'pending-cancel': 'Member is pending cancel',
                'expired': 'Expired',
                'cancelled': 'Account has been cancelled.',
                'yellow': 'Invalid Billing Information.',  # Added yellow category
                'inactive': 'Inactive',  # Added inactive category
                'member-will-expire-within-30-days': 'Member will expire within 30 days.',  # Added expiring members
                'expiring-soon': 'Member will expire within 30 days.',  # Alternative name
                'invalid-bad-address-information': 'Invalid/Bad Address information.',  # Added address issues
                'address-issues': 'Invalid/Bad Address information.',  # Alternative name
                # Training client categories (use training_clients table)
                'training-past-due': 'training_past_due',  # Special case - query training_clients table
                'training-current': 'training_current',  # Special case - query training_clients table  
                'training-clients-past-due': 'training_past_due',  # Alternative name
                'training-clients-current': 'training_current',  # Alternative name
                'past-due-training': 'training_past_due',  # Alternative name
                # Add more mappings as needed based on your actual status messages
                'all_members': 'all_members',
                'prospects': 'prospects'
            }
            
            # Convert category name to actual database status_message
            actual_status_message = category_mapping.get(category, category)
            category_debug['mapped_status_message'] = actual_status_message
            
            logger.info(f"🔍 DEBUG: Mapped '{category}' to '{actual_status_message}'")
            
            # Use the mapped status message for database queries
            category_to_use = actual_status_message
            original_category = category  # Keep original for special case checks
            
            if category_to_use == 'all_members':
                # Special case: get all members regardless of status
                query = '''
                    SELECT id, prospect_id, email, mobile_phone, full_name, status_message
                    FROM members 
                    ORDER BY id
                    LIMIT ?
                '''
                query_params = (max_recipients,)
            elif category_to_use == 'prospects':
                # Special case: get prospects from prospects table
                query = '''
                    SELECT prospect_id as id, prospect_id, email, phone as mobile_phone, full_name, status as status_message
                    FROM prospects 
                    ORDER BY prospect_id
                    LIMIT ?
                '''
                query_params = (max_recipients,)
            elif category_to_use == 'training_past_due':
                # Special case: get past due training clients from training_clients table
                query = '''
                    SELECT 
                        tc.id as id,
                        tc.clubos_member_id as prospect_id,
                        COALESCE(tc.email, m.email) as email,
                        COALESCE(tc.phone, m.mobile_phone) as mobile_phone,
                        tc.full_name as full_name,
                        tc.payment_status as status_message
                    FROM training_clients tc
                    LEFT JOIN members m ON LOWER(TRIM(tc.full_name)) = LOWER(TRIM(m.full_name))
                    WHERE tc.payment_status = 'Past Due'
                    AND (COALESCE(tc.email, m.email) IS NOT NULL AND COALESCE(tc.email, m.email) != '')
                    AND (COALESCE(tc.phone, m.mobile_phone) IS NOT NULL AND COALESCE(tc.phone, m.mobile_phone) != '')
                    ORDER BY tc.id
                    LIMIT ?
                '''
                query_params = (max_recipients,)
            elif category_to_use == 'training_current':
                # Special case: get current training clients from training_clients table
                query = '''
                    SELECT member_id as id, clubos_member_id as prospect_id, email, phone as mobile_phone, member_name as full_name, payment_status as status_message
                    FROM training_clients 
                    WHERE payment_status = 'Current'
                    ORDER BY member_id
                    LIMIT ?
                '''
                query_params = (max_recipients,)
            elif original_category in ['expiring-soon', 'expiring']:
                # Special case for expiring members: include multiple status patterns
                query = '''
                    SELECT id, prospect_id, email, mobile_phone, full_name, status_message
                    FROM members 
                    WHERE status_message LIKE '%expire%' OR status_message = 'Expired'
                    ORDER by id
                    LIMIT ?
                '''
                query_params = (max_recipients,)
            else:
                # Regular category: filter by status_message
                query = '''
                    SELECT id, prospect_id, email, mobile_phone, full_name, status_message
                    FROM members 
                    WHERE status_message LIKE ?
                    ORDER BY id
                    LIMIT ?
                '''
                query_params = (f'%{category_to_use}%', max_recipients)
            
            category_debug['query_executed'] = query
            category_debug['query_parameters'] = query_params
            
            logger.info(f"🔍 DEBUG: Executing query with params: {query_params}")
            
            # Execute the exact same query as the campaign route
            try:
                category_members = current_app.db_manager.execute_query(query, query_params)
                
                if category_members is None:
                    category_members = []
                    logger.warning(f"🔍 DEBUG: execute_query returned None!")
                elif not isinstance(category_members, list):
                    logger.warning(f"🔍 DEBUG: execute_query returned unexpected type: {type(category_members)}")
                    category_members = []
                else:
                    logger.info(f"🔍 DEBUG: execute_query returned {len(category_members)} results")
                
                category_debug['raw_query_results'] = len(category_members)
                
                # Validate each member
                valid_email_count = 0
                valid_phone_count = 0
                valid_both_count = 0
                validation_errors = []
                
                for i, member in enumerate(category_members):
                    if i < 3:  # Store first 3 members as samples
                        category_debug['sample_members'].append({
                            'full_name': member.get('full_name') if hasattr(member, 'get') else str(member),
                            'email': member.get('email') if hasattr(member, 'get') else 'N/A',
                            'mobile_phone': member.get('mobile_phone') if hasattr(member, 'get') else 'N/A',
                            'status_message': member.get('status_message') if hasattr(member, 'get') else 'N/A'
                        })
                    
                    try:
                        # Convert row to dict for validation - handle different return types
                        if hasattr(member, 'get'):
                            member_dict = member
                        elif hasattr(member, 'keys'):
                            member_dict = dict(member)
                        else:
                            logger.warning(f"🔍 DEBUG: Unexpected member type: {type(member)}")
                            continue
                        
                        # Email validation
                        email = member_dict.get('email', '').strip() if member_dict.get('email') else ''
                        has_valid_email = bool(email and '@' in email)
                        if has_valid_email:
                            valid_email_count += 1
                        
                        # Phone validation
                        phone = member_dict.get('mobile_phone', '').strip() if member_dict.get('mobile_phone') else ''
                        clean_phone = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '') if phone else ''
                        has_valid_phone = bool(clean_phone and len(clean_phone) >= 10 and clean_phone.isdigit())
                        if has_valid_phone:
                            valid_phone_count += 1
                        
                        if has_valid_email and has_valid_phone:
                            valid_both_count += 1
                            
                    except Exception as validation_error:
                        validation_errors.append(str(validation_error))
                        logger.warning(f"🔍 DEBUG: Validation error for member: {validation_error}")
                
                category_debug['validation_results'] = {
                    'valid_email_count': valid_email_count,
                    'valid_phone_count': valid_phone_count,
                    'valid_both_count': valid_both_count,
                    'validation_errors': validation_errors
                }
                
                # Check if validation would pass for the requested message type
                if message_type == 'email':
                    would_pass = valid_email_count > 0
                elif message_type == 'sms':
                    would_pass = valid_phone_count > 0
                else:
                    would_pass = valid_both_count > 0
                
                category_debug['would_pass_validation'] = would_pass
                
                debug_results['total_validated_members'] += (valid_email_count if message_type == 'email' else valid_phone_count)
                
            except Exception as query_error:
                logger.error(f"🔍 DEBUG: Query execution error: {query_error}")
                category_debug['query_error'] = str(query_error)
                category_debug['raw_query_results'] = 0
            
            debug_results['category_results'].append(category_debug)
        
        # Final validation summary
        debug_results['validation_summary'] = {
            'total_members_found': sum(cr['raw_query_results'] for cr in debug_results['category_results']),
            'total_valid_for_message_type': debug_results['total_validated_members'],
            'would_campaign_succeed': debug_results['total_validated_members'] > 0,
            'failure_reason': 'No valid members found' if debug_results['total_validated_members'] == 0 else None
        }
        
        logger.info(f"🔍 DEBUG: Validation complete - {debug_results['total_validated_members']} valid members for {message_type}")
        
        return jsonify({
            'success': True,
            'debug_results': debug_results,
            'message': f'Debug complete: {debug_results["total_validated_members"]} valid members found for {message_type} campaigns'
        })
        
    except Exception as e:
        logger.error(f"❌ Error in debug campaign validation: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@messaging_bp.route('/api/campaign-templates', methods=['GET'])
# @require_auth  # Temporarily disabled for testing
def get_campaign_templates():
    """Get saved campaign templates"""
    try:
        logger.info("📚 Loading campaign templates...")
        
        # Get database connection
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Ensure campaign_templates table exists
        create_table_query = """
            CREATE TABLE IF NOT EXISTS campaign_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                target_group TEXT NOT NULL,
                category TEXT NOT NULL,
                max_recipients INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            )
        """
        db_manager.execute_query(create_table_query)
        
        # Query for saved campaign templates
        query = """
            SELECT id, name, message, target_group, category, created_at, 
                   last_used, usage_count, max_recipients
            FROM campaign_templates 
            WHERE active = 1
            ORDER BY usage_count DESC, last_used DESC
        """
        
        templates = db_manager.execute_query(query, fetch_all=True)
        
        # Convert to list of dicts
        template_list = []
        for template in templates or []:
            template_dict = {
                'id': template[0],
                'name': template[1],
                'message': template[2],
                'target_group': template[3],
                'category': template[4],
                'created_at': template[5],
                'last_used': template[6],
                'usage_count': template[7] or 0,
                'max_recipients': template[8] or 100
            }
            template_list.append(template_dict)
        
        logger.info(f"📚 Retrieved {len(template_list)} campaign templates")
        
        return jsonify({
            'success': True,
            'templates': template_list,
            'count': len(template_list)
        })
        
    except Exception as e:
        logger.error(f"❌ Error loading campaign templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'templates': []
        }), 500

@messaging_bp.route('/api/campaign-templates', methods=['POST'])
# @require_auth  # Temporarily disabled for testing
def save_campaign_template():
    """Save a new campaign template"""
    try:
        data = request.get_json()
        logger.info(f"💾 Saving campaign template: {data.get('name', 'Unnamed')}")
        
        # Validate required fields
        required_fields = ['name', 'message', 'target_group', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Get database connection
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Create campaign_templates table if it doesn't exist
        create_table_query = """
            CREATE TABLE IF NOT EXISTS campaign_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                target_group TEXT NOT NULL,
                category TEXT NOT NULL,
                max_recipients INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                active INTEGER DEFAULT 1
            )
        """
        db_manager.execute_query(create_table_query)
        
        # Insert new template
        insert_query = """
            INSERT INTO campaign_templates 
            (name, message, target_group, category, max_recipients, created_at, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        
        params = (
            data['name'],
            data['message'],
            data['target_group'],
            data['category'],
            data.get('max_recipients', 100),
            datetime.now().isoformat()
        )
        
        template_id = db_manager.execute_query(insert_query, params, fetch_one=False)
        
        logger.info(f"💾 Campaign template saved with ID: {template_id}")
        
        return jsonify({
            'success': True,
            'message': 'Campaign template saved successfully',
            'template_id': template_id
        })
        
    except Exception as e:
        logger.error(f"❌ Error saving campaign template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/api/campaign-templates/<int:template_id>/use', methods=['POST'])
# @require_auth  # Temporarily disabled for testing
def use_campaign_template(template_id):
    """Mark a campaign template as used (updates usage statistics)"""
    try:
        logger.info(f"🚀 Using campaign template ID: {template_id}")
        
        # Get database connection
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Update usage statistics
        update_query = """
            UPDATE campaign_templates 
            SET usage_count = COALESCE(usage_count, 0) + 1,
                last_used = ?
            WHERE id = ?
        """
        
        params = (datetime.now().isoformat(), template_id)
        db_manager.execute_query(update_query, params)
        
        # Get the updated template
        select_query = """
            SELECT name, message, target_group, category, max_recipients
            FROM campaign_templates 
            WHERE id = ? AND active = 1
        """
        
        template = db_manager.execute_query(select_query, (template_id,), fetch_one=True)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Campaign template not found'
            }), 404
        
        template_data = {
            'id': template_id,
            'name': template[0],
            'message': template[1],
            'target_group': template[2],
            'category': template[3],
            'max_recipients': template[4] or 100
        }
        
        logger.info(f"🚀 Template loaded: {template_data['name']}")
        
        return jsonify({
            'success': True,
            'template': template_data,
            'message': f'Template "{template_data["name"]}" loaded successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error using campaign template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@messaging_bp.route('/api/messaging/member-history/<member_id>', methods=['GET'])
# @require_auth  # Temporarily disabled for testing
def get_member_message_history(member_id):
    """Get complete ClubOS message history for a specific member using FollowUp endpoint"""
    try:
        from datetime import datetime
        
        logger.info(f"📬 Getting message history for member ID: {member_id}")
        
        # Try ClubOS FollowUp API first with automatic authentication
        try:
            import requests
            
            # Use the unified authentication service to get fresh ClubOS credentials
            logger.info(f"� Authenticating with ClubOS for member {member_id}")
            
            # Get authentication from the working ClubOS messaging client
            if hasattr(current_app, 'messaging_client') and current_app.messaging_client:
                messaging_client = current_app.messaging_client
                
                # Use the same session that's successfully sending messages
                if hasattr(messaging_client, 'session') and messaging_client.session:
                    auth_session = messaging_client.session
                    logger.info("✅ Using working ClubOS messaging client session")
                    # Ensure client is authenticated; try to refresh if not
                    try:
                        is_auth = getattr(messaging_client, 'authenticated', False)
                        if not is_auth and hasattr(messaging_client, 'authenticate'):
                            logger.info("🔐 Messaging client not authenticated - attempting authenticate()")
                            try:
                                auth_ok = messaging_client.authenticate()
                                logger.info(f"🔐 authenticate() returned: {auth_ok}")
                            except Exception as aerr:
                                logger.warning(f"⚠️ authenticate() raised: {aerr}")
                                logger.debug(traceback.format_exc())
                    except Exception:
                        logger.debug(traceback.format_exc())

                    # Resolve profile member identifier (guid/prospect) to actual ClubOS numeric ID and name for delegation
                    try:
                        clubos_member_id = member_id  # Default to input if lookup fails
                        member_full_name = None  # For database fallback queries
                        try:
                            # CRITICAL FIX: Select prospect_id (numeric ClubOS ID) AND full_name
                            # The guid is what we already have - we need the numeric ClubOS ID for the FollowUp API
                            # We also need the full_name for database fallback queries (messages table uses names, not IDs)
                            # Database schema: prospect_id = ClubOS numeric member ID (e.g., '66082049'), full_name = "Mark Benzinger"
                            member_lookup = None
                            
                            # First try members table by guid or prospect_id
                            try:
                                member_lookup = current_app.db_manager.execute_query(
                                    "SELECT prospect_id, full_name FROM members WHERE guid = ? OR prospect_id = ? LIMIT 1",
                                    (member_id, member_id),
                                    fetch_one=True
                                )
                            except Exception as e:
                                logger.warning(f"⚠️ Members table lookup failed: {e}")
                            
                            # If not found in members, try prospects table
                            if not member_lookup:
                                try:
                                    # Search prospects by prospect_id OR by exact full_name match
                                    member_lookup = current_app.db_manager.execute_query(
                                        "SELECT prospect_id, full_name FROM prospects WHERE prospect_id = ? OR full_name = ? COLLATE NOCASE LIMIT 1",
                                        (member_id, member_id),
                                        fetch_one=True
                                    )
                                    if member_lookup:
                                        logger.info(f"✅ Found in prospects table: {member_lookup}")
                                except Exception as pe:
                                    logger.warning(f"⚠️ Prospects table lookup failed: {pe}")
                            
                            # If still not found and member_id looks like a name, try name search
                            if not member_lookup and ' ' in member_id:
                                logger.info(f"🔍 member_id looks like a name, trying name search: {member_id}")
                                try:
                                    # Try members by name first
                                    name_parts = member_id.rsplit(' ', 1)
                                    if len(name_parts) == 2:
                                        first_name, last_name = name_parts
                                        member_lookup = current_app.db_manager.execute_query(
                                            "SELECT prospect_id, full_name FROM members WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?) LIMIT 1",
                                            (first_name, last_name),
                                            fetch_one=True
                                        )
                                        if not member_lookup:
                                            # Try prospects by name
                                            member_lookup = current_app.db_manager.execute_query(
                                                "SELECT prospect_id, full_name FROM prospects WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?) LIMIT 1",
                                                (first_name, last_name),
                                                fetch_one=True
                                            )
                                            if member_lookup:
                                                logger.info(f"✅ Found prospect by name parts: {first_name} {last_name}")
                                except Exception as ne:
                                    logger.warning(f"⚠️ Name search failed: {ne}")

                            if member_lookup:
                                # Extract the prospect_id AND full_name from the query result
                                if isinstance(member_lookup, dict):
                                    resolved_id = member_lookup.get('prospect_id')
                                    member_full_name = member_lookup.get('full_name')
                                else:
                                    resolved_id = member_lookup[0] if len(member_lookup) > 0 else None
                                    member_full_name = member_lookup[1] if len(member_lookup) > 1 else None

                                if resolved_id:
                                    clubos_member_id = str(resolved_id)  # This is ClubHub prospect_id (e.g., 66082049)
                                    logger.info(f"✅ Resolved profile ID {member_id} -> ClubHub prospect_id {clubos_member_id}, Name: {member_full_name}")

                                    # CRITICAL FIX: Get the actual ClubOS member_id by searching ClubOS
                                    # ClubHub prospect_id (66082049) ≠ ClubOS member_id (125814462)
                                    # The FollowUp API requires the ClubOS member_id, not ClubHub prospect_id!
                                    if member_full_name and hasattr(messaging_client, 'search_member_by_name'):
                                        try:
                                            # Parse first and last name from full name
                                            name_parts = member_full_name.strip().split()
                                            if len(name_parts) >= 2:
                                                first_name = name_parts[0]
                                                last_name = ' '.join(name_parts[1:])

                                                logger.info(f"🔍 Searching ClubOS for actual member_id: {first_name} {last_name}")

                                                # Search ClubOS to get the actual ClubOS member_id
                                                actual_clubos_id = messaging_client.search_member_by_name(first_name, last_name, member_type="member")

                                                if actual_clubos_id:
                                                    # Found the ClubOS member_id! Use this instead of ClubHub prospect_id
                                                    logger.info(f"✅ Found ClubOS member_id: {actual_clubos_id} (was using ClubHub prospect_id: {clubos_member_id})")
                                                    clubos_member_id = str(actual_clubos_id)
                                                else:
                                                    logger.warning(f"⚠️ ClubOS search returned no results for {member_full_name}, using ClubHub prospect_id {clubos_member_id} as fallback")
                                            else:
                                                logger.warning(f"⚠️ Could not parse name '{member_full_name}' into first/last, using ClubHub prospect_id {clubos_member_id}")
                                        except Exception as search_err:
                                            logger.error(f"❌ ClubOS search failed: {search_err}, using ClubHub prospect_id {clubos_member_id} as fallback")
                                            logger.debug(traceback.format_exc())
                                    else:
                                        logger.warning(f"⚠️ Cannot search ClubOS (no name or search function unavailable), using ClubHub prospect_id {clubos_member_id}")
                                else:
                                    logger.warning(f"⚠️ Member lookup returned None for {member_id}, using fallback")
                            else:
                                logger.warning(f"⚠️ No member found with ID {member_id}, using original ID")
                        except Exception as lookup_err:
                            logger.error(f"❌ Error during member ID resolution: {lookup_err}")
                            logger.debug(traceback.format_exc())

                        # Ensure we are delegated to the target member before calling FollowUp
                        if hasattr(messaging_client, 'delegate_to_member'):
                            logger.info(f"🔁 Performing per-member delegation for member {clubos_member_id} (profile id {member_id})")
                            try:
                                delegated_result = messaging_client.delegate_to_member(clubos_member_id)
                                logger.info(f"🔑 Delegation result for {clubos_member_id}: {delegated_result}")
                                # Log presence of delegation tokens/cookies (not their values)
                                try:
                                    sess = getattr(messaging_client, 'session', None)
                                    token_present = False
                                    delegated_id_present = False
                                    if sess and hasattr(sess, 'cookies'):
                                        token_present = bool(sess.cookies.get('apiV3AccessToken'))
                                        delegated_id_present = bool(sess.cookies.get('delegatedUserId'))
                                    logger.info(f"🔍 Delegation cookie presence - apiV3AccessToken: {token_present}, delegatedUserId: {delegated_id_present}")
                                except Exception:
                                    logger.debug(traceback.format_exc())
                            except Exception as de:
                                logger.warning(f"⚠️ Delegation call raised exception for {member_id}: {de}")
                                logger.debug(traceback.format_exc())
                        else:
                            logger.warning("⚠️ messaging_client.delegate_to_member not present; proceeding without explicit delegation")
                    except Exception:
                        logger.debug(traceback.format_exc())
                    
                    follow_up_url = "https://anytime.club-os.com/action/FollowUp"
                    
                    # Use the same headers and cookies that work for messaging
                    headers = {
                        'accept': '*/*',
                        'accept-language': 'en-US,en;q=0.9',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'origin': 'https://anytime.club-os.com',
                        'referer': 'https://anytime.club-os.com/action/Dashboard/view',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
                        'x-requested-with': 'XMLHttpRequest'
                    }
                    
                    # Copy headers from working session
                    if hasattr(auth_session, 'headers'):
                        headers.update(auth_session.headers)
                        logger.info("✅ Added headers from working session")
                    
                    cookies = auth_session.cookies if hasattr(auth_session, 'cookies') else {}
                    
                else:
                    logger.error("❌ No working session found")
                    raise Exception("No ClubOS session available")
            else:
                logger.warning("⚠️ ClubOS messaging client not available on app — attempting to create temporary client from secrets")
                # Try to create a temporary messaging client from stored secrets so the route can continue
                try:
                    try:
                        from .services.clubos_messaging_client_simple import ClubOSMessagingClient
                        from .services.authentication.secure_secrets_manager import SecureSecretsManager
                    except Exception:
                        from services.clubos_messaging_client_simple import ClubOSMessagingClient
                        from services.authentication.secure_secrets_manager import SecureSecretsManager

                    secrets_manager = SecureSecretsManager()
                    username = secrets_manager.get_secret('clubos-username')
                    password = secrets_manager.get_secret('clubos-password')

                    if username and password:
                        messaging_client = ClubOSMessagingClient(username, password)
                        auth_ok = False
                        try:
                            auth_ok = messaging_client.authenticate()
                        except Exception as tauth:
                            logger.warning(f"⚠️ Temporary messaging client authenticate() raised: {tauth}")

                        if auth_ok:
                            # Attach to app for reuse
                            try:
                                current_app.messaging_client = messaging_client
                            except Exception:
                                pass
                            auth_session = messaging_client.session
                            logger.info("✅ Temporary ClubOS messaging client created and authenticated")
                        else:
                            logger.error("❌ Could not authenticate temporary ClubOS messaging client")
                            raise Exception("ClubOS messaging client not available and temporary authentication failed")
                    else:
                        logger.error("❌ ClubOS credentials missing in secrets manager; cannot create messaging client")
                        raise Exception("ClubOS messaging client not available and no credentials")
                except Exception as create_err:
                    logger.error(f"❌ Failed to create temporary ClubOS messaging client: {create_err}")
                    raise
            
            # CRITICAL FIX: Use the resolved clubos_member_id (from above), NOT delegated_user_id
            # delegated_user_id is the MANAGER's ID (who we're logged in as)
            # clubos_member_id is the MEMBER's numeric ID (whose messages we want to fetch)
            follow_up_user = clubos_member_id  # This was resolved above from GUID→numeric ID

            # Validation: Ensure we're not accidentally fetching the manager's own messages
            # when requesting a different member's conversation
            if hasattr(messaging_client, 'logged_in_user_id'):
                manager_id = str(messaging_client.logged_in_user_id)
                if follow_up_user == manager_id and member_id != manager_id:
                    logger.error(f"❌ VALIDATION FAILED: Attempting to fetch manager's messages ({manager_id}) for member profile {member_id}")
                    logger.error(f"❌ This indicates the GUID→numeric ID lookup failed")
                    raise ValueError(f"Member ID resolution failed: would fetch wrong user's messages")

            logger.info(f"✅ Using followUpUserId: {follow_up_user} for member profile {member_id}")

            data = {
                'followUpUserId': follow_up_user,
                'followUpType': '3'  # Type 3 for messages/conversation history
            }

            # CRITICAL FIX: Get or Generate Bearer token with CORRECT delegateUserId for FollowUp API
            try:
                # First, try to get the Bearer token that ClubOS provides in cookies (most reliable)
                clubos_bearer_token = auth_session.cookies.get('apiV3AccessToken')

                if clubos_bearer_token:
                    # Use the Bearer token that ClubOS provided (best option)
                    headers['Authorization'] = f'Bearer {clubos_bearer_token}'
                    logger.info(f"✅ Using ClubOS-provided Bearer token from apiV3AccessToken cookie")
                else:
                    # If ClubOS didn't provide a token, generate one ourselves
                    import base64
                    import hashlib
                    import json

                    # Get session data
                    session_id = auth_session.cookies.get('JSESSIONID')
                    logged_in_user_id = messaging_client.logged_in_user_id if hasattr(messaging_client, 'logged_in_user_id') else auth_session.cookies.get('loggedInUserId')

                    # CRITICAL: delegateUserId should be the MEMBER we're viewing (follow_up_user)
                    # NOT the logged-in manager ID
                    delegate_user_id = follow_up_user  # This is the member's ClubOS ID

                    logger.info(f"🔑 Generating Bearer token - loggedInUserId: {logged_in_user_id}, delegateUserId: {delegate_user_id}, sessionId: {session_id}")

                    # Generate JWT Bearer token with proper delegateUserId
                    payload = {
                        'delegateUserId': int(delegate_user_id),
                        'loggedInUserId': int(logged_in_user_id),
                        'sessionId': session_id
                    }

                    # Create JWT-like token matching ClubOS format
                    header = 'eyJhbGciOiJIUzI1NiJ9'  # Standard JWT header for HMAC SHA256
                    payload_json = json.dumps(payload, separators=(',', ':'))
                    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')

                    # Generate signature based on session data
                    signature_data = f"{session_id}:{logged_in_user_id}:{delegate_user_id}"
                    signature = hashlib.sha256(signature_data.encode()).hexdigest()[:43]  # 43 chars to match JWT signature length

                    bearer_token = f"{header}.{payload_b64}.{signature}"

                    # Add Bearer token to Authorization header
                    headers['Authorization'] = f'Bearer {bearer_token}'
                    logger.info(f"✅ Generated and added Bearer token to Authorization header for FollowUp API")
                    logger.info(f"   Token payload: delegateUserId={delegate_user_id}, loggedInUserId={logged_in_user_id}")

            except Exception as token_error:
                logger.error(f"❌ Failed to get/generate Bearer token: {token_error}")
                logger.debug(traceback.format_exc())

                # Fallback: Try to use existing Authorization header from session
                try:
                    auth_header = None
                    if hasattr(messaging_client, 'session') and getattr(messaging_client, 'session') is not None:
                        auth_header = messaging_client.session.headers.get('Authorization')
                    if auth_header:
                        headers['Authorization'] = auth_header
                        logger.info("🔐 Using existing delegated Authorization header as fallback")
                    else:
                        logger.warning("⚠️ No Bearer token available - FollowUp API may fail")
                except Exception:
                    logger.debug(traceback.format_exc())
            
            logger.info(f"📬 Making ClubOS FollowUp request for member {member_id} (followUpUserId={follow_up_user})")
            
            # Use the authenticated session instead of requests.post
            response = auth_session.post(
                follow_up_url,
                headers=headers,
                data=data,
                timeout=30,
                verify=False
            )
            
            if response.status_code == 200:
                # Parse the response to extract message history
                html_content = response.text
                
                # Check for session expiry or error responses first
                if "Session Expired" in html_content or "Something isn't right" in html_content or "Please refresh the page" in html_content:
                    logger.warning(f"🔐 ClubOS session expired or error for member {member_id}: {html_content[:50]}...")
                    # Create a session expiry message
                    session_expired_message = {
                        'id': f"clubos_session_expired_{member_id}_{int(datetime.now().timestamp())}",
                        'member_id': member_id,
                        'content': "⚠️ ClubOS session expired. Recent messages may not be visible. Please refresh ClubOS authentication to view complete message history.",
                        'timestamp': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                        'created_at': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                        'message_type': 'system',
                        'status': 'info',
                        'from_user': 'System',
                        'to_user': 'Staff',
                        'source': 'clubos_session',
                        'channel': 'system',
                        'note': 'ClubOS authentication needed'
                    }
                    
                    # Combine with database messages
                    # Try a flexible DB query for local messages — be defensive about schema differences
                    # CRITICAL FIX: Messages table stores member NAMES, not numeric IDs in member_id column
                    # Search by full_name (if we have it) instead of member_id numeric value
                    try:
                        if member_full_name:
                            # Search by member name (messages table uses names, not numeric IDs)
                            db_messages = current_app.db_manager.execute_query('''
                                SELECT * FROM messages
                                WHERE from_user LIKE ? OR recipient_name LIKE ? OR content LIKE ?
                                ORDER BY created_at DESC
                                LIMIT 50
                            ''', (f'%{member_full_name}%', f'%{member_full_name}%', f'%{member_full_name}%'), fetch_all=True)
                            logger.info(f"📋 Database fallback query for '{member_full_name}' returned {len(db_messages) if db_messages else 0} messages")
                        else:
                            # Fallback: try with the original member_id (might be a GUID or name)
                            db_messages = current_app.db_manager.execute_query('''
                                SELECT * FROM messages
                                WHERE from_user LIKE ? OR recipient_name LIKE ? OR content LIKE ?
                                ORDER BY created_at DESC
                                LIMIT 50
                            ''', (f'%{member_id}%', f'%{member_id}%', f'%{member_id}%'), fetch_all=True)
                            logger.info(f"📋 Database fallback query for ID '{member_id}' returned {len(db_messages) if db_messages else 0} messages")

                        if db_messages and not isinstance(db_messages[0], dict):
                            db_messages = [dict(row) for row in db_messages]
                    except Exception as db_err:
                        logger.warning(f"⚠️ Database fallback query failed (trying simpler query): {db_err}")
                        try:
                            # Simplified fallback - just search by name in from_user
                            search_term = member_full_name if member_full_name else member_id
                            db_messages = current_app.db_manager.execute_query(
                                "SELECT * FROM messages WHERE from_user LIKE ? OR recipient_name LIKE ? ORDER BY created_at DESC LIMIT 50",
                                (f'%{search_term}%', f'%{search_term}%'),
                                fetch_all=True
                            )
                            if db_messages and not isinstance(db_messages[0], dict):
                                db_messages = [dict(row) for row in db_messages]
                            logger.info(f"📋 Simplified fallback returned {len(db_messages) if db_messages else 0} messages")
                        except Exception as db_err2:
                            logger.error(f"❌ Simplified DB fallback also failed: {db_err2}")
                            db_messages = []
                    
                    all_messages = [session_expired_message] + db_messages
                    
                    return jsonify({
                        'success': True,
                        'member_id': member_id,
                        'message_history': all_messages,
                        'count': len(all_messages),
                        'source': 'clubos_session_expired',
                        'note': 'ClubOS authentication required'
                    })
                
                # Save response for debugging (optional)
                try:
                    import os
                    from datetime import datetime
                    debug_dir = 'data/debug_outputs'
                    os.makedirs(debug_dir, exist_ok=True)
                    timestamp = int(datetime.now().timestamp())
                    debug_file = os.path.join(debug_dir, f'followup_response_{member_id}_{timestamp}.html')
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    logger.info(f"📝 Saved ClubOS FollowUp response to {debug_file}")
                except Exception as save_error:
                    logger.debug(f"⚠️ Could not save debug file: {save_error}")
                
                # Extract message history from HTML response
                clubos_messages = parse_clubos_followup_response(html_content, member_id)

                logger.info(f"✅ Retrieved {len(clubos_messages)} messages from ClubOS FollowUp API for member {member_id}")

                # CRITICAL FIX: DO NOT merge with database when ClubOS API works
                # The database contains OLD messages with incorrect timestamps (2001) from before the timestamp fix
                # ClubOS FollowUp API now works correctly and returns properly parsed messages with accurate timestamps (2025)
                # Database should ONLY be used as fallback when ClubOS API fails completely

                if clubos_messages:
                    # ClubOS API worked! Return ONLY ClubOS messages (with correct timestamps)
                    logger.info(f"✅ Using {len(clubos_messages)} messages from ClubOS FollowUp API (database fallback DISABLED - timestamps are correct)")

                    # DEBUG: Log sample messages to verify timestamps
                    if clubos_messages:
                        logger.info(f"📊 Sample ClubOS messages (with correct timestamps):")
                        for i, msg in enumerate(clubos_messages[:5]):  # First 5 messages
                            logger.info(f"   Message {i+1}: from={msg.get('from_user')}, timestamp={msg.get('timestamp')}, content={msg.get('content', '')[:50]}")

                    return jsonify({
                        'success': True,
                        'member_id': member_id,
                        'message_history': clubos_messages,
                        'count': len(clubos_messages),
                        'source': 'clubos_followup_api',
                        'note': 'Database fallback disabled - using only ClubOS messages with correct timestamps'
                    })

                # FALLBACK: ClubOS API returned empty - try database
                logger.warning(f"⚠️ ClubOS FollowUp API returned no messages - falling back to database")

                # Get member name to search database messages
                member_name = None
                try:
                    member = current_app.db_manager.execute_query(
                        "SELECT full_name, first_name, last_name FROM members WHERE guid = ? OR prospect_id = ? LIMIT 1",
                        (member_id, member_id), fetch_one=True
                    )
                    if member:
                        if not isinstance(member, dict):
                            member = dict(member)
                        member_name = member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                        logger.info(f"✅ Found member name for database fallback: {member_name}")
                except Exception as name_err:
                    logger.warning(f"⚠️ Error getting member name for database fallback: {name_err}")

                # Query database for messages as fallback
                db_messages = []
                if member_name:
                    try:
                        db_messages = current_app.db_manager.execute_query('''
                            SELECT * FROM messages
                            WHERE LOWER(from_user) = LOWER(?)
                               OR LOWER(to_user) = LOWER(?)
                               OR LOWER(recipient_name) = LOWER(?)
                               OR LOWER(from_member_name) = LOWER(?)
                               OR LOWER(to_staff_name) = LOWER(?)
                               OR (LOWER(recipient_name) = LOWER(?) AND status = 'sent')
                               OR (LOWER(recipient_name) = LOWER(?) AND delivery_status = 'sent')
                            ORDER BY created_at DESC
                            LIMIT 100
                        ''', (member_name, member_name, member_name, member_name, member_name, member_name, member_name), fetch_all=True)

                        # Convert to dict if needed
                        if db_messages and not isinstance(db_messages[0], dict):
                            db_messages = [dict(row) for row in db_messages]

                        logger.info(f"✅ Database fallback retrieved {len(db_messages)} messages for member {member_name}")
                    except Exception as db_err:
                        logger.warning(f"⚠️ Error querying database for fallback: {db_err}")
                        db_messages = []

                return jsonify({
                    'success': True,
                    'member_id': member_id,
                    'message_history': db_messages,
                    'count': len(db_messages),
                    'source': 'database_fallback',
                    'note': 'ClubOS API returned no messages - using database as fallback'
                })
            else:
                logger.warning(f"⚠️ ClubOS FollowUp request failed with status {response.status_code}: {response.text[:100]}")

                # If 403, attempt auto-reauth and retry ONCE
                if response.status_code == 403:
                    logger.info("🔑 Detected 403 - attempting automatic re-authentication...")
                    try:
                        if messaging_client.authenticate():
                            logger.info("✅ Auto-reauth successful, retrying request...")

                            # Retry the same request with fresh session
                            response_retry = messaging_client.session.post(
                                f"{messaging_client.base_url}/action/FollowUp",
                                data=payload,
                                timeout=30
                            )

                            if response_retry.status_code == 200:
                                logger.info("✅ Retry successful after re-authentication!")
                                html_content = response_retry.text
                                clubos_messages_retry = parse_clubos_followup_response(html_content, member_id)

                                # CRITICAL FIX: DO NOT merge with database (same as above)
                                # Return ONLY ClubOS messages with correct timestamps
                                logger.info(f"✅ Retry returned {len(clubos_messages_retry)} messages from ClubOS (database fallback DISABLED)")

                                return jsonify({
                                    'success': True,
                                    'member_id': member_id,
                                    'message_history': clubos_messages_retry,
                                    'count': len(clubos_messages_retry),
                                    'source': 'clubos_followup_api_retry',
                                    'note': 'Retry after re-auth successful - using only ClubOS messages with correct timestamps'
                                })
                            else:
                                logger.warning(f"⚠️ Retry failed with status {response_retry.status_code}")
                        else:
                            logger.warning("⚠️ Auto-reauth failed")
                    except Exception as reauth_error:
                        logger.warning(f"⚠️ Auto-reauth error: {reauth_error}")

                # Create an error message
                api_error_message = {
                    'id': f"clubos_api_error_{member_id}_{int(datetime.now().timestamp())}",
                    'member_id': member_id,
                    'content': f"⚠️ ClubOS API unavailable (Status: {response.status_code}). Authentication expired. Please refresh ClubOS login to view complete message history.",
                    'timestamp': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'created_at': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'message_type': 'system',
                    'status': 'warning',
                    'from_user': 'System',
                    'to_user': 'Staff',
                    'source': 'clubos_error',
                    'channel': 'system',
                    'note': f'ClubOS API error: {response.status_code}'
                }

                # Fall through to database fallback with error message
                
        except Exception as api_error:
            logger.warning(f"⚠️ ClubOS FollowUp API error: {api_error}")
            
            # Create an exception error message
            exception_message = {
                'id': f"clubos_exception_{member_id}_{int(datetime.now().timestamp())}",
                'member_id': member_id,
                'content': f"❌ Error connecting to ClubOS: {str(api_error)[:100]}. Showing local messages only.",
                'timestamp': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                'created_at': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                'message_type': 'system',
                'status': 'error',
                'from_user': 'System',
                'to_user': 'Staff',
                'source': 'clubos_exception',
                'channel': 'system',
                'error': str(api_error)
            }
            # Fall through to database fallback with exception message
        
        # Fallback to database messages if ClubOS API fails
        logger.info(f"🔄 Using database fallback for member {member_id}")

        # Get any error message created above
        error_message = None
        if 'api_error_message' in locals():
            error_message = api_error_message
        elif 'exception_message' in locals():
            error_message = exception_message

        # CRITICAL FIX: Get member's NAME to search messages (messages have name, not GUID)
        member_name = None
        try:
            member = current_app.db_manager.execute_query(
                "SELECT full_name, first_name, last_name FROM members WHERE guid = ? OR prospect_id = ? LIMIT 1",
                (member_id, member_id), fetch_one=True
            )
            if member:
                # Convert Row object to dict
                if not isinstance(member, dict):
                    member = dict(member)
                member_name = member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                logger.info(f"✅ Found member name for {member_id}: {member_name}")
            else:
                logger.warning(f"⚠️ No member found with GUID/prospect_id: {member_id}")
        except Exception as name_err:
            logger.warning(f"⚠️ Error getting member name: {name_err}")

        # Search messages by member NAME (not GUID)
        messages = []
        try:
            if member_name:
                # ENHANCED: Search by all possible name fields to capture FULL conversation (both directions)
                # This ensures we get messages FROM member AND messages TO member (staff replies)
                messages = current_app.db_manager.execute_query('''
                    SELECT * FROM messages
                    WHERE LOWER(from_user) = LOWER(?)
                       OR LOWER(to_user) = LOWER(?)
                       OR LOWER(recipient_name) = LOWER(?)
                       OR LOWER(from_member_name) = LOWER(?)
                       OR LOWER(to_staff_name) = LOWER(?)
                       OR (LOWER(recipient_name) = LOWER(?) AND status = 'sent')
                       OR (LOWER(recipient_name) = LOWER(?) AND delivery_status = 'sent')
                    ORDER BY created_at DESC
                    LIMIT 100
                ''', (member_name, member_name, member_name, member_name, member_name, member_name, member_name), fetch_all=True)
                logger.info(f"📬 Found {len(messages) if messages else 0} messages for {member_name} (full conversation with staff replies)")

            # Fallback: search by member_id if name search found nothing
            if not messages or len(messages) == 0:
                logger.info(f"🔄 No messages found by name, trying member_id search")
                messages = current_app.db_manager.execute_query('''
                    SELECT * FROM messages
                    WHERE (owner_id = ? OR member_id = ?)
                    OR (content LIKE ? OR from_user LIKE ? OR to_user LIKE ?)
                    ORDER BY created_at DESC
                    LIMIT 100
                ''', (member_id, member_id, f'%{member_id}%', f'%{member_id}%', f'%{member_id}%'), fetch_all=True)

            if messages and not isinstance(messages[0], dict):
                messages = [dict(row) for row in messages]

            # DETAILED LOGGING: Show what we're actually returning
            if messages:
                logger.info(f"✅ Database returned {len(messages)} messages")
                logger.info(f"🔍 Message type: {type(messages[0])}")
                logger.info(f"🔍 First message keys: {list(messages[0].keys()) if isinstance(messages[0], dict) else 'Not a dict'}")
                logger.info(f"🔍 Sample message: from_user='{messages[0].get('from_user')}', content_preview='{messages[0].get('content', '')[:50]}...'")
            else:
                logger.warning(f"⚠️ No messages found in database for member_name='{member_name}' or member_id='{member_id}'")
        except Exception as e_db:
            logger.error(f"❌ Database fallback query failed: {e_db}")
            messages = []

        # Add error message if any
        all_messages = messages
        if error_message:
            all_messages = [error_message] + messages

        logger.info(f"📤 Returning API response: success=True, count={len(all_messages)}, source=database_fallback")

        return jsonify({
            'success': True,
            'member_id': member_id,
            'message_history': all_messages,
            'count': len(all_messages),
            'source': 'database_fallback' + ('_with_error' if error_message else '')
        })
    
    except Exception as e:
        logger.error(f"❌ Error getting member message history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def parse_clubos_followup_response(html_content: str, member_id: str) -> List[Dict]:
    """Parse ClubOS FollowUp HTML response to extract message history"""
    try:
        from bs4 import BeautifulSoup
        import re
        from datetime import datetime
        
        soup = BeautifulSoup(html_content, 'html.parser')
        messages = []
        
        logger.info(f"📄 ClubOS response length: {len(html_content)} characters")

        # CRITICAL FIX: Look up member's actual name for proper message attribution
        # This fixes the bug where staff replies were stored with to_user='Member' instead of actual name
        member_name = None
        try:
            from flask import current_app
            member = current_app.db_manager.execute_query(
                "SELECT full_name, first_name, last_name FROM members WHERE guid = ? OR prospect_id = ? LIMIT 1",
                (member_id, member_id), fetch_one=True
            )
            if member:
                if not isinstance(member, dict):
                    member = dict(member)
                member_name = member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                logger.info(f"✅ Resolved member name for message attribution: {member_name}")
        except Exception as e:
            logger.warning(f"⚠️ Could not resolve member name: {e}")
            member_name = None

        # Method 1: Look for followup-entry divs (preferred format)
        followup_entries = soup.find_all('div', class_='followup-entry')
        logger.info(f"🔍 Found {len(followup_entries)} followup-entry divs")
        
        for entry in followup_entries:
            try:
                # Extract date and author from followup-entry-date
                date_div = entry.find('div', class_='followup-entry-date')
                note_div = entry.find('div', class_='followup-entry-note')

                # ENHANCED: Try to extract content even if structure is imperfect
                # This ensures we capture member messages with different HTML structure
                if not date_div and not note_div:
                    logger.debug(f"⚠️ Skipping entry - completely missing both date_div and note_div")
                    continue

                # Allow entries with only one of the divs (be more lenient)
                if not date_div:
                    # Try to find date text anywhere in the entry
                    date_text = entry.get_text(strip=True)
                    logger.debug(f"⚠️ No date_div found, using entire entry text for date parsing")
                else:
                    date_text = date_div.get_text(strip=True)

                if not note_div:
                    # Try to extract content from the entry itself
                    note_text = entry.get_text(strip=True)
                    # Remove the date text to isolate the message content
                    if date_text:
                        note_text = note_text.replace(date_text, '').strip()
                    logger.debug(f"⚠️ No note_div found, using entry text minus date")
                else:
                    note_text = note_div.get_text(strip=True)

                # Skip empty entries (allow short messages like "Ok", "Yes")
                if len(note_text.strip()) < 1:
                    logger.debug(f"⚠️ Skipping empty entry")
                    continue

                logger.debug(f"📝 Processing entry - Date: {repr(date_text[:50])}, Content: {repr(note_text[:100])}")
                
                timestamp = None
                author = 'ClubOS System'

                # Parse date and author from date_text (handle multiline with flexible whitespace)
                # FIXED: Accept both forward slash AND backslash as date separators (ClubOS uses backslashes)
                date_match = re.search(r'(\d{1,2}[/\\]\d{1,2}[/\\]\d{2,4})\s*@\s*(\d{1,2}:\d{2}\s*[AP]M)', date_text, re.MULTILINE | re.DOTALL)
                if date_match:
                    date_str = date_match.group(1)
                    time_str = date_match.group(2)

                    logger.debug(f"🔍 Raw date_str from ClubOS: {repr(date_str)}, time_str: {repr(time_str)}")

                    # FIXED: Normalize backslashes to forward slashes (ClubOS returns dates like 9\26\25)
                    date_str = date_str.replace('\\', '/')
                    logger.debug(f"🔄 After backslash normalization: {repr(date_str)}")

                    # CRITICAL FIX: Use proper datetime parsing to ensure correct year handling
                    try:
                        from datetime import datetime as dt

                        # Parse the date string
                        date_parts = date_str.split('/')
                        month = int(date_parts[0])
                        day = int(date_parts[1])
                        year = int(date_parts[2])

                        # Convert 2-digit year to 4-digit year (2000-2099 range)
                        if year < 100:
                            # Assume all 2-digit years are in the 2000s (00-99 -> 2000-2099)
                            year = 2000 + year
                            logger.debug(f"📅 Converted 2-digit year {date_parts[2]} to 4-digit: {year}")

                        # Parse the time string
                        time_obj = dt.strptime(time_str.strip(), '%I:%M %p')

                        # Create a proper datetime object
                        dt_obj = dt(year, month, day, time_obj.hour, time_obj.minute)

                        # Format as ISO 8601 for consistency and proper sorting
                        timestamp = dt_obj.isoformat()

                        logger.debug(f"✅ Parsed datetime object: {dt_obj}")
                        logger.debug(f"✅ Final ISO timestamp: {timestamp}")

                    except Exception as parse_error:
                        logger.warning(f"⚠️ Datetime parsing failed: {parse_error}, falling back to string concatenation")
                        # Fallback to original string-based approach
                        if '/' in date_str:
                            date_parts = date_str.split('/')
                            if len(date_parts[2]) == 2:  # Convert YY to YYYY
                                year = int(date_parts[2])
                                date_parts[2] = f"20{year:02d}"  # Force 2000s range with zero-padding
                            date_str = '/'.join(date_parts)
                        timestamp = f"{date_str} {time_str}"

                else:
                    logger.debug(f"⚠️ Could not parse timestamp from: {repr(date_text)}")

                # Extract author (handle newlines and whitespace in HTML)
                author_match = re.search(r'by\s+(.+?)(?:\n|$)', date_text, re.MULTILINE | re.DOTALL)
                if author_match:
                    author = author_match.group(1).strip()
                    # Remove trailing periods and extra whitespace
                    author = re.sub(r'\.$', '', author).strip()
                    logger.debug(f"✅ Parsed author: {author}")
                else:
                    logger.debug(f"⚠️ No author found in: {repr(date_text)}")
                
                # Determine message type and status
                message_type = 'conversation'
                status = 'received'

                if 'icon_text.png' in str(note_div) or 'Text -' in note_text:
                    message_type = 'sms'
                elif 'icon_email.png' in str(note_div) or 'Email -' in note_text:
                    message_type = 'email'
                elif 'icon_phone.png' in str(note_div) or 'Call -' in note_text:
                    message_type = 'call'

                # Smart direction detection: Staff messages always have "by [Name]" attribution
                # Member messages typically don't have "by" in the date text
                if re.search(r'by\s+', date_text, re.IGNORECASE):
                    status = 'sent'  # Staff message TO member
                    logger.debug(f"✅ Detected as STAFF message (has 'by' attribution)")
                elif 'Message sent' in note_text or 'sent successfully' in note_text.lower():
                    status = 'sent'  # Also catch system confirmations
                    logger.debug(f"✅ Detected as STAFF message (has 'sent' indicator)")
                else:
                    status = 'received'  # Member message FROM member
                    logger.debug(f"✅ Detected as MEMBER message (no 'by' attribution)")
                
                # Clean up content
                content = note_text
                content = re.sub(r'^(Text|Email|Call)\s*-\s*', '', content)

                # CRITICAL FIX: Use actual member name instead of generic "Member"
                # This allows database queries to find staff replies by searching for the member's name
                message_data = {
                    'id': f"clubos_followup_{member_id}_{hash(content + str(timestamp)) % 1000000}",
                    'member_id': member_id,
                    'content': content[:1000],
                    'timestamp': timestamp or datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'created_at': timestamp or datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'message_type': message_type,
                    'status': status,
                    # FIXED: Staff messages (status='sent') should show staff as from_user and member as to_user
                    # Member messages (status='received') should show member as from_user and staff as to_user
                    'from_user': author if status == 'sent' else (member_name or 'Member'),
                    'to_user': (member_name or 'Member') if status == 'sent' else author,
                    'recipient_name': (member_name or 'Member') if status == 'sent' else None,
                    'from_member_name': (member_name or 'Member') if status != 'sent' else None,
                    'to_staff_name': author if status != 'sent' else None,
                    'source': 'clubos_followup',
                    'channel': 'clubos'
                }

                messages.append(message_data)
                logger.debug(f"✅ Added message: {status.upper()} - {message_type} - {author} - {content[:50]}...")

            except Exception as entry_error:
                logger.warning(f"⚠️ Error parsing followup entry: {entry_error}")
                import traceback
                logger.debug(f"Full traceback: {traceback.format_exc()}")
                continue
        
        # Method 2: If no followup entries found, try to extract from HTML tables or other structures
        if not messages:
            logger.info("📋 No followup-entry divs found, trying alternative parsing...")
            
            # Look for any divs or elements containing date patterns
            # FIXED: Accept both forward slash AND backslash as date separators
            date_pattern = re.compile(r'(\d{1,2}[/\\]\d{1,2}[/\\]\d{2,4})\s*[@at]\s*(\d{1,2}:\d{2}\s*[AP]M)', re.IGNORECASE)

            # Search in all text content for date patterns
            all_text_elements = soup.find_all(text=date_pattern)
            logger.info(f"🔍 Found {len(all_text_elements)} elements with date patterns")

            for text_element in all_text_elements[:10]:  # Limit to first 10
                try:
                    parent = text_element.parent
                    if parent:
                        parent_text = parent.get_text(strip=True)

                        # Extract date/time
                        date_match = date_pattern.search(parent_text)
                        if date_match:
                            # FIXED: Normalize backslashes to forward slashes
                            date_str = date_match.group(1).replace('\\', '/')
                            time_str = date_match.group(2)
                            timestamp = f"{date_str} {time_str}"
                            
                            # Get surrounding content
                            content = parent_text
                            if len(content) > 10:
                                message_data = {
                                    'id': f"clubos_alt_{member_id}_{hash(content) % 1000000}",
                                    'member_id': member_id,
                                    'content': content[:500],
                                    'timestamp': timestamp,
                                    'created_at': timestamp,
                                    'message_type': 'conversation',
                                    'status': 'received',
                                    'from_user': 'ClubOS System',
                                    'to_user': 'Member',
                                    'source': 'clubos_followup',
                                    'channel': 'clubos'
                                }
                                messages.append(message_data)
                                
                except Exception as alt_error:
                    logger.debug(f"⚠️ Error in alternative parsing: {alt_error}")
                    continue
        
        # Method 3: If still no messages, try to find any meaningful content
        if not messages:
            logger.info("📝 No structured data found, creating summary message...")
            
            # Create a single summary message indicating we got data but couldn't parse it
            body_content = soup.get_text(strip=True)
            if len(body_content) > 100:
                summary_content = f"ClubOS FollowUp data retrieved ({len(html_content)} characters). Raw content includes member interaction history and system logs."
                
                if "9/25/25" in body_content or "PM by" in body_content:
                    summary_content += " Contains message timestamps and activity logs."
                
                message_data = {
                    'id': f"clubos_summary_{member_id}_{int(datetime.now().timestamp())}",
                    'member_id': member_id,
                    'content': summary_content,
                    'timestamp': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'created_at': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'message_type': 'system',
                    'status': 'received',
                    'from_user': 'ClubOS System',
                    'to_user': 'Member',
                    'source': 'clubos_followup',
                    'channel': 'clubos',
                    'note': 'Raw ClubOS data - parsing in progress'
                }
                messages.append(message_data)
        
        # Sort messages by timestamp (newest first)
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Log summary statistics with detailed breakdown
        sent_count = sum(1 for m in messages if m.get('status') == 'sent')
        received_count = sum(1 for m in messages if m.get('status') == 'received')
        sms_count = sum(1 for m in messages if m.get('message_type') == 'sms')
        email_count = sum(1 for m in messages if m.get('message_type') == 'email')
        conversation_count = sum(1 for m in messages if m.get('message_type') == 'conversation')

        logger.info(f"✅ Successfully parsed {len(messages)} messages from ClubOS FollowUp response for member {member_id}")
        logger.info(f"   📊 Direction: {sent_count} staff→member (sent), {received_count} member→staff (received)")
        logger.info(f"   📊 Types: {conversation_count} conversation, {sms_count} SMS, {email_count} email")

        # CRITICAL FIX: Sort messages by timestamp in descending order (newest first)
        try:
            from datetime import datetime as dt

            def parse_timestamp_for_sorting(msg):
                """Parse timestamp for sorting - handles both ISO format and legacy formats"""
                timestamp = msg.get('timestamp') or msg.get('created_at')
                if not timestamp:
                    return dt.min  # Put messages with no timestamp at the end

                try:
                    # Try ISO 8601 format first (from our fixed parser)
                    return dt.fromisoformat(timestamp)
                except:
                    try:
                        # Try legacy format: "9/4/2025 6:00 AM"
                        return dt.strptime(timestamp, '%m/%d/%Y %I:%M %p')
                    except:
                        try:
                            # Try another common format
                            return dt.strptime(timestamp, '%m/%d/%Y %H:%M:%S')
                        except:
                            logger.debug(f"⚠️ Could not parse timestamp for sorting: {timestamp}")
                            return dt.min

            # Sort by timestamp descending (newest first)
            messages.sort(key=parse_timestamp_for_sorting, reverse=True)
            logger.info(f"✅ Sorted {len(messages)} messages by timestamp (newest first)")

        except Exception as sort_error:
            logger.warning(f"⚠️ Failed to sort messages by timestamp: {sort_error}")
            # Continue without sorting rather than failing

        return messages
        
    except Exception as e:
        logger.error(f"❌ Error parsing ClubOS FollowUp response: {e}")
        # Still return a basic message so the API doesn't fail completely
        return [{
            'id': f"clubos_error_{member_id}_{int(datetime.now().timestamp())}",
            'member_id': member_id,
            'content': f"ClubOS FollowUp API returned data but parsing failed. Response size: {len(html_content)} characters.",
            'timestamp': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
            'created_at': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
            'message_type': 'system',
            'status': 'error',
            'from_user': 'System',
            'to_user': 'User',
            'source': 'clubos_followup',
            'channel': 'clubos',
            'error': str(e)
        }]

def extract_message_from_element(element, member_id: str) -> Dict:
    """Extract message data from a single HTML element"""
    try:
        # This function needs to be customized based on ClubOS HTML structure
        # For now, return a basic structure
        
        text_content = element.get_text(strip=True)
        if len(text_content) < 10:  # Skip empty or very short elements
            return None
        
        # Try to extract timestamp
        timestamp_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}', text_content)
        timestamp = timestamp_match.group(0) if timestamp_match else datetime.now().isoformat()
        
        # Try to extract message content
        # Look for common message patterns
        content = text_content[:200]  # Limit content length
        
        return {
            'id': f"clubos_{member_id}_{hash(text_content) % 10000}",
            'member_id': member_id,
            'content': content,
            'timestamp': timestamp,
            'created_at': timestamp,
            'source': 'clubos_followup',
            'message_type': 'conversation',
            'status': 'received'
        }
        
    except Exception as e:
        logger.debug(f"⚠️ Error extracting message data: {e}")
        return None
