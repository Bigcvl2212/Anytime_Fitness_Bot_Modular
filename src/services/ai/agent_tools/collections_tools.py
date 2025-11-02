"""
Collections Management Tools

Tools for managing past due collections, payment reminders, and escalation
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from services.database_manager import DatabaseManager
from services.clubos_messaging_client_simple import ClubOSMessagingClient
from services.authentication.secure_secrets_manager import SecureSecretsManager

logger = logging.getLogger(__name__)

def get_past_due_members(min_amount: float = 0.01, days_past_due: int = None) -> Dict[str, Any]:
    """Get list of members with past due balances
    
    Args:
        min_amount: Minimum past due amount (default $0.01)
        days_past_due: Filter by days past due (optional)
    
    Returns:
        {
            "success": True,
            "members": [...],
            "count": 23,
            "total_amount": 1234.56
        }
    """
    try:
        db = DatabaseManager()
        
        # Get past due members
        past_due = db.get_past_due_members(min_amount=min_amount)
        
        # Convert ALL rows to dicts FIRST before processing
        past_due_dicts = [dict(member) if hasattr(member, 'keys') else member for member in past_due]
        
        # Calculate totals
        total_amount = sum(float(m.get('amount_past_due', 0) or 0) for m in past_due_dicts)
        
        # Format for collections use
        collections_list = []
        for m in past_due_dicts:
            collections_list.append({
                "id": m.get('prospect_id') or m.get('guid'),
                "name": m.get('display_name') or m.get('full_name'),
                "email": m.get('email'),
                "phone": m.get('phone_number') or m.get('primary_phone'),
                "amount_past_due": float(m.get('amount_past_due', 0) or 0),
                "base_amount_past_due": float(m.get('base_amount_past_due', 0) or 0),
                "status": m.get('status_message'),
                "agreement_status": m.get('agreement_status')
            })
        
        logger.info(f"✅ Retrieved {len(collections_list)} past due members (total: ${total_amount:.2f})")
        
        return {
            "success": True,
            "members": collections_list,
            "count": len(collections_list),
            "total_amount": round(total_amount, 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting past due members: {e}")
        return {
            "success": False,
            "error": str(e),
            "members": [],
            "count": 0,
            "total_amount": 0
        }

def get_past_due_training_clients(min_amount: float = 0.01) -> Dict[str, Any]:
    """Get list of training clients with past due balances
    
    Args:
        min_amount: Minimum past due amount (default $0.01)
    
    Returns:
        {
            "success": True,
            "clients": [...],
            "count": 5,
            "total_amount": 567.89
        }
    """
    try:
        db = DatabaseManager()
        
        # Get training clients with past due amounts
        # Column is 'past_due_amount' NOT 'amount_past_due'
        query = """
            SELECT * FROM training_clients
            WHERE past_due_amount > ?
            ORDER BY past_due_amount DESC
        """
        clients_raw = db.execute_query(query, (min_amount,), fetch_all=True)
        
        # Convert to dicts and format
        clients_list = []
        total_amount = 0
        
        for client in clients_raw:
            c = dict(client) if hasattr(client, 'keys') else client
            past_due = float(c.get('past_due_amount', 0) or 0)
            
            if past_due >= min_amount:
                clients_list.append({
                    "id": c.get('member_id') or c.get('clubos_member_id'),
                    "name": c.get('full_name') or c.get('member_name'),
                    "email": c.get('email'),
                    "phone": c.get('phone') or c.get('mobile_phone'),
                    "past_due_amount": past_due,
                    "total_past_due": float(c.get('total_past_due', 0) or 0),
                    "training_package": c.get('training_package'),
                    "payment_status": c.get('payment_status'),
                    "sessions_remaining": c.get('sessions_remaining')
                })
                total_amount += past_due
        
        logger.info(f"✅ Retrieved {len(clients_list)} past due training clients (total: ${total_amount:.2f})")
        
        return {
            "success": True,
            "clients": clients_list,
            "count": len(clients_list),
            "total_amount": round(total_amount, 2)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting past due training clients: {e}")
        return {
            "success": False,
            "error": str(e),
            "clients": [],
            "count": 0,
            "total_amount": 0
        }

def send_payment_reminder(
    member_id: str,
    amount_past_due: float,
    reminder_type: str = "friendly",
    channel: str = "sms"
) -> Dict[str, Any]:
    """Send payment reminder to past due member
    
    Args:
        member_id: Member/prospect ID
        amount_past_due: Amount owed
        reminder_type: 'friendly', 'firm', or 'final'
        channel: 'sms' or 'email'
    
    Returns:
        {
            "success": True,
            "message_id": "...",
            "sent_at": "..."
        }
    """
    try:
        # Get reminder templates
        templates = {
            "friendly": f"Hi! Your Anytime Fitness account has a balance of ${amount_past_due:.2f}. Please update your payment method to avoid service interruption. Reply STOP to opt out.",
            "firm": f"Important: Your account balance of ${amount_past_due:.2f} is overdue. Please make payment immediately to maintain access. Contact us with questions. Reply STOP to opt out.",
            "final": f"FINAL NOTICE: Your account balance of ${amount_past_due:.2f} requires immediate payment. Failure to pay may result in collections referral. Reply STOP to opt out."
        }
        
        message_text = templates.get(reminder_type, templates["friendly"])
        
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
        
        # Send reminder
        success = client.send_message(
            member_id=str(member_id),
            message_text=message_text,
            channel=channel
        )
        
        if success:
            # Track the attempt
            track_collection_attempt(
                member_id=member_id,
                attempt_type=reminder_type,
                amount=amount_past_due,
                channel=channel
            )
            
            logger.info(f"✅ Sent {reminder_type} payment reminder to member {member_id}")
            
            return {
                "success": True,
                "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "sent_at": datetime.now().isoformat(),
                "reminder_type": reminder_type,
                "amount": amount_past_due
            }
        else:
            return {
                "success": False,
                "error": "Failed to send message"
            }
        
    except Exception as e:
        logger.error(f"❌ Error sending payment reminder: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def track_collection_attempt(
    member_id: str,
    attempt_type: str,
    amount: float,
    channel: str,
    notes: str = None
) -> Dict[str, Any]:
    """Track a collection attempt in the database
    
    Args:
        member_id: Member/prospect ID
        attempt_type: Type of collection attempt
        amount: Amount past due
        channel: Communication channel used
        notes: Optional notes
    
    Returns:
        {
            "success": True,
            "attempt_id": "..."
        }
    """
    try:
        db = DatabaseManager()
        
        # Create collection_attempts table if doesn't exist
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS collection_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                attempt_date TEXT NOT NULL,
                attempt_type TEXT NOT NULL,
                amount_past_due REAL NOT NULL,
                channel TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert attempt
        attempt_id = db.execute_query("""
            INSERT INTO collection_attempts 
            (member_id, attempt_date, attempt_type, amount_past_due, channel, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            member_id,
            datetime.now().isoformat(),
            attempt_type,
            amount,
            channel,
            notes
        ))
        
        logger.info(f"✅ Tracked collection attempt for member {member_id}")
        
        return {
            "success": True,
            "attempt_id": str(attempt_id)
        }
        
    except Exception as e:
        logger.error(f"❌ Error tracking collection attempt: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_collection_attempts(member_id: str, days_back: int = 30) -> Dict[str, Any]:
    """Get collection attempt history for a member
    
    Args:
        member_id: Member/prospect ID
        days_back: Number of days to look back (default 30)
    
    Returns:
        {
            "success": True,
            "attempts": [...],
            "count": 3
        }
    """
    try:
        db = DatabaseManager()
        
        # Ensure table exists
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS collection_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                attempt_date TEXT NOT NULL,
                method TEXT,
                outcome TEXT,
                notes TEXT,
                performed_by TEXT
            )
        """, fetch_all=False)
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        attempts = db.execute_query("""
            SELECT * FROM collection_attempts
            WHERE member_id = ? AND attempt_date >= ?
            ORDER BY attempt_date DESC
        """, (member_id, cutoff_date))
        
        logger.info(f"✅ Retrieved {len(attempts)} collection attempts for member {member_id}")
        
        return {
            "success": True,
            "attempts": attempts,
            "count": len(attempts)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting collection attempts: {e}")
        return {
            "success": False,
            "error": str(e),
            "attempts": [],
            "count": 0
        }

def generate_collections_referral_list(
    min_attempts: int = 3,
    min_days_past_due: int = 14,
    min_amount: float = 50.0
) -> Dict[str, Any]:
    """Generate collections referral list for external collections agency
    
    Args:
        min_attempts: Minimum collection attempts before referral (default 3)
        min_days_past_due: Minimum days past due (default 14)
        min_amount: Minimum amount to refer (default $50)
    
    Returns:
        {
            "success": True,
            "referrals": [...],
            "count": 12,
            "total_amount": 3456.78
        }
    """
    try:
        db = DatabaseManager()
        
        # Ensure collection_attempts table exists first
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS collection_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT NOT NULL,
                attempt_date TEXT NOT NULL,
                attempt_type TEXT,
                amount_past_due REAL,
                channel TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """, fetch_all=False)
        
        # Get members with sufficient attempts
        cutoff_date = (datetime.now() - timedelta(days=min_days_past_due)).isoformat()
        
        query = """
            SELECT m.*, COUNT(ca.id) as attempt_count
            FROM members m
            LEFT JOIN collection_attempts ca ON m.prospect_id = ca.member_id OR m.guid = ca.member_id
            WHERE CAST(COALESCE(m.amount_past_due, '0') AS FLOAT) >= ?
            GROUP BY m.prospect_id
            HAVING attempt_count >= ?
            ORDER BY m.amount_past_due DESC
        """
        
        referrals = db.execute_query(query, (min_amount, min_attempts))
        
        # Format referral list
        referral_list = []
        total_amount = 0
        
        for member in referrals:
            amount = float(member.get('amount_past_due', 0) or 0)
            total_amount += amount
            
            referral_list.append({
                "member_id": member.get('prospect_id') or member.get('guid'),
                "name": member.get('display_name') or member.get('full_name'),
                "email": member.get('email'),
                "phone": member.get('phone_number') or member.get('primary_phone'),
                "amount_past_due": amount,
                "attempt_count": member.get('attempt_count', 0),
                "status": member.get('status_message'),
                "referral_date": datetime.now().isoformat()
            })
        
        logger.info(f"✅ Generated collections referral list: {len(referral_list)} members (total: ${total_amount:.2f})")
        
        return {
            "success": True,
            "referrals": referral_list,
            "count": len(referral_list),
            "total_amount": round(total_amount, 2),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating collections referral list: {e}")
        return {
            "success": False,
            "error": str(e),
            "referrals": [],
            "count": 0,
            "total_amount": 0
        }
