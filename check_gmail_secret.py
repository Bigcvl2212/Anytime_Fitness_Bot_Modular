#!/usr/bin/env python3

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def check_gmail_secret():
    """Check what's stored in the Gmail secret"""
    
    print("🔍 Checking Gmail Secret in Secrets Manager")
    print("=" * 50)
    
    try:
        secrets_manager = SecureSecretsManager()
        
        # Check if gmail-password exists
        gmail_password = secrets_manager.get_secret("gmail-password")
        
        if gmail_password:
            print(f"✅ Gmail password found: {gmail_password}")
            print(f"✅ Password length: {len(gmail_password)}")
            print(f"✅ Password type: {type(gmail_password)}")
        else:
            print("❌ Gmail password not found in secrets manager")
            
        # List all available secrets
        print("\n📋 Available secrets:")
        try:
            # This might not work depending on the secrets manager implementation
            all_secrets = secrets_manager.list_secrets()
            for secret in all_secrets:
                print(f"  - {secret}")
        except:
            print("  (Cannot list secrets - method not available)")
            
    except Exception as e:
        print(f"❌ Error checking secrets: {e}")

if __name__ == "__main__":
    check_gmail_secret()
