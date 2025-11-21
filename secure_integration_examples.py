"""
Integration Example: How to Use Secure Credentials in Existing Services

This file demonstrates how to integrate the new secure credential system
with existing ClubOS and ClubHub services.
"""

# Example 1: Updating existing ClubOS API usage
def example_clubos_integration():
    """
    Example of how to update existing ClubOS API calls to use secure credentials
    """
    print("🏢 ClubOS Integration Example")
    
    # OLD WAY (insecure hardcoded credentials)
    # from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD
    
    # NEW WAY (secure credential service)
    from src.services.authentication.secure_credential_service import get_clubos_credentials
    
    username, password = get_clubos_credentials()
    
    if username and password:
        print(f"✅ Retrieved ClubOS credentials for user: {username}")
        # Your existing ClubOS API code here
        # api_client.login(username, password)
    else:
        print("❌ No authenticated manager found. Please login first.")
        return None


# Example 2: Updating existing ClubHub API usage  
def example_clubhub_integration():
    """
    Example of how to update existing ClubHub API calls to use secure credentials
    """
    print("📱 ClubHub Integration Example")
    
    # OLD WAY (insecure hardcoded credentials)
    # from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
    
    # NEW WAY (secure credential service)
    from src.services.authentication.secure_credential_service import get_clubhub_credentials
    
    email, password = get_clubhub_credentials()
    
    if email and password:
        print(f"✅ Retrieved ClubHub credentials for: {email}")
        # Your existing ClubHub API code here
        # clubhub_client.login(email, password)
    else:
        print("❌ No authenticated manager found. Please login first.")
        return None


# Example 3: Backward compatibility with get_secret function
def example_legacy_secret_access():
    """
    Example of how the legacy get_secret function still works
    """
    print("🔑 Legacy Secret Access Example")
    
    from src.services.authentication.secure_credential_service import get_secret
    
    # This will first try to get from authenticated session,
    # then fall back to Google Secret Manager legacy secrets
    square_token = get_secret('square-production-access-token')
    
    if square_token:
        print("✅ Retrieved Square token from secure storage")
    else:
        print("❌ Square token not found")


# Example 4: Check if manager is authenticated
def example_authentication_check():
    """
    Example of how to check if there's an authenticated manager
    """
    print("🔐 Authentication Check Example")
    
    from src.services.authentication.secure_credential_service import is_authenticated, get_current_manager_id
    
    if is_authenticated():
        manager_id = get_current_manager_id()
        print(f"✅ Manager {manager_id} is authenticated")
        return True
    else:
        print("❌ No authenticated session. Redirect to login.")
        return False


# Example 5: Integration with existing ClubOS Calendar API
def example_calendar_api_integration():
    """
    Example of integrating with the existing calendar API
    """
    print("📅 Calendar API Integration Example")
    
    from src.services.authentication.secure_credential_service import get_clubos_credentials, is_authenticated
    
    if not is_authenticated():
        print("❌ Authentication required for calendar access")
        return None
    
    username, password = get_clubos_credentials()
    
    if username and password:
        print(f"✅ Initializing calendar API for user: {username}")
        
        # Example integration with your existing calendar code
        # from clubos_real_calendar_api import ClubOSRealCalendarAPI
        # calendar_api = ClubOSRealCalendarAPI()
        # calendar_api.authenticate(username, password)
        # events = calendar_api.get_events()
        
        return "Calendar API ready"
    else:
        print("❌ Failed to retrieve credentials")
        return None


# Example 6: Secure credential access in Flask routes
def example_flask_route_integration():
    """
    Example of how to use secure credentials in Flask routes
    """
    print("🌐 Flask Route Integration Example")
    
    from flask import Flask, jsonify, session
    from src.services.authentication.secure_credential_service import get_clubos_credentials, is_authenticated
    
    app = Flask(__name__)
    
    @app.route('/api/members')
    def get_members():
        # Check authentication first
        if not is_authenticated():
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get credentials securely
        username, password = get_clubos_credentials()
        
        if not username or not password:
            return jsonify({'error': 'Credentials not available'}), 500
        
        # Use credentials for API calls
        try:
            # Your existing member retrieval code here
            # members = clubos_api.get_members(username, password)
            members = ["Example Member 1", "Example Member 2"]  # Placeholder
            
            return jsonify({
                'success': True,
                'members': members,
                'authenticated_as': username
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    print("✅ Flask route configured with secure credentials")


# Migration Steps for Existing Services
def migration_guide():
    """
    Step-by-step migration guide for existing services
    """
    print("📋 MIGRATION GUIDE")
    print("=" * 50)
    
    steps = [
        "1. Replace hardcoded imports:",
        "   OLD: from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD",
        "   NEW: from src.services.authentication.secure_credential_service import get_clubos_credentials",
        "",
        "2. Update credential access:",
        "   OLD: username = CLUBOS_USERNAME",
        "   NEW: username, password = get_clubos_credentials()",
        "",
        "3. Add authentication checks:",
        "   from src.services.authentication.secure_credential_service import is_authenticated",
        "   if not is_authenticated():",
        "       return redirect('/login')",
        "",
        "4. Update error handling:",
        "   if not username or not password:",
        "       return {'error': 'Please login to access this feature'}",
        "",
        "5. Test the integration:",
        "   - Start the secure dashboard app",
        "   - Register/login with manager credentials", 
        "   - Test your existing API calls",
        ""
    ]
    
    for step in steps:
        print(step)


if __name__ == "__main__":
    print("🔐 Secure Credential Integration Examples")
    print("=" * 50)
    
    # Run all examples
    example_clubos_integration()
    print()
    example_clubhub_integration()
    print()
    example_legacy_secret_access()
    print()
    example_authentication_check()
    print()
    example_calendar_api_integration()
    print()
    example_flask_route_integration()
    print()
    migration_guide()