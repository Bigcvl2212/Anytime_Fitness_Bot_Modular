#!/usr/bin/env python3
"""
Analyze HAR file to extract the complete sequence of API calls made when viewing an agreement.
This will help us understand what the browser does when you click on an agreement link.
"""
import json
import re
from urllib.parse import urlparse, parse_qs

def analyze_agreement_api_sequence(har_file_path):
    """Extract all API calls related to agreements and their sequence."""
    print(f"🔍 Analyzing agreement API sequence from: {har_file_path}")
    
    try:
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data.get('log', {}).get('entries', [])
        print(f"📄 Found {len(entries)} total HAR entries")
        
        # Find all agreement-related requests
        agreement_requests = []
        
        for i, entry in enumerate(entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            # Look for agreement-related URLs
            if any(pattern in url.lower() for pattern in [
                'agreement', 'package_agreement', 'billing_status', 
                'salespeople', 'total_value', '/v2/', 'clubservices'
            ]):
                parsed_url = urlparse(url)
                
                # Extract request details
                req_info = {
                    'sequence': i,
                    'method': method,
                    'url': url,
                    'path': parsed_url.path,
                    'query_params': parse_qs(parsed_url.query),
                    'headers': {h['name']: h['value'] for h in request.get('headers', [])},
                    'status_code': response.get('status', 0),
                    'response_size': response.get('content', {}).get('size', 0),
                    'timing': entry.get('time', 0)
                }
                
                # Extract agreement ID if present
                agreement_id_match = re.search(r'/(\d{6,})', url)
                if agreement_id_match:
                    req_info['agreement_id'] = agreement_id_match.group(1)
                
                agreement_requests.append(req_info)
        
        print(f"\n🎯 Found {len(agreement_requests)} agreement-related requests")
        
        if not agreement_requests:
            print("❌ No agreement-related requests found")
            return
        
        # Group by agreement ID to understand the complete flow for each agreement
        by_agreement_id = {}
        
        for req in agreement_requests:
            agreement_id = req.get('agreement_id', 'unknown')
            if agreement_id not in by_agreement_id:
                by_agreement_id[agreement_id] = []
            by_agreement_id[agreement_id].append(req)
        
        # Analyze each agreement's API call pattern
        print(f"\n📋 Agreement API patterns found:")
        
        for agreement_id, requests in by_agreement_id.items():
            print(f"\n🔹 Agreement ID: {agreement_id}")
            print(f"   📊 Total API calls: {len(requests)}")
            
            # Sort by sequence to show the order
            requests.sort(key=lambda x: x['sequence'])
            
            for req in requests:
                print(f"   {req['sequence']:3d}. {req['method']} {req['path']}")
                print(f"        Status: {req['status_code']}, Size: {req['response_size']} bytes")
                
                # Show important headers
                important_headers = ['authorization', 'referer', 'x-requested-with']
                for header in important_headers:
                    if header in req['headers']:
                        value = req['headers'][header]
                        if header == 'authorization' and len(value) > 20:
                            value = value[:20] + "..."
                        print(f"        {header.title()}: {value}")
                print()
        
        # Look for the most complete agreement (most API calls)
        if by_agreement_id:
            most_complete = max(by_agreement_id.items(), key=lambda x: len(x[1]))
            agreement_id, requests = most_complete
            
            print(f"\n🏆 Most complete agreement flow (ID: {agreement_id}) - {len(requests)} API calls:")
            
            # Create the API call sequence
            api_calls = []
            for req in sorted(requests, key=lambda x: x['sequence']):
                api_calls.append({
                    'method': req['method'],
                    'url': req['url'],
                    'path': req['path'],
                    'status': req['status_code'],
                    'headers': req['headers']
                })
            
            # Save the complete sequence for implementation
            sequence_file = f"data/api_references/agreement_{agreement_id}_api_sequence.json"
            with open(sequence_file, 'w', encoding='utf-8') as f:
                json.dump(api_calls, f, indent=2)
            
            print(f"💾 Saved complete API sequence to: {sequence_file}")
            
            # Create a Python implementation template
            template_file = f"data/api_references/agreement_{agreement_id}_implementation.py"
            create_implementation_template(api_calls, agreement_id, template_file)
            
            print(f"🛠️ Created implementation template: {template_file}")
        
    except Exception as e:
        print(f"❌ Error analyzing HAR file: {e}")

def create_implementation_template(api_calls, agreement_id, output_file):
    """Create a Python template for making all the API calls in sequence."""
    
    template = f'''#!/usr/bin/env python3
"""
Implementation template for agreement {agreement_id} API call sequence.
Based on actual browser behavior captured in HAR file.
"""

def get_complete_agreement_data(session, agreement_id="{agreement_id}"):
    """Make all API calls in the correct sequence to get complete agreement data."""
    base_url = "https://anytime.club-os.com"
    results = {{}}
    
    try:
'''
    
    for i, call in enumerate(api_calls):
        method = call['method']
        path = call['path']
        
        # Extract the endpoint name for the result key
        endpoint_name = path.split('/')[-1] if '/' in path else f"call_{i}"
        if endpoint_name.isdigit():
            endpoint_name = path.split('/')[-2] if path.count('/') > 1 else f"call_{i}"
        
        template += f'''
        # API Call {i+1}: {method} {path}
        headers_{i} = {{
'''
        
        # Add important headers
        for header_name, header_value in call['headers'].items():
            if header_name.lower() in ['authorization', 'referer', 'x-requested-with', 'accept']:
                template += f'            "{header_name}": "{header_value}",\n'
        
        template += f'''        }}
        
        response_{i} = session.{method.lower()}(
            f"{{base_url}}{path}",
            headers=headers_{i},
            timeout=15
        )
        
        if response_{i}.status_code == 200:
            try:
                results["{endpoint_name}"] = response_{i}.json()
            except:
                results["{endpoint_name}"] = response_{i}.text
        else:
            results["{endpoint_name}"] = None
'''
    
    template += '''
        return results
        
    except Exception as e:
        return {"error": str(e)}

# Usage example:
# session = authenticated_session  # Your authenticated requests session
# data = get_complete_agreement_data(session)
# print(json.dumps(data, indent=2))
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

if __name__ == "__main__":
    har_file = "data/api_references/anytime.club-os.com.har"
    analyze_agreement_api_sequence(har_file)
