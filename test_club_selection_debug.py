#!/usr/bin/env python3
"""
Debug club selection issue - Test the flow locally with minimal setup
"""

import os
import sys
sys.path.append('.')

# Set environment for local development
os.environ['LOCAL_DEVELOPMENT'] = 'true'
os.environ['DB_TYPE'] = 'sqlite'
os.environ['SQLITE_DB_PATH'] = 'gym_bot_debug.db'

from flask import Flask, session
from src.routes.club_selection import club_selection_bp
from src.routes.auth import auth_bp 
from src.routes.dashboard import dashboard_bp
from src.services.multi_club_manager import multi_club_manager

def test_club_selection_issue():
    """Test club selection components locally"""
    
    print("🔧 Testing Club Selection Issue")
    print("=" * 50)
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.secret_key = 'test-secret-key-for-debugging'
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(club_selection_bp)
    app.register_blueprint(dashboard_bp)
    
    with app.app_context():
        print("✅ Flask app context created")
        
        # Test 1: Check multi_club_manager
        try:
            print("\n1. Testing multi_club_manager...")
            available_clubs = multi_club_manager.get_available_clubs_for_selection()
            print(f"   Available clubs: {available_clubs}")
            
            user_summary = multi_club_manager.get_user_summary()
            print(f"   User summary: {user_summary}")
            
        except Exception as e:
            print(f"   ❌ Multi-club manager error: {e}")
            import traceback
            print(f"   Error details: {traceback.format_exc()}")
        
        # Test 2: Check database connection
        try:
            print("\n2. Testing database connection...")
            from src.services.database_manager import DatabaseManager
            db = DatabaseManager()
            print(f"   Database type: {db.db_type}")
            print(f"   Database path: {getattr(db, 'db_path', 'N/A')}")
            
            # Test basic query
            result = db.execute_query("SELECT 1 as test", fetch_one=True)
            print(f"   Database test query result: {result}")
            
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            import traceback  
            print(f"   Error details: {traceback.format_exc()}")
        
        # Test 3: Check authentication service
        try:
            print("\n3. Testing authentication service...")
            from src.services.authentication.secure_auth_service import SecureAuthService
            auth_service = SecureAuthService()
            print("   ✅ Authentication service loaded")
            
            # Create a test session
            with app.test_request_context('/test'):
                session['authenticated'] = True
                session['manager_id'] = 'test_manager_123'
                session['user_info'] = {'name': 'Test Manager', 'club_access': ['club1', 'club2']}
                
                is_valid, manager_id = auth_service.validate_session()
                print(f"   Session validation: is_valid={is_valid}, manager_id={manager_id}")
            
        except Exception as e:
            print(f"   ❌ Authentication service error: {e}")
            import traceback
            print(f"   Error details: {traceback.format_exc()}")
        
        print("\n" + "=" * 50)
        print("🏁 Test completed!")

if __name__ == "__main__":
    test_club_selection_issue()