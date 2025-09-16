#!/usr/bin/env python3
"""
Test configuration and fixtures for Gym Bot
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import sqlite3

@pytest.fixture
def app():
    """Create application for testing"""
    # Set test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    # Import and create app
    from src.main_app import create_app
    app = create_app()
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test runner"""
    return app.test_cli_runner()

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    try:
        os.unlink(db_path)
    except OSError:
        pass

@pytest.fixture
def mock_secrets(monkeypatch):
    """Mock secrets for testing"""
    def mock_get_secret(key, default=None):
        mock_secrets_data = {
            'square-production-access-token': 'test-token',
            'square-production-location-id': 'test-location',
            'clubos-username': 'test-user',
            'clubos-password': 'test-pass',
            'clubhub-email': 'test@test.com',
            'clubhub-password': 'test-pass'
        }
        return mock_secrets_data.get(key, default)
    
    # Mock the secrets_local.get_secret function
    monkeypatch.setattr('src.config.secrets_local.get_secret', mock_get_secret)
    return mock_get_secret