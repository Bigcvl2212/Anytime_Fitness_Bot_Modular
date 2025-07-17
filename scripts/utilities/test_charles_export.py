#!/usr/bin/env python3
"""
Test Charles Export Automation
Simple test script to verify automated Charles session export works.
"""

import os
import sys
import time
import subprocess
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.authentication.clubhub_token_capture import export_charles_session_robust

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/charles_export_test.log')
        ]
    )

def check_charles_running():
    """Check if Charles is currently running"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Charles.exe"],
            capture_output=True, text=True, timeout=5
        )
        is_running = "Charles.exe" in result.stdout
        print(f"Charles Proxy running: {'Yes' if is_running else 'No'}")
        return is_running
    except Exception as e:
        print(f"Error checking Charles status: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 CHARLES EXPORT AUTOMATION TEST")
    print("=" * 40)
    
    setup_logging()
    
    # Step 1: Check if Charles is running
    print("\n1. Checking Charles Proxy status...")
    if not check_charles_running():
        print("❌ Charles Proxy is not running!")
        print("   Please start Charles Proxy first, then run this test again.")
        return False
    
    print("✅ Charles Proxy is running")
    
    # Step 2: Ensure charles_session.chls folder exists
    print("\n2. Setting up export directory...")
    export_dir = "charles_session.chls"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        print(f"✅ Created export directory: {export_dir}")
    else:
        print(f"✅ Export directory exists: {export_dir}")
    
    # Step 3: Clear any existing session files
    print("\n3. Clearing existing session files...")
    import glob
    existing_files = glob.glob(os.path.join(export_dir, "*.chls")) + glob.glob(os.path.join(export_dir, "*.chlz"))
    for file in existing_files:
        try:
            os.remove(file)
            print(f"   Removed: {file}")
        except Exception as e:
            print(f"   Could not remove {file}: {e}")
    
    # Step 4: Test automated export
    print("\n4. Testing automated export...")
    print("   This will attempt to:")
    print("   - Bring Charles window to foreground")
    print("   - Send Ctrl+Shift+E to trigger export")
    print("   - Type filename and confirm")
    print()
    
    input("Press Enter when you're ready to test the automated export...")
    
    print("🔄 Running automated export test...")
    result = export_charles_session_robust()
    
    # Step 5: Check results
    print("\n5. Checking results...")
    if result:
        print("✅ Automated export returned success!")
        
        # Check if files were actually created
        new_files = glob.glob(os.path.join(export_dir, "*.chls")) + glob.glob(os.path.join(export_dir, "*.chlz"))
        if new_files:
            print(f"✅ Session file(s) created: {new_files}")
            
            # Check file sizes
            for file in new_files:
                size = os.path.getsize(file)
                print(f"   File size: {file} = {size} bytes")
                if size > 1000:  # Reasonable minimum size
                    print("   ✅ File size looks good")
                else:
                    print("   ⚠️ File size seems small - might be empty")
        else:
            print("❌ No session files found despite success return")
            print("   This suggests the automation triggered but didn't complete properly")
    else:
        print("❌ Automated export failed")
        print("   Common causes:")
        print("   - Charles window couldn't be activated")
        print("   - Export dialog didn't appear")
        print("   - Timing issues with automation")
    
    print("\n6. Manual test instructions:")
    print("If automated export failed, you can test manually:")
    print("1. Focus on Charles window")
    print("2. Press Ctrl+Shift+E")
    print("3. Type 'charles_session.chls\\charles_session.chlz'")
    print("4. Press Enter")
    print("5. Check if file appears in charles_session.chls folder")
    
    return result

if __name__ == "__main__":
    success = main()
    print(f"\n🏁 Test {'PASSED' if success else 'FAILED'}")
    input("\nPress Enter to exit...")
