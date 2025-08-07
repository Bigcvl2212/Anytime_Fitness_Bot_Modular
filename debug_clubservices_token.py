import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI
import re

def debug_clubservices_page():
    """Debug the ClubServicesNew page to see how the access token is embedded"""
    print("🔍 DEBUGGING CLUBSERVICES PAGE")
    print("=" * 50)
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ ClubOS authentication failed")
        return
    
    try:
        # Load ClubServicesNew page
        clubservices_url = f"{api.base_url}/action/ClubServicesNew"
        
        clubservices_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Referer': f'{api.base_url}/action/Dashboard/view'
        }
        
        response = api.session.get(clubservices_url, headers=clubservices_headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to load ClubServicesNew page: {response.status_code}")
            return
            
        page_html = response.text
        print(f"✅ Loaded ClubServicesNew page ({len(page_html)} chars)")
        
        # Search for different ACCESS_TOKEN patterns
        print("\n🔍 Searching for ACCESS_TOKEN patterns...")
        
        # Pattern 1: var ACCESS_TOKEN = "..."
        pattern1 = re.search(r'var\s+ACCESS_TOKEN\s*=\s*["\']([^"\']+)["\']', page_html)
        if pattern1:
            print(f"✅ Found pattern 1: var ACCESS_TOKEN = \"{pattern1.group(1)[:50]}...\"")
        else:
            print("❌ Pattern 1 not found: var ACCESS_TOKEN = \"...\"")
        
        # Pattern 2: ACCESS_TOKEN: "..."
        pattern2 = re.search(r'ACCESS_TOKEN\s*:\s*["\']([^"\']+)["\']', page_html)
        if pattern2:
            print(f"✅ Found pattern 2: ACCESS_TOKEN: \"{pattern2.group(1)[:50]}...\"")
        else:
            print("❌ Pattern 2 not found: ACCESS_TOKEN: \"...\"")
        
        # Pattern 3: window.ACCESS_TOKEN = "..."
        pattern3 = re.search(r'window\.ACCESS_TOKEN\s*=\s*["\']([^"\']+)["\']', page_html)
        if pattern3:
            print(f"✅ Found pattern 3: window.ACCESS_TOKEN = \"{pattern3.group(1)[:50]}...\"")
        else:
            print("❌ Pattern 3 not found: window.ACCESS_TOKEN = \"...\"")
        
        # Pattern 4: accessToken: "..."
        pattern4 = re.search(r'accessToken\s*:\s*["\']([^"\']+)["\']', page_html)
        if pattern4:
            print(f"✅ Found pattern 4: accessToken: \"{pattern4.group(1)[:50]}...\"")
        else:
            print("❌ Pattern 4 not found: accessToken: \"...\"")
            
        # Pattern 5: Look for Bearer tokens directly
        pattern5 = re.search(r'Bearer\s+([A-Za-z0-9\.\-_]+)', page_html)
        if pattern5:
            print(f"✅ Found pattern 5: Bearer {pattern5.group(1)[:50]}...")
        else:
            print("❌ Pattern 5 not found: Bearer tokens")
            
        # Pattern 6: Look for JWT tokens (eyJ...)
        pattern6 = re.search(r'["\']?(eyJ[A-Za-z0-9\.\-_]+)["\']?', page_html)
        if pattern6:
            print(f"✅ Found pattern 6: JWT token {pattern6.group(1)[:50]}...")
        else:
            print("❌ Pattern 6 not found: JWT tokens")
        
        # Search for any script tag with token-like content
        print("\n🔍 Searching for script tags with token content...")
        script_tags = re.findall(r'<script[^>]*>(.*?)</script>', page_html, re.DOTALL)
        
        for i, script in enumerate(script_tags):
            if 'token' in script.lower() or 'access' in script.lower() or 'bearer' in script.lower():
                print(f"\n📜 Script tag {i+1} with token content:")
                # Show first 500 chars of script
                script_preview = script.strip()[:500]
                print(f"   {script_preview}{'...' if len(script.strip()) > 500 else ''}")
                
        # Look for any hardcoded tokens in the HTML
        print("\n🔍 Looking for any hardcoded authorization tokens...")
        auth_patterns = [
            r'authorization["\']?\s*:\s*["\']Bearer\s+([^"\']+)["\']',
            r'Authorization["\']?\s*:\s*["\']Bearer\s+([^"\']+)["\']',
            r'headers[^}]*authorization[^}]*Bearer\s+([A-Za-z0-9\.\-_]+)',
            r'setRequestHeader\(["\']authorization["\'][^)]*Bearer\s+([A-Za-z0-9\.\-_]+)'
        ]
        
        for i, pattern in enumerate(auth_patterns):
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            if matches:
                print(f"✅ Found auth pattern {i+1}: {len(matches)} matches")
                for match in matches[:3]:  # Show first 3 matches
                    print(f"   Token: {match[:50]}...")
            else:
                print(f"❌ Auth pattern {i+1} not found")
        
        # Save the page for manual inspection
        with open('clubservices_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_html)
        print(f"\n💾 Saved page content to clubservices_debug.html for manual inspection")
        
    except Exception as e:
        print(f"❌ Error debugging ClubServices page: {e}")

if __name__ == "__main__":
    debug_clubservices_page()
