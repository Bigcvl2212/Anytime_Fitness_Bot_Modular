#!/usr/bin/env python3
"""
Analyze HAR files to extract the EXACT authentication flow that worked successfully.
Instead of guessing, we'll parse the actual HTTP requests and responses.
"""

import json
import os
import base64
import urllib.parse
from datetime import datetime

class HARAuthFlowAnalyzer:
    def __init__(self):
        self.har_folder = "charles_session.chls"
        self.auth_requests = []
        self.successful_tokens = []
        
    def analyze_all_har_files(self):
        """Analyze all HAR files to find successful authentication flows"""
        print("🔍 Analyzing HAR files for successful authentication flows...")
        
        if not os.path.exists(self.har_folder):
            print(f"❌ HAR folder not found: {self.har_folder}")
            return
            
        har_files = [f for f in os.listdir(self.har_folder) if f.endswith('.har')]
        print(f"📁 Found {len(har_files)} HAR files")
        
        for har_file in har_files:
            print(f"\n📊 Analyzing: {har_file}")
            self.analyze_har_file(os.path.join(self.har_folder, har_file))
            
        self.print_analysis_results()
        
    def analyze_har_file(self, file_path):
        """Analyze a single HAR file for authentication patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
                
            entries = har_data.get('log', {}).get('entries', [])
            print(f"  📊 Found {len(entries)} HTTP requests")
            
            # Look for authentication-related requests
            auth_patterns = [
                'login',
                'auth',
                'token',
                'session',
                'clubhub.onlineapp.com',
                'api/v1/users/sign_in',
                'api/v1/session'
            ]
            
            for entry in entries:
                request = entry.get('request', {})
                response = entry.get('response', {})
                url = request.get('url', '')
                method = request.get('method', '')
                
                # Check if this looks like an auth request
                if any(pattern in url.lower() for pattern in auth_patterns):
                    self.analyze_auth_request(entry, file_path)
                    
                # Look for responses with tokens
                if response.get('status') == 200:
                    self.check_for_tokens(entry, file_path)
                    
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path}: {e}")
            
    def analyze_auth_request(self, entry, source_file):
        """Analyze a specific authentication request"""
        request = entry['request']
        response = entry['response']
        
        auth_info = {
            'source_file': os.path.basename(source_file),
            'url': request['url'],
            'method': request['method'],
            'status': response['status'],
            'headers': request.get('headers', []),
            'post_data': request.get('postData', {}),
            'response_headers': response.get('headers', []),
            'response_content': None
        }
        
        # Extract response content if available
        content = response.get('content', {})
        if content.get('text'):
            try:
                if content.get('encoding') == 'base64':
                    auth_info['response_content'] = base64.b64decode(content['text']).decode('utf-8')
                else:
                    auth_info['response_content'] = content['text']
            except:
                auth_info['response_content'] = "Could not decode content"
                
        self.auth_requests.append(auth_info)
        
        print(f"    🔐 Auth request: {request['method']} {request['url']} -> {response['status']}")
        
    def check_for_tokens(self, entry, source_file):
        """Check response for authentication tokens"""
        response = entry['response']
        content = response.get('content', {})
        
        if not content.get('text'):
            return
            
        try:
            text = content['text']
            if content.get('encoding') == 'base64':
                text = base64.b64decode(text).decode('utf-8')
                
            # Look for JWT tokens
            if 'eyJ' in text:  # JWT tokens start with eyJ
                self.extract_tokens_from_text(text, entry, source_file)
                
            # Look for bearer tokens in headers
            for header in response.get('headers', []):
                if header.get('name', '').lower() == 'authorization':
                    value = header.get('value', '')
                    if 'Bearer' in value:
                        token_info = {
                            'source_file': os.path.basename(source_file),
                            'url': entry['request']['url'],
                            'type': 'Bearer Header',
                            'token': value,
                            'timestamp': entry.get('startedDateTime', '')
                        }
                        self.successful_tokens.append(token_info)
                        
        except Exception as e:
            pass  # Skip problematic content
            
    def extract_tokens_from_text(self, text, entry, source_file):
        """Extract JWT tokens from response text"""
        import re
        
        # Find JWT patterns
        jwt_pattern = r'eyJ[A-Za-z0-9+/=]+'
        tokens = re.findall(jwt_pattern, text)
        
        for token in tokens:
            if len(token) > 50:  # Filter out short matches
                token_info = {
                    'source_file': os.path.basename(source_file),
                    'url': entry['request']['url'],
                    'type': 'JWT Response',
                    'token': token,
                    'timestamp': entry.get('startedDateTime', ''),
                    'context': text[:500] + '...' if len(text) > 500 else text
                }
                self.successful_tokens.append(token_info)
                
    def print_analysis_results(self):
        """Print comprehensive analysis results"""
        print(f"\n" + "="*80)
        print(f"🔍 AUTHENTICATION FLOW ANALYSIS RESULTS")
        print(f"="*80)
        
        print(f"\n📊 AUTHENTICATION REQUESTS FOUND: {len(self.auth_requests)}")
        print("-" * 50)
        
        for i, auth in enumerate(self.auth_requests, 1):
            print(f"\n{i}. {auth['source_file']} - {auth['method']} {auth['url']}")
            print(f"   Status: {auth['status']}")
            
            # Print request headers
            print("   Request Headers:")
            for header in auth['headers']:
                name = header.get('name', '')
                value = header.get('value', '')
                if name.lower() in ['authorization', 'cookie', 'x-csrf-token', 'content-type']:
                    print(f"     {name}: {value}")
                    
            # Print POST data
            if auth['post_data']:
                print("   POST Data:")
                post_data = auth['post_data']
                if 'text' in post_data:
                    try:
                        parsed = urllib.parse.parse_qs(post_data['text'])
                        for key, values in parsed.items():
                            print(f"     {key}: {values[0] if values else ''}")
                    except:
                        print(f"     Raw: {post_data['text'][:200]}...")
                        
            # Print response content (truncated)
            if auth['response_content']:
                print("   Response Content:")
                content = auth['response_content']
                if len(content) > 300:
                    print(f"     {content[:300]}...")
                else:
                    print(f"     {content}")
                    
        print(f"\n🎯 SUCCESSFUL TOKENS FOUND: {len(self.successful_tokens)}")
        print("-" * 50)
        
        for i, token in enumerate(self.successful_tokens, 1):
            print(f"\n{i}. {token['source_file']} - {token['type']}")
            print(f"   URL: {token['url']}")
            print(f"   Timestamp: {token['timestamp']}")
            print(f"   Token: {token['token'][:100]}...")
            
            # If it's a JWT, try to decode header
            if token['token'].startswith('eyJ'):
                try:
                    import jwt
                    header = jwt.get_unverified_header(token['token'])
                    payload = jwt.decode(token['token'], options={"verify_signature": False})
                    print(f"   JWT Header: {header}")
                    print(f"   JWT Payload: {payload}")
                except:
                    print("   (Could not decode JWT)")
                    
        # Generate authentication script
        self.generate_auth_script()
        
    def generate_auth_script(self):
        """Generate a script to replicate the successful authentication"""
        print(f"\n" + "="*80)
        print(f"🚀 GENERATING AUTHENTICATION REPLICATION SCRIPT")
        print(f"="*80)
        
        # Find the most promising authentication flow
        successful_auth = None
        for auth in self.auth_requests:
            if auth['status'] == 200 and 'sign_in' in auth['url']:
                successful_auth = auth
                break
                
        if not successful_auth and self.auth_requests:
            successful_auth = self.auth_requests[0]  # Use first available
            
        if successful_auth:
            script_content = self.create_replication_script(successful_auth)
            
            with open('replicate_successful_auth.py', 'w') as f:
                f.write(script_content)
                
            print("✅ Created replicate_successful_auth.py")
            print("🔧 This script replicates the exact authentication flow from HAR data")
        else:
            print("❌ No suitable authentication flow found to replicate")
            
    def create_replication_script(self, auth_request):
        """Create a Python script that replicates the successful auth flow"""
        script = f'''#!/usr/bin/env python3
"""
Replicate the exact authentication flow found in HAR file: {auth_request['source_file']}
This script mimics the successful request that was captured.
"""

import requests
import json
import urllib.parse

def replicate_successful_auth():
    """Replicate the exact authentication request from HAR data"""
    
    # URL from successful request
    url = "{auth_request['url']}"
    
    # Headers from successful request
    headers = {{'''
        
        # Add headers
        for header in auth_request['headers']:
            name = header.get('name', '')
            value = header.get('value', '')
            if name.lower() not in ['content-length', 'host']:
                script += f'\n        "{name}": "{value}",'
                
        script += '''
    }
    
    # POST data from successful request'''
        
        if auth_request['post_data']:
            post_data = auth_request['post_data']
            if 'text' in post_data:
                script += f'''
    data = "{post_data['text']}"'''
            else:
                script += '''
    data = None'''
        else:
            script += '''
    data = None'''
            
        script += f'''
    
    print("🔄 Replicating authentication request...")
    print(f"URL: {{url}}")
    print(f"Method: {auth_request['method']}")
    
    try:
        response = requests.{auth_request['method'].lower()}(
            url,
            headers=headers,
            data=data,
            verify=False,
            timeout=30
        )
        
        print(f"Status: {{response.status_code}}")
        print(f"Response Headers: {{dict(response.headers)}}")
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            content = response.text
            print(f"Response: {{content[:500]}}...")
            
            # Look for tokens in response
            if 'token' in content.lower() or 'bearer' in content.lower():
                print("🎯 Found token in response!")
                
            return response
        else:
            print(f"❌ Authentication failed: {{response.status_code}}")
            print(f"Response: {{response.text}}")
            return None
            
    except Exception as e:
        print(f"❌ Error during authentication: {{e}}")
        return None

if __name__ == "__main__":
    replicate_successful_auth()
'''
        
        return script

def main():
    analyzer = HARAuthFlowAnalyzer()
    analyzer.analyze_all_har_files()

if __name__ == "__main__":
    main()
