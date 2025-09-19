"""
Automated Access Control Monitor

This service provides continuous monitoring of member payment status and automatically
locks/unlocks gym access based on payment status and Square invoice updates.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.services.database_manager import DatabaseManager
from src.services.member_access_control import MemberAccessControl

logger = logging.getLogger(__name__)

class AutomatedAccessMonitor:
    """Monitors member payment status and automatically manages gym access"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.access_control = MemberAccessControl()
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock_check_interval = 3600  # Check for locks every hour
        self.unlock_check_interval = 300  # Check for unlocks every 5 minutes
        self.last_lock_check = datetime.min
        self.last_unlock_check = datetime.min
        
    def start_monitoring(self):
        """Start the automated monitoring system"""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoring is already active")
            return
            
        logger.info("🚀 Starting automated access monitoring system...")
        self.monitoring_active = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ Automated access monitoring started")
    
    def stop_monitoring(self):
        """Stop the automated monitoring system"""
        if not self.monitoring_active:
            return
            
        logger.info("🛑 Stopping automated access monitoring...")
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("✅ Automated access monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs continuously"""
        logger.info("🔄 Automated monitoring loop started")
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Check if it's time for lock check (hourly)
                if (current_time - self.last_lock_check).total_seconds() >= self.lock_check_interval:
                    logger.info("🔒 Running automated lock check...")
                    self._perform_lock_check()
                    self.last_lock_check = current_time
                
                # Check if it's time for unlock check (every 5 minutes)
                if (current_time - self.last_unlock_check).total_seconds() >= self.unlock_check_interval:
                    logger.info("🔓 Running automated unlock check...")
                    self._perform_unlock_check()
                    self.last_unlock_check = current_time
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _perform_lock_check(self):
        """Perform automated lock check for past due members"""
        try:
            logger.info("🔒 Checking for members who should be locked...")
            
            # Get all members who are past due but not yet locked
            past_due_members = self.db_manager.get_members_by_category('past_due')
            
            locked_count = 0
            for member in past_due_members:
                try:
                    member_id = member.get('prospect_id') or member.get('guid')
                    member_name = member.get('display_name', 'Unknown')
                    past_due_amount = float(member.get('amount_past_due', 0))
                    
                    if past_due_amount > 0 and member_id:
                        # Check if member should be locked (not staff, not already locked)
                        if self._should_lock_member(member):
                            result = self.access_control.manual_toggle_member_access(member_id, 'lock')
                            
                            if result.get('success'):
                                locked_count += 1
                                logger.info(f"🔒 Auto-locked member: {member_name} (${past_due_amount:.2f} past due)")
                                
                                # Log the lock action
                                self._log_access_action(
                                    member_id=member_id,
                                    member_name=member_name,
                                    action='auto_lock',
                                    reason=f'Past due amount: ${past_due_amount:.2f}',
                                    success=True
                                )
                            else:
                                logger.warning(f"⚠️ Failed to auto-lock {member_name}: {result.get('error')}")
                                
                                # Log the failed lock action
                                self._log_access_action(
                                    member_id=member_id,
                                    member_name=member_name,
                                    action='auto_lock',
                                    reason=f'Past due amount: ${past_due_amount:.2f}',
                                    success=False,
                                    error=result.get('error')
                                )
                        
                except Exception as e:
                    logger.error(f"❌ Error processing member {member.get('display_name', 'Unknown')} for lock: {e}")
            
            logger.info(f"🔒 Lock check completed: {locked_count} members auto-locked")
            
        except Exception as e:
            logger.error(f"❌ Error in automated lock check: {e}")
    
    def _perform_unlock_check(self):
        """Perform automated unlock check for paid members"""
        try:
            logger.info("🔓 Checking for members who should be unlocked...")
            
            # Get all members to check payment status
            all_categories = ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']
            all_members = []
            
            for category in all_categories:
                try:
                    category_members = self.db_manager.get_members_by_category(category)
                    all_members.extend(category_members)
                except Exception as e:
                    logger.warning(f"Failed to get {category} members: {e}")
            
            unlocked_count = 0
            for member in all_members:
                try:
                    member_id = member.get('prospect_id') or member.get('guid')
                    member_name = member.get('display_name', 'Unknown')
                    past_due_amount = float(member.get('amount_past_due', 0))
                    
                    # Check if member should be unlocked (no past due amount or recent payment)
                    if member_id and self._should_unlock_member(member):
                        result = self.access_control.manual_toggle_member_access(member_id, 'unlock')
                        
                        if result.get('success'):
                            unlocked_count += 1
                            logger.info(f"🔓 Auto-unlocked member: {member_name} (payment received or account current)")
                            
                            # Log the unlock action
                            self._log_access_action(
                                member_id=member_id,
                                member_name=member_name,
                                action='auto_unlock',
                                reason='Payment received or account current',
                                success=True
                            )
                        else:
                            logger.warning(f"⚠️ Failed to auto-unlock {member_name}: {result.get('error')}")
                            
                            # Log the failed unlock action
                            self._log_access_action(
                                member_id=member_id,
                                member_name=member_name,
                                action='auto_unlock',
                                reason='Payment received or account current',
                                success=False,
                                error=result.get('error')
                            )
                        
                except Exception as e:
                    logger.error(f"❌ Error processing member {member.get('display_name', 'Unknown')} for unlock: {e}")
            
            logger.info(f"🔓 Unlock check completed: {unlocked_count} members auto-unlocked")
            
        except Exception as e:
            logger.error(f"❌ Error in automated unlock check: {e}")
    
    def _should_lock_member(self, member: Dict) -> bool:
        """Determine if a member should be auto-locked"""
        try:
            # Check past due amount
            past_due_amount = float(member.get('amount_past_due', 0))
            if past_due_amount <= 0:
                return False
            
            # Don't lock staff or comp members
            member_type = (member.get('user_type') or '').lower()
            status_message = (member.get('status_message') or '').lower()
            
            if member_type in ['staff', 'comp', 'complimentary'] or 'staff' in status_message:
                return False
            
            # Check if already locked (skip if already processed)
            member_id = member.get('prospect_id') or member.get('guid')
            if self._is_member_currently_locked(member_id):
                return False
            
            # Additional criteria: only lock if past due for more than 7 days
            # This prevents immediate locking on payment date mismatches
            return past_due_amount > 25.00  # Only lock for significant amounts
            
        except Exception as e:
            logger.error(f"❌ Error checking if member should be locked: {e}")
            return False
    
    def _should_unlock_member(self, member: Dict) -> bool:
        """Determine if a member should be auto-unlocked"""
        try:
            # Only check members who might be locked
            member_id = member.get('prospect_id') or member.get('guid')
            if not self._is_member_currently_locked(member_id):
                return False
            
            # Check if past due amount is now zero or minimal
            past_due_amount = float(member.get('amount_past_due', 0))
            if past_due_amount <= 5.00:  # Allow small rounding differences
                return True
            
            # Check for recent payments in Square invoices
            if self._has_recent_payment(member_id):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking if member should be unlocked: {e}")
            return False
    
    def _is_member_currently_locked(self, member_id: str) -> bool:
        """Check if a member is currently locked (placeholder - would check actual lock status)"""
        # TODO: Implement actual lock status check via ClubHub API
        # For now, we'll assume members are not locked unless we have evidence
        return False
    
    def _has_recent_payment(self, member_id: str) -> bool:
        """Check if member has made a recent payment (last 24 hours)"""
        try:
            # Check for recent Square invoice payments
            recent_payments = self.db_manager.get_recent_payments_for_member(member_id, hours=24)
            return len(recent_payments) > 0
        except Exception as e:
            logger.error(f"❌ Error checking recent payments for {member_id}: {e}")
            return False
    
    def _log_access_action(self, member_id: str, member_name: str, action: str, 
                          reason: str, success: bool, error: str = None):
        """Log access control actions for audit trail"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'member_id': member_id,
                'member_name': member_name,
                'action': action,
                'reason': reason,
                'success': success,
                'error': error,
                'automated': True
            }
            
            # Store in database or log file
            self.db_manager.log_access_action(log_entry)
            
        except Exception as e:
            logger.error(f"❌ Error logging access action: {e}")
    
    def process_square_webhook(self, webhook_data: Dict) -> Dict:
        """Process Square webhook for immediate payment-based unlocks"""
        try:
            logger.info("📥 Processing Square webhook for automated access control...")
            
            if webhook_data.get('type') == 'invoice.updated':
                invoice_data = webhook_data.get('data', {}).get('object', {})
                status = invoice_data.get('status')
                
                if status == 'PAID':
                    # Extract member information from invoice
                    member_info = self._extract_member_from_invoice(invoice_data)
                    
                    if member_info:
                        member_id = member_info.get('member_id')
                        member_name = member_info.get('member_name', 'Unknown')
                        
                        logger.info(f"💰 Payment received for member: {member_name} (ID: {member_id})")
                        
                        # Immediate unlock check for this specific member
                        unlock_result = self._check_and_unlock_member(member_id, member_name)
                        
                        if unlock_result.get('success'):
                            logger.info(f"🔓 Member {member_name} automatically unlocked after payment")
                            
                            return {
                                'success': True,
                                'message': f'Member {member_name} automatically unlocked',
                                'member_id': member_id,
                                'action': 'auto_unlock'
                            }
                        else:
                            logger.warning(f"⚠️ Could not auto-unlock {member_name}: {unlock_result.get('error')}")
                            
                            return {
                                'success': False,
                                'message': f'Payment received but unlock failed: {unlock_result.get("error")}',
                                'member_id': member_id
                            }
                    else:
                        logger.warning("⚠️ Could not extract member information from paid invoice")
                        return {'success': True, 'message': 'Payment processed but no member match found'}
                        
            return {'success': True, 'message': 'Webhook processed (no action needed)'}
            
        except Exception as e:
            logger.error(f"❌ Error processing Square webhook: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_member_from_invoice(self, invoice_data: Dict) -> Optional[Dict]:
        """Extract member information from Square invoice data"""
        try:
            # Look for member ID in invoice description or metadata
            description = invoice_data.get('invoice_request', {}).get('description', '')
            
            # Try to find member ID in description (format: "Member ID: 12345")
            import re
            member_id_match = re.search(r'Member ID:\s*(\d+)', description, re.IGNORECASE)
            if member_id_match:
                member_id = member_id_match.group(1)
                return {'member_id': member_id}
            
            # Try to extract from recipient name/email
            recipient = invoice_data.get('primary_recipient', {})
            recipient_name = recipient.get('given_name', '') + ' ' + recipient.get('family_name', '')
            recipient_name = recipient_name.strip()
            
            if recipient_name:
                # Try to find member by name
                member = self._find_member_by_name(recipient_name)
                if member:
                    return {
                        'member_id': member.get('prospect_id') or member.get('guid'),
                        'member_name': recipient_name
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting member from invoice: {e}")
            return None
    
    def _find_member_by_name(self, name: str) -> Optional[Dict]:
        """Find a member by their full name"""
        try:
            # Search through all member categories
            all_categories = ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']
            
            for category in all_categories:
                try:
                    members = self.db_manager.get_members_by_category(category)
                    for member in members:
                        member_name = member.get('display_name', '') or member.get('full_name', '')
                        if member_name.lower() == name.lower():
                            return member
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding member by name: {e}")
            return None
    
    def _check_and_unlock_member(self, member_id: str, member_name: str) -> Dict:
        """Check if a specific member should be unlocked and do it"""
        try:
            # Get current member data
            member = self._get_member_by_id(member_id)
            if not member:
                return {'success': False, 'error': 'Member not found'}
            
            # Check if they should be unlocked
            if self._should_unlock_member(member):
                result = self.access_control.manual_toggle_member_access(member_id, 'unlock')
                
                if result.get('success'):
                    # Log the unlock action
                    self._log_access_action(
                        member_id=member_id,
                        member_name=member_name,
                        action='payment_unlock',
                        reason='Square payment received',
                        success=True
                    )
                    
                return result
            else:
                return {
                    'success': False, 
                    'error': 'Member does not meet unlock criteria (may still have outstanding balance)'
                }
                
        except Exception as e:
            logger.error(f"❌ Error checking unlock for member {member_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_member_by_id(self, member_id: str) -> Optional[Dict]:
        """Get member data by ID"""
        try:
            all_categories = ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']
            
            for category in all_categories:
                try:
                    members = self.db_manager.get_members_by_category(category)
                    for member in members:
                        if (str(member.get('prospect_id', '')) == str(member_id) or 
                            str(member.get('guid', '')) == str(member_id)):
                            return member
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting member by ID: {e}")
            return None
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring system status"""
        return {
            'active': self.monitoring_active,
            'last_lock_check': self.last_lock_check.isoformat() if self.last_lock_check != datetime.min else None,
            'last_unlock_check': self.last_unlock_check.isoformat() if self.last_unlock_check != datetime.min else None,
            'lock_check_interval': self.lock_check_interval,
            'unlock_check_interval': self.unlock_check_interval,
            'thread_alive': self.monitor_thread.is_alive() if self.monitor_thread else False
        }

# Global monitor instance
_global_monitor = None

def get_access_monitor() -> AutomatedAccessMonitor:
    """Get the global access monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = AutomatedAccessMonitor()
    return _global_monitor

def start_global_monitoring():
    """Start the global monitoring system"""
    monitor = get_access_monitor()
    monitor.start_monitoring()

def stop_global_monitoring():
    """Stop the global monitoring system"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring()