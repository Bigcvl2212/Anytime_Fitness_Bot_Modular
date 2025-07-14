"""
Gym Bot Main Application
Entry point for the modular Gym Bot application.
"""

import argparse
import sys
import traceback
from typing import Optional

from gym_bot_backend import (
    get_driver, login_to_clubos, close_driver,
    get_gemini_client, get_messaging_service, get_square_client, test_square_connection,
    GCP_PROJECT_ID
)

def initialize_services() -> bool:
    """
    Initialize all required services.
    
    Returns:
        bool: True if all services initialized successfully
    """
    print("🔧 INITIALIZING SERVICES")
    print("="*40)
    
    success = True
    
    # Initialize Gemini AI
    try:
        ai_client = get_gemini_client()
        if ai_client:
            print("✅ Gemini AI service initialized")
        else:
            print("⚠️ Gemini AI service not available (missing API key)")
    except Exception as e:
        print(f"⚠️ Gemini AI not available: {e}")
        # Don't fail completely for missing credentials
    
    # Initialize Square payments
    try:
        square_client = get_square_client()
        if square_client and hasattr(square_client, 'test_connection'):
            if square_client.test_connection():
                print("✅ Square payment service initialized")
            else:
                print("❌ Square payment service connection failed")
                success = False
        else:
            print("⚠️ Square payment service not available (missing credentials)")
    except Exception as e:
        print(f"⚠️ Square payments not available: {e}")
        # Don't fail completely for missing credentials
    
    print(f"{'✅ Services initialized successfully' if success else '❌ Some services failed to initialize'}")
    return success

def setup_driver_and_login():
    """
    Setup WebDriver and login to ClubOS.
    
    Returns:
        WebDriver instance or None if failed
    """
    try:
        print("🚀 SETTING UP WEBDRIVER AND LOGIN")
        print("="*40)
        
        # Get driver
        driver = get_driver(headless=False)  # Set to False for testing invoice sending
        
        # Login to ClubOS
        if login_to_clubos(driver):
            print("✅ Successfully logged into ClubOS")
            return driver
        else:
            print("❌ Failed to login to ClubOS")
            close_driver()
            return None
            
    except Exception as e:
        print(f"❌ Error setting up driver and login: {e}")
        close_driver()
        return None

def run_message_processing():
    """Run the message processing workflow."""
    print("📬 PROCESSING MESSAGES")
    print("="*30)
    
    driver = setup_driver_and_login()
    if not driver:
        return
    
    try:
        messaging_service = get_messaging_service(driver)
        
        # Get last message sender
        sender = messaging_service.get_last_message_sender()
        if not sender:
            print("📭 No new messages to process")
            return
        
        print(f"📧 Processing message from: {sender}")
        
        # Get conversation history
        conversation = messaging_service.scrape_conversation_for_contact(sender)
        
        if conversation:
            print(f"✅ Retrieved {len(conversation)} messages from conversation")
            
            # Generate AI response (this would integrate with your AI workflow)
            ai_client = get_gemini_client()
            response = ai_client.generate_message_response(
                member_name=sender,
                conversation_history=conversation,
                member_type="member"
            )
            
            if response:
                print(f"🤖 Generated AI response: {response[:100]}...")
                
                # Send response (uncomment when ready for production)
                # messaging_service.send_text_message(sender, response)
                # print("✅ Response sent successfully")
            else:
                print("❌ Failed to generate AI response")
        else:
            print("❌ Failed to retrieve conversation history")
            
    except Exception as e:
        print(f"❌ Error processing messages: {e}")
        traceback.print_exc()
    finally:
        close_driver()

def run_payment_workflow():
    """Run the payment processing workflow."""
    print("💳 PROCESSING PAYMENTS")
    print("="*30)
    
    try:
        # Test Square connection
        if not test_square_connection():
            print("❌ Square connection failed - aborting payment workflow")
            return
        
        # Here you would implement your payment processing logic
        # For now, just test invoice creation
        square_client = get_square_client()
        
        test_invoice = square_client.create_invoice(
            member_name="Test Member",
            amount=50.00,
            member_email="test@example.com",
            description="Test Invoice"
        )
        
        if test_invoice and test_invoice.get("success"):
            print("✅ Test invoice created successfully")
            print(f"   Invoice URL: {test_invoice.get('invoice_url')}")
        else:
            print("❌ Test invoice creation failed")
            
    except Exception as e:
        print(f"❌ Error processing payments: {e}")
        traceback.print_exc()

def run_test_connections():
    """Test all service connections."""
    print("🔍 TESTING SERVICE CONNECTIONS")
    print("="*40)
    
    success = True
    
    # Test Square connection
    try:
        if test_square_connection():
            print("✅ Square API connection successful")
        else:
            print("❌ Square API connection failed")
            success = False
    except Exception as e:
        print(f"❌ Square API test error: {e}")
        success = False
    
    # Test ClubOS login
    try:
        driver = setup_driver_and_login()
        if driver:
            print("✅ ClubOS login successful")
            close_driver()
        else:
            print("❌ ClubOS login failed")
            success = False
    except Exception as e:
        print(f"❌ ClubOS login test error: {e}")
        success = False
    
    # Test Gemini AI
    try:
        ai_client = get_gemini_client()
        test_response = ai_client.generate_response("Say hello!")
        if test_response:
            print("✅ Gemini AI connection successful")
            print(f"   Test response: {test_response[:50]}...")
        else:
            print("❌ Gemini AI connection failed")
            success = False
    except Exception as e:
        print(f"❌ Gemini AI test error: {e}")
        success = False
    
    print(f"\n{'✅ All services connected successfully' if success else '❌ Some service connections failed'}")
    return success

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Gym Bot - Modular Gym Management System")
    parser.add_argument(
        "--action", 
        required=True,
        choices=[
            "test-connections",
            "process-messages", 
            "process-payments",
            "run-campaigns",
            "training-workflow"
        ],
        help="Action to perform"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,  # Changed to False for testing
        help="Run browser in headless mode (default: False)"
    )
    parser.add_argument(
        "--environment",
        choices=["sandbox", "production"],
        default="sandbox",
        help="Square API environment (default: sandbox)"
    )
    
    args = parser.parse_args()
    
    print("🏋️ GYM BOT - MODULAR SYSTEM")
    print("="*50)
    print(f"Action: {args.action}")
    print(f"Environment: {args.environment}")
    print(f"GCP Project: {GCP_PROJECT_ID}")
    print("="*50)
    
    try:
        # Initialize services
        if not initialize_services():
            print("❌ Service initialization failed - exiting")
            sys.exit(1)
        
        # Execute requested action
        if args.action == "test-connections":
            success = run_test_connections()
            sys.exit(0 if success else 1)
            
        elif args.action == "process-messages":
            run_message_processing()
            
        elif args.action == "process-payments":
            run_payment_workflow()
            
        elif args.action == "run-campaigns":
            print("📢 Campaign workflow not yet implemented")
            
        elif args.action == "training-workflow":
            print("🏋️ Training workflow not yet implemented")
        
        print("\n✅ WORKFLOW COMPLETED SUCCESSFULLY")
        
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        try:
            close_driver()
        except:
            pass

if __name__ == "__main__":
    main()
