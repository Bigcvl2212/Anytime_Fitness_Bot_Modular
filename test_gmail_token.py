#!/usr/bin/env python3
"""
Quick Gmail Token Test & Refresh
This script will test the current Gmail token and refresh it if needed.
"""

import os
import sys
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_and_refresh_gmail_token():
    """Test current Gmail token and refresh if needed"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        # Gmail API scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        # File paths
        token_file = 'gmail_token.json'
        
        if not os.path.exists(token_file):
            logger.error(f"❌ Token file not found: {token_file}")
            return False
        
        # Load existing token
        logger.info(f"📄 Loading token from {token_file}")
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        logger.info(f"📅 Token expiry: {creds.expiry}")
        logger.info(f"🔄 Token valid: {creds.valid}")
        logger.info(f"🔄 Token expired: {creds.expired}")
        logger.info(f"🔄 Has refresh token: {bool(creds.refresh_token)}")
        
        # Check if token needs refresh
        if creds.expired and creds.refresh_token:
            logger.info("🔄 Token is expired, refreshing...")
            creds.refresh(Request())
            logger.info("✅ Token refreshed successfully!")
            
            # Save refreshed token
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
            logger.info("💾 Refreshed token saved")
            
            # Load the refreshed token to verify
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            logger.info(f"📅 New token expiry: {creds.expiry}")
        
        # Test Gmail API connection
        logger.info("🧪 Testing Gmail API connection...")
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile to test
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"✅ Gmail API connection successful!")
        logger.info(f"📧 Connected as: {profile.get('emailAddress', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Gmail token: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🔧 Gmail Token Test & Refresh")
    print("=" * 40)
    
    success = test_and_refresh_gmail_token()
    
    if success:
        print("\n✅ Gmail token is working properly!")
        print("📧 Collections emails should work now.")
    else:
        print("\n❌ Gmail token test failed!")
        print("🔍 You may need to re-authorize the Gmail app.")
    
    return success

if __name__ == "__main__":
    main()