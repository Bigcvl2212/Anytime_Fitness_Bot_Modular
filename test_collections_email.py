#!/usr/bin/env python3

"""
Test the actual collections email function
"""

def test_collections_email():
    """Test the collections email function directly"""
    
    print("🧪 Testing Collections Email Function")
    print("=" * 50)
    
    try:
        # Import the actual function from the routes
        from src.routes.members import send_email_to_club, generate_collections_email
        
        # Create test data
        test_accounts = [
            {
                'name': 'Test Member',
                'past_due_amount': 150.00,
                'type': 'member',
                'agreement_id': '12345678',
                'agreement_type': 'Membership',
                'email': 'test@example.com',
                'phone': '+1234567890'
            }
        ]
        
        # Generate email content
        email_content = generate_collections_email(test_accounts)
        print("✅ Email content generated successfully")
        print(f"📧 Email content preview:\n{email_content[:200]}...")
        
        # Test sending email
        print("\n📧 Attempting to send email...")
        success = send_email_to_club(email_content)
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email sending failed - check logs for details")
            
    except Exception as e:
        print(f"❌ Error testing collections email: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_collections_email()
