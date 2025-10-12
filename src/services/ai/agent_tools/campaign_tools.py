"""
Campaign Management Tools - FIXED to use ClubHub API directly

Tools for managing marketing campaigns to prospects, green members, and PPV members
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from services.database_manager import DatabaseManager
from services.clubos_messaging_client_simple import ClubOSMessagingClient
from services.authentication.secure_secrets_manager import SecureSecretsManager

logger = logging.getLogger(__name__)

def get_campaign_prospects(filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get list of ACTIVE prospects from ClubHub API for campaign targeting
    
    NOTE: Database has 110K+ historical prospects. This fetches CURRENT active prospects from ClubHub API (~3800).
    
    Args:
        filters: Optional filters (not used - ClubHub returns current prospects)
    
    Returns:
        {
            "success": True,
            "count": ~3800,
            "sample": [...first 10 prospects...],
            "summary": "human readable summary"
        }
    """
    try:
        from services.api.clubhub_api_client import ClubHubAPIClient
        
        # Initialize ClubHub client (uses unified auth service internally)
        client = ClubHubAPIClient()
        
        # Authenticate (unified auth will get credentials from env or database)
        logger.info("Authenticating with ClubHub API...")
        auth_success = client.authenticate()
        if not auth_success:
            logger.error("ClubHub authentication failed - check CLUBHUB_EMAIL and CLUBHUB_PASSWORD env vars")
            return {
                "success": False,
                "error": "ClubHub authentication failed - check credentials in environment",
                "count": 0
            }
        
        logger.info("Fetching active prospects from ClubHub API...")
        
        # Fetch ALL current prospects from ClubHub (paginated)
        prospects_raw = client.get_all_prospects_paginated()
        
        if not prospects_raw:
            logger.error("No prospects returned from ClubHub API")
            return {
                "success": False,
                "error": "No prospects returned from ClubHub",
                "count": 0
            }
        
        # Format for campaign use
        campaign_prospects = []
        for prospect in prospects_raw:
            campaign_prospects.append({
                "id": prospect.get('guid') or prospect.get('prospectId'),
                "name": prospect.get('displayName') or prospect.get('fullName') or f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip(),
                "email": prospect.get('email'),
                "phone": prospect.get('primaryPhone') or prospect.get('phone'),
                "status": prospect.get('status') or prospect.get('statusMessage')
            })
        
        count = len(campaign_prospects)
        logger.info(f"Retrieved {count} ACTIVE prospects from ClubHub API")
        
        # Return summary to avoid token limit issues
        return {
            "success": True,
            "count": count,
            "sample": campaign_prospects[:10],  # First 10 as examples
            "summary": f"Found {count} active prospects ready for campaigns. Sample includes names, emails, phones, and status.",
            "note": "Full prospect list available internally. Use send_bulk_campaign to target all prospects."
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign prospects from ClubHub: {e}")
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }


def get_green_members(days_since_signup: int = 30) -> Dict[str, Any]:
    """Get recently signed up members (green members)
    
    Args:
        days_since_signup: Number of days since signup (default 30)
    
    Returns:
        {
            "success": True,
            "members": [...],
            "count": 45
        }
    """
    try:
        db = DatabaseManager()
        
        # Get green members (members category)
        green_members_list = db.get_members_by_category('green')
        
        # Format for campaign use
        campaign_members = []
        for member in green_members_list:
            # Convert sqlite3.Row to dict
            m = dict(member) if hasattr(member, 'keys') else member
            campaign_members.append({
                "id": m.get('prospect_id') or m.get('guid'),
                "name": m.get('display_name') or m.get('full_name'),
                "email": m.get('email'),
                "phone": m.get('phone_number') or m.get('primary_phone'),
                "signup_date": m.get('created_at') or m.get('join_date'),
                "status": m.get('status_message')
            })
        
        logger.info(f"Retrieved {len(campaign_members)} green members for campaign")
        
        return {
            "success": True,
            "members": campaign_members,
            "count": len(campaign_members)
        }
        
    except Exception as e:
        logger.error(f"Error getting green members: {e}")
        return {
            "success": False,
            "error": str(e),
            "members": [],
            "count": 0
        }

def get_ppv_members(filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get pre-paid visitor (PPV) members for conversion campaigns
    
    PPV members have status_message = 'Pay Per Visit Member'
    
    Args:
        filters: Optional filters (not currently used)
    
    Returns:
        {
            "success": True,
            "members": [...],
            "count": 12
        }
    """
    try:
        db = DatabaseManager()
        
        # Get PPV members (status_message = 'Pay Per Visit Member')
        ppv_members_list = db.get_members_by_category('ppv')
        
        # Format for campaign use
        campaign_members = []
        for member in ppv_members_list:
            # Convert sqlite3.Row to dict
            m = dict(member) if hasattr(member, 'keys') else member
            campaign_members.append({
                "id": m.get('prospect_id') or m.get('guid'),
                "name": m.get('display_name') or m.get('full_name'),
                "email": m.get('email'),
                "phone": m.get('phone_number') or m.get('primary_phone'),
                "status": m.get('status_message'),
                "membership_type": "PPV"
            })
        
        logger.info(f"Retrieved {len(campaign_members)} PPV members for campaign")
        
        return {
            "success": True,
            "members": campaign_members,
            "count": len(campaign_members)
        }
        
    except Exception as e:
        logger.error(f"Error getting PPV members: {e}")
        return {
            "success": False,
            "error": str(e),
            "members": [],
            "count": 0
        }

def send_bulk_campaign(
    recipient_list: List[Dict[str, Any]],
    message_text: str,
    campaign_name: str = "Untitled Campaign",
    channel: str = "sms",
    subject: str = None
) -> Dict[str, Any]:
    """Send bulk campaign message to recipient list
    
    Args:
        recipient_list: List of recipients [{"id": ..., "name": ..., "phone": ..., "email": ...}]
        message_text: Message content
        campaign_name: Campaign name for tracking
        channel: 'sms' or 'email'
        subject: Email subject (required if channel='email')
    
    Returns:
        {
            "success": True,
            "campaign_id": "...",
            "sent": 145,
            "failed": 3,
            "status": "completed"
        }
    """
    try:
        logger.info(f"Starting bulk campaign: {campaign_name}")
        logger.info(f"   Recipients: {len(recipient_list)}, Channel: {channel}")
        
        # Get ClubOS credentials
        secrets_manager = SecureSecretsManager()
        clubos_user = secrets_manager.get_secret("clubos-email")
        clubos_pass = secrets_manager.get_secret("clubos-password")
        
        if not clubos_user or not clubos_pass:
            return {
                "success": False,
                "error": "ClubOS credentials not found",
                "sent": 0,
                "failed": len(recipient_list)
            }
        
        # Initialize messaging client
        client = ClubOSMessagingClient()
        
        # Authenticate
        auth_success = client.authenticate(clubos_user, clubos_pass)
        if not auth_success:
            return {
                "success": False,
                "error": "ClubOS authentication failed",
                "sent": 0,
                "failed": len(recipient_list)
            }
        
        # Send campaign
        sent_count = 0
        failed_count = 0
        errors = []
        
        for recipient in recipient_list:
            try:
                member_id = recipient.get('id')
                if not member_id:
                    failed_count += 1
                    continue
                
                # Send message
                success = client.send_message(
                    member_id=str(member_id),
                    message_text=message_text,
                    channel=channel
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    errors.append(f"Failed to send to {recipient.get('name')}")
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Error sending to {recipient.get('name')}: {str(e)}")
        
        # Store campaign in database
        db = DatabaseManager()
        # TODO: Add campaign tracking to database
        
        logger.info(f"Campaign completed: {sent_count}/{len(recipient_list)} sent successfully")
        
        return {
            "success": True,
            "campaign_id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "campaign_name": campaign_name,
            "sent": sent_count,
            "failed": failed_count,
            "total": len(recipient_list),
            "status": "completed",
            "errors": errors[:10] if errors else []  # Return first 10 errors
        }
        
    except Exception as e:
        logger.error(f"Error sending bulk campaign: {e}")
        return {
            "success": False,
            "error": str(e),
            "sent": 0,
            "failed": len(recipient_list) if recipient_list else 0
        }

def get_campaign_templates() -> Dict[str, Any]:
    """Get available campaign message templates
    
    Returns:
        {
            "success": True,
            "templates": [...]
        }
    """
    try:
        # Define built-in campaign templates
        templates = [
            {
                "name": "prospect_welcome",
                "title": "Prospect Welcome",
                "message": "Hi {name}! Welcome to Anytime Fitness! We're excited to have you join our community. Stop by anytime to check out our facility. Reply STOP to opt out.",
                "variables": ["name"],
                "channel": "sms"
            },
            {
                "name": "green_member_welcome",
                "title": "New Member Welcome",
                "message": "Welcome to Anytime Fitness, {name}! We're thrilled you joined us. Download our app for class schedules, booking, and more. Need help? Just ask! Reply STOP to opt out.",
                "variables": ["name"],
                "channel": "sms"
            },
            {
                "name": "ppv_conversion",
                "title": "PPV to Full Member Conversion",
                "message": "Hi {name}! Loving your workouts? Convert to a full membership and get unlimited access + exclusive perks. Ask us about member rates today! Reply STOP to opt out.",
                "variables": ["name"],
                "channel": "sms"
            },
            {
                "name": "monthly_special",
                "title": "Monthly Special Offer",
                "message": "Special Offer: Join Anytime Fitness this month and get 50% off enrollment! 24/7 access, no commitments. Text back or stop by to claim. Reply STOP to opt out.",
                "variables": [],
                "channel": "sms"
            },
            {
                "name": "referral_bonus",
                "title": "Referral Bonus",
                "message": "Hi {name}! Refer a friend and you both get $20 off next month. Share the fitness love! Ask staff for details. Reply STOP to opt out.",
                "variables": ["name"],
                "channel": "sms"
            }
        ]
        
        logger.info(f"Retrieved {len(templates)} campaign templates")
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
        
    except Exception as e:
        logger.error(f"Error getting campaign templates: {e}")
        return {
            "success": False,
            "error": str(e),
            "templates": []
        }
