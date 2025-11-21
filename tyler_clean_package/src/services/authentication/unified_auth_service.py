#!/usr/bin/env python3
"""
Unified Authentication Service for ClubOS/ClubHub APIs

This service consolidates ALL authentication functions found across the codebase:
1. ClubOSRealCalendarAPI.authenticate()
2. ClubOSTrainingPackageAPI.authenticate()  
3. ClubOSFreshDataAPI.authenticate()
4. ClubOSMessagingClient.authenticate()
5. ClubOSMessagingClientSimple.authenticate()
6. ClubHubAPIClient.authenticate() 
7. SecureAuthService.authenticate_clubhub()
8. SecureAuthService.authenticate_manager()
9. ClubOSEventDeletion.authenticate()
10. ClubOSCalendarClient.authenticate()
11. ClubOSIntegration.authenticate()

Key Features:
- Single source of truth for authentication
- Credential management via SecureSecretsManager
- Session caching and reuse
- Thread-safe authentication
- Multiple authentication types (ClubOS, ClubHub)
- Automatic token management
- Session validation and refresh
"""

import requests
import logging
import threading
import time
import json
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
import urllib3

# Import SecureSecretsManager
try:
    from .secure_secrets_manager import SecureSecretsManager
except ImportError:
    from src.services.authentication.secure_secrets_manager import SecureSecretsManager

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class AuthenticationSession:
    """Represents an authenticated session with tokens and metadata"""
    
    def __init__(self, auth_type: str):
        self.auth_type = auth_type
        self.authenticated = False
        self.session = requests.Session()
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        
        # ClubOS specific tokens
        self.session_id = None
        self.logged_in_user_id = None
        self.delegated_user_id = None
        self.api_v3_access_token = None
        self.bearer_token = None
        self.club_id = None
        self.club_location_id = None
        
        # ClubHub specific tokens
        self.clubhub_bearer_token = None
        
        # Session metadata
        self.username = None
        self.base_url = None
        
    def is_expired(self, max_age_hours: int = 8) -> bool:
        """Check if session is expired"""
        age = datetime.now() - self.created_at
        return age > timedelta(hours=max_age_hours)
    
    def is_stale(self, max_idle_hours: int = 2) -> bool:
        """Check if session has been idle too long"""
        idle_time = datetime.now() - self.last_used
        return idle_time > timedelta(hours=max_idle_hours)
    
    def touch(self):
        """Update last used timestamp"""
        self.last_used = datetime.now()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        headers = {}
        if self.bearer_token:
            headers['Authorization'] = f'Bearer {self.bearer_token}'
        elif self.clubhub_bearer_token:
            headers['Authorization'] = f'Bearer {self.clubhub_bearer_token}'
        return headers

class UnifiedAuthService:
    """
    Unified Authentication Service that handles all authentication needs
    
    Consolidates patterns from:
    - ClubOS form-based authentication (calendar, training, messaging APIs)
    - ClubHub JWT-based authentication 
    - Session management and token caching
    - Thread-safe concurrent authentication
    """
    
    def __init__(self):
        self.secrets_manager = SecureSecretsManager()
        self._sessions: Dict[str, AuthenticationSession] = {}
        self._auth_lock = threading.RLock()
        self._auth_cooldown = 5.0  # Minimum seconds between auth attempts
        self._last_auth_attempts: Dict[str, float] = {}
        
        # Standard headers used across all ClubOS APIs
        self.clubos_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # ClubHub headers
        self.clubhub_headers = {
            'Host': 'clubhub-ios-api.anytimefitness.com',
            'API-version': '1',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json'
        }
        
        logger.info("🔐 Unified Authentication Service initialized")
    
    def get_credentials(self, service: str) -> Tuple[Optional[str], Optional[str]]:
        """Get credentials for a specific service from SecureSecretsManager"""
        try:
            if service.lower() == 'clubos':
                username = self.secrets_manager.get_secret('clubos-username')
                password = self.secrets_manager.get_secret('clubos-password')
                return username, password
            elif service.lower() == 'clubhub':
                email = self.secrets_manager.get_secret('clubhub-email')
                password = self.secrets_manager.get_secret('clubhub-password')
                return email, password
            else:
                logger.error(f"❌ Unknown service: {service}")
                return None, None
        except Exception as e:
            logger.error(f"❌ Error getting credentials for {service}: {e}")
            return None, None
    
    def _get_session_key(self, service: str, username: str) -> str:
        """Generate unique session key"""
        return f"{service}:{username}".lower()
    
    def _should_throttle_auth(self, session_key: str) -> bool:
        """Check if we should throttle authentication attempts"""
        last_attempt = self._last_auth_attempts.get(session_key, 0)
        return time.time() - last_attempt < self._auth_cooldown
    
    def _cleanup_expired_sessions(self):
        """Remove expired and stale sessions"""
        with self._auth_lock:
            expired_keys = []
            for key, session in self._sessions.items():
                if session.is_expired() or session.is_stale():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._sessions[key]
                logger.debug(f"🗑️ Cleaned up expired session: {key}")
    
    def authenticate_clubos(self, username: str = None, password: str = None) -> Optional[AuthenticationSession]:
        """
        Authenticate with ClubOS using the consolidated authentication pattern
        
        This implements the working authentication flow used by:
        - ClubOSRealCalendarAPI
        - ClubOSTrainingPackageAPI  
        - ClubOSMessagingClient
        - etc.
        """
        # Get credentials if not provided
        if not username or not password:
            username, password = self.get_credentials('clubos')
            
        if not username or not password:
            logger.error("❌ ClubOS credentials not available")
            return None
            
        session_key = self._get_session_key('clubos', username)
        
        with self._auth_lock:
            # Check for existing valid session
            if session_key in self._sessions:
                session = self._sessions[session_key]
                if not session.is_expired() and not session.is_stale():
                    # Validate session is still active
                    if self._validate_clubos_session(session):
                        session.touch()
                        logger.info(f"✅ Using cached ClubOS session for {username}")
                        return session
                    else:
                        # Session invalid, remove it
                        del self._sessions[session_key]
                        logger.info(f"🔄 Cached ClubOS session expired, re-authenticating {username}")
                        
            # Check throttling
            if self._should_throttle_auth(session_key):
                wait_time = self._auth_cooldown - (time.time() - self._last_auth_attempts[session_key])
                logger.info(f"⏳ Throttling ClubOS auth for {wait_time:.1f}s")
                time.sleep(wait_time)
            
            self._last_auth_attempts[session_key] = time.time()
            
            try:
                logger.info(f"🔐 Authenticating ClubOS user: {username}")
                
                # Create new session
                session = AuthenticationSession('clubos')
                session.username = username
                session.base_url = 'https://anytime.club-os.com'
                session.session.headers.update(self.clubos_headers)
                
                # Step 1: Get login page and extract CSRF tokens
                login_url = f"{session.base_url}/action/Login/view?__fsk=1221801756"
                login_response = session.session.get(login_url, verify=False, timeout=30)
                login_response.raise_for_status()
                
                soup = BeautifulSoup(login_response.text, 'html.parser')
                
                # Extract required form fields
                source_page = soup.find('input', {'name': '_sourcePage'})
                fp_token = soup.find('input', {'name': '__fp'})
                
                # Step 2: Submit login form
                login_data = {
                    'login': 'Submit',
                    'username': username,
                    'password': password,
                    '_sourcePage': source_page.get('value') if source_page else '',
                    '__fp': fp_token.get('value') if fp_token else ''
                }
                
                login_headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': login_url
                }
                
                auth_response = session.session.post(
                    f"{session.base_url}/action/Login",
                    data=login_data,
                    headers=login_headers,
                    allow_redirects=True,
                    verify=False,
                    timeout=30
                )
                
                logger.debug(f"🔍 Auth response status: {auth_response.status_code}, URL: {auth_response.url}")
                
                # Check if we're redirected to club selection page
                if "selectclub" in auth_response.url.lower() or "club/select" in auth_response.url.lower():
                    logger.info("🏢 Club selection page detected, selecting default club...")
                    
                    # Parse club selection page
                    soup = BeautifulSoup(auth_response.text, 'html.parser')
                    
                    # Look for club selection form
                    club_form = soup.find('form')
                    if club_form:
                        # Find the first available club option
                        club_select = soup.find('select', {'name': 'clubLocationId'}) or soup.find('select', {'name': 'clubId'})
                        if club_select:
                            options = club_select.find_all('option', {'value': True})
                            if options and len(options) > 0:
                                # Select the first non-empty option
                                selected_club_id = options[0].get('value')
                                logger.info(f"🏢 Selecting club ID: {selected_club_id}")
                                
                                # Submit club selection
                                club_data = {
                                    'clubLocationId': selected_club_id,
                                    'clubId': selected_club_id
                                }
                                
                                # Add any hidden form fields
                                hidden_inputs = soup.find_all('input', {'type': 'hidden'})
                                for hidden in hidden_inputs:
                                    name = hidden.get('name')
                                    value = hidden.get('value', '')
                                    if name:
                                        club_data[name] = value
                                
                                # Submit club selection
                                club_response = session.session.post(
                                    club_form.get('action') or f"{session.base_url}/action/Club/select",
                                    data=club_data,
                                    headers={'Referer': auth_response.url},
                                    allow_redirects=True,
                                    verify=False,
                                    timeout=30
                                )
                                
                                logger.debug(f"🏢 Club selection response: {club_response.status_code}, URL: {club_response.url}")
                
                # Step 3: Extract session information from cookies
                session.session_id = session.session.cookies.get('JSESSIONID')
                session.logged_in_user_id = session.session.cookies.get('loggedInUserId')
                session.delegated_user_id = session.session.cookies.get('delegatedUserId')
                session.api_v3_access_token = session.session.cookies.get('apiV3AccessToken')
                
                if not session.session_id or not session.logged_in_user_id:
                    logger.error(f"❌ ClubOS authentication failed for {username} - missing session cookies")
                    logger.debug(f"🔍 Available cookies: {list(session.session.cookies.keys())}")
                    return None
                
                # Step 4: Create Bearer token for API calls
                if session.api_v3_access_token:
                    session.bearer_token = session.api_v3_access_token
                else:
                    # Fallback: create JWT-like token
                    session.bearer_token = self._create_clubos_bearer_token(session)
                
                # Step 5: Extract club information from dashboard
                self._extract_club_info(session)
                
                # Step 6: Mark session as authenticated and cache it
                session.authenticated = True
                self._sessions[session_key] = session
                
                logger.info(f"✅ ClubOS authentication successful for {username} - User ID: {session.logged_in_user_id}")
                return session
                
            except Exception as e:
                logger.error(f"❌ ClubOS authentication error for {username}: {e}")
                return None
    
    def authenticate_clubhub(self, email: str = None, password: str = None) -> Optional[AuthenticationSession]:
        """
        Authenticate with ClubHub using JWT-based authentication
        
        This implements the working ClubHub authentication pattern
        """
        # Get credentials if not provided
        if not email or not password:
            email, password = self.get_credentials('clubhub')
            
        if not email or not password:
            logger.error("❌ ClubHub credentials not available")
            return None
            
        session_key = self._get_session_key('clubhub', email)
        
        with self._auth_lock:
            # Check for existing valid session
            if session_key in self._sessions:
                session = self._sessions[session_key]
                if not session.is_expired() and not session.is_stale():
                    session.touch()
                    logger.info(f"✅ Using cached ClubHub session for {email}")
                    return session
                else:
                    # Session expired, remove it
                    del self._sessions[session_key]
            
            # Check throttling
            if self._should_throttle_auth(session_key):
                wait_time = self._auth_cooldown - (time.time() - self._last_auth_attempts[session_key])
                logger.info(f"⏳ Throttling ClubHub auth for {wait_time:.1f}s")
                time.sleep(wait_time)
            
            self._last_auth_attempts[session_key] = time.time()
            
            try:
                logger.info(f"🔐 Authenticating ClubHub user: {email}")
                
                # Create new session
                session = AuthenticationSession('clubhub')
                session.username = email
                session.base_url = 'https://clubhub-ios-api.anytimefitness.com'
                session.session.headers.update(self.clubhub_headers)
                
                # ClubHub login
                login_url = f"{session.base_url}/api/login"
                login_data = {
                    'username': email,
                    'password': password
                }
                
                auth_response = session.session.post(
                    login_url,
                    json=login_data,
                    timeout=30
                )
                
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    session.clubhub_bearer_token = auth_data.get('accessToken')
                    
                    if session.clubhub_bearer_token:
                        session.bearer_token = session.clubhub_bearer_token
                        session.session.headers['Authorization'] = f'Bearer {session.clubhub_bearer_token}'
                        session.authenticated = True
                        self._sessions[session_key] = session
                        
                        logger.info(f"✅ ClubHub authentication successful for {email}")
                        return session
                    else:
                        logger.error(f"❌ No accessToken in ClubHub response for {email}")
                        return None
                else:
                    logger.error(f"❌ ClubHub authentication failed for {email}: {auth_response.status_code}")
                    return None
                    
            except Exception as e:
                logger.error(f"❌ ClubHub authentication error for {email}: {e}")
                return None
    
    def get_session(self, service: str, username: str = None) -> Optional[AuthenticationSession]:
        """Get an authenticated session for the specified service"""
        if service.lower() == 'clubos':
            return self.authenticate_clubos(username)
        elif service.lower() == 'clubhub':
            return self.authenticate_clubhub(username)
        else:
            logger.error(f"❌ Unknown service: {service}")
            return None
    
    def _validate_clubos_session(self, session: AuthenticationSession) -> bool:
        """Validate that a ClubOS session is still active"""
        try:
            test_response = session.session.get(
                f"{session.base_url}/action/Dashboard/view",
                timeout=10,
                verify=False,
                allow_redirects=False  # Don't follow redirects to detect login redirects
            )
            
            # Check if we're being redirected to login
            if test_response.status_code in [302, 301] and 'Login' in test_response.headers.get('Location', ''):
                logger.debug("🔄 Session expired - redirected to login")
                return False
                
            # Check if response contains login form (indicating we're at login page)
            if test_response.status_code == 200:
                if 'login' in test_response.text.lower() and 'password' in test_response.text.lower():
                    logger.debug("🔄 Session expired - at login page")
                    return False
                return True
                
            return test_response.status_code == 200
        except Exception as e:
            logger.debug(f"🔄 Session validation failed: {e}")
            return False
    
    def _create_clubos_bearer_token(self, session: AuthenticationSession) -> str:
        """Create a ClubOS Bearer token from session data"""
        try:
            payload = {
                'delegateUserId': int(session.logged_in_user_id),
                'loggedInUserId': int(session.logged_in_user_id),
                'sessionId': session.session_id
            }
            
            # Create JWT-like token
            header = 'eyJhbGciOiJIUzI1NiJ9'  # Standard JWT header
            payload_json = json.dumps(payload, separators=(',', ':'))
            payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')
            
            # Use a signature based on session data
            signature_data = f"{session.session_id}:{session.logged_in_user_id}"
            signature = hashlib.sha256(signature_data.encode()).hexdigest()[:43]  # 43 chars to match JWT
            
            return f"{header}.{payload_b64}.{signature}"
        except Exception as e:
            logger.warning(f"⚠️ Could not create Bearer token: {e}")
            return session.api_v3_access_token or "fallback_token"
    
    def _extract_club_info(self, session: AuthenticationSession):
        """Extract club information from ClubOS dashboard"""
        try:
            dashboard_response = session.session.get(
                f"{session.base_url}/action/Dashboard/view",
                verify=False,
                timeout=10
            )
            
            if dashboard_response.status_code == 200:
                soup = BeautifulSoup(dashboard_response.text, 'html.parser')
                
                # Look for club info in JavaScript
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'clubId' in script.string:
                        import re
                        club_id_match = re.search(r'clubId["\']?\s*[:=]\s*["\']?(\d+)', script.string)
                        location_id_match = re.search(r'clubLocationId["\']?\s*[:=]\s*["\']?(\d+)', script.string)
                        
                        if club_id_match:
                            session.club_id = club_id_match.group(1)
                        if location_id_match:
                            session.club_location_id = location_id_match.group(1)
                        break
                
                # Fallback to known values
                if not session.club_id:
                    session.club_id = "291"
                if not session.club_location_id:
                    session.club_location_id = "3586"
                    
        except Exception as e:
            logger.warning(f"⚠️ Could not extract club info: {e}")
            # Use fallback values
            session.club_id = "291"
            session.club_location_id = "3586"
    
    def invalidate_session(self, service: str, username: str = None):
        """Invalidate and remove a cached session"""
        if not username:
            # Get username from credentials
            username, _ = self.get_credentials(service)
            
        if username:
            session_key = self._get_session_key(service, username)
            with self._auth_lock:
                if session_key in self._sessions:
                    del self._sessions[session_key]
                    logger.info(f"🗑️ Invalidated {service} session for {username}")
    
    def cleanup_sessions(self):
        """Clean up expired sessions (can be called periodically)"""
        self._cleanup_expired_sessions()
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about current sessions for debugging"""
        with self._auth_lock:
            return {
                'total_sessions': len(self._sessions),
                'sessions': {
                    key: {
                        'auth_type': session.auth_type,
                        'authenticated': session.authenticated,
                        'created_at': session.created_at.isoformat(),
                        'last_used': session.last_used.isoformat(),
                        'is_expired': session.is_expired(),
                        'is_stale': session.is_stale(),
                        'username': session.username
                    }
                    for key, session in self._sessions.items()
                }
            }

# Global instance
_unified_auth_service = None

def get_unified_auth_service() -> UnifiedAuthService:
    """Get the global unified authentication service instance"""
    global _unified_auth_service
    if _unified_auth_service is None:
        _unified_auth_service = UnifiedAuthService()
    return _unified_auth_service

# Convenience functions for backward compatibility
def authenticate_clubos(username: str = None, password: str = None) -> Optional[AuthenticationSession]:
    """Convenience function to authenticate with ClubOS"""
    service = get_unified_auth_service()
    return service.authenticate_clubos(username, password)

def authenticate_clubhub(email: str = None, password: str = None) -> Optional[AuthenticationSession]:
    """Convenience function to authenticate with ClubHub"""
    service = get_unified_auth_service()
    return service.authenticate_clubhub(email, password)

def get_auth_session(service: str, username: str = None) -> Optional[AuthenticationSession]:
    """Convenience function to get an authenticated session"""
    auth_service = get_unified_auth_service()
    return auth_service.get_session(service, username)