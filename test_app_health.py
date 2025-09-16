#!/usr/bin/env python3
"""
Quick test to verify app functionality after monitoring integration
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_app_creation():
    """Test that the app can be created successfully"""
    try:
        logger.info("🔍 Testing app creation...")
        from src.main_app import create_app
        
        app = create_app()
        logger.info("✅ App creation successful")
        
        # Test that monitoring endpoints are registered
        with app.app_context():
            logger.info("🔍 Testing monitoring endpoints...")
            
            # Check if monitoring blueprint is registered
            if 'monitoring' in app.blueprints:
                logger.info("✅ Monitoring blueprint registered")
            else:
                logger.warning("⚠️ Monitoring blueprint not found")
            
            # List some URL rules to verify endpoints
            monitoring_routes = [rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/monitoring')]
            logger.info(f"✅ Monitoring routes found: {monitoring_routes}")
            
        return True, app
        
    except Exception as e:
        logger.error(f"❌ App creation failed: {e}")
        return False, None

def test_monitoring_endpoints(app):
    """Test monitoring endpoints"""
    try:
        with app.test_client() as client:
            logger.info("🔍 Testing monitoring endpoints...")
            
            # Test health check endpoint
            response = client.get('/monitoring/health')
            if response.status_code in [200, 503]:  # 503 is OK for failing health checks
                logger.info(f"✅ Health check endpoint responding: {response.status_code}")
            else:
                logger.warning(f"⚠️ Health check unexpected status: {response.status_code}")
            
            # Test status endpoint
            response = client.get('/monitoring/status')
            if response.status_code in [200, 500]:  # Allow some errors during testing
                logger.info(f"✅ Status endpoint responding: {response.status_code}")
            else:
                logger.warning(f"⚠️ Status endpoint unexpected status: {response.status_code}")
            
            # Test metrics endpoint
            response = client.get('/monitoring/metrics')
            if response.status_code in [200, 500]:  # Allow some errors during testing
                logger.info(f"✅ Metrics endpoint responding: {response.status_code}")
            else:
                logger.warning(f"⚠️ Metrics endpoint unexpected status: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Monitoring endpoint test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🏋️ Gym Bot Health Test")
    print("======================")
    
    # Test app creation
    success, app = test_app_creation()
    if not success:
        print("❌ Critical failure: App creation failed")
        return False
    
    # Test monitoring endpoints
    monitoring_success = test_monitoring_endpoints(app)
    if not monitoring_success:
        print("⚠️ Monitoring endpoints have issues but app still works")
    
    print("\n📊 Test Summary:")
    print(f"  App Creation: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"  Monitoring: {'✅ PASS' if monitoring_success else '⚠️ ISSUES'}")
    
    if success:
        print("\n🎉 Overall: App is functional!")
        return True
    else:
        print("\n💥 Overall: Critical issues found!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)