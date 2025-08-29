#!/usr/bin/env python3
"""
BREAKTHROUGH TRAINING PACKAGES PROCESS
======================================

This script documents and replicates the EXACT working process that successfully 
retrieved Mark Benzinger's 13 training packages during the breakthrough discovery.

BREAKTHROUGH PROCESS TIMELINE:
1. Initial Issue: All training clients showing "No active packages"
2. Cookie Errors: Fixed CookieConflictError with duplicate 'delegatedUserId' cookies  
3. JavaScript Fix: Fixed ReferenceError in training_clients.html template
4. BREAKTHROUGH: Found working 6-step process for Mark Benzinger (GUID: 66082049)
5. Current State: GUID lookup working, but API calls failing with 500 server errors

THE WORKING 6-STEP PROCESS:
Step 1: GUID Lookup (✅ Working)
Step 2: Authentication (✅ Working) 
Step 3: Delegation (✅ Working)
Step 4: Agreement Discovery (❌ 500 Server Error)
Step 5: Agreement Processing (❌ Dependent on Step 4)  
Step 6: Invoice Analysis (❌ Dependent on Steps 4-5)

This script tests each step individually to isolate exactly where the process breaks.
"""

import sys
import time
import traceback
sys.path.append('.')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI
from src.config.clubos_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_breakthrough_process():
    """Test the complete breakthrough process step by step"""
    print("🚀 BREAKTHROUGH TRAINING PACKAGES PROCESS")
    print("="*50)
    
    # Test Member: Mark Benzinger (known to have 13 training packages)
    test_member_id = "125814462"  # ClubOS Member ID
    expected_guid = "66082049"    # Known GUID from breakthrough
    
    print(f"📋 Testing Member: {test_member_id}")
    print(f"📋 Expected GUID: {expected_guid}")
    print()
    
    try:
        # STEP 1: GUID LOOKUP
        print("🔍 STEP 1: GUID LOOKUP")
        print("-" * 20)
        
        # Test the EXACT GUID lookup process used in Flask app
        import sqlite3
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # BREAKTHROUGH STRATEGY 1: Direct GUID lookup by clubos_member_id from training_clients
        cursor.execute('SELECT member_name FROM training_clients WHERE clubos_member_id = ?', (test_member_id,))
        training_result = cursor.fetchone()
        
        if training_result:
            member_name = training_result[0]
            print(f"✅ Found training client: {member_name} for clubos_member_id: {test_member_id}")
            
            # Now find the GUID in members table by name
            cursor.execute('SELECT guid FROM members WHERE full_name = ?', (member_name,))
            guid_result = cursor.fetchone()
            
            if guid_result:
                guid = guid_result[0]
                print(f"✅ STEP 1 SUCCESS: Found GUID {guid} for member {member_name}")
                
                if str(guid) == expected_guid:
                    print(f"✅ GUID MATCHES expected value: {expected_guid}")
                else:
                    print(f"⚠️ GUID MISMATCH: Got {guid}, expected {expected_guid}")
            else:
                print(f"❌ No GUID found in members table for name: {member_name}")
                conn.close()
                return False
        else:
            print(f"❌ STEP 1 FAILED: No training client found for clubos_member_id: {test_member_id}")
            conn.close()
            return False
            
        conn.close()
        
        # STEP 2: AUTHENTICATION  
        print(f"\n🔐 STEP 2: AUTHENTICATION")
        print("-" * 20)
        
        api = ClubOSTrainingPackageAPI()
        api.username = CLUBOS_USERNAME
        api.password = CLUBOS_PASSWORD
        
        print(f"📋 Using credentials: {CLUBOS_USERNAME[:3]}*** / {len(CLUBOS_PASSWORD)} chars")
        
        auth_result = api.authenticate()
        if auth_result:
            print("✅ STEP 2 SUCCESS: ClubOS Authentication successful")
            print(f"✅ Session cookies: {list(api.session.cookies.keys())}")
        else:
            print("❌ STEP 2 FAILED: Authentication failed")
            return False
            
        # STEP 3: DELEGATION
        print(f"\n👤 STEP 3: DELEGATION")
        print("-" * 20)
        
        # Clear any existing delegation cookies to prevent conflicts
        cookies_to_remove = []
        for cookie in api.session.cookies:
            if cookie.name in ['delegatedUserId', 'staffDelegatedUserId']:
                cookies_to_remove.append((cookie.name, cookie.domain, cookie.path))
        
        for name, domain, path in cookies_to_remove:
            api.session.cookies.clear(domain, path, name)
            
        delegate_result = api.delegate_to_member(guid)
        if delegate_result:
            print(f"✅ STEP 3 SUCCESS: Delegated to member GUID: {guid}")
            # Safe cookie logging
            delegation_cookies = []
            for cookie in api.session.cookies:
                if cookie.name == 'delegatedUserId':
                    delegation_cookies.append(cookie.value)
            print(f"✅ Delegation cookies: {delegation_cookies}")
        else:
            print(f"❌ STEP 3 FAILED: Delegation to GUID {guid} failed")
            return False
            
        # STEP 4: AGREEMENT DISCOVERY (The breaking point)
        print(f"\n📋 STEP 4: AGREEMENT DISCOVERY")
        print("-" * 20)
        
        print("🧪 Testing direct /list endpoint (the failing method):")
        
        # Test the exact API call that's failing
        timestamp = int(time.time() * 1000)
        api_headers = api._auth_headers(referer=f'{api.base_url}/action/PackageAgreementUpdated/spa/')
        api_headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        })

        list_url = f"{api.base_url}/api/agreements/package_agreements/list"
        params = {
            'memberId': guid,  # Use the GUID as memberId parameter  
            '_': timestamp
        }
        
        print(f"🌐 API URL: {list_url}")
        print(f"📋 Headers: {dict(api_headers)}")
        print(f"📋 Params: {params}")
        
        response = api.session.get(list_url, headers=api_headers, params=params, timeout=15)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Response Body: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                agreements_data = response.json()
                print(f"✅ STEP 4 SUCCESS: API returned {len(agreements_data) if isinstance(agreements_data, list) else 'non-list'} agreements")
                print(f"📋 Agreements data: {agreements_data}")
                
                if isinstance(agreements_data, list) and agreements_data:
                    # Extract agreement IDs
                    agreement_ids = []
                    for agreement in agreements_data:
                        if isinstance(agreement, dict) and 'id' in agreement:
                            agreement_ids.append(agreement['id'])
                        elif isinstance(agreement, (str, int)):
                            agreement_ids.append(str(agreement))
                    
                    print(f"📋 Extracted Agreement IDs: {agreement_ids}")
                    
                    if agreement_ids:
                        # STEP 5: AGREEMENT PROCESSING
                        print(f"\n📦 STEP 5: AGREEMENT PROCESSING")
                        print("-" * 20)
                        
                        package_names = []
                        total_past_due = 0.0
                        
                        for i, agreement_id in enumerate(agreement_ids[:3], 1):  # Test first 3 only
                            print(f"📦 Processing Agreement {i}: {agreement_id}")
                            
                            # Re-delegate to ensure session state
                            api.delegate_to_member(guid)
                            
                            # V2 API call for agreement details
                            detail_url = f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
                            detail_params = {
                                'include': 'invoices,scheduledPayments,prohibitChangeTypes',
                                '_': timestamp
                            }
                            
                            detail_response = api.session.get(detail_url, headers=api_headers, params=detail_params, timeout=15)
                            
                            if detail_response.status_code == 200:
                                response_json = detail_response.json()
                                detail_data = response_json.get('data', {})
                                agreement_name = detail_data.get('name', f'Training Package {agreement_id}')
                                agreement_status = detail_data.get('agreementStatus', 0)
                                
                                print(f"   📋 Agreement: {agreement_name} (Status: {agreement_status})")
                                
                                # Only process active agreements (status 2 = active)
                                if agreement_status == 2:
                                    package_names.append(agreement_name)
                                    
                                    # STEP 6: INVOICE ANALYSIS
                                    include_data = response_json.get('include', {})
                                    invoices = include_data.get('invoices', [])
                                    
                                    past_due_amount = 0.0
                                    for invoice in invoices:
                                        invoice_status = invoice.get('invoiceStatus')
                                        if invoice_status == 5:  # Past due
                                            amount = float(invoice.get('total', 0))
                                            past_due_amount += amount
                                    
                                    total_past_due += past_due_amount
                                    print(f"   ✅ ACTIVE Package: {agreement_name}, ${past_due_amount} past due")
                                else:
                                    status_names = {1: "draft", 2: "active", 3: "pending", 4: "completed", 5: "canceled"}
                                    status_name = status_names.get(agreement_status, f"unknown({agreement_status})")
                                    print(f"   ⏭️ SKIPPING {status_name} package: {agreement_name}")
                            else:
                                print(f"   ❌ V2 API failed for {agreement_id}: {detail_response.status_code}")
                        
                        # FINAL RESULTS
                        print(f"\n🎯 BREAKTHROUGH RESULTS:")
                        print(f"✅ Member: {test_member_id} (GUID: {guid})")
                        print(f"✅ Total Agreements Found: {len(agreement_ids)}")
                        print(f"✅ Active Packages: {len(package_names)}")
                        print(f"✅ Package Names: {package_names}")
                        print(f"✅ Total Past Due: ${total_past_due}")
                        
                        if len(package_names) == 13:
                            print("🎉 SUCCESS: Found the expected 13 packages for Mark Benzinger!")
                        else:
                            print(f"⚠️ Expected 13 packages, found {len(package_names)}")
                            
                        return True
                    else:
                        print("❌ STEP 4 FAILED: No agreement IDs could be extracted")
                        return False
                else:
                    print("❌ STEP 4 FAILED: Empty or invalid agreements data")
                    return False
                    
            except Exception as json_error:
                print(f"❌ STEP 4 FAILED: JSON parsing error: {json_error}")
                return False
        else:
            print(f"❌ STEP 4 FAILED: API returned {response.status_code}")
            print(f"❌ Error Response: {response.text}")
            
            # This is the current breaking point - 500 server error
            if response.status_code == 500:
                print("🚨 CRITICAL: ClubOS server returning 500 error for /list endpoint")
                print("🚨 This is the exact point where the breakthrough process is breaking")
            
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION in breakthrough process: {e}")
        traceback.print_exc()
        return False

def test_alternative_discovery_methods():
    """Test alternative methods for agreement discovery"""
    print(f"\n🔬 TESTING ALTERNATIVE DISCOVERY METHODS")
    print("="*50)
    
    try:
        api = ClubOSTrainingPackageAPI()
        api.username = CLUBOS_USERNAME
        api.password = CLUBOS_PASSWORD
        
        if not api.authenticate():
            print("❌ Authentication failed for alternative methods")
            return
            
        guid = "66082049"
        api.delegate_to_member(guid)
        
        # Test Method 1: Direct member agreements endpoint
        print("🧪 Method 1: /api/members/{guid}/agreements/package")
        member_url = f"{api.base_url}/api/members/{guid}/agreements/package"
        headers = {
            'User-Agent': api.session.headers.get('User-Agent', 'Mozilla/5.0'),
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'{api.base_url}/action/Dashboard/',
        }
        
        response = api.session.get(member_url, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Success: {len(data) if isinstance(data, list) else 'non-list'} agreements")
                print(f"   Data: {data}")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Failed: {response.text[:200]}...")
            
        # Test Method 2: Training clients endpoint
        print("\n🧪 Method 2: /api/training/clients")
        training_url = f"{api.base_url}/api/training/clients"
        response = api.session.get(training_url, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    # Look for this member in training clients
                    for client in data:
                        if str(client.get('memberId')) == guid or str(client.get('id')) == guid:
                            print(f"   ✅ Found member in training clients!")
                            print(f"   Client data: {client}")
                            break
                    else:
                        print(f"   ⚠️ Member not found in {len(data)} training clients")
                else:
                    print(f"   ⚠️ Unexpected response format: {type(data)}")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Failed: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error in alternative methods: {e}")

if __name__ == "__main__":
    print("🚀 STARTING BREAKTHROUGH TRAINING PACKAGES TEST")
    print("This script replicates the EXACT process that worked for Mark Benzinger")
    print()
    
    # Test the main breakthrough process
    success = test_breakthrough_process()
    
    if not success:
        print("\n🔬 Main process failed, testing alternative methods...")
        test_alternative_discovery_methods()
    
    print(f"\n📋 BREAKTHROUGH PROCESS COMPLETE")
    print("="*50)
