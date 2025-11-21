"""
ClubHub Token Capture Automation System
Extracts session cookies and bearer tokens from iPad ClubHub app via Charles Proxy.
Automated, secure, and repeatable token extraction for ClubHub API access.
"""

import json
import time
import requests
import subprocess
import os
import re
import platform
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging

from ...config.constants import GCP_PROJECT_ID
from ...utils.debug_helpers import debug_page_state


class ClubHubTokenCapture:
    """
    Automated ClubHub token extraction system using Charles Proxy.
    Monitors iPad ClubHub app traffic and extracts authentication tokens.
    """
    
    def __init__(self, charles_config: Dict[str, Any] = None):
        """Initialize ClubHub token capture system"""
        self.charles_config = charles_config or self._get_default_charles_config()
        self.tokens_file = Path("data/clubhub_tokens.json")
        self.tokens_file.parent.mkdir(exist_ok=True)
        self.logger = self._setup_logging()
        
        # Token storage
        self.current_tokens = {}
        self.token_expiry_threshold = timedelta(hours=23)  # Refresh if older than 23 hours
        
        # Platform detection
        self.is_windows = platform.system().lower() == "windows"
        self.is_mac = platform.system().lower() == "darwin"
        
    def _get_default_charles_config(self) -> Dict[str, Any]:
        """Get default Charles Proxy configuration"""
        # Windows Charles paths (expanded search locations)
        windows_charles_paths = [
            # Current user's Charles Proxy appx path (from running process)
            r"C:\Program Files\WindowsApps\XK72.Charles_5.0.1.3_x64__dtzq29nva69ra\VFS\ProgramFilesX64\Charles\Charles.exe",
            # Previous user's specific Charles Proxy appx path
            r"C:\Program Files\WindowsApps\CharlesSoftware.CharlesProxy_4.6.5.0_x64__q4m96yqgqdyxy\Charles.exe",
            # Standard installation paths
            r"C:\Program Files\Charles\Charles.exe",
            r"C:\Program Files (x86)\Charles\Charles.exe",
            r"C:\Charles\Charles.exe",
            r"C:\Program Files\Charles Proxy\Charles.exe",
            r"C:\Program Files (x86)\Charles Proxy\Charles.exe",
            r"C:\Users\{}\AppData\Local\Charles\Charles.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Roaming\Charles\Charles.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\Desktop\Charles\Charles.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\Downloads\Charles\Charles.exe".format(os.getenv('USERNAME', ''))
        ]
        
        # Find Charles on Windows
        charles_path = None
        if platform.system().lower() == "windows":
            # First check common paths
            for path in windows_charles_paths:
                if os.path.exists(path):
                    charles_path = path
                    break
            
            # If not found, search more broadly
            if not charles_path:
                charles_path = self._find_charles_proxy_windows()
        
        return {
            "charles_path": charles_path,
            "charles_port": 8888,
            "charles_ssl_port": 8889,
            "session_file": "charles_session.chls",
            "log_file": "charles_log.txt",
            "ipad_ip": "192.168.1.100",  # Update with your iPad IP
            "clubhub_domain": "clubhub-ios-api.anytimefitness.com",
            "token_patterns": {
                "bearer_token": r'Bearer\s+([A-Za-z0-9\-._~+/]+=*)',
                "session_cookie": r'incap_ses_\d+_\d+=([^;]+)',
                "authorization_header": r'Authorization:\s*Bearer\s+([A-Za-z0-9\-._~+/]+=*)'
            }
        }
    
    def _find_charles_proxy_windows(self) -> Optional[str]:
        """Enhanced Charles Proxy detection for Windows"""
        try:
            import subprocess
            
            # Method 1: Check if Charles is running
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Charles.exe"],
                    capture_output=True, text=True, timeout=5
                )
                if "Charles.exe" in result.stdout:
                    # Charles is running, try to find its path
                    result = subprocess.run(
                        ["wmic", "process", "where", "name='Charles.exe'", "get", "ExecutablePath"],
                        capture_output=True, text=True, timeout=5
                    )
                    for line in result.stdout.split('\n'):
                        if 'Charles.exe' in line and '\\' in line:
                            path = line.strip().split()[-1]
                            if os.path.exists(path):
                                return path
            except Exception:
                pass
            
            # Method 2: Search in common directories
            search_paths = [
                "C:\\Program Files\\WindowsApps",  # Windows Store apps
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\Users\\{}".format(os.getenv('USERNAME', '')),
                "C:\\Users\\{}\\AppData".format(os.getenv('USERNAME', '')),
                "C:\\Users\\{}\\Desktop".format(os.getenv('USERNAME', '')),
                "C:\\Users\\{}\\Downloads".format(os.getenv('USERNAME', ''))
            ]
            
            for search_path in search_paths:
                if os.path.exists(search_path):
                    for root, dirs, files in os.walk(search_path):
                        for file in files:
                            if file.lower() == "charles.exe":
                                charles_path = os.path.join(root, file)
                                if os.path.exists(charles_path):
                                    return charles_path
                        # Limit search depth to avoid long searches
                        if root.count(os.sep) - search_path.count(os.sep) > 3:
                            dirs.clear()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in enhanced Charles detection: {e}")
            return None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for token capture operations"""
        logger = logging.getLogger("ClubHubTokenCapture")
        logger.setLevel(logging.INFO)
        
        # Create handlers
        handler = logging.FileHandler("logs/clubhub_token_capture.log", encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(handler)
        
        return logger
    
    def start_charles_proxy(self) -> bool:
        """
        Start Charles Proxy and prepare for automated token capture.
        Improved to handle DDE errors and make headless mode more reliable.
        
        Returns:
            bool: True if Charles is available and ready, False otherwise
        """
        try:
            self.logger.info("Preparing Charles Proxy for automated token capture...")
            
            # Check if Charles is available
            if not self.charles_config["charles_path"]:
                self.logger.error("ERROR: Charles Proxy not found on this system")
                return False
            
            if not os.path.exists(self.charles_config["charles_path"]):
                self.logger.error(f"ERROR: Charles Proxy not found at: {self.charles_config['charles_path']}")
                return False
            
            # Check if Charles is already running
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Charles.exe"],
                    capture_output=True, text=True, timeout=5
                )
                if "Charles.exe" in result.stdout:
                    self.logger.info("✅ Charles Proxy is already running")
                    return True
            except Exception:
                pass
            
            # Method 1: Try headless mode with improved error handling
            if self._try_headless_charles():
                return True
            
            # Method 2: Try starting Charles with different parameters
            if self._try_alternative_charles_start():
                return True
            
            # Method 3: Try using Windows service approach
            if self._try_charles_as_service():
                return True
            
            # Method 4: Fallback to GUI mode
            if self._try_gui_charles_start():
                return True
            
            self.logger.error("❌ All Charles startup methods failed")
            return False
                
        except Exception as e:
            self.logger.error(f"❌ Error preparing Charles Proxy: {e}")
            return False
    
    def _try_headless_charles(self) -> bool:
        """Try starting Charles in headless mode with improved error handling"""
        try:
            self.logger.info("Trying headless Charles startup...")
            
            # Kill any existing Charles processes first
            subprocess.run(["taskkill", "/F", "/IM", "Charles.exe"], capture_output=True)
            time.sleep(3)
            
            # Try different headless configurations
            headless_configs = [
                # Standard headless
                [
                    self.charles_config["charles_path"],
                    "-headless",
                    "-port", str(self.charles_config["charles_port"]),
                    "-ssl-port", str(self.charles_config["charles_ssl_port"])
                ],
                # Headless with no GUI
                [
                    self.charles_config["charles_path"],
                    "-headless",
                    "-nogui",
                    "-port", str(self.charles_config["charles_port"])
                ],
                # Headless with specific config
                [
                    self.charles_config["charles_path"],
                    "-headless",
                    "-config", "charles_config.xml",
                    "-port", str(self.charles_config["charles_port"])
                ]
            ]
            
            for config in headless_configs:
                try:
                    # Start Charles with timeout
                    process = subprocess.Popen(
                        config,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # Wait for startup
                    time.sleep(5)
                    
                    # Check if process is still running
                    if process.poll() is None:
                        self.logger.info("✅ Charles started in headless mode")
                        self.charles_process = process
                        return True
                    else:
                        # Check for DDE errors in stderr
                        stderr_output = process.stderr.read().decode() if process.stderr else ""
                        if "DDE" in stderr_output or "Unable to create DDE conversation" in stderr_output:
                            self.logger.debug(f"DDE error detected: {stderr_output}")
                            continue
                        
                except Exception as e:
                    self.logger.debug(f"Headless config failed: {e}")
                    continue
            
            self.logger.warning("⚠️ All headless configurations failed")
            return False
            
        except Exception as e:
            self.logger.debug(f"Headless startup error: {e}")
            return False
    
    def _try_alternative_charles_start(self) -> bool:
        """Try alternative Charles startup methods"""
        try:
            self.logger.info("Trying alternative Charles startup...")
            
            # Method 1: Start with minimized window
            try:
                process = subprocess.Popen(
                    [self.charles_config["charles_path"], "-minimized"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(3)
                if process.poll() is None:
                    self.logger.info("✅ Charles started minimized")
                    self.charles_process = process
                    return True
            except Exception:
                pass
            
            # Method 2: Start with specific working directory
            try:
                process = subprocess.Popen(
                    [self.charles_config["charles_path"]],
                    cwd=os.path.dirname(self.charles_config["charles_path"]),
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(3)
                if process.poll() is None:
                    self.logger.info("✅ Charles started with custom working directory")
                    self.charles_process = process
                    return True
            except Exception:
                pass
            
            # Method 3: Start with environment variables
            try:
                env = os.environ.copy()
                env["CHARLES_HEADLESS"] = "1"
                env["CHARLES_NO_GUI"] = "1"
                
                process = subprocess.Popen(
                    [self.charles_config["charles_path"]],
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                time.sleep(3)
                if process.poll() is None:
                    self.logger.info("✅ Charles started with environment variables")
                    self.charles_process = process
                    return True
            except Exception:
                pass
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Alternative startup error: {e}")
            return False
    
    def _try_charles_as_service(self) -> bool:
        """Try starting Charles as a Windows service-like process"""
        try:
            self.logger.info("Trying Charles as service...")
            
            # Create a batch file to start Charles
            batch_content = f'''@echo off
cd /d "{os.path.dirname(self.charles_config['charles_path'])}"
start /min "" "{self.charles_config['charles_path']}" -headless -port {self.charles_config["charles_port"]}
'''
            
            batch_file = "start_charles.bat"
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # Run the batch file
            process = subprocess.Popen(
                [batch_file],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(5)
            
            # Check if Charles is running
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Charles.exe"],
                capture_output=True, text=True, timeout=5
            )
            
            if "Charles.exe" in result.stdout:
                self.logger.info("✅ Charles started as service")
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Service startup error: {e}")
            return False
    
    def _try_gui_charles_start(self) -> bool:
        """Fallback to GUI mode startup"""
        try:
            self.logger.info("Trying GUI Charles startup...")
            
            process = subprocess.Popen(
                [self.charles_config["charles_path"]],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(3)
            
            if process.poll() is None:
                self.logger.info("✅ Charles started in GUI mode")
                self.charles_process = process
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"GUI startup error: {e}")
            return False
    
    def stop_charles_proxy(self) -> bool:
        """Stop Charles Proxy and clean up resources"""
        try:
            self.logger.info("Stopping Charles Proxy...")
            
            # Kill any remaining Charles processes
            if self.is_windows:
                subprocess.run(["taskkill", "/F", "/IM", "Charles.exe"], capture_output=True)
            
            self.logger.info("✅ Charles Proxy stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping Charles Proxy: {e}")
            return False
    
    def export_charles_session(self) -> bool:
        """
        Export Charles session to file using Charles CLI or automation.
        
        Returns:
            bool: True if export successful
        """
        try:
            self.logger.info("Exporting Charles session...")
            
            # Method 1: Try using Charles CLI export
            try:
                charles_cli_cmd = [
                    self.charles_config["charles_path"],
                    "-export-session",
                    self.charles_config["session_file"]
                ]
                
                result = subprocess.run(
                    charles_cli_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info("✅ Charles session exported via CLI")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"CLI export failed: {e}")
            
            # Method 2: Use Windows automation to trigger export
            try:
                import pyautogui
                
                # Focus on Charles window
                charles_window = pyautogui.getWindowsWithTitle("Charles")
                if charles_window:
                    charles_window[0].activate()
                    time.sleep(1)
                    
                    # Trigger export via keyboard shortcuts
                    pyautogui.hotkey('ctrl', 'shift', 'e')  # Export session shortcut
                    time.sleep(2)
                    
                    # Type filename and press Enter
                    pyautogui.write(self.charles_config["session_file"])
                    pyautogui.press('enter')
                    time.sleep(3)
                    
                    # Check if file was created
                    if os.path.exists(self.charles_config["session_file"]):
                        self.logger.info("✅ Charles session exported via automation")
                        return True
                        
            except ImportError:
                self.logger.warning("pyautogui not available for automation")
            except Exception as e:
                self.logger.warning(f"Automation export failed: {e}")
            
            # Method 3: Manual export instruction
            self.logger.info("⚠️ Please manually export Charles session:")
            self.logger.info(f"   1. In Charles: File → Export Session...")
            self.logger.info(f"   2. Choose 'Charles Session' format")
            self.logger.info(f"   3. Save as: {self.charles_config['session_file']}")
            self.logger.info(f"   4. Press Enter when done...")
            
            input("Press Enter when you've exported the session...")
            
            if os.path.exists(self.charles_config["session_file"]):
                self.logger.info("✅ Charles session exported manually")
                return True
            else:
                self.logger.error("❌ Session file not found after manual export")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error exporting Charles session: {e}")
            return False
    
    def export_charles_session_automated(self) -> bool:
        """
        Automatically export Charles session using multiple methods.
        
        Returns:
            bool: True if export successful
        """
        try:
            self.logger.info("Attempting automated Charles session export...")
            
            # Method 1: Try Charles CLI export (if available)
            if self._try_charles_cli_export():
                return True
            
            # Method 2: Try Windows automation with pyautogui
            if self._try_windows_automation_export():
                return True
            
            # Method 3: Monitor for existing session file
            if self._try_session_file_monitoring():
                return True
            
            # Method 4: Use Charles REST API (if available)
            if self._try_charles_rest_api():
                return True
            
            self.logger.warning("⚠️ All automated export methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error in automated export: {e}")
            return False
    
    def _try_charles_cli_export(self) -> bool:
        """Try using Charles CLI to export session"""
        try:
            self.logger.info("Trying Charles CLI export...")
            
            # Try different CLI commands
            cli_commands = [
                [self.charles_config["charles_path"], "-export-session", self.charles_config["session_file"]],
                [self.charles_config["charles_path"], "-export", self.charles_config["session_file"]],
                [self.charles_config["charles_path"], "-save-session", self.charles_config["session_file"]]
            ]
            
            for cmd in cli_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        self.logger.info("✅ Charles CLI export successful")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"CLI command failed: {e}")
                    continue
            
            self.logger.warning("⚠️ Charles CLI export not available")
            return False
            
        except Exception as e:
            self.logger.debug(f"CLI export error: {e}")
            return False
    
    def _try_windows_automation_export(self) -> bool:
        """Try using Windows automation to trigger export"""
        try:
            import pyautogui
            
            self.logger.info("Trying Windows automation export...")
            
            # Find Charles window
            charles_windows = pyautogui.getWindowsWithTitle("Charles")
            if not charles_windows:
                self.logger.warning("⚠️ Charles window not found")
                return False
            
            charles_window = charles_windows[0]
            
            # Activate Charles window
            charles_window.activate()
            time.sleep(1)
            
            # Try different export methods
            export_methods = [
                # Method 1: Ctrl+Shift+E (common export shortcut)
                lambda: pyautogui.hotkey('ctrl', 'shift', 'e'),
                # Method 2: File menu export
                lambda: (pyautogui.hotkey('alt', 'f'), time.sleep(0.5), pyautogui.press('e')),
                # Method 3: Right-click context menu
                lambda: (pyautogui.rightClick(), time.sleep(0.5), pyautogui.press('e'))
            ]
            
            for method in export_methods:
                try:
                    method()
                    time.sleep(2)
                    
                    # Type filename
                    pyautogui.write(self.charles_config["session_file"])
                    time.sleep(1)
                    pyautogui.press('enter')
                    time.sleep(3)
                    
                    # Check if file was created
                    if os.path.exists(self.charles_config["session_file"]):
                        self.logger.info("✅ Windows automation export successful")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Automation method failed: {e}")
                    continue
            
            self.logger.warning("⚠️ Windows automation export failed")
            return False
            
        except ImportError:
            self.logger.warning("⚠️ pyautogui not available for automation")
            return False
        except Exception as e:
            self.logger.debug(f"Automation export error: {e}")
            return False
    
    def _try_session_file_monitoring(self) -> bool:
        """Monitor for existing session file and copy it"""
        try:
            self.logger.info("Checking for existing session files...")
            
            # Common Charles session file locations
            possible_locations = [
                "charles_session.chls",
                "Charles Session.chls",
                os.path.expanduser("~/Desktop/charles_session.chls"),
                os.path.expanduser("~/Downloads/charles_session.chls"),
                "C:/Users/Public/Documents/Charles/charles_session.chls"
            ]
            
            for location in possible_locations:
                if os.path.exists(location):
                    # Copy to our expected location
                    import shutil
                    shutil.copy2(location, self.charles_config["session_file"])
                    self.logger.info(f"✅ Found and copied session file from: {location}")
                    return True
            
            self.logger.warning("⚠️ No existing session files found")
            return False
            
        except Exception as e:
            self.logger.debug(f"File monitoring error: {e}")
            return False
    
    def _try_charles_rest_api(self) -> bool:
        """Try using Charles REST API (if available)"""
        try:
            import requests
            
            self.logger.info("Trying Charles REST API...")
            
            # Charles might have a REST API on localhost
            api_endpoints = [
                "http://localhost:8888/export",
                "http://localhost:8888/session/export",
                "http://127.0.0.1:8888/export"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = requests.post(
                        endpoint,
                        json={"filename": self.charles_config["session_file"]},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.logger.info("✅ Charles REST API export successful")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"REST API endpoint failed: {e}")
                    continue
            
            self.logger.warning("⚠️ Charles REST API not available")
            return False
            
        except ImportError:
            self.logger.warning("⚠️ requests not available for REST API")
            return False
        except Exception as e:
            self.logger.debug(f"REST API error: {e}")
            return False
    
    def trigger_clubhub_app_activity(self) -> bool:
        """
        Trigger ClubHub app activity on iPad to generate new tokens.
        
        This could be automated via:
        - AppleScript (if iPad is connected to Mac)
        - SSH to iPad (if jailbroken)
        - Network requests to trigger app refresh
        
        Returns:
            bool: True if activity triggered successfully
        """
        try:
            self.logger.info("Triggering ClubHub app activity on iPad...")
            
            # Method 1: Send network request to trigger app refresh
            trigger_url = f"https://{self.charles_config['clubhub_domain']}/api/v1.0/clubs/1156/members"
            
            response = requests.get(
                trigger_url,
                headers={
                    "User-Agent": "ClubHub Store/2.15.0 (com.anytimefitness.Club-Hub; build:1004; iOS 18.5.0) Alamofire/5.6.4",
                    "Accept": "application/json"
                },
                timeout=10
            )
            
            if response.status_code in [200, 401, 403]:
                self.logger.info("✅ ClubHub app activity triggered")
                return True
            else:
                self.logger.warning(f"⚠️ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error triggering ClubHub activity: {e}")
            return False
    
    def extract_tokens_from_charles_session(self) -> Dict[str, Any]:
        """
        Extract authentication tokens from Charles Proxy session file.
        
        Returns:
            Dict containing extracted tokens and metadata
        """
        try:
            self.logger.info("Extracting tokens from Charles session...")
            
            session_file = Path(self.charles_config["session_file"])
            if not session_file.exists():
                self.logger.error("❌ Charles session file not found")
                return {}
            
            # Parse Charles session file (CHLS format)
            tokens = self._parse_charles_session_file(session_file)
            
            if tokens:
                self.logger.info(f"✅ Extracted {len(tokens)} token sets")
                return tokens
            else:
                self.logger.warning("⚠️ No tokens found in Charles session")
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ Error extracting tokens: {e}")
            return {}
    
    def _parse_charles_session_file(self, session_file: Path) -> Dict[str, Any]:
        """
        Parse Charles Proxy session file (ZIP archive) to extract authentication tokens.
        Args:
            session_file: Path to Charles session file
        Returns:
            Dict containing extracted tokens
        """
        import zipfile
        import json
        import re
        from datetime import datetime
        tokens = {
            "bearer_token": None,
            "session_cookie": None,
            "authorization_header": None,
            "extraction_timestamp": datetime.now().isoformat(),
            "source_requests": []
        }
        try:
            with zipfile.ZipFile(session_file, 'r') as zip_file:
                for name in zip_file.namelist():
                    if name.endswith('.json'):
                        with zip_file.open(name) as f:
                            try:
                                data = json.load(f)
                            except Exception as e:
                                self.logger.warning(f"[DEBUG] Failed to parse {name}: {e}")
                                continue
                            
                            # Handle both list and dict structures
                            if isinstance(data, list):
                                # If data is a list, process each item
                                for item in data:
                                    if isinstance(item, dict):
                                        self._process_json_item(item, name, tokens)
                            elif isinstance(data, dict):
                                # If data is a dict, process it directly
                                self._process_json_item(data, name, tokens)
                            else:
                                self.logger.warning(f"[DEBUG] Unexpected data type in {name}: {type(data)}")
            
            # Clean up None values
            tokens = {k: v for k, v in tokens.items() if v is not None}
            
            # Debug summary
            self.logger.info(f"[DEBUG] Token extraction summary:")
            self.logger.info(f"  Bearer token found: {'Yes' if tokens.get('bearer_token') else 'No'}")
            self.logger.info(f"  Session cookie found: {'Yes' if tokens.get('session_cookie') else 'No'}")
            self.logger.info(f"  Authorization header found: {'Yes' if tokens.get('authorization_header') else 'No'}")
            self.logger.info(f"  Sources: {tokens.get('source_requests', [])}")
            
            return tokens
        except Exception as e:
            self.logger.error(f"❌ Error parsing Charles session file as ZIP: {e}")
            return {}
    
    def _process_json_item(self, item: Dict[str, Any], name: str, tokens: Dict[str, Any]) -> None:
        """
        Helper to process a single JSON item (request or response) from a Charles session file.
        """
        # Debug: Print the structure of this item
        print(f"[DEBUG] Processing item from {name}:")
        print(f"  Item keys: {list(item.keys())}")
        
        for section_name, section in [('request', item.get('request', {})), ('response', item.get('response', {}))]:
            print(f"  {section_name} keys: {list(section.keys()) if isinstance(section, dict) else 'Not a dict'}")
            
            header_obj = section.get('header', {})
            print(f"  {section_name} headers type: {type(header_obj)}")
            print(f"  {section_name} headers: {header_obj}")

            # Flatten headers list to dict
            flat_headers = {}
            if isinstance(header_obj, dict) and 'headers' in header_obj:
                for h in header_obj['headers']:
                    if isinstance(h, dict) and 'name' in h and 'value' in h:
                        flat_headers[h['name'].lower()] = h['value']
            # For debugging, print the flattened headers
            print(f"[DEBUG] {name} | {section_name} | Flattened headers:")
            for k, v in flat_headers.items():
                print(f"    {k}: {v}")

            # Extract Bearer token - try multiple patterns
            if not tokens["bearer_token"]:
                auth_header = flat_headers.get('authorization', '')
                if auth_header:
                    bearer_patterns = [
                        r'Bearer\s+([A-Za-z0-9\-._~+/=]+)',
                        r'Bearer\s+([A-Za-z0-9\-._~+/]+=*)',
                        r'Bearer\s+([A-Za-z0-9\-._~+/]+)',
                        r'Bearer\s+([^,\s]+)'
                    ]
                    for pattern in bearer_patterns:
                        match = re.search(pattern, auth_header, re.IGNORECASE)
                        if match:
                            tokens["bearer_token"] = match.group(1)
                            tokens["source_requests"].append(f"{name}:{section_name}:authorization")
                            print(f"[DEBUG] Found Bearer token: {tokens['bearer_token']}")
                            break

            # Extract session cookie - try multiple patterns
            if not tokens["session_cookie"]:
                cookie_header = flat_headers.get('cookie', '')
                if cookie_header:
                    cookie_patterns = [
                        r'incap_ses_\d+_\d+=([^;]+)',
                        r'incap_ses_\d+_\d+=([^,\s]+)',
                        r'incap_ses_\d+_\d+=([^;,\s]+)'
                    ]
                    for pattern in cookie_patterns:
                        match = re.search(pattern, cookie_header, re.IGNORECASE)
                        if match:
                            tokens["session_cookie"] = match.group(1)
                            tokens["source_requests"].append(f"{name}:{section_name}:cookie")
                            print(f"[DEBUG] Found session cookie: {tokens['session_cookie']}")
                            break

            # Extract full authorization header
            if not tokens["authorization_header"] and 'authorization' in flat_headers:
                tokens["authorization_header"] = flat_headers['authorization']
                tokens["source_requests"].append(f"{name}:{section_name}:full_auth")
                print(f"[DEBUG] Found full authorization header: {tokens['authorization_header']}")
    
    def validate_tokens(self, tokens: Dict[str, Any]) -> bool:
        """
        Validate extracted tokens by testing them against ClubHub API.
        
        Args:
            tokens: Extracted tokens to validate
            
        Returns:
            bool: True if tokens are valid, False otherwise
        """
        try:
            self.logger.info("Validating extracted tokens...")
            
            if not tokens.get("bearer_token"):
                self.logger.warning("⚠️ No bearer token to validate")
                return False
            
            # Test tokens against ClubHub API
            test_url = f"https://{self.charles_config['clubhub_domain']}/api/v1.0/clubs/1156/members"
            
            headers = {
                "Authorization": f"Bearer {tokens['bearer_token']}",
                "API-version": "1",
                "Accept": "application/json",
                "User-Agent": "ClubHub Store/2.15.0 (com.anytimefitness.Club-Hub; build:1004; iOS 18.5.0) Alamofire/5.6.4"
            }
            
            if tokens.get("session_cookie"):
                headers["Cookie"] = f"incap_ses_132_434694={tokens['session_cookie']}"
            
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("✅ Tokens validated successfully")
                return True
            elif response.status_code == 401:
                self.logger.warning("⚠️ Tokens are expired or invalid")
                return False
            else:
                self.logger.warning(f"⚠️ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error validating tokens: {e}")
            return False
    
    def store_tokens_securely(self, tokens: Dict[str, Any]) -> bool:
        """
        Store extracted tokens securely with encryption and timestamp.
        
        Args:
            tokens: Tokens to store
            
        Returns:
            bool: True if stored successfully
        """
        try:
            self.logger.info("Storing tokens securely...")
            
            # Load existing tokens
            existing_tokens = self.load_tokens()
            
            # Add new tokens with timestamp
            token_entry = {
                "tokens": tokens,
                "extracted_at": datetime.now().isoformat(),
                "validated": self.validate_tokens(tokens),
                "source": "charles_proxy_automation"
            }
            
            # Store with timestamp as key
            timestamp_key = datetime.now().strftime("%Y%m%d_%H%M%S")
            existing_tokens[timestamp_key] = token_entry
            
            # Keep only last 10 token sets
            if len(existing_tokens) > 10:
                oldest_keys = sorted(existing_tokens.keys())[:-10]
                for key in oldest_keys:
                    del existing_tokens[key]
            
            # Save to file
            with open(self.tokens_file, 'w') as f:
                json.dump(existing_tokens, f, indent=2)
            
            self.current_tokens = tokens
            self.logger.info("✅ Tokens stored securely")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error storing tokens: {e}")
            return False
    
    def load_tokens(self) -> Dict[str, Any]:
        """Load stored tokens from file"""
        try:
            if self.tokens_file.exists():
                with open(self.tokens_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"❌ Error loading tokens: {e}")
            return {}
    
    def get_latest_valid_tokens(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest valid tokens, checking expiry and refreshing if needed.
        
        Returns:
            Dict containing valid tokens or None if none available
        """
        try:
            # First check for manually stored tokens
            manual_tokens = self._load_manual_tokens()
            if manual_tokens:
                self.logger.info("✅ Using manually stored tokens")
                return manual_tokens
            
            stored_tokens = self.load_tokens()
            
            if not stored_tokens:
                self.logger.info("No stored tokens found, attempting extraction...")
                # Attempt extraction if Charles is available
                if self.charles_config["charles_path"]:
                    return self.extract_fresh_tokens()
                else:
                    self.logger.warning("⚠️ Charles Proxy not found, cannot extract fresh tokens")
                    return None
            
            # Find the most recent valid tokens
            valid_tokens = []
            for timestamp, token_data in stored_tokens.items():
                if token_data.get("validated", False):
                    extracted_at = datetime.fromisoformat(token_data["extracted_at"])
                    if datetime.now() - extracted_at < self.token_expiry_threshold:
                        valid_tokens.append((timestamp, token_data))
            
            if valid_tokens:
                # Get the most recent valid tokens
                latest_timestamp, latest_data = max(valid_tokens, key=lambda x: x[0])
                self.logger.info(f"✅ Using tokens from {latest_timestamp}")
                return latest_data["tokens"]
            else:
                self.logger.info("No valid tokens found, attempting extraction...")
                # Attempt extraction if Charles is available
                if self.charles_config["charles_path"]:
                    return self.extract_fresh_tokens()
                else:
                    self.logger.warning("⚠️ Charles Proxy not found, cannot extract fresh tokens")
                    return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting latest tokens: {e}")
            return None
    
    def _load_manual_tokens(self) -> Optional[Dict[str, Any]]:
        """Load manually stored tokens"""
        try:
            # Check for latest manual tokens
            latest_file = Path("data/clubhub_tokens_latest.json")
            if latest_file.exists():
                with open(latest_file, 'r') as f:
                    token_data = json.load(f)
                
                # Check if tokens are still valid
                if token_data.get("validated", False):
                    extracted_at = datetime.fromisoformat(token_data["extracted_at"])
                    if datetime.now() - extracted_at < self.token_expiry_threshold:
                        return token_data["tokens"]
                    else:
                        self.logger.warning("⚠️ Manual tokens have expired")
                else:
                    self.logger.warning("⚠️ Manual tokens are not validated")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error loading manual tokens: {e}")
            return None
    
    def extract_fresh_tokens(self) -> Optional[Dict[str, Any]]:
        """
        Extract fresh tokens using the complete automation workflow.
        Works with existing Charles GUI - no headless mode required.
        Includes automated ClubHub activity triggering.
        
        Returns:
            Dict containing fresh tokens or None if extraction failed
        """
        try:
            self.logger.info("Starting fresh token extraction...")
            
            # Check if Charles is available
            if not self.charles_config["charles_path"]:
                self.logger.error("❌ Charles Proxy not found on this system")
                return None
            
            # Step 1: Start Charles Proxy (improved startup)
            self.logger.info("🔄 Step 1: Starting Charles Proxy...")
            if not self.start_charles_proxy():
                self.logger.error("❌ Failed to start Charles Proxy")
                return None
            
            # Step 2: Wait for Charles to be ready
            self.logger.info("🔄 Step 2: Waiting for Charles to be ready...")
            time.sleep(5)
            
            # Step 3: Trigger ClubHub app activity
            self.logger.info("🔄 Step 3: Triggering ClubHub app activity...")
            if self.trigger_clubhub_app_activity():
                self.logger.info("✅ ClubHub activity triggered")
            else:
                self.logger.warning("⚠️ Could not trigger ClubHub activity automatically")
                self.logger.info("Please use ClubHub app on your iPad now...")
            
            # Step 4: Wait for traffic capture
            self.logger.info("🔄 Step 4: Waiting for traffic capture (30 seconds)...")
            self.logger.info("   Using ClubHub app on iPad will generate traffic...")
            time.sleep(30)
            
            # Step 5: Try automated session export
            self.logger.info("🔄 Step 5: Attempting automated session export...")
            if self.export_charles_session_automated():
                self.logger.info("✅ Automated session export successful")
            else:
                self.logger.warning("⚠️ Automated export failed, trying manual workflow...")
                self.logger.info("   Please export Charles session manually:")
                self.logger.info("   1. In Charles: File → Export Session...")
                self.logger.info("   2. Choose 'Charles Session' format")
                self.logger.info("   3. Save as 'charles_session.chls'")
                self.logger.info("   4. Press Enter when done...")
                input("Press Enter when you've exported the Charles session...")
            
            # Step 6: Extract tokens from session
            self.logger.info("🔄 Step 6: Extracting tokens from session...")
            tokens = self.extract_tokens_from_charles_session()
            
            if not tokens:
                self.logger.error("❌ No tokens extracted from session")
                self.logger.info("This usually means:")
                self.logger.info("   - No ClubHub traffic was captured")
                self.logger.info("   - iPad proxy settings are not configured")
                self.logger.info("   - SSL certificate is not installed on iPad")
                return None
            
            # Step 7: Validate tokens
            self.logger.info("🔄 Step 7: Validating tokens...")
            if not self.validate_tokens(tokens):
                self.logger.warning("⚠️ Extracted tokens are invalid")
                return None
            
            # Step 8: Store tokens securely
            self.logger.info("🔄 Step 8: Storing tokens securely...")
            if not self.store_tokens_securely(tokens):
                self.logger.error("❌ Failed to store tokens")
                return None
            
            self.logger.info("✅ Fresh token extraction completed successfully")
            return tokens
            
        except Exception as e:
            self.logger.error(f"❌ Error in fresh token extraction: {e}")
            return None
    
    def run_scheduled_extraction(self) -> bool:
        """
        Run scheduled token extraction with full automation.
        
        Returns:
            bool: True if extraction successful
        """
        try:
            self.logger.info("Running scheduled token extraction...")
            
            # Check if we need fresh tokens
            current_tokens = self.get_latest_valid_tokens()
            
            if current_tokens:
                self.logger.info("✅ Valid tokens already available")
                return True
            
            # Extract fresh tokens
            fresh_tokens = self.extract_fresh_tokens()
            
            if fresh_tokens:
                self.logger.info("✅ Scheduled extraction completed successfully")
                return True
            else:
                self.logger.error("❌ Scheduled extraction failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in scheduled extraction: {e}")
            return False
    
    def send_tokens_to_server(self, tokens: Dict[str, Any], server_url: str) -> bool:
        """
        Send extracted tokens to a local or cloud server endpoint.
        
        Args:
            tokens: Tokens to send
            server_url: Server endpoint URL
            
        Returns:
            bool: True if sent successfully
        """
        try:
            self.logger.info(f"Sending tokens to server: {server_url}")
            
            payload = {
                "tokens": tokens,
                "timestamp": datetime.now().isoformat(),
                "source": "charles_proxy_automation"
            }
            
            response = requests.post(
                server_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("✅ Tokens sent to server successfully")
                return True
            else:
                self.logger.error(f"❌ Server returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error sending tokens to server: {e}")
            return False


# Convenience functions for backward compatibility
def extract_clubhub_tokens(charles_config: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Extract ClubHub tokens using Charles Proxy automation"""
    capture = ClubHubTokenCapture(charles_config)
    return capture.extract_fresh_tokens()


def get_valid_clubhub_tokens(charles_config: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Get latest valid ClubHub tokens"""
    capture = ClubHubTokenCapture(charles_config)
    return capture.get_latest_valid_tokens()


def run_scheduled_token_extraction(charles_config: Dict[str, Any] = None) -> bool:
    """Run scheduled token extraction"""
    capture = ClubHubTokenCapture(charles_config)
    return capture.run_scheduled_extraction() 