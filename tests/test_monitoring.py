#!/usr/bin/env python3
"""
Test monitoring endpoints and health checks
"""

import pytest
import json

class TestMonitoringEndpoints:
    """Test all monitoring endpoints"""
    
    def test_health_check_endpoint(self, client):
        """Test main health check endpoint"""
        response = client.get('/monitoring/health')
        assert response.status_code in [200, 503]  # 503 is acceptable for some failing checks
        
        # Verify JSON structure
        data = response.get_json()
        assert 'status' in data
        assert 'timestamp' in data
        assert 'uptime_seconds' in data
        assert 'checks' in data
        
        # Verify status is valid
        assert data['status'] in ['healthy', 'unhealthy']
        
        # Verify checks structure
        assert isinstance(data['checks'], dict)
        expected_checks = ['database', 'secrets_manager', 'square_integration', 'system_resources', 'flask_app']
        
        for check_name in expected_checks:
            assert check_name in data['checks'], f"Health check {check_name} missing"
            check_data = data['checks'][check_name]
            assert 'status' in check_data
            assert 'message' in check_data
            assert 'timestamp' in check_data
    
    def test_status_endpoint(self, client):
        """Test status overview endpoint"""
        response = client.get('/monitoring/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'service' in data
        assert 'version' in data
        assert 'status' in data
        assert 'timestamp' in data
        assert 'environment' in data
        
        # Verify service info
        assert data['service'] == 'Gym Bot Dashboard'
        assert 'production-ready' in data['version']
        assert data['status'] in ['healthy', 'unhealthy', 'error']
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get('/monitoring/metrics')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'timestamp' in data
        assert 'system' in data
        assert 'application' in data
        assert 'database' in data
        
        # Verify system metrics structure
        if 'error' not in data['system']:
            assert 'cpu_percent' in data['system']
            assert 'memory_percent' in data['system']
        
        # Verify application metrics
        assert 'uptime_seconds' in data['application']
        assert 'flask_debug' in data['application']
    
    def test_individual_health_checks(self, client):
        """Test individual health check endpoints"""
        checks = ['database', 'secrets_manager', 'square_integration', 'system_resources', 'flask_app']
        
        for check_name in checks:
            response = client.get(f'/monitoring/health/{check_name}')
            assert response.status_code in [200, 503], f"Health check {check_name} returned unexpected status"
            
            data = response.get_json()
            assert 'status' in data
            assert 'message' in data
            assert 'timestamp' in data
            assert data['status'] in ['healthy', 'unhealthy', 'error']

class TestHealthCheckLogic:
    """Test health check logic and responses"""
    
    def test_database_health_check(self, app):
        """Test database health check specifically"""
        with app.app_context():
            from src.monitoring.health_checks import check_database_connection
            
            result = check_database_connection()
            assert 'healthy' in result
            assert 'message' in result
            
            if result['healthy']:
                assert 'details' in result
                assert 'database_path' in result['details']
    
    def test_flask_app_health_check(self, app):
        """Test Flask application health check"""
        with app.app_context():
            from src.monitoring.health_checks import check_flask_app
            
            result = check_flask_app()
            assert 'healthy' in result
            assert 'message' in result
            assert 'details' in result
            
            # Should be healthy since we have a working app
            assert result['healthy'] is True
            
            # Check service status details
            services = result['details']['services']
            assert 'db_manager' in services
            assert 'training_package_cache' in services
    
    def test_system_resources_health_check(self, app):
        """Test system resources health check"""
        with app.app_context():
            from src.monitoring.health_checks import check_system_resources
            
            result = check_system_resources()
            assert 'healthy' in result
            assert 'message' in result
            
            if result['healthy']:
                assert 'details' in result
                assert 'cpu_percent' in result['details']
                assert 'memory_percent' in result['details']

class TestHealthCheckIntegration:
    """Test health check integration with the application"""
    
    def test_startup_health_check(self, app):
        """Test that startup health checks run successfully"""
        with app.app_context():
            from src.monitoring.health_checks import run_startup_health_check
            
            # This should not raise an exception
            result = run_startup_health_check(app)
            
            # Result might be None if health check fails, but should not crash
            if result is not None:
                assert 'status' in result
                assert 'checks' in result
    
    def test_health_checker_registration(self, app):
        """Test that health checks are properly registered"""
        from src.monitoring.health_checks import health_checker
        
        # Check that all expected health checks are registered
        expected_checks = ['database', 'secrets_manager', 'square_integration', 'system_resources', 'flask_app']
        
        for check_name in expected_checks:
            assert check_name in health_checker.checks, f"Health check {check_name} not registered"
    
    def test_monitoring_blueprint_routes(self, app):
        """Test that monitoring blueprint routes are accessible"""
        with app.test_client() as client:
            # Test that all monitoring routes are accessible
            monitoring_routes = [
                '/monitoring/health',
                '/monitoring/status', 
                '/monitoring/metrics'
            ]
            
            for route in monitoring_routes:
                response = client.get(route)
                assert response.status_code in [200, 500, 503], f"Route {route} not accessible"