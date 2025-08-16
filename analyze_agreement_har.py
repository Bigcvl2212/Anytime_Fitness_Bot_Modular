#!/usr/bin/env python3
"""
Analyze the ClubOS HAR file to extract agreement-related requests
"""

import json
import sys

def analyze_agreement_requests():
    """Extract and analyze agreement-related requests from HAR analysis"""
    
    try:
        with open('data/har_analysis_20250813_145440.json', 'r') as f:
            data = json.load(f)
        
        print('=== AGREEMENT-RELATED REQUESTS FROM HAR ===')
        print()
        
        agreement_requests = []
        for req in data.get('all_requests', []):
            url = req.get('url', '').lower()
            if 'agreement' in url:
                agreement_requests.append(req)
        
        print(f"Found {len(agreement_requests)} agreement-related requests:")
        print()
        
        for i, req in enumerate(agreement_requests, 1):
            print(f"{i}. {req['method']} {req['url']}")
            print(f"   Status: {req['status']}")
            
            # Extract key headers
            headers = req.get('headers', [])
            for header in headers:
                name = header['name'].lower()
                if name in ['authorization', 'referer', 'x-requested-with', 'accept']:
                    value = header['value']
                    if name == 'authorization' and len(value) > 50:
                        value = value[:30] + "..." + value[-10:]
                    print(f"   {header['name']}: {value}")
            
            # Extract query parameters
            if 'queryString' in req:
                params = req['queryString']
                if params:
                    print("   Query Params:")
                    for param in params:
                        print(f"     {param['name']}: {param['value']}")
            
            print()
        
        # Extract delegation requests
        print('=== DELEGATION REQUESTS ===')
        print()
        
        delegation_requests = []
        for req in data.get('all_requests', []):
            url = req.get('url', '').lower()
            if 'delegate' in url:
                delegation_requests.append(req)
        
        for i, req in enumerate(delegation_requests, 1):
            print(f"{i}. {req['method']} {req['url']}")
            print(f"   Status: {req['status']}")
            
            # Extract key headers
            headers = req.get('headers', [])
            for header in headers:
                name = header['name'].lower()
                if name in ['authorization', 'referer', 'accept']:
                    value = header['value']
                    if name == 'authorization' and len(value) > 50:
                        value = value[:30] + "..." + value[-10:]
                    print(f"   {header['name']}: {value}")
            print()
        
        # Look for specific agreement ID patterns
        print('=== AGREEMENT IDS FOUND ===')
        print()
        
        agreement_ids = set()
        for req in data.get('all_requests', []):
            url = req.get('url', '')
            
            # Look for agreement IDs in URL paths
            import re
            matches = re.findall(r'/package_agreements/(\d+)', url)
            for match in matches:
                agreement_ids.add(match)
        
        if agreement_ids:
            print(f"Found agreement IDs: {sorted(agreement_ids)}")
        else:
            print("No agreement IDs found in URLs")
        
        print()
        print('=== MEMBER/USER IDS ===')
        
        user_ids = set()
        for req in data.get('all_requests', []):
            url = req.get('url', '')
            
            # Look for user/member IDs
            matches = re.findall(r'/(\d{8,})', url)  # 8+ digit numbers
            for match in matches:
                user_ids.add(match)
        
        if user_ids:
            print(f"Found user/member IDs: {sorted(user_ids)}")
        
    except FileNotFoundError:
        print("HAR analysis file not found. Please run har_analyzer.py first.")
    except Exception as e:
        print(f"Error analyzing HAR file: {e}")

if __name__ == "__main__":
    analyze_agreement_requests()
