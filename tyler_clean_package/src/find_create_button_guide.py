#!/usr/bin/env python3
"""
Quick guide to help find the CREATE INSTANCE button in Google Cloud Console
"""

import webbrowser
import sys
from urllib.request import urlopen

def check_internet():
    """Check if internet connection is working"""
    try:
        urlopen('https://www.google.com', timeout=5)
        return True
    except:
        return False

def main():
    print("🔍 Google Cloud SQL - Finding the CREATE INSTANCE Button")
    print("=" * 60)
    print()
    
    if not check_internet():
        print("❌ No internet connection detected")
        print("Please check your internet connection and try again")
        return
    
    print("Let me help you find the CREATE INSTANCE button!")
    print()
    
    # Get their current status
    print("First, let's check where you are:")
    print()
    print("1. Do you have a Google Cloud account? (y/N): ", end="")
    has_account = input().lower().strip() == 'y'
    
    if not has_account:
        print("\n📋 You'll need to create a Google account first:")
        print("   1. Go to https://accounts.google.com/signup")
        print("   2. Create a Google account")
        print("   3. Come back and run this script again")
        return
    
    print("\n2. Do you have a Google Cloud project? (y/N): ", end="")
    has_project = input().lower().strip() == 'y'
    
    print("\n3. Do you have billing enabled? (y/N): ", end="")
    has_billing = input().lower().strip() == 'y'
    
    print("\n" + "=" * 60)
    print("🚀 Opening the right page for you...")
    print("=" * 60)
    
    # Open the appropriate page
    if not has_project:
        print("\n📋 Opening project creation page...")
        print("Create a project first, then navigate to SQL")
        webbrowser.open("https://console.cloud.google.com/projectcreate")
        
        print("\nAfter creating your project:")
        print("1. Look for the search bar at the top")
        print("2. Type 'SQL' and press Enter")
        print("3. Click on 'SQL' from the results")
        
    elif not has_billing:
        print("\n💳 Opening billing setup page...")
        print("You need billing enabled to use Cloud SQL")
        webbrowser.open("https://console.cloud.google.com/billing")
        
        print("\nAfter setting up billing:")
        print("1. Look for the search bar at the top")
        print("2. Type 'SQL' and press Enter")
        print("3. Click on 'SQL' from the results")
        
    else:
        print("\n🎯 Opening Cloud SQL directly...")
        webbrowser.open("https://console.cloud.google.com/sql")
        
        print("\nOn the Cloud SQL page, you should see:")
        print("1. A blue 'CREATE INSTANCE' button (usually prominent)")
        print("2. If you don't see it, you might need to:")
        print("   - Select your project from the dropdown at the top")
        print("   - Enable the Cloud SQL API (there will be an 'ENABLE' button)")
    
    print("\n" + "=" * 60)
    print("🔍 What to look for:")
    print("=" * 60)
    
    print("\n✅ You're on the RIGHT page if you see:")
    print("   - URL contains 'console.cloud.google.com/sql'")
    print("   - Page title says 'SQL instances'")
    print("   - Blue 'CREATE INSTANCE' button visible")
    print("   - Google Cloud navigation menu on the left")
    
    print("\n❌ You're on the WRONG page if you see:")
    print("   - Any other Google service (Gmail, Drive, etc.)")
    print("   - A page asking to 'Select a project' with no other options")
    print("   - An error about 'API not enabled'")
    
    print("\n🆘 If you still don't see CREATE INSTANCE:")
    print("   1. Make sure you selected a project (dropdown at top)")
    print("   2. Look for 'Enable Cloud SQL API' button and click it")
    print("   3. Wait 1-2 minutes for the API to enable")
    print("   4. Refresh the page")
    
    print("\n📞 Current Status Check:")
    print("   - Google account: ✅" if has_account else "   - Google account: ❌ (need to create)")
    print("   - Google Cloud project: ✅" if has_project else "   - Google Cloud project: ❌ (need to create)")  
    print("   - Billing enabled: ✅" if has_billing else "   - Billing enabled: ❌ (need to enable)")
    
    print(f"\n🌐 Browser should have opened with the correct page.")
    print("If it didn't open automatically, copy this URL:")
    
    if not has_project:
        print("https://console.cloud.google.com/projectcreate")
    elif not has_billing:
        print("https://console.cloud.google.com/billing")
    else:
        print("https://console.cloud.google.com/sql")
    
    print("\n💡 Next: Once you see the CREATE INSTANCE button:")
    print("   1. Follow the detailed_cloud_sql_setup.md guide")
    print("   2. Or run: python setup_cloud_sql.py after creating the instance")

if __name__ == '__main__':
    main()