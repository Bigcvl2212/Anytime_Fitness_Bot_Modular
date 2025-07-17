import json
import re
from collections import defaultdict

# Path to the HAR file
har_path = 'charles_session.chls/Newest_clubhub_scrape.har'

# Keywords to search for in endpoints and response fields
KEYWORDS = ['agreement', 'billing', 'payment', 'balance', 'due', 'invoice']

# Helper to check if any keyword is in a string
contains_keyword = lambda s: any(k in s.lower() for k in KEYWORDS)

# Store unique endpoints and matching responses
endpoints = set()
endpoint_fields = defaultdict(set)

with open(har_path, 'r', encoding='utf-8') as f:
    har = json.load(f)

for entry in har.get('log', {}).get('entries', []):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    method = req.get('method', '')
    # Only look at API calls
    if '/api/' not in url:
        continue
    # Extract endpoint path (strip domain and query)
    path = re.sub(r'^https?://[^/]+', '', url).split('?')[0]
    if contains_keyword(path):
        endpoints.add((method, path))
    # Try to parse JSON response
    content = res.get('content', {})
    text = content.get('text', '')
    if 'application/json' in content.get('mimeType', '') and text:
        try:
            data = json.loads(text)
            # Recursively search for fields with keywords
            def find_fields(obj, prefix=''):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if contains_keyword(k):
                            endpoint_fields[(method, path)].add(prefix + k)
                        find_fields(v, prefix + k + '.')
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_fields(item, prefix)
            find_fields(data)
        except Exception:
            pass

print('=== Unique API Endpoints with Keywords ===')
for method, path in sorted(endpoints):
    print(f'{method} {path}')

print('\n=== Endpoints with Matching Response Fields ===')
for (method, path), fields in endpoint_fields.items():
    if fields:
        print(f'\n{method} {path}')
        for field in sorted(fields):
            print(f'  - {field}') 