#!/usr/bin/env python3
"""
Comprehensive Square API setup verification
Tests credential format, API endpoints, and basic connectivity
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.secrets_local import get_secret

def verify_credentials():
    """Verify credential format and structure"""
    print("🔐 CREDENTIAL VERIFICATION")
    print("=" * 50)
    
    # Get credentials using the same method as the actual code
    prod_token = get_secret("square-production-access-token")
    prod_location = get_secret("square-production-location-id")
    sandbox_token = get_secret("square-sandbox-access-token")
    sandbox_location = get_secret("square-sandbox-location-id")
    
    # Production credentials
    print(f"Production Token: {prod_token[:10] if prod_token else 'None'}...")
    print(f"Production Location: {prod_location[:10] if prod_location else 'None'}...")
    
    # Sandbox credentials
    print(f"\nSandbox Token: {sandbox_token[:10] if sandbox_token else 'None'}...")
    print(f"Sandbox Location: {sandbox_location[:10] if sandbox_location else 'None'}...")
    
    # Token format validation
    prod_valid = prod_token and prod_token.startswith('EAAA') and len(prod_token) >= 60
    sandbox_valid = sandbox_token and sandbox_token.startswith('EAAA') and len(sandbox_token) >= 60
    
    print(f"\nProduction token format: {'✅' if prod_valid else '❌'}")
    print(f"Sandbox token format: {'✅' if sandbox_valid else '❌'}")
    
    # Location ID format (should start with sq0idp- for production, sq0csp- for sandbox)
    prod_loc_valid = prod_location and (prod_location.startswith('sq0idp-') or prod_location.startswith('LCR'))
    sandbox_loc_valid = sandbox_location and sandbox_location.startswith('sq0csp-')
    
    print(f"Production location format: {'✅' if prod_loc_valid else '❌'}")
    print(f"Sandbox location format: {'✅' if sandbox_loc_valid else '❌'}")
    
    return {
        'production': {'token': prod_token, 'location': prod_location},
        'sandbox': {'token': sandbox_token, 'location': sandbox_location}
    }

def test_basic_square_import():
    """Test if Square SDK can be imported and initialized"""
    print("\n🏗️  SQUARE SDK INITIALIZATION")
    print("=" * 50)
    
    try:
        import square
        from square.environment import SquareEnvironment
        
        print("✅ Square SDK imported successfully")
        print(f"Square SDK version: {square.__version__ if hasattr(square, '__version__') else 'Unknown'}")
        
        # Test client initialization (no API calls)
        creds = verify_credentials()
        
        client = square.Square(
            token=creds['production']['token'],
            environment=SquareEnvironment.PRODUCTION
        )
        print("✅ Production client initialized")
        
        sandbox_client = square.Square(
            token=creds['sandbox']['token'],
            environment=SquareEnvironment.SANDBOX
        )
        print("✅ Sandbox client initialized")
        
        return True
    except Exception as e:
        print(f"❌ Square SDK error: {e}")
        return False

def test_simple_api_call():
    """Test the simplest possible API call - locations"""
    print("\n🌐 BASIC API CONNECTIVITY")
    print("=" * 50)
    
    creds = verify_credentials()
    
    try:
        import square
        from square.environment import SquareEnvironment
        
        # Test production environment
        print("Testing PRODUCTION environment...")
        client = square.Square(
            token=creds['production']['token'],
            environment=SquareEnvironment.PRODUCTION
        )
        
        result = client.locations.list()
        if result.is_success():
            locations = result.body.get('locations', [])
            print(f"✅ Production API working - {len(locations)} locations found")
            for loc in locations[:2]:  # Show first 2
                print(f"  - {loc.get('name', 'Unknown')} ({loc.get('id', 'No ID')})")
        else:
            print(f"❌ Production API error: {result.errors}")
            
    except Exception as e:
        print(f"❌ Production API exception: {e}")
    
    try:
        # Test sandbox environment
        print("\nTesting SANDBOX environment...")
        sandbox_client = square.Square(
            token=creds['sandbox']['token'],
            environment=SquareEnvironment.SANDBOX
        )
        
        result = sandbox_client.locations.list()
        if result.is_success():
            locations = result.body.get('locations', [])
            print(f"✅ Sandbox API working - {len(locations)} locations found")
            for loc in locations[:2]:  # Show first 2
                print(f"  - {loc.get('name', 'Unknown')} ({loc.get('id', 'No ID')})")
        else:
            print(f"❌ Sandbox API error: {result.errors}")
            
    except Exception as e:
        print(f"❌ Sandbox API exception: {e}")

if __name__ == "__main__":
    print("🔍 SQUARE API DIAGNOSTIC TOOL")
    print("=" * 50)
    
    creds = verify_credentials()
    
    if test_basic_square_import():
        test_simple_api_call()
    
    print("\n📋 NEXT STEPS:")
    print("If all credentials are valid but API calls fail:")
    print("1. Check Square Dashboard for application status")
    print("2. Verify permissions are enabled for your application")
    print("3. Check if tokens have expired")
    print("4. Ensure application is approved for production (if using production)")
