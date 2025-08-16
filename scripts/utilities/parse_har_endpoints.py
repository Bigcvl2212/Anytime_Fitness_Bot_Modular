#!/usr/bin/env python3
"""
Parse HAR file to extract ClubOS API endpoints
"""

import os
import json
import re
from urllib.parse import urlparse
from collections import defaultdict
import sys

# List of explicit file paths to process
SESSION_FILES = [
    "charles_session.chls/clubos_login.har",
    "charles_session.chls/Clubos_message_send.har",
    "charles_session.chls/new_club_session.har",
    "charles_session.chls/Newest_clubhub_scrape.har",
    "charles_session.chls/newest_!.har",
    "charles_session.chls/newest.har",
    "charles_session.chls/Charles_session_mapping.har",
    "charles_session.chls/Training_Endpoints.har",
    "charles_session.chls/Calendar_Endpoints.har",
    "charles_session.chls/Training_payments.har",
]

KEYWORDS = ['agreement', 'billing', 'payment', 'balance', 'due', 'invoice']
# SESSION_EXTENSIONS = ['.har', '.chls', '.chlz']

# Helper to check if any keyword is in a string
contains_keyword = lambda s: any(k in s.lower() for k in KEYWORDS)

def extract_fields(obj, prefix=''):
    fields = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if contains_keyword(k):
                fields.add(prefix + k)
            fields |= extract_fields(v, prefix + k + '.')
    elif isinstance(obj, list):
        for item in obj:
            fields |= extract_fields(item, prefix)
    return fields

def summarize_endpoint(method, path, req, res, fields):
    return {
        'method': method,
        'path': path,
        'example_request': req,
        'example_response': res,
        'keyword_fields': list(fields)
    }

def main():
    print("=== HAR/Session Endpoint Extraction Debug Log ===")
    endpoints_dict = defaultdict(list)
    all_endpoints_dict = defaultdict(list)
    all_files = SESSION_FILES
    print(f"🔍 Using explicit list of {len(all_files)} session files.")
    if not all_files:
        print("❌ No session files found. Exiting.")
        return
    total_entries = 0
    for session_file in all_files:
        if session_file.endswith('.chlz'):
            print(f"⚠️ Skipping {session_file}: .chlz files are not valid JSON. Please export as .har from Charles.")
            continue
        print(f"\n📄 Processing: {session_file}")
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                try:
                    session_data = json.load(f)
                except Exception as e:
                    print(f"   ⚠️ Skipping {session_file}: Not valid JSON ({e})")
                    continue
        except Exception as e:
            print(f"❌ Error loading {session_file}: {e}")
            continue
        entries = session_data.get('log', {}).get('entries', [])
        print(f"   - {len(entries)} entries found.")
        total_entries += len(entries)
        found_in_file = 0
        for entry in entries:
            req = entry.get('request', {})
            res = entry.get('response', {})
            url = req.get('url', '')
            method = req.get('method', 'GET')
            # Parse URL early
            parsed_url = urlparse(url)
            path = parsed_url.path or ''
            if '/api/' not in path:
                continue
            path_group = re.sub(r'/\d{3,}/', '/{id}/', path)
            content = res.get('content', {})
            text = content.get('text', '')
            fields = set()
            example_response = None
            if content.get('mimeType', '') and 'application/json' in content.get('mimeType', '') and text:
                try:
                    data = json.loads(text)
                    fields = extract_fields(data)
                    example_response = data if fields else None
                except Exception as e:
                    print(f"      ⚠️ Error parsing JSON response for {method} {path}: {e}")
            # Add to all endpoints dict (regardless of keywords/fields)
            if not all_endpoints_dict[(method, path_group)]:
                all_endpoints_dict[(method, path_group)].append(summarize_endpoint(
                    method, path_group, req, example_response, fields
                ))
            # Only add to keyword endpoints if matches
            if contains_keyword(path) or fields:
                print(f"   - Found endpoint: {method} {path_group} (fields: {len(fields)})")
                endpoints_dict[(method, path_group)].append(summarize_endpoint(
                    method, path_group, req, example_response, fields
                ))
                found_in_file += 1
        print(f"   - {found_in_file} endpoints with keywords found in {session_file}.")
    # Build reference dicts
    reference = {}
    for (method, path), examples in endpoints_dict.items():
        example = examples[0]
        reference[f"{method} {path}"] = {
            'method': method,
            'path': path,
            'example_request': {
                'url': example['example_request'].get('url', ''),
                'headers': example['example_request'].get('headers', []),
                'queryString': example['example_request'].get('queryString', []),
                'postData': example['example_request'].get('postData', {})
            },
            'example_response': example['example_response'],
            'keyword_fields': example['keyword_fields']
        }
    all_reference = {}
    for (method, path), examples in all_endpoints_dict.items():
        example = examples[0]
        all_reference[f"{method} {path}"] = {
                    'method': method,
                    'path': path,
            'example_request': {
                'url': example['example_request'].get('url', ''),
                'headers': example['example_request'].get('headers', []),
                'queryString': example['example_request'].get('queryString', []),
                'postData': example['example_request'].get('postData', {})
            },
            'example_response': example['example_response'],
            'keyword_fields': example['keyword_fields']
        }
    print(f"\n🔎 Total unique endpoints with keywords found: {len(reference)} (from {total_entries} total entries)")
    print(f"🔎 Total unique endpoints (all): {len(all_reference)}")
    if not reference:
        print("❗ No endpoints with relevant keywords found in any session file.")
    try:
        with open('api_endpoint_reference.json', 'w', encoding='utf-8') as f:
            json.dump(reference, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved API endpoint reference to api_endpoint_reference.json")
    except Exception as e:
        print(f"❌ Error writing api_endpoint_reference.json: {e}")
    try:
        with open('api_endpoint_reference.md', 'w', encoding='utf-8') as f:
            f.write('# API Endpoint Reference (Keyword Matches)\n\n')
            for key, val in reference.items():
                f.write(f"## {key}\n")
                f.write(f"**Path:** `{val['path']}`\n\n")
                f.write(f"**Method:** `{val['method']}`\n\n")
                f.write(f"**Keyword Fields:** {', '.join(val['keyword_fields']) if val['keyword_fields'] else 'None'}\n\n")
                f.write("**Example Request:**\n````json\n" + json.dumps(val['example_request'], indent=2, ensure_ascii=False) + "\n````\n\n")
                if val['example_response']:
                    f.write("**Example Response:**\n````json\n" + json.dumps(val['example_response'], indent=2, ensure_ascii=False)[:2000] + "\n````\n\n")
                else:
                    f.write("**Example Response:** None\n\n")
        print(f"💾 Saved API endpoint reference to api_endpoint_reference.md")
    except Exception as e:
        print(f"❌ Error writing api_endpoint_reference.md: {e}")
    # Save all endpoints
    try:
        with open('all_api_endpoints.json', 'w', encoding='utf-8') as f:
            json.dump(all_reference, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved ALL API endpoints to all_api_endpoints.json")
    except Exception as e:
        print(f"❌ Error writing all_api_endpoints.json: {e}")
    try:
        with open('all_api_endpoints.md', 'w', encoding='utf-8') as f:
            f.write('# ALL API Endpoints\n\n')
            for key, val in all_reference.items():
                f.write(f"## {key}\n")
                f.write(f"**Path:** `{val['path']}`\n\n")
                f.write(f"**Method:** `{val['method']}`\n\n")
                f.write(f"**Keyword Fields:** {', '.join(val['keyword_fields']) if val['keyword_fields'] else 'None'}\n\n")
                f.write("**Example Request:**\n````json\n" + json.dumps(val['example_request'], indent=2, ensure_ascii=False) + "\n````\n\n")
                if val['example_response']:
                    f.write("**Example Response:**\n````json\n" + json.dumps(val['example_response'], indent=2, ensure_ascii=False)[:2000] + "\n````\n\n")
                else:
                    f.write("**Example Response:** None\n\n")
        print(f"💾 Saved ALL API endpoints to all_api_endpoints.md")
    except Exception as e:
        print(f"❌ Error writing all_api_endpoints.md: {e}")
    print(f"\n✅ Complete! {len(all_reference)} total unique endpoints documented from all session files.")

if __name__ == "__main__":
    main() 