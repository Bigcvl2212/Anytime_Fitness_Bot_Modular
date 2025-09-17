#!/usr/bin/env python3

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def check_gmail_password():
    """Check what Gmail password is stored in secrets manager"""
    
    print("🔍 Checking Gmail Password in Secrets Manager")
    print("=" * 50)
    
    try:
        secrets_manager = SecureSecretsManager()
        password = secrets_manager.get_secret("gmail-password")
        
        if password:
            print(f"✅ Gmail password found: {password}")
            print(f"✅ Password length: {len(password)}")
            print(f"✅ Password type: {type(password)}")
            
            # Check if it looks like the expected password
            if password == "Anytime1#":
                print("✅ Password matches expected value")
            else:
                print("⚠️ Password doesn't match expected 'Anytime1#'")
                print("💡 You may need to update the secret in Google Cloud Console")
        else:
            print("❌ Gmail password not found in secrets manager")
            print("💡 You need to add 'gmail-password' secret with value 'Anytime1#'")
            
    except Exception as e:
        print(f"❌ Error checking password: {e}")

if __name__ == "__main__":
    check_gmail_password()
