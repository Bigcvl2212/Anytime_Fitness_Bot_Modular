#!/usr/bin/env python3
"""
Analyze HAR files to find the EXACT API calls that were used to refresh prospects and members list
Stop guessing and find the actual working requests
"""

import json
import os
import base64
import urllib.parse
from datetime import datetime

class HARProspectsAnalyzer:
    def __init__(self):
        self.har_folder = "charles_session.chls"
        self.prospect_requests = []
        self.member_requests = []
        
    def analyze_har_files_for_prospects(self):
        """Find the exact API calls used to get prospects and members"""
        print("🔍 Analyzing HAR files for prospect/member API calls...")
        
        if not os.path.exists(self.har_folder):
            print(f"❌ HAR folder not found: {self.har_folder}")
            return
            
        har_files = [f for f in os.listdir(self.har_folder) if f.endswith('.har')]
        print(f"📁 Found {len(har_files)} HAR files")
        
        for har_file in har_files:
            print(f"\n📊 Analyzing: {har_file}")
            self.analyze_har_file_for_data_requests(os.path.join(self.har_folder, har_file))
            
        self.print_findings()
        
    def analyze_har_file_for_data_requests(self, file_path):
        """Analyze HAR file specifically for prospect/member data requests"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
                
            entries = har_data.get('log', {}).get('entries', [])
            print(f"  📊 Found {len(entries)} HTTP requests")
            
            # Look for prospect/member related requests
            data_patterns = [
                'prospect',
                'member',
                'contact',
                'people',
                'club/1156',
                'clubs/1156',
                'lead'
            ]
            
            for entry in entries:
                request = entry.get('request', {})
                response = entry.get('response', {})
                url = request.get('url', '')
                method = request.get('method', '')
                
                # Check if this looks like a data request
                if any(pattern in url.lower() for pattern in data_patterns):
                    self.analyze_data_request(entry, file_path)
                    
        except Exception as e:
            print(f"  ❌ Error analyzing {file_path}: {e}")
            
    def analyze_data_request(self, entry, source_file):
        """Analyze a specific data request for prospects/members"""
        request = entry['request']
        response = entry['response']
        url = request['url']
        
        # Parse URL and query parameters
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        request_info = {
            'source_file': os.path.basename(source_file),
            'url': url,
            'base_url': f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
            'method': request['method'],
            'status': response['status'],
            'query_params': query_params,
            'headers': {h['name']: h['value'] for h in request.get('headers', [])},
            'post_data': request.get('postData', {}),
            'response_size': len(response.get('content', {}).get('text', '')),
            'timestamp': entry.get('startedDateTime', '')
        }
        
        # Check response content for data count
        content = response.get('content', {})
        if content.get('text') and response['status'] == 200:
            try:
                text = content['text']
                if content.get('encoding') == 'base64':
                    text = base64.b64decode(text).decode('utf-8')
                    
                # Try to parse as JSON to count records
                try:
                    data = json.loads(text)
                    if isinstance(data, list):
                        request_info['record_count'] = len(data)
                        request_info['sample_record'] = data[0] if data else None
                    elif isinstance(data, dict):
                        # Look for arrays in the response
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                request_info['record_count'] = len(value)
                                request_info['data_key'] = key
                                request_info['sample_record'] = value[0] if value else None
                                break
                except json.JSONDecodeError:
                    request_info['record_count'] = 'not_json'
                    
            except Exception as e:
                request_info['parse_error'] = str(e)
        
        # Categorize the request
        if 'prospect' in url.lower():
            self.prospect_requests.append(request_info)
        elif 'member' in url.lower():
            self.member_requests.append(request_info)
        else:
            # Could be either, add to both for analysis
            self.prospect_requests.append(request_info)
            self.member_requests.append(request_info)
            
        print(f"    📋 Data request: {request['method']} {url} -> {response['status']} ({request_info.get('record_count', '?')} records)")
        
    def print_findings(self):
        """Print analysis results focusing on the highest record counts"""
        print(f"\n" + "="*80)
        print(f"🎯 PROSPECT/MEMBER API ANALYSIS RESULTS")
        print(f"="*80)
        
        print(f"\n📊 PROSPECT REQUESTS FOUND: {len(self.prospect_requests)}")
        print("-" * 50)
        
        # Sort by record count (highest first)
        prospect_requests = sorted(
            [r for r in self.prospect_requests if isinstance(r.get('record_count'), int)],
            key=lambda x: x.get('record_count', 0),
            reverse=True
        )
        
        for i, req in enumerate(prospect_requests[:10], 1):  # Top 10
            print(f"\n{i}. {req['source_file']} - {req['method']} {req['base_url']}")
            print(f"   Records: {req.get('record_count', 'unknown')}")
            print(f"   Status: {req['status']}")
            print(f"   Query Params: {req['query_params']}")
            
            # Show important headers
            important_headers = ['authorization', 'content-type', 'api-version']
            for header in important_headers:
                if header in req['headers']:
                    value = req['headers'][header]
                    if 'bearer' in value.lower():
                        value = f"Bearer {value.split('Bearer ')[-1][:20]}..."
                    print(f"   {header}: {value}")
        
        print(f"\n🏢 MEMBER REQUESTS FOUND: {len(self.member_requests)}")
        print("-" * 50)
        
        member_requests = sorted(
            [r for r in self.member_requests if isinstance(r.get('record_count'), int)],
            key=lambda x: x.get('record_count', 0),
            reverse=True
        )
        
        for i, req in enumerate(member_requests[:10], 1):  # Top 10
            print(f"\n{i}. {req['source_file']} - {req['method']} {req['base_url']}")
            print(f"   Records: {req.get('record_count', 'unknown')}")
            print(f"   Status: {req['status']}")
            print(f"   Query Params: {req['query_params']}")
        
        # Generate the exact replication script
        self.generate_replication_script(prospect_requests, member_requests)
        
    def generate_replication_script(self, prospect_requests, member_requests):
        """Generate script that replicates the highest-record-count requests"""
        print(f"\n" + "="*80)
        print(f"🚀 GENERATING EXACT REPLICATION SCRIPT")
        print(f"="*80)
        
        best_prospect_req = prospect_requests[0] if prospect_requests else None
        best_member_req = member_requests[0] if member_requests else None
        
        if not best_prospect_req and not best_member_req:
            print("❌ No suitable requests found to replicate")
            return
            
        script_content = f'''#!/usr/bin/env python3
"""
EXACT replication of the HAR file requests that got the most prospect/member data
Generated from HAR analysis on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import requests
import json

class HARReplicator:
    def __init__(self):
        self.session = requests.Session()
        
    def authenticate(self):
        """Add your authentication here"""
        # TODO: Add authentication logic
        pass
        
    def replicate_best_prospect_request(self):
        """Replicate the request that returned the most prospects"""'''
        
        if best_prospect_req:
            script_content += f'''
        print("🎯 Replicating best prospect request...")
        print("Source: {best_prospect_req['source_file']}")
        print("Original record count: {best_prospect_req.get('record_count', 'unknown')}")
        
        url = "{best_prospect_req['base_url']}"
        params = {json.dumps(best_prospect_req['query_params'], indent=12)}
        
        headers = {json.dumps({k: v for k, v in best_prospect_req['headers'].items() 
                              if k.lower() not in ['host', 'content-length']}, indent=12)}
        
        response = self.session.get(url, params=params, headers=headers)
        print(f"Status: {{response.status_code}}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Retrieved {{len(data)}} prospects")
                return data
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"✅ Retrieved {{len(value)}} prospects from key '{{key}}'")
                        return value
        else:
            print(f"❌ Request failed: {{response.text}}")
        return []'''
        
        if best_member_req:
            script_content += f'''
            
    def replicate_best_member_request(self):
        """Replicate the request that returned the most members"""
        print("🏢 Replicating best member request...")
        print("Source: {best_member_req['source_file']}")
        print("Original record count: {best_member_req.get('record_count', 'unknown')}")
        
        url = "{best_member_req['base_url']}"
        params = {json.dumps(best_member_req['query_params'], indent=12)}
        
        headers = {json.dumps({k: v for k, v in best_member_req['headers'].items() 
                              if k.lower() not in ['host', 'content-length']}, indent=12)}
        
        response = self.session.get(url, params=params, headers=headers)
        print(f"Status: {{response.status_code}}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Retrieved {{len(data)}} members")
                return data
            elif isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"✅ Retrieved {{len(value)}} members from key '{{key}}'")
                        return value
        else:
            print(f"❌ Request failed: {{response.text}}")
        return []'''
            
        script_content += '''

if __name__ == "__main__":
    replicator = HARReplicator()
    replicator.authenticate()
    
    prospects = replicator.replicate_best_prospect_request()
    members = replicator.replicate_best_member_request()
    
    print(f"\\n🎉 Total retrieved: {len(prospects)} prospects + {len(members)} members = {len(prospects) + len(members)} total")
'''
        
        with open('har_exact_replication.py', 'w') as f:
            f.write(script_content)
            
        print("✅ Created har_exact_replication.py")
        print("🔧 This script replicates the exact requests that returned the most data")

def main():
    analyzer = HARProspectsAnalyzer()
    analyzer.analyze_har_files_for_prospects()

if __name__ == "__main__":
    main()
