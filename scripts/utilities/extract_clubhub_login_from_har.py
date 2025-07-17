import json
import sys

HAR_FILE = "charles_session.chls/Newest_clubhub_scrape.har"


def extract_clubhub_login_requests(har_file):
    with open(har_file, 'r', encoding='utf-8') as f:
        har_data = json.load(f)

    if 'log' not in har_data or 'entries' not in har_data['log']:
        print("❌ Invalid HAR format")
        return

    entries = har_data['log']['entries']
    print(f"Scanning {len(entries)} requests for ClubHub /api/login POSTs...")
    found = 0
    for entry in entries:
        request = entry.get('request', {})
        url = request.get('url', '')
        method = request.get('method', '')
        if '/api/login' in url and method == 'POST':
            found += 1
            print("\n============================")
            print(f"URL: {url}")
            print(f"Method: {method}")
            print("Headers:")
            for h in request.get('headers', []):
                print(f"  {h['name']}: {h['value']}")
            post_data = request.get('postData', {})
            if 'text' in post_data:
                print("Payload:")
                print(post_data['text'])
            else:
                print("No payload found.")
    if found == 0:
        print("No ClubHub /api/login POST requests found.")
    else:
        print(f"\nFound {found} ClubHub /api/login POST requests.")

if __name__ == "__main__":
    har_file = sys.argv[1] if len(sys.argv) > 1 else HAR_FILE
    extract_clubhub_login_requests(har_file) 