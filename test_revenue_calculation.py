#!/usr/bin/env python3
"""Test revenue calculation with updated categorization"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.database_manager import DatabaseManager

def test_revenue_calculation():
    """Test the revenue calculation"""
    print("=== TESTING REVENUE CALCULATION ===")
    
    db = DatabaseManager()
    
    # Get monthly revenue calculation
    revenue_data = db.get_monthly_revenue_calculation()
    monthly_revenue = revenue_data.get('total_monthly_revenue', 0)
    print(f"💰 Monthly Revenue: ${monthly_revenue:,.2f}")
    print(f"🔢 Revenue Members Count: {revenue_data.get('revenue_members_count', 0)}")
    print(f"📊 Full Revenue Data: {revenue_data}")
    
    # Get category counts for context
    counts = db.get_category_counts()
    green_count = counts.get('green', 0)
    
    print(f"\n🟢 Green Members (revenue-generating): {green_count}")
    print(f"📊 Average revenue per green member: ${monthly_revenue / green_count:,.2f}" if green_count > 0 else "📊 No green members for calculation")
    
    # Test the specific revenue query
    revenue_query_result = db.execute_query("""
        SELECT COUNT(*) as count FROM members
        WHERE status_message = 'Member is in good standing'
    """)
    
    revenue_member_count = revenue_query_result[0]['count'] if revenue_query_result else 0
    print(f"\n🔍 Revenue query verification: {revenue_member_count} members with 'Member is in good standing' status")

if __name__ == "__main__":
    test_revenue_calculation()