#!/usr/bin/env python3
"""
Test script to debug URL generation in Flask app
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app

# Create the Flask app
app = create_app()

with app.app_context():
    from flask import url_for
    
    print("Testing URL generation:")
    print(f"url_for('auth.login') = {url_for('auth.login')}")
    
    try:
        dashboard_url = url_for('dashboard.dashboard')
        print(f"url_for('dashboard.dashboard') = {dashboard_url}")
    except Exception as e:
        print(f"ERROR generating dashboard URL: {e}")
    
    try:
        club_selection_url = url_for('club_selection.club_selection')
        print(f"url_for('club_selection.club_selection') = {club_selection_url}")
    except Exception as e:
        print(f"ERROR generating club selection URL: {e}")
    
    # List all registered routes
    print("\nAll registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} ({rule.methods})")