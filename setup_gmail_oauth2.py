#!/usr/bin/env python3

"""
Setup Gmail OAuth2 for Collections Email
This will guide you through setting up Gmail OAuth2 authentication
"""

def setup_gmail_oauth2():
    """Setup Gmail OAuth2 authentication"""
    
    print("🔧 Gmail OAuth2 Setup for Collections Email")
    print("=" * 50)
    print()
    print("STEP 1: Download OAuth2 Credentials")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your existing Gym Bot project")
    print("3. Go to: APIs & Services > Credentials")
    print("4. Click 'Create Credentials' > 'OAuth client ID'")
    print("5. Choose 'Desktop application'")
    print("6. Download the JSON file")
    print("7. Rename it to 'credentials.json' and place in project root")
    print()
    print("STEP 2: Enable Gmail API")
    print("1. Go to: APIs & Services > Library")
    print("2. Search for 'Gmail API'")
    print("3. Click on it and press 'Enable'")
    print()
    print("STEP 3: Test Authentication")
    print("Run: python test_gmail_oauth2.py")
    print()
    print("Once setup is complete, the collections system will send real emails!")

def test_gmail_oauth2():
    """Test Gmail OAuth2 authentication"""
    
    print("🧪 Testing Gmail OAuth2 Authentication")
    print("=" * 40)
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        import os
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        if not os.path.exists('credentials.json'):
            print("❌ credentials.json not found!")
            print("Please download OAuth2 credentials from Google Cloud Console")
            return False
        
        creds = None
        token_file = 'gmail_token.json'
        
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        # Test Gmail API
        service = build('gmail', 'v1', credentials=creds)
        
        # Get user profile to test connection
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail OAuth2 working! Connected to: {profile.get('emailAddress')}")
        return True
        
    except Exception as e:
        print(f"❌ Gmail OAuth2 test failed: {e}")
        return False

if __name__ == "__main__":
    setup_gmail_oauth2()
    print()
    test_gmail_oauth2()
