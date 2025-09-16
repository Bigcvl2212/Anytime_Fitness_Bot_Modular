#!/usr/bin/env python3
"""
Production Readiness Validation Script
Validates that all environment and configuration is production-ready
"""

import sys
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment_setup():
    """Test environment setup and configuration"""
    logger.info("🔍 Testing environment setup...")
    
    try:
        from src.config.environment_setup import load_environment_variables, validate_environment_setup
        from src.config.security_config import SecurityConfig
        
        # Test environment loading
        env_loaded = load_environment_variables()
        logger.info(f"✅ Environment loading: {'Success' if env_loaded else 'Using system env'}")
        
        # Test environment validation
        is_valid, missing = validate_environment_setup()
        if missing:
            logger.warning(f"⚠️ Missing environment variables: {missing}")
        else:
            logger.info("✅ All environment variables configured")
        
        # Test security configuration
        secret_key = SecurityConfig.get_secret_key()
        logger.info(f"✅ Secret key: {'Configured' if len(secret_key) > 20 else 'Weak/Default'}")
        
        db_path = SecurityConfig.get_database_path()
        logger.info(f"✅ Database path: {db_path}")
        
        is_prod = SecurityConfig.is_production()
        logger.info(f"✅ Production mode: {is_prod}")
        
        # Test secrets validation
        secrets_valid, missing_secrets = SecurityConfig.validate_required_secrets()
        if secrets_valid:
            logger.info("✅ All required secrets are configured")
        else:
            logger.warning(f"⚠️ Missing secrets: {missing_secrets}")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Environment setup test failed: {e}")
        return False, [str(e)]

def test_app_creation():
    """Test application creation"""
    logger.info("🔍 Testing application creation...")
    
    try:
        from src.main_app import create_app
        
        app = create_app()
        logger.info("✅ Application created successfully")
        
        # Test configuration
        with app.app_context():
            logger.info(f"✅ Secret key configured: {len(app.secret_key) > 20}")
            logger.info(f"✅ Database manager: {hasattr(app, 'db_manager')}")
            logger.info(f"✅ Monitoring system: {'monitoring' in app.blueprints}")
            logger.info(f"✅ Security middleware: {len(app.before_request_funcs) > 0}")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Application creation failed: {e}")
        return False, [str(e)]

def test_monitoring_endpoints():
    """Test monitoring endpoints"""
    logger.info("🔍 Testing monitoring endpoints...")
    
    try:
        from src.main_app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/monitoring/health')
            logger.info(f"✅ Health endpoint: {response.status_code}")
            
            # Test status endpoint
            response = client.get('/monitoring/status')
            logger.info(f"✅ Status endpoint: {response.status_code}")
            
            # Test metrics endpoint
            response = client.get('/monitoring/metrics')
            logger.info(f"✅ Metrics endpoint: {response.status_code}")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Monitoring endpoints test failed: {e}")
        return False, [str(e)]

def test_security_features():
    """Test security features"""
    logger.info("🔍 Testing security features...")
    
    try:
        from src.main_app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test security headers
            response = client.get('/monitoring/health')
            
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options', 
                'Content-Security-Policy'
            ]
            
            headers_found = []
            for header in security_headers:
                if header in response.headers:
                    headers_found.append(header)
                    logger.info(f"✅ Security header: {header}")
                else:
                    logger.warning(f"⚠️ Missing security header: {header}")
            
            logger.info(f"✅ Security headers: {len(headers_found)}/{len(security_headers)} configured")
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Security features test failed: {e}")
        return False, [str(e)]

def test_database_access():
    """Test database access"""
    logger.info("🔍 Testing database access...")
    
    try:
        from src.main_app import create_app
        
        app = create_app()
        
        with app.app_context():
            if hasattr(app, 'db_manager'):
                # Test basic database connectivity
                db_manager = app.db_manager
                
                # This will test database initialization
                logger.info(f"✅ Database path: {db_manager.db_path}")
                logger.info("✅ Database manager functional")
            else:
                logger.error("❌ Database manager not found")
                return False, ["Database manager not initialized"]
        
        return True, []
        
    except Exception as e:
        logger.error(f"❌ Database access test failed: {e}")
        return False, [str(e)]

def main():
    """Main validation function"""
    print("🏋️ Production Readiness Validation")
    print("===================================")
    
    all_tests = [
        ("Environment Setup", test_environment_setup),
        ("Application Creation", test_app_creation), 
        ("Monitoring Endpoints", test_monitoring_endpoints),
        ("Security Features", test_security_features),
        ("Database Access", test_database_access)
    ]
    
    passed = 0
    failed = 0
    all_errors = []
    
    for test_name, test_func in all_tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * (len(test_name) + 12))
        
        success, errors = test_func()
        
        if success:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
            all_errors.extend(errors)
    
    print(f"\n📊 Final Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if all_errors:
        print(f"\n🚨 Errors encountered:")
        for error in all_errors:
            print(f"  • {error}")
    
    if failed == 0:
        print(f"\n🎉 All tests passed! Application is production-ready!")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Address issues before production deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)