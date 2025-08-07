import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
import requests
import json
import re
import time

def explore_clubos_api_structure():
    """Deep dive into ClubOS API to understand how training data is actually stored"""
    print("🔬 DEEP DIVE: EXPLORING CLUBOS API STRUCTURE")
    print("=" * 60)
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return
        
    print("✅ ClubOS authenticated")
    print(f"🌐 Base URL: {api.base_url}")
    print(f"🍪 Session cookies: {list(api.session.cookies.keys())}")
    
    # Get the main dashboard to see what's available
    print("\n🔍 STEP 1: Exploring main dashboard")
    try:
        dashboard_url = f"{api.base_url}/action/Dashboard/view"
        dashboard_response = api.session.get(dashboard_url)
        
        if dashboard_response.status_code == 200:
            print("✅ Dashboard accessible")
            
            # Look for API endpoints or JavaScript that might reveal training client structure
            dashboard_html = dashboard_response.text
            
            # Look for API endpoints in JavaScript
            api_patterns = [
                r'/api/[^"\s]+',
                r'"/action/[^"\s]+',
                r'ajax[^"]*url[^"]*"([^"]+)"',
                r'fetch\([^)]*"([^"]+)"'
            ]
            
            found_endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, dashboard_html)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]
                    if '/api/' in match or '/action/' in match:
                        found_endpoints.add(match)
            
            print(f"🔍 Found {len(found_endpoints)} potential API endpoints:")
            for endpoint in sorted(list(found_endpoints)[:20]):  # Show first 20
                print(f"   {endpoint}")
                
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard exploration failed: {e}")
    
    # Try to find training-related endpoints
    print("\n🔍 STEP 2: Testing training-related endpoints")
    
    training_endpoints = [
        "/api/training/clients",
        "/api/training/packages", 
        "/api/training/members",
        "/api/members/training",
        "/api/agreements/training",
        "/api/agreements/package_agreements/all",
        "/api/agreements/active",
        "/api/billing/training",
        "/api/schedule/training",
        "/action/Training/view",
        "/action/TrainingClients/view",
        "/action/Members/training",
        "/action/Agreements/training"
    ]
    
    working_endpoints = []
    
    for endpoint in training_endpoints:
        try:
            url = f"{api.base_url}{endpoint}"
            print(f"   Testing: {endpoint}")
            
            response = api.session.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint}: SUCCESS")
                working_endpoints.append(endpoint)
                
                # Try to get a sample of the data
                try:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        data = response.json()
                        if isinstance(data, list):
                            print(f"      📊 Returns list with {len(data)} items")
                            if data:
                                print(f"      📄 Sample item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not dict'}")
                        elif isinstance(data, dict):
                            print(f"      📊 Returns dict with keys: {list(data.keys())}")
                    else:
                        print(f"      📄 Returns HTML page")
                except:
                    print(f"      📄 Response data format unknown")
                    
            elif response.status_code == 404:
                print(f"   ❌ {endpoint}: Not found")
            else:
                print(f"   ⚠️ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ {endpoint}: Error - {str(e)}")
    
    print(f"\n✅ Found {len(working_endpoints)} working endpoints")
    
    # Deep dive into working endpoints
    if working_endpoints:
        print("\n🔍 STEP 3: Deep dive into working endpoints")
        
        for endpoint in working_endpoints[:5]:  # Limit to first 5 to avoid spam
            try:
                url = f"{api.base_url}{endpoint}"
                print(f"\n📋 ANALYZING: {endpoint}")
                
                response = api.session.get(url, timeout=10)
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    
                    if isinstance(data, list) and data:
                        print(f"   📊 List with {len(data)} items")
                        sample_item = data[0]
                        print(f"   📄 Sample item structure:")
                        
                        if isinstance(sample_item, dict):
                            for key, value in sample_item.items():
                                value_type = type(value).__name__
                                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                print(f"      {key}: {value_type} = {value_preview}")
                                
                                # Look for Dennis in the data
                                if isinstance(value, str) and ('dennis' in value.lower() or 'rost' in value.lower()):
                                    print(f"      🎯 DENNIS FOUND! {key}: {value}")
                                    
                    elif isinstance(data, dict):
                        print(f"   📄 Dict structure:")
                        for key, value in data.items():
                            value_type = type(value).__name__
                            if isinstance(value, list):
                                print(f"      {key}: list[{len(value)}]")
                            else:
                                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                print(f"      {key}: {value_type} = {value_preview}")
                                
                else:
                    print(f"   📄 HTML page - checking for training client references")
                    html_content = response.text
                    
                    # Look for Dennis in HTML
                    if 'dennis' in html_content.lower() or 'rost' in html_content.lower():
                        print(f"   🎯 DENNIS FOUND in HTML!")
                        
                        # Extract surrounding context
                        lines = html_content.lower().split('\n')
                        for i, line in enumerate(lines):
                            if 'dennis' in line or 'rost' in line:
                                print(f"      Line {i}: {line.strip()}")
                                
            except Exception as e:
                print(f"   ⚠️ Error analyzing {endpoint}: {e}")
    
    # Try the delegation approach but look for all training clients
    print("\n🔍 STEP 4: Try to enumerate all training clients")
    
    try:
        # Use Jordan's known working ID to get into the training system
        jordan_id = "160402199"
        print(f"   Using Jordan's ID ({jordan_id}) to access training system...")
        
        # Set delegation to Jordan
        delegate_url = f"{api.base_url}/action/Delegate/{jordan_id}/url=false"
        delegate_params = {'_': int(time.time() * 1000)}
        
        delegate_response = api.session.get(delegate_url, params=delegate_params)
        
        if delegate_response.status_code == 200:
            print("   ✅ Delegation to Jordan successful")
            
            # Get the package agreement page
            package_url = f"{api.base_url}/action/PackageAgreementUpdated/spa/"
            package_response = api.session.get(package_url)
            
            if package_response.status_code == 200:
                # Extract token
                token_match = re.search(r'var ACCESS_TOKEN = "([^"]+)";', package_response.text)
                
                if token_match:
                    delegated_token = token_match.group(1)
                    print("   ✅ Got delegated token")
                    
                    # Try to get a list of all training clients/agreements
                    api_headers = {
                        'Authorization': f'Bearer {delegated_token}',
                        'Accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    list_endpoints = [
                        "/api/agreements/package_agreements/list",
                        "/api/agreements/package_agreements",
                        "/api/training/all_clients", 
                        "/api/members/all",
                        "/api/members?limit=1000"
                    ]
                    
                    for endpoint in list_endpoints:
                        try:
                            url = f"{api.base_url}{endpoint}"
                            response = api.session.get(url, headers=api_headers, timeout=15)
                            
                            if response.status_code == 200:
                                data = response.json()
                                print(f"   ✅ {endpoint}: Got {len(data) if isinstance(data, list) else 'data'}")
                                
                                # Look for Dennis in this data
                                if isinstance(data, list):
                                    for item in data:
                                        if isinstance(item, dict):
                                            item_str = json.dumps(item).lower()
                                            if 'dennis' in item_str or 'rost' in item_str:
                                                print(f"   🎯 DENNIS FOUND in {endpoint}!")
                                                print(f"      {json.dumps(item, indent=2)}")
                                                
                            else:
                                print(f"   ❌ {endpoint}: {response.status_code}")
                                
                        except Exception as e:
                            print(f"   ⚠️ {endpoint}: {e}")
                            
    except Exception as e:
        print(f"   ❌ Training client enumeration failed: {e}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"This deep dive should reveal:")
    print(f"1. How ClubOS actually stores training client data")
    print(f"2. Whether Dennis exists in the system under a different structure")
    print(f"3. What API endpoints are available for training data")
    print(f"4. How to properly enumerate all training clients")

if __name__ == "__main__":
    explore_clubos_api_structure()
