#!/usr/bin/env python3

"""
Gmail App Password Setup for Collections Email
This script helps you set up the Gmail App Password for the collections email system.
"""

def print_instructions():
    """Print instructions for setting up Gmail App Password"""
    
    print("🔧 Gmail App Password Setup for Collections Email")
    print("=" * 60)
    print()
    print("The collections email system needs a Gmail App Password to send emails.")
    print("The current password 'Anytime1#' is the regular password, but Gmail")
    print("requires an App Password for SMTP when 2-Factor Authentication is enabled.")
    print()
    print("📋 Steps to generate App Password:")
    print("1. Go to https://myaccount.google.com/security")
    print("2. Sign in with fdl.gym.bot@gmail.com")
    print("3. Under 'Signing in to Google', click '2-Step Verification'")
    print("4. Scroll down and click 'App passwords'")
    print("5. Select 'Mail' as the app")
    print("6. Select 'Other' as the device and name it 'Gym Bot Collections'")
    print("7. Click 'Generate'")
    print("8. Copy the 16-character password (it will look like: abcd efgh ijkl mnop)")
    print()
    print("📋 Steps to update the secret:")
    print("1. Go to your Google Cloud Console")
    print("2. Navigate to Secret Manager")
    print("3. Find the 'gmail-password' secret")
    print("4. Update it with the new 16-character App Password")
    print("5. Remove spaces from the App Password (abcd efgh ijkl mnop → abcdefghijklmnop)")
    print()
    print("🧪 After updating, test with: python test_email_sending.py")
    print()
    print("⚠️  Important Notes:")
    print("- App Passwords are 16 characters long")
    print("- They don't contain spaces or special characters like #")
    print("- They're different from your regular Gmail password")
    print("- Each App Password can only be used for one application")
    print()

def test_current_setup():
    """Test the current Gmail setup"""
    
    print("🧪 Testing Current Gmail Setup")
    print("=" * 40)
    
    try:
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        sender_email = "fdl.gym.bot@gmail.com"
        sender_password = secrets_manager.get_secret("gmail-password")
        
        print(f"✅ Email: {sender_email}")
        print(f"✅ Password: {sender_password}")
        print(f"✅ Password length: {len(sender_password)}")
        
        if len(sender_password) == 9 and '#' in sender_password:
            print("⚠️  Current password appears to be the regular password")
            print("⚠️  Need to generate App Password for SMTP access")
            return False
        elif len(sender_password) == 16:
            print("✅ Password appears to be an App Password (16 characters)")
            return True
        else:
            print("⚠️  Password length is unexpected")
            return False
            
    except Exception as e:
        print(f"❌ Error testing setup: {e}")
        return False

if __name__ == "__main__":
    print_instructions()
    print()
    test_current_setup()
