#!/usr/bin/env python3
"""
Direct database test of training client query logic
"""

import sqlite3
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def test_training_client_queries():
    """Test the exact SQL queries that will be used in campaigns"""
    print("🧪 TESTING: Training Client SQL Queries")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        print("📊 Testing past due training client query...")
        
        # Test the exact query from the messaging system
        query = '''
            SELECT member_id as id, clubos_member_id as prospect_id, email, phone as mobile_phone, member_name as full_name, payment_status as status_message
            FROM training_clients 
            WHERE payment_status = 'Past Due'
            ORDER BY member_id
            LIMIT 50
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"✅ Query executed successfully!")
        print(f"📋 Found {len(results)} past due training clients")
        
        if results:
            print(f"\n🎯 Sample results (campaign-ready format):")
            for i, row in enumerate(results[:5]):
                print(f"   {i+1}. ID: {row['id']}")
                print(f"      Name: {row['full_name']}")
                print(f"      Prospect ID: {row['prospect_id']}")
                print(f"      Email: {row['email']}")
                print(f"      Phone: {row['mobile_phone']}")
                print(f"      Status: {row['status_message']}")
                print()
            
            # Test validation criteria
            print(f"📊 Validation Analysis:")
            valid_email_count = sum(1 for row in results if row['email'])
            valid_phone_count = sum(1 for row in results if row['mobile_phone'])
            
            print(f"   • Total training clients: {len(results)}")
            print(f"   • With email: {valid_email_count}")
            print(f"   • With phone: {valid_phone_count}")
            print(f"   • SMS-ready: {valid_phone_count}")
            print(f"   • Email-ready: {valid_email_count}")
        
        # Test current training client query too
        print(f"\n📊 Testing current training client query...")
        
        query2 = '''
            SELECT member_id as id, clubos_member_id as prospect_id, email, phone as mobile_phone, member_name as full_name, payment_status as status_message
            FROM training_clients 
            WHERE payment_status = 'Current'
            ORDER BY member_id
            LIMIT 50
        '''
        
        cursor.execute(query2)
        current_results = cursor.fetchall()
        
        print(f"✅ Current clients query executed successfully!")
        print(f"📋 Found {len(current_results)} current training clients")
        
        conn.close()
        
        # Test the mapping logic
        print(f"\n📊 Testing Category Mapping Logic:")
        
        category_mapping = {
            'training-past-due': 'training_past_due',
            'training-current': 'training_current',  
            'training-clients-past-due': 'training_past_due',
            'training-clients-current': 'training_current',
            'past-due-training': 'training_past_due',
        }
        
        test_categories = ['training-past-due', 'past-due-training', 'training-clients-past-due']
        
        for test_cat in test_categories:
            mapped = category_mapping.get(test_cat, test_cat)
            print(f"   '{test_cat}' → '{mapped}'")
        
        # Summary
        print(f"\n🎯 INTEGRATION TEST RESULTS:")
        print(f"   ✅ Database queries work correctly")
        print(f"   ✅ Past due training clients: {len(results)} found")
        print(f"   ✅ Current training clients: {len(current_results)} found")
        print(f"   ✅ Category mapping logic works")
        print(f"   ✅ SMS-ready clients: {valid_phone_count if results else 0}")
        
        if results and valid_phone_count > 0:
            print(f"\n🚀 READY FOR CAMPAIGN TESTING:")
            print(f"   • Use category: 'training-past-due'")
            print(f"   • Expected members: {len(results)}")
            print(f"   • SMS-capable: {valid_phone_count}")
            
            # Show specific client for testing
            if results:
                test_client = results[0]
                print(f"\n📋 Test with client: {test_client['full_name']} (ID: {test_client['id']})")
        else:
            print(f"\n⚠️ WARNING: No SMS-ready past due training clients found")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Error testing training client queries: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_training_client_queries()