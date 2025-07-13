#!/usr/bin/env python3
"""
Smart Token Capture System
Automatically starts Charles Proxy and guides user through token capture process.
"""

import sys
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path
import atexit
import pygetwindow
import pyautogui

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def minimize_charles_window():
    """Minimize Charles Proxy window so user can see terminal output"""
    try:
        import win32gui
        import win32con
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "Charles" in window_text:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        for hwnd in windows:
            # Minimize the window
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            print("✅ Charles window minimized")
            return True
            
        return False
        
    except ImportError:
        print("⚠️  pywin32 not available - cannot minimize Charles window automatically")
        print("   Please minimize Charles window manually to see terminal output")
        return False
    except Exception as e:
        print(f"⚠️  Could not minimize Charles window: {e}")
        return False

def kill_charles_proxy():
    """Kill any running Charles Proxy processes"""
    import subprocess
    try:
        print("[DEBUG] Killing any running Charles Proxy processes...")
        subprocess.run(["taskkill", "/F", "/IM", "Charles.exe"], capture_output=True)
    except Exception as e:
        print(f"[DEBUG] Error killing Charles Proxy: {e}")

def smart_token_capture():
    """Smart token capture with user guidance"""
    # Kill Charles before starting
    kill_charles_proxy()
    print("🚀 Smart ClubHub Token Capture System")
    print("=" * 60)
    print()
    
    # Register Charles shutdown on exit
    atexit.register(kill_charles_proxy)
    try:
        # Import the token capture system
        from gym_bot.services.authentication.clubhub_token_capture import ClubHubTokenCapture
        
        # Create token capture instance
        capture = ClubHubTokenCapture()
        
        # Step 1: Start Charles Proxy automatically
        print("🔄 Step 1: Starting Charles Proxy...")
        print("   - Attempting to start Charles Proxy automatically")
        print("   - If this fails, you'll be prompted to start it manually")
        print()
        
        charles_started = False
        try:
            charles_started = capture.start_charles_proxy()
        except Exception as e:
            print(f"   ⚠️  Auto-start failed: {e}")
            charles_started = False
        
        if charles_started:
            print("✅ Charles Proxy started successfully!")
        else:
            print("❌ Failed to start Charles Proxy automatically")
            print()
            print("Please start Charles Proxy manually:")
            print("1. Open Charles Proxy from your Start Menu or Desktop")
            print("2. Make sure it's running and visible")
            print("3. Press Enter when Charles is ready...")
            input()
            
            # Verify Charles is running
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Charles.exe"],
                    capture_output=True, text=True, timeout=5
                )
                if "Charles.exe" in result.stdout:
                    print("✅ Charles Proxy detected as running!")
                else:
                    print("❌ Charles Proxy not detected. Please make sure it's running.")
                    return False
            except Exception:
                print("⚠️  Could not verify Charles Proxy status, continuing anyway...")
        
        # Step 2: Wait for Charles to be fully ready (increased wait time)
        print("\n⏳ Waiting for Charles to be fully ready...")
        print("   - Charles needs time to load completely")
        print("   - This can take 10-20 seconds...")
        print("   - Please wait for the countdown to finish before using your iPad")
        print()
        
        # Wait 20 seconds for Charles to fully load
        for i in range(20):
            print(f"   Loading... ({i+1}/20 seconds)")
            time.sleep(1)
        
        print("✅ Charles should be fully loaded now!")
        
        # Step 3: Minimize Charles window
        print("\n🔄 Minimizing Charles window...")
        if minimize_charles_window():
            print("✅ Charles window minimized - you can now see terminal output")
        else:
            print("⚠️  Please minimize Charles window manually to see terminal output")
        
        # Step 4: Guide user to use ClubHub app
        print("\n📱 Step 2: Use ClubHub App on iPad")
        print("=" * 40)
        print("🎯 NOW IS THE TIME TO USE YOUR IPAD!")
        print("Please follow these steps:")
        print("1. Open ClubHub app on your iPad")
        print("2. Navigate to any section in the app (Members, Dashboard, etc.)")
        print("3. Generate some traffic by browsing around")
        print("4. The system will monitor and detect when traffic is captured")
        print()
        print("⏳ The system will now monitor for ClubHub traffic...")
        print("   (Start using your iPad now!)")
        print()
        
        # Step 5: Monitor for traffic and guide user
        print("🔄 Step 3: Monitoring for ClubHub traffic...")
        print("   - Using ClubHub app will generate traffic")
        print("   - Charles will capture the authentication data")
        print("   - System will detect when authentication is captured")
        print()
        
        # Wait for user to use the app
        print("⏳ Please use the ClubHub app now...")
        print("   (The system will wait for you to generate traffic)")
        print("   🎯 START USING YOUR IPAD NOW!")
        print()

        # Wait for user to finish (prompt for Enter)
        input("When you are done using the ClubHub app and want to capture the session, press Enter to continue...")

        print("✅ Charles Proxy is ready and user has generated traffic!")
        print("🔄 Now proceeding to monitor and extract tokens...")
        return True
            
    except Exception as e:
        print(f"❌ Error in smart token capture: {e}")
        kill_charles_proxy()
        return False

def monitor_for_traffic(capture, timeout=120):
    """Monitor for ClubHub traffic capture"""
    print(f"⏳ Monitoring for ClubHub traffic (timeout: {timeout} seconds)...")
    print("   Looking for traffic to: clubhub-ios-api.anytimefitness.com")
    print()
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check if Charles has captured any ClubHub traffic
        if check_for_clubhub_traffic():
            return True
        
        # Show progress
        elapsed = int(time.time() - start_time)
        remaining = timeout - elapsed
        print(f"   Monitoring... ({elapsed}s elapsed, {remaining}s remaining)")
        
        time.sleep(5)
    
    return False

def check_for_clubhub_traffic(session_file):
    """Check if Charles has captured ClubHub traffic"""
    try:
        # Check for session files
        session_files = [
            Path("charles_session.chls/charles_session.chls"),
            Path("charles_session.chls/Untitled.chlz"),
            Path("Untitled.chlz")
        ]
        
        for session_file in session_files:
            if session_file.exists():
                print(f"   Found session file: {session_file}")
                # Check if file contains ClubHub traffic
                if contains_clubhub_traffic(session_file):
                    print(f"   ✅ ClubHub traffic found in {session_file}")
                    return True
                else:
                    print(f"   ❌ No ClubHub traffic in {session_file}")
        
        print("   No session files found with ClubHub traffic")
        return False
        
    except Exception as e:
        print(f"   Error checking traffic: {e}")
        return False

def contains_clubhub_traffic(session_file):
    """Check if session file contains ClubHub traffic"""
    try:
        import zipfile
        
        # Check if it's a ZIP file (Charles session format)
        if session_file.suffix == '.chls':
            with zipfile.ZipFile(session_file, 'r') as zip_file:
                for name in zip_file.namelist():
                    if name.endswith('.json'):
                        with zip_file.open(name) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            if 'clubhub-ios-api.anytimefitness.com' in content:
                                print(f"     Found ClubHub API traffic in {name}")
                                return True
                            elif 'anytimefitness.com' in content:
                                print(f"     Found Anytime Fitness traffic in {name}")
                                return True
        
        return False
        
    except Exception as e:
        print(f"     Error reading session file: {e}")
        return False

def monitor_for_fresh_traffic(capture, timeout=60):
    """Wait for a new Charles session file and check for ClubHub traffic"""
    print(f"⏳ Waiting for a fresh Charles session file (timeout: {timeout} seconds)...")
    session_files = [
        Path("charles_session.chls/charles_session.chls"),
        Path("charles_session.chls/Untitled.chlz"),
        Path("Untitled.chlz")
    ]
    start_time = time.time()
    last_mtime = max([f.stat().st_mtime for f in session_files if f.exists()] + [0])
    while time.time() - start_time < timeout:
        for session_file in session_files:
            if session_file.exists() and session_file.stat().st_mtime > last_mtime:
                print(f"   Detected new session file: {session_file}")
                if contains_clubhub_traffic(session_file):
                    print(f"   ✅ ClubHub traffic found in {session_file}")
                    return True
                else:
                    print(f"   ❌ No ClubHub traffic in {session_file}")
        time.sleep(2)
    print("   No new session file with ClubHub traffic detected in time window.")
    return False

def save_current_charles_session():
    """Save the current Charles session to the expected file location"""
    try:
        import subprocess
        import time
        
        # Method 1: Try using Charles CLI to save session
        charles_paths = [
            r"C:\Program Files\WindowsApps\XK72.Charles_5.0.1.3_x64__dtzq29nva69ra\VFS\ProgramFilesX64\Charles\Charles.exe",
            r"C:\Program Files\Charles\Charles.exe",
            r"C:\Program Files (x86)\Charles\Charles.exe"
        ]
        
        charles_exe = None
        for path in charles_paths:
            if os.path.exists(path):
                charles_exe = path
                break
        
        if charles_exe:
            print(f"   [DEBUG] Found Charles at: {charles_exe}")
            
            # Check what files exist before saving
            print("   [DEBUG] Files before save attempt:")
            session_files = [
                Path("charles_session.chls/charles_session.chls"),
                Path("charles_session.chls/Untitled.chlz"),
                Path("Untitled.chlz")
            ]
            for session_file in session_files:
                if session_file.exists():
                    print(f"     - {session_file} (exists, modified: {session_file.stat().st_mtime})")
                else:
                    print(f"     - {session_file} (does not exist)")
            
            # Try to save session using Charles CLI
            try:
                print(f"   [DEBUG] Running Charles CLI command: {charles_exe} -save-session charles_session.chls")
                result = subprocess.run([
                    charles_exe, 
                    "-save-session", 
                    "charles_session.chls"
                ], capture_output=True, text=True, timeout=10)
                print(f"   [DEBUG] Charles CLI save result: {result.returncode}")
                print(f"   [DEBUG] Charles CLI stdout: {result.stdout}")
                print(f"   [DEBUG] Charles CLI stderr: {result.stderr}")
                
                if result.returncode == 0:
                    print("   [DEBUG] Charles CLI reported success")
                else:
                    print(f"   [DEBUG] Charles CLI failed with return code: {result.returncode}")
            except Exception as e:
                print(f"   [DEBUG] Charles CLI save failed: {e}")
            
            # Check what files exist after saving
            print("   [DEBUG] Files after save attempt:")
            for session_file in session_files:
                if session_file.exists():
                    print(f"     - {session_file} (exists, modified: {session_file.stat().st_mtime})")
                else:
                    print(f"     - {session_file} (does not exist)")
        
        # Method 2: Try Windows automation to trigger File > Save Session As
        try:
            print("   [DEBUG] Attempting Windows automation to trigger File > Save Session As...")
            import win32gui
            import win32con
            import win32api
            import time
            
            def find_charles_window():
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if "Charles" in window_text:
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                return windows[0] if windows else None
            
            charles_hwnd = find_charles_window()
            if charles_hwnd:
                print(f"   [DEBUG] Found Charles window: {charles_hwnd}")
                # Bring Charles to front
                win32gui.SetForegroundWindow(charles_hwnd)
                time.sleep(1)
                
                # Send Alt+F to open File menu
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt down
                win32api.keybd_event(ord('F'), 0, 0, 0)  # F down
                win32api.keybd_event(ord('F'), 0, win32con.KEYEVENTF_KEYUP, 0)  # F up
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)  # Alt up
                time.sleep(0.5)
                
                # Send S for Save Session As
                win32api.keybd_event(ord('S'), 0, 0, 0)
                win32api.keybd_event(ord('S'), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(1)
                
                # Type the filename
                filename = "charles_session.chls"
                for char in filename:
                    win32api.keybd_event(ord(char), 0, 0, 0)
                    win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.1)
                
                # Press Enter to save
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(2)
                
                print("   [DEBUG] Sent File > Save Session As command to Charles with filename")
                return True
            else:
                print("   [DEBUG] Could not find Charles window for automation")
        except Exception as e:
            print(f"   [DEBUG] Windows automation failed: {e}")
        
        # Method 3: Prompt user to manually save
        print("   [DEBUG] CLI and automation failed, prompting for manual save...")
        print("   Please manually save the session in Charles:")
        print("   1. In Charles, go to File > Save Session As...")
        print("   2. Save as 'charles_session.chls' in the current directory")
        print("   3. Press Enter when done...")
        input()
        
        # Method 4: Try to copy the current session file
        current_session_paths = [
            Path("charles_session.chls/charles_session.chls"),
            Path("charles_session.chls/Untitled.chlz"),
            Path("Untitled.chlz")
        ]
        
        for session_path in current_session_paths:
            if session_path.exists():
                print(f"   [DEBUG] Found existing session: {session_path}")
                # Copy to the expected location
                target_path = Path("charles_session.chls/charles_session.chls")
                target_path.parent.mkdir(exist_ok=True)
                
                import shutil
                shutil.copy2(session_path, target_path)
                print(f"   [DEBUG] Copied session to: {target_path}")
                return True
        
        print("   [DEBUG] No existing session files found to copy")
        return False
        
    except Exception as e:
        print(f"   [DEBUG] Error in save_current_charles_session: {e}")
        return False

def analyze_saved_session_for_traffic():
    """Analyze the saved session file for ClubHub traffic"""
    print("   [DEBUG] Analyzing saved session for ClubHub traffic...")
    
    session_files = [
        Path("charles_session.chls/charles_session.chls"),
        Path("charles_session.chls/Untitled.chlz"),
        Path("Untitled.chlz")
    ]
    
    for session_file in session_files:
        if session_file.exists():
            print(f"   [DEBUG] Checking session file: {session_file}")
            if contains_clubhub_traffic(session_file):
                print(f"   ✅ ClubHub traffic found in {session_file}")
                return True
            else:
                print(f"   ❌ No ClubHub traffic in {session_file}")
    
    print("   [DEBUG] No ClubHub traffic found in any session files")
    return False

def trigger_windows_save():
    """Trigger Charles Save Session As via Windows automation"""
    print("🔧 Attempting Windows automation to trigger Save Session As...")
    
    try:
        # Find Charles window
        charles_window = None
        for window in pygetwindow.getAllTitles():
            if "Charles Proxy" in window:
                charles_window = pygetwindow.getWindowsWithTitle(window)[0]
                break
        
        if not charles_window:
            print("❌ Could not find Charles Proxy window")
            return False
        
        # Activate Charles window
        charles_window.activate()
        time.sleep(1)
        
        # Get initial files in directory
        CHARLES_SESSION_DIR = Path("charles_session.chls")
        initial_files = set()
        if CHARLES_SESSION_DIR.exists():
            initial_files = set(os.listdir(CHARLES_SESSION_DIR))
        print(f"📁 Initial files in directory: {initial_files}")
        
        # Click File menu
        print("   [DEBUG] Clicking File menu...")
        pyautogui.click(charles_window.left + 50, charles_window.top + 30)
        time.sleep(1)
        
        # Click Save Session As
        print("   [DEBUG] Clicking Save Session As...")
        pyautogui.click(charles_window.left + 50, charles_window.top + 80)
        time.sleep(2)  # Wait for dialog to appear
        
        # Type the filename
        print("   [DEBUG] Typing filename: charles_session_auto.chls")
        pyautogui.write("charles_session_auto.chls")
        time.sleep(1)
        
        # Press Enter to save
        print("   [DEBUG] Pressing Enter to save...")
        pyautogui.press('enter')
        
        # Wait for the save dialog to close and file to be written
        print("   [DEBUG] Waiting for save operation to complete...")
        time.sleep(3)  # Give time for file to be written
        
        # Monitor for new session file
        print("   [DEBUG] Monitoring for new session file...")
        start_time = time.time()
        new_file_found = False
        
        while time.time() - start_time < 30:  # Wait up to 30 seconds
            current_files = set()
            if CHARLES_SESSION_DIR.exists():
                current_files = set(os.listdir(CHARLES_SESSION_DIR))
            
            new_files = current_files - initial_files
            
            if new_files:
                print(f"   ✅ New file detected: {new_files}")
                new_file_found = True
                break
            
            print(f"   [DEBUG] Waiting for file... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(2)
        
        if new_file_found:
            print("✅ Session saved successfully via Windows automation!")
            return True
        else:
            print("❌ No new session file detected after 30 seconds")
            return False
            
    except Exception as e:
        print(f"❌ Windows automation failed: {e}")
        return False

def trigger_cli_save():
    """Trigger Charles Save Session As via CLI"""
    print("🔧 Attempting CLI to trigger Save Session As...")
    try:
        charles_paths = [
            r"C:\Program Files\WindowsApps\XK72.Charles_5.0.1.3_x64__dtzq29nva69ra\VFS\ProgramFilesX64\Charles\Charles.exe",
            r"C:\Program Files\Charles\Charles.exe",
            r"C:\Program Files (x86)\Charles\Charles.exe"
        ]
        
        charles_exe = None
        for path in charles_paths:
            if os.path.exists(path):
                charles_exe = path
                break
        
        if not charles_exe:
            print("❌ Could not find Charles CLI executable.")
            return False
        
        print(f"   [DEBUG] Running CLI command: {charles_exe} -save-session charles_session.chls")
        result = subprocess.run([
            charles_exe, 
            "-save-session", 
            "charles_session.chls"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ CLI reported success")
            return True
        else:
            print(f"❌ CLI failed with return code: {result.returncode}")
            print(f"   [DEBUG] CLI stdout: {result.stdout}")
            print(f"   [DEBUG] CLI stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI save failed: {e}")
        return False

def get_latest_session_file():
    """Get the latest modified session file from the expected directory"""
    session_files = [
        Path("charles_session.chls/charles_session.chls"),
        Path("charles_session.chls/Untitled.chlz"),
        Path("Untitled.chlz")
    ]
    latest_file = None
    latest_mtime = 0
    
    for session_file in session_files:
        if session_file.exists():
            current_mtime = session_file.stat().st_mtime
            if current_mtime > latest_mtime:
                latest_mtime = current_mtime
                latest_file = session_file
    
    return latest_file

def analyze_session_file(session_file):
    """Analyze a single session file for ClubHub traffic"""
    try:
        print(f"   [DEBUG] Analyzing session file: {session_file}")
        if contains_clubhub_traffic(session_file):
            print(f"   ✅ ClubHub traffic found in {session_file}")
            return True
        else:
            print(f"   ❌ No ClubHub traffic in {session_file}")
            return False
    except Exception as e:
        print(f"     Error analyzing session file {session_file}: {e}")
        return False

def monitor_and_extract_tokens():
    """Monitor Charles for ClubHub traffic and extract tokens"""
    print("🔍 Monitoring Charles Proxy for ClubHub traffic...")
    
    # Get initial session files
    CHARLES_SESSION_DIR = Path("charles_session.chls")
    initial_files = set()
    if CHARLES_SESSION_DIR.exists():
        initial_files = set(os.listdir(CHARLES_SESSION_DIR))
    
    print(f"📁 Initial session files: {initial_files}")
    
    # Monitor for new traffic
    start_time = time.time()
    clubhub_detected = False
    
    while time.time() - start_time < 300:  # 5 minutes max
        try:
            # Check for new session files
            current_files = set()
            if CHARLES_SESSION_DIR.exists():
                current_files = set(os.listdir(CHARLES_SESSION_DIR))
            
            new_files = current_files - initial_files
            
            if new_files:
                print(f"🆕 New files detected: {new_files}")
                
                # Check if any new files contain ClubHub traffic
                for file in new_files:
                    if file.endswith('.chls'):
                        print(f"🔍 Analyzing new session file: {file}")
                        if analyze_session_file(CHARLES_SESSION_DIR / file):
                            clubhub_detected = True
                            break
            
            # Also check existing files for ClubHub traffic
            if not clubhub_detected:
                for file in current_files:
                    if file.endswith('.chls'):
                        if analyze_session_file(CHARLES_SESSION_DIR / file):
                            clubhub_detected = True
                            break
            
            if clubhub_detected:
                print("🎯 ClubHub traffic detected!")
                print("💾 Now attempting to save the Charles session automatically...")
                
                # Try Windows automation first
                session_saved = False
                if trigger_windows_save():
                    print("✅ Session saved via Windows automation")
                    session_saved = True
                else:
                    print("❌ Windows automation failed, trying CLI...")
                    # Try CLI save
                    if trigger_cli_save():
                        print("✅ Session saved via CLI")
                        session_saved = True
                    else:
                        print("❌ CLI save failed, please save manually")
                        print("📝 Please manually save the session as 'charles_session_manual.chls'")
                        input("Press Enter when you've saved the session...")
                        session_saved = True  # Assume manual save worked
                
                if session_saved:
                    # Wait a moment for file to be written
                    time.sleep(2)
                    
                    # Look for the saved session file
                    saved_session_file = None
                    session_files_to_check = [
                        CHARLES_SESSION_DIR / "charles_session_auto.chls",
                        CHARLES_SESSION_DIR / "charles_session_manual.chls",
                        CHARLES_SESSION_DIR / "charles_session.chls"
                    ]
                    
                    for session_file in session_files_to_check:
                        if session_file.exists():
                            saved_session_file = session_file
                            break
                    
                    if saved_session_file:
                        print(f"✅ Found saved session: {saved_session_file}")
                        
                        # Extract tokens from the saved session
                        print("🔍 Extracting tokens from saved session...")
                        from gym_bot.services.authentication.clubhub_token_capture import ClubHubTokenCapture
                        capture = ClubHubTokenCapture()
                        
                        # Use the specific session file path by updating the config
                        capture.charles_config["session_file"] = str(saved_session_file)
                        
                        # Extract tokens (method doesn't accept file path parameter)
                        tokens = capture.extract_tokens_from_charles_session()
                        
                        if tokens:
                            print("✅ Tokens extracted successfully!")
                            print(f"   Bearer Token: {tokens.get('bearer_token', 'Not found')[:50]}...")
                            print(f"   Session Cookie: {tokens.get('session_cookie', 'Not found')[:50]}...")
                            
                            # Store tokens
                            if capture.store_tokens_securely(tokens):
                                print("✅ Tokens stored securely!")
                                return tokens
                            else:
                                print("❌ Failed to store tokens")
                        else:
                            print("❌ No valid tokens found in saved session")
                            
                            # Try to analyze what's in the session file
                            print("🔍 Analyzing session file contents...")
                            try:
                                import zipfile
                                with zipfile.ZipFile(saved_session_file, 'r') as zip_file:
                                    print(f"   Session file contains {len(zip_file.namelist())} files")
                                    for name in zip_file.namelist():
                                        if name.endswith('.json'):
                                            with zip_file.open(name) as f:
                                                content = f.read().decode('utf-8', errors='ignore')
                                                if 'clubhub-ios-api.anytimefitness.com' in content:
                                                    print(f"   ✅ Found ClubHub traffic in {name}")
                                                    # Look for authorization headers
                                                    if 'Authorization' in content:
                                                        print(f"   🔍 Found Authorization headers in {name}")
                                                    if 'Cookie' in content:
                                                        print(f"   🔍 Found Cookie headers in {name}")
                            except Exception as e:
                                print(f"   ❌ Error analyzing session file: {e}")
                    else:
                        print("❌ No saved session file found")
                        print("   Expected: charles_session_auto.chls or charles_session_manual.chls")
                
                break
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error during monitoring: {e}")
            time.sleep(5)
    
    if not clubhub_detected:
        print("❌ No ClubHub traffic detected within 5 minutes")
    
    return None

def main():
    """Main function"""
    print("🚀 Starting Smart Token Capture...")
    print("This system will:")
    print("1. Start Charles Proxy automatically")
    print("2. Wait for Charles to fully load (20 seconds)")
    print("3. Minimize Charles window for better visibility")
    print("4. Guide you through using ClubHub app")
    print("5. Monitor for authentication traffic")
    print("6. Extract and validate tokens")
    print("7. Store tokens for the bot to use")
    print()
    
    # Start Charles and guide user
    charles_ready = smart_token_capture()
    
    if charles_ready:
        print("\n🔄 Now monitoring for ClubHub traffic and extracting tokens...")
        tokens = monitor_and_extract_tokens()
        
        if tokens:
            print("\n🎉 Smart token capture completed successfully!")
            print("You can now use the bot with fresh ClubHub tokens.")
            return True
        else:
            print("\n❌ Token extraction failed.")
            print("Please check your setup and try again.")
            return False
    else:
        print("\n❌ Failed to start Charles Proxy.")
        print("Please check your setup and try again.")
        return False

if __name__ == "__main__":
    main() 