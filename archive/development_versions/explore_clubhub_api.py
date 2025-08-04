import requests
import json
import base64

class ClubHubAPIExplorer:
    """Explore ClubHub API endpoints to find the right ones"""
    
    def __init__(self):
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        self.access_token = None
        self.session = requests.Session()
        
        # Working credentials from HAR analysis
        self.username = "mayo.jeremy2212@gmail.com"
        self.password = "SruLEqp464_GLrF"
        
        self.headers = {
            'Content-Type': 'application/json',
            'API-version': '1',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8'
        }
    
    def authenticate(self):
        """Authenticate with ClubHub"""
        print("🔐 Authenticating with ClubHub...")
        
        login_url = f"{self.base_url}/api/login"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(login_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('accessToken')
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    **self.headers
                })
                
                print("✅ Authentication successful!")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_endpoint(self, endpoint, method='GET', params=None):
        """Test an API endpoint"""
        url = f"{self.base_url}/api/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=params)
            else:
                return None
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text[:500] if response.text else None
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def explore_api(self):
        """Explore common API endpoints"""
        print("\n🔍 Exploring ClubHub API endpoints...")
        print("=" * 50)
        
        # Common endpoints to test
        endpoints = [
            ('me', 'GET'),
            ('clubs', 'GET'),
            ('members', 'GET'),
            ('prospects', 'GET'), 
            ('memberships', 'GET'),
            ('agreements', 'GET'),
            ('contacts', 'GET'),
            ('leads', 'GET'),
            ('users', 'GET'),
            ('profile', 'GET'),
            ('dashboard', 'GET'),
            ('members/search', 'GET'),
            ('prospects/search', 'GET'),
        ]
        
        working_endpoints = []
        
        for endpoint, method in endpoints:
            print(f"\n📡 Testing: {method} /api/{endpoint}")
            result = self.test_endpoint(endpoint, method)
            
            if result and not result.get('error'):
                status = result['status_code']
                if status == 200:
                    print(f"   ✅ SUCCESS (200)")
                    working_endpoints.append(endpoint)
                    
                    # Show response preview
                    content = result.get('content', '')
                    if content:
                        print(f"   📄 Response: {content[:100]}...")
                elif status == 401:
                    print(f"   🔒 UNAUTHORIZED (401)")
                elif status == 403:
                    print(f"   🚫 FORBIDDEN (403)")
                elif status == 404:
                    print(f"   ❌ NOT FOUND (404)")
                else:
                    print(f"   ⚠️  Status: {status}")
            else:
                error = result.get('error', 'Unknown error') if result else 'No response'
                print(f"   💥 ERROR: {error}")
        
        print(f"\n🎯 Working endpoints found: {len(working_endpoints)}")
        for endpoint in working_endpoints:
            print(f"   ✅ /api/{endpoint}")
        
        return working_endpoints
    
    def test_club_specific_endpoints(self, club_ids=['1156', '1657']):
        """Test club-specific endpoints"""
        print(f"\n🏢 Testing club-specific endpoints...")
        print("=" * 40)
        
        working_endpoints = []
        
        for club_id in club_ids:
            print(f"\nClub {club_id}:")
            
            # Test different member/prospect endpoints for this club
            club_endpoints = [
                f'clubs/{club_id}/members',
                f'clubs/{club_id}/prospects', 
                f'clubs/{club_id}/agreements',
                f'clubs/{club_id}/contacts',
                f'members?clubId={club_id}',
                f'prospects?clubId={club_id}',
                f'agreements?clubId={club_id}',
            ]
            
            for endpoint in club_endpoints:
                print(f"  📡 Testing: /api/{endpoint}")
                result = self.test_endpoint(endpoint)
                
                if result and result.get('status_code') == 200:
                    print(f"     ✅ SUCCESS")
                    working_endpoints.append(f"{club_id}: {endpoint}")
                    
                    # Show data preview
                    content = result.get('content', '')
                    if content:
                        try:
                            data = json.loads(content)
                            if isinstance(data, list):
                                print(f"     📊 Found {len(data)} items")
                            elif isinstance(data, dict):
                                if 'data' in data:
                                    print(f"     📊 Found {len(data['data'])} items in data array")
                                else:
                                    print(f"     📊 Response object keys: {list(data.keys())}")
                        except:
                            print(f"     📄 Response: {content[:100]}...")
                else:
                    status = result.get('status_code', 'ERROR') if result else 'ERROR'
                    print(f"     ❌ Status: {status}")
        
        print(f"\n🎯 Working club endpoints: {len(working_endpoints)}")
        for endpoint in working_endpoints:
            print(f"   ✅ {endpoint}")
        
        return working_endpoints

if __name__ == "__main__":
    explorer = ClubHubAPIExplorer()
    
    if explorer.authenticate():
        # Explore general endpoints
        working_general = explorer.explore_api()
        
        # Test club-specific endpoints  
        working_club = explorer.test_club_specific_endpoints()
        
        print(f"\n🎉 API Exploration Complete!")
        print(f"📊 Total working endpoints: {len(working_general) + len(working_club)}")
    else:
        print("❌ Could not authenticate - skipping API exploration")
