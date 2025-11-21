#!/usr/bin/env python3
"""
Messaging Routes
ClubOS messaging integration, conversation management, and campaign functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from functools import wraps
from typing import Dict, List, Any
import logging
import time
import json
import re
import hashlib
import traceback
from datetime import datetime
from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
from .auth import require_auth

logger = logging.getLogger(__name__)
messaging_bp = Blueprint('messaging', __name__)

def get_clubos_credentials(owner_id: str) -> Dict[str, str]:
    """Get ClubOS credentials for a specific owner"""
    try:
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        base_url = secrets_manager.get_secret('clubos-base-url') or 'https://anytime.club-os.com'
        
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
@require_auth
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
		logger.info(f"📨 Campaign send request received: {data}")
		
		if not data:
			logger.error("❌ No data provided in campaign request")
			return jsonify({'success': False, 'error': 'No data provided'}), 400
		
		# Extract campaign parameters
		message_text = data.get('message', '')
		message_type = data.get('type', 'sms')  # 'sms' or 'email'
		subject = data.get('subject', '')
		member_categories = data.get('categories', [])  # Changed default from ['green'] to []
		max_recipients = data.get('max_recipients', 100)
		campaign_notes = data.get('notes', '')
		
		logger.info(f"📋 Campaign params - Message: '{message_text[:50]}...', Type: {message_type}, Categories: {member_categories}, Max: {max_recipients}")
		logger.info(f"📝 Campaign notes: '{campaign_notes[:100]}...'")  # Log notes for debugging
		
		if not message_text:
			logger.error("❌ Message text is required but not provided")
			return jsonify({'success': False, 'error': 'Message text is required'}), 400
		
		if not member_categories:
			logger.error("❌ No member categories selected")
			return jsonify({'success': False, 'error': 'At least one member category must be selected'}), 400
		
		# Get members from selected categories with validation
		member_ids = []
		validated_members = []
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		for category in member_categories:
			logger.info(f"🔍 Processing category: '{category}'")
			
			# Check campaign progress to see where we left off
			cursor.execute('''
				SELECT last_processed_member_id, last_processed_index, total_members_in_category
				FROM campaign_progress 
				WHERE category = ?
				ORDER BY last_campaign_date DESC 
				LIMIT 1
			''', (category,))
			
			progress_row = cursor.fetchone()
			start_after_member_id = None
			start_index = 0
			
			if progress_row:
				start_after_member_id = progress_row['last_processed_member_id']
				start_index = progress_row['last_processed_index'] + 1  # Start after last processed
				logger.info(f"📍 Resuming {category} from index {start_index} (after member {start_after_member_id})")
			else:
				logger.info(f"📍 Starting {category} from beginning (no previous progress)")
			
			if category == 'all_members':
				# Special case: get all members regardless of status
				logger.info("📊 Selecting all members from all categories")
				if start_after_member_id:
					cursor.execute('''
						SELECT id, prospect_id, email, mobile_phone, full_name, status_message
						FROM members 
						WHERE id > (SELECT id FROM members WHERE prospect_id = ? OR id = ? LIMIT 1)
						ORDER BY id
						LIMIT ?
					''', (start_after_member_id, start_after_member_id, max_recipients))
				else:
					cursor.execute('''
						SELECT id, prospect_id, email, mobile_phone, full_name, status_message
						FROM members 
						ORDER BY id
						LIMIT ?
					''', (max_recipients,))
			elif category == 'prospects':
				# Special case: get prospects from prospects table (different column names)
				logger.info("📊 Selecting prospects")
				if start_after_member_id:
					cursor.execute('''
						SELECT prospect_id as id, prospect_id, email, phone as mobile_phone, full_name, status as status_message
						FROM prospects 
						WHERE prospect_id > ?
						ORDER BY prospect_id
						LIMIT ?
					''', (start_after_member_id, max_recipients))
				else:
					cursor.execute('''
						SELECT prospect_id as id, prospect_id, email, phone as mobile_phone, full_name, status as status_message
						FROM prospects 
						ORDER BY prospect_id
						LIMIT ?
					''', (max_recipients,))
			else:
				# Regular category: filter by status_message (members table only)
				logger.info(f"📊 Selecting members with status_message: '{category}'")
				if start_after_member_id:
					cursor.execute('''
						SELECT id, prospect_id, email, mobile_phone, full_name, status_message
						FROM members 
						WHERE status_message = ? AND id > (SELECT id FROM members WHERE prospect_id = ? OR id = ? LIMIT 1)
						ORDER BY id
						LIMIT ?
					''', (category, start_after_member_id, start_after_member_id, max_recipients))
				else:
					cursor.execute('''
						SELECT id, prospect_id, email, mobile_phone, full_name, status_message
						FROM members 
						WHERE status_message = ?
						ORDER BY id
						LIMIT ?
					''', (category, max_recipients))
			
			category_members = cursor.fetchall()
			logger.info(f"📋 Found {len(category_members)} members for category '{category}'")
			
			# Validate each member before adding
			for member in category_members:
				if len(member_ids) >= max_recipients:
					break
					
				# Convert row to dict for validation
				member_dict = {
					'member_id': member['prospect_id'] or str(member['id']),
					'prospect_id': member['prospect_id'],
					'email': member['email'],
					'mobile_phone': member['mobile_phone'],
					'full_name': member['full_name'],
					'status_message': member['status_message']
				}
				
				# Basic validation for SMS campaigns
				if message_type == 'sms':
					phone = member_dict.get('mobile_phone', '').strip()
					if not phone:
						logger.warning(f"⚠️ Skipping member {member_dict['full_name']} - no phone number")
						continue
				
				# Basic validation for email campaigns  
				if message_type == 'email':
					email = member_dict.get('email', '').strip()
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
		
		# Send the campaign using the simple client with full member data
		results = client.send_bulk_campaign(
			member_data_list=validated_members[:max_recipients],
			message=message_text,
			message_type=message_type
		)
		
		results['method'] = 'simple_client'
		
		# Log campaign results
		logger.info(f"📢 Campaign completed: {results['successful']}/{results['total']} sent successfully")
		
		# Ensure campaigns table exists with progress tracking
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS campaigns (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT,
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
		
		# Ensure campaign_progress table exists for tracking where we left off
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS campaign_progress (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				category TEXT,
				last_processed_member_id TEXT,
				last_processed_index INTEGER,
				last_campaign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				total_members_in_category INTEGER,
				notes TEXT
			)
		''')
		
		# Store campaign in database
		campaign_cursor = cursor.execute('''
			INSERT INTO campaigns 
			(campaign_name, message_text, message_type, subject, categories, total_recipients, successful_sends, failed_sends, errors, notes)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		''', (
			data.get('campaignName', 'Untitled Campaign'),
			message_text,
			message_type,
			subject,
			','.join(member_categories),
			results['total'],
			results['successful'],
			results['failed'],
			'\n'.join(results['errors']),
			campaign_notes
		))
		
		campaign_id = campaign_cursor.lastrowid
		
		# Store individual messages sent in this campaign
		if 'sent_messages' in results:
			for msg_data in results['sent_messages']:
				cursor.execute('''
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
				
				# Update or insert progress tracking
				cursor.execute('''
					INSERT OR REPLACE INTO campaign_progress 
					(category, last_processed_member_id, last_processed_index, last_campaign_date, total_members_in_category, notes)
					VALUES (?, ?, ?, ?, ?, ?)
				''', (
					category,
					last_member_id,
					last_index,
					datetime.now().isoformat(),
					len(validated_members),
					f"Campaign: {data.get('campaignName', 'Untitled')} - {results['successful']}/{results['total']} sent"
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

@messaging_bp.route('/api/campaigns/progress', methods=['GET'])
def get_campaign_progress():
	"""Get campaign progress tracking for all categories"""
	try:
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		# Ensure campaign_progress table exists
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS campaign_progress (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				category TEXT,
				last_processed_member_id TEXT,
				last_processed_index INTEGER,
				last_campaign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				total_members_in_category INTEGER,
				notes TEXT
			)
		''')
		
		cursor.execute('''
			SELECT category, last_processed_member_id, last_processed_index, 
			       last_campaign_date, total_members_in_category, notes
			FROM campaign_progress 
			ORDER BY last_campaign_date DESC
		''')
		
		progress = [dict(row) for row in cursor.fetchall()]
		conn.close()
		
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
		
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		if category == 'all':
			cursor.execute('DELETE FROM campaign_progress')
			logger.info("🔄 Reset campaign progress for all categories")
		else:
			cursor.execute('DELETE FROM campaign_progress WHERE category = ?', (category,))
			logger.info(f"🔄 Reset campaign progress for category: {category}")
		
		conn.commit()
		conn.close()
		
		return jsonify({'success': True, 'message': f'Campaign progress reset for {category}'})
		
	except Exception as e:
		logger.error(f"❌ Error resetting campaign progress: {e}")
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
				name TEXT,
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
	"""Get member categories for campaign targeting based on actual ClubHub statusMessage values"""
	try:
		conn = current_app.db_manager.get_connection()
		cursor = conn.cursor()
		
		# Debug: Check what database we're connected to
		cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
		table_exists = cursor.fetchone()
		logger.info(f"🔍 Database table check: members table exists = {table_exists is not None}")
		
		# Get actual status_message counts from ClubHub data
		cursor.execute('''
			SELECT 
				status_message,
				COUNT(*) as count
			FROM members 
			WHERE status_message IS NOT NULL AND status_message != ''
			GROUP BY status_message
			ORDER BY count DESC
		''')
		
		raw_results = cursor.fetchall()
		logger.info(f"🔍 Raw database query results: {len(raw_results)} rows")
		for i, row in enumerate(raw_results[:5]):  # Log first 5 results
			logger.info(f"  Row {i+1}: status_message='{row[0]}', count={row[1]}")
		
		categories = []
		for row in raw_results:
			status_msg = row[0]  # Use index instead of named access for compatibility
			count = row[1]
			categories.append({
				'name': status_msg,
				'count': count,
				'label': status_msg,  # Use the actual ClubHub status message as label
				'value': status_msg   # For consistent API response
			})
		
		conn.close()
		
		logger.info(f"✅ Retrieved {len(categories)} real ClubHub status categories")
		return jsonify({'success': True, 'categories': categories})
		
	except Exception as e:
		logger.error(f"❌ Error getting member categories: {e}")
		import traceback
		logger.error(f"Full traceback: {traceback.format_exc()}")
		return jsonify({'success': False, 'error': str(e)}), 500

@messaging_bp.route('/api/messages/send', methods=['POST'])
def send_message_route():
    """Route to send a message to a member."""
    if request.method == 'POST':
        data = request.get_json()
        member_id = data.get('member_id')
        message = data.get('message')

        if not member_id or not message:
            return jsonify({'status': 'error', 'message': 'Member ID and message are required.'}), 400

        try:
            # Initialize the messaging client
            messaging_client = ClubOSMessagingClient()
            
            # Send the message
            success = messaging_client.send_message(member_id, message)
            
            if success:
                return jsonify({'status': 'success', 'message': 'Message sent successfully.'})
            else:
                return jsonify({'status': 'error', 'message': 'Failed to send message.'}), 500
        except Exception as e:
            current_app.logger.error(f"Error sending message: {e}")
            return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500

    return jsonify({'status': 'error', 'message': 'Invalid request method.'}), 405


@messaging_bp.route('/api/messages/send_bulk', methods=['POST'])
@require_auth
def send_bulk_message_route():
	"""Route to send a message to a member."""
	if request.method == 'POST':
		data = request.get_json()
		member_ids = data.get('member_ids')
		message = data.get('message')

		if not member_ids or not message:
			return jsonify({'status': 'error', 'message': 'Member IDs and message are required.'}), 400

		try:
			from src.services.clubos_messaging_client import ClubOSMessagingClient
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
@require_auth
def get_message_templates():
	try:
		from src.services.clubos_messaging_client import ClubOSMessagingClient
		messaging_client = ClubOSMessagingClient()
		templates = messaging_client.get_message_templates()
		if templates is not None:
			return jsonify({'status': 'success', 'templates': templates})
		else:
			return jsonify({'status': 'error', 'message': 'Failed to retrieve message templates.'}), 500
	except Exception as e:
		current_app.logger.error(f"Error getting message templates: {e}")
		return jsonify({'status': 'error', 'message': 'An unexpected error occurred.'}), 500
