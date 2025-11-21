#!/usr/bin/env python3
"""
Manual script to save cached members to PostgreSQL database
This will run the same logic that should happen automatically after sync
"""

import os
import sys
sys.path.append('src')

from src.main_app import create_app

# Create the Flask app (this will run the sync)
print("🔄 Creating Flask app and running startup sync...")
app = create_app()

with app.app_context():
    print(f"✅ App created with db_manager: {hasattr(app, 'db_manager')}")
    print(f"✅ Cached members count: {len(getattr(app, 'cached_members', []))}")
    print(f"✅ Cached prospects count: {len(getattr(app, 'cached_prospects', []))}")
    print(f"✅ Cached training clients count: {len(getattr(app, 'cached_training_clients', []))}")
    
    # Force run the enhanced startup sync to ensure data is loaded
    if len(getattr(app, 'cached_members', [])) == 0:
        print("🔄 No cached members found, running enhanced startup sync...")
        from src.main_app import enhanced_startup_sync
        enhanced_startup_sync(app)
        
        print(f"✅ After sync - Cached members count: {len(getattr(app, 'cached_members', []))}")
        print(f"✅ After sync - Cached prospects count: {len(getattr(app, 'cached_prospects', []))}")
        print(f"✅ After sync - Cached training clients count: {len(getattr(app, 'cached_training_clients', []))}")
    
    # Now manually save to database
    if hasattr(app, 'db_manager'):
        try:
            # Save members with comprehensive billing data
            if hasattr(app, 'cached_members') and app.cached_members:
                print(f"💾 Saving {len(app.cached_members)} members to database...")
                success = app.db_manager.save_members_to_db(app.cached_members)
                if success:
                    print(f"✅ Database: {len(app.cached_members)} members saved with billing data")
                else:
                    print("❌ Failed to save members to database")
            
            # Save prospects
            if hasattr(app, 'cached_prospects') and app.cached_prospects:
                print(f"💾 Saving {len(app.cached_prospects)} prospects to database...")
                success = app.db_manager.save_prospects_to_db(app.cached_prospects)
                if success:
                    print(f"✅ Database: {len(app.cached_prospects)} prospects saved")
                else:
                    print("❌ Failed to save prospects to database")
                    
            # Save training clients
            if hasattr(app, 'cached_training_clients') and app.cached_training_clients:
                print(f"💾 Saving {len(app.cached_training_clients)} training clients to database...")
                success = app.db_manager.save_training_clients_to_db(app.cached_training_clients)
                if success:
                    print(f"✅ Database: {len(app.cached_training_clients)} training clients saved")
                else:
                    print("❌ Failed to save training clients to database")
                    
        except Exception as db_e:
            print(f"❌ Database save error: {db_e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No database manager found")

print("✅ Manual database save complete!")