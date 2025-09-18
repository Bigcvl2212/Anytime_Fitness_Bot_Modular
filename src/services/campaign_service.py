"""
Campaign Service - Handles campaign management operations
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .database_manager import DatabaseManager
import asyncio
import threading
import time

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, database_manager: DatabaseManager):
        self.db = database_manager
        self._active_campaigns = {}  # Track active campaign threads
    
    def get_campaign_status(self, category: str) -> Dict[str, Any]:
        """Get campaign status for a category"""
        try:
            campaign = self.db.get_campaign_by_category(category)
            
            if not campaign:
                return {
                    'status': 'none',
                    'progress': 0,
                    'total_recipients': 0,
                    'sent_count': 0,
                    'can_continue': False
                }
            
            progress = self.db.get_campaign_progress(campaign['id'])
            
            return {
                'status': campaign['status'],
                'campaign_id': campaign['id'],
                'name': campaign['name'],
                'progress': progress['percentage'],
                'total_recipients': progress['total'],
                'sent_count': progress['sent'],
                'delivered_count': progress['delivered'],
                'failed_count': progress['failed'],
                'current_position': campaign.get('current_position', 0),
                'can_continue': campaign['status'] in ['paused', 'draft'] and progress['total'] > 0,
                'created_at': campaign['created_at'],
                'started_at': campaign.get('started_at'),
                'paused_at': campaign.get('paused_at'),
                'completed_at': campaign.get('completed_at')
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign status for {category}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def create_campaign(self, campaign_data: Dict[str, Any], recipients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new campaign with recipients"""
        try:
            # Add recipient count to campaign data
            campaign_data['total_recipients'] = len(recipients)
            
            # Create the campaign
            campaign_id = self.db.create_campaign(campaign_data)
            if not campaign_id:
                return {'status': 'error', 'message': 'Failed to create campaign'}
            
            # Add recipients
            if recipients:
                success = self.db.add_campaign_recipients(campaign_id, recipients)
                if not success:
                    logger.error(f"Failed to add recipients to campaign {campaign_id}")
            
            return {
                'status': 'success',
                'campaign_id': campaign_id,
                'message': f'Campaign created with {len(recipients)} recipients'
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def start_campaign(self, campaign_id: int, continue_from_position: bool = False) -> Dict[str, Any]:
        """Start or resume a campaign"""
        try:
            campaign = self.db.get_campaign_by_id(campaign_id)
            if not campaign:
                return {'status': 'error', 'message': 'Campaign not found'}
            
            # Update campaign status to running
            update_data = {'status': 'running'}
            if not continue_from_position:
                update_data['current_position'] = 0
            
            success = self.db.update_campaign_status(campaign_id, 'running', **update_data)
            if not success:
                return {'status': 'error', 'message': 'Failed to update campaign status'}
            
            # Start campaign execution in background thread
            self._start_campaign_thread(campaign_id, continue_from_position)
            
            return {
                'status': 'success',
                'message': 'Campaign started successfully',
                'campaign_id': campaign_id
            }
            
        except Exception as e:
            logger.error(f"Error starting campaign {campaign_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def pause_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Pause a running campaign"""
        try:
            # Update campaign status
            success = self.db.update_campaign_status(campaign_id, 'paused')
            if not success:
                return {'status': 'error', 'message': 'Failed to update campaign status'}
            
            # Stop the campaign thread if running
            if campaign_id in self._active_campaigns:
                self._active_campaigns[campaign_id] = False
            
            return {
                'status': 'success',
                'message': 'Campaign paused successfully'
            }
            
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def resume_campaign(self, campaign_id: int) -> Dict[str, Any]:
        """Resume a paused campaign"""
        try:
            campaign = self.db.get_campaign_by_id(campaign_id)
            if not campaign:
                return {'status': 'error', 'message': 'Campaign not found'}
            
            if campaign['status'] != 'paused':
                return {'status': 'error', 'message': 'Campaign is not paused'}
            
            # Update status and resume from current position
            success = self.db.update_campaign_status(campaign_id, 'running')
            if not success:
                return {'status': 'error', 'message': 'Failed to update campaign status'}
            
            # Start campaign thread from current position
            self._start_campaign_thread(campaign_id, continue_from_position=True)
            
            return {
                'status': 'success',
                'message': 'Campaign resumed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error resuming campaign {campaign_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_campaign_progress(self, campaign_id: int) -> Dict[str, Any]:
        """Get real-time campaign progress"""
        try:
            progress = self.db.get_campaign_progress(campaign_id)
            campaign = self.db.get_campaign_by_id(campaign_id)
            
            if campaign:
                progress.update({
                    'status': campaign['status'],
                    'current_position': campaign.get('current_position', 0),
                    'is_running': campaign_id in self._active_campaigns and self._active_campaigns[campaign_id]
                })
            
            return progress
            
        except Exception as e:
            logger.error(f"Error getting campaign progress for {campaign_id}: {e}")
            return {'percentage': 0, 'total': 0, 'sent': 0, 'delivered': 0, 'failed': 0}
    
    def _start_campaign_thread(self, campaign_id: int, continue_from_position: bool = False):
        """Start campaign execution in background thread"""
        try:
            # Mark campaign as active
            self._active_campaigns[campaign_id] = True
            
            # Start background thread
            thread = threading.Thread(
                target=self._execute_campaign,
                args=(campaign_id, continue_from_position),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting campaign thread for {campaign_id}: {e}")
    
    def _execute_campaign(self, campaign_id: int, continue_from_position: bool = False):
        """Execute campaign sending (mock implementation)"""
        try:
            campaign = self.db.get_campaign_by_id(campaign_id)
            if not campaign:
                return
            
            # Get recipients that haven't been sent yet
            current_position = campaign.get('current_position', 0) if continue_from_position else 0
            
            # This is a mock implementation - replace with actual SMS/email sending logic
            query = """
                SELECT * FROM campaign_recipients 
                WHERE campaign_id = %s AND status = 'pending'
                ORDER BY id
                LIMIT %s OFFSET %s
            """ if self.db.db_type == 'postgresql' else """
                SELECT * FROM campaign_recipients 
                WHERE campaign_id = ? AND status = 'pending'
                ORDER BY id
                LIMIT ? OFFSET ?
            """
            
            batch_size = 10  # Process in batches
            offset = current_position
            
            while self._active_campaigns.get(campaign_id, False):
                # Get next batch of recipients
                recipients = self.db.execute_query(query, (campaign_id, batch_size, offset))
                
                if not recipients:
                    # Campaign complete
                    self.db.update_campaign_status(campaign_id, 'completed')
                    break
                
                for recipient in recipients:
                    if not self._active_campaigns.get(campaign_id, False):
                        # Campaign was paused
                        break
                    
                    # Mock sending - replace with actual API calls
                    success = self._send_message(recipient, campaign)
                    
                    if success:
                        self.db.update_recipient_status(campaign_id, recipient['member_id'], 'sent')
                    else:
                        self.db.update_recipient_status(campaign_id, recipient['member_id'], 'failed', 'Send failed')
                    
                    # Update campaign position
                    offset += 1
                    self.db.update_campaign_status(campaign_id, 'running', current_position=offset)
                    
                    # Add delay between messages to avoid rate limiting
                    time.sleep(0.5)
                
                if not self._active_campaigns.get(campaign_id, False):
                    # Campaign was paused
                    break
            
            # Clean up
            if campaign_id in self._active_campaigns:
                del self._active_campaigns[campaign_id]
                
        except Exception as e:
            logger.error(f"Error executing campaign {campaign_id}: {e}")
            self.db.update_campaign_status(campaign_id, 'failed')
    
    def _send_message(self, recipient: Dict[str, Any], campaign: Dict[str, Any]) -> bool:
        """Mock message sending - replace with actual SMS/email API calls"""
        try:
            message_type = campaign.get('message_type', 'sms')
            
            if message_type == 'sms':
                # Mock SMS sending
                phone = recipient.get('member_phone')
                if not phone:
                    return False
                
                # Replace with actual SMS API call
                logger.info(f"Sending SMS to {phone}: {campaign['message'][:50]}...")
                return True
                
            elif message_type == 'email':
                # Mock email sending  
                email = recipient.get('member_email')
                if not email:
                    return False
                
                # Replace with actual email API call
                logger.info(f"Sending email to {email}: {campaign.get('email_subject', 'No Subject')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending message to {recipient.get('member_name')}: {e}")
            return False
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get all campaign templates"""
        return self.db.get_campaign_templates()
    
    def save_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new campaign template"""
        try:
            template_id = self.db.save_campaign_template(template_data)
            if template_id:
                return {
                    'status': 'success',
                    'template_id': template_id,
                    'message': 'Template saved successfully'
                }
            else:
                return {'status': 'error', 'message': 'Failed to save template'}
                
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return {'status': 'error', 'message': str(e)}