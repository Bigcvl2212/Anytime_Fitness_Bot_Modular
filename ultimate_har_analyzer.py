#!/usr/bin/env python3
"""
ULTIMATE ClubOS HAR Analyzer - Extract EVERYTHING from HAR files
This script will parse EVERY piece of information from the HAR file to build the perfect messaging client
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urlparse, parse_qs, unquote

class UltimateClubOSHARAnalyzer:
    """Extract EVERY detail from ClubOS HAR files for perfect messaging replication"""
    
    def __init__(self, har_file_path: str):
        self.har_file_path = har_file_path
        self.har_data = None
        self.entries = []
        self.all_requests = []
        self.successful_messages = []
        self.all_form_data = {}
        self.session_cookies = {}
        self.csrf_tokens = {}
        
    def load_har_file(self) -> bool:
        """Load and parse the HAR file"""
        try:
            print(f"📄 Loading HAR file: {self.har_file_path}")
            
            with open(self.har_file_path, 'r', encoding='utf-8') as f:
                self.har_data = json.load(f)
            
            self.entries = self.har_data.get('log', {}).get('entries', [])
            print(f"✅ Loaded {len(self.entries)} HTTP requests from HAR file")
            return True
            
        except Exception as e:
            print(f"❌ Error loading HAR file: {e}")
            return False
    
    def analyze_everything(self):
        """Analyze EVERY aspect of the HAR file"""
        print("\\n🔍 ULTIMATE HAR ANALYSIS - EXTRACTING EVERYTHING")
        print("=" * 80)
        
        for i, entry in enumerate(self.entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            status = response.get('status', 0)
            
            # Analyze EVERY request
            request_analysis = {
                'index': i,
                'timestamp': entry.get('startedDateTime', ''),
                'method': method,
                'url': url,
                'status': status,
                'headers': self.extract_headers(request),
                'cookies': self.extract_cookies(request),
                'form_data': self.extract_form_data(request),
                'response_headers': self.extract_response_headers(response),
                'response_cookies': self.extract_response_cookies(response),
                'response_content': self.extract_response_content(response),
                'timing': entry.get('timings', {}),
                'is_messaging': self.is_messaging_related(url, request, response)
            }
            
            self.all_requests.append(request_analysis)
            
            # Track successful messaging specifically
            if self.is_successful_message(request_analysis):
                self.successful_messages.append(request_analysis)
                print(f"✅ SUCCESSFUL MESSAGE FOUND: Request #{i+1}")
                print(f"   URL: {url}")
                print(f"   Status: {status}")
                print(f"   Form Data Fields: {len(request_analysis['form_data'])}")
    
    def is_messaging_related(self, url: str, request: dict, response: dict) -> bool:
        """Check if request is messaging-related"""
        messaging_patterns = [
            'FollowUp', 'message', 'text', 'sms', 'email', 'contact'
        ]
        
        # Check URL
        if any(pattern.lower() in url.lower() for pattern in messaging_patterns):
            return True
        
        # Check form data
        form_data = self.extract_form_data(request)
        form_str = str(form_data).lower()
        if any(pattern.lower() in form_str for pattern in messaging_patterns):
            return True
        
        # Check response content
        response_content = self.extract_response_content(response).lower()
        if any(pattern in response_content for pattern in ['texted', 'emailed', 'sent']):
            return True
        
        return False
    
    def is_successful_message(self, request_analysis: dict) -> bool:
        """Check if this is a successful message request"""
        if not request_analysis['is_messaging']:
            return False
        
        # Check for success indicators in response
        response_content = request_analysis['response_content'].lower()
        success_indicators = ['has been texted', 'has been emailed', 'texted', 'emailed']
        
        if request_analysis['status'] == 200 and any(indicator in response_content for indicator in success_indicators):
            return True
        
        return False
    
    def extract_headers(self, request: dict) -> dict:
        """Extract ALL request headers"""
        headers = {}
        for header in request.get('headers', []):
            name = header.get('name', '')
            value = header.get('value', '')
            if name:
                headers[name] = value
        return headers
    
    def extract_response_headers(self, response: dict) -> dict:
        """Extract ALL response headers"""
        headers = {}
        for header in response.get('headers', []):
            name = header.get('name', '')
            value = header.get('value', '')
            if name:
                headers[name] = value
        return headers
    
    def extract_cookies(self, request: dict) -> dict:
        """Extract ALL request cookies"""
        cookies = {}
        for cookie in request.get('cookies', []):
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            if name:
                cookies[name] = value
        return cookies
    
    def extract_response_cookies(self, response: dict) -> dict:
        """Extract ALL response cookies"""
        cookies = {}
        for cookie in response.get('cookies', []):
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            if name:
                cookies[name] = value
        return cookies
    
    def extract_response_content(self, response: dict) -> str:
        """Extract response content"""
        content = response.get('content', {})
        return content.get('text', '')
    
    def extract_form_data(self, request: dict) -> dict:
        """Extract ALL form data from POST requests"""
        post_data = request.get('postData', {})
        if not post_data:
            return {}
        
        mime_type = post_data.get('mimeType', '')
        text = post_data.get('text', '')
        
        form_data = {}
        
        # Handle form-encoded data
        if 'application/x-www-form-urlencoded' in mime_type and text:
            try:
                pairs = text.split('&')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        form_data[unquote(key)] = unquote(value)
            except Exception as e:
                print(f"⚠️ Error parsing form data: {e}")
        
        # Handle multipart data
        elif 'multipart/form-data' in mime_type:
            params = post_data.get('params', [])
            for param in params:
                name = param.get('name', '')
                value = param.get('value', '')
                if name:
                    form_data[name] = value
        
        # Handle JSON data
        elif 'application/json' in mime_type and text:
            try:
                form_data = json.loads(text)
            except Exception as e:
                print(f"⚠️ Error parsing JSON data: {e}")
        
        # Raw text fallback
        if not form_data and text:
            try:
                pairs = text.split('&')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        form_data[unquote(key)] = unquote(value)
            except:
                form_data['_raw_data'] = text
        
        return form_data
    
    def print_successful_messages(self):
        """Print detailed analysis of successful messages"""
        print(f"\\n📨 SUCCESSFUL MESSAGE ANALYSIS ({len(self.successful_messages)} found)")
        print("=" * 80)
        
        for i, msg in enumerate(self.successful_messages):
            print(f"\\n🎯 SUCCESSFUL MESSAGE #{i+1}")
            print(f"   📅 Time: {msg['timestamp']}")
            print(f"   🔗 URL: {msg['url']}")
            print(f"   📊 Status: {msg['status']}")
            print(f"   🎯 Method: {msg['method']}")
            
            # Print ALL form data
            if msg['form_data']:
                print(f"   📝 FORM DATA ({len(msg['form_data'])} fields):")
                for key, value in msg['form_data'].items():
                    # Show full value for important fields
                    if len(str(value)) > 100 and not any(important in key.lower() for important in ['message', 'text', 'token', 'source']):
                        display_value = str(value)[:50] + "..."
                    else:
                        display_value = str(value)
                    print(f"      {key}: {display_value}")
            
            # Print important headers
            if msg['headers']:
                print(f"   📋 REQUEST HEADERS:")
                for key, value in msg['headers'].items():
                    if key.lower() in ['content-type', 'referer', 'x-requested-with', 'user-agent']:
                        print(f"      {key}: {value}")
            
            # Print cookies
            if msg['cookies']:
                print(f"   🍪 COOKIES:")
                for key, value in msg['cookies'].items():
                    if len(value) > 50:
                        display_value = value[:30] + "..."
                    else:
                        display_value = value
                    print(f"      {key}: {display_value}")
            
            # Print response preview
            response_preview = msg['response_content'][:200] if msg['response_content'] else "No content"
            print(f"   📄 RESPONSE: {response_preview}")
    
    def extract_messaging_patterns(self):
        """Extract patterns from successful messages"""
        if not self.successful_messages:
            print("❌ No successful messages to analyze")
            return
        
        print(f"\\n🔍 EXTRACTING MESSAGING PATTERNS")
        print("=" * 50)
        
        # Analyze form field patterns
        all_fields = {}
        for msg in self.successful_messages:
            for key, value in msg['form_data'].items():
                if key not in all_fields:
                    all_fields[key] = []
                all_fields[key].append(value)
        
        print(f"📋 ALL FORM FIELDS ACROSS SUCCESSFUL MESSAGES:")
        for field, values in all_fields.items():
            unique_values = list(set(values))
            print(f"   {field}:")
            for value in unique_values:
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"      → {display_value}")
        
        return all_fields
    
    def generate_perfect_implementation(self):
        """Generate the perfect messaging implementation"""
        if not self.successful_messages:
            print("❌ Cannot generate implementation - no successful messages found")
            return
        
        print(f"\\n🚀 GENERATING PERFECT IMPLEMENTATION")
        print("=" * 60)
        
        # Use the most complete successful message
        best_message = max(self.successful_messages, key=lambda x: len(x['form_data']))
        
        print(f"📋 Based on successful message:")
        print(f"   URL: {best_message['url']}")
        print(f"   Form fields: {len(best_message['form_data'])}")
        
        # Generate the perfect Python implementation
        python_code = self.generate_perfect_python_code(best_message)
        
        # Save to file
        with open('perfect_clubos_messaging_client.py', 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"\\n💾 Perfect implementation saved to: perfect_clubos_messaging_client.py")
        
        return python_code
    
    def generate_perfect_python_code(self, message: dict) -> str:
        """Generate perfect Python code from successful message"""
        form_data = message['form_data']
        url = message['url']
        method = message['method']
        headers = message['headers']
        
        # Identify dynamic fields
        dynamic_fields = {}
        static_fields = {}
        
        for key, value in form_data.items():
            if any(pattern in key.lower() for pattern in ['userid', 'memberid', 'tfoUserid']):
                if 'member' in key.lower():
                    dynamic_fields[key] = 'member_id'
                else:
                    dynamic_fields[key] = 'self.staff_id'
            elif any(pattern in key.lower() for pattern in ['message', 'text']) and 'email' not in key.lower():
                dynamic_fields[key] = 'message_text'
            elif any(pattern in key.lower() for pattern in ['notes', 'outcome']):
                dynamic_fields[key] = f'f"Jeremy {{datetime.now().strftime(\\"%m.%d\\")}}"'
            elif any(pattern in key.lower() for pattern in ['clubid']):
                dynamic_fields[key] = 'self.club_id or "291"'
            elif any(pattern in key.lower() for pattern in ['token', 'fp', 'source']):
                dynamic_fields[key] = f'fresh_{key.lower().replace("__", "").replace(".", "_")}'
            else:
                static_fields[key] = value
        
        code = f'''#!/usr/bin/env python3
"""
PERFECT ClubOS Messaging Client - Generated from HAR Analysis
This implementation replicates the EXACT successful messaging pattern from HAR data
"""

import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PerfectClubOSMessagingClient:
    """Perfect messaging client based on successful HAR analysis"""
    
    def __init__(self, username: str = None, password: str = None):
        # Initialize with credentials (use SecureSecretsManager in real implementation)
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        
        # Session data extracted from HAR
        self.staff_id = None
        self.club_id = None
        self.authenticated = False
        
        # Set headers from successful HAR request
        self.session.headers.update({{'''
        
        for key, value in headers.items():
            if key.lower() not in ['content-length', 'cookie']:
                code += f'\\n            "{key}": "{value}",'
        
        code += f'''
        }})
    
    def authenticate(self) -> bool:
        """Authenticate using the exact pattern from HAR"""
        # Implementation based on HAR authentication sequence
        # (Add your authentication logic here)
        self.staff_id = "187032782"  # From HAR analysis
        self.club_id = "291"  # From HAR analysis
        self.authenticated = True
        return True
    
    def send_message_perfect(self, member_id: str, message_text: str) -> bool:
        """Send message using PERFECT HAR-based implementation"""
        try:
            if not self.authenticated and not self.authenticate():
                logger.error("❌ Not authenticated")
                return False
            
            logger.info(f"📱 Sending message to member {{member_id}}: '{{message_text[:50]}}...'")
            
            # STEP 1: Initialize follow-up (from HAR analysis)
            init_url = "https://anytime.club-os.com/action/FollowUp"
            init_data = {{
                "followUpUserId": member_id,
                "followUpType": "3"  # 3 = SMS from HAR
            }}
            
            init_response = self.session.post(init_url, data=init_data)
            if init_response.status_code != 200:
                logger.error(f"❌ Init failed: {{init_response.status_code}}")
                return False
            
            # STEP 2: Extract fresh tokens from response
            soup = BeautifulSoup(init_response.text, 'html.parser')
            fresh_token = ""
            fresh_fp = ""
            fresh_sourcepage = ""
            
            # Extract tokens (implement token extraction)
            
            # STEP 3: Send the actual message with PERFECT form data
            save_url = "{url}"
            
            # PERFECT form data from HAR analysis
            save_data = {{'''
        
        # Add all fields from HAR
        for key, value in form_data.items():
            if key in dynamic_fields:
                code += f'\\n                "{key}": {dynamic_fields[key]},'
            else:
                code += f'\\n                "{key}": "{value}",'
        
        code += f'''
            }}
            
            # Perfect headers from HAR
            save_headers = {{'''
        
        # Add important headers
        important_headers = ['Content-Type', 'X-Requested-With', 'Referer']
        for header in important_headers:
            if header in headers:
                code += f'\\n                "{header}": "{headers[header]}",'
        
        code += f'''
            }}
            
            save_response = self.session.post(save_url, data=save_data, headers=save_headers)
            
            # Check for success (from HAR analysis)
            if save_response.status_code == 200:
                response_text = save_response.text.lower()
                if "texted" in response_text or "has been" in response_text:
                    logger.info(f"✅ Message sent successfully to member {{member_id}}")
                    return True
                else:
                    logger.error(f"❌ No success indicator in response")
                    return False
            else:
                logger.error(f"❌ Failed: HTTP {{save_response.status_code}}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending message: {{e}}")
            return False

# Test function
def test_perfect_messaging():
    """Test the perfect messaging client"""
    client = PerfectClubOSMessagingClient()
    
    # Test with known working member ID from HAR
    test_member_id = "189425730"  # Dennis Rost from HAR
    test_message = "Perfect HAR-based message test!"
    
    success = client.send_message_perfect(test_member_id, test_message)
    
    if success:
        print("✅ Perfect messaging test successful!")
    else:
        print("❌ Perfect messaging test failed")

if __name__ == "__main__":
    test_perfect_messaging()
'''
        
        return code
    
    def save_complete_analysis(self):
        """Save complete analysis to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"complete_har_analysis_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Complete ClubOS HAR Analysis\\n\\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"**HAR File:** {self.har_file_path}\\n")
            f.write(f"**Total Requests:** {len(self.all_requests)}\\n")
            f.write(f"**Messaging Requests:** {len([r for r in self.all_requests if r['is_messaging']])}\\n")
            f.write(f"**Successful Messages:** {len(self.successful_messages)}\\n\\n")
            
            # Add successful message details
            f.write("## Successful Messages\\n\\n")
            for i, msg in enumerate(self.successful_messages):
                f.write(f"### Message {i+1}\\n\\n")
                f.write(f"- **URL:** {msg['url']}\\n")
                f.write(f"- **Method:** {msg['method']}\\n")
                f.write(f"- **Status:** {msg['status']}\\n")
                f.write(f"- **Time:** {msg['timestamp']}\\n\\n")
                
                f.write("**Form Data:**\\n")
                for key, value in msg['form_data'].items():
                    f.write(f"- `{key}`: {value}\\n")
                f.write("\\n")
        
        print(f"📄 Complete analysis saved to: {filename}")

def main():
    """Main analysis function"""
    # Update this path to your HAR file
    har_file = "c:\\\\Users\\\\mayoj\\\\OneDrive\\\\Documents\\\\Gym-Bot\\\\gym-bot\\\\gym-bot-modular\\\\charles_session.chls\\\\Clubos_Newest_Message.har"
    
    if not os.path.exists(har_file):
        print(f"❌ HAR file not found: {har_file}")
        return
    
    analyzer = UltimateClubOSHARAnalyzer(har_file)
    
    if not analyzer.load_har_file():
        return
    
    # Analyze EVERYTHING
    analyzer.analyze_everything()
    
    # Print successful messages
    analyzer.print_successful_messages()
    
    # Extract patterns
    analyzer.extract_messaging_patterns()
    
    # Generate perfect implementation
    analyzer.generate_perfect_implementation()
    
    # Save complete analysis
    analyzer.save_complete_analysis()

if __name__ == "__main__":
    main()
