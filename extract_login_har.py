import json
import os

def extract_login_from_har():
    """Extract actual login requests from HAR files"""
    
    print("HAR Login Request Extractor")
    print("=" * 50)
    
    # Priority files that likely contain login
    priority_files = [
        "clubos_login.har",
        "Newest_clubhub_scrape.har", 
        "newest_!.har",
        "Agreement_Creation.har"
    ]
    
    charles_dir = "charles_session.chls"
    
    for har_file in priority_files:
        filepath = os.path.join(charles_dir, har_file)
        if not os.path.exists(filepath):
            print(f"File not found: {har_file}")
            continue
            
        print(f"\nAnalyzing: {har_file}")
        print("-" * 30)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
                
            entries = har_data.get('log', {}).get('entries', [])
            print(f"Found {len(entries)} HTTP requests")
            
            login_requests = []
            
            for i, entry in enumerate(entries):
                request = entry.get('request', {})
                url = request.get('url', '')
                method = request.get('method', '')
                
                # Look for login-related URLs
                if any(pattern in url.lower() for pattern in [
                    '/auth/sign_in', '/login', '/signin', '/auth', 
                    'authentication', 'token'
                ]):
                    login_requests.append((i, entry))
                    print(f"  Request #{i}: {method} {url}")
                    
                    # Check headers
                    headers = request.get('headers', [])
                    for header in headers:
                        if header.get('name', '').lower() in ['authorization', 'x-api-key', 'content-type']:
                            print(f"    {header.get('name')}: {header.get('value')}")
                    
                    # Check POST data
                    if method.upper() == 'POST':
                        post_data = request.get('postData', {})
                        if post_data:
                            print(f"    POST Data: {post_data.get('text', '')[:100]}...")
            
            if login_requests:
                print(f"\nFound {len(login_requests)} login-related requests!")
                
                # Show detailed info for first login request
                _, first_login = login_requests[0]
                print(f"\nDetailed analysis of first login request:")
                print(f"URL: {first_login['request']['url']}")
                print(f"Method: {first_login['request']['method']}")
                
                print("Headers:")
                for header in first_login['request'].get('headers', []):
                    print(f"  {header.get('name')}: {header.get('value')}")
                
                if first_login['request'].get('postData'):
                    print(f"POST Data: {first_login['request']['postData'].get('text', '')}")
                
                # Check response
                response = first_login.get('response', {})
                print(f"Response Status: {response.get('status')}")
                
                # Look for tokens in response
                response_text = response.get('content', {}).get('text', '')
                if 'token' in response_text.lower() or 'bearer' in response_text.lower():
                    print("Response contains token data!")
                    print(f"Response snippet: {response_text[:200]}...")
                
            else:
                print("No login requests found")
                
                # Show some sample URLs to understand what's in the file
                print("\nSample URLs in this file:")
                for i in range(min(5, len(entries))):
                    url = entries[i].get('request', {}).get('url', '')
                    method = entries[i].get('request', {}).get('method', '')
                    print(f"  {method} {url}")
                    
        except Exception as e:
            print(f"Error processing {har_file}: {e}")

if __name__ == "__main__":
    extract_login_from_har()
