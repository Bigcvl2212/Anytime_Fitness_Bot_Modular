#!/usr/bin/env python3
"""
Quick Gmail OAuth2 Token Refresh Script
Fixes the expired Gmail API token for collections emails.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_gmail_token():
    """Refresh the expired Gmail OAuth2 token"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Gmail API scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        # File paths
        token_file = 'gmail_token.json'
        credentials_path = os.path.join('config', 'google_oauth_credentials.json')
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(token_file):
            logger.info(f"📄 Loading existing token from {token_file}")
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            logger.info(f"📅 Token expiry: {creds.expiry}")
            logger.info(f"🔄 Token valid: {creds.valid}")
            logger.info(f"🔄 Has refresh token: {bool(creds.refresh_token)}")
        
        # If no valid credentials, refresh or get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing expired token...")
                try:
                    creds.refresh(Request())
                    logger.info("✅ Token refreshed successfully!")
                except Exception as refresh_error:
                    logger.error(f"❌ Token refresh failed: {refresh_error}")
                    logger.info("🔄 Getting new authorization...")
                    creds = None
            
            if not creds or not creds.valid:
                logger.info("🔐 Starting OAuth2 flow for new token...")
                if not os.path.exists(credentials_path):
                    logger.error(f"❌ Credentials file not found: {credentials_path}")
                    logger.error("Download OAuth2 credentials from Google Cloud Console")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("✅ New token obtained!")
            
            # Save credentials for next time
            logger.info(f"💾 Saving token to {token_file}")
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Test the token by creating a service
        logger.info("🧪 Testing Gmail API connection...")
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile to test
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"✅ Gmail API connection successful!")
        logger.info(f"📧 Connected as: {profile.get('emailAddress', 'Unknown')}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing required modules: {e}")
        logger.error("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        logger.error(f"❌ Error refreshing Gmail token: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🔧 Gmail OAuth2 Token Refresh Tool")
    print("=" * 50)
    
    success = refresh_gmail_token()
    
    if success:
        print("✅ Gmail OAuth2 token refresh completed successfully!")
        print("📧 Collections emails should now work properly.")
    else:
        print("❌ Gmail OAuth2 token refresh failed!")
        print("🔍 Check the logs above for details.")
    
    return success

if __name__ == "__main__":
    main()