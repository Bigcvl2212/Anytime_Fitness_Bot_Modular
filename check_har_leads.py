#!/usr/bin/env python3
"""Check HAR file for leads endpoint details."""
import json

with open('data/api_references/anytime.club-os.com.har', 'r', encoding='utf-8') as f:
    data = json.load(f)

entries = [e for e in data['log']['entries'] if 'leads' in e['request']['url'].lower()]
print(f"Found {len(entries)} leads entries\n")

for e in entries[:10]:
    req = e['request']
    resp = e['response']
    print(f"URL: {req['url']}")
    print(f"Method: {req['method']}")
    print(f"Status: {resp['status']}")
    print(f"Headers:")
    for h in req['headers']:
        if h['name'].lower() in ['authorization', 'cookie', 'accept', 'x-requested-with', 'referer']:
            val = h['value'][:100] + '...' if len(h['value']) > 100 else h['value']
            print(f"  {h['name']}: {val}")
    print("-" * 60)
