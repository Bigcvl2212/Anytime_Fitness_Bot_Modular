#!/usr/bin/env python3
"""
Test joining training_clients with members by name matching
"""

import sqlite3
import json

def test_name_based_join():
    """Test joining training_clients with members using name matching"""
    print("🔍 TESTING: Training Client + Member JOIN by Name Matching")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        # Test name-based JOIN query
        print("📊 Testing name-based JOIN query for past due training clients...")
        
        name_join_query = '''
            SELECT 
                tc.member_id as training_client_id,
                tc.clubos_member_id,
                tc.member_name as training_client_name,
                tc.payment_status,
                tc.past_due_amount,
                tc.total_past_due,
                tc.package_summary,
                tc.package_details,
                tc.trainer_name,
                -- Get contact info from members table by name matching
                m.id as member_db_id,
                m.prospect_id as member_prospect_id,
                m.email,
                m.mobile_phone,
                m.full_name as member_full_name,
                m.status_message as member_status
            FROM training_clients tc
            LEFT JOIN members m ON (
                TRIM(LOWER(tc.member_name)) = TRIM(LOWER(m.full_name))
                OR TRIM(LOWER(tc.full_name)) = TRIM(LOWER(m.full_name))
                OR (
                    tc.first_name IS NOT NULL AND tc.last_name IS NOT NULL 
                    AND TRIM(LOWER(tc.first_name || ' ' || tc.last_name)) = TRIM(LOWER(m.full_name))
                )
                OR (
                    m.first_name IS NOT NULL AND m.last_name IS NOT NULL
                    AND TRIM(LOWER(tc.member_name)) = TRIM(LOWER(m.first_name || ' ' || m.last_name))
                )
            )
            WHERE tc.payment_status = 'Past Due'
            ORDER BY tc.total_past_due DESC
        '''
        
        cursor.execute(name_join_query)
        results = cursor.fetchall()
        
        print(f"✅ Name-based JOIN query executed successfully!")
        print(f"📋 Found {len(results)} past due training clients")
        
        if results:
            matches_found = 0
            sms_ready = 0
            email_ready = 0
            total_past_due = 0
            
            print(f"\n🎯 Name-based matching results:")
            
            for i, row in enumerate(results):
                print(f"\n   {i+1}. {row['training_client_name']} (Training Client)")
                print(f"      Training Client ID: {row['training_client_id']}")
                print(f"      ClubOS ID: {row['clubos_member_id']}")
                print(f"      Past Due Amount: ${row['past_due_amount']:.2f}")
                print(f"      Total Past Due: ${row['total_past_due']:.2f}")
                print(f"      Package: {row['package_summary']}")
                print(f"      Trainer: {row['trainer_name']}")
                
                # Check if we found a matching member
                if row['member_db_id']:
                    matches_found += 1
                    print(f"      ✅ MATCHED with member record:")
                    print(f"         Member DB ID: {row['member_db_id']}")
                    print(f"         Member Prospect ID: {row['member_prospect_id']}")
                    print(f"         Member Full Name: {row['member_full_name']}")
                    print(f"         📧 Email: {row['email'] or 'None'}")
                    print(f"         📱 Phone: {row['mobile_phone'] or 'None'}")
                    print(f"         👤 Member Status: {row['member_status'] or 'None'}")
                    
                    # Count contact readiness
                    if row['email']:
                        email_ready += 1
                    if row['mobile_phone']:
                        sms_ready += 1
                        
                else:
                    print(f"      ❌ NO MATCH found in members table")
                
                total_past_due += row['total_past_due'] or 0
                
                # Parse package details
                if row['package_details']:
                    try:
                        package_details = json.loads(row['package_details'])
                        print(f"      📦 Agreement IDs:")
                        for package in package_details:
                            if package.get('agreement_id'):
                                print(f"         - {package.get('package_name')}: Agreement {package['agreement_id']} (${package.get('amount_owed', 0):.2f})")
                    except:
                        pass
            
            # Summary
            print(f"\n📊 NAME-BASED MATCHING SUMMARY:")
            print(f"   • Total past due training clients: {len(results)}")
            print(f"   • Successfully matched with members: {matches_found}")
            print(f"   • Match rate: {matches_found/len(results)*100:.1f}%")
            print(f"   • SMS-ready (have phone): {sms_ready}")
            print(f"   • Email-ready (have email): {email_ready}")
            print(f"   • Total campaign-ready: {sms_ready + email_ready}")
            print(f"   • Total past due amount: ${total_past_due:.2f}")
            
            # Generate campaign-ready format
            if matches_found > 0:
                print(f"\n🚀 CAMPAIGN-READY DATA FORMAT:")
                campaign_ready_query = '''
                    SELECT 
                        tc.member_id as training_client_id,
                        tc.clubos_member_id,
                        tc.member_name,
                        tc.payment_status,
                        tc.past_due_amount,
                        tc.total_past_due,
                        tc.package_summary,
                        tc.package_details,
                        tc.trainer_name,
                        m.prospect_id,
                        m.email,
                        m.mobile_phone,
                        m.full_name
                    FROM training_clients tc
                    JOIN members m ON (
                        TRIM(LOWER(tc.member_name)) = TRIM(LOWER(m.full_name))
                        OR TRIM(LOWER(tc.full_name)) = TRIM(LOWER(m.full_name))
                        OR (
                            tc.first_name IS NOT NULL AND tc.last_name IS NOT NULL 
                            AND TRIM(LOWER(tc.first_name || ' ' || tc.last_name)) = TRIM(LOWER(m.full_name))
                        )
                        OR (
                            m.first_name IS NOT NULL AND m.last_name IS NOT NULL
                            AND TRIM(LOWER(tc.member_name)) = TRIM(LOWER(m.first_name || ' ' || m.last_name))
                        )
                    )
                    WHERE tc.payment_status = 'Past Due'
                    AND (m.email IS NOT NULL OR m.mobile_phone IS NOT NULL)
                    ORDER BY tc.total_past_due DESC
                '''
                
                cursor.execute(campaign_ready_query)
                campaign_ready = cursor.fetchall()
                
                print(f"   📋 Campaign-ready clients with contact info: {len(campaign_ready)}")
                
                if campaign_ready:
                    sample = campaign_ready[0]
                    print(f"\n   📄 Sample campaign-ready client:")
                    print(f"      Name: {sample['member_name']}")
                    print(f"      Training Client ID: {sample['training_client_id']}")
                    print(f"      Member Prospect ID: {sample['prospect_id']}")
                    print(f"      Email: {sample['email']}")
                    print(f"      Phone: {sample['mobile_phone']}")
                    print(f"      Past Due: ${sample['total_past_due']:.2f}")
                    print(f"      Package: {sample['package_summary']}")
                
                return len(campaign_ready) > 0
            else:
                print(f"\n❌ No matches found - cannot create campaign-ready data")
                return False
        else:
            print(f"\n❌ No past due training clients found")
            return False
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing name-based JOIN: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_name_based_join()
    
    if success:
        print(f"\n✅ SUCCESS: Name-based matching works for training clients + members")
        print(f"   • Update messaging.py to use name-based JOIN queries")
        print(f"   • This will provide complete campaign data with contact info")
    else:
        print(f"\n❌ ISSUE: Name-based matching needs refinement")
        print(f"   • Check name formatting differences between tables")
        print(f"   • May need fuzzy matching or name normalization")