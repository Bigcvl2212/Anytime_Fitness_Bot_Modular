#!/usr/bin/env python3
"""
Test breakthrough method directly to see if past due amounts are preserved
"""

import sys
sys.path.append('c:/Users/mayoj/OneDrive/Documents/Gym-Bot/gym-bot/gym-bot-modular')

from src.services.clubos_integration import ClubOSIntegration

def test_breakthrough_direct():
    print("🎯 Testing breakthrough method directly...")
    
    # Test breakthrough method directly
    clubos_int = ClubOSIntegration()
    clubos_int.init_services()
    
    # Get ONE specific client that had past due amount
    training_clients = clubos_int.get_training_clients()
    print(f"Found {len(training_clients)} training clients")
    
    # Look for clients with past due amounts
    past_due_clients = []
    for client in training_clients:
        total_past_due = client.get('total_past_due', 0.0)
        past_due_amount = client.get('past_due_amount', 0.0) 
        if total_past_due > 0 or past_due_amount > 0:
            past_due_clients.append(client)
            print(f"💰 PAST DUE CLIENT: {client.get('member_name', 'Unknown')}")
            print(f"   Total: ${total_past_due:.2f}, Amount: ${past_due_amount:.2f}")
            print(f"   Status: {client.get('payment_status', 'Unknown')}")
            print(f"   Package details: {len(client.get('package_details', []))} packages")
    
    if not past_due_clients:
        print("❌ No past due clients found in breakthrough result")
        # Show first client as example
        if training_clients:
            client = training_clients[0]
            print(f"📋 Example client: {client.get('member_name', 'Unknown')}")
            print(f"   Total: ${client.get('total_past_due', 0.0):.2f}")
            print(f"   Status: {client.get('payment_status', 'Unknown')}")
            print(f"   Package details sample: {client.get('package_details', [])[:1]}")
    else:
        print(f"✅ Found {len(past_due_clients)} past due clients")

if __name__ == "__main__":
    test_breakthrough_direct()