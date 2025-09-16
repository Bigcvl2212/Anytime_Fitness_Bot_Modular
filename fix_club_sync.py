#!/usr/bin/env python3
"""
Fix the club selection issue and run the sync properly
"""

import os
import sys
sys.path.append('src')

from src.main_app import create_app

# Create the Flask app (this will run the sync)
print("🔄 Creating Flask app...")
app = create_app()

with app.app_context():
    print("✅ App created successfully")
    
    # Fix the club selection issue
    print("🔧 Fixing club selection...")
    try:
        from src.services.multi_club_manager import multi_club_manager
        
        # Manually set the club ID to 1156 (your club)
        multi_club_manager.set_selected_clubs(['1156'])
        selected_clubs = multi_club_manager.get_selected_clubs()
        print(f"✅ Selected clubs: {selected_clubs}")
        
        # Now run the sync
        print("🔄 Running enhanced startup sync with correct club selection...")
        from src.main_app import enhanced_startup_sync
        enhanced_startup_sync(app)
        
        print(f"✅ After sync - Cached members count: {len(getattr(app, 'cached_members', []))}")
        print(f"✅ After sync - Cached prospects count: {len(getattr(app, 'cached_prospects', []))}")
        print(f"✅ After sync - Cached training clients count: {len(getattr(app, 'cached_training_clients', []))}")
        
        # Check the database now
        if hasattr(app, 'db_manager'):
            import psycopg2.extras
            conn = app.db_manager.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute('SELECT COUNT(*) as count FROM members')
            member_count = cur.fetchone()['count']
            print(f"📊 Members in database: {member_count}")
            
            cur.execute('SELECT COUNT(*) as count FROM member_categories')
            category_count = cur.fetchone()['count']
            print(f"📊 Member categories in database: {category_count}")
            
            conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("✅ Club sync fix complete!")