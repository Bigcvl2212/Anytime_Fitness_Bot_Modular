#!/usr/bin/env python3
"""Test the fixed assignees method."""

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_assignees():
    """Test the assignees fetching."""
    
    api = ClubOSTrainingPackageAPI()
    print('🔐 Authenticating...')
    
    if api.authenticate():
        print('✅ Authentication successful')
        
        print('🔍 Testing assignees fetching...')
        assignees = api._fetch_assignees_from_main_page()
        print(f'Found {len(assignees)} assignees')
        
        # Show first 5 assignees
        for i, assignee in enumerate(assignees[:5]):
            print(f'  {i+1}. {assignee.get("member_name")} (ID: {assignee.get("member_id")})')
        
        if len(assignees) > 5:
            print(f'  ... and {len(assignees) - 5} more')
            
        # Now test the V2 flow with the first assignee
        if assignees:
            first_member = assignees[0]
            print(f'\n🎯 Testing V2 flow with: {first_member.get("member_name")} (ID: {first_member.get("member_id")})')
            
            result = api.get_training_clients_with_v2_data(first_member.get("member_id"))
            
            if result.get('success'):
                print(f'✅ V2 flow success!')
                print(f'📊 Clients processed: {result.get("total_clients_processed", 0)}')
                print(f'📋 Agreements found: {result.get("total_agreements_found", 0)}')
                print(f'✅ V2 successes: {result.get("v2_success_count", 0)}')
                print(f'❌ V2 errors: {result.get("v2_error_count", 0)}')
                
                for client in result.get('clients', []):
                    print(f'\n👤 Client: {client.get("member_name")} (ID: {client.get("member_id")})')
                    print(f'   Payment Status: {client.get("payment_status")}')
                    print(f'   Amount Owed: ${client.get("amount_owed", 0):.2f}')
                    print(f'   Agreements: {client.get("total_agreements", 0)}')
                    
                    for agreement in client.get('agreements', []):
                        aid = agreement.get('agreement_id')
                        success = agreement.get('v2_success', False)
                        amount = agreement.get('past_due_amount', 0)
                        print(f'     📄 Agreement {aid}: V2={success}, ${amount:.2f} past due')
            else:
                print(f'❌ V2 flow failed: {result.get("error")}')
        
    else:
        print('❌ Authentication failed')

if __name__ == "__main__":
    test_assignees()