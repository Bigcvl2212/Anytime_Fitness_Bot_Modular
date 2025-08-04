#!/usr/bin/env python3
"""
Simple Dual Capture Script
"""

print("*** DUAL CAPTURE EXECUTION SCRIPT ***")
print("="*50)
print("This script will guide you through capturing ClubOS workflow")
print("using both Charles Proxy and Playwright simultaneously.")
print("="*50)

def main():
    print("\n[CHECK] Checking prerequisites...")
    
    # Check if Playwright is available
    try:
        import playwright
        print("   [OK] Playwright: Available")
    except ImportError:
        print("   [ERROR] Playwright not installed")
        return
    
    # Check if capture script exists
    import os
    if os.path.exists("playwright_calendar_capture.py"):
        print("   [OK] Playwright capture script: Found")
    else:
        print("   [ERROR] Playwright capture script not found")
        return
    
    print("\nAll checks passed!")
    
    # Get credentials
    print("\n[CONFIG] ClubOS Login Details:")
    username = input("Username (j.mayo): ").strip() or "j.mayo"
    password = input("Password: ").strip()
    
    if not password:
        print("[ERROR] Password is required!")
        return
    
    duration = 5  # 5 minutes
    
    print(f"\n[INFO] Configuration:")
    print(f"   Username: {username}")
    print(f"   Duration: {duration} minutes")
    
    # Instructions for Charles Proxy
    print("\n[PROXY] Charles Proxy Setup:")
    print("1. Open Charles Proxy")
    print("2. Enable recording")
    print("3. Add SSL proxy for club-os.com:443")
    print("4. Clear session")
    print("5. Start recording")
    
    input("\nPress Enter when Charles Proxy is ready...")
    
    # Run Playwright capture
    print("\n[PLAYWRIGHT] Starting capture...")
    
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"captures/capture_{timestamp}"
    
    cmd = [
        "python", "playwright_calendar_capture.py",
        "--username", username,
        "--password", password,
        "--output-dir", output_dir,
        "--duration", str(duration * 60)
    ]
    
    try:
        print("   Running Playwright capture...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration * 60 + 60)
        
        if result.returncode == 0:
            print("   [OK] Playwright capture completed!")
            print(f"\nNext steps:")
            print(f"1. Stop Charles Proxy and export as HAR file")
            print(f"2. Save HAR file as: captures/charles_{timestamp}.har")
            print(f"3. Run analysis on both datasets")
            return True
        else:
            print(f"   [ERROR] Playwright failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Failed to run capture: {e}")
        return False

if __name__ == "__main__":
    main()
