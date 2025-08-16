#!/usr/bin/env python3
"""
Simple test script to debug ClubOS package agreement parsing
"""

import requests
import logging
from bs4 import BeautifulSoup
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def test_clubos_agreement_endpoint():
    """Test ClubOS agreement endpoint directly"""
    
    print("🧪 Testing ClubOS Agreement Endpoint")
    print("=" * 50)
    
    # We need to authenticate first
    session = requests.Session()
    
    # ClubOS login URL
    login_url = "https://anytime.club-os.com/action/Login"
    
    # Login credentials (from config)
    try:
        from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
        username = CLUBOS_USERNAME
        password = CLUBOS_PASSWORD
    except ImportError:
        print("❌ Could not import ClubOS credentials")
        return
    
    print(f"🔐 Authenticating with ClubOS...")
    
    # Login payload
    login_data = {
        'username': username,
        'password': password
    }
    
    # Perform login
    login_response = session.post(login_url, data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed with status {login_response.status_code}")
        return
    
    print("✅ ClubOS authentication successful")
    
    # Now test the agreement endpoint with a known member ID
    test_member_id = "189425730"  # Dennis Rost
    agreement_url = f"https://anytime.club-os.com/action/Agreements?memberId={test_member_id}"
    
    print(f"🔍 Fetching agreements for member {test_member_id}...")
    print(f"URL: {agreement_url}")
    
    # Fetch the agreement page
    agreement_response = session.get(agreement_url)
    
    print(f"📥 Response status: {agreement_response.status_code}")
    print(f"📄 Response length: {len(agreement_response.text)} characters")
    
    if agreement_response.status_code == 200:
        # Parse with BeautifulSoup
        soup = BeautifulSoup(agreement_response.text, 'html.parser')
        
        print("\n🔍 Analyzing HTML content...")
        print("-" * 30)
        
        # Show first 500 characters of the response
        print(f"📄 First 500 characters:")
        print(agreement_response.text[:500])
        print("...")
        
        # Look for specific patterns that might indicate agreements
        tables = soup.find_all('table')
        print(f"\n📊 Found {len(tables)} table(s)")
        
        divs = soup.find_all('div')
        print(f"📊 Found {len(divs)} div(s)")
        
        # Look for common agreement-related terms
        agreement_terms = ['package', 'agreement', 'session', 'training', 'purchased', 'used', 'remaining']
        
        for term in agreement_terms:
            count = agreement_response.text.lower().count(term)
            if count > 0:
                print(f"🔍 Found '{term}': {count} times")
        
        # Check if it's an error page
        error_indicators = [
            "something isn't right",
            "please refresh",
            "error",
            "not found",
            "unauthorized"
        ]
        
        for indicator in error_indicators:
            if indicator.lower() in agreement_response.text.lower():
                print(f"⚠️ Error indicator found: '{indicator}'")
        
    else:
        print(f"❌ Failed to fetch agreements: {agreement_response.status_code}")
        print(f"Response: {agreement_response.text[:200]}...")

if __name__ == "__main__":
    test_clubos_agreement_endpoint()
