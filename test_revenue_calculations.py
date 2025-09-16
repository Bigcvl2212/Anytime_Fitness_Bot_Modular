#!/usr/bin/env python3
"""
Test the updated revenue calculations to verify fixes
"""
import sqlite3
import json
from src.services.database_manager import DatabaseManager

def test_revenue_calculations():
    """Test the updated revenue calculation methods"""
    print("🧪 Testing Updated Revenue Calculations")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Test the monthly revenue calculation
    print("\n💰 Testing Monthly Revenue Calculation:")
    revenue_data = db.get_monthly_revenue_calculation()
    
    print(f"Member Revenue: ${revenue_data['member_revenue']:.2f}")
    print(f"Revenue Members Count: {revenue_data['revenue_members_count']}")
    print(f"Training Revenue: ${revenue_data['training_revenue']:.2f}")
    print(f"Training Clients Count: {revenue_data['training_clients_count']}")
    print(f"Total Monthly Revenue: ${revenue_data['total_monthly_revenue']:.2f}")
    
    # Test training clients with agreements display
    print(f"\n🏋️ Testing Training Client Display:")
    training_clients = db.get_training_clients_with_agreements()
    print(f"Found {len(training_clients)} training clients")
    
    if training_clients:
        print("\nSample training client data:")
        for i, client in enumerate(training_clients[:3]):  # Show first 3
            print(f"\n  Client {i+1}: {client.get('first_name')} {client.get('last_name')}")
            print(f"    Past Due: ${client.get('past_due_amount', 0):.2f}")
            print(f"    Package Details: {client.get('package_details', 'N/A')[:100]}...")
    
    # Test member categorization
    print(f"\n📊 Testing Member Category Counts:")
    counts = db.get_category_counts()
    
    total_members = sum(counts.values())
    print(f"Green Members: {counts.get('green', 0)}")
    print(f"Past Due Members: {counts.get('past_due', 0)}")
    print(f"Red Members: {counts.get('red', 0)}")
    print(f"Comp Members: {counts.get('comp', 0)}")
    print(f"PPV Members: {counts.get('ppv', 0)}")
    print(f"Staff Members: {counts.get('staff', 0)}")
    print(f"Frozen Members: {counts.get('frozen', 0)}")
    print(f"Inactive Members: {counts.get('inactive', 0)}")
    print(f"Total Categorized: {total_members}")
    
    # Verify green members breakdown
    print(f"\n🟢 Green Members Analysis:")
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Count green members with revenue
    cursor.execute("""
        SELECT COUNT(*) FROM members
        WHERE status_message = 'Member is in good standing'
        AND COALESCE(agreement_recurring_cost, 0) > 0
    """)
    green_with_revenue = cursor.fetchone()[0]
    
    # Count green members without revenue
    cursor.execute("""
        SELECT COUNT(*) FROM members
        WHERE status_message = 'Member is in good standing'
        AND (agreement_recurring_cost IS NULL OR agreement_recurring_cost = 0)
    """)
    green_without_revenue = cursor.fetchone()[0]
    
    print(f"  Green members with recurring revenue: {green_with_revenue}")
    print(f"  Green members without recurring revenue: {green_without_revenue} (staff + paid-in-full)")
    print(f"  Total green members: {green_with_revenue + green_without_revenue}")
    
    conn.close()
    
    print(f"\n✅ Revenue calculation testing complete!")

if __name__ == "__main__":
    test_revenue_calculations()