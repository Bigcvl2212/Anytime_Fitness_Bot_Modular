"""
Enhanced Gym Bot Main Application - API Migration Enabled
Entry point for the modular Gym Bot application with full API support.
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
try:
    from config.migration_config import (
        get_migration_mode, 
        MIGRATION_CONFIG,
        WORKFLOW_MIGRATION_CONFIG
    )
    # Import enhanced API-based workflows
    from workflows.overdue_payments_enhanced import (
        process_overdue_payments_api,
        compare_api_vs_selenium_payments
    )
    from src.services.api.migration_service import get_migration_service
except ImportError as e:
    print(f"Warning: Some enhanced features not available: {e}")
    # Define stub functions
    def get_migration_mode(): return "selenium"
    MIGRATION_CONFIG = {}
    WORKFLOW_MIGRATION_CONFIG = {}
    def process_overdue_payments_api(): return False
    def compare_api_vs_selenium_payments(): return False
    def get_migration_service(): return None


def initialize_services() -> bool:
    """
    Initialize all required services including API migration services.
    
    Returns:
        bool: True if all services initialized successfully
    """
    print("🔧 INITIALIZING SERVICES (API-ENHANCED)")
    print("="*40)
    
    success = True
    
    # Initialize Gemini AI
    try:
        ai_client = get_gemini_client()
        print("✅ Gemini AI service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini AI: {e}")
        success = False
    
    # Initialize Square payments
    try:
        square_client = get_square_client()
        if square_client.test_connection():
            print("✅ Square payment service initialized")
        else:
            print("❌ Square payment service connection failed")
            success = False
    except Exception as e:
        print(f"❌ Failed to initialize Square payments: {e}")
        success = False
    
    # Initialize API migration service
    try:
        migration_mode = get_migration_mode()
        migration_service = get_migration_service(migration_mode)
        migration_stats = migration_service.get_migration_stats()
        print(f"✅ API migration service initialized (mode: {migration_mode})")
        print(f"   API operations: {migration_stats['api_attempts']}")
        print(f"   Success rate: {migration_stats['api_success_rate']:.1f}%")
    except Exception as e:
        print(f"⚠️ API migration service warning: {e}")
        print("   Falling back to Selenium-only mode")
        # Don't fail initialization, just warn
    
    print(f"{'✅ Services initialized successfully' if success else '❌ Some services failed to initialize'}")
    return success


def setup_driver_and_login_enhanced():
    """
    Enhanced setup that tries API authentication first, falls back to WebDriver.
    
    Returns:
        WebDriver instance or None if both methods failed
    """
    try:
        print("🚀 SETTING UP AUTHENTICATION (API-ENHANCED)")
        print("="*40)
        
        # Try API authentication first
        try:
            migration_service = get_migration_service()
            if migration_service.api_service:
                print("✅ API authentication successful - no WebDriver needed")
                return "API_MODE"  # Special indicator for API mode
        except Exception as e:
            print(f"⚠️ API authentication failed: {e}")
            print("   Falling back to WebDriver authentication...")
        
        # Fallback to WebDriver
        driver = get_driver(headless=False)
        
        # Login to ClubOS
        if login_to_clubos(driver):
            print("✅ Successfully logged into ClubOS via WebDriver")
            return driver
        else:
            print("❌ Failed to login to ClubOS")
            close_driver()
            return None
            
    except Exception as e:
        print(f"❌ Error setting up authentication: {e}")
        close_driver()
        return None


def run_message_processing_enhanced(migration_mode: str = None):
    """Enhanced message processing with API support."""
    print("📬 PROCESSING MESSAGES (API-ENHANCED)")
    print("="*30)
    
    if migration_mode is None:
        migration_mode = get_migration_mode("member_messaging")
    
    try:
        # Get migration service
        migration_service = get_migration_service(migration_mode)
        
        # Get last message sender using API/hybrid approach
        sender = migration_service.get_last_message_sender()
        if not sender:
            print("📭 No new messages to process")
            return
        
        print(f"📧 Processing message from: {sender}")
        
        # Get conversation history using API/hybrid approach
        conversation = migration_service.get_member_conversation(sender)
        
        if conversation:
            print(f"✅ Retrieved {len(conversation)} messages from conversation")
            
            # Generate AI response
            ai_client = get_gemini_client()
            response = ai_client.generate_message_response(
                member_name=sender,
                conversation_history=conversation,
                member_type="member"
            )
            
            if response:
                print(f"🤖 Generated AI response: {response[:100]}...")
                
                # Send response using migration service
                success = migration_service.send_message(
                    member_name=sender,
                    subject="Re: Your Message",
                    body=response
                )
                
                if success:
                    print("✅ Response sent successfully")
                else:
                    print("❌ Failed to send response")
            else:
                print("❌ Failed to generate AI response")
        else:
            print("❌ Failed to retrieve conversation history")
            
        # Print migration statistics
        stats = migration_service.get_migration_stats()
        print(f"\n📊 Session Stats: {stats['api_attempts']} API calls, {stats['selenium_fallbacks']} fallbacks")
            
    except Exception as e:
        print(f"❌ Error processing messages: {e}")
        traceback.print_exc()


def run_payment_workflow_enhanced(migration_mode: str = None):
    """Enhanced payment processing with API support."""
    print("💳 PROCESSING PAYMENTS (API-ENHANCED)")
    print("="*30)
    
    if migration_mode is None:
        migration_mode = get_migration_mode("overdue_payments")
    
    try:
        # Test Square connection
        if not test_square_connection():
            print("❌ Square connection failed - aborting payment workflow")
            return
        
        # Run enhanced overdue payments workflow
        print(f"🔄 Running overdue payments in {migration_mode} mode...")
        success = process_overdue_payments_api(migration_mode)
        
        if success:
            print("✅ Overdue payments processed successfully")
        else:
            print("❌ Overdue payments processing failed")
            
        # Get migration statistics
        migration_service = get_migration_service(migration_mode)
        stats = migration_service.get_migration_stats()
        
        print(f"\n📊 Payment Workflow Stats:")
        print(f"   API operations: {stats['api_attempts']}")
        print(f"   API success rate: {stats['api_success_rate']:.1f}%")
        print(f"   Selenium fallbacks: {stats['selenium_fallbacks']}")
        
        # Save migration report
        migration_service.save_migration_report()
            
    except Exception as e:
        print(f"❌ Error processing payments: {e}")
        traceback.print_exc()


def run_api_testing():
    """Run API vs Selenium testing and comparison."""
    print("🧪 RUNNING API TESTING SUITE")
    print("="*30)
    
    try:
        # Import test suite
        from test_api_vs_selenium import APISeleniumTestSuite
        
        # Run comprehensive tests
        test_suite = APISeleniumTestSuite()
        results = test_suite.run_all_tests()
        
        print(f"\n📊 TEST RESULTS SUMMARY:")
        print(f"   Tests run: {results['tests_run']}")
        print(f"   Tests passed: {results['tests_passed']}")
        print(f"   Tests failed: {results['tests_failed']}")
        print(f"   Success rate: {(results['tests_passed']/max(results['tests_run'],1))*100:.1f}%")
        
        return results['overall_success']
        
    except Exception as e:
        print(f"❌ Error running API tests: {e}")
        return False


def run_api_discovery():
    """Run API endpoint discovery."""
    print("🔍 RUNNING API DISCOVERY")
    print("="*30)
    
    try:
        # Import discovery tool
        from discover_clubos_api import ClubOSAPIDiscovery
        from gym_bot.config.constants import CLUBOS_USERNAME_SECRET, CLUBOS_PASSWORD_SECRET
        from gym_bot.config.secrets import get_secret
        
        username = get_secret(CLUBOS_USERNAME_SECRET)
        password = get_secret(CLUBOS_PASSWORD_SECRET)
        
        if not username or not password:
            print("❌ ClubOS credentials not available")
            return False
        
        # Run discovery
        discovery = ClubOSAPIDiscovery(username, password)
        results = discovery.run_complete_discovery()
        
        print(f"\n🔍 DISCOVERY RESULTS:")
        print(f"   Endpoints discovered: {len(discovery.discovered_endpoints)}")
        print(f"   Tests completed: {results.get('endpoint_tests', {}).get('tested_count', 0)}")
        print(f"   Recommendations: {len(results.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running API discovery: {e}")
        return False


def run_payment_comparison():
    """Run payment workflow comparison between API and Selenium."""
    print("⚖️ COMPARING PAYMENT WORKFLOWS")
    print("="*30)
    
    try:
        # Run comparison
        results = compare_api_vs_selenium_payments(test_member_count=3)
        
        if "error" in results:
            print(f"❌ Comparison failed: {results['error']}")
            return False
        
        print(f"\n📊 COMPARISON RESULTS:")
        print(f"   Members tested: {results['test_member_count']}")
        print(f"   API avg time: {results.get('avg_api_time', 0):.2f}s")
        print(f"   Selenium avg time: {results.get('avg_selenium_time', 0):.2f}s")
        print(f"   API success rate: {results.get('api_success_rate', 0):.1f}%")
        print(f"   Selenium success rate: {results.get('selenium_success_rate', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running payment comparison: {e}")
        return False


def run_test_connections_enhanced():
    """Enhanced connection testing including API services."""
    print("🔍 TESTING ALL CONNECTIONS (API-ENHANCED)")
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
    
    # Test API migration service
    try:
        migration_service = get_migration_service("api_only")
        print("✅ API migration service initialized")
        
        # Test API authentication
        if hasattr(migration_service, 'api_service') and migration_service.api_service:
            print("✅ ClubOS API authentication successful")
        else:
            print("❌ ClubOS API authentication failed")
            success = False
            
    except Exception as e:
        print(f"❌ API migration service test error: {e}")
        success = False
    
    # Test Selenium (fallback)
    try:
        auth_result = setup_driver_and_login_enhanced()
        if auth_result == "API_MODE":
            print("✅ API mode - no WebDriver needed")
        elif auth_result:
            print("✅ ClubOS Selenium login successful")
            if auth_result != "API_MODE":
                close_driver()
        else:
            print("❌ ClubOS Selenium login failed")
            success = False
    except Exception as e:
        print(f"❌ Selenium login test error: {e}")
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
    """Enhanced main application entry point with API support."""
    parser = argparse.ArgumentParser(description="Gym Bot - Enhanced API-Supported System")
    parser.add_argument(
        "--action", 
        required=True,
        choices=[
            "test-connections",
            "process-messages", 
            "process-payments",
            "run-campaigns",
            "training-workflow",
            "api-testing",
            "api-discovery", 
            "payment-comparison"
        ],
        help="Action to perform"
    )
    parser.add_argument(
        "--migration-mode",
        choices=["api_only", "hybrid", "selenium_only", "testing"],
        help="Override migration mode for this session"
    )
    parser.add_argument(
        "--environment",
        choices=["sandbox", "production", "testing", "development"],
        default="sandbox",
        help="Environment configuration (default: sandbox)"
    )
    
    args = parser.parse_args()
    
    # Set environment variable for configuration
    import os
    os.environ["ENVIRONMENT"] = args.environment
    if args.migration_mode:
        os.environ["MIGRATION_MODE"] = args.migration_mode
    
    print("🏋️ GYM BOT - API-ENHANCED SYSTEM")
    print("="*50)
    print(f"Action: {args.action}")
    print(f"Environment: {args.environment}")
    print(f"Migration Mode: {args.migration_mode or get_migration_mode()}")
    print(f"GCP Project: {GCP_PROJECT_ID}")
    print("="*50)
    
    try:
        # Initialize services
        if not initialize_services():
            print("❌ Service initialization failed - exiting")
            sys.exit(1)
        
        # Execute requested action
        if args.action == "test-connections":
            success = run_test_connections_enhanced()
            sys.exit(0 if success else 1)
            
        elif args.action == "process-messages":
            run_message_processing_enhanced(args.migration_mode)
            
        elif args.action == "process-payments":
            run_payment_workflow_enhanced(args.migration_mode)
            
        elif args.action == "api-testing":
            success = run_api_testing()
            sys.exit(0 if success else 1)
            
        elif args.action == "api-discovery":
            success = run_api_discovery()
            sys.exit(0 if success else 1)
            
        elif args.action == "payment-comparison":
            success = run_payment_comparison()
            sys.exit(0 if success else 1)
            
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