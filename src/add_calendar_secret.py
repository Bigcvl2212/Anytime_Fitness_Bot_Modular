#!/usr/bin/env python3
"""
Script to add the calendar sync URL to SecureSecretsManager
Run this once to store the URL securely, then delete this file.
"""

import sys
import os
sys.path.append('src')

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def add_calendar_secret():
    """Add calendar sync URL to SecureSecretsManager"""
    
    # The calendar sync URL that was previously hardcoded
    calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
    
    try:
        secrets_manager = SecureSecretsManager()
        
        # Store the calendar sync URL
        success = secrets_manager.set_secret('clubos-calendar-sync-url', calendar_sync_url)
        
        if success:
            print("✅ Calendar sync URL successfully stored in SecureSecretsManager")
            print("🔐 Secret name: 'clubos-calendar-sync-url'")
            print("⚠️ You should delete this script file now for security")
        else:
            print("❌ Failed to store calendar sync URL")
            
    except Exception as e:
        print(f"❌ Error storing calendar sync URL: {e}")

if __name__ == "__main__":
    print("🔐 Adding calendar sync URL to SecureSecretsManager...")
    add_calendar_secret()