"""
Member Access Control Service

This service handles automated locking and unlocking of member gym access
based on payment status and invoice tracking.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .database_manager import DatabaseManager
from .api.clubhub_api_client import ClubHubAPIClient

logger = logging.getLogger(__name__)

class MemberAccessControl:
    """Manages member gym access based on payment status"""
    
    def __init__(self, user_email: str = None, club_id: str = None):
        self.db_manager = DatabaseManager()
        self.clubhub_client = None  # Initialize lazily when needed
        self.user_email = user_email or 'Gym Bot System'  # From login session
        self.club_id = club_id  # From login session or JWT token
    
    def _get_authenticated_clubhub_client(self):
        """Get authenticated ClubHub client, authenticate if needed"""
        if not self.clubhub_client:
            self.clubhub_client = ClubHubAPIClient()
            # Authenticate using credentials from SecureSecretsManager
            try:
                from src.services.authentication.secure_secrets_manager import SecureSecretsManager
                secrets_manager = SecureSecretsManager()
                
                email = secrets_manager.get_secret("clubhub-email")
                password = secrets_manager.get_secret("clubhub-password")
                
                if email and password:
                    logger.info("🔐 Authenticating ClubHub client...")
                    success = self.clubhub_client.authenticate(email, password)
                    if not success:
                        logger.error("❌ ClubHub authentication failed")
                        return None
                    logger.info("✅ ClubHub client authenticated")
                else:
                    logger.error("❌ No ClubHub credentials found")
                    return None
            except Exception as e:
                logger.error(f"❌ ClubHub authentication error: {e}")
                return None
        return self.clubhub_client
        
    def check_and_lock_past_due_members(self) -> Dict[str, int]:
        """
        Check all members and automatically lock those who are past due
        
        Returns:
            Dict with counts of locked members
        """
        try:
            logger.info("🔒 Starting automated member lock check...")
            
            # Get all members by combining all categories
            all_members = []
            for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                try:
                    category_members = self.db_manager.get_members_by_category(category)
                    all_members.extend(category_members)
                except Exception as e:
                    logger.warning(f"Failed to get {category} members: {e}")
            members = all_members
            
            locked_count = 0
            already_locked_count = 0
            errors = []
            
            for member in members:
                try:
                    if self._should_lock_member(member):
                        lock_result = self._lock_member(member)
                        if lock_result['success']:
                            if lock_result['was_already_locked']:
                                already_locked_count += 1
                            else:
                                locked_count += 1
                                logger.info(f"🔒 Locked member: {member.get('display_name', 'Unknown')} (${member.get('amount_past_due', 0):.2f} past due)")
                        else:
                            errors.append(f"Failed to lock {member.get('display_name', 'Unknown')}: {lock_result['error']}")
                except Exception as e:
                    logger.error(f"❌ Error processing member {member.get('display_name', 'Unknown')}: {e}")
                    errors.append(f"Error processing {member.get('display_name', 'Unknown')}: {str(e)}")
            
            result = {
                'locked_count': locked_count,
                'already_locked_count': already_locked_count,
                'total_processed': len(members),
                'errors': errors
            }
            
            logger.info(f"🔒 Lock check completed: {locked_count} new locks, {already_locked_count} already locked")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in automated member lock check: {e}")
            return {'error': str(e)}
    
    def check_and_unlock_paid_members(self) -> Dict[str, int]:
        """
        Check all locked members and unlock those who have paid their invoices
        
        Returns:
            Dict with counts of unlocked members
        """
        try:
            logger.info("🔓 Starting automated member unlock check...")
            
            # Get all members by combining all categories
            all_members = []
            for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                try:
                    category_members = self.db_manager.get_members_by_category(category)
                    all_members.extend(category_members)
                except Exception as e:
                    logger.warning(f"Failed to get {category} members: {e}")
            members = all_members
            unlocked_count = 0
            still_locked_count = 0
            errors = []
            
            for member in members:
                try:
                    if self._should_unlock_member(member):
                        unlock_result = self._unlock_member(member)
                        if unlock_result['success']:
                            if unlock_result['was_already_unlocked']:
                                still_locked_count += 1
                            else:
                                unlocked_count += 1
                                logger.info(f"🔓 Unlocked member: {member.get('display_name', 'Unknown')} (payment received)")
                        else:
                            errors.append(f"Failed to unlock {member.get('display_name', 'Unknown')}: {unlock_result['error']}")
                except Exception as e:
                    logger.error(f"❌ Error processing member {member.get('display_name', 'Unknown')}: {e}")
                    errors.append(f"Error processing {member.get('display_name', 'Unknown')}: {str(e)}")
            
            result = {
                'unlocked_count': unlocked_count,
                'still_locked_count': still_locked_count,
                'total_processed': len([m for m in members if m.get('amount_past_due', 0) > 0]),
                'errors': errors
            }
            
            logger.info(f"🔓 Unlock check completed: {unlocked_count} new unlocks, {still_locked_count} still locked")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in automated member unlock check: {e}")
            return {'error': str(e)}
    
    def _should_lock_member(self, member: Dict) -> bool:
        """Determine if a member should be locked"""
        try:
            # Check if member has past due amount
            past_due_amount = float(member.get('amount_past_due', 0))
            if past_due_amount <= 0:
                return False
            
            # Check if member is already locked (we'll track this in a separate field)
            is_locked = member.get('gym_access_locked', False)
            if is_locked:
                return False  # Already locked
            
            # Additional criteria can be added here:
            # - How long they've been past due
            # - Number of missed payments
            # - Member type (staff, comp members might not be locked)
            
            member_type = (member.get('user_type') or '').lower()
            if member_type in ['staff', 'comp', 'complimentary']:
                logger.info(f"⚠️ Skipping lock for {member_type} member: {member.get('display_name', 'Unknown')}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking if member should be locked: {e}")
            return False
    
    def _should_unlock_member(self, member: Dict) -> bool:
        """Determine if a member should be unlocked"""
        try:
            # Check if member is currently locked
            is_locked = member.get('gym_access_locked', False)
            if not is_locked:
                return False  # Not locked, no need to unlock
            
            # Check if member has no past due amount
            past_due_amount = float(member.get('amount_past_due', 0))
            if past_due_amount <= 0:
                return True
            
            # TODO: Check if recent payments have been made
            # This would require integration with Square webhooks or payment tracking
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking if member should be unlocked: {e}")
            return False
    
    def _lock_member(self, member: Dict) -> Dict:
        """Lock a member's gym access via ClubHub using bans system"""
        try:
            member_id = member.get('prospect_id') or member.get('guid')
            if not member_id:
                return {'success': False, 'error': 'No member ID found'}
            
            # Check if this is a staff member - skip banning staff
            status_message = member.get('status_message', '')
            if status_message and 'Staff' in status_message:
                logger.info(f"⚠️ Skipping staff member {member.get('display_name', 'Unknown')} (ID: {member_id}) - Staff cannot be banned")
                return {
                    'success': True,
                    'was_already_locked': False,
                    'member_id': member_id,
                    'action': 'skipped_staff',
                    'message': 'Staff member - access control not applicable'
                }
            
            logger.info(f"🔒 Banning member {member.get('display_name', 'Unknown')} (ID: {member_id})")
            
            # Get authenticated ClubHub client
            client = self._get_authenticated_clubhub_client()
            if not client:
                logger.error("❌ Cannot authenticate ClubHub client")
                return {'success': False, 'error': 'Authentication failed'}
            
            # Skip checking existing bans since GET endpoint returns 405
            # We'll handle "already banned" errors from the PUT request instead
            
            # Create ban data for past due member using ClubHub's actual ban structure
            # Use user email from login session for proper attribution
            ban_data = {
                "member": {"id": int(member_id)},
                "note": f"Banned by: {self.user_email}\\nReason: Payment Issue"
            }
            
            # Call ClubHub API to ban member (using correct ban endpoint)
            ban_result = client.put_member_bans(member_id, ban_data)
            
            if ban_result and not ban_result.get('error'):
                logger.info(f"✅ Successfully banned member {member_id}")
                return {
                    'success': True,
                    'was_already_locked': False,
                    'member_id': member_id,
                    'action': 'locked',
                    'ban_data': ban_result
                }
            else:
                # Check if this is an "already banned" error or a real failure
                error_msg = ban_result.get('error', 'Unknown error') if ban_result else 'No response from ClubHub'
                
                # If the error indicates the member is already banned, treat as success
                if 'already banned' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    logger.info(f"⚠️ Member {member_id} was already banned")
                    return {
                        'success': True,
                        'was_already_locked': True,
                        'member_id': member_id,
                        'action': 'already_locked'
                    }
                else:
                    logger.error(f"❌ Failed to ban member {member_id}: {error_msg}")
                    return {
                        'success': False,
                        'error': f'ClubHub ban failed: {error_msg}',
                        'member_id': member_id
                    }
            
        except Exception as e:
            logger.error(f"❌ Error locking member: {e}")
            return {'success': False, 'error': str(e)}
    
    def _unlock_member(self, member: Dict) -> Dict:
        """Unlock a member's gym access via ClubHub by removing bans"""
        try:
            member_id = member.get('prospect_id') or member.get('guid')
            if not member_id:
                return {'success': False, 'error': 'No member ID found'}
            
            # Check if this is a staff member - skip unbanning staff  
            status_message = member.get('status_message', '')
            if status_message and 'Staff' in status_message:
                logger.info(f"⚠️ Skipping staff member {member.get('display_name', 'Unknown')} (ID: {member_id}) - Staff access not managed by ban system")
                return {
                    'success': True,
                    'was_already_unlocked': False,
                    'member_id': member_id,
                    'action': 'skipped_staff',
                    'message': 'Staff member - access control not applicable'
                }
            
            logger.info(f"🔓 Unbanning member {member.get('display_name', 'Unknown')} (ID: {member_id})")
            
            # Get authenticated ClubHub client
            client = self._get_authenticated_clubhub_client()
            if not client:
                logger.error("❌ Cannot authenticate ClubHub client")
                return {'success': False, 'error': 'Authentication failed'}
            
            # Skip checking existing bans since GET endpoint returns 405
            # We'll handle "not banned" errors from the DELETE request instead
            
            # Call ClubHub API to remove all bans for this member
            unban_result = client.delete_member_bans(member_id)
            
            if unban_result and not unban_result.get('error'):
                logger.info(f"✅ Successfully unbanned member {member_id}")
                return {
                    'success': True,
                    'was_already_unlocked': False,
                    'member_id': member_id,
                    'action': 'unlocked',
                    'unban_data': unban_result
                }
            else:
                error_msg = unban_result.get('error', 'Unknown error') if unban_result else 'No response from ClubHub'
                logger.error(f"❌ Failed to unban member {member_id}: {error_msg}")
                return {
                    'success': False,
                    'error': f'ClubHub unban failed: {error_msg}',
                    'member_id': member_id
                }
            
        except Exception as e:
            logger.error(f"❌ Error unlocking member: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_member_access_status(self, member_id: str) -> Dict:
        """Get current access status for a member"""
        try:
            # Get all members by combining all categories
            all_members = []
            for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                try:
                    category_members = self.db_manager.get_members_by_category(category)
                    all_members.extend(category_members)
                except Exception as e:
                    logger.warning(f"Failed to get {category} members: {e}")
            
            member = None
            for m in all_members:
                if str(m.get('prospect_id', '')) == str(member_id) or str(m.get('guid', '')) == str(member_id):
                    member = m
                    break
            
            if not member:
                return {'success': False, 'error': 'Member not found'}
            
            # Skip checking actual ban status since GET endpoint returns 405
            # For now, we'll assume members are not locked unless we have evidence otherwise
            is_locked = False
            
            past_due_amount = float(member.get('amount_past_due', 0))
            
            return {
                'success': True,
                'member_id': member_id,
                'is_locked': is_locked,
                'past_due_amount': past_due_amount,
                'should_be_locked': past_due_amount > 0,
                'access_status': 'locked' if is_locked else 'active',
                'bans': bans.get('bans', []) if bans else []
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting member access status: {e}")
            return {'success': False, 'error': str(e)}
    
    def manual_toggle_member_access(self, member_id: str, action: str) -> Dict:
        """Manually lock or unlock a member's access"""
        try:
            # Get all members by combining all categories
            all_members = []
            for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                try:
                    category_members = self.db_manager.get_members_by_category(category)
                    all_members.extend(category_members)
                except Exception as e:
                    logger.warning(f"Failed to get {category} members: {e}")
            
            member = None
            for m in all_members:
                if str(m.get('prospect_id', '')) == str(member_id) or str(m.get('guid', '')) == str(member_id):
                    member = m
                    break
            
            if not member:
                return {'success': False, 'error': 'Member not found'}
            
            if action == 'lock':
                result = self._lock_member(member)
            elif action == 'unlock':
                result = self._unlock_member(member)
            else:
                return {'success': False, 'error': 'Invalid action. Must be "lock" or "unlock"'}
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error manually toggling member access: {e}")
            return {'success': False, 'error': str(e)}
    
    def check_member_access_status(self, member_id: str) -> Dict:
        """Check current member access status and past due information"""
        try:
            logger.info(f"🔐 Checking access status for member: {member_id}")
            
            # Get all members by combining all categories
            all_members = []
            for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                try:
                    category_members = self.db_manager.get_members_by_category(category)
                    all_members.extend(category_members)
                except Exception as e:
                    logger.warning(f"Failed to get {category} members: {e}")
            
            # Find the member
            member = None
            for m in all_members:
                if str(m.get('prospect_id', '')) == str(member_id) or str(m.get('guid', '')) == str(member_id):
                    member = m
                    break
            
            if not member:
                logger.warning(f"Member {member_id} not found in database")
                return {'success': False, 'error': 'Member not found'}
            
            # Get member's past due amount
            past_due_amount = float(member.get('past_due_amount', 0)) if member.get('past_due_amount') else 0
            
            # For now, assume member is locked if they have past due amount
            # In the future, this could query ClubHub's actual ban status
            is_locked = past_due_amount > 0
            should_be_locked = past_due_amount > 0
            
            logger.info(f"🔐 Member {member_id} status - Past Due: ${past_due_amount:.2f}, Locked: {is_locked}")
            
            return {
                'success': True,
                'member_id': member_id,
                'is_locked': is_locked,
                'should_be_locked': should_be_locked,
                'past_due_amount': past_due_amount,
                'access_status': 'LOCKED' if is_locked else 'ACTIVE',
                'member_category': member.get('category', 'Unknown'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking member access status: {e}")
            return {'success': False, 'error': str(e)}
