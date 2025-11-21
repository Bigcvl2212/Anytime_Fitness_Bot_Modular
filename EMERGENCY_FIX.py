#!/usr/bin/env python3
"""
EMERGENCY FIX - Clear Python cache and fix database schema
Run this script, then restart the server
"""

import os
import shutil
import sqlite3
from pathlib import Path

def clear_python_cache():
    """Delete all __pycache__ directories and .pyc files"""
    print("🧹 Clearing Python bytecode cache...")
    cache_count = 0
    pyc_count = 0
    
    # Find and delete __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                cache_count += 1
                print(f"  ✅ Deleted: {cache_dir}")
            except Exception as e:
                print(f"  ⚠️ Could not delete {cache_dir}: {e}")
        
        # Delete .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                try:
                    os.remove(pyc_file)
                    pyc_count += 1
                except Exception as e:
                    print(f"  ⚠️ Could not delete {pyc_file}: {e}")
    
    print(f"✅ Cleared {cache_count} __pycache__ directories and {pyc_count} .pyc files")

def fix_prospects_schema():
    """Fix prospects table to allow NULL prospect_id"""
    print("\n💾 Fixing prospects database schema...")
    
    db_path = "gym_bot.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(prospects)")
        columns = cursor.fetchall()
        print(f"📋 Current prospects columns: {len(columns)}")
        
        # Create new table with prospect_id as nullable
        print("  ➕ Creating new prospects table with nullable prospect_id...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospects_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id TEXT,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                status TEXT,
                prospect_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mobile_phone TEXT,
                source TEXT,
                interest_level TEXT,
                club_name TEXT,
                created_date TEXT,
                last_contact_date TEXT,
                notes TEXT
            )
        """)
        
        # Copy data from old table
        print("  📦 Copying existing prospect data...")
        cursor.execute("""
            INSERT INTO prospects_new 
            SELECT * FROM prospects
        """)
        
        # Drop old table and rename new one
        print("  🔄 Swapping tables...")
        cursor.execute("DROP TABLE prospects")
        cursor.execute("ALTER TABLE prospects_new RENAME TO prospects")
        
        # Create index for faster lookups
        print("  📊 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_prospect_id ON prospects(prospect_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_email ON prospects(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prospects_phone ON prospects(phone)")
        
        conn.commit()
        print("✅ Prospects schema fixed - prospect_id is now nullable")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error fixing prospects schema: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def verify_api_code():
    """Verify the API code fix is present"""
    print("\n🔍 Verifying API code fix...")
    
    api_file = "src/routes/api.py"
    if not os.path.exists(api_file):
        print(f"❌ API file not found: {api_file}")
        return
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'isinstance(table_count, int)' in content:
        print("✅ API type handling fix is present in code")
    else:
        print("⚠️ API type handling fix NOT found in code - may need to reapply")

if __name__ == "__main__":
    print("🚨 EMERGENCY FIX SCRIPT")
    print("=" * 60)
    
    # Step 1: Clear Python cache
    clear_python_cache()
    
    # Step 2: Fix database schema
    fix_prospects_schema()
    
    # Step 3: Verify API code
    verify_api_code()
    
    print("\n" + "=" * 60)
    print("✅ EMERGENCY FIX COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("1. STOP the Flask server (Ctrl+C)")
    print("2. RESTART the Flask server: python run_dashboard.py")
    print("3. The API errors should be FIXED")
    print("\n⚠️ ClubOS/Square credentials still need manual setup:")
    print("   - Edit .env file")
    print("   - Replace CLUBOS_USERNAME and CLUBOS_PASSWORD with real values")
    print("   - Add SQUARE_PRODUCTION_LOCATION_ID if needed")
