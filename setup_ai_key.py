#!/usr/bin/env python3
"""
Setup script for configuring Claude AI API key
Run this script to configure the Claude API key for AI services
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def setup_claude_api_key():
    """Setup Claude API key in Google Secret Manager"""
    print("🤖 Setting up Claude AI API key...")

    # Initialize secrets manager
    try:
        secrets_manager = SecureSecretsManager()
        if not secrets_manager.client:
            print("❌ Could not initialize Google Secret Manager client")
            print("Make sure you have Google Cloud credentials configured")
            return False
    except Exception as e:
        print(f"❌ Error initializing secrets manager: {e}")
        return False

    # Get API key from user
    api_key = input("Enter your Claude API key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return False

    if not api_key.startswith('sk-ant-'):
        print("⚠️ Warning: Claude API keys usually start with 'sk-ant-'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False

    # Store the key
    try:
        success = secrets_manager.set_secret('claude-api-key', api_key)
        if success:
            print("✅ Claude API key configured successfully!")
            print("🤖 AI services will now be available when you restart the application")
            return True
        else:
            print("❌ Failed to store Claude API key")
            return False
    except Exception as e:
        print(f"❌ Error storing API key: {e}")
        return False

if __name__ == "__main__":
    print("Claude AI API Key Setup")
    print("=" * 30)
    success = setup_claude_api_key()
    if not success:
        sys.exit(1)