#!/usr/bin/env python3
"""
Fix Dennis Rost's training client data using what we know
"""

import sqlite3
import sys
sys.path.append('.')

def fix_dennis_training_data():
    """Add Dennis to training_clients table with his known ClubOS data"""
    
    db_path = 'gym_bot.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("🔧 Fixing Dennis Rost's training client data...")
        
        # First, check if Dennis is already in training_clients
        cursor.execute("""
            SELECT * FROM training_clients 
            WHERE LOWER(member_name) LIKE '%dennis%' 
               OR LOWER(member_name) LIKE '%rost%'
        """)
        
        existing = cursor.fetchone()
        if existing:
            print("✅ Dennis already exists in training_clients table:")
            print(f"   {dict(existing)}")
            
            # Update with correct ClubOS ID if needed
            cursor.execute("""
                UPDATE training_clients 
                SET clubos_member_id = ?, 
                    package_name = ?,
                    funding_status = ?,
                    last_updated = datetime('now')
                WHERE LOWER(member_name) LIKE '%dennis%'
            """, ("189425730", "2025 1X1 Training", "Current"))
            
            conn.commit()
            print("✅ Updated Dennis's ClubOS member ID")
        else:
            print("📝 Adding Dennis to training_clients table...")
            
            # First, check the actual schema of training_clients table
            cursor.execute("PRAGMA table_info(training_clients)")
            columns = cursor.fetchall()
            print(f"   Training clients table columns: {[col[1] for col in columns]}")
            
            # Add Dennis with basic data (adjust based on actual schema)
            cursor.execute("""
                INSERT INTO training_clients (
                    member_name, 
                    clubos_member_id
                ) VALUES (?, ?)
            """, (
                "Dennis Rost",
                "189425730"  # His working ClubOS delegate ID
            ))
            
            conn.commit()
            print("✅ Dennis added to training_clients table successfully!")
        
        # Verify Dennis is now in the table
        cursor.execute("""
            SELECT * FROM training_clients 
            WHERE LOWER(member_name) LIKE '%dennis%'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"\n📋 Dennis's training client record:")
            for key in result.keys():
                print(f"   {key}: {result[key]}")
        
        conn.close()
        
        # Test the funding lookup system
        print(f"\n🧪 Testing funding lookup for Dennis...")
        
        try:
            from src.services.training_package_cache import TrainingPackageCache
            
            # Initialize the training package cache system
            cache = TrainingPackageCache()
            
            # Look up Dennis's funding status
            funding_data = cache.lookup_participant_funding("Dennis Rost")
            
            if funding_data:
                print(f"✅ Funding lookup SUCCESS!")
                print(f"   Status: {funding_data.get('status', 'Unknown')}")
                print(f"   Package: {funding_data.get('package_name', 'Unknown')}")
                print(f"   Amount Owed: ${funding_data.get('amount_owed', 0)}")
                print(f"   Data Source: {funding_data.get('data_source', 'Unknown')}")
            else:
                print(f"❌ Funding lookup still failing")
                
        except Exception as e:
            print(f"❌ Error testing funding lookup: {e}")
    
    except Exception as e:
        print(f"❌ Database error: {e}")

def test_dennis_clubos_api():
    """Test Dennis's ClubOS API access directly"""
    
    print(f"\n🔍 Testing Dennis's ClubOS API access...")
    
    try:
        from clubos_training_api import ClubOSTrainingPackageAPI
        
        api = ClubOSTrainingPackageAPI()
        if not api.authenticate():
            print("❌ Failed to authenticate with ClubOS")
            return
        
        # Test his delegate ID
        dennis_delegate_id = "189425730"
        
        print(f"🎯 Testing delegate ID: {dennis_delegate_id}")
        
        # Use exact delegation endpoint
        delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{dennis_delegate_id}/url=false")
        print(f"   Delegation status: {delegation_response.status_code}")
        
        if delegation_response.status_code == 200:
            # Get package agreements
            agreements_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
            print(f"   Agreements status: {agreements_response.status_code}")
            
            if agreements_response.status_code == 200:
                agreements = agreements_response.json()
                print(f"   Found {len(agreements)} agreements")
                
                if agreements:
                    agreement = agreements[0]
                    package_info = agreement.get('packageAgreement', {})
                    billing_info = agreement.get('billingStatuses', {}).get('current', {})
                    
                    print(f"   ✅ Package: {package_info.get('name', 'Unknown')}")
                    print(f"   ✅ Agreement ID: {package_info.get('id', 'Unknown')}")
                    print(f"   ✅ Status: {package_info.get('agreementStatus', 'Unknown')}")
                    print(f"   ✅ Billing State: {billing_info.get('billingState', 'Unknown')}")
                    
                    # Get billing status for past due amount
                    agreement_id = package_info.get('id')
                    if agreement_id:
                        billing_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status")
                        if billing_response.status_code == 200:
                            billing_data = billing_response.json()
                            past_due = billing_data.get('pastDueAmount', 0)
                            print(f"   ✅ Past Due Amount: ${past_due}")
        
    except Exception as e:
        print(f"❌ Error testing ClubOS API: {e}")

if __name__ == "__main__":
    print("🔧 Fixing Dennis Rost's training data...")
    print("=" * 60)
    
    fix_dennis_training_data()
    test_dennis_clubos_api()
    
    print("\n" + "=" * 60)
    print("🏁 Dennis fix complete!")
    print("\nNow try checking Dennis in the dashboard - he should show up as a training client!")
