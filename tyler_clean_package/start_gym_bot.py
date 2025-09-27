#!/usr/bin/env python3
import os
import sys
import webbrowser
from pathlib import Path

def main():
    """Start the Gym Bot application with clean setup"""
    print("🏋️‍♂️ Starting Gym Bot Dashboard...")
    print("=" * 50)
    
    # Set environment variables for local development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['DB_TYPE'] = 'sqlite'
    
    # Add src to Python path
    current_dir = Path(__file__).parent
    src_path = current_dir / 'src'
    sys.path.insert(0, str(src_path))
    
    try:
        # Import and create the app
        from src.main_app import create_app
        
        app = create_app()
        
        print("✅ App initialized successfully")
        print("🌐 Starting server...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🔐 You'll need to set up ClubOS credentials on first login")
        print("🌍 INTERNET REQUIRED: For ClubOS and ClubHub connections")
        print("\n💡 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the Flask development server
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you ran: python setup_for_tyler.py")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("💡 Check the error message above for details")

if __name__ == '__main__':
    main()
