#!/usr/bin/env python3
"""
Test script to verify the member data refresh fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def test_member_save_fix():
    """Test that member saving no longer has the '%s' parameter error"""
    print("🔍 Testing member data save functionality...")
    
    db_manager = DatabaseManager()
    
    # Create test member data similar to what comes from ClubHub
    test_members = [{
        'prospect_id': 'test_123',
        'first_name': 'Test',
        'last_name': 'Member',
        'full_name': 'Test Member', 
        'email': 'test@example.com',
        'mobile_phone': '555-1234',
        'status': 'Active',
        'status_message': 'In good standing',
        'member_type': 'Monthly',
        'amount_past_due': 0.0,
        'base_amount_past_due': 0.0,
        'missed_payments': 0,
        'late_fees': 0.0,
        'agreement_recurring_cost': 29.99,
        'date_of_next_payment': '2025-10-01',
        'agreement_id': 'AGR123',
        'agreement_guid': 'guid-123',
        'agreement_type': 'Membership'
    }]
    
    # Create test prospect data
    test_prospects = [{
        'prospect_id': 'prospect_456',
        'first_name': 'Test',
        'last_name': 'Prospect',
        'full_name': 'Test Prospect',
        'email': 'prospect@example.com',
        'phone': '555-5678',
        'status': 'Active',
        'prospect_type': 'Lead'
    }]
    
    try:
        print(f"📊 Database type: {db_manager.db_type}")
        
        # Test member saving
        print("💾 Testing member save...")
        member_result = db_manager.save_members_to_db(test_members)
        print(f"✅ Member save result: {member_result}")
        
        # Test prospect saving 
        print("💾 Testing prospect save...")
        prospect_result = db_manager.save_prospects_to_db(test_prospects)
        print(f"✅ Prospect save result: {prospect_result}")
        
        # Verify data was saved
        print("🔍 Verifying saved data...")
        saved_member = db_manager.execute_query(
            "SELECT * FROM members WHERE prospect_id = ?",
            ('test_123',),
            fetch_one=True
        )
        
        saved_prospect = db_manager.execute_query(
            "SELECT * FROM prospects WHERE prospect_id = ?", 
            ('prospect_456',),
            fetch_one=True
        )
        
        if saved_member:
            print(f"✅ Member saved: {saved_member['full_name']}")
        else:
            print("❌ Member not found")
            
        if saved_prospect:
            print(f"✅ Prospect saved: {saved_prospect['full_name']}")
        else:
            print("❌ Prospect not found")
            
        print("\n🎉 All database operations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_member_save_fix()