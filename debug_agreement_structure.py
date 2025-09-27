#!/usr/bin/env python3
"""
Debug script to examine the exact structure of package agreement responses
"""

import sys
import os
import json
import pprint

# Add the src directory to Python path for imports
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_agreement_structure():
    """Debug the exact structure of package agreement responses"""
    
    print("🔍 Debugging Package Agreement Response Structure")
    print("=" * 60)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    print("🔐 Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed!")
        return False
    
    print("✅ Authentication successful!")
    
    # Test member ID that we know has agreements
    member_id = '185777276'  # Grace Sphatt - had 2 agreements
    
    print(f"\n🧪 Testing member ID: {member_id}")
    print("-" * 30)
    
    try:
        # Step 1: Delegate to member
        if not api.delegate_to_member(member_id):
            print(f"❌ Failed to delegate to member {member_id}")
            return False
        
        print(f"✅ Successfully delegated to member {member_id}")
        
        # Step 2: Call the bare list endpoint
        url = f"{api.base_url}/api/agreements/package_agreements/list"
        print(f"🔍 Calling: {url}")
        
        response = api.session.get(url, timeout=20)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📊 Response type: {type(data)}")
                print(f"📊 Response length: {len(data) if isinstance(data, (list, dict)) else 'N/A'}")
                
                print(f"\n🔍 RAW JSON RESPONSE:")
                print("=" * 40)
                print(json.dumps(data, indent=2, default=str))
                
                if isinstance(data, list) and data:
                    print(f"\n🔍 FIRST AGREEMENT STRUCTURE:")
                    print("=" * 40)
                    first_agreement = data[0]
                    print(f"Type: {type(first_agreement)}")
                    if isinstance(first_agreement, dict):
                        print("Keys in first agreement:")
                        for key, value in first_agreement.items():
                            print(f"  {key}: {type(value)} = {value}")
                    
                    if len(data) > 1:
                        print(f"\n🔍 SECOND AGREEMENT STRUCTURE:")
                        print("=" * 40)
                        second_agreement = data[1]
                        print(f"Type: {type(second_agreement)}")
                        if isinstance(second_agreement, dict):
                            print("Keys in second agreement:")
                            for key, value in second_agreement.items():
                                print(f"  {key}: {type(value)} = {value}")
                
                return True
                
            except Exception as json_error:
                print(f"❌ Failed to parse JSON: {json_error}")
                print(f"📄 Raw response text: {response.text}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"📄 Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    debug_agreement_structure()