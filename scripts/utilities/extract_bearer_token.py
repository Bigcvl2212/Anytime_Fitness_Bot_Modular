import json
import sys

HAR_FILE = "charles_session.chls/Newest_clubhub_scrape.har"

def extract_bearer_token(har_file):
    with open(har_file, 'r', encoding='utf-8') as f:
        har_data = json.load(f)

    if 'log' not in har_data or 'entries' not in har_data['log']:
        print("Invalid HAR format")
        return

    entries = har_data['log']['entries']
    print(f"Scanning {len(entries)} requests for Bearer tokens...")
    
    bearer_tokens = set()
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url', '')
        method = request.get('method', '')
        status = response.get('status', 0)
        
        if 'clubhub-ios-api.anytimefitness.com' in url and status == 200:
            headers = {h['name']: h['value'] for h in request.get('headers', [])}
            if 'Authorization' in headers:
                auth_header = headers['Authorization']
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]  # Remove 'Bearer ' prefix
                    bearer_tokens.add(token)
                    print(f"Found Bearer token: {token[:50]}...")
    
    if bearer_tokens:
        print(f"\nFound {len(bearer_tokens)} unique Bearer tokens:")
        for token in bearer_tokens:
            print(f"  {token}")
    else:
        print("No Bearer tokens found.")

if __name__ == "__main__":
    har_file = sys.argv[1] if len(sys.argv) > 1 else HAR_FILE
    extract_bearer_token(har_file) 