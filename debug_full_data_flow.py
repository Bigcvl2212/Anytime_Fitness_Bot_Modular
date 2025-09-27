#!/usr/bin/env python3
"""
DEBUG: Trace the ENTIRE data flow from breakthrough method to dashboard
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
from src.services.clubos_integration import ClubOSIntegration
from src.services.database_manager import DatabaseManager

def trace_full_data_flow():
    """Trace every step from API to database to dashboard"""
    
    print("=" * 80)
    print("TRACING FULL DATA FLOW: API → Integration → Database → Dashboard")
    print("=" * 80)
    
    # Test with Miguel who we KNOW is past due
    member_id = "177673765"  # Miguel Belmontes
    
    print(f"\n🔍 TRACING MEMBER: {member_id} (Miguel Belmontes)")
    print("📋 Expected: Past Due with ~$40.00 owed (billingState: 4)")
    
    # STEP 1: Test breakthrough method directly
    print(f"\n--- STEP 1: Breakthrough Method Direct ---")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Auth failed")
        return
    
    breakthrough_result = api.get_member_training_packages_breakthrough(member_id)
    
    if breakthrough_result.get('success'):
        packages = breakthrough_result.get('packages', [])
        print(f"✅ Breakthrough found {len(packages)} packages")
        
        total_past_due = 0
        for pkg in packages:
            agreement_id = pkg.get('agreement_id')
            payment_status = pkg.get('payment_status')
            amount_owed = pkg.get('amount_owed', 0)
            billing_state = pkg.get('billing_state')
            biweekly_amount = pkg.get('biweekly_amount', 0)
            
            print(f"  📦 Agreement {agreement_id}: {payment_status}, ${amount_owed:.2f} owed")
            print(f"      Billing State: {billing_state}, Biweekly: ${biweekly_amount:.2f}")
            
            if payment_status == 'Past Due':
                total_past_due += amount_owed
        
        print(f"💰 BREAKTHROUGH TOTAL PAST DUE: ${total_past_due:.2f}")
        
        if total_past_due == 0:
            print("🚨 PROBLEM: Breakthrough method shows $0 past due when should show ~$40!")
            print("🔍 Let's check the raw billing data...")
            
            # Check raw agreement data
            agreements_list = api.get_package_agreements_list(member_id)
            for agreement in agreements_list:
                agreement_id = agreement.get('packageAgreement', {}).get('id')
                billing_statuses = agreement.get('billingStatuses', {})
                current_billing = billing_statuses.get('current', {})
                billing_state = current_billing.get('billingState', 'NOT_SET')
                
                package_agreement = agreement.get('packageAgreement', {})
                services = package_agreement.get('packageAgreementMemberServices', [])
                
                print(f"    🔍 Raw Agreement {agreement_id}:")
                print(f"        Billing State: {billing_state}")
                print(f"        Services Count: {len(services)}")
                
                for service in services:
                    price = service.get('priceAfterDiscount', 0)
                    units = service.get('unitsPerBillingDuration', 0)
                    print(f"        Service: ${price} x {units} units = ${price * units}")
    else:
        print(f"❌ Breakthrough failed: {breakthrough_result.get('error')}")
        return
    
    # STEP 2: Test ClubOS Integration processing
    print(f"\n--- STEP 2: ClubOS Integration Processing ---")
    
    try:
        integration = ClubOSIntegration()
        
        # Test the sync method that processes breakthrough data
        sync_result = integration.sync_breakthrough_training_clients()
        
        print(f"✅ Integration sync completed")
        print(f"📊 Sync result keys: {list(sync_result.keys()) if isinstance(sync_result, dict) else 'Not a dict'}")
        
        if 'members_processed' in sync_result:
            print(f"👥 Members processed: {sync_result.get('members_processed', 0)}")
        
        if 'past_due_found' in sync_result:
            print(f"⚠️ Past due found: {sync_result.get('past_due_found', 0)}")
            
    except Exception as e:
        print(f"❌ Integration error: {e}")
    
    # STEP 3: Check database directly
    print(f"\n--- STEP 3: Database Direct Check ---")
    
    try:
        db = DatabaseManager()
        db.init_database()
        
        # Query training_clients table directly
        query = "SELECT * FROM training_clients WHERE member_id = ? OR name LIKE ?"
        results = db.execute_query(query, (member_id, '%Miguel%'))
        
        print(f"📊 Database query returned {len(results)} rows")
        
        for row in results:
            print(f"  📋 DB Row: ID={row.get('member_id')}, Name={row.get('name')}")
            print(f"      Status: {row.get('payment_status')}, Past Due: ${row.get('past_due_amount', 0):.2f}")
            print(f"      Total Past Due: ${row.get('total_past_due', 0):.2f}")
            print(f"      Last Updated: {row.get('last_updated')}")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # STEP 4: Test dashboard data source
    print(f"\n--- STEP 4: Dashboard Data Source ---")
    
    try:
        # This is what the dashboard calls
        dashboard_query = """
        SELECT tc.*, 
               COALESCE(tc.past_due_amount, 0) + COALESCE(tc.total_past_due, 0) as total_owed
        FROM training_clients tc 
        WHERE tc.payment_status = 'Past Due' 
        AND (COALESCE(tc.past_due_amount, 0) + COALESCE(tc.total_past_due, 0)) > 0
        ORDER BY total_owed DESC
        """
        
        dashboard_results = db.execute_query(dashboard_query)
        
        print(f"📊 Dashboard query returned {len(dashboard_results)} past due clients")
        
        for row in dashboard_results:
            name = row.get('name', 'Unknown')
            total_owed = row.get('total_owed', 0)
            print(f"  ⚠️ Past Due: {name} - ${total_owed:.2f}")
            
        if len(dashboard_results) == 0:
            print("🚨 DASHBOARD SHOWS 0 PAST DUE CLIENTS!")
            print("🔍 Let's check if Miguel is in the database at all...")
            
            all_miguel_query = "SELECT * FROM training_clients WHERE name LIKE '%Miguel%' OR member_id = ?"
            all_miguel = db.execute_query(all_miguel_query, (member_id,))
            
            print(f"📊 Found {len(all_miguel)} Miguel records in database:")
            for row in all_miguel:
                print(f"  📋 {row.get('name')}: Status={row.get('payment_status')}, Amount=${row.get('past_due_amount', 0):.2f}")
                
    except Exception as e:
        print(f"❌ Dashboard query error: {e}")
    
    print(f"\n{'='*80}")
    print("🔍 ANALYSIS SUMMARY:")
    print("1. Does breakthrough method return correct past due data?")
    print("2. Does integration process breakthrough data correctly?") 
    print("3. Does database contain correct past due amounts?")
    print("4. Does dashboard query find the past due clients?")
    print(f"{'='*80}")

if __name__ == "__main__":
    trace_full_data_flow()