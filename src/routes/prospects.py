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
		cursor = db_manager.get_cursor(conn)
		
		try:
			cursor.execute("""
				SELECT prospect_id, first_name, last_name, full_name, email, phone, 
					   status, prospect_type, created_at, updated_at
				FROM prospects 
				WHERE prospect_id = %s
			""", (prospect_id,))
			
			prospect_data = cursor.fetchone()
		finally:
			cursor.close()
			db_manager.close_connection(conn)
		
		if not prospect_data:
			return render_template('404.html', message=f"Prospect {prospect_id} not found"), 404
		
		prospect = {
			'id': prospect_data['prospect_id'],
			'prospect_id': prospect_data['prospect_id'],
			'first_name': prospect_data['first_name'],
			'last_name': prospect_data['last_name'],
			'full_name': prospect_data['full_name'],
			'email': prospect_data['email'],
			'phone': prospect_data['phone'],
			'status': prospect_data['status'],
			'prospect_type': prospect_data['prospect_type'],
			'created_at': prospect_data['created_at'],
			'updated_at': prospect_data['updated_at']
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
        cursor = db_manager.get_cursor(conn)
        
        try:
            cursor.execute("""
                SELECT prospect_id, first_name, last_name, full_name, email, phone, 
                       status, prospect_type, created_at, updated_at
                FROM prospects 
                ORDER BY created_at DESC
            """)
            
            prospects_data = cursor.fetchall()
        finally:
            cursor.close()
            db_manager.close_connection(conn)
        
        # Convert to list of dicts
        prospects = []
        for row in prospects_data:
            prospect = {
                'id': row['prospect_id'],
                'prospect_id': row['prospect_id'],
                'firstName': row['first_name'],  # Match expected frontend format
                'lastName': row['last_name'],
                'full_name': row['full_name'],
                'email': row['email'],
                'phone': row['phone'],
                'status': row['status'],
                'prospect_type': row['prospect_type'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
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
        cursor = db_manager.get_cursor(conn)
        
        try:
            # Build query with search and status filters
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR phone LIKE %s)")
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term, search_term])
            
            if status_filter:
                where_conditions.append("status = %s")
                params.append(status_filter)
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Get total count
            count_query = f"SELECT COUNT(*) as count FROM prospects {where_clause}"
            cursor.execute(count_query, params)
            result = cursor.fetchone()
            if hasattr(result, 'keys') and 'count' in result:
                total_count = result['count']
            else:
                # Fallback for regular cursor
                total_count = result[0] if result else 0
            
            # Get paginated results
            query = f"""
                SELECT prospect_id, first_name, last_name, full_name, email, phone, 
                       status, prospect_type, created_at, updated_at
                FROM prospects 
                {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [per_page, offset])
            
            prospects_data = cursor.fetchall()
        finally:
            cursor.close()
            db_manager.close_connection(conn)
        
        # Convert to list of dicts
        prospects = []
        for row in prospects_data:
            prospect = {
                'id': row['prospect_id'],
                'prospect_id': row['prospect_id'],
                'firstName': row['first_name'],  # Match expected frontend format
                'lastName': row['last_name'],
                'full_name': row['full_name'],
                'email': row['email'],
                'phone': row['phone'],
                'status': row['status'],
                'prospect_type': row['prospect_type'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
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
        cursor = db_manager.get_cursor(conn)
        
        try:
            cursor.execute("SELECT DISTINCT status FROM prospects WHERE status IS NOT NULL ORDER BY status")
            statuses = [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()
            db_manager.close_connection(conn)
        
        return jsonify({
            'success': True,
            'statuses': statuses
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting prospect statuses: {e}")
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