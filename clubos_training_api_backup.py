#!/usr/bin/env python3
from __future__ import annotations
"""
ClubOS Training Package API - HAR-based implementation

Provides: ClubOSTrainingPackageAPI
- authenticate(): start a logged-in session to ClubOS
- search_member_id(name, email=None, phone=None) -> Optional[str]
- get_member_payment_status(member_id) -> Optional[str]  # 'Current' | 'Past Due' | None
- fetch_assignees() / get_assignee_index() helpers
- discover_member_agreement_ids(member_id) -> list[str] # Find agreement IDs
- get_agreement_total_value(agreement_id) -> Optional[dict]
- get_agreement_salespeople(agreement_id) -> Optional[dict]
- get_member_package_agreements(member_id) -> list[dict] # Complete implementation
"""

import json
import logging
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
import threading


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClubOSTrainingPackageAPI:
    """HAR-based client for Training lookups in ClubOS used by clean_dashboard.py."""

    def __init__(self) -> None:
        # Credentials come from config; avoid printing secrets
        try:
            from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD  # type: ignore
            self.username = CLUBOS_USERNAME
            self.password = CLUBOS_PASSWORD
        except Exception:
            self.username = None
            self.password = None

        self.base_url = "https://anytime.club-os.com"
        self.session = requests.Session()
        self.authenticated = False
        self.access_token: Optional[str] = None
        self.session_data: dict = {}
        
        # Auth coordination
        self._auth_lock = threading.Lock()
        self._auth_in_progress = False
        self._last_auth_attempt_at: float = 0.0
        self._last_auth_success_at: float = 0.0
        self._auth_cooldown_seconds: float = 8.0  # minimum spacing between login attempts

        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{self.base_url}/action/Dashboard/view',
        })

        # Assignees cache
        self._assignees_cache: Optional[list[dict]] = None
        self._assignees_index: Optional[dict] = None
        self._assignees_fetched_at: float = 0.0

    # ---------- helpers ----------
    def _ensure_session_alive(self) -> None:
        try:
            self.session.get(f"{self.base_url}/action/Dashboard/view", timeout=10)
        except Exception:
            pass

    def _normalize_name(self, name: str | None) -> str | None:
        if not name:
            return None
        try:
            cleaned = re.sub(r"[^a-z0-9\s]", " ", str(name).lower())
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            return cleaned or None
        except Exception:
            return None

    def _normalize_phone(self, phone: str | None) -> str | None:
        if not phone:
            return None
        try:
            digits = re.sub(r"\D", "", str(phone))
            if len(digits) >= 10:
                return digits[-10:]
            return digits or None
        except Exception:
            return None

    # ---------- public API ----------
    def authenticate(self) -> bool:
        """Authenticate to ClubOS using the same /action/Login flow used elsewhere."""
        try:
            # Fast-path: if already authenticated and session is alive, return
            if self.authenticated:
                try:
                    test_response = self.session.get(f"{self.base_url}/action/Dashboard/view", timeout=5)
                    if test_response.status_code == 200:
                        logger.info("✅ Existing ClubOS session is still valid")
                        return True
                except Exception:
                    logger.info("🔄 Existing session expired, re-authenticating...")

            if not self.username or not self.password:
                logger.warning("ClubOS credentials missing; cannot authenticate.")
                return False

            # Throttle: avoid rapid-fire logins from concurrent requests
            now = time.time()
            # Passive wait if another thread is currently authenticating
            if self._auth_in_progress:
                start_wait = now
                while self._auth_in_progress and (time.time() - start_wait) < 12.0:
                    time.sleep(0.15)
                # If after wait we got authenticated by another thread, return
                if self.authenticated:
                    return True

            # Enforce cooldown between attempts
            elapsed_since_attempt = now - self._last_auth_attempt_at
            if elapsed_since_attempt < self._auth_cooldown_seconds:
                wait_s = self._auth_cooldown_seconds - elapsed_since_attempt
                logger.info(f"⏳ Throttling login attempt for {wait_s:.1f}s to avoid 403s")
                time.sleep(min(wait_s, 2.0))  # cap individual sleeps to keep responsiveness

            # Acquire lock to ensure only one active login
            acquired = self._auth_lock.acquire(timeout=12.0)
            if not acquired:
                # As a fallback, wait briefly for another thread to complete
                logger.info("⏳ Waiting for ongoing authentication to complete")
                start_wait = time.time()
                while self._auth_in_progress and (time.time() - start_wait) < 10.0:
                    time.sleep(0.2)
                return self.authenticated

            self._auth_in_progress = True
            self._last_auth_attempt_at = time.time()

            # Reset/prepare session state
            if not hasattr(self, 'session') or self.session is None:
                self.session = requests.Session()

            self.authenticated = False
            self.access_token = None
            self.session_data = {}

            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Dashboard/view',
            })

            # Step 1: GET login page and extract tokens
            r0 = self.session.get(f"{self.base_url}/action/Login/view", timeout=20)
            if r0.status_code not in (200, 302):
                logger.error(f"Login view GET failed: {r0.status_code}")
                return False

            _sourcePage = None
            __fp = None
            try:
                soup = BeautifulSoup(r0.text, 'html.parser')
                sp = soup.find('input', {'name': '_sourcePage'})
                fp = soup.find('input', {'name': '__fp'})
                _sourcePage = sp.get('value') if sp else ''
                __fp = fp.get('value') if fp else ''
            except Exception:
                _sourcePage = ''
                __fp = ''

            # Step 2: POST credentials to /action/Login with limited retries/backoff
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'{self.base_url}/action/Login/view',
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
            }
            form = {
                'login': 'Submit',
                'username': self.username,
                'password': self.password,
                '_sourcePage': _sourcePage or '',
                '__fp': __fp or '',
            }

            attempt_status = None
            backoffs = [0.0, 1.5, 3.0]  # first attempt immediate, then backoff
            for i, delay in enumerate(backoffs):
                if delay > 0:
                    time.sleep(delay)
                r1 = self.session.post(f"{self.base_url}/action/Login", data=form, headers=headers, timeout=30, allow_redirects=True)
                attempt_status = r1.status_code
                if attempt_status in (200, 302):
                    break
                # For 403 specifically, continue to next retry
                if attempt_status == 403 and i < len(backoffs) - 1:
                    logger.warning("⚠️ Login POST returned 403; retrying with backoff")
                    continue
                else:
                    break

            if attempt_status not in (200, 302):
                logger.error(f"Login POST failed: {attempt_status}")
                return False

            cookies = self.session.cookies.get_dict()
            if 'JSESSIONID' not in cookies:
                logger.error("Missing JSESSIONID; login likely failed.")
                return False

            # Capture tokens if present
            self.access_token = cookies.get('apiV3AccessToken') or self.access_token
            self.session_data['apiV3AccessToken'] = self.access_token

            # Touch dashboard to finalize
            self.session.get(f"{self.base_url}/action/Dashboard", timeout=15)
            self.authenticated = True
            self._last_auth_success_at = time.time()
            logger.info("ClubOS Training API: authenticated via /action/Login")
            return True
        except Exception as e:
            logger.error(f"authenticate error: {e}")
            self.authenticated = False
            return False
        finally:
            # Release lock and clear in-progress flag
            try:
                self._auth_in_progress = False
                if self._auth_lock.locked():
                    self._auth_lock.release()
            except Exception:
                pass

    def search_member_id(self, name: str, email: str | None = None, phone: str | None = None) -> str | None:
        """Resolve a memberId via attendee-search (same widget Calendar uses)."""
        try:
            q = (name or email or phone or '').strip()
            if not q:
                return None

            if not self.authenticated and not self.authenticate():
                return None
            self._ensure_session_alive()

            name_norm = self._normalize_name(name)
            email_lc = (email or '').strip().lower() or None
            phone_norm = self._normalize_phone(phone)

            url = f"{self.base_url}/action/UserSuggest/attendee-search"
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Calendar',
            }
            bearer = self.session_data.get('apiV3AccessToken') or self.access_token
            if bearer:
                headers['Authorization'] = f'Bearer {bearer}'
            params = {'keyword': q, 'assignedOnly': 'false', 'limit': 50}

            r = self.session.get(url, headers=headers, params=params, timeout=12)
            if r.status_code != 200 or not r.text:
                return None

            soup = BeautifulSoup(r.text, 'html.parser')
            li_nodes = soup.find_all('li', class_=re.compile(r"\bperson\b", re.I))
            for li in li_nodes:
                data_input = li.find('input', class_=re.compile(r"\bdata\b", re.I))
                cand_name = None
                cand_id = None
                if data_input is not None:
                    raw_val = data_input.get('value') or ''
                    try:
                        j = json.loads(raw_val)
                        if isinstance(j, dict):
                            cand_name = self._normalize_name(j.get('name'))
                            cid = j.get('id')
                            if isinstance(cid, int) or (isinstance(cid, str) and cid.isdigit()):
                                cand_id = str(cid)
                    except Exception:
                        pass
                if not cand_id:
                    li_id = li.get('id')
                    if li_id and str(li_id).isdigit():
                        cand_id = str(int(li_id))

                visible = (li.get_text(' ', strip=True) or '').lower()

                match = False
                if name_norm:
                    vn = cand_name or self._normalize_name(visible)
                    match = bool(vn) and (vn == name_norm or name_norm in vn)
                if not match and email_lc:
                    match = email_lc in visible
                if not match and phone_norm:
                    match = phone_norm in re.sub(r"\D", "", visible)

                if match and cand_id:
                    return cand_id

            return None
        except Exception as e:
            logger.warning(f"search_member_id error: {e}")
            return None

    def get_member_payment_status(self, member_id: str | int) -> Optional[str]:
        """Return 'Current' or 'Past Due' when confidently determined; else None."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            self._ensure_session_alive()

            mid = str(member_id).strip()
            pages = [
                f"{self.base_url}/action/Members/view/{mid}",
                f"{self.base_url}/action/Members/{mid}",
                f"{self.base_url}/action/Agreements?memberId={mid}",
            ]
            for url in pages:
                try:
                    r = self.session.get(url, timeout=15)
                    if r.status_code != 200 or not r.text:
                        continue
                    doc = r.text.lower()
                    if 'past due' in doc:
                        return 'Past Due'
                    if re.search(r"\bstatus\s*:\s*current\b", doc) or 'account is current' in doc:
                        return 'Current'
                except Exception:
                    continue
            return None
        except Exception as e:
            logger.warning(f"get_member_payment_status error: {e}")
            return None

    def get_member_raw_training_data(self, member_id: str | int) -> dict:
        """Get ALL raw training package data for a member - no filtering, return everything."""
        try:
            # Ensure logged in
            if not self.authenticate():
                logger.error("❌ ClubOS authentication failed for raw training data")
                return {'error': 'Authentication failed', 'data': None}

            mid = str(member_id).strip()
            logger.info(f"🔍 Getting RAW training data for member: {mid}")

            # Step 1: Delegate to this member context 
            delegation_success = self.delegate_to_member(mid)
            logger.info(f"🔑 Delegation to {mid}: {'✅ Success' if delegation_success else '❌ Failed'}")

            # Step 2: Discover agreement IDs for this member
            agreement_ids = self.discover_member_agreement_ids(mid)
            logger.info(f"📋 Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            if not agreement_ids:
                return {
                    'member_id': mid,
                    'delegation_success': delegation_success,
                    'agreement_ids': [],
                    'agreements_data': [],
                    'message': 'No agreement IDs found'
                }

            # Step 3: Get RAW details for each agreement - NO FILTERING
            agreements_data = []
            
            for agreement_id in agreement_ids:
                try:
                    logger.info(f"🔍 Processing agreement {agreement_id}...")
                    
                    # Get raw agreement total value data
                    total_value_data = self.get_agreement_total_value(agreement_id)
                    logger.info(f"💰 Agreement {agreement_id} total_value_data: {total_value_data}")
                    
                    # Get raw salespeople data
                    salespeople_data = self.get_agreement_salespeople(agreement_id)
                    logger.info(f"👥 Agreement {agreement_id} salespeople_data: {salespeople_data}")
                    
                    # Combine all raw data
                    agreement_raw = {
                        'agreement_id': agreement_id,
                        'total_value_data': total_value_data,
                        'salespeople_data': salespeople_data,
                        'has_total_value': total_value_data is not None,
                        'has_salespeople': salespeople_data is not None
                    }
                    
                    agreements_data.append(agreement_raw)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error getting raw data for agreement {agreement_id}: {e}")
                    agreements_data.append({
                        'agreement_id': agreement_id,
                        'error': str(e),
                        'total_value_data': None,
                        'salespeople_data': None
                    })

            return {
                'member_id': mid,
                'delegation_success': delegation_success,
                'agreement_ids': agreement_ids,
                'agreements_data': agreements_data,
                'total_agreements': len(agreements_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting raw training data for member {member_id}: {e}")
            return {'error': str(e), 'data': None}

    def fetch_assignees(self, force_refresh: bool = False) -> list[dict]:
        """Parse /action/Assignees to build a minimal list of members with IDs."""
        try:
            now = time.time()
            if not force_refresh and self._assignees_cache and (now - self._assignees_fetched_at) < 900:
                return self._assignees_cache

            # Only authenticate if not already authenticated
            if not self.authenticated:
                if not self.authenticate():
                    logger.error("❌ Authentication failed for fetch_assignees")
                    return []

            # Use the working AJAX endpoint that returns actual assignee data
            timestamp = int(time.time() * 1000)  # JavaScript-style timestamp
            url = f"{self.base_url}/action/Assignees/members?_={timestamp}"
            
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/action/Assignees',
            }
            
            logger.info(f"🔍 Fetching assignees from AJAX endpoint: {url}")
            r = self.session.get(url, headers=headers, timeout=20)
            
            if r.status_code != 200:
                logger.error(f"❌ Failed to fetch assignees: HTTP {r.status_code}")
                # Try the main assignees page instead
                return self._fetch_assignees_from_main_page()

            # Debug: Log the actual response to understand why JSON parsing is failing
            response_text = (r.text or '')[:200]  # First 200 chars
            logger.info(f"🔍 AJAX response preview: {response_text}")

            # Try to parse as JSON first (AJAX endpoint should return JSON)
            try:
                data = r.json()
                if isinstance(data, list):
                    assignees = []
                    for item in data:
                        # Extract member data from JSON response
                        member_id = item.get('id') or item.get('memberId') or item.get('member_id')
                        name = item.get('name') or item.get('memberName') or f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()
                        email = item.get('email') or item.get('emailAddress')
                        phone = item.get('phone') or item.get('phoneNumber')
                        
                        if member_id:
                            assignees.append({
                                'id': str(member_id),
                                'name': name or 'Unknown',
                                'email': email,
                                'phone': phone
                            })
                    
                    if assignees:
                        logger.info(f"✅ Found {len(assignees)} training clients from AJAX endpoint")
                        self._assignees_cache = assignees
                        self._assignees_fetched_at = time.time()
                        return assignees
                    else:
                        logger.warning("⚠️ AJAX endpoint returned empty list")
                        # Fallback to main page parsing
                        return self._fetch_assignees_from_main_page()
                else:
                    logger.warning(f"⚠️ AJAX endpoint returned unexpected data type: {type(data)}")
            except Exception as json_error:
                logger.warning(f"⚠️ Failed to parse JSON from AJAX endpoint: {json_error}")
                logger.info(f"🔍 Raw response that failed JSON parsing: {r.text[:500]}")
                # The AJAX endpoint might be returning HTML instead of JSON
                # Let's try parsing it as HTML to see if it has the assignee data
                if '<li' in r.text and 'delegate(' in r.text:
                    logger.info("🔍 AJAX endpoint returned HTML instead of JSON, parsing as HTML...")
                    soup = BeautifulSoup(r.text, 'html.parser')
                    assignees = []
                    
                    # Look for <li class="client assignee"> elements in the response
                    assignee_elements = soup.find_all('li', class_='client assignee')
                    logger.info(f"📋 Found {len(assignee_elements)} <li class='client assignee'> elements in AJAX response")
                    
                    for li in assignee_elements:
                        try:
                            # Look for delegate onclick in child elements (specifically <a> tags)
                            for link in li.find_all('a'):
                                link_onclick = link.get('onclick', '')
                                link_match = re.search(r'delegate\((\d+),', link_onclick)
                                if link_match:
                                    member_id = link_match.group(1)
                                    member_name = link.get_text(strip=True)
                                    
                                    # Check if we already have this member
                                    existing = next((a for a in assignees if a['id'] == member_id), None)
                                    if not existing:
                                        assignees.append({
                                            'id': member_id,
                                            'name': member_name or 'Unknown',
                                            'email': None,
                                            'phone': None
                                        })
                                        logger.info(f"📝 AJAX found assignee from link: ID={member_id}, Name={member_name}")
                                        
                        except Exception as e:
                            logger.warning(f"⚠️ Error parsing AJAX assignee element: {e}")
                            continue
                    
                    if assignees:
                        logger.info(f"✅ Found {len(assignees)} training clients from AJAX HTML response")
                        self._assignees_cache = assignees
                        self._assignees_fetched_at = time.time()
                        return assignees

            # Fallback: parse as HTML (ClubOS assignees page structure)
            return self._fetch_assignees_from_main_page()
            
        except Exception as e:
            logger.warning(f"fetch_assignees error: {e}")
            return []

    def _fetch_assignees_from_main_page(self) -> list[dict]:
        """Fallback method to fetch assignees from the main /action/Assignees page."""
        try:
            url = f"{self.base_url}/action/Assignees"
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': f'{self.base_url}/action/Dashboard',
            }
            
            logger.info("🔍 Fallback: Fetching assignees from main page")
            r = self.session.get(url, headers=headers, timeout=20)
            
            if r.status_code != 200:
                logger.error(f"❌ Failed to fetch main assignees page: HTTP {r.status_code}")
                return []

            html = r.text or ''
            soup = BeautifulSoup(html, 'html.parser')
            assignees: list[dict] = []

            # Look for ClubOS assignees using the correct pattern
            # <li class="client assignee" onclick="delegate(MEMBER_ID,'/action/Assignees')">
            logger.info("🔍 Parsing HTML for ClubOS assignees with correct pattern...")
            
            # Method 1: Look for <li class="client assignee"> elements
            assignee_elements = soup.find_all('li', class_='client assignee')
            logger.info(f"📋 Found {len(assignee_elements)} <li class='client assignee'> elements")
            
            for li in assignee_elements:
                try:
                    # Extract member ID from onclick="delegate(MEMBER_ID,'/action/Assignees')"
                    onclick = li.get('onclick', '')
                    onclick_match = re.search(r'delegate\((\d+),', onclick)
                    
                    if onclick_match:
                        member_id = onclick_match.group(1)
                        
                        # Extract member name from the li element text
                        member_name = li.get_text(strip=True)
                        
                        # Look for email and phone in the element
                        email = None
                        phone = None
                        
                        # Check for email links
                        email_link = li.find('a', href=re.compile(r'^mailto:', re.I))
                        if email_link:
                            email = email_link.get('href', '').replace('mailto:', '')
                        
                        # Check for phone numbers in text
                        text_content = li.get_text(' ', strip=True)
                        phone_match = re.search(r'(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}', text_content)
                        if phone_match:
                            phone = phone_match.group(0)
                        
                        assignees.append({
                            'id': member_id,
                            'name': member_name or 'Unknown',
                            'email': email,
                            'phone': phone
                        })
                        
                        logger.info(f"📝 Found assignee: ID={member_id}, Name={member_name}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing assignee element: {e}")
                    continue
            
            # Method 2: Fallback to looking for any onclick with delegate pattern
            if not assignees:
                logger.info("🔍 Fallback: Looking for any elements with delegate onclick pattern...")
                all_elements = soup.find_all(attrs={'onclick': re.compile(r'delegate\(\d+,')})
                logger.info(f"📋 Found {len(all_elements)} elements with delegate onclick")
                
                for element in all_elements:
                    try:
                        onclick = element.get('onclick', '')
                        onclick_match = re.search(r'delegate\((\d+),', onclick)
                        
                        if onclick_match:
                            member_id = onclick_match.group(1)
                            member_name = element.get_text(strip=True) or 'Unknown'
                            
                            assignees.append({
                                'id': member_id,
                                'name': member_name,
                                'email': None,
                                'phone': None
                            })
                            
                            logger.info(f"📝 Fallback found assignee: ID={member_id}, Name={member_name}")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Error parsing fallback element: {e}")
                        continue

            # Deduplicate and merge assignee data
            by_id: dict[str, dict] = {}
            for row in assignees:
                rid = str(row['id'])
                if rid not in by_id:
                    by_id[rid] = row
                else:
                    if not by_id[rid].get('name') and row.get('name'):
                        by_id[rid]['name'] = row['name']
                    if not by_id[rid].get('email') and row.get('email'):
                        by_id[rid]['email'] = row['email']
                    if not by_id[rid].get('phone') and row.get('phone'):
                        by_id[rid]['phone'] = row['phone']

            result = list(by_id.values())
            
            if result:
                logger.info(f"✅ Found {len(result)} training clients from main page HTML parsing")
                self._assignees_cache = result
                self._assignees_index = None
                self._assignees_fetched_at = time.time()
                return result
            else:
                logger.warning("⚠️ No training clients found in main page HTML")
                return []
                
        except Exception as e:
            logger.warning(f"_fetch_assignees_from_main_page error: {e}")
            return []

    def get_assignee_index(self, force_refresh: bool = False) -> dict | None:
        """Return an index of assignees for quick lookup by email/name/phone."""
        try:
            if force_refresh or self._assignees_cache is None:
                self.fetch_assignees(force_refresh=force_refresh)
            if not self._assignees_cache:
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

    # ---------- delegation + agreements ----------
    def _get_bearer_token(self) -> Optional[str]:
        """Extract apiV3AccessToken from cookies and cache it."""
        try:
            # Prefer previously captured token
            if self.access_token:
                return self.access_token
            cookies = self.session.cookies.get_dict()
            token = cookies.get('apiV3AccessToken')
            if token:
                self.access_token = token
                self.session_data['apiV3AccessToken'] = token
                return token
            return None
        except Exception:
            return None

    def _auth_headers(self, referer: Optional[str] = None) -> dict:
        """Build headers including Authorization Bearer when available."""
        h = {
            'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
        }
        if referer:
            h['Referer'] = referer
        bearer = self._get_bearer_token()
        if bearer:
            h['Authorization'] = f'Bearer {bearer}'
        return h

    def delegate_to_member(self, member_or_user_id: str | int) -> bool:
        """Delegate context to a specific member/user using the exact HAR file pattern.
        
        Sets delegation cookies: delegatedUserId={member_id}, staffDelegatedUserId=
        """
        try:
            if not self.authenticated and not self.authenticate():
                return False
            self._ensure_session_alive()

            mid = str(member_or_user_id).strip()
            
            # Use the exact delegation pattern from HAR files with timestamp
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/action/Delegate/{mid}/url=false"
            params = {'_': timestamp}
            
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': f'{self.base_url}/action/Assignees',
            }
            
            # Include Bearer token if available (from HAR)
            bearer = self._get_bearer_token()
            if bearer:
                headers['Authorization'] = f'Bearer {bearer}'
            
            logger.info(f"🔑 Delegating to member ID: {mid}")
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code in (200, 302):
                # Check for delegation cookies that should be set
                cookies = self.session.cookies.get_dict()
                delegated_user_id = cookies.get('delegatedUserId')
                
                if delegated_user_id:
                    logger.info(f"✅ Delegation successful - delegatedUserId: {delegated_user_id}")
                    # Refresh bearer token in case it changed
                    self._get_bearer_token()
                    return True
                else:
                    # Manually set delegation cookies if not automatically set
                    self.session.cookies.set('delegatedUserId', mid)
                    self.session.cookies.set('staffDelegatedUserId', '')
                    logger.info(f"✅ Delegation cookies manually set for member: {mid}")
                    return True
            else:
                logger.error(f"❌ Delegation failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Delegation error: {e}")
            return False

    def get_complete_agreement_data(self, agreement_id: str) -> dict:
        """Make all the API calls that a browser makes when viewing an agreement.
        
        This replicates the exact sequence from the HAR file:
        1. billing_status
        2. V2 data 
        3. salespeople
        4. agreementTotalValue
        """
        try:
            if not self.authenticate():
                return {"error": "Authentication failed"}

            logging.info(f"🔄 Getting complete agreement data for ID: {agreement_id} (browser-style)")
            
            # Headers that match browser behavior
            headers = self._auth_headers(referer=f"{self.base_url}/action/Agreements")
            
            results = {}
            
            # Step 1: billing_status (first call browser makes)
            try:
                billing_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
                billing_params = {'_': int(time.time() * 1000)}
                billing_response = self.session.get(billing_url, headers=headers, params=billing_params, timeout=10)
                if billing_response.status_code == 200:
                    results['billing_status'] = billing_response.json()
                    logging.info(f"✅ Billing status: {billing_response.status_code}")
                else:
                    results['billing_status'] = None
                    logging.warning(f"⚠️ Billing status failed: {billing_response.status_code} | preview: {(billing_response.text or '')[:200]}")
            except Exception as e:
                results['billing_status'] = None
                logging.warning(f"⚠️ Billing status error: {e}")
            
            # Step 2: V2 data (main agreement details)
            try:
                v2_url = f"{self.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
                v2_params = {
                    'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes'],
                    '_': int(time.time() * 1000)
                }
                v2_response = self.session.get(v2_url, headers=headers, params=v2_params, timeout=12)
                if v2_response.status_code == 200:
                    results['v2_data'] = v2_response.json()
                    logging.info(f"✅ V2 data: {v2_response.status_code}")
                else:
                    results['v2_data'] = None
                    logging.warning(f"⚠️ V2 data failed: {v2_response.status_code} | preview: {(v2_response.text or '')[:200]}")
            except Exception as e:
                results['v2_data'] = None
                logging.warning(f"⚠️ V2 data error: {e}")
            
            # Step 3: salespeople (last call browser makes)
            try:
                salespeople_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/salespeople"
                sales_params = {'_': int(time.time() * 1000)}
                salespeople_response = self.session.get(salespeople_url, headers=headers, params=sales_params, timeout=10)
                if salespeople_response.status_code == 200:
                    results['salespeople'] = salespeople_response.json()
                    logging.info(f"✅ Salespeople: {salespeople_response.status_code}")
                else:
                    results['salespeople'] = None
                    logging.warning(f"⚠️ Salespeople failed: {salespeople_response.status_code} | preview: {(salespeople_response.text or '')[:200]}")
            except Exception as e:
                results['salespeople'] = None
                logging.warning(f"⚠️ Salespeople error: {e}")

            # Step 4: agreementTotalValue (often used alongside others)
            try:
                total_value = self.get_agreement_total_value(agreement_id)
                results['agreement_total_value'] = total_value
                if total_value is not None:
                    logging.info("✅ agreementTotalValue retrieved")
                else:
                    logging.warning("⚠️ agreementTotalValue not available")
            except Exception as e:
                results['agreement_total_value'] = None
                logging.warning(f"⚠️ agreementTotalValue error: {e}")
            
            # Determine payment status and amount owed based on actual data
            payment_status = "Status Unknown"
            amount_owed = 0.0

            # 1) Prefer explicit billing status flags and amounts
            if results.get('billing_status') and isinstance(results['billing_status'], dict):
                billing_data = results['billing_status']
                # Extract numeric amount from common fields
                for key in ['pastDueAmount', 'amountPastDue', 'past_due_amount', 'balanceDue', 'balance', 'amount_due']:
                    val = billing_data.get(key)
                    try:
                        if isinstance(val, str):
                            # Strip currency symbols/commas
                            cleaned = re.sub(r"[^0-9.\-]", "", val)
                            val_num = float(cleaned) if cleaned else 0.0
                        elif isinstance(val, (int, float)):
                            val_num = float(val)
                        else:
                            val_num = 0.0
                        amount_owed = max(amount_owed, val_num)
                    except Exception:
                        continue

                if billing_data.get('isPastDue') is True or billing_data.get('pastDue') is True or amount_owed > 0:
                    payment_status = "Past Due"
                elif billing_data.get('isCurrent') is True or billing_data.get('current') is True:
                    payment_status = "Current"
                elif 'status' in billing_data and isinstance(billing_data['status'], str):
                    # Fallback to provided status string
                    payment_status = billing_data['status']

            # 2) If still unknown, inspect invoices in V2 payload for outstanding balances
            if payment_status == 'Status Unknown' and results.get('v2_data') and isinstance(results['v2_data'], dict):
                v2 = results['v2_data']
                invoices = v2.get('invoices') or v2.get('Invoices') or []
                if isinstance(invoices, list):
                    for inv in invoices:
                        if not isinstance(inv, dict):
                            continue
                        for k in ['outstandingBalance', 'remainingBalance', 'totalDue', 'amountDue']:
                            val = inv.get(k)
                            try:
                                if isinstance(val, str):
                                    cleaned = re.sub(r"[^0-9.\-]", "", val)
                                    val_num = float(cleaned) if cleaned else 0.0
                                elif isinstance(val, (int, float)):
                                    val_num = float(val)
                                else:
                                    val_num = 0.0
                                amount_owed = max(amount_owed, val_num)
                            except Exception:
                                continue
                    payment_status = 'Past Due' if amount_owed > 0 else 'Current'
            
            return {
                'success': True,
                'agreement_id': agreement_id,
                'payment_status': payment_status,
                'amount_owed': round(amount_owed, 2),
                'billing_status': results.get('billing_status'),
                'v2_data': results.get('v2_data'),
                'salespeople': results.get('salespeople'),
                'agreement_total_value': results.get('agreement_total_value'),
                'has_billing_data': results.get('billing_status') is not None,
                'has_v2_data': results.get('v2_data') is not None,
                'has_salespeople_data': results.get('salespeople') is not None,
                'has_total_value': results.get('agreement_total_value') is not None
            }
            
        except Exception as e:
            logging.error(f"❌ Error getting complete agreement data: {e}")
            return {"error": str(e), "success": False}

    def get_member_payment_status_v2(self, member_id: str | int) -> Optional[str]:
        """Robust payment status using delegated agreement APIs.

        Rules:
        - If any agreement shows Past Due in billing_status => 'Past Due'
        - Else if any agreement shows Current => 'Current'
        - Else None
        """
        try:
            mid = str(member_id).strip()
            if not self.authenticate():
                return None

            # 1) Prefer fast, reliable member-level billing status first
            mbs = self.get_member_billing_status(mid)
            if isinstance(mbs, dict):
                # Normalize possible fields
                status_str = str(mbs.get('status') or '').strip().lower()
                if mbs.get('isPastDue') is True or mbs.get('pastDue') is True or status_str == 'past due':
                    return 'Past Due'
                if mbs.get('isCurrent') is True or mbs.get('current') is True or status_str == 'current':
                    return 'Current'

            # 2) If member-level billing didn't answer, try agreement-level billing
            # Ensure delegated context
            self.delegate_to_member(mid)

            agreement_ids = self.discover_member_agreement_ids(mid)
            if not agreement_ids:
                return None

            found_current = False
            # Cap how many we probe to avoid timeouts/noise from bad IDs
            for aid in agreement_ids[:5]:
                data = self.get_complete_agreement_data(aid)
                if not isinstance(data, dict):
                    continue
                status = data.get('payment_status')
                if isinstance(status, str):
                    s = status.lower()
                    if 'past' in s:
                        return 'Past Due'
                    if 'current' in s:
                        found_current = True
            return 'Current' if found_current else None
        except Exception:
            return None

    def get_member_billing_status(self, member_id: str | int) -> Optional[dict]:
        """Call /api/billing/member/{memberId}/billing_status (observed in working scripts)."""
        try:
            mid = str(member_id).strip()
            if not self.authenticate():
                return None
            # Ensure delegation context
            self.delegate_to_member(mid)
            url = f"{self.base_url}/api/billing/member/{mid}/billing_status"
            headers = self._auth_headers(referer=f"{self.base_url}/action/Agreements")
            params = {'_': int(time.time() * 1000)}
            r = self.session.get(url, headers=headers, params=params, timeout=12)
            if r.status_code == 200:
                try:
                    return r.json()
                except Exception:
                    return None
            return None
        except Exception:
            return None

    def get_member_training_payment_details(self, member_id: str | int) -> dict:
        """Compute Current/Past Due and amount owed for a member's training agreements.

        Process:
        - Try member-level billing for quick decision and amount
        - Delegate and enumerate agreements; derive max amount owed across agreements
        - Return compact result with status and amount_owed
        """
        try:
            mid = str(member_id).strip()
            if not self.authenticate():
                return {'success': False, 'error': 'Authentication failed'}

            # Member-level first
            mbs = self.get_member_billing_status(mid) or {}
            amt = 0.0
            if isinstance(mbs, dict):
                for key in ['pastDueAmount', 'amountPastDue', 'past_due_amount', 'balanceDue', 'balance', 'amount_due']:
                    val = mbs.get(key)
                    try:
                        if isinstance(val, str):
                            cleaned = re.sub(r"[^0-9.\-]", "", val)
                            val_num = float(cleaned) if cleaned else 0.0
                        elif isinstance(val, (int, float)):
                            val_num = float(val)
                        else:
                            val_num = 0.0
                        amt = max(amt, val_num)
                    except Exception:
                        continue
                status = 'Past Due' if (mbs.get('isPastDue') is True or mbs.get('pastDue') is True or amt > 0) else (
                    'Current' if (mbs.get('isCurrent') is True or mbs.get('current') is True) else None)
                if status:
                    return {
                        'success': True,
                        'member_id': mid,
                        'status': status,
                        'amount_owed': round(amt, 2),
                        'source': 'member_billing'
                    }

            # Agreement-level
            self.delegate_to_member(mid)
            aids = self.discover_member_agreement_ids(mid)
            if not aids:
                # No agreements found; default to Current with zero due
                return {'success': True, 'member_id': mid, 'status': 'Current', 'amount_owed': 0.0, 'source': 'no_agreements'}

            max_due = 0.0
            any_past_due = False
            checked = 0
            for aid in aids:
                data = self.get_complete_agreement_data(aid)
                if isinstance(data, dict) and data.get('success'):
                    amt_a = float(data.get('amount_owed') or 0.0)
                    max_due = max(max_due, amt_a)
                    if data.get('payment_status') == 'Past Due' or amt_a > 0:
                        any_past_due = True
                checked += 1
                if checked >= 5:
                    break
            return {
                'success': True,
                'member_id': mid,
                'status': 'Past Due' if any_past_due else 'Current',
                'amount_owed': round(max_due, 2),
                'agreement_ids': aids[:checked],
                'source': 'agreement_level'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_complete_agreement_flow(self, member_id: str = "191215290") -> dict:
        """Test the complete browser-like flow for discovering and processing agreements."""
        try:
            logging.info(f"🧪 Testing complete agreement flow for member: {member_id}")
            
            # Get all package agreements using the browser-like approach
            agreements = self.get_member_package_agreements(member_id)
            
            return {
                'success': True,
                'member_id': member_id,
                'agreements_found': len(agreements),
                'agreements': agreements
            }
            
        except Exception as e:
            logging.error(f"❌ Error in complete agreement flow test: {e}")
            return {"error": str(e), "success": False}

    def test_known_agreement_id(self, agreement_id: str = "1616463") -> dict:
        """Test with a known working agreement ID from HAR files to validate our methods."""
        try:
            if not self.authenticate():
                return {"error": "Authentication failed"}
            
            logger.info(f"🧪 Testing known agreement ID: {agreement_id}")
            
            # Test the V2 endpoint that was successful in HAR files
            v2_url = f"{self.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
            headers = self._auth_headers(referer=f"{self.base_url}/action/Agreements")
            
            # Add query parameters from HAR
            params = {
                'include': 'invoices',
                '_': int(time.time() * 1000)
            }
            
            logger.info(f"🧪 Testing V2 endpoint: {v2_url}")
            v2_response = self.session.get(v2_url, headers=headers, params=params, timeout=15)
            
            v2_success = v2_response.status_code == 200
            v2_data = None
            if v2_success:
                try:
                    v2_data = v2_response.json()
                    logger.info(f"🧪 V2 endpoint SUCCESS: Got {len(str(v2_data))} chars of data")
                except:
                    v2_data = v2_response.text[:200]
                    logger.info(f"🧪 V2 endpoint SUCCESS: Got text response")
            else:
                logger.warning(f"⚠️ V2 endpoint failed: {v2_response.status_code}")
            
            # Test billing status endpoint  
            billing_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
            billing_response = self.session.get(billing_url, headers=headers, timeout=15)
            
            billing_success = billing_response.status_code == 200
            billing_data = None
            if billing_success:
                try:
                    billing_data = billing_response.json()
                    logger.info(f"🧪 Billing status SUCCESS: {billing_data}")
                except:
                    billing_data = billing_response.text[:200]
            else:
                logger.warning(f"⚠️ Billing status failed: {billing_response.status_code}")
            
            # Test salespeople endpoint
            salespeople_url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/salespeople"
            salespeople_response = self.session.get(salespeople_url, headers=headers, timeout=15)
            
            salespeople_success = salespeople_response.status_code == 200
            salespeople_data = None
            if salespeople_success:
                try:
                    salespeople_data = salespeople_response.json()
                    logger.info(f"🧪 Salespeople SUCCESS: {salespeople_data}")
                except:
                    salespeople_data = salespeople_response.text[:200]
            else:
                logger.warning(f"⚠️ Salespeople failed: {salespeople_response.status_code}")
            
            return {
                "agreement_id": agreement_id,
                "v2_data": v2_data,
                "v2_success": v2_success,
                "billing_data": billing_data,
                "billing_success": billing_success,
                "salespeople_data": salespeople_data,
                "salespeople_success": salespeople_success
            }
            
        except Exception as e:
            logger.error(f"❌ Error testing known agreement ID: {e}")
            return {"error": str(e)}

    def clone_clubos_browser_flow(self, member_id):
        """Clone the exact browser flow that ClubOS uses to view member agreements"""
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        logging.info(f"🎭 Cloning ClubOS browser flow for member: {member_id}")
        
        # Step 1: Navigate to main dashboard first (like a real browser)
        dashboard_url = "https://anytime.club-os.com/action/Dashboard"
        dashboard_response = self.session.get(dashboard_url)
        logging.info(f"🏠 Dashboard visit: {dashboard_response.status_code}")
        
        # Step 2: Navigate to members page (common workflow)
        members_url = "https://anytime.club-os.com/action/Members"
        members_response = self.session.get(members_url)
        logging.info(f"👥 Members page: {members_response.status_code}")
        
        # Step 3: Delegate to the specific member (critical step)
        delegation_success = self.delegate_to_member(member_id)
        if not delegation_success:
            return {"error": "Delegation failed"}
        
        # Step 4: Navigate to member's profile page first
        profile_url = f"https://anytime.club-os.com/action/Profile?memberId={member_id}"
        profile_response = self.session.get(profile_url)
        logging.info(f"👤 Profile page: {profile_response.status_code}")
        
        # Step 5: Try different approaches to access agreement data
        
        # Approach 1: Check ClubServices first (training packages are often here)
        clubservices_url = f"https://anytime.club-os.com/action/ClubServices?memberId={member_id}"
        clubservices_response = self.session.get(clubservices_url)
        logging.info(f"🎯 ClubServices page: {clubservices_response.status_code}")
        
        if clubservices_response.status_code == 200:
            clubservices_content = clubservices_response.text
            logging.info(f"📄 ClubServices HTML length: {len(clubservices_content)}")
            
            # Save ClubServices page
            clubservices_debug = f"debug_browser_flow_clubservices_{member_id}.html"
            with open(clubservices_debug, 'w', encoding='utf-8') as f:
                f.write(clubservices_content)
        
        # Approach 2: Navigate to agreements page from profile (natural flow)
        agreements_url = f"https://anytime.club-os.com/action/Agreements?memberId={member_id}"
        agreements_response = self.session.get(agreements_url)
        logging.info(f"📋 Agreements page: {agreements_response.status_code}")
        
        # Approach 3: Try agreements without memberId parameter (delegated context)
        agreements_delegated_url = "https://anytime.club-os.com/action/Agreements"
        agreements_delegated_response = self.session.get(agreements_delegated_url)
        logging.info(f"📋 Agreements (delegated): {agreements_delegated_response.status_code}")
        
        if agreements_delegated_response.status_code == 200:
            delegated_content = agreements_delegated_response.text
            logging.info(f"📄 Delegated agreements HTML length: {len(delegated_content)}")
            
            # Save delegated agreements page
            delegated_debug = f"debug_browser_flow_agreements_delegated_{member_id}.html"
            with open(delegated_debug, 'w', encoding='utf-8') as f:
                f.write(delegated_content)
        
        # Step 6: Parse the HTML to find agreement data (like browser would)
        if agreements_response.status_code == 200:
            html_content = agreements_response.text
            logging.info(f"📄 Agreements HTML length: {len(html_content)}")
            
            # Save for debugging
            debug_file = f"debug_browser_flow_agreements_{member_id}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"💾 Saved agreements HTML to {debug_file}")
            
            # Look for agreement tables, forms, and data
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all tables (agreements are usually in tables)
            tables = soup.find_all('table')
            logging.info(f"🔍 Found {len(tables)} tables in agreements page")
            
            # Find all forms (might contain agreement actions)
            forms = soup.find_all('form')
            logging.info(f"🔍 Found {len(forms)} forms in agreements page")
            
            # Look for specific agreement-related elements
            agreement_links = soup.find_all('a', href=lambda x: x and 'agreement' in x.lower())
            logging.info(f"🔍 Found {len(agreement_links)} agreement links")
            
            # Look for any element with agreement ID patterns
            agreement_elements = soup.find_all(text=re.compile(r'\b\d{6,}\b'))  # 6+ digit numbers
            logging.info(f"🔍 Found {len(agreement_elements)} potential agreement ID elements")
            
            return {
                "success": True,
                "html_length": len(html_content),
                "tables_found": len(tables),
                "forms_found": len(forms),
                "agreement_links_found": len(agreement_links),
                "potential_agreement_ids": len(agreement_elements),
                "debug_file": debug_file
            }
        else:
            return {
                "error": "Failed to access agreements page",
                "status_code": agreements_response.status_code,
                "response_text": agreements_response.text[:500]
            }

    def discover_member_agreement_ids(self, member_id: str | int) -> list[str]:
        """Discover agreement IDs using the proper API endpoint from HAR files.
        
        Uses /api/agreements/package_agreements/list endpoint which is the correct way
        based on the actual ClubOS API flow documented in the HAR files.
        """
        try:
            mid = str(member_id).strip()
            
            # First ensure we're delegated to this member
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to member {mid}")
                return []
            
            # Use the proper API endpoint from HAR files
            # Important: pass memberId and use AJAX-style headers with an Agreements referer
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/list"
            params = {
                '_': timestamp,
                'memberId': mid,
            }
            headers = self._auth_headers(referer=f"{self.base_url}/action/Agreements?memberId={mid}")
            # Override Accept for this AJAX JSON endpoint to match browser behavior more closely
            headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            
            logger.info(f"🔍 Fetching package agreements list for member {mid}")
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code != 200:
                body_preview = (response.text or '')[:300]
                delegated_cookie = self.session.cookies.get_dict().get('delegatedUserId')
                has_bearer = 'Authorization' in headers
                logger.warning(
                    f"⚠️ Package agreements list API failed: {response.status_code} | delegatedUserId set: {bool(delegated_cookie)} | bearer header: {has_bearer} | preview: {body_preview}"
                )
                # Try HTML-based fallbacks if API fails
                fallback_ids: list[str] = []
                try:
                    # Agreements page (delegated)
                    agreements_url = f"{self.base_url}/action/Agreements?memberId={mid}"
                    r1 = self.session.get(agreements_url, timeout=12)
                    if r1.status_code == 200:
                        # Look for explicit agreementId assignments/attributes
                        m = []
                        html = r1.text
                        m += re.findall(r"agreement(?:Id|ID)\s*[:=]\s*['\"]?(\d{5,9})", html)
                        m += re.findall(r"/api/agreements/package_agreements/(?:V2/)?(\d{5,9})", html)
                        m += re.findall(r"/action/Agreement[^\d]*(\d{5,9})", html)
                        # data-agreement-id attributes and hidden inputs
                        m += re.findall(r"data-agreement-id=['\"](\d{5,9})['\"]", html)
                        m += re.findall(r"<input[^>]*name=['\"]agreementId['\"][^>]*value=['\"](\d{5,9})['\"]", html, flags=re.I)
                        fallback_ids.extend(m)
                    # Agreements page without memberId (delegated context)
                    agreements_no_mid = f"{self.base_url}/action/Agreements"
                    r1b = self.session.get(agreements_no_mid, timeout=12)
                    if r1b.status_code == 200:
                        htmlb = r1b.text
                        m = []
                        m += re.findall(r"agreement(?:Id|ID)\s*[:=]\s*['\"]?(\d{5,9})", htmlb)
                        m += re.findall(r"/api/agreements/package_agreements/(?:V2/)?(\d{5,9})", htmlb)
                        m += re.findall(r"/action/Agreement[^\d]*(\d{5,9})", htmlb)
                        m += re.findall(r"data-agreement-id=['\"](\d{5,9})['\"]", htmlb)
                        m += re.findall(r"<input[^>]*name=['\"]agreementId['\"][^>]*value=['\"](\d{5,9})['\"]", htmlb, flags=re.I)
                        fallback_ids.extend(m)
                    # ClubServices page
                    services_url = f"{self.base_url}/action/ClubServices?memberId={mid}"
                    r2 = self.session.get(services_url, timeout=12)
                    if r2.status_code == 200:
                        html2 = r2.text
                        m2 = []
                        m2 += re.findall(r"agreement(?:Id|ID)\s*[:=]\s*['\"]?(\d{5,9})", html2)
                        m2 += re.findall(r"/api/agreements/package_agreements/(?:V2/)?(\d{5,9})", html2)
                        m2 += re.findall(r"/action/Agreement[^\d]*(\d{5,9})", html2)
                        m2 += re.findall(r"data-agreement-id=['\"](\d{5,9})['\"]", html2)
                        m2 += re.findall(r"<input[^>]*name=['\"]agreementId['\"][^>]*value=['\"](\d{5,9})['\"]", html2, flags=re.I)
                        fallback_ids.extend(m2)
                    # ClubServicesNew page
                    services_new_url = f"{self.base_url}/action/ClubServicesNew?memberId={mid}"
                    r3 = self.session.get(services_new_url, timeout=12)
                    if r3.status_code == 200:
                        html3 = r3.text
                        m3 = []
                        m3 += re.findall(r"agreement(?:Id|ID)\s*[:=]\s*['\"]?(\d{5,9})", html3)
                        m3 += re.findall(r"/api/agreements/package_agreements/(?:V2/)?(\d{5,9})", html3)
                        m3 += re.findall(r"/action/Agreement[^\d]*(\d{5,9})", html3)
                        m3 += re.findall(r"data-agreement-id=['\"](\d{5,9})['\"]", html3)
                        m3 += re.findall(r"<input[^>]*name=['\"]agreementId['\"][^>]*value=['\"](\d{5,9})['\"]", html3, flags=re.I)
                        fallback_ids.extend(m3)
                except Exception:
                    pass
                # Validate: numeric, reasonable length (5-9 digits), not obvious timestamps or the memberId itself
                mid_num = re.sub(r"\D", "", mid)
                def _valid_aid(x: str) -> bool:
                    return x.isdigit() and 5 <= len(x) <= 9 and x != mid_num

                valid_fb = sorted({x for x in fallback_ids if _valid_aid(x)})
                if valid_fb:
                    logger.info(f"✅ Discovered {len(valid_fb)} fallback agreement IDs for member {mid}: {valid_fb}")
                    return valid_fb
                return []
            
            try:
                data = response.json()
                logger.info(f"� Package agreements list response type: {type(data)}")
                
                agreement_ids = []
                
                if isinstance(data, list):
                    # Direct list of agreements
                    for agreement in data:
                        if isinstance(agreement, dict):
                            aid = agreement.get('agreementId') or agreement.get('id')
                            # Don't over-filter here; collect first, filter later
                            if aid:
                                agreement_ids.append(str(aid))
                                
                elif isinstance(data, dict):
                    # Check for various wrapper formats
                    agreements_list = (data.get('agreements') or 
                                     data.get('packageAgreements') or 
                                     data.get('data') or 
                                     [])
                    
                    if isinstance(agreements_list, list):
                        for agreement in agreements_list:
                            if isinstance(agreement, dict):
                                aid = agreement.get('agreementId') or agreement.get('id')
                                if aid:
                                    agreement_ids.append(str(aid))
                
                # Dedup + light validation
                # Validate: numeric, reasonable length (5-9 digits), not the memberId
                mid_num = re.sub(r"\D", "", mid)
                agreement_ids = sorted({x for x in agreement_ids if x.isdigit() and 5 <= len(x) <= 9 and x != mid_num})
                logger.info(f"✅ Discovered {len(agreement_ids)} agreement IDs for member {mid}: {agreement_ids}")
                return agreement_ids
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Failed to parse JSON from package agreements list: {e}")
                logger.info(f"🔍 Raw response: {response.text[:500]}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Error discovering agreement IDs for member {member_id}: {e}")
            return []

    def get_agreement_total_value(self, agreement_id: str) -> Optional[dict]:
        """Get agreement total value using the specific HAR file endpoint pattern."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/agreementTotalValue"
            params = {'agreementId': agreement_id, '_': timestamp}
            headers = self._auth_headers(referer=f"{self.base_url}/action/ClubServicesNew")
            
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✅ Got agreement total value for {agreement_id}")
                    return data
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Non-JSON response from agreement total value API")
                    return None
            else:
                logger.warning(f"⚠️ Agreement total value API failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting agreement total value: {e}")
            return None

    def get_agreement_salespeople(self, agreement_id: str) -> Optional[dict]:
        """Get agreement salespeople using the specific HAR file endpoint pattern."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/salespeople"
            params = {'_': timestamp}
            headers = self._auth_headers(referer=f"{self.base_url}/action/ClubServicesNew")
            
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"✅ Got agreement salespeople for {agreement_id}")
                    return data
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Non-JSON response from agreement salespeople API")
                    return None
            else:
                logger.warning(f"⚠️ Agreement salespeople API failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting agreement salespeople: {e}")
            return None

    def get_member_package_agreements(self, member_id: str | int) -> list[dict]:
        """Fetch active training package agreements for a member using browser-like approach.
        
        This implementation:
        1. Delegates to the member context  
        2. Discovers agreement IDs dynamically
        3. Makes all API calls like a browser would
        4. Returns complete agreement data
        """
        try:
            mid = str(member_id).strip()
            logging.info(f"🏋️ Getting package agreements for member: {mid}")
            
            if not self.authenticate():
                logging.error("❌ ClubOS authentication failed for package agreements")
                return []
            
            # Step 1: Delegate to member context
            if not self.delegate_to_member(mid):
                logging.warning(f"⚠️ Delegation failed for member {mid}")
                return []
            
            # Step 2: Discover agreement IDs for this member
            agreement_ids = self.discover_member_agreement_ids(mid)
            if not agreement_ids:
                logging.info(f"ℹ️ No agreement IDs found for member {mid}")
                return []
            
            logging.info(f"📋 Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            # Step 3: Get complete data for each agreement (like browser does)
            agreements = []
            for agreement_id in agreement_ids:
                logging.info(f"🔍 Processing agreement {agreement_id}")
                agreement_data = self.get_complete_agreement_data(agreement_id)
                
                if agreement_data.get('success'):
                    agreements.append(agreement_data)
                    logging.info(f"✅ Successfully processed agreement {agreement_id}")
                else:
                    logging.warning(f"⚠️ Failed to process agreement {agreement_id}: {agreement_data.get('error', 'Unknown error')}")
            
            logging.info(f"✅ Processed {len(agreements)} agreements for member {mid}")
            return agreements
            
        except Exception as e:
            logging.error(f"❌ Error getting member package agreements: {e}")
            return []
            logger.info(f"🏋️ Getting package agreements for member: {mid}")

            # Step 1: Delegate to this member context 
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to {mid}; trying to continue anyway")

            # Step 2: Discover agreement IDs for this member
            agreement_ids = self.discover_member_agreement_ids(mid)
            
            if not agreement_ids:
                logger.info(f"ℹ️ No agreement IDs found for member {mid}")
                return []

            # Step 3: Get details for each agreement and filter for active training packages
            normalized_agreements = []
            
            for agreement_id in agreement_ids:
                try:
                    # Get agreement total value
                    total_value_data = self.get_agreement_total_value(agreement_id)
                    
                    # Skip if we can't get agreement data
                    if not total_value_data or not isinstance(total_value_data, dict):
                        logger.info(f"⏭️ Skipping agreement {agreement_id}: No total value data")
                        continue
                    
                    # Filter 1: Only include agreements with "Active" status
                    agreement_status = str(total_value_data.get('status', '')).lower()
                    if agreement_status not in ['active', 'current']:
                        logger.info(f"⏭️ Skipping agreement {agreement_id}: Status '{agreement_status}' is not active")
                        continue
                    
                    # Filter 2: Only include training packages (check package name)
                    package_name = str(total_value_data.get('packageName') or total_value_data.get('name') or '')
                    if not package_name or 'training' not in package_name.lower():
                        logger.info(f"⏭️ Skipping agreement {agreement_id}: Package name '{package_name}' is not a training package")
                        continue
                    
                    # Filter 3: Check for reasonable amount (training packages should have a cost)
                    amount = total_value_data.get('totalValue') or total_value_data.get('amount') or 0
                    if not amount or amount <= 0:
                        logger.info(f"⏭️ Skipping agreement {agreement_id}: No valid amount ({amount})")
                        continue
                    
                    # Get agreement salespeople
                    salespeople_data = self.get_agreement_salespeople(agreement_id)
                    
                    # Combine the data into our standard format
                    agreement_info = {
                        'agreement_id': agreement_id,
                        'package_name': package_name,
                        'trainer_name': 'Jeremy Mayo',  # Default trainer
                        'status': 'Active',
                        'sessions_remaining': total_value_data.get('sessionsRemaining') or 0,
                        'next_session_date': '',
                        'amount': amount,
                        'created_date': total_value_data.get('startDate') or total_value_data.get('createdDate') or '',
                        'total_value_data': total_value_data,
                        'salespeople_data': salespeople_data
                    }
                    
                    # Extract trainer info from salespeople data
                    if salespeople_data and isinstance(salespeople_data, dict):
                        if 'salespeople' in salespeople_data and isinstance(salespeople_data['salespeople'], list):
                            if salespeople_data['salespeople']:
                                first_salesperson = salespeople_data['salespeople'][0]
                                if isinstance(first_salesperson, dict):
                                    trainer_name = first_salesperson.get('name') or first_salesperson.get('firstName', '') + ' ' + first_salesperson.get('lastName', '')
                                    if trainer_name.strip():
                                        agreement_info['trainer_name'] = trainer_name.strip()
                    
                    normalized_agreements.append(agreement_info)
                    logger.info(f"✅ Added ACTIVE training package {agreement_id}: {package_name} - ${amount}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                    continue

            logger.info(f"✅ Found {len(normalized_agreements)} ACTIVE training package agreements for member {mid}")
            return normalized_agreements
            
        except Exception as e:
            logger.error(f"❌ Error fetching package agreements for member {member_id}: {e}")
            return []

    def get_member_agreements(self, member_id: str | int) -> list[dict]:
        """Get all agreements for a member using the reliable agreement endpoints."""
        try:
            mid = str(member_id).strip()
            if not self.authenticate():
                logger.error("❌ ClubOS authentication failed for member agreements")
                return []

            logger.info(f"🔍 Getting agreements for member: {mid}")
            
            # Ensure delegated context
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to member {mid}")
                return []

            # Discover agreement IDs for this member
            agreement_ids = self.discover_member_agreement_ids(mid)
            if not agreement_ids:
                logger.info(f"ℹ️ No agreement IDs found for member {mid}")
                return []

            logger.info(f"📋 Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            # Get complete data for each agreement
            agreements = []
            for agreement_id in agreement_ids:
                try:
                    logger.info(f"🔍 Processing agreement {agreement_id}")
                    agreement_data = self.get_complete_agreement_data(agreement_id)
                    
                    if agreement_data.get('success'):
                        # Extract key financial data
                        past_due = 0.0
                        if agreement_data.get('billing_status') and isinstance(agreement_data['billing_status'], dict):
                            billing = agreement_data['billing_status']
                            # Look for past due amount in various possible fields
                            for key in ['pastDueAmount', 'amountPastDue', 'past_due_amount', 'balanceDue', 'balance', 'amount_due']:
                                val = billing.get(key)
                                if val:
                                    try:
                                        if isinstance(val, str):
                                            val = re.sub(r'[^\d.-]', '', val)
                                        past_due = max(past_due, float(val) if val else 0.0)
                                    except (ValueError, TypeError):
                                        continue
                        
                        # Create standardized agreement object
                        agreement = {
                            'id': agreement_id,
                            'pastDueAmount': past_due,
                            'status': agreement_data.get('payment_status', 'Unknown'),
                            'type': 'Training Package',  # Default type
                            'totalValue': 0.0,  # Will be populated if available
                            'startDate': None,
                            'endDate': None
                        }
                        
                        # Add additional data if available
                        if agreement_data.get('v2_data') and isinstance(agreement_data['v2_data'], dict):
                            v2 = agreement_data['v2_data']
                            agreement['totalValue'] = v2.get('totalValue') or v2.get('amount') or 0.0
                            agreement['startDate'] = v2.get('startDate') or v2.get('createdDate')
                            agreement['endDate'] = v2.get('endDate') or v2.get('expirationDate')
                        
                        agreements.append(agreement)
                        logger.info(f"✅ Successfully processed agreement {agreement_id} - Past Due: ${past_due:.2f}")
                        
                    else:
                        logger.warning(f"⚠️ Failed to process agreement {agreement_id}: {agreement_data.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                    continue

            logger.info(f"✅ Processed {len(agreements)} agreements for member {mid}")
            return agreements
            
        except Exception as e:
            logger.error(f"❌ Error getting member agreements for {member_id}: {e}")
            return []


if __name__ == "__main__":
    api = ClubOSTrainingPackageAPI()
    ok = api.authenticate()
    print(f"auth: {ok}")
    
    if ok:
        # Test with known member IDs from your description
        test_members = [
            ('185182950', 'Javae Dixon'),
            ('185777276', 'Grace Sphatt'),
        ]
        
        for member_id, member_name in test_members:
            print(f"\n=== Testing {member_name} (ID: {member_id}) ===")
            try:
                agreements = api.get_member_package_agreements(member_id)
                print(f"Found {len(agreements)} agreements:")
                for i, agreement in enumerate(agreements, 1):
                    print(f"  {i}. {agreement['package_name']} - {agreement['trainer_name']} - ${agreement['amount']}")
            except Exception as e:
                print(f"Error: {e}")
