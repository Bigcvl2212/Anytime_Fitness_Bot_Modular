#!/usr/bin/env python3
"""
ClubOS HAR File Analyzer
Analyzes the captured Charles Proxy HAR file to understand ClubOS calendar workflow
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urlparse, parse_qs

class ClubOSHARAnalyzer:
    """Analyze ClubOS HAR files to understand the calendar workflow"""
    
    def __init__(self, har_file_path: str):
        self.har_file_path = har_file_path
        self.har_data = None
        self.entries = []
        self.auth_requests = []
        self.calendar_requests = []
        self.api_requests = []
        self.session_cookies = {}
        self.csrf_tokens = {}
        
    def load_har_file(self) -> bool:
        """Load and parse the HAR file"""
        try:
            print(f"Loading HAR file: {self.har_file_path}")
            
            with open(self.har_file_path, 'r', encoding='utf-8') as f:
                self.har_data = json.load(f)
            
            self.entries = self.har_data.get('log', {}).get('entries', [])
            print(f"Loaded {len(self.entries)} HTTP requests from HAR file")
            return True
            
        except Exception as e:
            print(f"Error loading HAR file: {e}")
            return False
    
    def analyze_requests(self):
        """Analyze all requests in the HAR file"""
        print("\nAnalyzing requests...")
        
        for i, entry in enumerate(self.entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            status_code = response.get('status', 0)
            
            # Categorize requests
            if any(keyword in url.lower() for keyword in ['login', 'auth', 'signin']):
                self.auth_requests.append(entry)
            elif any(keyword in url.lower() for keyword in ['calendar', 'appointment', 'schedule']):
                self.calendar_requests.append(entry)
            elif '/api/' in url or url.endswith('.json'):
                self.api_requests.append(entry)
            
            # Extract session cookies
            self._extract_cookies(entry)
            
            # Extract CSRF tokens
            self._extract_csrf_tokens(entry)
        
        print(f"Found {len(self.auth_requests)} authentication requests")
        print(f"Found {len(self.calendar_requests)} calendar requests")
        print(f"Found {len(self.api_requests)} API requests")
    
    def _extract_cookies(self, entry):
        """Extract session cookies from request/response"""
        request = entry.get('request', {})
        response = entry.get('response', {})
        
        # Extract from request cookies
        for cookie in request.get('cookies', []):
            name = cookie.get('name')
            value = cookie.get('value')
            if name in ['JSESSIONID', 'loggedInUserId', 'delegatedUserId', 'apiV3AccessToken']:
                self.session_cookies[name] = value
        
        # Extract from response Set-Cookie headers
        for header in response.get('headers', []):
            if header.get('name', '').lower() == 'set-cookie':
                self._parse_set_cookie(header.get('value', ''))
    
    def _parse_set_cookie(self, cookie_header):
        """Parse Set-Cookie header"""
        if '=' in cookie_header:
            parts = cookie_header.split(';')[0].split('=', 1)
            if len(parts) == 2:
                name, value = parts
                if name in ['JSESSIONID', 'loggedInUserId', 'delegatedUserId', 'apiV3AccessToken']:
                    self.session_cookies[name] = value
    
    def _extract_csrf_tokens(self, entry):
        """Extract CSRF tokens from form data"""
        request = entry.get('request', {})
        post_data = request.get('postData', {})
        
        if post_data.get('mimeType') == 'application/x-www-form-urlencoded':
            for param in post_data.get('params', []):
                name = param.get('name', '')
                value = param.get('value', '')
                if any(token_name in name.lower() for token_name in ['csrf', 'token', '_source', '__fp']):
                    self.csrf_tokens[name] = value
    
    def analyze_authentication_flow(self):
        """Analyze the authentication flow"""
        print("\n=== AUTHENTICATION FLOW ANALYSIS ===")
        
        print(f"\nAuthentication Requests ({len(self.auth_requests)}):")
        for i, entry in enumerate(self.auth_requests):
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            print(f"\n{i+1}. {request.get('method')} {request.get('url')}")
            print(f"   Status: {response.get('status')}")
            
            # Show form data for login attempts
            post_data = request.get('postData', {})
            if post_data.get('mimeType') == 'application/x-www-form-urlencoded':
                print("   Form Data:")
                for param in post_data.get('params', []):
                    name = param.get('name', '')
                    value = param.get('value', '')
                    if 'password' in name.lower():
                        value = '*' * len(value)
                    print(f"     {name}: {value}")
        
        print(f"\nSession Cookies Found:")
        for name, value in self.session_cookies.items():
            display_value = value[:20] + '...' if len(value) > 20 else value
            print(f"   {name}: {display_value}")
        
        print(f"\nCSRF Tokens Found:")
        for name, value in self.csrf_tokens.items():
            display_value = value[:20] + '...' if len(value) > 20 else value
            print(f"   {name}: {display_value}")
    
    def analyze_calendar_flow(self):
        """Analyze calendar-specific requests"""
        print("\n=== CALENDAR FLOW ANALYSIS ===")
        
        print(f"\nCalendar Requests ({len(self.calendar_requests)}):")
        for i, entry in enumerate(self.calendar_requests):
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            print(f"\n{i+1}. {request.get('method')} {request.get('url')}")
            print(f"   Status: {response.get('status')}")
            
            # Check for redirects
            if response.get('status') in [301, 302, 303, 307, 308]:
                for header in response.get('headers', []):
                    if header.get('name', '').lower() == 'location':
                        print(f"   Redirect to: {header.get('value')}")
            
            # Show query parameters
            parsed_url = urlparse(request.get('url', ''))
            if parsed_url.query:
                params = parse_qs(parsed_url.query)
                print("   Query Parameters:")
                for key, values in params.items():
                    print(f"     {key}: {values[0] if values else ''}")
    
    def analyze_api_requests(self):
        """Analyze API requests"""
        print("\n=== API REQUESTS ANALYSIS ===")
        
        # Group API requests by endpoint
        api_groups = {}
        for entry in self.api_requests:
            request = entry.get('request', {})
            url = request.get('url', '')
            
            # Extract endpoint path
            parsed_url = urlparse(url)
            endpoint = parsed_url.path
            
            if endpoint not in api_groups:
                api_groups[endpoint] = []
            api_groups[endpoint].append(entry)
        
        print(f"\nAPI Endpoints Found ({len(api_groups)}):")
        for endpoint, entries in api_groups.items():
            print(f"\n{endpoint} ({len(entries)} requests):")
            
            # Show details for first few requests
            for i, entry in enumerate(entries[:3]):
                request = entry.get('request', {})
                response = entry.get('response', {})
                
                print(f"   {i+1}. {request.get('method')} - Status: {response.get('status')}")
                
                # Show authorization headers
                for header in request.get('headers', []):
                    if header.get('name', '').lower() == 'authorization':
                        auth_value = header.get('value', '')
                        if len(auth_value) > 30:
                            auth_value = auth_value[:30] + '...'
                        print(f"      Authorization: {auth_value}")
                
                # Show response content type
                for header in response.get('headers', []):
                    if header.get('name', '').lower() == 'content-type':
                        print(f"      Content-Type: {header.get('value')}")
            
            if len(entries) > 3:
                print(f"   ... and {len(entries) - 3} more requests")
    
    def find_critical_requests(self):
        """Find the most critical requests for calendar access"""
        print("\n=== CRITICAL REQUESTS FOR CALENDAR ACCESS ===")
        
        critical_patterns = [
            '/action/Calendar',
            '/api/calendar/events',
            '/api/staff/',
            'delegate',
            'jeremy',
            '187032782'
        ]
        
        critical_requests = []
        
        for entry in self.entries:
            request = entry.get('request', {})
            url = request.get('url', '').lower()
            
            for pattern in critical_patterns:
                if pattern.lower() in url:
                    critical_requests.append(entry)
                    break
        
        print(f"\nFound {len(critical_requests)} critical requests:")
        
        for i, entry in enumerate(critical_requests):
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            print(f"\n{i+1}. {request.get('method')} {request.get('url')}")
            print(f"   Status: {response.get('status')}")
            
            # Show important headers
            auth_header = None
            for header in request.get('headers', []):
                if header.get('name', '').lower() == 'authorization':
                    auth_header = header.get('value', '')
                    break
            
            if auth_header:
                display_auth = auth_header[:50] + '...' if len(auth_header) > 50 else auth_header
                print(f"   Authorization: {display_auth}")
            
            # Show form data or query params
            post_data = request.get('postData', {})
            if post_data.get('mimeType') == 'application/x-www-form-urlencoded':
                print(f"   Form Data: {len(post_data.get('params', []))} fields")
            
            parsed_url = urlparse(request.get('url', ''))
            if parsed_url.query:
                print(f"   Query Params: {len(parse_qs(parsed_url.query))} params")
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n=== RECOMMENDATIONS ===")
        
        recommendations = []
        
        # Check authentication
        if self.session_cookies.get('JSESSIONID'):
            recommendations.append("✓ JSESSIONID found - session-based authentication is working")
        else:
            recommendations.append("✗ No JSESSIONID found - session authentication may be failing")
        
        if self.session_cookies.get('apiV3AccessToken'):
            recommendations.append("✓ API v3 access token found - JWT authentication available")
        else:
            recommendations.append("✗ No API v3 access token - may need JWT token management")
        
        if self.session_cookies.get('delegatedUserId'):
            recommendations.append("✓ Delegated user ID found - delegate functionality is active")
        else:
            recommendations.append("✗ No delegated user ID - may need delegate step for manager access")
        
        # Check calendar access
        calendar_success = any(
            entry.get('response', {}).get('status') == 200 
            for entry in self.calendar_requests
        )
        
        if calendar_success:
            recommendations.append("✓ Successful calendar requests found")
        else:
            recommendations.append("✗ No successful calendar requests - check authentication flow")
        
        # Check API access
        api_success = any(
            entry.get('response', {}).get('status') == 200 
            for entry in self.api_requests
        )
        
        if api_success:
            recommendations.append("✓ Successful API requests found")
        else:
            recommendations.append("✗ No successful API requests - may need proper authorization")
        
        for rec in recommendations:
            print(f"   {rec}")
        
        print(f"\nNext Steps:")
        print(f"1. Implement session management using the found cookies")
        print(f"2. Include delegate step if delegatedUserId is present")
        print(f"3. Use JWT tokens for API authentication if available")
        print(f"4. Follow the exact request sequence from successful flows")
    
    def export_analysis(self, output_file: str):
        """Export analysis results to file"""
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'har_file': self.har_file_path,
            'total_requests': len(self.entries),
            'auth_requests': len(self.auth_requests),
            'calendar_requests': len(self.calendar_requests),
            'api_requests': len(self.api_requests),
            'session_cookies': self.session_cookies,
            'csrf_tokens': self.csrf_tokens
        }
        
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\nAnalysis exported to: {output_file}")

def main():
    """Main analysis function"""
    print("ClubOS HAR File Analyzer")
    print("=" * 40)
    
    # Use the HAR file location
    har_file = "charles_session.chls/Training_payments.har"
    
    if not os.path.exists(har_file):
        print(f"HAR file not found: {har_file}")
        print("Please ensure the file exists and try again.")
        return
    
    # Create analyzer
    analyzer = ClubOSHARAnalyzer(har_file)
    
    # Load and analyze
    if not analyzer.load_har_file():
        return
    
    analyzer.analyze_requests()
    analyzer.analyze_authentication_flow()
    analyzer.analyze_calendar_flow()
    analyzer.analyze_api_requests()
    analyzer.find_critical_requests()
    analyzer.generate_recommendations()
    
    # Export results
    os.makedirs("data", exist_ok=True)
    output_file = f"data/har_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analyzer.export_analysis(output_file)

if __name__ == "__main__":
    main()
