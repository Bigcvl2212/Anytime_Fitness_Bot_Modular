#!/usr/bin/env python3
"""
Fast members page patch - replaces the slow members page function
"""

import sqlite3
from flask import render_template

def fast_members_page(app, db_manager, logger):
    """Create a fast-loading members page route"""
    
    @app.route('/members')
    def members_page():
        """Display members page with fast loading - data loads asynchronously via JavaScript."""
        
        logger.info("📋 Members page loaded - using fast loading with existing database data")
        
        # Get simple counts from database for initial display (fast operation)
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        
        conn.close()
        
        # Fast page load - render template immediately with minimal data
        # JavaScript will load the actual member data and category counts asynchronously
        return render_template('members.html',
                             members=[],  # Empty initially, loaded via JavaScript
                             total_members=total_members,
                             statuses=[],
                             search='',
                             status_filter='',
                             page=1,
                             total_pages=1,
                             per_page=50)
    
    return members_page
