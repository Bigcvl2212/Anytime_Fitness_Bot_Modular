#!/usr/bin/env python3
"""
Test Collections Email Function
Test the actual collections email sending function from the routes.
"""

import os
import sys
import json
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_collections_email_function():
    """Test the collections email function directly"""
    try:
        # Import the function from routes
        from routes.members import send_email_to_club, generate_collections_email
        
        # Create sample collections data
        sample_accounts = [
            {
                'name': 'Test Account 1',
                'past_due_amount': 150.00,
                'email': 'test1@example.com',
                'phone': '555-123-4567',
                'type': 'member',
                'agreement_id': '12345',
                'agreement_type': 'Monthly Membership'
            },
            {
                'name': 'Test Account 2', 
                'past_due_amount': 89.50,
                'email': 'test2@example.com',
                'phone': '555-987-6543',
                'type': 'training_client',
                'agreement_id': '67890',
                'agreement_type': '16 Session Package'
            }
        ]
        
        logger.info("📋 Generating collections email content...")
        email_content = generate_collections_email(sample_accounts)
        
        logger.info("📧 Generated email content:")
        print("=" * 50)
        print(email_content)
        print("=" * 50)
        
        logger.info("📤 Sending collections email...")
        success = send_email_to_club(email_content)
        
        if success:
            logger.info("✅ Collections email sent successfully!")
            return True
        else:
            logger.error("❌ Collections email sending failed!")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error testing collections email: {e}")
        import traceback
        logger.error(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🧪 Collections Email Function Test")
    print("=" * 40)
    
    success = test_collections_email_function()
    
    if success:
        print("\n✅ Collections email function works!")
        print("📧 The email should be sent to FondDuLacWI@anytimefitness.com")
    else:
        print("\n❌ Collections email function failed!")
    
    return success

if __name__ == "__main__":
    main()