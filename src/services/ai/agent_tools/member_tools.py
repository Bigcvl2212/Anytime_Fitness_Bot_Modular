"""
Member Management Tools

Tools for member profile access, notes, and messaging
"""

import logging
from typing import Dict, Any, List
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from services.database_manager import DatabaseManager
from services.clubos_messaging_client_simple import ClubOSMessagingClient
from services.authentication.secure_secrets_manager import SecureSecretsManager

logger = logging.getLogger(__name__)

def get_member_profile(member_id: str) -> Dict[str, Any]:
    """Get complete member profile including billing, membership, status
    
    Args:
        member_id: Member/prospect ID
    
    Returns:
        {
            "success": True,
            "profile": {...}
        }
    """
    try:
        # Validate input - member_id must be a string
        if not isinstance(member_id, str):
            member_id = str(member_id)
        
        db = DatabaseManager()
        
        # Try members table first
        query = "SELECT * FROM members WHERE prospect_id = ? OR guid = ?"
        result = db.execute_query(query, (member_id, member_id), fetch_all=True)
        
        if result and len(result) > 0:
            # Convert sqlite3.Row to dict
            profile_row = dict(result[0]) if hasattr(result[0], 'keys') else result[0]
            
            # Get collection attempts (check if table exists)
            attempt_count = 0
            try:
                attempts_query = """
                    SELECT COUNT(*) as attempt_count FROM collection_attempts
                    WHERE member_id = ?
                """
                attempts_result = db.execute_query(attempts_query, (member_id,), fetch_all=True)
                if attempts_result and len(attempts_result) > 0:
                    attempts_dict = dict(attempts_result[0]) if hasattr(attempts_result[0], 'keys') else attempts_result[0]
                    attempt_count = attempts_dict.get('attempt_count', 0)
            except Exception as e:
                logger.warning(f"⚠️ Could not get collection attempts (table may not exist): {e}")
            
            # Get access status (check if table exists)
            access_status = {}
            try:
                access_query = """
                    SELECT action, reason, timestamp FROM access_control_log
                    WHERE member_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """
                access_result = db.execute_query(access_query, (member_id,), fetch_all=True)
                if access_result and len(access_result) > 0:
                    access_status = dict(access_result[0]) if hasattr(access_result[0], 'keys') else access_result[0]
            except Exception as e:
                logger.warning(f"⚠️ Could not get access status (table may not exist): {e}")
            
            # Format profile
            formatted_profile = {
                "member_id": member_id,
                "name": profile_row.get('display_name') or profile_row.get('full_name'),
                "email": profile_row.get('email'),
                "phone": profile_row.get('phone_number') or profile_row.get('primary_phone'),
                "status": profile_row.get('status_message'),
                "membership_type": profile_row.get('membership_type'),
                "amount_past_due": float(profile_row.get('amount_past_due', 0) or 0),
                "base_amount_past_due": float(profile_row.get('base_amount_past_due', 0) or 0),
                "agreement_status": profile_row.get('agreement_status'),
                "join_date": profile_row.get('join_date') or profile_row.get('created_at'),
                "collection_attempts": attempt_count,
                "door_access": {
                    "status": access_status.get('action', 'unlocked'),
                    "reason": access_status.get('reason', ''),
                    "last_changed": access_status.get('timestamp', '')
                }
            }
            
            logger.info(f"✅ Retrieved profile for member {member_id}")
            
            return {
                "success": True,
                "profile": formatted_profile
            }
        else:
            # Try prospects table
            query = "SELECT * FROM prospects WHERE prospect_id = ? OR guid = ?"
            result = db.execute_query(query, (member_id, member_id))
            
            if result and len(result) > 0:
                # Convert sqlite3.Row to dict
                profile_row = dict(result[0]) if hasattr(result[0], 'keys') else result[0]
                
                formatted_profile = {
                    "member_id": member_id,
                    "name": profile_row.get('display_name') or profile_row.get('full_name'),
                    "email": profile_row.get('email'),
                    "phone": profile_row.get('phone_number') or profile_row.get('primary_phone'),
                    "status": profile_row.get('status_message'),
                    "type": "prospect",
                    "created_at": profile_row.get('created_at')
                }
                
                logger.info(f"✅ Retrieved prospect profile for {member_id}")
                
                return {
                    "success": True,
                    "profile": formatted_profile
                }
            else:
                return {
                    "success": False,
                    "error": "Member not found",
                    "member_id": member_id
                }
        
    except Exception as e:
        logger.error(f"❌ Error getting member profile {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "member_id": member_id
        }

def add_member_note(
    member_id: str,
    note_text: str,
    category: str = "general",
    priority: str = "normal"
) -> Dict[str, Any]:
    """Add a note to member's account
    
    Args:
        member_id: Member/prospect ID
        note_text: Note content
        category: Note category (billing, service, complaint, etc.)
        priority: Note priority (low, normal, high, urgent)
    
    Returns:
        {
            "success": True,
            "note_id": "..."
        }
    """
    try:
        db = DatabaseManager()
        
        # Create member_notes table if doesn't exist
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS member_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                note_text TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'ai_agent'
            )
        """)
        
        # Insert note
        note_id = db.execute_query("""
            INSERT INTO member_notes (member_id, note_text, category, priority)
            VALUES (?, ?, ?, ?)
        """, (member_id, note_text, category, priority))
        
        logger.info(f"✅ Added {priority} {category} note for member {member_id}")
        
        return {
            "success": True,
            "note_id": str(note_id),
            "member_id": member_id,
            "category": category,
            "priority": priority
        }
        
    except Exception as e:
        logger.error(f"❌ Error adding note for member {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "member_id": member_id
        }

def get_member_messages(member_id: str, limit: int = 10) -> Dict[str, Any]:
    """Get recent messages for a member
    
    Args:
        member_id: Member/prospect ID
        limit: Maximum number of messages to retrieve
    
    Returns:
        {
            "success": True,
            "messages": [...],
            "count": 5
        }
    """
    try:
        db = DatabaseManager()
        
        # Get messages from messages table
        query = """
            SELECT * FROM messages
            WHERE member_id = ? OR prospect_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        
        messages = db.execute_query(query, (member_id, member_id, limit))
        
        logger.info(f"✅ Retrieved {len(messages)} messages for member {member_id}")
        
        return {
            "success": True,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting messages for member {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "messages": [],
            "count": 0
        }

def send_message_to_member(
    member_id: str,
    message_text: str,
    channel: str = "sms",
    subject: str = None
) -> Dict[str, Any]:
    """Send a message to a member via ClubOS
    
    Args:
        member_id: Member/prospect ID
        message_text: Message content
        channel: 'sms' or 'email'
        subject: Email subject (required if channel='email')
    
    Returns:
        {
            "success": True,
            "message_id": "...",
            "sent_at": "..."
        }
    """
    try:
        # Get ClubOS credentials
        secrets_manager = SecureSecretsManager()
        clubos_user = secrets_manager.get_secret("clubos-email")
        clubos_pass = secrets_manager.get_secret("clubos-password")
        
        if not clubos_user or not clubos_pass:
            return {
                "success": False,
                "error": "ClubOS credentials not found"
            }
        
        # Initialize messaging client
        client = ClubOSMessagingClient()
        
        # Authenticate
        auth_success = client.authenticate(clubos_user, clubos_pass)
        if not auth_success:
            return {
                "success": False,
                "error": "ClubOS authentication failed"
            }
        
        # Send message
        success = client.send_message(
            member_id=str(member_id),
            message_text=message_text,
            channel=channel
        )
        
        if success:
            from datetime import datetime
            
            logger.info(f"✅ Sent {channel} message to member {member_id}")
            
            return {
                "success": True,
                "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "sent_at": datetime.now().isoformat(),
                "member_id": member_id,
                "channel": channel
            }
        else:
            return {
                "success": False,
                "error": "Failed to send message"
            }
        
    except Exception as e:
        logger.error(f"❌ Error sending message to member {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "member_id": member_id
        }
