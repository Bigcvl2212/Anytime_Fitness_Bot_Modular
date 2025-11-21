#!/usr/bin/env python3
"""
Test script for the modular dashboard structure
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        logger.info("🧪 Testing module imports...")
        
        # Test configuration
        from .config.settings import create_app_config
        logger.info("✅ config.settings imported successfully")
        
        # Test services
        from .services.database_manager import DatabaseManager
        logger.info("✅ services.database_manager imported successfully")
        
        from .services.training_package_cache import TrainingPackageCache
        logger.info("✅ services.training_package_cache imported successfully")
        
        from .services.clubos_integration import ClubOSIntegration
        logger.info("✅ services.clubos_integration imported successfully")
        
        # Test routes
        from .routes import register_blueprints
        logger.info("✅ routes package imported successfully")
        
        from .routes.dashboard import dashboard_bp
        logger.info("✅ routes.dashboard imported successfully")
        
        from .routes.members import members_bp
        logger.info("✅ routes.members imported successfully")
        
        from .routes.api import api_bp
        logger.info("✅ routes.api imported successfully")
        
        # Test utilities
        from .utils.data_import import classify_member_status, import_fresh_clubhub_data
        logger.info("✅ utils.data_import imported successfully")
        
        logger.info("🎉 All module imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def test_database_manager():
    """Test database manager functionality."""
    try:
        logger.info("🧪 Testing database manager...")
        
        from .services.database_manager import DatabaseManager
        
        # Create a test database manager
        db_manager = DatabaseManager('test_gym_bot.db')
        logger.info("✅ Database manager created successfully")
        
        # Test database operations
        member_count = db_manager.get_member_count()
        logger.info(f"✅ Member count: {member_count}")
        
        prospect_count = db_manager.get_prospect_count()
        logger.info(f"✅ Prospect count: {prospect_count}")
        
        # Clean up test database
        if os.path.exists('test_gym_bot.db'):
            os.remove('test_gym_bot.db')
            logger.info("✅ Test database cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database manager test failed: {e}")
        return False

def test_training_cache():
    """Test training package cache functionality."""
    try:
        logger.info("🧪 Testing training package cache...")
        
        from .services.training_package_cache import TrainingPackageCache
        
        # Create a test cache
        cache = TrainingPackageCache()
        logger.info("✅ Training package cache created successfully")
        
        # Test cache status
        cache_status = cache.get_cache_status()
        logger.info(f"✅ Cache status: {cache_status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Training cache test failed: {e}")
        return False

def test_clubos_integration():
    """Test ClubOS integration functionality."""
    try:
        logger.info("🧪 Testing ClubOS integration...")
        
        from .services.clubos_integration import ClubOSIntegration
        
        # Create ClubOS integration
        clubos = ClubOSIntegration()
        logger.info("✅ ClubOS integration created successfully")
        
        # Test connection status
        status = clubos.get_connection_status()
        logger.info(f"✅ Connection status: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ClubOS integration test failed: {e}")
        return False

def test_utility_functions():
    """Test utility functions."""
    try:
        logger.info("🧪 Testing utility functions...")
        
        from .utils.data_import import classify_member_status
        
        # Test member classification
        test_member = {
            'statusMessage': 'Active Member',
            'status': 'Active'
        }
        
        category = classify_member_status(test_member)
        logger.info(f"✅ Member classification: {category}")
        
        # Test with different status
        test_member2 = {
            'statusMessage': 'Pay Per Visit',
            'status': 'Active'
        }
        
        category2 = classify_member_status(test_member2)
        logger.info(f"✅ Member classification 2: {category2}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Utility functions test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting modular dashboard tests...")
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Manager", test_database_manager),
        ("Training Cache", test_training_cache),
        ("ClubOS Integration", test_clubos_integration),
        ("Utility Functions", test_utility_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Test Results: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Modular structure is working correctly.")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
