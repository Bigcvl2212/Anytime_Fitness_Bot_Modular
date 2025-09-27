#!/usr/bin/env python3
"""
Test different V2 endpoint approaches to match the working HAR exactly
"""

import sys
import json
import logging
import time
from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_v2_endpoint_variations():
    """Test V2 endpoint with different header combinations to match HAR exactly"""
    api = ClubOSTrainingPackageAPI()
    
    # Authenticate and delegate
    if not api.authenticate():
        logger.error("❌ Authentication failed")
        return
    
    test_member_id = "191215290"
    test_agreement_id = "1672118"
    
    # Must delegate first
    if not api.delegate_to_member(test_member_id):
        logger.error("❌ Delegation failed")
        return
    
    # Test different V2 endpoint approaches
    timestamp = int(time.time() * 1000)
    base_url = api.base_url
    url = f"{base_url}/api/agreements/package_agreements/V2/{test_agreement_id}"
    
    # Get bearer token
    bearer = api._get_bearer_token()
    logger.info(f"🔑 Bearer token available: {'✅ Yes' if bearer else '❌ No'}")
    
    variations = [
        {
            "name": "Exact HAR Headers",
            "params": [
                ('include', 'invoices'),
                ('include', 'scheduledPayments'), 
                ('include', 'prohibitChangeTypes'),
                ('_', timestamp)
            ],
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Priority': 'u=1, i',
                'Referer': f'{base_url}/action/PackageAgreementUpdated/spa/',
                'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
            }
        },
        {
            "name": "HAR with Fragment Referer",
            "params": [
                ('include', 'invoices'),
                ('include', 'scheduledPayments'), 
                ('include', 'prohibitChangeTypes'),
                ('_', timestamp)
            ],
            "headers": {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{base_url}/action/PackageAgreementUpdated/spa/#/package-agreements/{test_agreement_id}',
            }
        },
        {
            "name": "Simple Working Headers",
            "params": [
                ('include', 'invoices'),
                ('include', 'scheduledPayments'), 
                ('include', 'prohibitChangeTypes'),
                ('_', timestamp)
            ],
            "headers": {
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{base_url}/action/PackageAgreementUpdated/spa/',
            }
        }
    ]
    
    for i, variation in enumerate(variations, 1):
        logger.info(f"🧪 Test {i}: {variation['name']}")
        
        headers = variation['headers'].copy()
        if bearer:
            headers['Authorization'] = f'Bearer {bearer}'
        
        try:
            response = api.session.get(url, params=variation['params'], headers=headers, timeout=20)
            
            logger.info(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ SUCCESS! V2 endpoint worked!")
                try:
                    data = response.json()
                    include_data = data.get('include', {})
                    invoices = include_data.get('invoices', [])
                    
                    logger.info(f"📋 Retrieved {len(invoices)} invoices")
                    
                    # Save the successful response
                    with open(f'v2_success_{i}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    logger.info(f"💾 Saved successful response to v2_success_{i}.json")
                    
                    return data  # Return on first success
                    
                except Exception as e:
                    logger.error(f"❌ JSON parsing failed: {e}")
            else:
                logger.error(f"❌ HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
    
    logger.error("❌ All V2 variations failed")

def test_navigation_flow():
    """Test navigating to the SPA page first like a real browser would"""
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        return
    
    test_member_id = "191215290"  
    test_agreement_id = "1672118"
    
    logger.info("🌐 Testing browser-like navigation flow...")
    
    # Step 1: Navigate to SPA page first
    spa_url = f"{api.base_url}/action/PackageAgreementUpdated/spa/"
    logger.info(f"🌐 Step 1: Navigating to SPA page: {spa_url}")
    
    try:
        spa_response = api.session.get(spa_url, timeout=20)
        logger.info(f"📊 SPA page status: {spa_response.status_code}")
        
        if spa_response.status_code == 200:
            logger.info(f"✅ SPA page loaded successfully")
            
            # Step 2: Delegate after SPA navigation
            if not api.delegate_to_member(test_member_id):
                logger.error("❌ Delegation failed")
                return
            
            # Step 3: Try V2 endpoint after SPA navigation
            timestamp = int(time.time() * 1000)
            v2_url = f"{api.base_url}/api/agreements/package_agreements/V2/{test_agreement_id}"
            
            params = [
                ('include', 'invoices'),
                ('include', 'scheduledPayments'), 
                ('include', 'prohibitChangeTypes'),
                ('_', timestamp)
            ]
            
            headers = {
                'User-Agent': api.session.headers.get('User-Agent', 'Mozilla/5.0'),
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': spa_url,
            }
            
            bearer = api._get_bearer_token()
            if bearer:
                headers['Authorization'] = f'Bearer {bearer}'
            
            logger.info("🔍 Step 3: Testing V2 endpoint after SPA navigation...")
            v2_response = api.session.get(v2_url, params=params, headers=headers, timeout=20)
            
            logger.info(f"📊 V2 after SPA status: {v2_response.status_code}")
            
            if v2_response.status_code == 200:
                logger.info("✅ SUCCESS! V2 worked after SPA navigation!")
                try:
                    data = v2_response.json()
                    with open('v2_success_after_spa.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    logger.info("💾 Saved to v2_success_after_spa.json")
                except Exception as e:
                    logger.error(f"❌ JSON parsing failed: {e}")
            else:
                logger.error(f"❌ V2 after SPA failed: {v2_response.status_code} - {v2_response.text[:200]}")
        else:
            logger.error(f"❌ SPA page failed: {spa_response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Navigation flow failed: {e}")

if __name__ == "__main__":
    logger.info("🧪 Testing V2 endpoint variations...")
    test_v2_endpoint_variations()
    
    logger.info("\n🌐 Testing navigation flow...")
    test_navigation_flow()