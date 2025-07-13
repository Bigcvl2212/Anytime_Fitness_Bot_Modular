#!/usr/bin/env python3
"""
Test Square invoice creation
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gym_bot.services.payments.square_client import create_square_invoice

def test_square_invoice():
    """Test creating a Square invoice"""
    print("Testing Square invoice creation...")
    
    # Test with a small amount
    result = create_square_invoice(
        member_name="Test Member",
        amount=25.50,
        description="Test Invoice"
    )
    
    if result:
        print(f"✅ Success! Invoice URL: {result}")
        return True
    else:
        print("❌ Failed to create invoice")
        return False

if __name__ == "__main__":
    test_square_invoice()
