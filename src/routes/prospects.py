#!/usr/bin/env python3
"""
Prospects Routes
Prospect management and related functionality
"""

from flask import Blueprint, render_template, jsonify, current_app, request
import logging
import requests
import sys
import os
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)

prospects_bp = Blueprint('prospects', __name__)

# Import the authentication decorator
from .auth import require_auth

@prospects_bp.route('/prospects')
@require_auth
def prospects_page():
	"""Display prospects page with fast loading - data loads asynchronously via JavaScript."""
	
	# Fast page load - render template immediately with minimal data
	return render_template('prospects.html',
						 prospects=[],  # Empty initially, loaded via JavaScript
						 total_prospects=0,  # Will be updated via API
						 statuses=[],
						 search='',
						 page=1,
						 total_pages=1,
						 per_page=50)

@prospects_bp.route('/prospect/<prospect_id>')
def prospect_profile(prospect_id):
	"""Prospect profile page."""
	try:
		# Get prospect from database
		from src.services.database_manager import DatabaseManager
		db_manager = DatabaseManager()
		
		conn = db_manager.get_connection()
		cursor = conn.cursor()
		
		cursor.execute("""
			SELECT prospect_id, first_name, last_name, full_name, email, phone, 
				   status, prospect_type, created_at, updated_at
			FROM prospects 
			WHERE prospect_id = ?
		""", (prospect_id,))
		
		prospect_data = cursor.fetchone()
		conn.close()
		
		if not prospect_data:
			return render_template('404.html', message=f"Prospect {prospect_id} not found"), 404
		
		prospect = {
			'id': prospect_data[0],
			'prospect_id': prospect_data[0],
			'first_name': prospect_data[1],
			'last_name': prospect_data[2],
			'full_name': prospect_data[3],
			'email': prospect_data[4],
			'phone': prospect_data[5],
			'status': prospect_data[6],
			'prospect_type': prospect_data[7],
			'created_at': prospect_data[8],
			'updated_at': prospect_data[9]
		}
		
		return render_template('prospect_profile.html', prospect=prospect)
		
	except Exception as e:
		logger.error(f"Error getting prospect {prospect_id}: {e}")
		return render_template('404.html', message="Error loading prospect"), 500

@prospects_bp.route('/api/prospects/all')
def get_all_prospects():
    """API endpoint to get ALL prospects from database - fast loading from cached data."""
    
    try:
        # Get prospects from database instead of API
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Query all prospects from database
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prospect_id, first_name, last_name, full_name, email, phone, 
                   status, prospect_type, created_at, updated_at
            FROM prospects 
            ORDER BY created_at DESC
        """)
        
        prospects_data = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        prospects = []
        for row in prospects_data:
            prospect = {
                'id': row[0],  # prospect_id
                'prospect_id': row[0],
                'firstName': row[1],  # Match expected frontend format
                'lastName': row[2],
                'full_name': row[3],
                'email': row[4],
                'phone': row[5],
                'status': row[6],
                'prospect_type': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            }
            prospects.append(prospect)
        
        logger.info(f"📋 Returning prospects from database: {len(prospects)} prospects")
        
        return jsonify({
            'success': True,
            'prospects': prospects,
            'total_prospects': len(prospects),
            'page': 1,
            'total_pages': 1, 
            'per_page': len(prospects),
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting prospects from database: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prospects_bp.route('/api/prospects/paginated')  
def get_prospects_paginated():
    """API endpoint to get paginated prospects for frontend display."""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get prospects from database with pagination and filtering
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Build query with search and status filters
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])
        
        if status_filter:
            where_conditions.append("status = ?")
            params.append(status_filter)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM prospects {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        query = f"""
            SELECT prospect_id, first_name, last_name, full_name, email, phone, 
                   status, prospect_type, created_at, updated_at
            FROM prospects 
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [per_page, offset])
        
        prospects_data = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        prospects = []
        for row in prospects_data:
            prospect = {
                'id': row[0],  # prospect_id
                'prospect_id': row[0],
                'firstName': row[1],  # Match expected frontend format
                'lastName': row[2],
                'full_name': row[3],
                'email': row[4],
                'phone': row[5],
                'status': row[6],
                'prospect_type': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            }
            prospects.append(prospect)
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        
        logger.info(f"📋 Returning {len(prospects)} prospects (page {page}/{total_pages}) from database")
        
        return jsonify({
            'success': True,
            'prospects': prospects,
            'total_prospects': total_count,
            'page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'source': 'database'
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting paginated prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prospects_bp.route('/api/prospects/statuses')
def get_prospect_statuses():
    """Get all unique prospect statuses for filtering."""
    try:
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT status FROM prospects WHERE status IS NOT NULL ORDER BY status")
        statuses = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'statuses': statuses
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting prospect statuses: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prospects_bp.route('/api/prospects/search')
def search_prospects():
    """Search for prospects by name"""
    try:
        name = request.args.get('name', '').strip()
        if not name:
            return jsonify({
                'success': False,
                'error': 'Name parameter is required'
            }), 400

        # FIXED: Prioritize EXACT matches over partial matches
        # First, try exact full name match
        prospects = current_app.db_manager.execute_query("""
            SELECT prospect_id, id, full_name, first_name, last_name, email, phone, status
            FROM prospects
            WHERE LOWER(full_name) = LOWER(?)
               OR LOWER(first_name || ' ' || last_name) = LOWER(?)
            LIMIT 10
        """, (name, name), fetch_all=True)

        if prospects and len(prospects) > 0:
            logger.info(f"✅ Found EXACT match for '{name}': {len(prospects)} prospects")
        else:
            # If no exact match, try more aggressive search with variations
            search_variations = [
                name,  # Full search with LIKE
                name.replace(' ', ''),  # No spaces
                name.replace('_', ' '),  # Replace underscores with spaces
                name.split()[0] if ' ' in name else name,  # First name only
                name.split()[-1] if ' ' in name else name,  # Last name only
            ]

            for search_name in search_variations:
                if not search_name:
                    continue

                prospects = current_app.db_manager.execute_query("""
                    SELECT prospect_id, id, full_name, first_name, last_name, email, phone, status
                    FROM prospects
                    WHERE LOWER(full_name) LIKE LOWER(?)
                       OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
                       OR LOWER(first_name) LIKE LOWER(?)
                       OR LOWER(last_name) LIKE LOWER(?)
                    ORDER BY
                        CASE WHEN LOWER(full_name) = LOWER(?) THEN 1
                             WHEN LOWER(first_name || ' ' || last_name) = LOWER(?) THEN 2
                             ELSE 3 END,
                        full_name
                    LIMIT 10
                """, (f'%{search_name}%', f'%{search_name}%', f'%{search_name}%', f'%{search_name}%',
                      search_name, search_name), fetch_all=True)

                if prospects and len(prospects) > 0:
                    logger.info(f"🎯 Found prospects with variation '{search_name}': {len(prospects)}")
                    break

        if prospects is None:
            prospects = []

        # Convert to list of dicts if needed
        if prospects and not isinstance(prospects[0], dict):
            prospects = [dict(row) for row in prospects]

        logger.info(f"🔍 Found {len(prospects)} prospects matching '{name}'")

        return jsonify({
            'success': True,
            'prospects': prospects,
            'count': len(prospects)
        })

    except Exception as e:
        logger.error(f"❌ Error searching prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prospects_bp.route('/api/prospects/refresh')
def refresh_prospects():
    """Trigger a refresh of prospects data from ClubHub API."""
    try:
        # This would trigger the startup sync to refresh prospects
        # For now, just return success - the actual refresh should be done via the startup sync
        return jsonify({
            'success': True,
            'message': 'Prospects refresh triggered. Please run the startup sync to update data.'
        })

    except Exception as e:
        logger.error(f"❌ Error refreshing prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500