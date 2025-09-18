#!/usr/bin/env python3
"""Test script for training client campaign logic"""

import sqlite3

def test_training_campaign():
    """Test the training client campaign query logic"""
    
    # Initialize database connection
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print("=== TESTING CAMPAIGN LOGIC FOR TRAINING CLIENTS ===")
    
    # Test category mapping
    category_mapping = {
        'past-due-training': 'training_past_due'
    }
    
    test_category = 'past-due-training'
    mapped_category = category_mapping.get(test_category, test_category)
    print(f"Category '{test_category}' maps to: '{mapped_category}'")
    
    # Test the exact query from messaging.py
    category_to_use = mapped_category
    max_recipients = 100
    
    if category_to_use == 'training_past_due':
        print("📊 Selecting past due training clients (same as campaign logic)")
        
        query = """
        SELECT 
            tc.id as id,
            tc.clubos_member_id as prospect_id,
            COALESCE(tc.email, m.email) as email,
            COALESCE(tc.phone, m.mobile_phone) as mobile_phone,
            tc.full_name as full_name,
            tc.payment_status as status_message
        FROM training_clients tc
        LEFT JOIN members m ON LOWER(TRIM(tc.full_name)) = LOWER(TRIM(m.full_name))
        WHERE tc.payment_status = 'Past Due'
        AND (COALESCE(tc.email, m.email) IS NOT NULL AND COALESCE(tc.email, m.email) != '')
        AND (COALESCE(tc.phone, m.mobile_phone) IS NOT NULL AND COALESCE(tc.phone, m.mobile_phone) != '')
        ORDER BY tc.id
        LIMIT ?
        """
        
        try:
            cursor.execute(query, (max_recipients,))
            category_members = cursor.fetchall()
            
            print(f"Query executed successfully")
            print(f"Found {len(category_members) if category_members else 0} training clients")
            
            if category_members:
                print("Training clients found:")
                for i, member in enumerate(category_members[:5]):
                    print(f"  {i+1}. ID: {member[0]} | Name: {member[4]} | Email: {member[2]} | Phone: {member[3]}")
            else:
                print("❌ No category_members returned - this is the problem!")
                
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            conn.close()
    
    else:
        print(f"❌ Category '{category_to_use}' not handled in if statement")

if __name__ == "__main__":
    test_training_campaign()