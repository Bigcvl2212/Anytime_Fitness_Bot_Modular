#!/usr/bin/env python3
"""
Simple ClubHub Login Test
Tests the ClubHub authentication with current credentials
"""

import requests
import json
from datetime import datetime
import os

def test_clubhub_login():
    """Test ClubHub login with current credentials"""
    
    print(f"🕐 {datetime.now().strftime('%H:%M:%S')} - Testing ClubHub login...")
    
    try:
        url = 'https://clubhub-ios-api.anytimefitness.com/api/login'
        data = {
            'email': 'mayo.jeremy2212@gmail.com',
            'password': 'SruLEqp464_GLrF'
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'API-version': '1',
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4'
        }
        
        print('📡 Sending login request...')
        response = requests.post(url, json=data, headers=headers, timeout=15)
        print(f'📨 Response: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Login successful!')
            result = response.json()
            if 'token' in result:
                token = result['token']
                print(f'🎫 Token: {token[:50]}...')
                
                # Save the token
                os.makedirs('data', exist_ok=True)
                with open('data/fresh_clubhub_token.txt', 'w') as f:
                    f.write(token)
                print('💾 Token saved to data/fresh_clubhub_token.txt')
                
                # Test the token immediately
                print('🧪 Testing fresh token...')
                test_url = 'https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members'
                test_headers = {
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json',
                    'API-version': '1'
                }
                test_response = requests.get(test_url, headers=test_headers, params={'page': 1, 'pageSize': 1}, timeout=10)
                print(f'🔍 API test: {test_response.status_code}')
                
                if test_response.status_code == 200:
                    print('🎉 SUCCESS! Fresh token works!')
                    test_data = test_response.json()
                    members = test_data.get('members', test_data.get('data', []))
                    print(f'📊 Found {len(members)} members in test response')
                    return token
                else:
                    print('❌ Token test failed')
                    return None
            else:
                print('❌ No token in response')
                print(f'Response: {result}')
                return None
        else:
            print(f'❌ Login failed: {response.status_code}')
            try:
                error = response.json()
                print(f'Error: {error}')
            except:
                print(f'Response: {response.text[:200]}')
            return None
                
    except requests.exceptions.Timeout:
        print('⏰ Request timed out')
        return None
    except requests.exceptions.ConnectionError:
        print('🔌 Connection error')
        return None
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == "__main__":
    token = test_clubhub_login()
    if token:
        print("\n✅ ClubHub authentication successful!")
        print("🚀 Ready to run comprehensive data pull!")
    else:
        print("\n❌ ClubHub authentication failed")
        print("💡 Check credentials or network connection")
