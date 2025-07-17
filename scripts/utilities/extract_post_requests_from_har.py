#!/usr/bin/env python3
"""
Extract all POST request URLs and payloads from a HAR file to find message-sending endpoints.
"""
import sys
import json


def extract_all_post_details(har_path):
    with open(har_path, 'r', encoding='utf-8') as f:
        har = json.load(f)
    entries = har.get('log', {}).get('entries', [])
    print(f"Found {len(entries)} total requests in HAR file.")
    for entry in entries:
        req = entry.get('request', {})
        method = req.get('method')
        url = req.get('url', '')
        if method == 'POST':
            post_data = req.get('postData', {})
            text = post_data.get('text', '')
            params = post_data.get('params', [])
            print(f"\n--- POST Request ---")
            print(f"URL: {url}")
            if text:
                print(f"Payload (text): {text}")
            if params:
                print("Payload (form params):")
                for param in params:
                    print(f"  {param.get('name')}: {param.get('value')}")
            if not text and not params:
                print("Payload: <empty>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_post_requests_from_har.py <har_file>")
        sys.exit(1)
    extract_all_post_details(sys.argv[1]) 