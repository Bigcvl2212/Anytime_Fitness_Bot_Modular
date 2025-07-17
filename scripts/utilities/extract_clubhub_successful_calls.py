import json
import sys

HAR_FILE = "charles_session.chls/Newest_clubhub_scrape.har"

def extract_successful_clubhub_calls(har_file):
    with open(har_file, 'r', encoding='utf-8') as f:
        har_data = json.load(f)

    if 'log' not in har_data or 'entries' not in har_data['log']:
        print("Invalid HAR format")
        return

    entries = har_data['log']['entries']
    print(f"Scanning {len(entries)} requests for successful ClubHub API calls...")
    
    successful_calls = []
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url', '')
        method = request.get('method', '')
        status = response.get('status', 0)
        
        if 'clubhub-ios-api.anytimefitness.com' in url and status == 200:
            successful_calls.append({
                'url': url,
                'method': method,
                'status': status,
                'headers': {h['name']: h['value'] for h in request.get('headers', [])},
                'response_headers': {h['name']: h['value'] for h in response.get('headers', [])}
            })
    
    print(f"\nFound {len(successful_calls)} successful ClubHub API calls:")
    for call in successful_calls:
        print(f"\n{call['method']} {call['url']} - Status: {call['status']}")
        if 'Authorization' in call['headers']:
            print(f"  Auth: {call['headers']['Authorization'][:50]}...")
        if 'Cookie' in call['headers']:
            print(f"  Cookie: {call['headers']['Cookie'][:50]}...")

if __name__ == "__main__":
    har_file = sys.argv[1] if len(sys.argv) > 1 else HAR_FILE
    extract_successful_clubhub_calls(har_file) 