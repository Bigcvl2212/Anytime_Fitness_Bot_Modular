#!/usr/bin/env python3
"""
Debug the raw response from the bare list method to see what we're actually getting
"""

import sys
import json
import logging
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_bare_list_response():
    """Debug what the bare list method actually returns"""
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    logger.info("✅ Authentication successful")
    
    # Use the exact member ID from HAR where the request worked
    test_member_id = "191215290"  # From your HAR cookies
    
    logger.info(f"🔍 Debug: Checking raw bare list response for member {test_member_id}")
    
    # Step 1: Delegate to member
    delegation_success = api.delegate_to_member(test_member_id)
    logger.info(f"🔑 Delegation: {'✅ Success' if delegation_success else '❌ Failed'}")
    
    if not delegation_success:
        logger.error("❌ Cannot proceed without delegation")
        return
    
    # Step 2: Make the raw bare list call and capture EVERYTHING
    url = f"{api.base_url}/api/agreements/package_agreements/list"
    
    logger.info(f"🌐 Making RAW request to: {url}")
    raw_response = api.session.get(url, timeout=20)
    
    logger.info(f"📊 Raw Response Status: {raw_response.status_code}")
    logger.info(f"📊 Raw Response Headers: {dict(raw_response.headers)}")
    
    if raw_response.status_code == 200:
        raw_text = raw_response.text
        logger.info(f"📊 Raw Response Length: {len(raw_text)}")
        
        # Save the full raw response
        with open('debug_bare_list_raw_response.json', 'w', encoding='utf-8') as f:
            f.write(raw_text)
        logger.info("💾 Saved raw response to debug_bare_list_raw_response.json")
        
        try:
            data = raw_response.json()
            logger.info(f"📊 JSON Data Type: {type(data)}")
            
            if isinstance(data, list):
                logger.info(f"📊 List Length: {len(data)}")
                
                # Show structure of each agreement
                for i, agreement in enumerate(data):
                    logger.info(f"📋 Agreement {i+1}:")
                    logger.info(f"  Type: {type(agreement)}")
                    
                    if isinstance(agreement, dict):
                        # Show all keys in the agreement
                        logger.info(f"  Keys: {list(agreement.keys())}")
                        
                        # Show critical fields
                        agreement_id = agreement.get('id')
                        name = agreement.get('name', agreement.get('agreementName', 'Unknown'))
                        status = agreement.get('status', agreement.get('agreementStatus', 'Unknown'))
                        
                        logger.info(f"  ID: {agreement_id}")
                        logger.info(f"  Name: {name}")
                        logger.info(f"  Status: {status}")
                        
                        # Check if 1672118 is present
                        if str(agreement_id) == "1672118":
                            logger.info("🎯 FOUND 1672118! Full agreement data:")
                            logger.info(json.dumps(agreement, indent=2)[:1000] + "...")
                        
                        # Show a sample of the full agreement structure
                        if i == 0:
                            logger.info(f"📋 Sample Agreement Structure:")
                            sample_json = json.dumps(agreement, indent=2)[:2000]
                            logger.info(sample_json + ("..." if len(sample_json) >= 2000 else ""))
                    else:
                        logger.info(f"  Value: {agreement}")
            
            elif isinstance(data, dict):
                logger.info(f"📊 Dict Keys: {list(data.keys())}")
                logger.info(f"📋 Full Dict Structure:")
                logger.info(json.dumps(data, indent=2)[:1000] + "...")
                
            else:
                logger.info(f"📊 Raw Data: {data}")
                
        except Exception as json_error:
            logger.error(f"❌ JSON parsing failed: {json_error}")
            logger.info(f"📊 Raw Text Preview: {raw_text[:500]}")
    
    else:
        logger.error(f"❌ Request failed: {raw_response.status_code}")
        logger.error(f"Response: {raw_response.text[:500]}")

if __name__ == "__main__":
    debug_bare_list_response()