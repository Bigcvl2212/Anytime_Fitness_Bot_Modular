#!/usr/bin/env python3
"""
Fix Training Clients Past Due - Get REAL billing data from ClubOS Agreements
This script fetches actual past due amounts from agreement billing data
"""

import json
import re
from datetime import datetime
from clubos_training_api import ClubOSTrainingPackageAPI
from src.services.database_manager import DatabaseManager

def main():
    print("=" * 60)
    print("FETCHING REAL PAST DUE DATA FROM CLUBOS AGREEMENTS")
    print("=" * 60)
    
    # Initialize
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate with ClubOS")
        return
    
    db = DatabaseManager()
    
    # Get all training clients from database
    clients = db.execute_query(
        "SELECT id, member_name, clubos_member_id, prospect_id, past_due_amount, total_past_due, payment_status, agreement_id FROM training_clients ORDER BY member_name",
        fetch_all=True
    )
    
    print(f"\n📋 Found {len(clients)} training clients in database\n")
    
    # For each client, fetch their REAL billing data from ClubOS
    updates = []
    
    for client in clients:
        client_dict = dict(client)
        name = client_dict.get('member_name', 'Unknown')
        member_id = client_dict.get('clubos_member_id') or client_dict.get('prospect_id')
        db_id = client_dict['id']
        current_past_due = client_dict.get('past_due_amount', 0) or 0
        current_total_past_due = client_dict.get('total_past_due', 0) or 0
        current_status = client_dict.get('payment_status', '')
        
        if not member_id:
            print(f"⚠️  {name}: No ClubOS member ID - skipping")
            continue
        
        print(f"\n🔍 Checking {name} (ID: {member_id})...")
        
        # Get their agreements with billing data
        try:
            result = fetch_agreement_billing(api, member_id, name)
            
            if result:
                total_past_due = result.get('total_past_due', 0)
                is_past_due = result.get('is_past_due', False)
                agreement_ids = result.get('agreement_ids', [])
                billing_details = result.get('billing_details', [])
                
                new_status = 'Past Due' if is_past_due else 'Current'
                
                # Show what we found
                if is_past_due or total_past_due > 0:
                    print(f"   💰 PAST DUE: ${total_past_due:.2f}")
                    print(f"   📋 Agreements: {agreement_ids}")
                    for detail in billing_details:
                        print(f"      - Agreement {detail['agreement_id']}: ${detail['amount']:.2f} ({detail['status']})")
                else:
                    print(f"   ✅ CURRENT (no past due)")
                
                # Track update if changed
                if total_past_due != current_total_past_due or new_status != current_status:
                    updates.append({
                        'db_id': db_id,
                        'name': name,
                        'old_amount': current_total_past_due,
                        'new_amount': total_past_due,
                        'old_status': current_status,
                        'new_status': new_status,
                        'agreement_ids': agreement_ids
                    })
            else:
                print(f"   ⚠️  Could not fetch billing data")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary and update
    print("\n" + "=" * 60)
    print("SUMMARY OF CHANGES")
    print("=" * 60)
    
    if not updates:
        print("✅ No changes needed - database is already accurate")
        return
    
    print(f"\n📝 {len(updates)} clients need updates:\n")
    
    for upd in updates:
        old_str = f"${upd['old_amount']:.2f} ({upd['old_status']})" if upd['old_amount'] else upd['old_status']
        new_str = f"${upd['new_amount']:.2f} ({upd['new_status']})"
        print(f"   {upd['name']}: {old_str} → {new_str}")
    
    # Apply updates
    print("\n🔄 Applying updates to database...")
    
    for upd in updates:
        try:
            db.execute_query(
                """
                UPDATE training_clients 
                SET past_due_amount = ?,
                    total_past_due = ?,
                    payment_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (upd['new_amount'], upd['new_amount'], upd['new_status'], upd['db_id'])
            )
            print(f"   ✅ Updated {upd['name']}")
        except Exception as e:
            print(f"   ❌ Failed to update {upd['name']}: {e}")
    
    print("\n✅ Done!")
    
    # Final counts
    past_due_count = db.execute_query(
        "SELECT COUNT(*) FROM training_clients WHERE payment_status = 'Past Due' OR total_past_due > 0",
        fetch_one=True
    )
    print(f"\n📊 Training clients now showing past due: {past_due_count[0] if past_due_count else 0}")


def fetch_agreement_billing(api, member_id, member_name):
    """Fetch real billing data from ClubOS agreements for a member"""
    
    import time
    
    # Get a delegated token for this member
    delegated_token = api._get_delegated_token(str(member_id))
    
    if not delegated_token:
        # Try with session token
        delegated_token = api.access_token
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Authorization': f'Bearer {delegated_token}' if delegated_token else '',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    timestamp = int(time.time() * 1000)
    base_url = api.base_url
    
    # First: Get list of agreements for this member
    agreement_ids = []
    
    # Try the Agreements page for this member
    try:
        ag_page_url = f"{base_url}/action/Agreements?memberId={member_id}"
        ag_resp = api.session.get(ag_page_url, timeout=15)
        if ag_resp.status_code == 200:
            # Parse agreement IDs from the page
            html = ag_resp.text
            # Look for agreement links like /action/Agreement/12345 or data-agreement-id="12345"
            patterns = [
                r'/action/Agreement/(\d+)',
                r'data-agreement-id="(\d+)"',
                r'"agreementId"\s*:\s*(\d+)',
                r'"id"\s*:\s*(\d+).*?"type"\s*:\s*"Package',
            ]
            for pat in patterns:
                matches = re.findall(pat, html)
                for m in matches:
                    if m and m not in agreement_ids:
                        agreement_ids.append(m)
    except Exception as e:
        print(f"      Error getting agreements page: {e}")
    
    # Try API endpoints
    api_endpoints = [
        f"/api/agreements/package_agreements/list?memberId={member_id}",
        f"/api/agreements/package_agreements?memberId={member_id}",
        f"/api/members/{member_id}/agreements",
    ]
    
    for endpoint in api_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            resp = api.session.get(url, headers=headers, params={'_': timestamp}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                agreements = []
                if isinstance(data, list):
                    agreements = data
                elif isinstance(data, dict):
                    agreements = data.get('agreements', []) or data.get('data', []) or []
                
                for ag in agreements:
                    ag_id = str(ag.get('id') or ag.get('agreementId') or ag.get('agreement_id', ''))
                    if ag_id and ag_id not in agreement_ids:
                        agreement_ids.append(ag_id)
        except Exception:
            continue
    
    if not agreement_ids:
        return None
    
    # Now get billing status for each agreement
    total_past_due = 0
    is_past_due = False
    billing_details = []
    
    for ag_id in agreement_ids[:5]:  # Limit to first 5 agreements
        try:
            # Get billing status
            billing_url = f"{base_url}/api/agreements/package_agreements/{ag_id}/billing_status"
            billing_resp = api.session.get(billing_url, headers=headers, params={'_': timestamp}, timeout=10)
            
            if billing_resp.status_code == 200:
                billing_data = billing_resp.json()
                
                # Check for past due items
                past_items = []
                if isinstance(billing_data, dict):
                    past_items = billing_data.get('past', []) or billing_data.get('pastDue', [])
                
                if past_items:
                    is_past_due = True
                    # Sum up past due amounts
                    for item in past_items:
                        amount = 0
                        for key in ['amount', 'amountDue', 'balance', 'pastDueAmount']:
                            if key in item:
                                try:
                                    amount = float(item[key])
                                    break
                                except:
                                    pass
                        total_past_due += amount
                        billing_details.append({
                            'agreement_id': ag_id,
                            'amount': amount,
                            'status': 'Past Due',
                            'raw': item
                        })
                else:
                    billing_details.append({
                        'agreement_id': ag_id,
                        'amount': 0,
                        'status': 'Current'
                    })
                    
            # Also try to get the agreement details page for more info
            try:
                ag_detail_url = f"{base_url}/action/Agreement/{ag_id}"
                ag_detail_resp = api.session.get(ag_detail_url, timeout=10)
                if ag_detail_resp.status_code == 200:
                    html = ag_detail_resp.text
                    # Look for past due amount in the page
                    patterns = [
                        r'pastDue["\s:]+\$?([\d,]+\.?\d*)',
                        r'past due["\s:]+\$?([\d,]+\.?\d*)',
                        r'amount due["\s:]+\$?([\d,]+\.?\d*)',
                        r'balance["\s:]+\$?([\d,]+\.?\d*)',
                    ]
                    for pat in patterns:
                        match = re.search(pat, html, re.IGNORECASE)
                        if match:
                            try:
                                amt = float(match.group(1).replace(',', ''))
                                if amt > 0:
                                    is_past_due = True
                                    # Only add if not already counted
                                    if amt > total_past_due:
                                        total_past_due = amt
                            except:
                                pass
            except:
                pass
                
        except Exception as e:
            print(f"      Error checking agreement {ag_id}: {e}")
            continue
    
    return {
        'agreement_ids': agreement_ids,
        'total_past_due': total_past_due,
        'is_past_due': is_past_due,
        'billing_details': billing_details
    }


if __name__ == "__main__":
    main()
