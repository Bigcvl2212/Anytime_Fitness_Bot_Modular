#!/usr/bin/env python3
"""
Secure Dashboard Demo Runner

This script demonstrates the secure login system by running the Flask application
in a way that showcases the security features.
"""

import os
import sys
import threading
import time
import webbrowser
from werkzeug.serving import run_simple

def print_demo_info():
    """Print information about the demo"""
    print("🎯 ANYTIME FITNESS SECURE DASHBOARD DEMO")
    print("=" * 50)
    print("🔐 SECURITY FEATURES:")
    print("  ✅ Encrypted credential storage in Google Cloud Secret Manager")
    print("  ✅ Secure session management with 8-hour timeout")
    print("  ✅ CSRF protection and security headers")
    print("  ✅ Input validation and sanitization")
    print("  ✅ Manager authentication with unique ID generation")
    print("  ✅ API endpoint protection")
    print("")
    print("📋 HOW TO TEST:")
    print("  1. Visit http://localhost:5000")
    print("  2. Click 'Register your credentials securely'")
    print("  3. Enter test credentials:")
    print("     ClubOS Username: test_manager")
    print("     ClubOS Password: test_password_123")
    print("     ClubHub Email: test@example.com")
    print("     ClubHub Password: clubhub_password_123")
    print("  4. Login with the same credentials")
    print("  5. Explore the secure dashboard")
    print("")
    print("🛡️ SECURITY NOTES:")
    print("  - All passwords are encrypted and never stored in plain text")
    print("  - Session tokens expire automatically")
    print("  - API endpoints require authentication")
    print("  - In production, credentials are stored in Google Secret Manager")
    print("")

def run_demo():
    """Run the demo application"""
    try:
        # Set environment variables for demo
        os.environ['FLASK_ENV'] = 'development' 
        os.environ['GCP_PROJECT_ID'] = 'round-device-460522-g8'
        
        # Import and configure the app
        from secure_dashboard_app import app
        
        # Print demo information
        print_demo_info()
        
        print("🚀 STARTING SECURE DASHBOARD...")
        print("💻 Demo running at: http://localhost:5000")
        print("🔐 Use Ctrl+C to stop the demo")
        print("=" * 50)
        print()
        
        # Try to open browser automatically
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            try:
                webbrowser.open('http://localhost:5000')
                print("🌐 Opened browser automatically")
            except:
                print("ℹ️  Please manually visit http://localhost:5000")
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent double startup
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()

def create_test_data():
    """Create test data to demonstrate the system"""
    print("📊 CREATING TEST DATA...")
    
    try:
        # This would create test data in a real environment
        print("  ✅ Test data would be created in Google Secret Manager")
        print("  ✅ Manager credentials would be encrypted and stored")
        print("  ✅ Session management would be configured")
    except Exception as e:
        print(f"  ❌ Error creating test data: {e}")

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 CHECKING REQUIREMENTS...")
    
    required_packages = ['flask', 'flask-session', 'google-cloud-secret-manager', 'bcrypt']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ❌ {package}")
    
    if missing:
        print(f"🚨 Missing packages: {', '.join(missing)}")
        print("💡 Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All requirements met!")
    return True

if __name__ == "__main__":
    print("🏋️ ANYTIME FITNESS BOT - SECURE DASHBOARD DEMO")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        check_requirements()
    elif len(sys.argv) > 1 and sys.argv[1] == '--info':
        print_demo_info()
    else:
        if check_requirements():
            create_test_data()
            print()
            run_demo()
        else:
            print("❌ Cannot run demo due to missing requirements")
            sys.exit(1)