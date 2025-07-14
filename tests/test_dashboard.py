"""
Test suite for gym_bot_dashboard.py

Basic tests to ensure the dashboard is working correctly.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the dashboard module
import gym_bot_dashboard


class TestGymBotDashboard(unittest.TestCase):
    """Test cases for the Gym Bot Dashboard."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = gym_bot_dashboard.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_page(self):
        """Test that the home page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gym Bot System Dashboard', response.data)
        self.assertIn(b'Monitor and control your gym automation system', response.data)
    
    def test_workflows_page(self):
        """Test that the workflows page loads successfully."""
        response = self.client.get('/workflows')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Workflow Management', response.data)
        self.assertIn(b'Message Processing', response.data)
        self.assertIn(b'Payment Processing', response.data)
    
    def test_logs_page(self):
        """Test that the logs page loads successfully."""
        response = self.client.get('/logs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'System Logs', response.data)
        self.assertIn(b'Monitor real-time system activity', response.data)
    
    def test_settings_page(self):
        """Test that the settings page loads successfully."""
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Settings & Configuration', response.data)
        self.assertIn(b'System Configuration', response.data)
    
    def test_api_status_endpoint(self):
        """Test the API status endpoint."""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('services', data)
        self.assertIn('logs', data)
        self.assertIn('last_update', data)
        self.assertIn('workflows', data)
    
    def test_api_refresh_status(self):
        """Test the API refresh status endpoint."""
        response = self.client.get('/api/refresh-status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('status', data)
    
    def test_api_logs_endpoint(self):
        """Test the API logs endpoint."""
        response = self.client.get('/api/logs')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('logs', data)
        self.assertIsInstance(data['logs'], list)
    
    def test_run_workflow_api_valid_workflow(self):
        """Test running a valid workflow via API."""
        response = self.client.post('/api/run-workflow', 
                                  json={'workflow': 'message_processing', 'migration_mode': 'hybrid'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_run_workflow_api_invalid_workflow(self):
        """Test running an invalid workflow via API."""
        response = self.client.post('/api/run-workflow', 
                                  json={'workflow': 'invalid_workflow'})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])  # It will start even if workflow doesn't exist
    
    def test_run_workflow_api_no_workflow(self):
        """Test API call without specifying workflow."""
        response = self.client.post('/api/run-workflow', json={})
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_service_status_check(self):
        """Test the service status check functionality."""
        status = gym_bot_dashboard.check_service_status()
        
        # Should have all expected services
        expected_services = ['square_payments', 'gemini_ai', 'migration_service', 'clubos_auth']
        for service in expected_services:
            self.assertIn(service, status)
            self.assertIn('status', status[service])
            self.assertIn('details', status[service])
    
    def test_log_message_functionality(self):
        """Test the log message functionality."""
        initial_log_count = len(gym_bot_dashboard.system_status['logs'])
        
        gym_bot_dashboard.log_message('INFO', 'Test message', 'TestComponent')
        
        # Should have one more log entry
        self.assertEqual(len(gym_bot_dashboard.system_status['logs']), initial_log_count + 1)
        
        # Check the latest log entry
        latest_log = gym_bot_dashboard.system_status['logs'][0]
        self.assertEqual(latest_log['level'], 'INFO')
        self.assertEqual(latest_log['message'], 'Test message')
        self.assertEqual(latest_log['component'], 'TestComponent')
        self.assertIn('timestamp', latest_log)
    
    def test_dashboard_navigation_links(self):
        """Test that all navigation links are present."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Check for navigation links
        self.assertIn(b'href="/"', response.data)  # Dashboard link
        self.assertIn(b'href="/workflows"', response.data)  # Workflows link
        self.assertIn(b'href="/logs"', response.data)  # Logs link
        self.assertIn(b'href="/settings"', response.data)  # Settings link
    
    def test_demo_mode_values(self):
        """Test that demo mode provides appropriate values."""
        # Since gym_bot modules aren't available, should be in demo mode
        self.assertFalse(gym_bot_dashboard.gym_bot_available)
        
        # Test mock functions
        self.assertEqual(gym_bot_dashboard.GCP_PROJECT_ID, "demo-project")
        self.assertEqual(gym_bot_dashboard.get_migration_mode(), "demo")
        self.assertTrue(gym_bot_dashboard.test_square_connection())


class TestDashboardUtilities(unittest.TestCase):
    """Test utility functions of the dashboard."""
    
    def test_create_templates_directory(self):
        """Test that template creation works."""
        # This test ensures the create_templates function doesn't crash
        try:
            gym_bot_dashboard.create_templates()
            self.assertTrue(True)  # If we get here, no exception was raised
        except Exception as e:
            self.fail(f"create_templates() raised an exception: {e}")
    
    def test_initialize_dashboard(self):
        """Test dashboard initialization."""
        try:
            gym_bot_dashboard.initialize_dashboard()
            self.assertTrue(True)  # If we get here, no exception was raised
        except Exception as e:
            self.fail(f"initialize_dashboard() raised an exception: {e}")


def run_dashboard_tests():
    """Run all dashboard tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestGymBotDashboard))
    test_suite.addTest(unittest.makeSuite(TestDashboardUtilities))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_dashboard_tests()
    sys.exit(0 if success else 1)