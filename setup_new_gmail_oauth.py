#!/usr/bin/env python3
"""
Gmail OAuth2 Setup Script
This will authorize the Gmail API and create a new token file.
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_gmail_oauth():
    """Set up Gmail OAuth2 authorization"""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        # Gmail API scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        # Credentials file path
        credentials_path = os.path.join('config', 'google_oauth_credentials.json')
        token_file = 'gmail_token.json'
        
        if not os.path.exists(credentials_path):
            logger.error(f"❌ Credentials file not found: {credentials_path}")
            return False
        
        logger.info("🔐 Starting OAuth2 authorization flow...")
        logger.info("📋 Required scopes: Gmail Send")
        logger.info("🌐 This will open your browser for authorization...")
        
        # Create flow from client secrets
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        
        # Run the OAuth flow
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        logger.info(f"💾 Saving credentials to {token_file}")
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        
        # Test the credentials by building the service
        logger.info("🧪 Testing Gmail API connection...")
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"✅ Gmail API authorized successfully!")
        logger.info(f"📧 Connected as: {profile.get('emailAddress', 'Unknown')}")
        logger.info(f"📅 Token expires: {creds.expiry}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing required modules: {e}")
        logger.error("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
        return False
    except Exception as e:
        logger.error(f"❌ Error setting up Gmail OAuth: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🔧 Gmail OAuth2 Setup")
    print("=" * 30)
    print()
    print("This script will:")
    print("1. Open your browser for Gmail authorization")
    print("2. Create a new gmail_token.json file")
    print("3. Test the Gmail API connection")
    print()
    
    input("Press Enter to continue...")
    print()
    
    success = setup_gmail_oauth()
    
    if success:
        print()
        print("✅ Gmail OAuth2 setup completed successfully!")
        print("📧 The collections email functionality should now work.")
        print(f"💾 Token saved to: gmail_token.json")
    else:
        print()
        print("❌ Gmail OAuth2 setup failed!")
        print("🔍 Check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()