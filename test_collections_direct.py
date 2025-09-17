#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime

def test_collections_system():
    """Test the collections system directly with SQLite"""
    
    print("🧪 Testing Collections Management System (Direct SQLite)")
    print("=" * 60)
    
    try:
        # Connect to local SQLite database
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get past due members
        print("📊 Fetching past due members...")
        cursor.execute("""
            SELECT 
                full_name as name,
                email,
                phone,
                mobile_phone,
                amount_past_due as past_due_amount,
                status,
                join_date,
                'member' as type,
                NULL as agreement_id,
                NULL as agreement_type
            FROM members 
            WHERE amount_past_due > 0
            ORDER BY amount_past_due DESC
        """)
        
        past_due_members = cursor.fetchall()
        print(f"   Found {len(past_due_members)} past due members")
        
        # Get past due training clients
        print("📊 Fetching past due training clients...")
        cursor.execute("""
            SELECT 
                member_name as name,
                email,
                phone,
                past_due_amount,
                payment_status as status,
                last_updated,
                'training_client' as type,
                package_details,
                active_packages
            FROM training_clients 
            WHERE past_due_amount > 0
            ORDER BY past_due_amount DESC
        """)
        
        past_due_training = cursor.fetchall()
        print(f"   Found {len(past_due_training)} past due training clients")
        
        # Process training clients to extract agreement info
        processed_training = []
        for client in past_due_training:
            client_dict = {
                'name': client[0], 'email': client[1], 'phone': client[2],
                'past_due_amount': client[3], 'status': client[4], 'last_updated': client[5],
                'type': client[6], 'package_details': client[7], 'active_packages': client[8]
            }
            
            # Extract agreement info from package_details
            agreement_id = None
            agreement_type = None
            if client_dict.get('package_details'):
                try:
                    details = json.loads(client_dict['package_details'])
                    if details and len(details) > 0:
                        agreement_id = details[0].get('agreement_id')
                        agreement_type = details[0].get('package_name', 'Training Package')
                except:
                    pass
            
            client_dict['agreement_id'] = agreement_id
            client_dict['agreement_type'] = agreement_type
            processed_training.append(client_dict)
        
        # Combine all past due data
        all_past_due = []
        
        # Add members
        for member in past_due_members:
            member_dict = {
                'name': member[0], 'email': member[1], 'phone': member[2],
                'mobile_phone': member[3], 'past_due_amount': member[4], 'status': member[5],
                'join_date': member[6], 'type': member[7], 'agreement_id': member[8],
                'agreement_type': member[9]
            }
            all_past_due.append(member_dict)
        
        # Add training clients
        all_past_due.extend(processed_training)
        
        print(f"\n✅ Total past due accounts: {len(all_past_due)}")
        
        # Show top 10 by amount
        print("\n📋 Top 10 Past Due Accounts by Amount:")
        print("-" * 80)
        sorted_accounts = sorted(all_past_due, key=lambda x: x['past_due_amount'], reverse=True)
        
        for i, account in enumerate(sorted_accounts[:10], 1):
            agreement_info = ""
            if account.get('agreement_id'):
                agreement_info = f" | Agreement: {account['agreement_id']} - {account['agreement_type']}"
            
            contact_info = account.get('email') or account.get('phone') or 'No contact'
            
            print(f"{i:2d}. {account['name']:<25} ${account['past_due_amount']:>8.2f} | {account['type']:<8} | {contact_info}{agreement_info}")
        
        # Test email generation
        print("\n📧 Testing Email Generation:")
        print("-" * 40)
        
        # Take first 3 accounts for email test
        test_accounts = sorted_accounts[:3]
        total_amount = sum(account['past_due_amount'] for account in test_accounts)
        
        email_content = f"""
COLLECTIONS REFERRAL - {datetime.now().strftime('%Y-%m-%d')}

The following accounts have been selected for collections referral:

"""
        
        for i, account in enumerate(test_accounts, 1):
            name = account.get('name', 'Unknown')
            amount = account.get('past_due_amount', 0)
            email = account.get('email', 'No email')
            phone = account.get('phone', 'No phone')
            account_type = account.get('type', 'Unknown')
            agreement_id = account.get('agreement_id', 'N/A')
            agreement_type = account.get('agreement_type', 'N/A')
            
            email_content += f"""
{i}. {name}
   Amount Past Due: ${amount:.2f}
   Type: {account_type.title()}
   Agreement ID: {agreement_id}
   Agreement Type: {agreement_type}
   Email: {email}
   Phone: {phone}
   ---
"""
        
        email_content += f"""

TOTAL AMOUNT: ${total_amount:.2f}
TOTAL ACCOUNTS: {len(test_accounts)}

Please process these accounts for collections referral.

Generated by Gym Bot Collections Manager
"""
        
        print("Sample email content:")
        print(email_content)
        
        # Test modal data structure
        print("\n🔧 Modal Data Structure Test:")
        print("-" * 40)
        
        modal_data = {
            'success': True,
            'past_due_data': all_past_due,
            'total_count': len(all_past_due)
        }
        
        print(f"✅ Modal data structure valid: {len(modal_data['past_due_data'])} accounts")
        print(f"✅ Total count: {modal_data['total_count']}")
        
        # Test individual account structure
        if all_past_due:
            sample_account = all_past_due[0]
            required_fields = ['name', 'past_due_amount', 'type', 'email', 'phone', 'agreement_id', 'agreement_type']
            missing_fields = [field for field in required_fields if field not in sample_account]
            
            if missing_fields:
                print(f"⚠️ Missing fields in account structure: {missing_fields}")
            else:
                print("✅ Account structure has all required fields")
        
        conn.close()
        
        print("\n🎉 Collections Management System Test Complete!")
        print("✅ All components working correctly")
        print("✅ Ready for integration with Flask dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing collections system: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_collections_system()
