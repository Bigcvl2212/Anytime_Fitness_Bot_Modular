#!/usr/bin/env python3
"""
ClubOS Training Package API - Working implementation
Extracted from enhanced_dashboard_with_agreements.py for better modularity
"""

import requests
import json
import re
import time
import threading
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from typing import Optional

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class ClubOSTrainingPackageAPI:
    """
    Integrated ClubOS Training Package API for dashboard use
    Uses the working authentication and token extraction from test_leisa_training_packages_clean.py
    """
    def __init__(self):
        # Initialize HTTP session and base state
        self.session = requests.Session()
        self.base_url = "https://anytime.club-os.com"
        self.authenticated = False
        self.session_data = {}
        self.access_token = None
        self._last_auth_time = 0.0
        self._auth_lock = threading.Lock()

        # Cached assignees list and index (refresh periodically)
        self._assignees_cache = None
        self._assignees_index = None
        self._assignees_fetched_at = 0.0

        # Set headers to mimic working browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session.headers.update(headers)

        # Add robust retry strategy for transient errors
        retry_strategy = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _extract_access_token(self, html: str) -> str | None:
        """Extract delegated ACCESS_TOKEN from a variety of patterns present in SPA pages."""
        try:
            patterns = [
                r'ACCESS_TOKEN\s*=\s*"([^"]+)"',              # var ACCESS_TOKEN = "..."
                r"ACCESS_TOKEN\s*=\s*'([^']+)'",               # var ACCESS_TOKEN = '...'
                r'window\.ACCESS_TOKEN\s*=\s*["\']([^"\']+)["\']',
                r'\"accessToken\"\s*:\s*\"([^\"]+)\"', # JSON embedded
                r'"accessToken"\s*:\s*"([^"]+)"'
            ]
            for pat in patterns:
                m = re.search(pat, html)
                if m:
                    return m.group(1)
        except Exception:
            pass
        return None
        
    def authenticate(self, force: bool = False):
        """Authenticate using the working HAR sequence with retry and serialization."""
        try:
            # Fast-path reuse if recently authenticated
            if not force and self.authenticated and (time.time() - self._last_auth_time) < 600:
                return True

            with self._auth_lock:
                # Re-check state under lock
                if not force and self.authenticated and (time.time() - self._last_auth_time) < 600:
                    return True

                print("🔐 Authenticating with ClubOS...")
                # Load credentials from config when available
                username = None
                password = None
                try:
                    from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
                    username = CLUBOS_USERNAME
                    password = CLUBOS_PASSWORD
                except Exception:
                    # Fallback to historical hardcoded values as last resort
                    username = 'j.mayo'
                    password = 'j@SD4fjhANK5WNA'
            
            # Step 1: GET login page
            login_get_url = f"{self.base_url}/action/Login/view"
            get_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'DNT': '1',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Simple retry loop
            last_error = None
            for attempt in range(1, 4):
                login_response = self.session.get(login_get_url, headers=get_headers, timeout=30)
                if not login_response.ok:
                    last_error = f"GET login status {login_response.status_code}"
                    time.sleep(0.6 * attempt)
                    continue

                # Extract form fields dynamically
                soup = BeautifulSoup(login_response.text, 'html.parser')
                login_form = soup.find('form')
                if not login_form:
                    last_error = "No login form"
                    time.sleep(0.6 * attempt)
                    continue

                # Extract ALL hidden fields
                hidden_inputs = login_form.find_all('input', type='hidden')
                form_data = {}
                for hidden_input in hidden_inputs:
                    name = hidden_input.get('name')
                    value = hidden_input.get('value', '')
                    if name:
                        form_data[name] = value

                # Check for required tokens
                if '_sourcePage' not in form_data or '__fp' not in form_data:
                    last_error = "Missing CSRF tokens"
                    time.sleep(0.6 * attempt)
                    continue

                # Step 2: POST login with extracted CSRF tokens
                login_action = login_form.get('action') or '/action/Login'
                if login_action.startswith('/'):
                    login_action_url = f"{self.base_url}{login_action}"
                elif login_action.startswith('http'):
                    login_action_url = login_action
                else:
                    login_action_url = f"{self.base_url}/{login_action.lstrip('/')}"

                # Build payload from hidden fields + credentials (preserving unexpected required fields)
                payload = dict(form_data)
                # Detect username and password field names dynamically
                uname_field = None
                pwd_field = None
                # Prefer explicit inputs
                text_inputs = login_form.find_all('input', attrs={'type': re.compile('^text|email$', re.I)})
                pass_inputs = login_form.find_all('input', attrs={'type': re.compile('^password$', re.I)})
                # Heuristics for username
                candidates = ['username', 'user', 'email', 'login', 'j_username']
                for inp in text_inputs:
                    n = inp.get('name') or ''
                    if any(k.lower() == n.lower() for k in candidates):
                        uname_field = n
                        break
                if not uname_field:
                    uname_field = (text_inputs[0].get('name') if text_inputs else 'username')
                # Heuristics for password
                if pass_inputs:
                    pwd_field = pass_inputs[0].get('name') or 'password'
                else:
                    # fallback common names
                    pwd_field = 'password'
                # Compose payload
                payload.update({
                    'login': payload.get('login', 'Submit'),
                    uname_field: username,
                    pwd_field: password,
                    'rememberMe': payload.get('rememberMe', 'on')
                })

                post_headers = {
                    'User-Agent': get_headers['User-Agent'],
                    'Accept': get_headers['Accept'],
                    'Accept-Language': get_headers['Accept-Language'],
                    'Accept-Encoding': get_headers['Accept-Encoding'],
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'DNT': '1',
                    'Cache-Control': 'max-age=0',
                    'Origin': 'https://anytime.club-os.com',
                    'Referer': login_get_url,
                    'Sec-Ch-Ua': get_headers['Sec-Ch-Ua'],
                    'Sec-Ch-Ua-Mobile': get_headers['Sec-Ch-Ua-Mobile'],
                    'Sec-Ch-Ua-Platform': get_headers['Sec-Ch-Ua-Platform'],
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                }

                auth_response = self.session.post(
                    login_action_url,
                    data=payload,
                    headers=post_headers,
                    allow_redirects=True,
                    timeout=30
                )

                # Follow-up: visit dashboard to finalize cookies/tokens
                try:
                    # Prime a few key pages to materialize tokens/cookies
                    dash = self.session.get(f"{self.base_url}/action/Dashboard/view", timeout=30)
                    try:
                        self.session.get(f"{self.base_url}/action/Members", timeout=20)
                    except Exception:
                        pass
                except Exception:
                    dash = auth_response

                # Check for successful login: relaxed criteria
                stayed_on_login = (
                    (auth_response.status_code == 200 and "action/Login" in auth_response.url) or
                    (dash.status_code == 200 and ("action/Login" in dash.url or "Login" in (dash.text or "")[:1024]))
                )
                # Extract cookies
                session_id = self.session.cookies.get('JSESSIONID')
                logged_in_user_id = self.session.cookies.get('loggedInUserId')
                delegated_user_id = self.session.cookies.get('delegatedUserId')
                api_v3_access_token = self.session.cookies.get('apiV3AccessToken')

                # If we have JSESSIONID and loggedInUserId, consider login successful even without apiV3AccessToken
                if stayed_on_login and not (session_id and logged_in_user_id):
                    last_error = "Stayed on login page"
                    time.sleep(0.8 * attempt)
                    continue

                # Try to extract an ACCESS_TOKEN from dashboard/SPAs page if cookie not present
                access_token = api_v3_access_token
                if (dash is not None) and (not access_token):
                    access_token = self._extract_access_token(dash.text or "")
                if not access_token:
                    try:
                        spa = self.session.get(f"{self.base_url}/action/PackageAgreementUpdated/spa/", timeout=20)
                        if spa.status_code == 200:
                            access_token = self._extract_access_token(spa.text or "")
                    except Exception:
                        pass

                # Store session data
                self.session_data = {
                    'loggedInUserId': logged_in_user_id,
                    'delegatedUserId': delegated_user_id,
                    'JSESSIONID': session_id,
                    'apiV3AccessToken': access_token
                }

                self.access_token = access_token
                self.authenticated = True
                self._last_auth_time = time.time()

                print(f"   ✅ Authentication successful!")
                return True

            # If we got here, all attempts failed
            print(f"   ❌ Authentication failed: {last_error}")
            return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def _ensure_session_alive(self) -> bool:
        """Ping a lightweight page to ensure session is still valid; re-auth if needed."""
        try:
            r = self.session.get(f"{self.base_url}/action/Dashboard/view", timeout=15, allow_redirects=True)
            if r.status_code == 200 and ("action/Login" not in r.url):
                return True
        except Exception:
            pass
        return self.authenticate(force=True)

    def _get_delegated_token(self, member_id: str) -> Optional[str]:
        """Delegate to member context and extract ACCESS_TOKEN from multiple candidate pages."""
        # 1) Try delegate endpoint
        try:
            delegation_headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            delegate_url = f"{self.base_url}/action/Delegate/{member_id}/url=false"
            self.session.get(delegate_url, headers=delegation_headers, params={'_': int(datetime.now().timestamp() * 1000)}, timeout=15)
            time.sleep(0.4)
        except Exception:
            # Try setting cookie directly as last resort
            try:
                self.session.cookies.set('delegatedUserId', str(member_id))
            except Exception:
                pass

        # 2) Try several SPA pages that typically expose ACCESS_TOKEN
        candidate_pages = [
            f"{self.base_url}/action/PackageAgreementUpdated/spa/",
            f"{self.base_url}/action/MemberDashboard/{member_id}/spa/",
            f"{self.base_url}/action/Agreements/view/{member_id}",
        ]
        for page in candidate_pages:
            try:
                r = self.session.get(page, headers={'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'), 'Accept': 'text/html,*/*;q=0.8', 'Referer': f'{self.base_url}/action/Dashboard/view'}, timeout=20)
                if r.status_code != 200:
                    continue
                token = self._extract_access_token(r.text or "")
                if token:
                    return token
            except Exception:
                continue

        # 3) Fallback to stored v3 access token if available
        return self.session_data.get('apiV3AccessToken')

    def get_member_payment_status(self, member_id):
        """Get payment status for a specific member - REAL DATA ONLY"""
        if not self.authenticated:
            if not self.authenticate():
                return None  # No fallbacks - return None if can't authenticate
        # Ensure session still alive
        if not self._ensure_session_alive():
            return None
        
        try:
            # Step 1: Get a delegated token for the member
            logger.info(f"[ClubOS] Delegating to member {member_id}...")
            print(f"[ClubOS] ▶ Delegating to member {member_id}...")
            delegated_token = self._get_delegated_token(str(member_id))
            logger.info(f"[ClubOS] Delegated token {'FOUND' if delegated_token else 'NOT FOUND'}")
            print(f"[ClubOS] 🔑 Delegated token {'FOUND' if delegated_token else 'NOT FOUND'}")

            if not delegated_token:
                # Try billing/member endpoint with just delegated cookie
                try:
                    billing_url_fallback = f"{self.base_url}/api/billing/member/{member_id}/billing_status"
                    auth_fallback = self.session_data.get('apiV3AccessToken')
                    fb_headers = {'Accept': '*/*'}
                    if auth_fallback:
                        fb_headers['Authorization'] = f'Bearer {auth_fallback}'
                    billing_resp_fb = self.session.get(billing_url_fallback, headers=fb_headers)
                    print(f"[ClubOS] ◀ billing/member fb (Bearer v3) -> {billing_resp_fb.status_code}")
                    if billing_resp_fb.status_code == 200:
                        billing_data = billing_resp_fb.json()
                        past_due_items = billing_data.get('past', []) if isinstance(billing_data, dict) else []
                        return "Past Due" if past_due_items else "Current"
                except Exception:
                    pass
                return None

            # Step 2: Call billing_status API with the delegated token
            timestamp = int(time.time() * 1000)

            # First, discover active agreements for this member
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Authorization': f'Bearer {delegated_token}',
                'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/'
            }

            discovery_endpoints = [
                f"/api/agreements/package_agreements/list?memberId={member_id}",
                f"/api/agreements/package_agreements/active?memberId={member_id}",
                f"/api/members/{member_id}/active_agreements",
                f"/api/agreements/package_agreements?memberId={member_id}",
            ]

            for endpoint in discovery_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    params = {'_': timestamp}

                    response = self.session.get(url, headers=api_headers, params=params, timeout=10)
                    if response.status_code in (401, 403):
                        alt_headers = dict(api_headers)
                        alt_headers['Authorization'] = delegated_token
                        response = self.session.get(url, headers=alt_headers, params=params, timeout=10)
                    logger.info(f"[ClubOS] Discovery {endpoint} -> {response.status_code}")
                    print(f"[ClubOS] ◀ Discovery {endpoint} -> {response.status_code}")

                    if response.status_code == 200:
                        data = response.json()
                        agreements = []
                        if isinstance(data, list):
                            agreements = data
                        elif isinstance(data, dict):
                            if 'agreements' in data and isinstance(data['agreements'], list):
                                agreements = data['agreements']
                            elif 'data' in data and isinstance(data['data'], list):
                                agreements = data['data']

                        logger.info(f"[ClubOS] Agreements discovered: {len(agreements)}")
                        if agreements:
                            active = [a for a in agreements if a.get('agreementStatus') in (2, 'Active', 'active') or a.get('status') in (2, 'Active', 'active')]
                            candidates = active if active else agreements[:3]
                            for ag in candidates:
                                ag_id = ag.get('id') or ag.get('agreementId') or ag.get('agreement_id')
                                if not ag_id:
                                    continue
                                billing_url = f"{self.base_url}/api/agreements/package_agreements/{ag_id}/billing_status"
                                billing_params = {'_': timestamp + 1}
                                billing_response = self.session.get(billing_url, headers=api_headers, params=billing_params, timeout=10)
                                if billing_response.status_code in (401, 403):
                                    alt_headers = dict(api_headers)
                                    alt_headers['Authorization'] = delegated_token
                                    billing_response = self.session.get(billing_url, headers=alt_headers, params=billing_params, timeout=10)
                                logger.info(f"[ClubOS] Billing status for agreement {ag_id} -> {billing_response.status_code}")
                                print(f"[ClubOS] ◀ Billing status for agreement {ag_id} -> {billing_response.status_code}")
                                if billing_response.status_code == 200:
                                    billing_data = billing_response.json()
                                    past_due_items = []
                                    if isinstance(billing_data, dict):
                                        past_due_items = billing_data.get('past', []) or billing_data.get('pastDue', [])
                                    if past_due_items:
                                        logger.info("[ClubOS] Agreement billing shows PAST DUE")
                                        print("[ClubOS] 💳 Agreement billing -> PAST DUE")
                                        return "Past Due"
                                    else:
                                        logger.info("[ClubOS] Agreement billing shows CURRENT")
                                        print("[ClubOS] 💳 Agreement billing -> CURRENT")
                                        return "Current"
                except Exception as e:
                    logger.warning(f"[ClubOS] Discovery error on {endpoint}: {e}")
                    continue

            # Final fallback: directly query member billing status using delegated token/cookie
            try:
                billing_url = f"{self.base_url}/api/billing/member/{member_id}/billing_status"
                if delegated_token:
                    billing_headers = dict(api_headers)
                else:
                    billing_headers = {
                        'User-Agent': api_headers['User-Agent'],
                        'Accept': '*/*'
                    }
                    v3 = self.session_data.get('apiV3AccessToken')
                    if v3:
                        billing_headers['Authorization'] = f'Bearer {v3}'

                billing_resp = self.session.get(billing_url, headers=billing_headers, timeout=10)
                if billing_resp.status_code in (401, 403):
                    alt_headers = dict(billing_headers)
                    if 'Authorization' in alt_headers and isinstance(alt_headers['Authorization'], str) and alt_headers['Authorization'].startswith('Bearer '):
                        alt_headers['Authorization'] = alt_headers['Authorization'].replace('Bearer ', '')
                    elif delegated_token and 'Authorization' in alt_headers:
                        alt_headers['Authorization'] = delegated_token
                    billing_resp = self.session.get(billing_url, headers=alt_headers, timeout=10)
                logger.info(f"[ClubOS] Member billing_status -> {billing_resp.status_code}")
                print(f"[ClubOS] ◀ Member billing_status -> {billing_resp.status_code}")
                if billing_resp.status_code == 200:
                    bdata = billing_resp.json()
                    past_due_items = bdata.get('past', []) if isinstance(bdata, dict) else []
                    return "Past Due" if past_due_items else "Current"
                # Last-ditch: try all combinations of tokens and header formats
                tokens_to_try = []
                if delegated_token:
                    tokens_to_try.append(delegated_token)
                v3 = self.session_data.get('apiV3AccessToken')
                if v3:
                    tokens_to_try.append(v3)
                for tok in tokens_to_try:
                    for prefix in ("Bearer ", ""):
                        try:
                            hdrs = {
                                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                                'Accept': '*/*',
                                'Authorization': f"{prefix}{tok}"
                            }
                            rtry = self.session.get(billing_url, headers=hdrs, timeout=10)
                            print(f"[ClubOS] ◀ Member billing retry ({prefix or 'raw'}) -> {rtry.status_code}")
                            if rtry.status_code == 200:
                                bdata = rtry.json()
                                past = bdata.get('past', []) if isinstance(bdata, dict) else []
                                return "Past Due" if past else "Current"
                        except Exception:
                            continue
            except Exception:
                pass

            return None  # Could not determine payment status

        except Exception as e:
            print(f"Error getting payment status for member {member_id}: {e}")
            return None  # No fallbacks

    def search_member_id(self, name: str, email: str = None) -> str | None:
        """Best-effort live lookup of a ClubOS member ID by name/email using captured endpoints.

        Tries lightweight search endpoints seen in Charles sessions. Returns the first matching ID.
        """
        try:
            if not self.authenticated and not self.authenticate():
                return None
            # Ensure session alive before search
            self._ensure_session_alive()

            # 0) Try fast path via Assignees index if available
            try:
                idx = self.get_assignee_index(force_refresh=False)
                if idx:
                    if email and email.lower() in idx.get('by_email', {}):
                        return str(idx['by_email'][email.lower()])
                    norm = self._normalize_name(name)
                    if norm and norm in idx.get('by_name', {}):
                        return str(idx['by_name'][norm])
            except Exception:
                pass

            # Ensure we have a delegated browsing context to Personal Training/Dashboard first
            try:
                self.session.get(f"{self.base_url}/action/Dashboard/view", timeout=10)
            except Exception:
                pass

            # Add Authorization if available
            bearer = self.session_data.get('apiV3AccessToken') or self.access_token
            headers_json = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Members',
            }
            if bearer:
                headers_json['Authorization'] = f'Bearer {bearer}'

            # Build name variants to increase match chances
            name_variants = []
            raw = (name or '').strip()
            if raw:
                name_variants.append(raw)
                # Handle "Last, First" -> "First Last"
                if ',' in raw:
                    parts = [p.strip() for p in raw.split(',')]
                    if len(parts) >= 2:
                        name_variants.append(f"{parts[1]} {parts[0]}")
                toks = raw.split()
                if len(toks) >= 2:
                    first, last = toks[0], toks[-1]
                    name_variants.append(first)
                    name_variants.append(last)
            name_variants = [v for i, v in enumerate(name_variants) if v and v not in name_variants[:i]]

            # Try a few known search endpoints and payload styles
            # Base headers for UserSuggest endpoints (match HAR more closely)
            suggest_get_headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar',
            }
            suggest_post_headers = {
                **suggest_get_headers,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            if bearer:
                suggest_get_headers['Authorization'] = f'Bearer {bearer}'
                suggest_post_headers['Authorization'] = f'Bearer {bearer}'
            # Also prepare non-auth variants in case endpoint doesn't require Authorization
            suggest_get_headers_noauth = {k: v for k, v in suggest_get_headers.items() if k != 'Authorization'}
            suggest_post_headers_noauth = {k: v for k, v in suggest_post_headers.items() if k != 'Authorization'}

            attempts = [
                # Generic API/member searches (may 404 but cheap to try)
                { 'method': 'GET',  'url': f"{self.base_url}/api/members/search",                  'params': {'q': raw, 'term': raw, 'name': raw, 'keyword': raw} },
                { 'method': 'POST', 'url': f"{self.base_url}/api/members/search",                  'json':   {'query': raw, 'term': raw, 'name': raw, 'limit': 10} },
                { 'method': 'POST', 'url': f"{self.base_url}/ajax/members/search",                 'data':   {'query': raw, 'term': raw, 'name': raw, 'limit': 10} },
                # Observed in utilities: UserSearch endpoint
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSearch",                   'params': {'q': raw, 'query': raw, 'term': raw, 'keyword': raw}, 'headers': headers_json },
                # Captured UserSuggest endpoints (observed to work in browser)
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global/",          'params': {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers },
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global/",          'data':   {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers },
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global",           'params': {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers },
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global",           'data':   {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers },
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global/",          'params': {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers_noauth },
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global/",          'data':   {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers_noauth },
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global",           'params': {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers_noauth },
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global",           'data':   {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers_noauth },
                # attendee-search prefers keyword + assignedOnly (per HAR)
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/attendee-search",  'data':   {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false'},      'headers': suggest_post_headers },
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/attendee-search",  'params': {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false'},      'headers': suggest_get_headers },
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/attendee-search",  'data':   {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false'},      'headers': suggest_post_headers_noauth },
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/attendee-search",  'params': {'keyword': raw, 'query': raw, 'q': raw, 'term': raw, 'assignedOnly': 'false'},      'headers': suggest_get_headers_noauth },
                # Fallback payload shapes
                { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/attendee-search",  'data':   {'q': raw, 'term': raw, 'name': raw},                         'headers': suggest_post_headers },
                { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/attendee-search",  'params': {'q': raw, 'term': raw, 'name': raw},                         'headers': suggest_get_headers },
            ]

            # Add attempts for individual name variants to improve recall
            for nv in name_variants:
                attempts.extend([
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global/",         'params': {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers },
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global/",         'data':   {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers },
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global",          'params': {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers },
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global",          'data':   {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers },
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global/",         'params': {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers_noauth },
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global/",         'data':   {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers_noauth },
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/global",          'params': {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50}, 'headers': suggest_get_headers_noauth },
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/global",          'data':   {'keyword': nv, 'query': nv, 'q': nv, 'assignedOnly': 'false', 'limit': 50},     'headers': suggest_post_headers_noauth },
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/attendee-search", 'data':   {'keyword': nv, 'query': nv, 'assignedOnly': 'false'},      'headers': suggest_post_headers },
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/attendee-search", 'params': {'keyword': nv, 'query': nv, 'assignedOnly': 'false'},      'headers': suggest_get_headers },
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/attendee-search", 'data':   {'keyword': nv, 'query': nv, 'assignedOnly': 'false'},      'headers': suggest_post_headers_noauth },
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/attendee-search", 'params': {'keyword': nv, 'query': nv, 'assignedOnly': 'false'},      'headers': suggest_get_headers_noauth },
                    # Fallback payload shapes
                    { 'method': 'POST', 'url': f"{self.base_url}/action/UserSuggest/attendee-search", 'data':   {'q': nv, 'term': nv, 'name': nv},                         'headers': suggest_post_headers },
                    { 'method': 'GET',  'url': f"{self.base_url}/action/UserSuggest/attendee-search", 'params': {'q': nv, 'term': nv, 'name': nv},                         'headers': suggest_get_headers },
                ])

            logger.info(f"[ClubOS] Starting live search for '{name}' with {len(attempts)} attempts")
            for attempt in attempts:
                try:
                    dbg = f"{attempt['method']} {attempt['url'].replace(self.base_url,'')}"
                    req_headers = attempt.get('headers') or headers_json
                    if attempt['method'] == 'GET':
                        r = self.session.get(attempt['url'], headers=req_headers, params=attempt.get('params'), timeout=10)
                    elif 'json' in attempt:
                        r = self.session.post(attempt['url'], headers=req_headers, json=attempt['json'], timeout=10)
                    else:
                        r = self.session.post(attempt['url'], headers=req_headers, data=attempt.get('data'), timeout=10)

                    logger.info(f"[ClubOS] search attempt {dbg} -> {r.status_code}")
                    if r.status_code != 200:
                        continue

                    # Parse possible shapes: list of members, dict with 'members' or 'results', or single dict
                    try:
                        data = r.json()
                        # Debug JSON shape
                        if isinstance(data, list):
                            logger.info(f"[ClubOS] 200 JSON from {dbg}: list len={len(data)}")
                            if not data:
                                # include tiny snippet to see actual payload
                                logger.info(f"[ClubOS] empty list payload from {dbg}; snippet: {(r.text or '')[:200].replace('\n',' ')}")
                        elif isinstance(data, dict):
                            logger.info(f"[ClubOS] 200 JSON from {dbg}: dict keys={list(data.keys())[:6]}")
                            if not data:
                                logger.info(f"[ClubOS] empty dict payload from {dbg}; snippet: {(r.text or '')[:200].replace('\n',' ')}")
                    except Exception:
                        # Fallback: try to extract IDs from raw text/HTML snippets, but only if the name appears nearby
                        text = r.text or ''
                        ctype = r.headers.get('Content-Type', '')
                        logger.info(f"[ClubOS] 200 non-JSON from {dbg} (Content-Type: {ctype}); snippet: {text[:240].replace('\n',' ') if text else ''}")
                        # Skip HTML extraction on generic UserSearch page to avoid unrelated links
                        if '/action/UserSearch' in dbg:
                            continue
                        # Only trust HTML extraction if the searched name appears in the document
                        name_lc = (name or '').strip().lower()
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(text, 'html.parser')
                            # Prefer anchors whose visible text contains the name
                            if name_lc:
                                for a in soup.find_all('a', href=True):
                                    label = (a.get_text(' ', strip=True) or '').lower()
                                    if label and name_lc in label:
                                        href = a['href']
                                        mm = re.search(r"/Members/view/(\d+)", href) or re.search(r"/action/Members/view/(\d+)", href)
                                        if mm:
                                            return mm.group(1)
                                        # Check common id-carrying attributes on the same element
                                        for attr in ('data-id','data-member-id','data-memberid','data-user-id','data-userid','data-value','value'):
                                            aval = a.get(attr)
                                            if aval and str(aval).isdigit():
                                                return str(int(aval))
                            # If name not present or no matching anchors, avoid taking the first generic /Members/view link
                            # As a very last resort on suggest-like widgets, accept explicit id attributes without name only if the response is tiny (autocomplete widget)
                            if text and len(text) < 2000:
                                m = re.search(r"data-value\s*=\s*['\"](\d{5,9})['\"]", text) or re.search(r"(?:data-id|value)\s*=\s*['\"](\d{5,9})['\"]", text)
                                if m:
                                    return m.group(1)
                            # Otherwise skip this attempt
                            continue
                        except Exception:
                            # If BeautifulSoup not available or parsing fails, fall back to very conservative regex only when name appears nearby
                            if name_lc and (name_lc in (text.lower())):
                                # Try to find the link preceding the name occurrence
                                m = re.search(r"/Members/view/(\d+)", text)
                                if m:
                                    return m.group(1)
                            continue

                    def extract_id(obj):
                        # Try common numeric fields first
                        for key in ('id', 'memberId', 'userId', 'value'):
                            if key in obj:
                                val = obj[key]
                                # Direct numeric
                                if isinstance(val, (int,)) or (isinstance(val, str) and val.isdigit()):
                                    return str(val)
                                # Try to parse from strings like "Member 12345" or URLs
                                if isinstance(val, str):
                                    mm = re.search(r"/Members/view/(\d+)", val) or re.search(r"\b(\d{5,9})\b", val)
                                    if mm:
                                        return mm.group(1)
                        # Try generic URL-like fields
                        for v in obj.values():
                            if isinstance(v, str) and '/Members/view/' in v:
                                mm = re.search(r"/Members/view/(\d+)", v)
                                if mm:
                                    return mm.group(1)
                        return None

                    # If list
                    if isinstance(data, list) and data:
                        # Optionally filter by email if present
                        if email:
                            for item in data:
                                if str(item.get('email','')).lower() == str(email).lower():
                                    found = extract_id(item)
                                    if found:
                                        return found
                        # Fallback to first with an ID
                        for item in data:
                            found = extract_id(item)
                            if found:
                                return found

                    # If dict with 'members'
                    if isinstance(data, dict) and 'members' in data and isinstance(data['members'], list):
                        logger.info(f"[ClubOS] members[] len={len(data['members'])}")
                        if not data['members']:
                            # log mini snippet
                            logger.info(f"[ClubOS] members empty; snippet: {(r.text or '')[:200].replace('\n',' ')}")
                        else:
                            if email:
                                for item in data['members']:
                                    if str(item.get('email','')).lower() == str(email).lower():
                                        found = extract_id(item)
                                        if found:
                                            return found
                            for item in data['members']:
                                found = extract_id(item)
                                if found:
                                    return found

                    # If dict with 'results' (common for suggest endpoints)
                    if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
                        logger.info(f"[ClubOS] results[] len={len(data['results'])}")
                        if not data['results']:
                            logger.info(f"[ClubOS] results empty; snippet: {(r.text or '')[:200].replace('\n',' ')}")
                        else:
                            if email:
                                for item in data['results']:
                                    if str(item.get('email','')).lower() == str(email).lower():
                                        found = extract_id(item)
                                        if found:
                                            return found
                            for item in data['results']:
                                found = extract_id(item)
                                if found:
                                    return found

                    # If single dict with an id
                    if isinstance(data, dict):
                        found = extract_id(data)
                        if found:
                            return found

                except Exception:
                    # Continue with next attempt on any error
                    continue

            # Last-resort HTML scrape of Members/Assignees pages with strict name matching
            try:
                html_headers = {
                    'User-Agent': headers_json['User-Agent'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Referer': f'{self.base_url}/action/Members'
                }
                pages = [
                    # Try common query param names observed in various flows
                    (f"{self.base_url}/action/Members", {'q': name, 'term': name, 'name': name}),
                    (f"{self.base_url}/action/Members", {'keyword': name}),
                    (f"{self.base_url}/action/Members", {'query': name}),
                    (f"{self.base_url}/action/Members", {'search': name}),
                    (f"{self.base_url}/action/Assignees", None),
                ]
                for url, params in pages:
                    try:
                        rr = self.session.get(url, headers=html_headers, params=params, timeout=15)
                        if rr.status_code != 200:
                            continue
                        txt = rr.text or ''
                        # Require the searched name to appear in the page to consider any match
                        name_lc = (name or '').strip().lower()
                        if name_lc and (name_lc not in txt.lower()):
                            continue
                        # Parse anchors near the name and scan common attributes
                        try:
                            soup = BeautifulSoup(txt, 'html.parser')
                            # Match anchors whose text contains the search name
                            for a in soup.find_all('a', href=True):
                                label = (a.get_text(" ", strip=True) or '')
                                if not label:
                                    continue
                                if name_lc in label.lower():
                                    href = a['href']
                                    mm = re.search(r"/Members/view/(\d+)", href) or re.search(r"/action/Members/view/(\d+)", href)
                                    if mm:
                                        return mm.group(1)
                                    # If anchor has data attributes with ID
                                    for attr in ('data-id','data-member-id','data-memberid','data-user-id','data-userid','data-value','value'):
                                        aval = a.get(attr)
                                        if aval and str(aval).isdigit():
                                            return str(int(aval))
                            # Also scan list items/options that may contain IDs
                            for tag in soup.find_all(['li','option','div','span']):
                                # Heuristic: contains the name and an id-like attribute
                                textlbl = (tag.get_text(" ", strip=True) or '').lower()
                                if name_lc in textlbl:
                                    for attr in ('data-id','data-member-id','data-memberid','data-user-id','data-userid','data-value','value'):
                                        aval = tag.get(attr)
                                        if aval and str(aval).isdigit():
                                            return str(int(aval))
                                # Fallback: embedded link
                                href = tag.get('href')
                                if href and ('/Members/view/' in href or '/action/Members/view/' in href):
                                    mm = re.search(r"/Members/view/(\d+)", href) or re.search(r"/action/Members/view/(\d+)", href)
                                    if mm:
                                        return mm.group(1)
                        except Exception:
                            pass
                    except Exception:
                        continue
            except Exception:
                pass

            return None
        except Exception:
            return None

    # ---- Assignees helpers -------------------------------------------------
    def _normalize_name(self, name: str | None) -> str | None:
        if not name:
            return None
        try:
            # Lowercase, remove punctuation and excess spaces
            cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", name).lower()
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            return cleaned if cleaned else None
        except Exception:
            return None

    def fetch_assignees(self, force_refresh: bool = False) -> list[dict]:
        """Fetch the Assignees page and parse a list of members with ClubOS IDs.

    Returns a list of { 'id': int, 'name': str | None, 'email': str | None, 'phone': str | None }.
        Caches results for 15 minutes.
        """
        try:
            now = time.time()
            # 15-minute TTL
            if not force_refresh and self._assignees_cache and (now - self._assignees_fetched_at) < 900:
                return self._assignees_cache

            if not self.authenticated and not self.authenticate():
                return []

            url = f"{self.base_url}/action/Assignees"
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            r = self.session.get(url, headers=headers, timeout=20)
            if r.status_code != 200:
                logger.warning(f"[ClubOS] Assignees page status: {r.status_code}")
                return []

            html = r.text or ''
            soup = BeautifulSoup(html, 'html.parser')
            assignees: list[dict] = []

            # Strategy 1: find explicit member links
            for a in soup.find_all('a', href=True):
                href = a['href']
                m = re.search(r"/Members/view/(\d+)", href)
                if not m:
                    m = re.search(r"/action/Members/view/(\d+)", href)
                if not m:
                    continue
                mid = int(m.group(1))

                # Try to get display name
                name_text = a.get_text(strip=True) or None
                # Search nearby for an email (mailto link) in the same row/container
                email_text = None
                phone_text = None
                container = a.find_parent(['tr', 'div', 'li']) or a.parent
                if container:
                    mail = container.find('a', href=re.compile(r'^mailto:', re.I))
                    if mail and isinstance(mail.get('href'), str):
                        email_text = mail.get('href').split(':', 1)[-1]
                    # Try to extract phone-like text near the link
                    try:
                        surrounding = container.get_text(" ", strip=True) or ''
                        # Simple US phone pattern
                        pm = re.search(r'(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}', surrounding)
                        if pm:
                            phone_text = pm.group(0)
                    except Exception:
                        pass

                assignees.append({'id': mid, 'name': name_text, 'email': email_text, 'phone': phone_text})

            # Strategy 2: regex fallback in raw HTML (in case content is not well-structured)
            if not assignees:
                for m in re.finditer(r"/Members/view/(\d+)", html):
                    mid = int(m.group(1))
                    assignees.append({'id': mid, 'name': None, 'email': None})

            # Deduplicate by id, prefer entries with a name/email
            by_id: dict[int, dict] = {}
            for row in assignees:
                rid = row['id']
                if rid not in by_id:
                    by_id[rid] = row
                else:
                    # Merge fields if missing
                    if not by_id[rid].get('name') and row.get('name'):
                        by_id[rid]['name'] = row['name']
                    if not by_id[rid].get('email') and row.get('email'):
                        by_id[rid]['email'] = row['email']
                    if not by_id[rid].get('phone') and row.get('phone'):
                        by_id[rid]['phone'] = row['phone']

            result = list(by_id.values())
            self._assignees_cache = result
            self._assignees_index = None  # reset index; will rebuild on demand
            self._assignees_fetched_at = now
            logger.info(f"[ClubOS] Assignees fetched: {len(result)}")
            return result
        except Exception as e:
            logger.warning(f"[ClubOS] Failed to fetch assignees: {e}")
            return []

    def _normalize_phone(self, phone: str | None) -> str | None:
        if not phone or not isinstance(phone, str):
            return None
        try:
            digits = re.sub(r"\D", "", phone)
            if len(digits) >= 10:
                return digits[-10:]  # use last 10 digits
            return digits or None
        except Exception:
            return None

    def get_assignee_index(self, force_refresh: bool = False) -> dict | None:
        """Return an index of assignees for quick lookup by email or normalized name."""
        try:
            if force_refresh or self._assignees_cache is None:
                self.fetch_assignees(force_refresh=force_refresh)
            if not self._assignees_cache:
                # Fallback: build index via UserSuggest global scans
                try:
                    scanned = self._suggest_scan_index()
                    if scanned:
                        self._assignees_cache = scanned
                    else:
                        # Last resort: scrape Members directory HTML
                        scraped = self._scrape_members_directory(max_pages=5)
                        if scraped:
                            self._assignees_cache = scraped
                        else:
                            return None
                except Exception:
                    try:
                        scraped = self._scrape_members_directory(max_pages=5)
                        if scraped:
                            self._assignees_cache = scraped
                        else:
                            return None
                    except Exception:
                        return None

            if self._assignees_index is not None and not force_refresh:
                return self._assignees_index

            by_email: dict[str, int] = {}
            by_name: dict[str, int] = {}
            by_phone: dict[str, int] = {}
            for row in self._assignees_cache:
                mid = row.get('id')
                if not mid:
                    continue
                em = (row.get('email') or '').strip().lower()
                nm = self._normalize_name(row.get('name'))
                ph = self._normalize_phone(row.get('phone'))
                if em:
                    by_email[em] = int(mid)
                if nm:
                    by_name[nm] = int(mid)
                if ph:
                    by_phone[ph] = int(mid)

            self._assignees_index = {'by_email': by_email, 'by_name': by_name, 'by_phone': by_phone}
            return self._assignees_index
        except Exception:
            return None

    def _scrape_members_directory(self, max_pages: int = 5) -> list[dict] | None:
        """Scrape the Members directory HTML to build a coarse member list when APIs fail."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': f'{self.base_url}/action/Dashboard/view'
            }
            aggregated: dict[int, dict] = {}
            urls = [f"{self.base_url}/action/Members"]
            # Try simple pagination param up to max_pages
            for p in range(2, max_pages + 1):
                urls.append(f"{self.base_url}/action/Members?page={p}")
            for url in urls:
                try:
                    r = self.session.get(url, headers=headers, timeout=20)
                    if r.status_code != 200:
                        continue
                    html = r.text or ''
                    soup = BeautifulSoup(html, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        m = re.search(r"/Members/view/(\d+)", href) or re.search(r"/action/Members/view/(\d+)", href)
                        if not m:
                            continue
                        mid = int(m.group(1))
                        name = a.get_text(" ", strip=True) or None
                        email = None
                        container = a.find_parent(['tr', 'div', 'li']) or a.parent
                        if container:
                            mail = container.find('a', href=re.compile(r'^mailto:', re.I))
                            if mail and isinstance(mail.get('href'), str):
                                email = mail.get('href').split(':', 1)[-1]
                        if mid not in aggregated:
                            aggregated[mid] = {'id': mid, 'name': name, 'email': email, 'phone': None}
                        else:
                            if name and not aggregated[mid].get('name'):
                                aggregated[mid]['name'] = name
                            if email and not aggregated[mid].get('email'):
                                aggregated[mid]['email'] = email
                except Exception:
                    continue
            result = list(aggregated.values())
            if result:
                logger.info(f"[ClubOS] Members directory scrape built index of {len(result)} members")
            return result
        except Exception:
            return None

    def _suggest_scan_index(self) -> list[dict] | None:
        """Scan UserSuggest endpoint with multiple keywords to build a coarse member index."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            headers_json = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Members',
            }
            keywords = ['a','e','i','o','u','s','n','r','t','l','m']
            aggregated: dict[int, dict] = {}
            for kw in keywords:
                try:
                    r = self.session.get(
                        f"{self.base_url}/action/UserSuggest/global/",
                        headers=headers_json,
                        params={'keyword': kw, 'assignedOnly': 'false'},
                        timeout=10
                    )
                    if r.status_code != 200:
                        continue
                    data = None
                    parsed_list = []
                    try:
                        data = r.json()
                    except Exception:
                        data = None
                    if isinstance(data, list):
                        parsed_list = data
                    else:
                        # Try to extract list-like items from HTML
                        text = r.text or ''
                        # Look for JSON-like arrays embedded
                        try:
                            # Simple heuristic: find occurrences of Members/view/ID or data-value="ID"
                            for m in re.finditer(r"/Members/view/(\d+)", text):
                                parsed_list.append({'id': m.group(1)})
                            for m in re.finditer(r"data-value\s*=\s*['\"](\d{5,9})['\"]", text):
                                parsed_list.append({'id': m.group(1)})
                            for m in re.finditer(r"(?:data-id|value)\s*=\s*['\"](\d{5,9})['\"]", text):
                                parsed_list.append({'id': m.group(1)})
                        except Exception:
                            pass
                    if not parsed_list:
                        continue
                    for item in parsed_list:
                        # Attempt to extract id, name, email
                        mid = None
                        for key in ('id','memberId','userId','value'):
                            if key in item and str(item[key]).isdigit():
                                mid = int(item[key])
                                break
                        if not mid:
                            # Try parsing URL-like fields
                            for v in item.values():
                                if isinstance(v, str) and '/Members/view/' in v:
                                    m = re.search(r"/Members/view/(\d+)", v)
                                    if m:
                                        mid = int(m.group(1))
                                        break
                        if not mid:
                            continue
                        name = item.get('label') or item.get('display') or item.get('name')
                        email = item.get('email') or None
                        if mid not in aggregated:
                            aggregated[mid] = {'id': mid, 'name': name, 'email': email, 'phone': None}
                        else:
                            if name and not aggregated[mid].get('name'):
                                aggregated[mid]['name'] = name
                            if email and not aggregated[mid].get('email'):
                                aggregated[mid]['email'] = email
                except Exception:
                    continue
            result = list(aggregated.values())
            logger.info(f"[ClubOS] UserSuggest scan built index of {len(result)} members")
            return result
        except Exception:
            return None
