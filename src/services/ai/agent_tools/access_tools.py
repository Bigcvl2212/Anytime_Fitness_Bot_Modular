"""
Access Control Tools

Tools for managing gym door access based on payment status
"""

import logging
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from services.member_access_control import MemberAccessControl
from services.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

def lock_door_for_member(member_id: str, reason: str = "Payment Issue") -> Dict[str, Any]:
    """Lock gym door access for a member (ClubHub API ban)
    
    Args:
        member_id: Member/prospect ID
        reason: Reason for locking access
    
    Returns:
        {
            "success": True,
            "member_id": "...",
            "action": "locked",
            "reason": "..."
        }
    """
    try:
        access_control = MemberAccessControl()
        
        # Lock member access
        result = access_control._lock_member(member_id, reason)
        
        if result.get('success'):
            logger.info(f"🔒 Locked door access for member {member_id} (reason: {reason})")
            
            return {
                "success": True,
                "member_id": member_id,
                "action": "locked",
                "reason": reason,
                "timestamp": result.get('timestamp')
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Failed to lock access'),
                "member_id": member_id
            }
        
    except Exception as e:
        logger.error(f"❌ Error locking door access for member {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "member_id": member_id
        }

def unlock_door_for_member(member_id: str, reason: str = "Payment Resolved") -> Dict[str, Any]:
    """Unlock gym door access for a member (ClubHub API unban)
    
    Args:
        member_id: Member/prospect ID
        reason: Reason for unlocking access
    
    Returns:
        {
            "success": True,
            "member_id": "...",
            "action": "unlocked",
            "reason": "..."
        }
    """
    try:
        access_control = MemberAccessControl()
        
        # Unlock member access
        result = access_control._unlock_member(member_id, reason)
        
        if result.get('success'):
            logger.info(f"🔓 Unlocked door access for member {member_id} (reason: {reason})")
            
            return {
                "success": True,
                "member_id": member_id,
                "action": "unlocked",
                "reason": reason,
                "timestamp": result.get('timestamp')
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Failed to unlock access'),
                "member_id": member_id
            }
        
    except Exception as e:
        logger.error(f"❌ Error unlocking door access for member {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "member_id": member_id
        }

def check_member_access_status(member_id: str) -> Dict[str, Any]:
    """Check current door access status for a member
    
    Args:
        member_id: Member/prospect ID
    
    Returns:
        {
            "success": True,
            "member_id": "...",
            "access_status": "locked" or "unlocked",
            "reason": "...",
            "last_action_date": "..."
        }
    """
    try:
        db = DatabaseManager()
        
        # Get latest access action from log
        query = """
            SELECT * FROM access_control_log
            WHERE member_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """
        
        result = db.execute_query(query, (member_id,))
        
        if result and len(result) > 0:
            latest_action = result[0]
            
            return {
                "success": True,
                "member_id": member_id,
                "access_status": latest_action.get('action', 'unknown'),
                "reason": latest_action.get('reason', ''),
                "last_action_date": latest_action.get('timestamp', ''),
                "performed_by": latest_action.get('performed_by', 'system')
            }
        else:
            # No access log found - assume unlocked
            return {
                "success": True,
                "member_id": member_id,
                "access_status": "unlocked",
                "reason": "No access log found",
                "last_action_date": None
            }
        
    except Exception as e:
        logger.error(f"❌ Error checking access status for member {member_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "member_id": member_id
        }

def auto_manage_access_by_payment_status(
    min_past_due_amount: float = 0.01,
    grace_period_days: int = 3
) -> Dict[str, Any]:
    """Automatically manage door access based on payment status
    
    Locks access for past due members, unlocks for paid members
    
    Args:
        min_past_due_amount: Minimum amount to trigger lock (default $0.01)
        grace_period_days: Grace period before locking (default 3 days)
    
    Returns:
        {
            "success": True,
            "locked": 5,
            "unlocked": 2,
            "errors": []
        }
    """
    try:
        access_control = MemberAccessControl()
        
        # Run the automated check
        result = access_control.check_and_lock_past_due_members(
            min_amount=min_past_due_amount
        )
        
        logger.info(f"✅ Auto-managed door access: {result.get('locked', 0)} locked, {result.get('unlocked', 0)} unlocked")
        
        return {
            "success": True,
            "locked": result.get('locked', 0),
            "unlocked": result.get('unlocked', 0),
            "checked": result.get('checked', 0),
            "errors": result.get('errors', [])
        }
        
    except Exception as e:
        logger.error(f"❌ Error auto-managing door access: {e}")
        return {
            "success": False,
            "error": str(e),
            "locked": 0,
            "unlocked": 0
        }
