#!/usr/bin/env python3
"""
Test joining training_clients with members table for complete campaign data
"""

import sqlite3
import json

def test_training_client_member_join():
    """Test joining training_clients with members to get complete contact + agreement data"""
    print("🔍 TESTING: Training Client + Member JOIN for Complete Campaign Data")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        # Test JOIN query to get training client data + member contact info
        print("📊 Testing JOIN query for past due training clients + member contact info...")
        
        join_query = '''
            SELECT 
                tc.member_id,
                tc.clubos_member_id,
                tc.member_name,
                tc.payment_status,
                tc.past_due_amount,
                tc.total_past_due,
                tc.package_summary,
                tc.package_details,
                tc.trainer_name,
                -- Get contact info from members table
                m.email,
                m.mobile_phone,
                m.prospect_id,
                m.full_name as member_full_name,
                m.status_message as member_status
            FROM training_clients tc
            LEFT JOIN members m ON (
                tc.clubos_member_id = m.prospect_id 
                OR tc.member_id = m.prospect_id
                OR tc.member_id = CAST(m.id as TEXT)
            )
            WHERE tc.payment_status = 'Past Due'
            ORDER BY tc.total_past_due DESC
        '''
        
        cursor.execute(join_query)
        results = cursor.fetchall()
        
        print(f"✅ JOIN query executed successfully!")
        print(f"📋 Found {len(results)} past due training clients with member data")
        
        if results:
            print(f"\n🎯 Complete campaign data (training + member info):")
            
            sms_ready = 0
            email_ready = 0
            total_past_due = 0
            
            for i, row in enumerate(results):
                print(f"\n   {i+1}. {row['member_name']} (Training Client)")
                print(f"      Training Client ID: {row['member_id']}")
                print(f"      ClubOS ID: {row['clubos_member_id']}")
                print(f"      Past Due Amount: ${row['past_due_amount']:.2f}")
                print(f"      Total Past Due: ${row['total_past_due']:.2f}")
                print(f"      Package: {row['package_summary']}")
                print(f"      Trainer: {row['trainer_name']}")
                
                # Contact info from members table
                email = row['email']
                phone = row['mobile_phone']
                member_status = row['member_status']
                
                print(f"      📧 Email: {email or 'None'}")
                print(f"      📱 Phone: {phone or 'None'}")  
                print(f"      👤 Member Status: {member_status or 'No member record'}")
                
                # Count ready for campaigns
                if email:
                    email_ready += 1
                if phone:
                    sms_ready += 1
                
                total_past_due += row['total_past_due'] or 0
                
                # Parse package details if available
                if row['package_details']:
                    try:
                        package_details = json.loads(row['package_details'])
                        print(f"      📦 Package Details:")
                        for package in package_details:
                            print(f"         - {package.get('package_name')}: ${package.get('amount_owed', 0):.2f}")
                            if package.get('agreement_id'):
                                print(f"           Agreement ID: {package['agreement_id']}")
                    except:
                        print(f"      📦 Package Details: {row['package_details'][:50]}...")
            
            # Summary
            print(f"\n📊 CAMPAIGN READINESS SUMMARY:")
            print(f"   • Total past due training clients: {len(results)}")
            print(f"   • SMS-ready (have phone): {sms_ready}")
            print(f"   • Email-ready (have email): {email_ready}")
            print(f"   • Total past due amount: ${total_past_due:.2f}")
            print(f"   • Can send campaigns: {'YES' if sms_ready > 0 or email_ready > 0 else 'NO'}")
            
            # Test the campaign-ready format
            print(f"\n🚀 CAMPAIGN-READY DATA FORMAT:")
            campaign_ready_clients = []
            for row in results:
                if row['email'] or row['mobile_phone']:  # Has contact info
                    campaign_client = {
                        'member_id': row['clubos_member_id'] or row['member_id'],
                        'prospect_id': row['clubos_member_id'],
                        'email': row['email'],
                        'mobile_phone': row['mobile_phone'],
                        'full_name': row['member_name'],
                        'status_message': f"Training Past Due: ${row['total_past_due']:.2f}",
                        'training_data': {
                            'past_due_amount': row['past_due_amount'],
                            'total_past_due': row['total_past_due'],
                            'package_summary': row['package_summary'],
                            'trainer_name': row['trainer_name']
                        }
                    }
                    campaign_ready_clients.append(campaign_client)
            
            print(f"   📋 Campaign-ready clients: {len(campaign_ready_clients)}")
            if campaign_ready_clients:
                sample_client = campaign_ready_clients[0]
                print(f"   📄 Sample client data:")
                print(f"      Name: {sample_client['full_name']}")
                print(f"      Email: {sample_client['email']}")
                print(f"      Phone: {sample_client['mobile_phone']}")
                print(f"      Status: {sample_client['status_message']}")
                print(f"      Training Info: ${sample_client['training_data']['total_past_due']:.2f} past due")
            
            return len(campaign_ready_clients) > 0
        else:
            print(f"\n❌ No results from JOIN query")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing training client + member JOIN: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_training_client_member_join()
    
    if success:
        print(f"\n✅ SUCCESS: Can create complete campaign data by joining training_clients + members tables")
        print(f"   • Next: Update messaging.py to use this JOIN approach")
        print(f"   • This will give us agreement data + contact info for campaigns")
    else:
        print(f"\n❌ ISSUE: JOIN approach needs adjustment")
        print(f"   • Check member ID matching between tables")
        print(f"   • Verify data exists in both tables")