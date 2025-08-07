import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
import re

def check_training_pages_for_dennis():
    """Check the working training pages to find Dennis"""
    print("🔍 CHECKING TRAINING PAGES FOR DENNIS")
    print("=" * 50)
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return
        
    print("✅ ClubOS authenticated")
    
    # Check the training-related pages we found working
    training_pages = [
        "/action/Training/view",
        "/action/TrainingClients/view", 
        "/action/Members/training",
        "/action/Agreements/training"
    ]
    
    for page in training_pages:
        print(f"\n🔍 ANALYZING: {page}")
        
        try:
            url = f"{api.base_url}{page}"
            response = api.session.get(url, timeout=15)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Look for Dennis in various ways
                dennis_patterns = [
                    r'dennis[^<]*rost',
                    r'rost[^<]*dennis', 
                    r'DENNIS[^<]*ROST',
                    r'ROST[^<]*DENNIS',
                    r'65828815',  # His ClubHub ID
                    r'96530079',  # His agreement ID from CSV
                    r'31489560'   # His user ID from CSV
                ]
                
                found_matches = []
                
                for pattern in dennis_patterns:
                    matches = re.finditer(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        # Get context around the match
                        start = max(0, match.start() - 100)
                        end = min(len(html_content), match.end() + 100)
                        context = html_content[start:end]
                        found_matches.append((pattern, context))
                
                if found_matches:
                    print(f"   🎯 DENNIS FOUND in {page}!")
                    for pattern, context in found_matches:
                        print(f"   Pattern '{pattern}':")
                        print(f"      ...{context.strip()}...")
                        print()
                else:
                    print(f"   ❌ Dennis not found in {page}")
                    
                # Also look for any member lists, tables, or data structures
                if 'table' in html_content.lower() or 'client' in html_content.lower():
                    print(f"   📊 Page contains tables/client data")
                    
                    # Look for JavaScript data or AJAX endpoints
                    js_data_patterns = [
                        r'var\s+\w+\s*=\s*(\[.*?\]);',
                        r'data\s*:\s*(\[.*?\])',
                        r'members\s*:\s*(\[.*?\])',
                        r'clients\s*:\s*(\[.*?\])',
                        r'url\s*:\s*["\']([^"\']*api[^"\']*)["\']'
                    ]
                    
                    for pattern in js_data_patterns:
                        matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            print(f"   📄 Found JS data pattern: {match.group(0)[:100]}...")
                            
                            # Check if Dennis is in this data
                            if 'dennis' in match.group(0).lower() or 'rost' in match.group(0).lower():
                                print(f"   🎯 DENNIS FOUND in JS data!")
                                print(f"      {match.group(0)}")
                
            else:
                print(f"   ❌ {page}: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Error checking {page}: {e}")
    
    # Try to access the training client list directly
    print(f"\n🔍 TRYING TO ACCESS TRAINING CLIENT LIST DIRECTLY")
    
    try:
        # The TrainingClients page might have an AJAX endpoint to load data
        training_clients_url = f"{api.base_url}/action/TrainingClients/view"
        response = api.session.get(training_clients_url, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            
            # Look for AJAX endpoints in the page
            ajax_patterns = [
                r'ajax.*?url.*?["\']([^"\']+)["\']',
                r'fetch\(["\']([^"\']+)["\']',
                r'\.get\(["\']([^"\']+)["\']',
                r'DataTable.*?ajax.*?["\']([^"\']+)["\']'
            ]
            
            ajax_endpoints = set()
            for pattern in ajax_patterns:
                matches = re.finditer(pattern, html, re.IGNORECASE)
                for match in matches:
                    endpoint = match.group(1)
                    if '/action/' in endpoint or '/api/' in endpoint:
                        ajax_endpoints.add(endpoint)
            
            print(f"   Found {len(ajax_endpoints)} potential AJAX endpoints:")
            for endpoint in ajax_endpoints:
                print(f"      {endpoint}")
                
                # Try to call these endpoints
                try:
                    if endpoint.startswith('/'):
                        full_url = f"{api.base_url}{endpoint}"
                    else:
                        full_url = endpoint
                        
                    ajax_response = api.session.get(full_url, timeout=10)
                    
                    if ajax_response.status_code == 200:
                        print(f"      ✅ {endpoint}: Success")
                        
                        # Check if it returns JSON with training clients
                        try:
                            if ajax_response.headers.get('content-type', '').startswith('application/json'):
                                data = ajax_response.json()
                                print(f"         📊 JSON data: {len(data) if isinstance(data, list) else 'dict'}")
                                
                                # Look for Dennis in the JSON
                                data_str = str(data).lower()
                                if 'dennis' in data_str or 'rost' in data_str:
                                    print(f"         🎯 DENNIS FOUND!")
                                    print(f"         {data}")
                                    
                        except:
                            print(f"         📄 Non-JSON response")
                            
                    else:
                        print(f"      ❌ {endpoint}: {ajax_response.status_code}")
                        
                except Exception as e:
                    print(f"      ⚠️ {endpoint}: {e}")
                    
    except Exception as e:
        print(f"   ❌ Training client list access failed: {e}")

if __name__ == "__main__":
    check_training_pages_for_dennis()
