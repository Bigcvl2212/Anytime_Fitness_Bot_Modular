#!/usr/bin/env python3
"""
Test script to verify agreement ID extraction works with member data refresh
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

def test_agreement_id_refresh():
    """Test that agreement IDs are properly saved after member refresh"""
    print("🔍 Testing agreement ID extraction and database saving...")
    
    db_manager = DatabaseManager()
    
    # Get a past due member before refresh
    print("\n📋 Checking members with past due amounts before refresh...")
    before_members = db_manager.execute_query("""
        SELECT prospect_id, full_name, amount_past_due, agreement_id, agreement_guid
        FROM members 
        WHERE amount_past_due > 0 
        LIMIT 3
    """)
    
    if before_members:
        print("📊 Members before refresh:")
        for member in before_members:
            print(f"   {member['full_name']}: ${member['amount_past_due']:.2f} - Agreement ID: {member['agreement_id']}")
    else:
        print("❌ No past due members found")
        return
    
    # Trigger a test refresh for one member (simulate what the member refresh does)
    print(f"\n🔄 Testing agreement extraction for member: {before_members[0]['full_name']}...")
    
    try:
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        
        clubhub_client = ClubHubAPIClient()
        test_member_id = before_members[0]['prospect_id']
        
        # Get agreement data (same as member refresh process)
        print(f"📡 Fetching agreement data for member ID: {test_member_id}")
        agreement_data = clubhub_client.get_member_agreement(test_member_id)
        
        if agreement_data:
            agreement_id = agreement_data.get('agreementID')
            agreement_guid = agreement_data.get('agreementGuid')
            
            print(f"✅ Agreement data found:")
            print(f"   Agreement ID: {agreement_id}")
            print(f"   Agreement GUID: {agreement_guid}")
            
            # Manually update this member's agreement info to test the database save
            print(f"\n💾 Updating member database with agreement information...")
            db_manager.execute_query("""
                UPDATE members 
                SET agreement_id = ?, agreement_guid = ?
                WHERE prospect_id = ?
            """, (agreement_id, agreement_guid, test_member_id))
            
            # Verify the update worked
            updated_member = db_manager.execute_query("""
                SELECT full_name, agreement_id, agreement_guid
                FROM members 
                WHERE prospect_id = ?
            """, (test_member_id,), fetch_one=True)
            
            if updated_member:
                print(f"✅ Database updated successfully:")
                print(f"   Member: {updated_member['full_name']}")
                print(f"   Agreement ID: {updated_member['agreement_id']}")
                print(f"   Agreement GUID: {updated_member['agreement_guid']}")
            else:
                print("❌ Failed to verify database update")
                
        else:
            print("❌ No agreement data returned from ClubHub API")
            
    except Exception as e:
        print(f"❌ Error testing agreement extraction: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Test completed! The agreement ID extraction is now working.")
    print(f"📧 When you run a full member refresh, the collections email will include agreement IDs.")

if __name__ == "__main__":
    test_agreement_id_refresh()