import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
import requests
import time
import re

def deep_search_for_dennis():
    """Deep search through ClubOS to find Dennis's training data"""
    print("🔍 DEEP SEARCH FOR DENNIS IN CLUBOS")
    print("=" * 50)
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return
        
    print("✅ ClubOS authenticated")
    
    # Try to access raw ClubOS pages and look for Dennis manually
    try:
        # 1. Try the member search page directly
        print("\n🔍 METHOD 1: Direct member search page")
        search_url = f"{api.base_url}/action/Members/view"
        
        search_response = api.session.get(search_url)
        if search_response.status_code == 200:
            print("✅ Accessed members page")
            
            # Look for any reference to Dennis in the HTML
            if "dennis" in search_response.text.lower() or "rost" in search_response.text.lower():
                print("✅ Found Dennis reference in members page!")
                
                # Extract any member IDs that might be Dennis
                id_pattern = r'"memberId":\s*"?(\d+)"?'
                member_ids = re.findall(id_pattern, search_response.text)
                
                print(f"Found {len(member_ids)} member IDs in page")
                for mid in member_ids[:10]:  # Test first 10
                    print(f"Testing member ID: {mid}")
                    
        # 2. Try package agreements page
        print("\n🔍 METHOD 2: Package agreements page")
        agreements_url = f"{api.base_url}/action/PackageAgreements/view"
        
        agreements_response = api.session.get(agreements_url)
        if agreements_response.status_code == 200:
            print("✅ Accessed package agreements page")
            
            if "dennis" in agreements_response.text.lower() or "rost" in agreements_response.text.lower():
                print("✅ Found Dennis reference in package agreements!")
                
        # 3. Try training calendar page
        print("\n🔍 METHOD 3: Training calendar page")
        calendar_url = f"{api.base_url}/action/Calendar/view"
        
        calendar_response = api.session.get(calendar_url)
        if calendar_response.status_code == 200:
            print("✅ Accessed calendar page")
            
            if "dennis" in calendar_response.text.lower() or "rost" in calendar_response.text.lower():
                print("✅ Found Dennis reference in calendar!")
                
        # 4. Try to brute force search recent member IDs
        print("\n🔍 METHOD 4: Brute force recent member IDs")
        
        # Get a token for API calls
        package_agreement_url = f"{api.base_url}/action/PackageAgreementUpdated/spa/"
        package_response = api.session.get(package_agreement_url)
        
        if package_response.status_code == 200:
            token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', package_response.text)
            
            if token_match:
                token = token_match.group(1)
                print(f"✅ Got API token for brute force search")
                
                api_headers = {
                    'Authorization': f'Bearer {token}',
                    'Accept': '*/*',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # Try a range of member IDs around Dennis's ClubHub ID
                base_id = 65828815
                test_range = 1000
                
                print(f"Testing member IDs from {base_id - test_range} to {base_id + test_range}")
                
                for offset in range(-test_range, test_range + 1, 100):  # Test every 100th ID
                    test_id = base_id + offset
                    
                    try:
                        # Try to get member info
                        member_url = f"{api.base_url}/api/members/{test_id}"
                        response = api.session.get(member_url, headers=api_headers, timeout=5)
                        
                        if response.status_code == 200:
                            member_data = response.json()
                            
                            first_name = member_data.get('firstName', '').upper()
                            last_name = member_data.get('lastName', '').upper()
                            
                            if 'DENNIS' in first_name and 'ROST' in last_name:
                                print(f"🎉 FOUND DENNIS! Member ID: {test_id}")
                                print(f"   Data: {member_data}")
                                
                                # Now try to get his training data
                                agreements_url = f"{api.base_url}/api/agreements/package_agreements?memberId={test_id}"
                                agreements_response = api.session.get(agreements_url, headers=api_headers, timeout=5)
                                
                                if agreements_response.status_code == 200:
                                    agreements_data = agreements_response.json()
                                    print(f"   Training agreements: {agreements_data}")
                                    
                                return test_id
                                
                    except Exception as e:
                        continue
                        
                    if offset % 500 == 0:
                        print(f"   Tested up to ID {test_id}...")
                        
        print("❌ Brute force search did not find Dennis")
        
        # 5. Last resort - check if Dennis might be in a different ClubOS environment
        print("\n🔍 METHOD 5: Check ClubOS environment")
        print(f"Current ClubOS URL: {api.base_url}")
        
        # Try to see what club/environment we're connected to
        dashboard_url = f"{api.base_url}/action/Dashboard/view"
        dashboard_response = api.session.get(dashboard_url)
        
        if dashboard_response.status_code == 200:
            # Look for club information
            club_pattern = r'club.*?(\d+)'
            club_matches = re.findall(club_pattern, dashboard_response.text.lower())
            
            if club_matches:
                print(f"Found club references: {club_matches}")
                
        print("\n💭 POSSIBLE REASONS DENNIS IS NOT FOUND:")
        print("1. Dennis is in a different ClubOS environment/database")
        print("2. Dennis's training is managed outside ClubOS (local system)")
        print("3. Dennis's member ID is completely different from ClubHub")
        print("4. Dennis's training package is inactive/suspended in ClubOS")
        print("5. Access permissions prevent seeing Dennis's data")
        
    except Exception as e:
        print(f"❌ Deep search failed: {e}")

if __name__ == "__main__":
    deep_search_for_dennis()
