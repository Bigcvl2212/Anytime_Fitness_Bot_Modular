"""
ClubOS Training Clients API Integration
Pull fresh training client data directly from ClubOS API
"""

import requests
import json
import logging
from datetime import datetime
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClubOSTrainingClientsAPI:
    """Pull training clients data directly from ClubOS using captured API endpoints"""
    
    def __init__(self, username="j.mayo", password="j@SD4fjhANK5WNA"):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticated = False
        self.bearer_token = None
        self.session_id = None
        self.user_id = None
        
        # ClubOS API endpoints
        self.base_url = "https://anytime.club-os.com"
        self.login_url = f"{self.base_url}/action/SignIn"
        self.delegate_url = f"{self.base_url}/action/Delegate/0/url=false"
        
        # Standard headers for ClubOS requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://anytime.club-os.com/action/Dashboard/PersonalTraining'
        }
        
        self.session.headers.update(self.headers)
        
    def authenticate(self):
        """Authenticate with ClubOS and get session tokens"""
        try:
            logger.info("🔑 Authenticating with ClubOS...")
            
            # First, get the login page to establish session
            login_page_url = f"{self.base_url}/action/SignIn"
            response = self.session.get(login_page_url)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to access login page: {response.status_code}")
                return False
            
            # Prepare login data
            login_data = {
                'userName': self.username,
                'password': self.password,
                'rememberMe': 'false'
            }
            
            # Submit login form
            login_response = self.session.post(self.login_url, data=login_data)
            
            if login_response.status_code == 200:
                # Check if login was successful by looking for redirect or session cookies
                cookies = self.session.cookies.get_dict()
                
                if 'JSESSIONID' in cookies and 'loggedInUserId' in cookies:
                    self.session_id = cookies['JSESSIONID']
                    self.user_id = cookies['loggedInUserId']
                    
                    logger.info(f"✅ ClubOS authentication successful")
                    logger.info(f"   Session ID: {self.session_id[:20]}...")
                    logger.info(f"   User ID: {self.user_id}")
                    
                    self.authenticated = True
                    return True
                else:
                    logger.error("❌ Login failed - no session cookies received")
                    return False
            else:
                logger.error(f"❌ Login request failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_training_clients(self):
        """Get all training clients from ClubOS Personal Training system"""
        if not self.authenticated:
            logger.info("🔐 Not authenticated, attempting login...")
            if not self.authenticate():
                logger.error("❌ Failed to authenticate with ClubOS")
                return []
        
        try:
            logger.info("📋 Fetching training clients from ClubOS...")
            
            # Add timestamp parameter like in the captured request
            timestamp = int(time.time() * 1000)
            
            # Make request to the delegate endpoint (training clients list)
            delegate_url = f"{self.delegate_url}?_={timestamp}"
            
            response = self.session.get(delegate_url)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully fetched training clients data")
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    logger.info(f"📊 Received JSON data with keys: {list(data.keys()) if isinstance(data, dict) else 'List data'}")
                    return data
                except json.JSONDecodeError:
                    # If not JSON, log the response content
                    logger.info(f"📄 Received text response: {response.text[:200]}...")
                    return response.text
                    
            else:
                logger.error(f"❌ Failed to fetch training clients: {response.status_code}")
                logger.error(f"   Response: {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching training clients: {e}")
            return []
    
    def get_personal_training_dashboard(self):
        """Get the personal training dashboard page to extract client data"""
        if not self.authenticated:
            if not self.authenticate():
                return None
        
        try:
            logger.info("📊 Fetching Personal Training dashboard...")
            
            dashboard_url = f"{self.base_url}/action/Dashboard/PersonalTraining"
            response = self.session.get(dashboard_url)
            
            if response.status_code == 200:
                logger.info("✅ Successfully fetched Personal Training dashboard")
                return response.text
            else:
                logger.error(f"❌ Failed to fetch dashboard: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching dashboard: {e}")
            return None

# Test the API
if __name__ == "__main__":
    print("🧪 Testing ClubOS Training Clients API...")
    
    api = ClubOSTrainingClientsAPI()
    
    # Test authentication
    if api.authenticate():
        print("✅ Authentication successful!")
        
        # Test getting training clients
        clients = api.get_training_clients()
        print(f"📋 Training clients result type: {type(clients)}")
        
        if isinstance(clients, dict):
            print(f"📊 Dictionary keys: {list(clients.keys())}")
        elif isinstance(clients, list):
            print(f"📊 List length: {len(clients)}")
        else:
            print(f"📄 Content preview: {str(clients)[:300]}...")
            
        # Also try getting the dashboard
        dashboard = api.get_personal_training_dashboard()
        if dashboard:
            print("✅ Dashboard fetched successfully")
            print(f"📄 Dashboard preview: {dashboard[:200]}...")
    else:
        print("❌ Authentication failed!")
