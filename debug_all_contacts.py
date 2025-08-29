#!/usr/bin/env python3
"""
Debug script to find the 9000 contacts/prospects in ClubHub
"""

import requests
import json

def test_all_contacts():
    """Test to find all 9000 contacts"""
    try:
        # Login to ClubHub
        headers = {
            'Content-Type': 'application/json',
            'API-version': '1',
            'Accept': 'application/json',
            'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # Login
        login_data = {'username': 'mayo.jeremy2212@gmail.com', 'password': 'SruLEqp464_GLrF'}
        login_response = session.post('https://clubhub-ios-api.anytimefitness.com/api/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get('accessToken')
            session.headers.update({'Authorization': f'Bearer {token}'})
            
            print('✅ Login successful')
            
            club_id = '1156'
            
            # Test members endpoint with massive pagination
            print('\n🔍 Testing MEMBERS endpoint with high pagination...')
            
            total_members = 0
            page = 1
            page_size = 1000  # Large page size
            
            while page <= 20:  # Test up to 20 pages (20,000 potential records)
                try:
                    url = f'https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/members?page={page}&pageSize={page_size}'
                    response = session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        count = len(data) if isinstance(data, list) else 0
                        total_members += count
                        
                        print(f'  Page {page}: {count} members (Total: {total_members})')
                        
                        if count > 0 and page == 1:
                            # Analyze first page
                            statuses = {}
                            for member in data:
                                status = member.get('membershipStatus', 'Unknown')
                                statuses[status] = statuses.get(status, 0) + 1
                            
                            print(f'    Statuses on page 1:')
                            for status, cnt in statuses.items():
                                print(f'      {status}: {cnt}')
                        
                        if count == 0:
                            print(f'  Page {page}: 0 members (stopping)')
                            break
                            
                    else:
                        print(f'  Page {page}: HTTP {response.status_code} (stopping)')
                        break
                        
                    page += 1
                    
                except Exception as e:
                    print(f'  Page {page}: Error - {e}')
                    break
            
            print(f'\n📊 Total members found: {total_members}')
            
            # Test with smaller page size to see if we get different results
            if total_members < 5000:
                print('\n🔍 Testing with smaller page size (100)...')
                
                total_small = 0
                page = 1
                
                while page <= 100 and total_small < 10000:  # Stop at 100 pages or 10k records
                    try:
                        url = f'https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/members?page={page}&pageSize=100'
                        response = session.get(url, timeout=15)
                        
                        if response.status_code == 200:
                            data = response.json()
                            count = len(data) if isinstance(data, list) else 0
                            total_small += count
                            
                            if page % 10 == 0 or count == 0:  # Print every 10th page
                                print(f'  Page {page}: {count} members (Total: {total_small})')
                            
                            if count == 0:
                                break
                                
                        else:
                            print(f'  Page {page}: HTTP {response.status_code} (stopping)')
                            break
                            
                        page += 1
                        
                    except Exception as e:
                        print(f'  Page {page}: Error - {e}')
                        break
                
                print(f'📊 Total with small pages: {total_small}')
            
            # Check if the 9000 includes both prospects AND members
            print(f'\n🎯 SUMMARY:')
            print(f'  Prospects endpoint: 47 records')
            print(f'  Members endpoint: {total_members} records')
            print(f'  Combined total: {47 + total_members} records')
            
            if total_members > 5000:
                print(f'✅ Found large dataset! The 9000 may include members + prospects combined.')
            else:
                print(f'⚠️ Still missing records. Need to investigate other endpoints.')
            
        else:
            print(f'❌ Login failed: {login_response.status_code}')
            
    except Exception as e:
        print(f'❌ Script error: {e}')

if __name__ == '__main__':
    test_all_contacts()








