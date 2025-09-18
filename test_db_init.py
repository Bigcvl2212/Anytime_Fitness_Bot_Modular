#!/usr/bin/env python3
"""
Simple test for database manager initialization
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for SQLite
os.environ['LOCAL_DEVELOPMENT'] = 'true'
os.environ['DB_TYPE'] = 'sqlite'
os.environ['DATABASE_URL'] = 'sqlite:///gym_bot_local.db'

def test_db_manager():
    """Test database manager initialization"""
    print("Testing database manager...")
    
    try:
        from src.services.database_manager import DatabaseManager
        
        # Create database manager
        db_path = os.path.join(project_root, 'gym_bot_test.db')
        db_manager = DatabaseManager(db_path=db_path)
        
        print(f"Database type detected: {db_manager.db_type}")
        print(f"Database path: {getattr(db_manager, 'db_path', 'N/A')}")
        
        # Try to initialize
        print("Running init_database()...")
        db_manager.init_database()
        print("✅ Database initialization completed")
        
        # Test a simple query
        print("Testing simple query...")
        result = db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'",
            fetch_all=True
        )
        
        if result:
            print(f"✅ Tables found: {[r[0] for r in result]}")
        else:
            print("⚠️ No tables found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_manager()