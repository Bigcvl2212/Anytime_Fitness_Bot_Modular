#!/usr/bin/env python3
"""
ClubOS Messaging HAR Analyzer
Analyzes HAR file to understand the complete messaging workflow
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urlparse, parse_qs, unquote

class ClubOSMessagingHARAnalyzer:
    """Analyze ClubOS HAR files specifically for messaging workflow"""
    
    def __init__(self, har_file_path: str):
        self.har_file_path = har_file_path
        self.har_data = None
        self.entries = []
        self.messaging_requests = []
        self.form_submissions = []
        self.auth_sequence = []
        self.session_data = {}
        
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
    
    def analyze_messaging_flow(self):
        """Analyze the complete messaging workflow"""
        print("\n🔍 Analyzing messaging workflow...")
        print("=" * 60)
        
        message_sequence = []
        current_sequence = 1
        
        for i, entry in enumerate(self.entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            # Track messaging-related requests
            if self.is_messaging_related(url, request):
                timestamp = entry.get('startedDateTime', '')
                
                analysis = {
                    'sequence': current_sequence,
                    'timestamp': timestamp,
                    'method': method,
                    'url': url,
                    'status': response.get('status', 0),
                    'request_details': self.extract_request_details(request),
                    'response_details': self.extract_response_details(response),
                    'form_data': self.extract_form_data(request),
                    'headers': self.extract_headers(request),
                    'cookies': self.extract_cookies(request)
                }
                
                message_sequence.append(analysis)
                current_sequence += 1
        
        self.messaging_requests = message_sequence
        return message_sequence
    
    def is_messaging_related(self, url: str, request: dict) -> bool:
        """Check if request is messaging-related"""
        messaging_patterns = [
            '/action/FollowUp',
            '/action/Dashboard/member',
            '/action/Api/send-message',
            '/action/Api/follow-up',
            'textMessage',
            'followUpLog',
            'followUpUser',
            'message',
            'sms',
            'email'
        ]
        
        # Check URL patterns
        for pattern in messaging_patterns:
            if pattern.lower() in url.lower():
                return True
        
        # Check form data for messaging fields
        form_data = self.extract_form_data(request)
        if form_data:
            form_str = str(form_data).lower()
            if any(pattern.lower() in form_str for pattern in messaging_patterns):
                return True
        
        return False
    
    def extract_request_details(self, request: dict) -> dict:
        """Extract detailed request information"""
        return {
            'method': request.get('method', ''),
            'url': request.get('url', ''),
            'http_version': request.get('httpVersion', ''),
            'body_size': request.get('bodySize', 0),
            'headers_size': request.get('headersSize', 0)
        }
    
    def extract_response_details(self, response: dict) -> dict:
        """Extract detailed response information"""
        content = response.get('content', {})
        return {
            'status': response.get('status', 0),
            'status_text': response.get('statusText', ''),
            'content_type': content.get('mimeType', ''),
            'content_size': content.get('size', 0),
            'content_preview': content.get('text', '')[:200] if content.get('text') else ''
        }
    
    def extract_form_data(self, request: dict) -> dict:
        """Extract form data from POST requests"""
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
                import json
                form_data = json.loads(text)
            except Exception as e:
                print(f"⚠️ Error parsing JSON data: {e}")
        
        # If no specific handling worked, try to parse the raw text
        if not form_data and text:
            try:
                # Try URL-encoded format even without proper mime type
                pairs = text.split('&')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        form_data[unquote(key)] = unquote(value)
            except:
                # Store raw text for manual inspection
                form_data['_raw_data'] = text
        
        return form_data
    
    def extract_headers(self, request: dict) -> dict:
        """Extract request headers"""
        headers = {}
        for header in request.get('headers', []):
            name = header.get('name', '')
            value = header.get('value', '')
            if name:
                headers[name] = value
        return headers
    
    def extract_cookies(self, request: dict) -> dict:
        """Extract request cookies"""
        cookies = {}
        for cookie in request.get('cookies', []):
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            if name:
                cookies[name] = value
        return cookies
    
    def print_messaging_sequence(self):
        """Print the complete messaging sequence"""
        print(f"\n📨 MESSAGING WORKFLOW SEQUENCE ({len(self.messaging_requests)} requests)")
        print("=" * 80)
        
        for req in self.messaging_requests:
            print(f"\n🔄 Step {req['sequence']}: {req['method']} {req['url']}")
            print(f"   📅 Time: {req['timestamp']}")
            print(f"   📊 Status: {req['status']}")
            
            # Print form data if available
            if req['form_data']:
                print(f"   📝 Form Data:")
                for key, value in req['form_data'].items():
                    # Truncate long values for readability
                    display_value = value[:100] + "..." if len(str(value)) > 100 else value
                    print(f"      {key}: {display_value}")
            
            # Print important headers
            if req['headers']:
                important_headers = ['Content-Type', 'Referer', 'X-Requested-With']
                for header in important_headers:
                    if header in req['headers']:
                        print(f"   📋 {header}: {req['headers'][header]}")
            
            print(f"   📄 Response Preview: {req['response_details']['content_preview']}")
    
    def debug_raw_posts(self):
        """Debug function to inspect raw POST data"""
        print(f"\n🐛 DEBUG: Raw POST Request Analysis")
        print("=" * 60)
        
        for i, entry in enumerate(self.entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            if method == 'POST' and 'FollowUp' in url:
                print(f"\n📋 POST Request #{i+1}")
                print(f"   URL: {url}")
                print(f"   Status: {response.get('status', 0)}")
                
                # Print raw post data
                post_data = request.get('postData', {})
                if post_data:
                    print(f"   Content-Type: {post_data.get('mimeType', 'N/A')}")
                    text = post_data.get('text', '')
                    if text:
                        print(f"   Raw Data Length: {len(text)} chars")
                        print(f"   Raw Data Preview: {text[:300]}...")
                    
                    # Check for params
                    params = post_data.get('params', [])
                    if params:
                        print(f"   Form Params ({len(params)}):")
                        for param in params[:10]:  # Show first 10
                            name = param.get('name', '')
                            value = param.get('value', '')
                            print(f"      {name}: {value[:100] if value else 'N/A'}")
                
                # Check response for success indicators
                response_content = response.get('content', {}).get('text', '')
                if 'texted' in response_content.lower():
                    print(f"   ✅ SUCCESS: Response contains 'texted'")
                    # EXTRACT ALL FORM PARAMETERS FOR SUCCESSFUL REQUESTS
                    params = post_data.get('params', [])
                    print(f"   📋 ALL FORM PARAMETERS ({len(params)}):")
                    for param in params:
                        name = param.get('name', '')
                        value = param.get('value', '')
                        print(f"      {name}: {value}")
                else:
                    print(f"   ❓ Response preview: {response_content[:100]}")
    
    def extract_messaging_patterns(self):
        """Extract patterns for successful messaging"""
        print(f"\n🔍 EXTRACTING MESSAGING PATTERNS")
        print("=" * 50)
        
        successful_requests = []
        form_patterns = {}
        
        for req in self.messaging_requests:
            # Check for successful messaging based on response content
            response_preview = req['response_details']['content_preview'].lower()
            is_success = (req['status'] == 200 and 
                         ('texted' in response_preview or 
                          'emailed' in response_preview or
                          'sent' in response_preview))
            
            if is_success and req['form_data']:
                successful_requests.append(req)
                
                # Collect form field patterns
                for key, value in req['form_data'].items():
                    if key not in form_patterns:
                        form_patterns[key] = []
                    form_patterns[key].append(value)
        
        print(f"✅ Found {len(successful_requests)} successful messaging requests")
        
        # Analyze form patterns
        print(f"\n📋 FORM FIELD PATTERNS:")
        for field, values in form_patterns.items():
            unique_values = list(set(values))
            print(f"   {field}:")
            for value in unique_values[:3]:  # Show first 3 unique values
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"      - {display_value}")
            if len(unique_values) > 3:
                print(f"      ... and {len(unique_values) - 3} more")
        
        return successful_requests, form_patterns
    
    def generate_working_implementation(self):
        """Generate working implementation based on HAR analysis"""
        print(f"\n🚀 GENERATING WORKING IMPLEMENTATION")
        print("=" * 50)
        
        successful_requests, form_patterns = self.extract_messaging_patterns()
        
        if not successful_requests:
            print("❌ No successful messaging requests found")
            return
        
        # Find the most complete form submission
        best_request = max(successful_requests, key=lambda x: len(x['form_data']))
        
        print(f"📋 Best messaging request template:")
        print(f"   URL: {best_request['url']}")
        print(f"   Method: {best_request['method']}")
        print(f"   Form fields ({len(best_request['form_data'])}):")
        
        # Generate Python code
        python_code = self.generate_python_code(best_request)
        
        print(f"\n🐍 PYTHON IMPLEMENTATION:")
        print("-" * 40)
        print(python_code)
        
        return python_code
    
    def generate_python_code(self, request: dict) -> str:
        """Generate Python code based on successful request"""
        form_data = request['form_data']
        url = request['url']
        method = request['method']
        
        code = f'''
# Generated from HAR analysis - Working ClubOS messaging implementation
import requests

def send_clubos_message_har_based(session, member_id, message_text):
    """Send message using HAR-extracted working pattern"""
    
    url = "{url}"
    
    form_data = {{'''
        
        for key, value in form_data.items():
            # Handle dynamic values
            if 'userId' in key.lower() or 'memberid' in key.lower():
                code += f'\n        "{key}": member_id,'
            elif 'message' in key.lower() or 'text' in key.lower():
                code += f'\n        "{key}": message_text,'
            else:
                code += f'\n        "{key}": "{value}",'
        
        code += '''
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    response = session.post(url, data=form_data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Message sent successfully")
        return True
    else:
        print(f"❌ Failed to send message: {response.status_code}")
        return False
'''
        
        return code
    
    def save_analysis_report(self, output_file: str = "messaging_har_analysis.md"):
        """Save complete analysis to markdown file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# ClubOS Messaging HAR Analysis Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**HAR File:** {self.har_file_path}\n")
                f.write(f"**Total Requests:** {len(self.entries)}\n")
                f.write(f"**Messaging Requests:** {len(self.messaging_requests)}\n\n")
                
                f.write("## Messaging Request Sequence\n\n")
                for req in self.messaging_requests:
                    f.write(f"### Step {req['sequence']}: {req['method']} {req['url']}\n\n")
                    f.write(f"- **Status:** {req['status']}\n")
                    f.write(f"- **Time:** {req['timestamp']}\n\n")
                    
                    if req['form_data']:
                        f.write("**Form Data:**\n")
                        for key, value in req['form_data'].items():
                            f.write(f"- `{key}`: {value}\n")
                        f.write("\n")
                
                # Add implementation
                python_code = self.generate_python_code(self.messaging_requests[0]) if self.messaging_requests else ""
                f.write("## Generated Implementation\n\n```python\n")
                f.write(python_code)
                f.write("\n```\n")
            
            print(f"📄 Analysis report saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")

def main():
    """Main analysis function"""
    har_file = "c:\\Users\\mayoj\\OneDrive\\Documents\\Gym-Bot\\gym-bot\\gym-bot-modular\\charles_session.chls\\Clubos_Newest_Message.har"
    
    analyzer = ClubOSMessagingHARAnalyzer(har_file)
    
    if not analyzer.load_har_file():
        return
    
    # Debug raw POST data first
    analyzer.debug_raw_posts()
    
    # Analyze the messaging workflow
    analyzer.analyze_messaging_flow()
    
    # Print the sequence
    analyzer.print_messaging_sequence()
    
    # Extract patterns and generate implementation
    analyzer.generate_working_implementation()
    
    # Save report
    analyzer.save_analysis_report("clubos_messaging_har_analysis.md")

if __name__ == "__main__":
    main()
