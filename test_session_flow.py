#!/usr/bin/env python3
"""
Test the complete session flow: login → club selection → members page
"""
import sys
import os
import logging
import requests
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_session_flow():
    """Test complete session flow to see where it breaks"""
    logger.info("🧪 Testing complete session flow...")
    
    # Create session to maintain cookies
    session = requests.Session()
    base_url = "http://localhost:5000"
    
    try:
        # Step 1: Get login page
        logger.info("📥 Step 1: Getting login page...")
        login_page = session.get(f"{base_url}/login")
        logger.info(f"Login page status: {login_page.status_code}")
        logger.info(f"Login page cookies: {list(login_page.cookies.keys())}")
        
        # Step 2: Submit login form 
        logger.info("🔐 Step 2: Submitting login...")
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        
        login_data = {
            'clubos_username': username,
            'clubos_password': password,
            'clubhub_email': username,  # Using same username as email
            'clubhub_password': password
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        logger.info(f"Login response status: {login_response.status_code}")
        logger.info(f"Login response location: {login_response.headers.get('Location')}")
        logger.info(f"Login response cookies: {list(session.cookies.keys())}")
        
        if login_response.status_code == 302:
            # Follow redirect
            redirect_url = login_response.headers.get('Location')
            if redirect_url:
                if redirect_url.startswith('/'):
                    redirect_url = base_url + redirect_url
                
                logger.info(f"🔄 Step 3: Following login redirect to {redirect_url}")
                redirect_response = session.get(redirect_url, allow_redirects=False)
                logger.info(f"Redirect response status: {redirect_response.status_code}")
                logger.info(f"Redirect response cookies: {list(session.cookies.keys())}")
                
                # If redirected to club selection, handle it
                if 'club-selection' in redirect_url:
                    logger.info("🏢 Step 4: Handling club selection...")
                    
                    # Get club selection page
                    club_page = session.get(redirect_url)
                    logger.info(f"Club selection page status: {club_page.status_code}")
                    
                    # Simulate selecting clubs (you may need to adjust this based on your form)
                    select_data = {'clubs': ['your-club-id']}  # Replace with actual club ID
                    select_response = session.post(f"{base_url}/select-clubs", json=select_data, allow_redirects=False)
                    logger.info(f"Club selection response status: {select_response.status_code}")
                    logger.info(f"Club selection response: {select_response.text[:200]}")
                    
                    # Small delay
                    time.sleep(1)
                
        # Step 5: Try to access dashboard
        logger.info("📊 Step 5: Accessing dashboard...")
        dashboard_response = session.get(f"{base_url}/dashboard", allow_redirects=False)
        logger.info(f"Dashboard response status: {dashboard_response.status_code}")
        logger.info(f"Dashboard response location: {dashboard_response.headers.get('Location')}")
        logger.info(f"Dashboard response cookies: {list(session.cookies.keys())}")
        
        # Step 6: Try to access members page (the failing one)
        logger.info("👥 Step 6: Accessing members page...")
        members_response = session.get(f"{base_url}/members", allow_redirects=False)
        logger.info(f"Members response status: {members_response.status_code}")
        logger.info(f"Members response location: {members_response.headers.get('Location')}")
        
        if members_response.status_code == 302:
            location = members_response.headers.get('Location')
            if 'login' in location:
                logger.error("❌ PROBLEM: Members page redirecting to login!")
                logger.error(f"❌ Redirect location: {location}")
                
                # Check session cookies
                logger.info(f"Session cookies at failure: {dict(session.cookies)}")
                
                # Try to understand what's happening
                logger.info("🔍 Investigating session state...")
                
            else:
                logger.info(f"✅ Members page working: redirected to {location}")
        else:
            logger.info(f"✅ Members page response: {members_response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Session flow test failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    test_full_session_flow()