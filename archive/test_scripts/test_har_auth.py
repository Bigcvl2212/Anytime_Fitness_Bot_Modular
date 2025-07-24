import json
import base64
import requests

def decode_response(encoded_response):
    """Decode base64 encoded response"""
    try:
        decoded = base64.b64decode(encoded_response).decode('utf-8')
        return json.loads(decoded)
    except:
        return encoded_response

def test_clubhub_authentication():
    """Test ClubHub authentication using exact HAR parameters"""
    
    print("ClubHub Authentication Test")
    print("=" * 40)
    
    # From successful HAR request #951
    login_url = "https://clubhub-ios-api.anytimefitness.com/api/login"
    
    # Exact headers from successful request
    headers = {
        'Host': 'clubhub-ios-api.anytimefitness.com',
        'Content-Type': 'application/json',
        'API-version': '1',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
        'Accept-Language': 'en-US',
        'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8'
    }
    
    # From the successful login (request #951) - different password!
    payload = {
        "password": "SruLEqp464_GLrF",
        "username": "mayo.jeremy2212@gmail.com"
    }
    
    print(f"Attempting login to: {login_url}")
    print(f"Username: {payload['username']}")
    print(f"Password: [REDACTED] (from successful HAR)")
    
    try:
        response = requests.post(login_url, headers=headers, json=payload)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SUCCESS! Login worked!")
            
            # Try to decode response
            response_text = response.text
            print(f"Raw response: {response_text[:100]}...")
            
            # Try base64 decode
            try:
                decoded_response = decode_response(response_text)
                print("\nDecoded response:")
                
                if isinstance(decoded_response, dict):
                    for key, value in decoded_response.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  {key}: {value[:50]}... (truncated)")
                        else:
                            print(f"  {key}: {value}")
                            
                    # Extract access token
                    if 'accessToken' in decoded_response:
                        access_token = decoded_response['accessToken']
                        print(f"\nAccess Token found: {access_token[:50]}...")
                        
                        # Test the token with a simple API call
                        test_headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Accept': 'application/json',
                            'User-Agent': headers['User-Agent'],
                            'API-version': '1'
                        }
                        
                        test_url = "https://clubhub-ios-api.anytimefitness.com/api/me"
                        test_response = requests.get(test_url, headers=test_headers)
                        
                        print(f"\nTesting token with /api/me endpoint:")
                        print(f"Status: {test_response.status_code}")
                        if test_response.status_code == 200:
                            print("Token is valid!")
                            print(f"Response: {test_response.text[:200]}...")
                        else:
                            print("Token test failed")
                            
                else:
                    print(f"Decoded response: {decoded_response}")
                    
            except Exception as e:
                print(f"Could not decode response: {e}")
                print(f"Raw response: {response_text}")
                
        else:
            print("Login failed!")
            print(f"Response: {response.text}")
            
            # Try to decode error response
            try:
                decoded_error = decode_response(response.text)
                print(f"Decoded error: {decoded_error}")
            except:
                pass
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_clubhub_authentication()
