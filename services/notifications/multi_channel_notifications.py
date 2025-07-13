"""
Enhanced Multi-Channel Notifications - IMPROVED FROM EXPERIMENTAL CODE
Uses the experimental multi-channel patterns from worker.py but enhanced with verified patterns.
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...config.constants import GCP_PROJECT_ID, TWILIO_SID_SECRET, TWILIO_TOKEN_SECRET, TWILIO_FROM_NUMBER_SECRET
from ...utils.debug_helpers import debug_page_state


class EnhancedMultiChannelNotifications:
    """
    Enhanced multi-channel notification service with SMS, Email, and ClubOS integration.
    Based on experimental code from worker.py but enhanced with verified patterns.
    """
    
    def __init__(self, gemini_model=None):
        """Initialize multi-channel notification service"""
        self.gemini_model = gemini_model
        self.twilio_client = None
        self.gmail_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all notification services"""
        try:
            # Initialize Twilio SMS
            self._initialize_twilio()
            
            # Initialize Gmail service
            self._initialize_gmail()
            
            print("✅ Multi-channel notification services initialized")
            
        except Exception as e:
            print(f"❌ Error initializing notification services: {e}")
    
    def _initialize_twilio(self):
        """Initialize Twilio SMS client"""
        try:
            from twilio.rest import Client
            from google.cloud import secretmanager
            
            # Get Twilio credentials from secret manager
            client = secretmanager.SecretManagerServiceClient()
            
            # Get Twilio SID
            sid_name = f"projects/{GCP_PROJECT_ID}/secrets/{TWILIO_SID_SECRET}/versions/latest"
            sid_response = client.access_secret_version(request={"name": sid_name})
            twilio_sid = sid_response.payload.data.decode("UTF-8")
            
            # Get Twilio token
            token_name = f"projects/{GCP_PROJECT_ID}/secrets/{TWILIO_TOKEN_SECRET}/versions/latest"
            token_response = client.access_secret_version(request={"name": token_name})
            twilio_token = token_response.payload.data.decode("UTF-8")
            
            # Get Twilio from number
            from_number_name = f"projects/{GCP_PROJECT_ID}/secrets/{TWILIO_FROM_NUMBER_SECRET}/versions/latest"
            from_number_response = client.access_secret_version(request={"name": from_number_name})
            twilio_from_number = from_number_response.payload.data.decode("UTF-8")
            
            # Initialize Twilio client
            self.twilio_client = Client(twilio_sid, twilio_token)
            self.twilio_from_number = twilio_from_number
            
            print("✅ Twilio SMS service initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Twilio: {e}")
            self.twilio_client = None
    
    def _initialize_gmail(self):
        """Initialize Gmail service for email notifications"""
        try:
            from google.cloud import secretmanager
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            # Get Gmail credentials from secret manager
            client = secretmanager.SecretManagerServiceClient()
            
            # Get Gmail credentials
            creds_name = f"projects/{GCP_PROJECT_ID}/secrets/bot-gmail-credentials/versions/latest"
            creds_response = client.access_secret_version(request={"name": creds_name})
            bot_creds_json = creds_response.payload.data.decode("UTF-8")
            
            # Get Gmail token
            token_name = f"projects/{GCP_PROJECT_ID}/secrets/bot-gmail-token/versions/latest"
            token_response = client.access_secret_version(request={"name": token_name})
            bot_token_json = token_response.payload.data.decode("UTF-8")
            
            # Initialize Gmail service
            bot_creds = Credentials.from_authorized_user_info(json.loads(bot_token_json))
            self.gmail_service = build('gmail', 'v1', credentials=bot_creds)
            
            print("✅ Gmail service initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Gmail: {e}")
            self.gmail_service = None
    
    def send_sms_notification(self, member_name: str, message: str, phone_number: str) -> bool:
        """
        Send SMS notification using Twilio.
        
        IMPROVED FROM EXPERIMENTAL CODE IN WORKER.PY
        """
        print(f"📱 Sending SMS notification to {member_name}...")
        
        if not self.twilio_client:
            print("   ❌ Twilio client not available")
            return False
        
        try:
            # Create SMS message
            message_body = f"Anytime Fitness FDL: {message}"
            
            # Send SMS via Twilio
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_from_number,
                to=phone_number
            )
            
            print(f"   ✅ SMS sent successfully to {member_name}")
            print(f"   📊 Message SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error sending SMS to {member_name}: {e}")
            return False
    
    def send_email_notification(self, member_name: str, subject: str, message: str, 
                              email_address: str) -> bool:
        """
        Send email notification using Gmail API.
        
        IMPROVED FROM EXPERIMENTAL CODE IN WORKER.PY
        """
        print(f"📧 Sending email notification to {member_name}...")
        
        if not self.gmail_service:
            print("   ❌ Gmail service not available")
            return False
        
        try:
            from email.mime.text import MIMEText
            import base64
            
            # Create email message
            email_message = MIMEText(message)
            email_message['to'] = email_address
            email_message['subject'] = subject
            
            # Encode message for Gmail API
            raw_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode('utf-8')
            
            # Send email via Gmail API
            message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"   ✅ Email sent successfully to {member_name}")
            print(f"   📊 Message ID: {message['id']}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error sending email to {member_name}: {e}")
            return False
    
    def send_clubos_notification(self, driver, member_name: str, subject: str, 
                                message: str) -> bool:
        """
        Send notification via ClubOS messaging system.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"💬 Sending ClubOS notification to {member_name}...")
        
        try:
            from ...services.clubos.messaging import send_clubos_message
            
            # Send message via ClubOS
            success = send_clubos_message(
                driver=driver,
                member_name=member_name,
                subject=subject,
                body=message
            )
            
            if success:
                print(f"   ✅ ClubOS message sent successfully to {member_name}")
            else:
                print(f"   ❌ Failed to send ClubOS message to {member_name}")
            
            return success
            
        except Exception as e:
            print(f"   ❌ Error sending ClubOS message to {member_name}: {e}")
            return False
    
    def send_multi_channel_notification(self, member_data: Dict[str, Any], 
                                      notification_type: str, 
                                      driver=None) -> Dict[str, bool]:
        """
        Send notification across multiple channels based on member preferences.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"📢 Sending multi-channel notification to {member_data.get('name', 'Unknown')}...")
        
        member_name = member_data.get('name', 'Unknown')
        email = member_data.get('email', '')
        phone = member_data.get('phone', '')
        
        # Generate notification content based on type
        notification_content = self._generate_notification_content(notification_type, member_data)
        
        results = {
            'sms': False,
            'email': False,
            'clubos': False
        }
        
        # Send SMS if phone number available
        if phone and self.twilio_client:
            results['sms'] = self.send_sms_notification(
                member_name, 
                notification_content['sms_message'], 
                phone
            )
        
        # Send email if email address available
        if email and self.gmail_service:
            results['email'] = self.send_email_notification(
                member_name,
                notification_content['email_subject'],
                notification_content['email_message'],
                email
            )
        
        # Send ClubOS message if driver available
        if driver:
            results['clubos'] = self.send_clubos_notification(
                driver,
                member_name,
                notification_content['clubos_subject'],
                notification_content['clubos_message']
            )
        
        # Log results
        successful_channels = [channel for channel, success in results.items() if success]
        print(f"   📊 Notification results: {successful_channels}")
        
        return results
    
    def _generate_notification_content(self, notification_type: str, 
                                    member_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate appropriate notification content based on type.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        member_name = member_data.get('name', 'Unknown')
        
        if notification_type == "payment_reminder":
            return {
                'sms_message': f"Hi {member_name}, your gym payment is due. Please call (920) 921-4800 to discuss payment options.",
                'email_subject': "Anytime Fitness - Payment Reminder",
                'email_message': f"""Hi {member_name},

This is a friendly reminder that your gym payment is due. 

Please call us at (920) 921-4800 or visit the gym to discuss payment options. We're here to help!

Best regards,
Anytime Fitness Fond du Lac""",
                'clubos_subject': "Payment Reminder",
                'clubos_message': f"Hi {member_name}, your gym payment is due. Please call (920) 921-4800 to discuss payment options."
            }
        
        elif notification_type == "training_reminder":
            return {
                'sms_message': f"Hi {member_name}, your training session is scheduled. Please call (920) 921-4800 if you need to reschedule.",
                'email_subject': "Anytime Fitness - Training Session Reminder",
                'email_message': f"""Hi {member_name},

This is a reminder about your upcoming training session.

Please call us at (920) 921-4800 if you need to reschedule or have any questions.

Best regards,
Anytime Fitness Fond du Lac""",
                'clubos_subject': "Training Session Reminder",
                'clubos_message': f"Hi {member_name}, your training session is scheduled. Please call (920) 921-4800 if you need to reschedule."
            }
        
        elif notification_type == "overdue_payment":
            return {
                'sms_message': f"Hi {member_name}, your account is overdue. Please call (920) 921-4800 immediately to avoid service interruption.",
                'email_subject': "URGENT: Anytime Fitness - Overdue Payment",
                'email_message': f"""Hi {member_name},

Your account is currently overdue. To avoid service interruption, please call us immediately at (920) 921-4800 to discuss payment options.

We're here to help resolve this quickly.

Best regards,
Anytime Fitness Fond du Lac""",
                'clubos_subject': "URGENT: Overdue Payment",
                'clubos_message': f"Hi {member_name}, your account is overdue. Please call (920) 921-4800 immediately to avoid service interruption."
            }
        
        else:  # General notification
            return {
                'sms_message': f"Hi {member_name}, you have a message from Anytime Fitness. Please call (920) 921-4800 for details.",
                'email_subject': "Anytime Fitness - Important Message",
                'email_message': f"""Hi {member_name},

You have an important message from Anytime Fitness.

Please call us at (920) 921-4800 or visit the gym for details.

Best regards,
Anytime Fitness Fond du Lac""",
                'clubos_subject': "Important Message",
                'clubos_message': f"Hi {member_name}, you have an important message. Please call (920) 921-4800 for details."
            }
    
    def send_bulk_notifications(self, member_list: List[Dict[str, Any]], 
                               notification_type: str, 
                               driver=None) -> Dict[str, Any]:
        """
        Send bulk notifications to multiple members.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"📢 Sending bulk {notification_type} notifications to {len(member_list)} members...")
        
        results = {
            'total_members': len(member_list),
            'successful_sms': 0,
            'successful_email': 0,
            'successful_clubos': 0,
            'failed': 0,
            'details': []
        }
        
        for i, member_data in enumerate(member_list, 1):
            member_name = member_data.get('name', 'Unknown')
            print(f"   [{i}/{len(member_list)}] Processing {member_name}...")
            
            try:
                # Send multi-channel notification
                notification_results = self.send_multi_channel_notification(
                    member_data, notification_type, driver
                )
                
                # Track results
                if notification_results['sms']:
                    results['successful_sms'] += 1
                if notification_results['email']:
                    results['successful_email'] += 1
                if notification_results['clubos']:
                    results['successful_clubos'] += 1
                
                # Check if any channel succeeded
                if any(notification_results.values()):
                    results['details'].append({
                        'member_name': member_name,
                        'status': 'success',
                        'channels': notification_results
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'member_name': member_name,
                        'status': 'failed',
                        'channels': notification_results
                    })
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error processing {member_name}: {e}")
                results['failed'] += 1
                results['details'].append({
                    'member_name': member_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        print(f"   📊 Bulk notification complete:")
        print(f"      - SMS: {results['successful_sms']}")
        print(f"      - Email: {results['successful_email']}")
        print(f"      - ClubOS: {results['successful_clubos']}")
        print(f"      - Failed: {results['failed']}")
        
        return results


# Convenience functions for backward compatibility
def send_sms_notification(member_name: str, message: str, phone_number: str) -> bool:
    """Send SMS notification"""
    service = EnhancedMultiChannelNotifications()
    return service.send_sms_notification(member_name, message, phone_number)


def send_email_notification(member_name: str, subject: str, message: str, email_address: str) -> bool:
    """Send email notification"""
    service = EnhancedMultiChannelNotifications()
    return service.send_email_notification(member_name, subject, message, email_address)


def send_multi_channel_notification(member_data: Dict[str, Any], notification_type: str, driver=None) -> Dict[str, bool]:
    """Send multi-channel notification"""
    service = EnhancedMultiChannelNotifications()
    return service.send_multi_channel_notification(member_data, notification_type, driver)


def send_bulk_notifications(member_list: List[Dict[str, Any]], notification_type: str, driver=None) -> Dict[str, Any]:
    """Send bulk notifications"""
    service = EnhancedMultiChannelNotifications()
    return service.send_bulk_notifications(member_list, notification_type, driver) 