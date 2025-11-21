#!/usr/bin/env python3

"""
SendGrid Email Sending for Collections System
This is the easiest and most reliable solution for 2025
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def send_email_sendgrid(email_content, recipient_email="FondDuLacWI@anytimefitness.com"):
    """Send email using SendGrid SMTP"""
    
    try:
        # SendGrid SMTP settings
        smtp_server = "smtp.sendgrid.net"
        smtp_port = 587
        
        # Get SendGrid credentials from environment or secrets manager
        try:
            from src.services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            sendgrid_username = secrets_manager.get_secret("sendgrid-username")
            sendgrid_password = secrets_manager.get_secret("sendgrid-password")
        except:
            # Fallback to environment variables
            sendgrid_username = os.getenv('SENDGRID_USERNAME', 'apikey')
            sendgrid_password = os.getenv('SENDGRID_PASSWORD')
        
        if not sendgrid_password:
            print("❌ SendGrid password not found!")
            print("Set SENDGRID_PASSWORD environment variable or add to secrets manager")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = "fdl.gym.bot@gmail.com"  # Your verified sender
        msg['To'] = recipient_email
        msg['Subject'] = f"Collections Referral - {datetime.now().strftime('%Y-%m-%d')}"
        
        msg.attach(MIMEText(email_content, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sendgrid_username, sendgrid_password)
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully via SendGrid!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email via SendGrid: {e}")
        return False

def setup_sendgrid():
    """Setup instructions for SendGrid"""
    
    print("🔧 SendGrid Setup Instructions")
    print("=" * 40)
    print()
    print("1. Sign up for SendGrid (free tier available):")
    print("   https://sendgrid.com/")
    print()
    print("2. Create an API key:")
    print("   - Go to Settings > API Keys")
    print("   - Create API Key with 'Mail Send' permissions")
    print("   - Copy the API key")
    print()
    print("3. Verify your sender email:")
    print("   - Go to Settings > Sender Authentication")
    print("   - Verify fdl.gym.bot@gmail.com")
    print()
    print("4. Add credentials to secrets manager:")
    print("   - sendgrid-username: 'apikey'")
    print("   - sendgrid-password: 'your-api-key'")
    print()
    print("5. Or set environment variables:")
    print("   SENDGRID_USERNAME=apikey")
    print("   SENDGRID_PASSWORD=your-api-key")

if __name__ == "__main__":
    setup_sendgrid()
