#!/usr/bin/env python3
"""
Test application startup and basic functionality
"""

import pytest
from flask import url_for

def test_app_creation(app):
    """Test that the Flask app can be created"""
    assert app is not None
    assert app.config['TESTING'] is True

def test_app_context(app):
    """Test that app context works"""
    with app.app_context():
        # Test basic app context functionality
        assert app.config is not None
        assert 'SECRET_KEY' in app.config

def test_blueprints_registered(app):
    """Test that all expected blueprints are registered"""
    expected_blueprints = [
        'auth', 'club_selection', 'dashboard', 'members', 'prospects', 
        'training', 'calendar', 'api', 'messaging', 'monitoring'
    ]
    
    for blueprint_name in expected_blueprints:
        assert blueprint_name in app.blueprints, f"Blueprint {blueprint_name} not registered"

def test_database_manager_initialized(app):
    """Test that database manager is properly initialized"""
    assert hasattr(app, 'db_manager')
    assert app.db_manager is not None

def test_monitoring_system_initialized(app):
    """Test that monitoring system is properly initialized"""
    # Check that monitoring blueprint is registered
    assert 'monitoring' in app.blueprints
    
    # Check that monitoring routes exist
    with app.app_context():
        monitoring_routes = [rule.rule for rule in app.url_map.iter_rules() 
                           if rule.rule.startswith('/monitoring')]
        expected_routes = ['/monitoring/health', '/monitoring/status', '/monitoring/metrics']
        
        for route in expected_routes:
            assert route in monitoring_routes, f"Monitoring route {route} not found"

def test_security_middleware_loaded(app):
    """Test that security middleware is properly loaded"""
    # Test that security headers are configured
    with app.test_client() as client:
        response = client.get('/monitoring/health')
        
        # Check for security headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-Content-Type-Options' in response.headers

def test_error_handlers_configured(app):
    """Test that error handlers are properly configured"""
    with app.test_client() as client:
        # Test 404 error handler
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Should return either HTML or JSON depending on request
        content_type = response.headers.get('Content-Type', '')
        assert any(ct in content_type for ct in ['text/html', 'application/json'])

class TestServicesInitialization:
    """Test that all services are properly initialized"""
    
    def test_training_package_cache(self, app):
        """Test training package cache initialization"""
        assert hasattr(app, 'training_package_cache')
        assert app.training_package_cache is not None
    
    def test_clubos_integration(self, app):
        """Test ClubOS integration initialization"""
        assert hasattr(app, 'clubos')
        # Note: ClubOS might not initialize in test environment, which is OK
    
    def test_data_cache_initialized(self, app):
        """Test that data cache is initialized"""
        assert hasattr(app, 'data_cache')
        assert isinstance(app.data_cache, dict)
        
        # Check expected cache structure
        expected_keys = ['messages', 'members', 'prospects', 'training_clients', 'last_sync']
        for key in expected_keys:
            assert key in app.data_cache

class TestConfigurationSafety:
    """Test that configuration is production-safe"""
    
    def test_secret_key_configured(self, app):
        """Test that secret key is properly configured"""
        assert app.secret_key is not None
        assert len(app.secret_key) > 10  # Ensure it's not a default short key
    
    def test_database_path_configured(self, app):
        """Test that database path is configured"""
        assert 'DATABASE_PATH' in app.config
        assert app.config['DATABASE_PATH'] is not None
    
    def test_session_configuration(self, app):
        """Test that session configuration is secure"""
        # Check session cookie settings
        assert app.config.get('SESSION_COOKIE_HTTPONLY') is True
        assert app.config.get('SESSION_COOKIE_SAMESITE') is not None
    
    def test_square_configuration(self, app):
        """Test Square integration configuration"""
        # Square should be available or safely disabled
        square_available = app.config.get('SQUARE_AVAILABLE', False)
        if square_available:
            assert app.config.get('SQUARE_CLIENT') is not None
        else:
            # If not available, it should be safely None
            assert app.config.get('SQUARE_CLIENT') is None