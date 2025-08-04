#!/usr/bin/env python3
"""
Debug script to find the correct endpoints for getting ALL prospects
"""

import requests
import json
import base64

class EndpointTester:
    def __init__(self):
        self.base_url = "https://clubhub-ios-api.anytimefitness.com"
        self.access_token = None
        self.session = requests.Session()
        
        # Working credentials
        self.username = "mayo.jeremy2212@gmail.com"
        self.password = "SruLEqp464_GLrF"
        
        # Headers that work
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
        print("🔐 Authenticating...")
        
        login_url = f"{self.base_url}/api/login"
        payload = {"username": self.username, "password": self.password}
        
        response = self.session.post(login_url, headers=self.headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('accessToken')
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                **self.headers
            })
            
            print("✅ Authentication successful!")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def test_endpoint(self, endpoint, params=None):
        """Test an endpoint and return response info"""
        try:
            response = self.session.get(endpoint, params=params)
            data = response.json() if response.status_code == 200 else None
            
            result = {
                'endpoint': endpoint,
                'params': params,
                'status': response.status_code,
                'data_type': type(data).__name__,
                'count': len(data) if isinstance(data, list) else 0,
                'keys': list(data.keys()) if isinstance(data, dict) else None,
                'sample': data[:2] if isinstance(data, list) and len(data) > 0 else data
            }
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'params': params,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def find_prospect_endpoints(self):
        """Test different endpoints to find where all prospects are stored"""
        print("\n🔍 Testing different prospect endpoints...")
        
        club_id = "1156"
        
        # Test various endpoint patterns
        endpoints_to_test = [
            f"{self.base_url}/api/clubs/{club_id}/prospects",
            f"{self.base_url}/api/clubs/{club_id}/leads",
            f"{self.base_url}/api/clubs/{club_id}/contacts",
            f"{self.base_url}/api/clubs/{club_id}/people",
            f"{self.base_url}/api/prospects",
            f"{self.base_url}/api/leads", 
            f"{self.base_url}/api/contacts",
            f"{self.base_url}/api/clubs/{club_id}/all-prospects",
            f"{self.base_url}/api/clubs/{club_id}/prospect-list",
            f"{self.base_url}/api/clubs/{club_id}/sales-prospects"
        ]
        
        # Test different pagination parameters
        pagination_params = [
            None,
            {'page': 1, 'per_page': 100},
            {'page': 1, 'limit': 100},
            {'offset': 0, 'limit': 100},
            {'start': 0, 'count': 100},
            {'size': 100},
            {'pageSize': 100},
            {'all': 'true'},
            {'include_inactive': 'true'},
            {'status': 'all'}
        ]
        
        results = []
        
        for endpoint in endpoints_to_test:
            print(f"\n📊 Testing: {endpoint}")
            
            # Test without params first
            result = self.test_endpoint(endpoint)
            results.append(result)
            print(f"  No params: {result['status']} - {result['count']} items")
            
            # Test with different pagination params
            for params in pagination_params[:3]:  # Test first 3 param sets
                if params:
                    result = self.test_endpoint(endpoint, params)
                    results.append(result)
                    print(f"  {params}: {result['status']} - {result['count']} items")
        
        # Find the best results
        print(f"\n" + "="*60)
        print("🎯 BEST RESULTS:")
        print("="*60)
        
        best_results = [r for r in results if r.get('count', 0) > 100]  # More than 100 items
        best_results.sort(key=lambda x: x.get('count', 0), reverse=True)
        
        for result in best_results[:5]:  # Top 5 results
            print(f"\n✅ {result['endpoint']}")
            print(f"   Params: {result['params']}")
            print(f"   Count: {result['count']} items")
            print(f"   Status: {result['status']}")
            if result.get('sample'):
                print(f"   Sample keys: {list(result['sample'][0].keys()) if result['sample'] else 'N/A'}")
        
        return best_results

def main():
    tester = EndpointTester()
    if tester.authenticate():
        tester.find_prospect_endpoints()

if __name__ == "__main__":
    main()
