#!/usr/bin/env python3
"""
Test if the fixed billing amounts are working in the full integration
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_integration import ClubOSIntegration

def test_integration():
    print("🧪 Testing full ClubOS integration with fixed billing amounts")
    
    integration = ClubOSIntegration()
    clients = integration.get_training_clients()
    
    print(f"✅ Retrieved {len(clients)} training clients")
    
    # Check billing amounts
    amounts = [c.get('biweekly_amount', 0) for c in clients]
    working_amounts = [a for a in amounts if a > 0]
    
    print(f"💰 Clients with billing amounts: {len(working_amounts)}")
    
    if working_amounts:
        print(f"📈 Sample amounts: ${working_amounts[:5]}")
    
    # Check for past due clients
    past_due = [c for c in clients if c.get('past_due_amount', 0) > 0]
    print(f"⚠️ Past due clients: {len(past_due)}")
    
    # Show sample client with amount
    clients_with_amounts = [c for c in clients if c.get('biweekly_amount', 0) > 0]
    if clients_with_amounts:
        client = clients_with_amounts[0]
        print(f"\n📋 Sample client: {client.get('member_name')} - ${client.get('biweekly_amount', 0):.2f} biweekly")
        print(f"   Status: {client.get('payment_status', 'Unknown')}")
        print(f"   Past Due: ${client.get('past_due_amount', 0):.2f}")

if __name__ == "__main__":
    test_integration()