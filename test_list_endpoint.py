#!/usr/bin/env python3
"""
Test the REAL working list endpoint process
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.clubos_training_api import ClubOSTrainingPackageAPI

def test_list_endpoint():
    print('=== Testing the REAL working process ===')
    
    api = ClubOSTrainingPackageAPI()
    member_id = '191215290'  # Alexander - your working example
    
    print('1. Authenticating...')
    auth_result = api.authenticate()
    print(f'   Authentication: {auth_result}')
    
    if not auth_result:
        print('   Authentication failed')
        return False
        
    print('2. Delegating to member...')
    delegate_result = api.delegate_to_member(member_id)
    print(f'   Delegation: {delegate_result}')
    
    if not delegate_result:
        print('   Delegation failed')
        return False
        
    print('3. Calling the list endpoint directly...')
    url = 'https://anytime.club-os.com/api/agreements/package_agreements/list'
    response = api.session.get(url)
    print(f'   Status: {response.status_code}')
    print(f'   Response preview: {response.text[:200]}')
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f'   Success! Found data type: {type(data)}')
            if isinstance(data, list):
                print(f'   Number of agreements: {len(data)}')
                if len(data) > 0:
                    first = data[0]
                    if isinstance(first, dict):
                        print(f'   First agreement keys: {list(first.keys())}')
                        if 'id' in first:
                            print(f'   First agreement ID: {first["id"]}')
                    else:
                        print(f'   First item type: {type(first)}')
            elif isinstance(data, dict):
                print(f'   Data keys: {list(data.keys())}')
            return True
        except Exception as e:
            print(f'   Could not parse JSON: {e}')
            return False
    else:
        print(f'   ERROR: {response.status_code}')
        print(f'   Error response: {response.text}')
        return False

if __name__ == "__main__":
    test_list_endpoint()
