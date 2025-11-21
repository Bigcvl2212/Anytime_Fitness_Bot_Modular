#!/usr/bin/env python3
"""
Basic tests for DatabaseManager service

Tests basic CRUD operations and connection management
"""

import os
import sqlite3
import pytest
import tempfile
from datetime import datetime

# Import from src package
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.database_manager import DatabaseManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    yield path

    # Cleanup - use try/except for Windows file locking issues
    import time
    for _ in range(5):  # Retry up to 5 times
        try:
            if os.path.exists(path):
                os.remove(path)
            break
        except PermissionError:
            time.sleep(0.1)  # Wait briefly and retry


@pytest.fixture
def db_manager(temp_db):
    """Create a DatabaseManager instance with temporary database"""
    return DatabaseManager(db_path=temp_db)


class TestDatabaseManager:
    """Test suite for DatabaseManager"""

    def test_initialization(self, db_manager):
        """Test database initialization"""
        assert db_manager is not None
        assert db_manager.db_type == 'sqlite'
        assert os.path.exists(db_manager.db_path)

    def test_get_connection(self, db_manager):
        """Test database connection"""
        conn = db_manager.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_get_cursor_context_manager(self, db_manager):
        """Test cursor context manager"""
        with db_manager.get_cursor() as cursor:
            assert cursor is not None
            assert isinstance(cursor, sqlite3.Cursor)

            # Execute a simple query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_schema_creation(self, db_manager):
        """Test that schema tables are created"""
        with db_manager.get_cursor() as cursor:
            # Check members table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
            assert cursor.fetchone() is not None

            # Check prospects table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prospects'")
            assert cursor.fetchone() is not None

            # Check training_clients table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='training_clients'")
            assert cursor.fetchone() is not None

            # Check messages table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
            assert cursor.fetchone() is not None

    def test_save_members_to_db(self, db_manager):
        """Test saving members to database"""
        test_members = [
            {
                'prospect_id': 'TEST001',
                'guid': 'guid-test-001',
                'first_name': 'John',
                'last_name': 'Doe',
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'mobile_phone': '555-0100',
                'status': 'Active',
                'amount_past_due': 0.0,
                'agreement_type': 'Monthly'
            }
        ]

        # Save members
        db_manager.save_members_to_db(test_members)

        # Verify saved
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM members WHERE prospect_id = 'TEST001'")
            count = cursor.fetchone()[0]
            assert count == 1

    def test_get_members(self, db_manager):
        """Test retrieving members from database"""
        # Save test member first
        test_members = [
            {
                'prospect_id': 'TEST002',
                'guid': 'guid-test-002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'full_name': 'Jane Smith',
                'email': 'jane@example.com',
                'mobile_phone': '555-0101',
                'status': 'Active',
                'amount_past_due': 0.0,
                'agreement_type': 'Monthly'
            }
        ]
        db_manager.save_members_to_db(test_members)

        # Retrieve members
        members = db_manager.get_members()
        assert len(members) >= 1

    def test_get_database_stats(self, db_manager):
        """Test database statistics retrieval"""
        stats = db_manager.get_database_stats()

        assert 'total_members' in stats
        assert 'total_prospects' in stats
        assert 'total_training_clients' in stats
        assert isinstance(stats['total_members'], int)

    def test_save_prospects_to_db(self, db_manager):
        """Test saving prospects to database"""
        test_prospects = [
            {
                'prospect_id': 'PROSPECT001',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice@example.com',
                'mobile_phone': '555-0102',
                'status': 'New',
                'source': 'Website'
            }
        ]

        db_manager.save_prospects_to_db(test_prospects)

        # Verify saved
        with db_manager.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM prospects WHERE prospect_id = 'PROSPECT001'")
            count = cursor.fetchone()[0]
            assert count == 1

    def test_get_past_due_members(self, db_manager):
        """Test retrieving past due members"""
        # Save a past due member
        test_members = [
            {
                'prospect_id': 'PASTDUE001',
                'guid': 'guid-pastdue-001',
                'first_name': 'Bob',
                'last_name': 'Brown',
                'full_name': 'Bob Brown',
                'email': 'bob@example.com',
                'mobile_phone': '555-0103',
                'status': 'Active',
                'amount_past_due': 150.00,
                'agreement_type': 'Monthly'
            }
        ]
        db_manager.save_members_to_db(test_members)

        # Retrieve past due members
        past_due = db_manager.get_past_due_members(min_amount=100)
        assert len(past_due) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
