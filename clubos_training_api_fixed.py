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
            if self.authenticated:
                return True
            if not self.username or not self.password:
                logger.warning("ClubOS credentials missing; cannot authenticate.")
                return False

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

            # Step 2: POST credentials to /action/Login
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
            r1 = self.session.post(f"{self.base_url}/action/Login", data=form, headers=headers, timeout=30, allow_redirects=True)
            if r1.status_code not in (200, 302):
                logger.error(f"Login POST failed: {r1.status_code}")
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
            logger.info("ClubOS Training API: authenticated via /action/Login")
            return True
        except Exception as e:
            logger.error(f"authenticate error: {e}")
            return False

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

    def fetch_assignees(self, force_refresh: bool = False) -> list[dict]:
        """Parse /action/Assignees to build a minimal list of members with IDs."""
        try:
            now = time.time()
            if not force_refresh and self._assignees_cache and (now - self._assignees_fetched_at) < 900:
                return self._assignees_cache

            if not self.authenticated and not self.authenticate():
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
                return []

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
                        return []
                else:
                    logger.warning(f"⚠️ AJAX endpoint returned unexpected data type: {type(data)}")
            except Exception as json_error:
                logger.warning(f"⚠️ Failed to parse JSON from AJAX endpoint: {json_error}")
                # Fall back to HTML parsing
                pass

            # Fallback: parse as HTML (ClubOS assignees page structure)
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
                logger.info(f"✅ Found {len(result)} training clients from HTML parsing")
                self._assignees_cache = result
                self._assignees_index = None
                self._assignees_fetched_at = time.time()
                return result
            else:
                logger.warning("⚠️ No training clients found in HTML")
                return []
        except Exception as e:
            logger.warning(f"fetch_assignees error: {e}")
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
            
            # Use the exact delegation pattern from working HAR files
            url = f"{self.base_url}/action/Delegate/{mid}/url=false"
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': f'{self.base_url}/action/Assignees',
            }
            
            logger.info(f"🔑 Delegating to member ID: {mid}")
            response = self.session.get(url, headers=headers, timeout=15)
            
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

    def discover_member_agreement_ids(self, member_id: str | int) -> list[str]:
        """Discover agreement IDs for a member by checking multiple ClubOS pages.
        
        Avoids the broken /list endpoint and finds agreement IDs from:
        1. Member profile pages with agreement references
        2. ClubServices pages that show agreements
        3. JavaScript/AJAX calls with agreement data
        """
        try:
            mid = str(member_id).strip()
            agreement_ids = []
            
            # First ensure we're delegated to this member
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to member {mid}")
            
            # Strategy 1: Check ClubServices page for agreement dropdowns/data
            try:
                services_url = f"{self.base_url}/action/ClubServicesNew"
                headers = {
                    'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Referer': f'{self.base_url}/action/Dashboard',
                }
                
                response = self.session.get(services_url, headers=headers, timeout=20)
                if response.status_code == 200:
                    # Look for agreement IDs in JavaScript variables or data attributes
                    html = response.text
                    
                    # Pattern 1: agreement IDs in JavaScript variables
                    js_matches = re.findall(r'agreementId["\']?\s*[:=]\s*["\']?(\d+)["\']?', html, re.IGNORECASE)
                    agreement_ids.extend(js_matches)
                    
                    # Pattern 2: agreement IDs in data attributes or option values
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Look for select options with agreement values
                    for select in soup.find_all('select'):
                        for option in select.find_all('option'):
                            value = option.get('value', '')
                            if value.isdigit() and len(value) >= 6:  # Agreement IDs are typically long numbers
                                agreement_ids.append(value)
                    
                    # Look for data attributes with agreement IDs
                    for elem in soup.find_all(attrs={'data-agreement-id': True}):
                        agreement_ids.append(elem['data-agreement-id'])
                    
                    # Look for links or forms with agreement parameters
                    for elem in soup.find_all(['a', 'form']):
                        href_or_action = elem.get('href') or elem.get('action', '')
                        agreement_match = re.search(r'agreementId=(\d+)', href_or_action)
                        if agreement_match:
                            agreement_ids.append(agreement_match.group(1))
                    
                    logger.info(f"📋 Found {len(agreement_ids)} potential agreement IDs from ClubServices")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error checking ClubServices page: {e}")
            
            # Strategy 2: Check member agreements page
            try:
                agreements_url = f"{self.base_url}/action/Agreements?memberId={mid}"
                response = self.session.get(agreements_url, headers=headers, timeout=20)
                if response.status_code == 200:
                    html = response.text
                    
                    # Look for agreement IDs in the agreements page
                    agreement_matches = re.findall(r'agreement[_-]?id["\']?\s*[:=]\s*["\']?(\d+)["\']?', html, re.IGNORECASE)
                    agreement_ids.extend(agreement_matches)
                    
                    # Look for package agreement references
                    package_matches = re.findall(r'package[_-]?agreement[_-]?id["\']?\s*[:=]\s*["\']?(\d+)["\']?', html, re.IGNORECASE)
                    agreement_ids.extend(package_matches)
                    
                    logger.info(f"📋 Found {len(agreement_matches + package_matches)} agreement IDs from agreements page")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error checking agreements page: {e}")
            
            # Strategy 3: Try AJAX endpoints that might return agreement data
            try:
                # Check if there are any AJAX endpoints that return agreement lists
                timestamp = int(time.time() * 1000)
                ajax_endpoints = [
                    f"{self.base_url}/action/ClubServicesNew/getAgreements?memberId={mid}&_={timestamp}",
                    f"{self.base_url}/api/members/{mid}/agreements?_={timestamp}",
                    f"{self.base_url}/action/Agreements/list?memberId={mid}&_={timestamp}",
                ]
                
                bearer_headers = self._auth_headers(referer=f"{self.base_url}/action/ClubServicesNew")
                
                for ajax_url in ajax_endpoints:
                    try:
                        ajax_response = self.session.get(ajax_url, headers=bearer_headers, timeout=10)
                        if ajax_response.status_code == 200:
                            try:
                                data = ajax_response.json()
                                if isinstance(data, list):
                                    for item in data:
                                        if isinstance(item, dict):
                                            item_id = item.get('id') or item.get('agreementId') or item.get('agreement_id')
                                            if item_id:
                                                agreement_ids.append(str(item_id))
                                elif isinstance(data, dict):
                                    # Single agreement or wrapped response
                                    item_id = data.get('id') or data.get('agreementId') or data.get('agreement_id')
                                    if item_id:
                                        agreement_ids.append(str(item_id))
                                        
                                logger.info(f"📋 Found agreement data from AJAX endpoint: {ajax_url}")
                                break  # Stop trying other endpoints if one works
                                        
                            except json.JSONDecodeError:
                                # Not JSON, might be HTML with agreement IDs
                                ajax_html = ajax_response.text
                                ajax_matches = re.findall(r'(\d{6,})', ajax_html)  # Look for long numbers
                                agreement_ids.extend([m for m in ajax_matches if len(m) >= 6])
                                
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.warning(f"⚠️ Error checking AJAX endpoints: {e}")
            
            # Deduplicate and validate agreement IDs
            unique_ids = list(set(agreement_ids))
            valid_ids = [aid for aid in unique_ids if aid.isdigit() and len(aid) >= 6]
            
            logger.info(f"✅ Discovered {len(valid_ids)} unique agreement IDs for member {mid}: {valid_ids}")
            return valid_ids
            
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
        """Fetch active training package agreements for a member using HAR-based approach.
        
        This implementation:
        1. Delegates to the member context
        2. Discovers agreement IDs for that member
        3. Uses the specific HAR endpoints to get agreement details
        4. Combines the data into a unified response
        """
        try:
            # Ensure logged in
            if not self.authenticate():
                logger.error("❌ ClubOS authentication failed for package agreements")
                return []

            mid = str(member_id).strip()
            logger.info(f"🏋️ Getting package agreements for member: {mid}")

            # Step 1: Delegate to this member context 
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to {mid}; trying to continue anyway")

            # Step 2: Discover agreement IDs for this member
            agreement_ids = self.discover_member_agreement_ids(mid)
            
            if not agreement_ids:
                logger.info(f"ℹ️ No agreement IDs found for member {mid}")
                return []

            # Step 3: Get details for each agreement using HAR endpoints
            normalized_agreements = []
            
            for agreement_id in agreement_ids:
                try:
                    # Get agreement total value
                    total_value_data = self.get_agreement_total_value(agreement_id)
                    
                    # Get agreement salespeople
                    salespeople_data = self.get_agreement_salespeople(agreement_id)
                    
                    # Combine the data into our standard format
                    agreement_info = {
                        'agreement_id': agreement_id,
                        'package_name': 'Training Package',  # Default, may be overridden
                        'trainer_name': 'Jeremy Mayo',  # Default trainer
                        'status': 'Active',  # Default status
                        'sessions_remaining': 0,
                        'next_session_date': '',
                        'amount': 0,
                        'created_date': '',
                        'total_value_data': total_value_data,
                        'salespeople_data': salespeople_data
                    }
                    
                    # Extract details from total value data
                    if total_value_data and isinstance(total_value_data, dict):
                        agreement_info['amount'] = total_value_data.get('totalValue') or total_value_data.get('amount') or 0
                        agreement_info['package_name'] = total_value_data.get('packageName') or total_value_data.get('name') or 'Training Package'
                        agreement_info['sessions_remaining'] = total_value_data.get('sessionsRemaining') or 0
                        agreement_info['status'] = total_value_data.get('status') or 'Active'
                    
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
                    logger.info(f"✅ Processed agreement {agreement_id}: {agreement_info['package_name']}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing agreement {agreement_id}: {e}")
                    continue

            logger.info(f"✅ Found {len(normalized_agreements)} package agreements for member {mid}")
            return normalized_agreements
            
        except Exception as e:
            logger.error(f"❌ Error fetching package agreements for member {member_id}: {e}")
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
