#!/usr/bin/env python3
"""Test the proper V2 browser flow implementation."""

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_v2_browser_flow():
    """Test the proper browser flow with V2 data for a specific member."""
    
    # Test the proper browser flow with a known member
    api = ClubOSTrainingPackageAPI()
    print('🔐 Authenticating...')
    
    if api.authenticate():
        print('✅ Authentication successful')
        
        # Test with specific member
        member_id = '185182950'  # Javae Dixon
        print(f'🎯 Testing proper browser flow for member {member_id}')
        
        result = api.get_training_clients_with_v2_data(member_id)
        
        if result.get('success'):
            print(f'✅ Browser flow success!')
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
                    
                    # Show V2 data structure if successful
                    if success and agreement.get('v2_data'):
                        v2_data = agreement['v2_data']
                        invoices = len(v2_data.get('invoices', []))
                        payments = len(v2_data.get('scheduledPayments', []))
                        print(f'       📋 V2 Data: {invoices} invoices, {payments} scheduled payments')
        else:
            print(f'❌ Browser flow failed: {result.get("error")}')
    else:
        print('❌ Authentication failed')

if __name__ == "__main__":
    test_v2_browser_flow()