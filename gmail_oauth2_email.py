#!/usr/bin/env python3

"""
Gmail OAuth2 Email Sending for Collections System
This implements OAuth2 authentication for Gmail SMTP in 2025
"""

import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime

def send_email_oauth2(email_content, recipient_email="FondDuLacWI@anytimefitness.com"):
    """Send email using Gmail OAuth2 authentication"""
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        # Gmail API scopes
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        
        # Check if we have existing credentials
        creds = None
        if os.path.exists('gmail_token.json'):
            creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
        
        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # You need to download credentials.json from Google Cloud Console
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('gmail_token.json', 'w') as token:
                token.write(creds.to_json())
        
        # Create Gmail API service
        service = build('gmail', 'v1', credentials=creds)
        
        # Create message
        message = MIMEMultipart()
        message['From'] = "fdl.gym.bot@gmail.com"
        message['To'] = recipient_email
        message['Subject'] = f"Collections Referral - {datetime.now().strftime('%Y-%m-%d')}"
        
        message.attach(MIMEText(email_content, 'plain'))
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Send email
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print("✅ Email sent successfully via Gmail OAuth2!")
        return True
        
    except ImportError:
        print("❌ Gmail OAuth2 libraries not installed")
        print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
    except FileNotFoundError:
        print("❌ credentials.json not found")
        print("Download from: https://console.cloud.google.com/apis/credentials")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def setup_gmail_oauth2():
    """Setup instructions for Gmail OAuth2"""
    
    print("🔧 Gmail OAuth2 Setup Instructions")
    print("=" * 50)
    print()
    print("1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    print()
    print("2. Create a new project or select existing")
    print()
    print("3. Enable Gmail API:")
    print("   - Go to APIs & Services > Library")
    print("   - Search for 'Gmail API' and enable it")
    print()
    print("4. Create OAuth2 credentials:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Choose 'Desktop application'")
    print("   - Download the JSON file as 'credentials.json'")
    print()
    print("5. Install required libraries:")
    print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    print()
    print("6. Run this script to authenticate and send emails")

if __name__ == "__main__":
    setup_gmail_oauth2()
