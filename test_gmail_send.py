#!/usr/bin/env python3
"""
Test Gmail Email Sending
Simple test to verify the Gmail OAuth token works for sending emails.
"""

import os
import sys
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gmail_send():
    """Test Gmail email sending capability"""
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        import base64
        from email.mime.text import MIMEText
        
        # Gmail API scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        token_file = 'gmail_token.json'
        
        if not os.path.exists(token_file):
            logger.error(f"❌ Token file not found: {token_file}")
            logger.error("Run setup_new_gmail_oauth.py first")
            return False
        
        # Load credentials
        logger.info(f"📄 Loading credentials from {token_file}")
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        logger.info(f"📅 Token expiry: {creds.expiry}")
        logger.info(f"🔄 Token valid: {creds.valid}")
        
        if not creds.valid:
            logger.error("❌ Token is not valid")
            return False
        
        # Create Gmail service
        logger.info("📧 Creating Gmail service...")
        service = build('gmail', 'v1', credentials=creds)
        
        # Create a test email
        sender_email = "fdl.gym.bot@gmail.com"
        test_recipient = "mayo.jeremy2212@gmail.com"  # Send test to yourself
        
        msg = MIMEText("✅ Gmail API test - Collections email system is working!")
        msg['From'] = sender_email
        msg['To'] = test_recipient
        msg['Subject'] = f"Gmail API Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Encode and send
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        
        logger.info(f"📤 Sending test email to {test_recipient}...")
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        logger.info("✅ Test email sent successfully!")
        logger.info("📧 Check your inbox to confirm delivery")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Gmail send: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🧪 Gmail Email Send Test")
    print("=" * 30)
    
    success = test_gmail_send()
    
    if success:
        print("\n✅ Gmail email sending works!")
        print("📧 Collections emails should work properly now.")
    else:
        print("\n❌ Gmail email sending failed!")
        print("🔧 You may need to re-run the OAuth setup.")
    
    return success

if __name__ == "__main__":
    main()