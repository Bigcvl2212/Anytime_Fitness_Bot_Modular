import requests
import json
import time
from typing import Dict, Optional, Tuple
import logging
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubHubAutomatedLogin:
    """
    Automated login system for ClubHub to obtain fresh Bearer tokens and cookies
    """
    
    def __init__(self):
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
            'Accept': 'application/json',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8',
            'Connection': 'keep-alive',
            'API-version': '1',
            'Content-Type': 'application/json',
            'Cookie': 'visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy'
        })
        
    def get_login_page(self) -> Optional[str]:
        """
        Get the login page to extract any necessary tokens or form data
        Note: ClubHub uses API-based authentication, not traditional web forms
        """
        try:
            logger.info("Getting fresh cookies from ClubHub domain...")
            
            # Make a request to get fresh cookies (like a browser would)
            response = self.session.get(f"{self.base_url}/api/clubs/1156/features")
            
            logger.info(f"Cookie refresh status: {response.status_code}")
            logger.info(f"Cookies received: {len(self.session.cookies)}")
            
            return "COOKIES_REFRESHED"
        except Exception as e:
            logger.error(f"Error refreshing cookies: {e}")
            return None
    
    def login(self, email: str = None, password: str = None) -> Tuple[bool, Dict]:
        """
        Perform automated login to ClubHub
        
        Args:
            email: User email (optional, will use config if not provided)
            password: User password (optional, will use config if not provided)
            
        Returns:
            Tuple of (success, auth_data)
        """
        try:
            # Get credentials from config if not provided
            if email is None or password is None:
                try:
                    from .secure_secrets_manager import SecureSecretsManager
                    secrets_manager = SecureSecretsManager()
                    CLUBHUB_EMAIL = secrets_manager.get_secret('clubhub-email')
                    CLUBHUB_PASSWORD = secrets_manager.get_secret('clubhub-password')
                except Exception:
                    CLUBHUB_EMAIL = None
                        CLUBHUB_PASSWORD = None
                    email = email or CLUBHUB_EMAIL
                    password = password or CLUBHUB_PASSWORD
                except ImportError:
                    logger.error("ClubHub credentials not found in config")
                    return False, {"error": "Credentials not configured"}
            
            logger.info("Starting ClubHub automated login...")
            
            # Step 1: Skip API availability check for now
            logger.info("Proceeding with API login...")
            
            # Step 2: Submit API login
            login_data = {
                'email': email,
                'password': password
            }
            
            logger.info("Submitting API login credentials...")
            response = self.session.post(
                f"{self.base_url}/api/login",
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'API-version': '1'
                }
            )
            
            logger.info(f"Login response status: {response.status_code}")
            
            # Check if login was successful
            if response.status_code == 200:
                try:
                    auth_response = response.json()
                    bearer_token = auth_response.get('token')
                    
                    if bearer_token:
                        logger.info("Login successful!")
                        
                        # Extract authentication data
                        auth_data = self._extract_auth_data(bearer_token)
                        return True, auth_data
                    else:
                        logger.error("No token in response")
                        return False, {"error": "No token in response"}
                except json.JSONDecodeError:
                    logger.error("Invalid JSON response")
                    return False, {"error": "Invalid JSON response"}
            else:
                logger.error(f"Login failed. Status: {response.status_code}")
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {error_data}")
                except:
                    logger.error(f"Response text: {response.text}")
                return False, {"error": "Login failed", "status": response.status_code}
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False, {"error": str(e)}
    
    def _extract_auth_data(self, bearer_token: str = None) -> Dict:
        """
        Extract Bearer token and cookies from the authenticated session
        """
        auth_data = {
            "bearer_token": bearer_token,
            "cookies": {},
            "headers": dict(self.session.headers)
        }
        
        # Extract cookies
        for cookie in self.session.cookies:
            auth_data["cookies"][cookie.name] = cookie.value
        
        logger.info(f"Extracted {len(auth_data['cookies'])} cookies")
        if auth_data["bearer_token"]:
            logger.info("Bearer token extracted from API response")
        else:
            logger.warning("No Bearer token available")
        
        return auth_data
    
    def test_api_access(self, auth_data: Dict) -> bool:
        """
        Test if the authentication data works for API calls
        """
        try:
            # Test with a simple API endpoint
            test_url = f"{self.base_url}/api/clubs/1156/members"
            
            headers = {
                'Authorization': f'Bearer {auth_data["bearer_token"]}' if auth_data["bearer_token"] else '',
                'Cookie': '; '.join([f"{k}={v}" for k, v in auth_data["cookies"].items()])
            }
            
            response = requests.get(test_url, headers=headers)
            logger.info(f"API test response: {response.status_code}")
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"API test failed: {e}")
            return False

def main():
    """
    Test the automated login system
    """
    try:
        from .secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        CLUBHUB_EMAIL = secrets_manager.get_secret('clubhub-email')
        CLUBHUB_PASSWORD = secrets_manager.get_secret('clubhub-password')
    except Exception as e:
        logger.error(f"ClubHub credentials not found: {e}")
        return None
    
    login_system = ClubHubAutomatedLogin()
    
    logger.info("Testing ClubHub automated login...")
    success, auth_data = login_system.login(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
    
    if success:
        logger.info("Login successful!")
        logger.info(f"Auth data keys: {list(auth_data.keys())}")
        
        # Test API access
        if login_system.test_api_access(auth_data):
            logger.info("API access confirmed!")
        else:
            logger.warning("API access failed - may need different auth method")
            
        return auth_data
    else:
        logger.error(f"Login failed: {auth_data}")
        return None

if __name__ == "__main__":
    main() 