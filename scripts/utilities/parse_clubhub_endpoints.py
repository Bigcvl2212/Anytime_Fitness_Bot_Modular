#!/usr/bin/env python3
"""
Parse HAR file to extract ClubHub API endpoints
"""

import json
import re
from urllib.parse import urlparse
from typing import Dict, List, Any

def parse_har_for_clubhub_endpoints(har_file_path: str) -> Dict[str, Any]:
    """Parse HAR file and extract ClubHub API endpoints"""
    
    print(f"🔍 Parsing HAR file: {har_file_path}")
    
    clubhub_endpoints = {
        "api_calls": [],
        "form_submissions": [],
        "ajax_requests": [],
        "contact_list_requests": [],
        "member_data_requests": [],
        "summary": {
            "total_requests": 0,
            "clubhub_requests": 0,
            "api_endpoints": 0,
            "form_submissions": 0,
            "contact_list_requests": 0
        }
    }
    
    try:
        with open(har_file_path, 'r', encoding='utf-8') as f:
            # Read in chunks to handle large files
            content = f.read()
            
        print("📄 Loading HAR content...")
        har_data = json.loads(content)
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            print("❌ Invalid HAR format")
            return clubhub_endpoints
            
        entries = har_data['log']['entries']
        print(f"📊 Found {len(entries)} total requests")
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            url = request.get('url', '')
            method = request.get('method', 'GET')
            
            # Check if this is a ClubHub request
            if 'clubhub' in url.lower() or 'club-hub' in url.lower():
                clubhub_endpoints['summary']['clubhub_requests'] += 1
                
                parsed_url = urlparse(url)
                path = parsed_url.path
                
                # Categorize the request
                request_info = {
                    'url': url,
                    'method': method,
                    'path': path,
                    'status': response.get('status', 0),
                    'headers': {h['name']: h['value'] for h in request.get('headers', [])},
                    'post_data': request.get('postData', {}),
                    'response_size': response.get('bodySize', 0)
                }
                
                # Check for contact list related requests
                if any(term in path.lower() for term in ['contact', 'member', 'prospect', 'list', 'export']):
                    clubhub_endpoints['contact_list_requests'].append(request_info)
                    clubhub_endpoints['summary']['contact_list_requests'] += 1
                    print(f"📋 Contact List: {method} {path}")
                    
                # Check for API endpoints
                elif '/api/' in path or '/ajax/' in path or '/action/' in path:
                    clubhub_endpoints['api_calls'].append(request_info)
                    clubhub_endpoints['summary']['api_endpoints'] += 1
                    print(f"🔗 API: {method} {path}")
                    
                # Check for form submissions
                elif method == 'POST' and request.get('postData'):
                    clubhub_endpoints['form_submissions'].append(request_info)
                    clubhub_endpoints['summary']['form_submissions'] += 1
                    print(f"📝 Form: {method} {path}")
                    
                # Check for AJAX requests
                elif 'X-Requested-With' in request_info['headers']:
                    clubhub_endpoints['ajax_requests'].append(request_info)
                    print(f"⚡ AJAX: {method} {path}")
                    
                # Check for member data requests
                elif any(term in path.lower() for term in ['member', 'prospect', 'user', 'customer']):
                    clubhub_endpoints['member_data_requests'].append(request_info)
                    print(f"👤 Member Data: {method} {path}")
                    
            clubhub_endpoints['summary']['total_requests'] += 1
            
    except Exception as e:
        print(f"❌ Error parsing HAR file: {e}")
        return clubhub_endpoints
    
    print(f"\n📈 Summary:")
    print(f"   Total requests: {clubhub_endpoints['summary']['total_requests']}")
    print(f"   ClubHub requests: {clubhub_endpoints['summary']['clubhub_requests']}")
    print(f"   API endpoints: {clubhub_endpoints['summary']['api_endpoints']}")
    print(f"   Form submissions: {clubhub_endpoints['summary']['form_submissions']}")
    print(f"   Contact list requests: {clubhub_endpoints['summary']['contact_list_requests']}")
    
    return clubhub_endpoints

def save_endpoints_report(endpoints: Dict[str, Any], output_file: str):
    """Save the extracted endpoints to a JSON file"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(endpoints, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved endpoints report to: {output_file}")

def main():
    """Main function to parse HAR and extract ClubHub endpoints"""
    
    har_file = "charles_session.chls/Newest_clubhub_scrape.har"
    output_file = "clubhub_api_endpoints.json"
    
    print("🚀 Starting HAR parsing for ClubHub API endpoints...")
    
    endpoints = parse_har_for_clubhub_endpoints(har_file)
    save_endpoints_report(endpoints, output_file)
    
    # Print key findings
    print(f"\n🎯 Key Findings:")
    
    if endpoints['contact_list_requests']:
        print(f"   Found {len(endpoints['contact_list_requests'])} contact list requests:")
        for contact in endpoints['contact_list_requests'][:10]:  # Show first 10
            print(f"     {contact['method']} {contact['path']}")
    
    if endpoints['api_calls']:
        print(f"   Found {len(endpoints['api_calls'])} API endpoints:")
        for api in endpoints['api_calls'][:10]:  # Show first 10
            print(f"     {api['method']} {api['path']}")
    
    if endpoints['member_data_requests']:
        print(f"   Found {len(endpoints['member_data_requests'])} member data requests:")
        for member in endpoints['member_data_requests'][:10]:  # Show first 10
            print(f"     {member['method']} {member['path']}")
    
    print(f"\n✅ Complete! Check {output_file} for full details.")

if __name__ == "__main__":
    main() 