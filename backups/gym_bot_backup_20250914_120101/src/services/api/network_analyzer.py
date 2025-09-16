"""
Network Analyzer Service
Captures and analyzes ClubOS API endpoints using Charles Proxy and Selenium DevTools.
"""

import time
import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ...config.constants import CLUBOS_LOGIN_URL, CLUBOS_CALENDAR_URL
from ...utils.debug_helpers import debug_page_state


class NetworkAnalyzer:
    """Analyzes network traffic to discover ClubOS API endpoints"""
    
    def __init__(self, charles_proxy_port: int = 8888):
        self.charles_proxy_port = charles_proxy_port
        self.proxy_url = f"http://localhost:{charles_proxy_port}"
        self.discovered_endpoints = {}
        self.driver = None
        
    def setup_selenium_with_proxy(self) -> bool:
        """Setup Selenium WebDriver with Charles Proxy"""
        try:
            print("🔧 Setting up Selenium with Charles Proxy...")
            
            chrome_options = Options()
            chrome_options.add_argument(f"--proxy-server={self.proxy_url}")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Enable network logging
            chrome_options.set_capability("goog:loggingPrefs", {
                "performance": "ALL",
                "browser": "ALL"
            })
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("   ✅ Selenium WebDriver configured with proxy")
            return True
            
        except Exception as e:
            print(f"   ❌ Error setting up Selenium: {e}")
            return False
    
    def login_and_capture_traffic(self, username: str, password: str) -> bool:
        """
        Login to ClubOS and capture network traffic
        
        Args:
            username: ClubOS username
            password: ClubOS password
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("🔐 Logging into ClubOS and capturing traffic...")
            
            if not self.driver:
                print("   ❌ WebDriver not initialized")
                return False
            
            # Navigate to login page
            self.driver.get(CLUBOS_LOGIN_URL)
            time.sleep(2)
            
            # Find and fill login form
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                password_field = self.driver.find_element(By.NAME, "password")
                
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)
                
                # Submit form
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_button.click()
                
                # Wait for redirect
                time.sleep(3)
                
                print("   ✅ Login form submitted")
                return True
                
            except Exception as e:
                print(f"   ❌ Error during login: {e}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error in login_and_capture_traffic: {e}")
            return False
    
    def navigate_and_capture(self, urls: List[str]) -> Dict[str, List[Dict]]:
        """
        Navigate to specific URLs and capture API calls
        
        Args:
            urls: List of URLs to navigate to
            
        Returns:
            Dict containing captured API calls by page
        """
        captured_data = {}
        
        try:
            print("🌐 Navigating to pages and capturing API calls...")
            
            for url in urls:
                print(f"   📄 Navigating to: {url}")
                
                # Navigate to page
                self.driver.get(url)
                time.sleep(3)
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Capture network logs
                logs = self.driver.get_log("performance")
                api_calls = self._extract_api_calls_from_logs(logs)
                
                if api_calls:
                    captured_data[url] = api_calls
                    print(f"   ✅ Captured {len(api_calls)} API calls from {url}")
                else:
                    print(f"   ⚠️ No API calls captured from {url}")
                
                time.sleep(2)  # Rate limiting
            
            return captured_data
            
        except Exception as e:
            print(f"   ❌ Error navigating and capturing: {e}")
            return captured_data
    
    def _extract_api_calls_from_logs(self, logs: List[Dict]) -> List[Dict]:
        """Extract API calls from browser performance logs"""
        api_calls = []
        
        try:
            for log in logs:
                if "message" not in log:
                    continue
                
                message = json.loads(log["message"])
                
                # Look for network requests
                if "message" in message and message["message"]["method"] == "Network.requestWillBeSent":
                    request = message["message"]["params"]["request"]
                    url = request["url"]
                    
                    # Filter for API calls
                    if self._is_api_call(url):
                        api_call = {
                            "url": url,
                            "method": request["method"],
                            "headers": request.get("headers", {}),
                            "timestamp": message["message"]["params"]["timestamp"]
                        }
                        
                        # Extract request body if present
                        if "postData" in request:
                            api_call["body"] = request["postData"]
                        
                        api_calls.append(api_call)
            
            return api_calls
            
        except Exception as e:
            print(f"   ⚠️ Error extracting API calls: {e}")
            return []
    
    def _is_api_call(self, url: str) -> bool:
        """Check if URL is an API call"""
        api_indicators = [
            "/api/",
            "/ajax/",
            "/rest/",
            "/v1/",
            "/v2/",
            "json",
            "xml"
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in api_indicators)
    
    def analyze_captured_data(self, captured_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Analyze captured network data to identify API patterns
        
        Args:
            captured_data: Captured API calls by page
            
        Returns:
            Dict containing analyzed API patterns
        """
        print("🔍 Analyzing captured network data...")
        
        analysis = {
            "endpoints": {},
            "authentication": {},
            "patterns": {},
            "recommendations": []
        }
        
        try:
            all_api_calls = []
            for page_calls in captured_data.values():
                all_api_calls.extend(page_calls)
            
            # Group by endpoint patterns
            endpoint_groups = {}
            for call in all_api_calls:
                url = call["url"]
                parsed = urlparse(url)
                base_path = parsed.path
                
                if base_path not in endpoint_groups:
                    endpoint_groups[base_path] = []
                endpoint_groups[base_path].append(call)
            
            # Analyze each endpoint group
            for base_path, calls in endpoint_groups.items():
                analysis["endpoints"][base_path] = {
                    "methods": list(set(call["method"] for call in calls)),
                    "call_count": len(calls),
                    "sample_calls": calls[:3],  # First 3 calls as examples
                    "headers": self._analyze_headers(calls),
                    "parameters": self._analyze_parameters(calls)
                }
            
            # Analyze authentication patterns
            analysis["authentication"] = self._analyze_authentication(all_api_calls)
            
            # Identify patterns
            analysis["patterns"] = self._identify_patterns(all_api_calls)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            print(f"   ✅ Analyzed {len(all_api_calls)} API calls across {len(endpoint_groups)} endpoints")
            return analysis
            
        except Exception as e:
            print(f"   ❌ Error analyzing captured data: {e}")
            return analysis
    
    def _analyze_headers(self, calls: List[Dict]) -> Dict[str, Any]:
        """Analyze headers across API calls"""
        header_analysis = {
            "common_headers": {},
            "auth_headers": [],
            "content_types": []
        }
        
        try:
            all_headers = {}
            for call in calls:
                headers = call.get("headers", {})
                for key, value in headers.items():
                    if key not in all_headers:
                        all_headers[key] = []
                    all_headers[key].append(value)
            
            # Find common headers
            for header, values in all_headers.items():
                if len(set(values)) == 1:  # Same value across all calls
                    header_analysis["common_headers"][header] = values[0]
                elif len(set(values)) < len(values):  # Some common values
                    header_analysis["common_headers"][header] = list(set(values))
            
            # Identify auth headers
            auth_indicators = ["authorization", "x-auth", "x-token", "cookie"]
            for header in all_headers:
                if any(indicator in header.lower() for indicator in auth_indicators):
                    header_analysis["auth_headers"].append(header)
            
            # Content types
            content_type_headers = [h for h in all_headers if "content-type" in h.lower()]
            header_analysis["content_types"] = list(set(all_headers.get("content-type", [])))
            
            return header_analysis
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing headers: {e}")
            return header_analysis
    
    def _analyze_parameters(self, calls: List[Dict]) -> Dict[str, Any]:
        """Analyze URL parameters across API calls"""
        param_analysis = {
            "common_params": {},
            "required_params": [],
            "optional_params": []
        }
        
        try:
            all_params = {}
            for call in calls:
                url = call["url"]
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                for param, values in params.items():
                    if param not in all_params:
                        all_params[param] = []
                    all_params[param].extend(values)
            
            # Find common parameters
            for param, values in all_params.items():
                if len(set(values)) == 1:  # Same value across all calls
                    param_analysis["common_params"][param] = values[0]
                elif len(set(values)) < len(values):  # Some common values
                    param_analysis["common_params"][param] = list(set(values))
            
            # Identify required vs optional parameters
            for param, values in all_params.items():
                if len(values) == len(calls):  # Present in all calls
                    param_analysis["required_params"].append(param)
                else:
                    param_analysis["optional_params"].append(param)
            
            return param_analysis
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing parameters: {e}")
            return param_analysis
    
    def _analyze_authentication(self, calls: List[Dict]) -> Dict[str, Any]:
        """Analyze authentication patterns"""
        auth_analysis = {
            "auth_methods": [],
            "token_patterns": [],
            "session_patterns": []
        }
        
        try:
            for call in calls:
                headers = call.get("headers", {})
                
                # Check for Bearer tokens
                auth_header = headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    auth_analysis["auth_methods"].append("Bearer Token")
                    auth_analysis["token_patterns"].append(auth_header)
                
                # Check for session cookies
                cookie_header = headers.get("cookie", "")
                if cookie_header:
                    auth_analysis["auth_methods"].append("Session Cookie")
                    auth_analysis["session_patterns"].append(cookie_header)
            
            # Remove duplicates
            auth_analysis["auth_methods"] = list(set(auth_analysis["auth_methods"]))
            auth_analysis["token_patterns"] = list(set(auth_analysis["token_patterns"]))
            auth_analysis["session_patterns"] = list(set(auth_analysis["session_patterns"]))
            
            return auth_analysis
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing authentication: {e}")
            return auth_analysis
    
    def _identify_patterns(self, calls: List[Dict]) -> Dict[str, Any]:
        """Identify patterns in API calls"""
        patterns = {
            "rest_patterns": [],
            "ajax_patterns": [],
            "data_formats": []
        }
        
        try:
            for call in calls:
                url = call["url"]
                method = call["method"]
                
                # REST patterns
                if "/api/" in url and method in ["GET", "POST", "PUT", "DELETE"]:
                    patterns["rest_patterns"].append({
                        "url": url,
                        "method": method
                    })
                
                # AJAX patterns
                if "/ajax/" in url or "json" in url:
                    patterns["ajax_patterns"].append({
                        "url": url,
                        "method": method
                    })
                
                # Data formats
                content_type = call.get("headers", {}).get("content-type", "")
                if "json" in content_type:
                    patterns["data_formats"].append("JSON")
                elif "xml" in content_type:
                    patterns["data_formats"].append("XML")
                elif "form" in content_type:
                    patterns["data_formats"].append("Form Data")
            
            # Remove duplicates
            patterns["data_formats"] = list(set(patterns["data_formats"]))
            
            return patterns
            
        except Exception as e:
            print(f"   ⚠️ Error identifying patterns: {e}")
            return patterns
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        try:
            # Authentication recommendations
            if analysis["authentication"]["auth_methods"]:
                recommendations.append(f"Use {', '.join(analysis['authentication']['auth_methods'])} for authentication")
            
            # Endpoint recommendations
            if analysis["endpoints"]:
                recommendations.append(f"Implement {len(analysis['endpoints'])} discovered API endpoints")
            
            # Pattern recommendations
            if analysis["patterns"]["rest_patterns"]:
                recommendations.append("Follow REST API patterns for consistency")
            
            if analysis["patterns"]["data_formats"]:
                recommendations.append(f"Use {', '.join(analysis['patterns']['data_formats'])} for data exchange")
            
            return recommendations
            
        except Exception as e:
            print(f"   ⚠️ Error generating recommendations: {e}")
            return recommendations
    
    def save_analysis_report(self, analysis: Dict[str, Any], filename: str = None) -> bool:
        """
        Save analysis report to file
        
        Args:
            analysis: Analysis results
            filename: Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"clubos_api_analysis_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            print(f"   ✅ Analysis report saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving analysis report: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                print("   ✅ WebDriver cleaned up")
        except Exception as e:
            print(f"   ⚠️ Error during cleanup: {e}")


def run_network_analysis(username: str, password: str, urls_to_analyze: List[str] = None) -> Dict[str, Any]:
    """
    Run complete network analysis of ClubOS
    
    Args:
        username: ClubOS username
        password: ClubOS password
        urls_to_analyze: List of URLs to analyze
        
    Returns:
        Dict containing analysis results
    """
    analyzer = NetworkAnalyzer()
    
    try:
        print("🚀 Starting ClubOS network analysis...")
        
        # Setup Selenium with proxy
        if not analyzer.setup_selenium_with_proxy():
            return {}
        
        # Login and capture traffic
        if not analyzer.login_and_capture_traffic(username, password):
            return {}
        
        # Define URLs to analyze
        if not urls_to_analyze:
            urls_to_analyze = [
                CLUBOS_CALENDAR_URL,
                "https://anytime.club-os.com/action/Dashboard/messages",
                "https://anytime.club-os.com/action/Dashboard/PersonalTraining",
                "https://anytime.club-os.com/action/Dashboard/view"
            ]
        
        # Navigate and capture
        captured_data = analyzer.navigate_and_capture(urls_to_analyze)
        
        # Analyze captured data
        analysis = analyzer.analyze_captured_data(captured_data)
        
        # Save report
        analyzer.save_analysis_report(analysis)
        
        print("✅ Network analysis completed successfully!")
        return analysis
        
    except Exception as e:
        print(f"❌ Error during network analysis: {e}")
        return {}
    
    finally:
        analyzer.cleanup() 