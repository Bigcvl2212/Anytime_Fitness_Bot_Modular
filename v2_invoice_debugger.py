#!/usr/bin/env python3
"""V2 Invoice Endpoint Debugger

Tries the high-level API method first (get_package_agreement_details).
If that returns an error / 500, falls back to a PreparedRequest that
mirrors the working cURL (tracing headers, newrelic, cookies set in
the session cookie jar) and logs full request/response for analysis.
"""

import sys
import os
import time
import json
import uuid
import logging
import traceback
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

logging.basicConfig(level=logging.INFO)

def make_trace_headers():
    trace_id = uuid.uuid4().hex[:32]
    span_id = uuid.uuid4().hex[:16]
    return {
        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6"...'},

def debug_v2_for_agreement(api: ClubOSTrainingPackageAPI, agreement_id: str) -> dict:
    """Try high-level method then fallback to prepared request if needed."""
    print(f"\n=== Debugging V2 for agreement {agreement_id} ===")

    # 1) High-level call using existing method (this includes cookie injection/newrelic in-class)
    try:
        print("-> Calling api.get_package_agreement_details() (high-level)")
        result = api.get_package_agreement_details(agreement_id)
        print(f"High-level result: success={result.get('success')}, error={result.get('error')}")
        if result.get('success'):
            return {'method': 'high_level', 'result': result}
    except Exception as e:
        print(f"High-level call raised: {e}")
        traceback.print_exc()

    # 2) Prepare a low-level request that mirrors the working cURL
    session = api.session
    bearer = api._get_bearer_token() or ''

    # Ensure critical cookies are in the session cookie jar
    critical = {
        'JSESSIONID': session.cookies.get('JSESSIONID'),
        'delegatedUserId': session.cookies.get('delegatedUserId'),
        'loggedInUserId': session.cookies.get('loggedInUserId'),
        'apiV3AccessToken': session.cookies.get('apiV3AccessToken'),
        'apiV3RefreshToken': session.cookies.get('apiV3RefreshToken')
    }
    print('\nSession cookie snapshot:')
    for k, v in critical.items():
        print(f"  {k}: {'SET' if v else 'MISSING'}")

    # Build headers (mirror working cURL + tracing)
    timestamp = int(time.time() * 1000)
    trace_id = uuid.uuid4().hex[:16]
    span_id = uuid.uuid4().hex[:8]

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {bearer}',
        'referer': 'https://anytime.club-os.com/action/PackageAgreementUpdated/spa/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'x-requested-with': 'XMLHttpRequest',
        'origin': 'https://anytime.club-os.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'priority': 'u=1, i',
        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjIwNjkxNDEiLCJhcCI6IjExMDMyNTU1NzkiLCJpZCI6"...',
        'traceparent': f'00-{trace_id}-{span_id}-01',
        'tracestate': f'2069141@nr=0-1-2069141-1103255579-{span_id}----{timestamp}',
        'x-newrelic-id': 'VgYBWFdXCRABVVFTBgUBVVQJ'
    }

    url = (
        f"https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}"
        f"?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={timestamp}"
    )

    # Ensure cookies are present in the session
    for k, v in critical.items():
        if v:
            session.cookies.set(k, v, domain='anytime.club-os.com')

    print('\n-> Falling back to prepared low-level request (session.send)')
    req = requests.Request('GET', url, headers=headers)
    prepped = session.prepare_request(req)

    # Log exact request being sent
    try:
        debug_req = {
            'method': prepped.method,
            'url': prepped.url,
            'headers': dict(prepped.headers),
            'cookies': session.cookies.get_dict()
        }
        debug_file = f'debug_v2_request_{agreement_id}.json'
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_req, f, indent=2)
        print(f"Saved prepared request debug -> {debug_file}")
    except Exception:
        pass

    # Try a couple retries with small backoff
    last_response = None
    for attempt in range(1, 4):
        try:
            print(f"  Attempt {attempt}/3 -> sending prepared request")
            resp = session.send(prepped, timeout=20)
            last_response = resp
            print(f"  Response: {resp.status_code}")
            resp_text_preview = resp.text[:2000]
            print(f"  Body preview: {resp_text_preview[:500]}{'...' if len(resp_text_preview)>500 else ''}")

            # Save full response for offline inspection
            outname = f'debug_v2_response_full_{agreement_id}_{int(time.time())}.txt'
            try:
                with open(outname, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url}\n\n")
                    f.write(f"REQUEST HEADERS:\n{json.dumps(dict(prepped.headers), indent=2)}\n\n")
                    f.write(f"COOKIES:\n{json.dumps(session.cookies.get_dict(), indent=2)}\n\n")
                    f.write(f"RESPONSE STATUS: {resp.status_code}\n\n")
                    f.write(resp.text)
                print(f"  Saved full response -> {outname}")
            except Exception as e:
                print(f"  Failed to save full response: {e}")

            if resp.status_code == 200:
                try:
                    data = resp.json()
                except Exception:
                    data = {'raw': resp.text}
                return {'method': 'prepared_request', 'status_code': 200, 'data': data}

            # If 500, wait briefly and retry
            if resp.status_code >= 500:
                time.sleep(1 * attempt)
                continue
            else:
                # Non-200, non-500 - return for analysis
                try:
                    content = resp.json()
                except Exception:
                    content = resp.text
                return {'method': 'prepared_request', 'status_code': resp.status_code, 'data': content}

        except Exception as e:
            print(f"  Exception sending prepared request: {e}")
            traceback.print_exc()
            time.sleep(0.5 * attempt)

    return {'method': 'prepared_request', 'status_code': (last_response.status_code if last_response is not None else None), 'error': 'All attempts failed', 'last_response_text': (last_response.text[:2000] if last_response is not None else None)}


def main():
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print('Authentication failed')
        return 1

    member_id = '177673765'
    agreements = api.get_package_agreements_list(member_id)
    if not agreements:
        print('No agreements found for member')
        return 1

    # Pick agreement IDs
    agreement_ids = []
    for a in agreements:
        if isinstance(a, dict) and 'packageAgreement' in a:
            aid = a['packageAgreement'].get('id')
            if aid:
                agreement_ids.append(str(aid))

    # Prefer known-working 1651819 if present
    if '1651819' in agreement_ids:
        to_test = ['1651819'] + [x for x in agreement_ids if x != '1651819']
    else:
        to_test = agreement_ids

    for aid in to_test:
        r = debug_v2_for_agreement(api, aid)
        print('\n--- RESULT SUMMARY ---')
        print(json.dumps(r if isinstance(r, dict) else {'result': str(r)}, indent=2, default=str))

    return 0

if __name__ == '__main__':
    sys.exit(main())
