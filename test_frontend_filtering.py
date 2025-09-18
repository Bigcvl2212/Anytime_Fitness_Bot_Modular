#!/usr/bin/env python3
"""
Test script to verify frontend filtering logic for past due training clients
"""

import requests
import json

def test_training_clients_filtering():
    """Test the corrected frontend filtering logic"""
    print("🔍 Testing training clients filtering logic...")
    
    try:
        # Get training clients from API
        response = requests.get('http://localhost:5000/api/training/clients')
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ API request failed: {data.get('error')}")
            return
        
        training_clients = data.get('training_clients', [])
        print(f"📊 Total training clients received: {len(training_clients)}")
        
        # Apply the corrected filtering logic (using past_due_amount instead of amount_past_due)
        past_due_training_clients = []
        for client in training_clients:
            amount_past_due = float(client.get('past_due_amount', 0))
            payment_status = (client.get('payment_status', '') or '').lower()
            status_message = (client.get('status_message', '') or '').lower()
            
            is_past_due = (
                amount_past_due > 0 or 
                'past due' in payment_status or 
                'past due' in status_message
            )
            
            if is_past_due:
                past_due_training_clients.append({
                    'name': client.get('full_name'),
                    'amount': amount_past_due,
                    'payment_status': client.get('payment_status'),
                    'email': client.get('email'),
                    'phone': client.get('phone')
                })
        
        print(f"🎯 Past due training clients found: {len(past_due_training_clients)}")
        
        # Display the past due training clients
        if past_due_training_clients:
            print("\n📋 Past Due Training Clients:")
            for i, client in enumerate(past_due_training_clients, 1):
                print(f"  {i}. {client['name']} - ${client['amount']:.2f} ({client['payment_status']})")
                print(f"      Email: {client['email'] or 'None'} | Phone: {client['phone'] or 'None'}")
        else:
            print("❌ No past due training clients found with corrected filtering")
        
        # Test what the old filtering would have found (using wrong field)
        old_logic_count = 0
        for client in training_clients:
            old_amount = float(client.get('amount_past_due', 0))  # Wrong field
            if old_amount > 0:
                old_logic_count += 1
        
        print(f"\n🔍 Comparison with old logic (amount_past_due field): {old_logic_count} clients")
        print(f"📈 New logic (past_due_amount field): {len(past_due_training_clients)} clients")
        
        return past_due_training_clients
        
    except Exception as e:
        print(f"❌ Error testing training clients filtering: {e}")
        return []

if __name__ == "__main__":
    test_training_clients_filtering()