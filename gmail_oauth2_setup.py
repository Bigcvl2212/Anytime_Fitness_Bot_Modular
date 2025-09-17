#!/usr/bin/env python3

"""
Gmail OAuth2 Setup for Collections Email
This provides an alternative to App Passwords using OAuth2
"""

import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_oauth2():
    """Test Gmail OAuth2 authentication"""
    
    print("🔧 Gmail OAuth2 Setup for Collections Email")
    print("=" * 50)
    
    print("Since App Passwords require 2-Step Verification, here are your options:")
    print()
    print("OPTION 1: Enable 2-Step Verification + App Password")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Step Verification")
    print("3. Go to App Passwords → Generate new password")
    print("4. Use the 16-character App Password")
    print()
    print("OPTION 2: Use Alternative Email Service")
    print("1. Use a different SMTP provider (SendGrid, Mailgun, etc.)")
    print("2. Or use a different Gmail account that has 2FA enabled")
    print()
    print("OPTION 3: Use Gmail OAuth2 (More Complex)")
    print("1. Requires Google Cloud Console setup")
    print("2. Generate OAuth2 credentials")
    print("3. More secure but more setup required")
    print()
    print("RECOMMENDATION: Enable 2-Step Verification and use App Password")
    print("This is the simplest and most secure option.")

def test_alternative_smtp():
    """Test with alternative SMTP settings"""
    
    print("\n🔧 Alternative Gmail SMTP Settings")
    print("=" * 40)
    
    # Try different Gmail SMTP settings
    smtp_configs = [
        {
            "name": "Gmail SMTP (TLS)",
            "server": "smtp.gmail.com",
            "port": 587,
            "security": "TLS"
        },
        {
            "name": "Gmail SMTP (SSL)",
            "server": "smtp.gmail.com", 
            "port": 465,
            "security": "SSL"
        },
        {
            "name": "Gmail SMTP (Alternative)",
            "server": "smtp.gmail.com",
            "port": 25,
            "security": "TLS"
        }
    ]
    
    for config in smtp_configs:
        print(f"📧 {config['name']}: {config['server']}:{config['port']} ({config['security']})")
    
    print("\n💡 Try enabling 2-Step Verification first, then App Passwords will appear!")

if __name__ == "__main__":
    test_gmail_oauth2()
    test_alternative_smtp()
