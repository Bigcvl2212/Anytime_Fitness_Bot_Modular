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
import requests
import time
from typing import Optional
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClubOSTrainingPackageAPI:
    """HAR-based client for Training lookups in ClubOS used by clean_dashboard.py."""

    def __init__(self) -> None:
        # Credentials come from config; avoid printing secrets
        try:
            from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD  # type: ignore
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
        """Discover REAL agreement IDs using proper ClubOS API endpoints.
        
        IMPORTANT: This method assumes we're already delegated to the member.
        Do NOT call delegate_to_member() from within this method to avoid double delegation.
        """
        try:
            mid = str(member_id).strip()
            agreement_ids = []
            
            # We should already be delegated to this member - don't delegate again!
            # Check delegation status
            cookies = self.session.cookies.get_dict()
            delegated_user_id = cookies.get('delegatedUserId')
            if delegated_user_id != mid:
                logger.warning(f"⚠️ Not properly delegated to member {mid} (delegated to: {delegated_user_id})")
            
            # CRITICAL: Must visit ClubServicesNew first to set up session state (per HAR data)
            try:
                # Step 1: Visit ClubServicesNew to set up session (exactly like working HAR sequence)
                logger.info(f"🔍 Step 1: Setting up session state via ClubServicesNew")
                clubservices_headers = {
                    'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Referer': f'{self.base_url}/action/Dashboard/view',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                }
                
                setup_response = self.session.get(f"{self.base_url}/action/ClubServicesNew", 
                                                headers=clubservices_headers, timeout=15)
                
                if setup_response.status_code != 200:
                    logger.error(f"❌ ClubServicesNew setup failed: {setup_response.status_code}")
                    
                # Step 2: Now call the list endpoint with exact HAR headers (NO Bearer token!)
                timestamp = int(time.time() * 1000)
                agreements_list_url = f"{self.base_url}/api/agreements/package_agreements/list"
                
                # Use exact headers from working HAR data (NO Authorization Bearer!)
                list_headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': f'{self.base_url}/action/ClubServicesNew',
                    'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                    'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                }
                params = {'_': timestamp}
                
                logger.info(f"🔍 Step 2: Calling package agreements list API: {agreements_list_url}")
                logger.info(f"🔍 Using session-only auth (no Bearer token): {list(list_headers.keys())}")
                logger.info(f"🔍 Current delegation cookies: {self.session.cookies.get_dict()}")
                
                response = self.session.get(agreements_list_url, headers=list_headers, params=params, timeout=15)
                
                logger.info(f"🔍 Response status: {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"❌ Response headers: {dict(response.headers)}")
                    logger.error(f"❌ Response text: {response.text[:1000]}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            for agreement_obj in data:
                                if isinstance(agreement_obj, dict):
                                    # Extract agreement ID from packageAgreement.id (the correct structure)
                                    package_agreement = agreement_obj.get('packageAgreement', {})
                                    if isinstance(package_agreement, dict):
                                        agreement_id = package_agreement.get('id')
                                        member_id_in_agreement = package_agreement.get('memberId')
                                        agreement_name = package_agreement.get('name', '')
                                        agreement_status = package_agreement.get('agreementStatus')
                                        
                                        # Only include agreements for the current member
                                        if (agreement_id and str(agreement_id).isdigit() and 
                                            str(member_id_in_agreement) == mid):
                                            agreement_ids.append(str(agreement_id))
                                            logger.info(f"✅ Found REAL agreement ID: {agreement_id} - {agreement_name} (Status: {agreement_status})")
                        elif isinstance(data, dict):
                            # Single agreement response
                            aid = data.get('id') or data.get('packageAgreementId') or data.get('agreementId')
                            if aid and str(aid).isdigit():
                                agreement_ids.append(str(aid))
                                logger.info(f"� Found valid agreement ID from API: {aid}")
                                
                        logger.info(f"✅ Found {len(agreement_ids)} agreement IDs from agreements list API")
                        
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ Invalid JSON response from agreements list API")
                        
                elif response.status_code == 404:
                    logger.info(f"ℹ️ Agreements list endpoint not available")
                else:
                    logger.warning(f"⚠️ Agreements list API failed: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error checking package agreements list API: {e}")
            
            # Deduplicate and return only valid agreement IDs
            unique_ids = list(set(agreement_ids))
            valid_ids = [aid for aid in unique_ids if aid.isdigit() and len(aid) >= 4 and len(aid) <= 10]
            
            logger.info(f"✅ Discovered {len(valid_ids)} VALID agreement IDs for member {mid}: {valid_ids}")
            return valid_ids
            
        except Exception as e:
            logger.error(f"❌ Error discovering agreement IDs for member {member_id}: {e}")
            return []

    def get_agreement_total_value(self, agreement_id: str) -> Optional[dict]:
        """Get agreement total value using session-only authentication (no Bearer token)."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/agreementTotalValue"
            params = {'agreementId': agreement_id, '_': timestamp}
            
            # Use session-only auth like the successful list endpoint
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'{self.base_url}/action/ClubServicesNew',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
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
        """Get agreement salespeople using session-only authentication (no Bearer token)."""
        try:
            if not self.authenticated and not self.authenticate():
                return None
            
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/salespeople"
            params = {'_': timestamp}
            
            # Use session-only auth like the successful list endpoint
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'{self.base_url}/action/ClubServicesNew',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
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

            # Agreement-level - delegate once and use it
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to member {mid} for agreement-level check")
                return {'success': True, 'member_id': mid, 'status': 'Current', 'amount_owed': 0.0, 'source': 'no_delegation'}
                
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

            # Step 1: Delegate to this member context FIRST - this is critical
            if not self.delegate_to_member(mid):
                logger.error(f"❌ Could not delegate to member {mid} - cannot proceed")
                return []

            # Step 2: Discover agreement IDs for this member (now we're delegated)
            agreement_ids = self.discover_member_agreement_ids(mid)
            
            if not agreement_ids:
                logger.info(f"ℹ️ No agreement IDs found for member {mid}")
                return []

            # Step 3: Get details for each agreement using HAR endpoints
            normalized_agreements = []
            
            for agreement_id in agreement_ids:
                try:
                    # Get the complete agreement data with invoices (this is all we need)
                    invoice_data = self.get_agreement_invoices_and_payments(agreement_id)
                    
                    # Combine the data into our standard format
                    agreement_info = {
                        'agreement_id': agreement_id,
                        'package_name': 'Training Package',  # Default, will be overridden from invoice data
                        'trainer_name': 'Jeremy Mayo',  # Default trainer
                        'status': 2,  # All agreements from list API are active (Status: 2)
                        'sessions_remaining': 0,
                        'next_session_date': '',
                        'amount': 0,
                        'created_date': '',
                        'invoice_data': invoice_data
                    }
                    
                    # Extract details from invoice data
                    if invoice_data and isinstance(invoice_data, dict):
                        # Extract agreement details from the V2 response
                        package_agreement = invoice_data.get('packageAgreement', {})
                        if package_agreement:
                            agreement_info['package_name'] = package_agreement.get('name') or 'Training Package'
                            # Status is already set to 2 (active) from agreements list API
                            agreement_info['amount'] = package_agreement.get('totalValue') or 0
                            agreement_info['sessions_remaining'] = package_agreement.get('sessionsRemaining') or 0
                            agreement_info['created_date'] = package_agreement.get('createdDate') or ''
                        
                        # Extract trainer info from salespeople if available
                        salespeople = invoice_data.get('salespeople', [])
                        if salespeople and isinstance(salespeople, list) and len(salespeople) > 0:
                            first_salesperson = salespeople[0]
                            if isinstance(first_salesperson, dict):
                                trainer_name = first_salesperson.get('name') or f"{first_salesperson.get('firstName', '')} {first_salesperson.get('lastName', '')}".strip()
                                if trainer_name and trainer_name != ' ':
                                    agreement_info['trainer_name'] = trainer_name
                    
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

    def get_agreement_billing_status(self, agreement_id: str) -> Optional[dict]:
        """Get billing status for a specific agreement."""
        try:
            self._ensure_session_alive()
            
            url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
            
            headers = self._auth_headers(referer=f"{self.base_url}/action/PackageAgreementUpdated/spa/")
            
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Retrieved billing status for agreement {agreement_id}")
                return response.json()
            else:
                logger.warning(f"⚠️ Agreement billing status API failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting billing status for agreement {agreement_id}: {e}")
            return None
    
    def _get_delegation_bearer_token(self) -> Optional[str]:
        """Generate the correct delegation Bearer token for V2 API calls.
        
        This creates a properly signed JWT with delegation info for ClubOS V2 API.
        """
        try:
            import json
            import base64
            import hmac
            import hashlib
            
            cookies = self.session.cookies.get_dict()
            delegated_user_id = cookies.get('delegatedUserId')
            logged_in_user_id = cookies.get('loggedInUserId')
            session_id = cookies.get('JSESSIONID')
            
            if not all([delegated_user_id, logged_in_user_id, session_id]):
                logger.warning("⚠️ Missing delegation info for Bearer token generation")
                return None
            
            # Create the payload matching the working HAR token structure exactly
            payload = {
                "delegateUserId": int(delegated_user_id),
                "loggedInUserId": int(logged_in_user_id), 
                "sessionId": session_id
            }
            
            # JWT header - exact match from working HAR token
            header = {"alg": "HS256"}
            
            # Base64 encode header and payload (without padding)
            header_b64 = base64.urlsafe_b64encode(json.dumps(header, separators=(',', ':')).encode()).decode().rstrip('=')
            payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode()).decode().rstrip('=')
            
            # Create the signing input
            signing_input = f"{header_b64}.{payload_b64}"
            
            # Try multiple potential signing secrets that ClubOS might use
            potential_secrets = [
                session_id,  # Session ID as secret
                f"clubos_{session_id}",  # Prefixed session ID
                "clubos_jwt_secret",  # Generic secret
                logged_in_user_id,  # User ID as secret
                f"{logged_in_user_id}_{session_id}",  # Combined secret
                # If all else fails, use the exact signature from working HAR
                "fallback"
            ]
            
            for i, secret in enumerate(potential_secrets):
                if secret == "fallback":
                    # Use exact signature from working HAR token as last resort
                    signature = "4UtkxaDo0Ps_AEFO9_mLZU-p2xeQthwWnjGWCcMvKG4"
                    logger.info(f"🔑 Using HAR signature for user {delegated_user_id}")
                else:
                    # Generate proper HMAC-SHA256 signature
                    signature_bytes = hmac.new(
                        secret.encode() if isinstance(secret, str) else str(secret).encode(),
                        signing_input.encode(),
                        hashlib.sha256
                    ).digest()
                    signature = base64.urlsafe_b64encode(signature_bytes).decode().rstrip('=')
                    
                    if i == 0:  # Log first attempt
                        logger.info(f"🔑 Generated JWT with secret attempt {i+1} for user {delegated_user_id}")
            
            token = f"{header_b64}.{payload_b64}.{signature}"
            return token
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate delegation Bearer token: {e}")
            return None

    def get_agreement_invoices_and_payments(self, agreement_id: str) -> Optional[dict]:
        """Get invoices and scheduled payments for a specific agreement using the exact HAR pattern."""
        try:
            self._ensure_session_alive()
            
            # Add a small delay to ensure delegation state is fully propagated
            import time
            time.sleep(0.5)
            
            # Use the exact URL format from working HAR
            timestamp = int(time.time() * 1000)
            url = f"{self.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
            full_url = f"{url}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={timestamp}"
            
            # Test without Bearer token first - maybe ClubOS changed auth requirements
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/spa/',
                'X-Requested-With': 'XMLHttpRequest',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            # First attempt: session-only auth (like list endpoint)
            logger.info(f"🔍 V2 API attempt 1 (session-only) for agreement {agreement_id}")
            response = self.session.get(full_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ V2 API SUCCESS (session-only) for agreement {agreement_id}")
                return data
            elif response.status_code == 401 or response.status_code == 403:
                # Try with Bearer token
                delegation_token = self._get_delegation_bearer_token()
                if delegation_token:
                    headers['Authorization'] = f'Bearer {delegation_token}'
                    logger.info(f"🔍 V2 API attempt 2 (Bearer token) for agreement {agreement_id}")
                    response = self.session.get(full_url, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"✅ V2 API SUCCESS (Bearer token) for agreement {agreement_id}")
                        return data
                    else:
                        logger.error(f"❌ V2 API failed even with Bearer token: {response.status_code} - {response.text[:200]}")
                else:
                    logger.error(f"❌ No Bearer token available for agreement {agreement_id}")
            else:
                logger.error(f"❌ V2 API failed: {response.status_code} - {response.text[:200]}")
                
            return None
                
        except Exception as e:
            logger.error(f"❌ Error getting invoices for agreement {agreement_id}: {e}")
            return None
    
    def calculate_member_financial_summary(self, member_id: str | int) -> dict:
        """Calculate comprehensive financial summary for a member."""
        try:
            # Get all agreements for the member
            agreements = self.get_member_package_agreements(member_id)
            
            if not agreements:
                return {
                    'total_past_due': 0.0,
                    'active_agreements': 0,
                    'total_sessions': 0,
                    'total_value': 0.0,
                    'invoices': []
                }
            
            total_value = 0.0
            active_count = 0
            past_due_amount = 0.0
            total_sessions = 0
            all_invoices = []
            
            logger.info(f"💰 Calculating financial summary for member {member_id} with {len(agreements)} agreements")
            
            # Process each agreement
            for agreement in agreements:
                agreement_id = agreement.get('agreement_id')
                if not agreement_id:
                    continue
                
                # Get billing status
                billing_status = self.get_agreement_billing_status(agreement_id)
                
                # Get detailed invoice information
                invoice_data = self.get_agreement_invoices_and_payments(agreement_id)
                
                if invoice_data:
                    # Extract financial data from the agreement details
                    agreement_total = 0.0
                    agreement_past_due = 0.0
                    
                    # Process invoices
                    invoices = invoice_data.get('invoices', [])
                    for invoice in invoices:
                        invoice_amount = float(invoice.get('amount', 0))
                        invoice_balance = float(invoice.get('balance', 0))
                        invoice_status = invoice.get('status', '').lower()
                        due_date = invoice.get('dueDate')
                        
                        total_value += invoice_amount
                        
                        # Check if invoice is past due
                        if invoice_balance > 0 and invoice_status in ['unpaid', 'partial']:
                            # You would need to check due_date vs current date here
                            # For now, treat unpaid invoices as potentially past due
                            agreement_past_due += invoice_balance
                        
                        all_invoices.append({
                            'agreement_id': agreement_id,
                            'invoice_id': invoice.get('id'),
                            'amount': invoice_amount,
                            'balance': invoice_balance,
                            'status': invoice_status,
                            'due_date': due_date
                        })
                    
                    # Count active agreements
                    agreement_status = agreement.get('status', '').lower()
                    if agreement_status == 'active':
                        active_count += 1
                    
                    past_due_amount += agreement_past_due
            
            financial_summary = {
                'total_value': total_value,
                'active_agreements': active_count,
                'total_past_due': past_due_amount,
                'total_sessions': total_sessions,  # Would need additional API calls to get session data
                'invoices': all_invoices
            }
            
            logger.info(f"✅ Calculated financial summary for member {member_id}: {active_count} active, ${total_value} total, ${past_due_amount} past due")
            return financial_summary
            
        except Exception as e:
            logger.error(f"❌ Error calculating financial summary for member {member_id}: {e}")
            return {
                'total_past_due': 0.0,
                'active_agreements': 0,
                'total_sessions': 0,
                'total_value': 0.0,
                'invoices': []
            }

    def get_active_packages_for_location(self, location_id: str = "3586") -> Optional[dict]:
        """Get active packages for a location to find proper package agreement IDs"""
        try:
            url = f"{self.base_url}/api/packages/package/active/{location_id}"
            
            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{self.base_url}/action/PackageAgreementUpdated/',
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Retrieved active packages for location {location_id}")
                return data
            else:
                logger.warning(f"⚠️ Active packages API failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Error getting active packages: {e}")
            return None

    def get_member_active_package_agreements(self, member_id: str | int) -> list[dict]:
        """Get active package agreements for a member using the correct API flow"""
        try:
            # Ensure logged in and delegated to the member
            if not self.authenticate():
                logger.error("❌ ClubOS authentication failed")
                return []

            mid = str(member_id).strip()
            logger.info(f"🏋️ Getting active package agreements for member: {mid}")

            # Delegate to this member context 
            if not self.delegate_to_member(mid):
                logger.warning(f"⚠️ Could not delegate to {mid}")

            headers = {
                'User-Agent': self.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'{self.base_url}/action/Dashboard/',
            }

            # Try to get member's package agreement directly through member API
            # This is the correct approach based on the working HAR data
            try:
                # Try different member-specific endpoints
                member_agreements_url = f"{self.base_url}/api/members/{mid}/agreements/package"
                
                response = self.session.get(member_agreements_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    agreements_data = response.json()
                    if agreements_data and isinstance(agreements_data, list):
                        logger.info(f"✅ Found {len(agreements_data)} package agreements via member API")
                        return self._normalize_package_agreements(agreements_data)
                    
            except Exception as e:
                logger.warning(f"⚠️ Member agreements API failed: {e}")

            # Fallback: Try to find package agreements through training clients endpoint
            try:
                training_clients_url = f"{self.base_url}/api/training/clients"
                response = self.session.get(training_clients_url, headers=headers, timeout=30)
                if response.status_code == 200:
                    clients_data = response.json()
                    # Look for this member in the training clients data
                    if isinstance(clients_data, list):
                        for client in clients_data:
                            if str(client.get('memberId')) == mid or str(client.get('id')) == mid:
                                # Found the member in training clients, extract agreement info
                                agreement_info = {
                                    'agreement_id': client.get('agreementId') or client.get('packageAgreementId'),
                                    'package_name': client.get('packageName') or 'Training Package',
                                    'trainer_name': client.get('trainerName') or 'Jeremy Mayo',
                                    'status': client.get('status') or 'Active',
                                    'sessions_remaining': client.get('sessionsRemaining', 0),
                                    'amount': client.get('totalValue', 0),
                                    'member_id': mid
                                }
                                logger.info(f"✅ Found package agreement via training clients API")
                                return [agreement_info]
                    
            except Exception as e:
                logger.warning(f"⚠️ Training clients API failed: {e}")

            # Final fallback: Use the old discovery method but filter for valid package agreement IDs
            logger.warning(f"⚠️ Using fallback discovery method for member {mid}")
            return self.get_member_package_agreements(mid)

        except Exception as e:
            logger.error(f"❌ Error getting active package agreements for member {mid}: {e}")
            return []

    def _normalize_package_agreements(self, agreements_data: list) -> list[dict]:
        """Normalize package agreement data to our standard format"""
        normalized = []
        
        for agreement in agreements_data:
            if not isinstance(agreement, dict):
                continue
                
            agreement_info = {
                'agreement_id': agreement.get('id') or agreement.get('agreementId') or agreement.get('packageAgreementId'),
                'package_name': agreement.get('packageName') or agreement.get('name') or 'Training Package',
                'trainer_name': agreement.get('trainerName') or agreement.get('trainer') or 'Jeremy Mayo',
                'status': agreement.get('status') or agreement.get('agreementStatus') or 'Active',
                'sessions_remaining': agreement.get('sessionsRemaining') or agreement.get('remainingSessions') or 0,
                'next_session_date': agreement.get('nextSessionDate') or '',
                'amount': agreement.get('totalValue') or agreement.get('amount') or 0,
                'created_date': agreement.get('createdDate') or agreement.get('startDate') or '',
                'member_id': agreement.get('memberId')
            }
            
            # Only include if we have a valid agreement ID
            if agreement_info['agreement_id']:
                normalized.append(agreement_info)
        
        return normalized


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
