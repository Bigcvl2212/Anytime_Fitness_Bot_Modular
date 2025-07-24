import json
import os

def extract_clubhub_login_details():
    """Extract exact ClubHub login details from HAR files"""
    
    print("ClubHub Login Extractor")
    print("=" * 40)
    
    # Focus on the file with ClubHub login
    har_file = "charles_session.chls/Newest_clubhub_scrape.har"
    
    if not os.path.exists(har_file):
        print(f"File not found: {har_file}")
        return
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
            
        entries = har_data.get('log', {}).get('entries', [])
        print(f"Analyzing {len(entries)} requests from {os.path.basename(har_file)}")
        
        # Find the actual login POST request
        for i, entry in enumerate(entries):
            request = entry.get('request', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            # Look for the ClubHub login POST
            if (method.upper() == 'POST' and 
                'clubhub-ios-api.anytimefitness.com/api/login' in url):
                
                print(f"\nFound ClubHub login request #{i}:")
                print(f"URL: {url}")
                print(f"Method: {method}")
                
                print("\nHeaders:")
                headers = request.get('headers', [])
                for header in headers:
                    name = header.get('name', '')
                    value = header.get('value', '')
                    print(f"  {name}: {value}")
                
                print("\nPOST Data:")
                post_data = request.get('postData', {})
                if post_data:
                    text = post_data.get('text', '')
                    print(f"  {text}")
                    
                    # Try to parse JSON
                    try:
                        json_data = json.loads(text)
                        print("\nParsed POST JSON:")
                        for key, value in json_data.items():
                            if key.lower() == 'password':
                                print(f"  {key}: [REDACTED]")
                            else:
                                print(f"  {key}: {value}")
                    except:
                        pass
                
                # Check response
                response = entry.get('response', {})
                status = response.get('status', '')
                print(f"\nResponse Status: {status}")
                
                # Look for response content
                response_content = response.get('content', {})
                response_text = response_content.get('text', '')
                
                if response_text:
                    print(f"\nResponse (first 300 chars):")
                    print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
                    
                    # Try to parse response JSON
                    try:
                        response_json = json.loads(response_text)
                        print("\nParsed Response JSON:")
                        for key, value in response_json.items():
                            if isinstance(value, str) and len(str(value)) > 100:
                                print(f"  {key}: {str(value)[:50]}... (truncated)")
                            else:
                                print(f"  {key}: {value}")
                    except:
                        pass
                
                print("\n" + "="*60)
                
        # Also find any token requests to AF API
        print("\nLooking for AF API token requests...")
        for i, entry in enumerate(entries):
            request = entry.get('request', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            if (method.upper() == 'POST' and 
                'api.anytimefitness.com/token' in url):
                
                print(f"\nFound AF API token request #{i}:")
                print(f"URL: {url}")
                
                post_data = request.get('postData', {})
                if post_data:
                    text = post_data.get('text', '')
                    print(f"POST Data: {text}")
                
                response = entry.get('response', {})
                response_content = response.get('content', {})
                response_text = response_content.get('text', '')
                
                if response_text:
                    print(f"Response: {response_text[:200]}...")
                
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    extract_clubhub_login_details()
