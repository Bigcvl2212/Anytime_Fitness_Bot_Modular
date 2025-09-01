#!/usr/bin/env python3
"""
Messaging Routes
ClubOS messaging integration, conversation management, and campaign functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app
import logging
from datetime import datetime
from typing import Dict, List, Any
import time # Added for retry logic
import json # Added for json parsing
import re # Added for regex
import hashlib # Added for conversation ID generation

# Import here to avoid circular imports
from ..services.clubos_messaging_client import ClubOSMessagingClient

logger = logging.getLogger(__name__)

messaging_bp = Blueprint('messaging', __name__)

def get_clubos_credentials(owner_id: str) -> Dict[str, str]:
    """Get ClubOS credentials for a specific owner"""
    try:
        from ..config.secrets_local import get_secret
        
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        base_url = get_secret('clubos-base-url', 'https://anytime.club-os.com')
        
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
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Drop and recreate messages table with enhanced schema for ClubOS
        cursor.execute('DROP TABLE IF EXISTS messages')
        cursor.execute('''
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                message_type TEXT,
                content TEXT,
                timestamp TEXT,
                from_user TEXT,
                to_user TEXT,
                status TEXT,
                owner_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                -- Enhanced metadata fields for ClubOS
                delivery_status TEXT DEFAULT 'received',
                campaign_id TEXT,
                channel TEXT DEFAULT 'clubos',
                member_id TEXT,
                message_actions TEXT, -- JSON for confirmations, emojis, opt-in/out
                is_confirmation BOOLEAN DEFAULT FALSE,
                is_opt_in BOOLEAN DEFAULT FALSE,
                is_opt_out BOOLEAN DEFAULT FALSE,
                has_emoji BOOLEAN DEFAULT FALSE,
                emoji_reactions TEXT, -- JSON array of emojis
                conversation_id TEXT, -- For grouping messages by conversation
                thread_id TEXT -- For message threading
            )
        ''')
        
        # Insert ClubOS messages with enhanced parsing
        stored_count = 0
        for message in messages:
            try:
                # Parse message content for actions and metadata
                content = message.get('content', '')
                message_actions = parse_message_actions(content)
                member_id = extract_member_id_from_content(content)
                conversation_id = generate_conversation_id(member_id, owner_id)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO messages 
                    (id, message_type, content, timestamp, from_user, to_user, status, owner_id,
                     delivery_status, campaign_id, channel, member_id, message_actions, 
                     is_confirmation, is_opt_in, is_opt_out, has_emoji, emoji_reactions,
                     conversation_id, thread_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message.get('id'),
                    message.get('message_type', message.get('type')),
                    content,
                    message.get('timestamp'),
                    message.get('from_user', message.get('from')),
                    message.get('to_user', message.get('to')),
                    message.get('status'),
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
                    message.get('thread_id')
                ))
                stored_count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error inserting ClubOS message {message.get('id')}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Stored {stored_count} ClubOS messages in database with enhanced metadata")
        return stored_count
        
    except Exception as e:
        logger.error(f"❌ Error storing ClubOS messages in database: {e}")
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

@messaging_bp.route('/messaging')
def messaging_page():
	"""Enhanced messaging center page with campaign interface."""
	try:
		return render_template('messaging.html')
	except Exception as e:
		logger.error(f"❌ Error loading messaging page: {e}")
		return render_template('error.html', error=str(e))

@messaging_bp.route('/api/messages/sync', methods=['POST'])
def sync_clubos_messages():
    """Sync messages from ClubOS to local database"""
    try:
        logger.info("🔄 Starting ClubOS message sync...")
        
        # Get owner_id from request
        if request.is_json:
            owner_id = request.json.get('owner_id')
        else:
            owner_id = request.form.get('owner_id')
        
        if not owner_id:
            return jsonify({'error': 'owner_id is required'}), 400
        
        # Get credentials for the owner
        credentials = get_clubos_credentials(owner_id)
        if not credentials:
            return jsonify({'error': 'ClubOS credentials not found'}), 400
        
        logger.info(f"✅ Got credentials for {credentials['username']}...")
        
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
                    
                    return jsonify({
                        'success': True,
                        'message': f'Synced {stored_count} messages from ClubOS',
                        'total_messages': len(messages),
                        'stored_count': stored_count
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

@messaging_bp.route('/api/messages/test-auth', methods=['POST'])
def test_clubos_auth():
	"""Simple test for ClubOS authentication"""
	try:
		logger.info("🧪 Testing ClubOS authentication...")
		
		# Import here to avoid circular imports
		try:
			from ..services.clubos_messaging_client import ClubOSMessagingClient
			logger.info("✅ Successfully imported ClubOSMessagingClient")
		except Exception as e:
			logger.error(f"❌ Failed to import ClubOSMessagingClient: {e}")
			return jsonify({'success': False, 'error': f'Import error: {str(e)}'}), 500
		
		try:
			from ..config.secrets_local import get_secret
			logger.info("✅ Successfully imported get_secret")
		except Exception as e:
			logger.error(f"❌ Failed to import get_secret: {e}")
			return jsonify({'success': False, 'error': f'Secrets import error: {str(e)}'}), 500
		
		# Get credentials
		try:
			username = get_secret('clubos-username')
			password = get_secret('clubos-password')
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

@messaging_bp.route('/api/messages', methods=['GET'])
def get_messages():
	"""Get messages from database or cache"""
	try:
		owner_id = request.args.get('owner_id', '187032782')
		limit = request.args.get('limit')  # Make limit optional
		
		# First try to get from cache if available
		if hasattr(current_app, 'data_cache') and current_app.data_cache.get('messages'):
			cached_messages = current_app.data_cache['messages']
			logger.info(f"✅ Retrieved {len(cached_messages)} messages from cache")
			
			if limit:
				limit = int(limit)
				return jsonify({'success': True, 'messages': cached_messages[:limit], 'source': 'cache'})
			else:
				return jsonify({'success': True, 'messages': cached_messages, 'source': 'cache'})

		# Fallback to database
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		if limit:
			# If limit is specified, use it
			limit = int(limit)
			cursor.execute('''
				SELECT * FROM messages 
				WHERE owner_id = ? 
				ORDER BY timestamp DESC, created_at DESC 
				LIMIT ?
			''', (owner_id, limit))
		else:
			# If no limit, get ALL messages
			cursor.execute('''
				SELECT * FROM messages 
				WHERE owner_id = ? 
				ORDER BY timestamp DESC, created_at DESC
			''', (owner_id,))
		
		messages = [dict(row) for row in cursor.fetchall()]
		conn.close()
		
		logger.info(f"✅ Retrieved {len(messages)} messages from database")
		return jsonify({'success': True, 'messages': messages, 'source': 'database'})
		
	except Exception as e:
		logger.error(f"❌ Error getting messages: {e}")
		return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/send', methods=['POST'])
def send_campaign():
	"""Send bulk messaging campaign"""
	try:
		data = request.json
		if not data:
			return jsonify({'success': False, 'error': 'No data provided'}), 400
		
		# Extract campaign parameters
		message_text = data.get('message', '')
		message_type = data.get('type', 'sms')  # 'sms' or 'email'
		subject = data.get('subject', '')
		member_categories = data.get('categories', ['green'])  # ['green', 'past_due', etc.]
		max_recipients = data.get('max_recipients', 100)
		
		if not message_text:
			return jsonify({'success': False, 'error': 'Message text is required'}), 400
		
		# Get members from selected categories
		member_ids = []
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		for category in member_categories:
			cursor.execute('''
				SELECT id, prospect_id, email, mobile_phone, full_name
				FROM members 
				WHERE status = ? OR status LIKE ?
				LIMIT ?
			''', (category, f'%{category}%', max_recipients))
			
			category_members = cursor.fetchall()
			for member in category_members:
				if len(member_ids) < max_recipients:
					# Use prospect_id if available, otherwise use id
					member_id = member['prospect_id'] or str(member['id'])
					member_ids.append(member_id)
		
		if not member_ids:
			return jsonify({'success': False, 'error': 'No members found in selected categories'}), 400
		
		# Initialize ClubOS messaging client
		from ..services.clubos_messaging_client import ClubOSMessagingClient
		from ..config.secrets_local import get_secret
		
		username = get_secret('clubos-username')
		password = get_secret('clubos-password')
		
		if not username or not password:
			return jsonify({'success': False, 'error': 'ClubOS credentials not configured'}), 400
		
		client = ClubOSMessagingClient(username, password)
		
		# Send bulk campaign
		results = client.send_bulk_campaign(
			member_ids=member_ids[:max_recipients],
			message=message_text,
			message_type=message_type,
			subject=subject
		)
		
		# Log campaign results
		logger.info(f"📢 Campaign completed: {results['successful']}/{results['total']} sent successfully")
		
		# Ensure campaigns table exists
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS campaigns (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				message_text TEXT,
				message_type TEXT,
				subject TEXT,
				categories TEXT,
				total_recipients INTEGER,
				successful_sends INTEGER,
				failed_sends INTEGER,
				errors TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		''')
		
		# Store campaign in database
		cursor.execute('''
			INSERT INTO campaigns 
			(message_text, message_type, subject, categories, total_recipients, successful_sends, failed_sends, errors)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		''', (
			message_text,
			message_type,
			subject,
			','.join(member_categories),
			results['total'],
			results['successful'],
			results['failed'],
			'\n'.join(results['errors'])
		))
		
		conn.commit()
		conn.close()
		
		return jsonify({
			'success': True,
			'campaign_results': results,
			'message': f"Campaign sent to {results['successful']} out of {results['total']} recipients"
		})
		
	except Exception as e:
		logger.error(f"❌ Error sending campaign: {e}")
		return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/campaigns/history', methods=['GET'])
def get_campaign_history():
	"""Get campaign history"""
	try:
		limit = int(request.args.get('limit', 20))
		
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		# Ensure campaigns table exists
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS campaigns (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				message_text TEXT,
				message_type TEXT,
				subject TEXT,
				categories TEXT,
				total_recipients INTEGER,
				successful_sends INTEGER,
				failed_sends INTEGER,
				errors TEXT,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			)
		''')
		
		cursor.execute('''
			SELECT * FROM campaigns 
			ORDER BY created_at DESC 
			LIMIT ?
		''', (limit,))
		
		campaigns = [dict(row) for row in cursor.fetchall()]
		conn.close()
		
		return jsonify({'success': True, 'campaigns': campaigns})
		
	except Exception as e:
		logger.error(f"❌ Error getting campaign history: {e}")
		return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/messages/member/<member_name>', methods=['GET'])
def get_member_messages(member_name):
    """Get all messages for a specific member"""
    try:
        owner_id = request.args.get('owner_id', '187032782')
        
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Search for messages containing the member name
        cursor.execute('''
            SELECT * FROM messages 
            WHERE owner_id = ? 
            AND (content LIKE ? OR from_user LIKE ?)
            ORDER BY timestamp DESC, created_at DESC
        ''', (owner_id, f'%{member_name}%', f'%{member_name}%'))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"✅ Retrieved {len(messages)} messages for member: {member_name}")
        return jsonify({'success': True, 'messages': messages, 'member_name': member_name})
        
    except Exception as e:
        logger.error(f"❌ Error getting member messages: {e}")
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
        cursor = conn.cursor()
        
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
        
        sql += ' ORDER BY timestamp DESC, created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(sql, params)
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"✅ Search returned {len(messages)} ClubOS messages for query: {query}")
        return jsonify({'success': True, 'messages': messages, 'query': query})
        
    except Exception as e:
        logger.error(f"❌ Error searching ClubOS messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/members/categories', methods=['GET'])
def get_member_categories():
	"""Get member categories for campaign targeting"""
	try:
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		# Get category counts
		cursor.execute('''
			SELECT 
				status,
				COUNT(*) as count
			FROM members 
			WHERE status IS NOT NULL
			GROUP BY status
			ORDER BY count DESC
		''')
		
		categories = []
		for row in cursor.fetchall():
			categories.append({
				'name': row['status'],
				'count': row['count'],
				'label': row['status'].title().replace('_', ' ')
			})
		
		conn.close()
		
		return jsonify({'success': True, 'categories': categories})
		
	except Exception as e:
		logger.error(f"❌ Error getting member categories: {e}")
		return jsonify({'success': False, 'error': str(e)}), 500
