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

@prospects_bp.route('/prospects')
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
		# First try to get prospect from cached data
		if hasattr(current_app, 'data_cache') and current_app.data_cache.get('prospects'):
			cached_prospects = current_app.data_cache['prospects']
			
			# Find prospect by ID in cached data
			prospect_data = None
			for prospect in cached_prospects:
				if (str(prospect.get('id')) == str(prospect_id) or 
					str(prospect.get('prospect_id')) == str(prospect_id) or
					str(prospect.get('prospectId')) == str(prospect_id)):
					prospect_data = prospect
					break
			
			if prospect_data:
				# Ensure full_name is set
				if not prospect_data.get('full_name'):
					first_name = prospect_data.get('firstName') or prospect_data.get('first_name') or ''
					last_name = prospect_data.get('lastName') or prospect_data.get('last_name') or ''
					prospect_data['full_name'] = f"{first_name} {last_name}".strip()
				
				# Also set 'name' field for template compatibility
				prospect_data['name'] = prospect_data.get('full_name') or 'Unknown Prospect'
				
				return render_template('prospect_profile.html', prospect=prospect_data)
		
		# Fallback: try to get prospect from ClubHub API
		from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
		
		CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
		USERNAME = CLUBHUB_EMAIL
		PASSWORD = CLUBHUB_PASSWORD
		
		headers = {
			"Content-Type": "application/json",
			"API-version": "1",
			"Accept": "application/json",
			"User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
		}
		
		session = requests.Session()
		session.headers.update(headers)
		
		# Login to get bearer token
		login_data = {"username": USERNAME, "password": PASSWORD}
		login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
		
		if login_response.status_code != 200:
			return render_template('error.html', error='Failed to authenticate with ClubHub API')
			
		login_result = login_response.json()
		bearer_token = login_result.get('accessToken')
		
		if not bearer_token:
			return render_template('error.html', error='No access token received')
			
		session.headers.update({"Authorization": f"Bearer {bearer_token}"})
		
		# Get specific prospect
		club_id = "1156"
		prospect_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/prospects/{prospect_id}"
		prospect_response = session.get(prospect_url)
		
		if prospect_response.status_code != 200:
			return render_template('error.html', error='Prospect not found')
		
		prospect_data = prospect_response.json()
		prospect_data['full_name'] = f"{prospect_data.get('firstName', '')} {prospect_data.get('lastName', '')}".strip()
		prospect_data['name'] = prospect_data.get('full_name') or 'Unknown Prospect'
		
		return render_template('prospect_profile.html', prospect=prospect_data)
		
	except Exception as e:
		logger.error(f"❌ Error loading prospect profile {prospect_id}: {e}")
		return render_template('error.html', error=str(e))

@prospects_bp.route('/api/prospects/all')
def get_all_prospects():
    """API endpoint to get ALL prospects with proper pagination - implemented to handle 9000+ prospects."""
    
    # First check if we have cached data to return immediately
    if hasattr(current_app, 'data_cache') and current_app.data_cache.get('prospects'):
        cached_prospects = current_app.data_cache['prospects']
        logger.info(f"� Returning cached prospects data: {len(cached_prospects)} prospects")
        
        return jsonify({
            'success': True,
            'prospects': cached_prospects,
            'total_prospects': len(cached_prospects),
            'page': 1,
            'total_pages': 1, 
            'per_page': len(cached_prospects),
            'source': 'cache'
        })
    
    try:
        # Import ClubHub API client and credentials from proper config
        from services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        logger.info("🔍 Fetching ALL prospects using ClubHub API client (paginated)...")
        
        # Initialize and authenticate the API client
        client = ClubHubAPIClient()
        
        # Authenticate first using proper config credentials
        auth_success = client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
        if not auth_success:
            logger.error("❌ ClubHub authentication failed")
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed',
                'prospects': [],
                'total_prospects': 0
            }), 401
        
        # Now use the authenticated client to get prospects
        all_prospects = client.get_all_prospects_paginated()
        
        if not all_prospects:
            logger.warning("⚠️ No prospects returned from ClubHubAPIClient")
            return jsonify({
                'success': False,
                'error': 'No prospects found or API authentication failed',
                'prospects': [],
                'total_prospects': 0
            }), 404
        
        # Process prospects data to ensure full_name is set
        for prospect in all_prospects:
            prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
        
        logger.info(f"✅ Successfully fetched {len(all_prospects)} prospects from ClubHub API")
        
        # Cache the results for faster subsequent requests
        if hasattr(current_app, 'data_cache'):
            current_app.data_cache['prospects'] = all_prospects
            current_app.data_cache['last_sync']['prospects'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'prospects': all_prospects,
            'total_prospects': len(all_prospects),
            'page': 1,
            'total_pages': 1,
            'per_page': len(all_prospects),
            'source': 'api'
        })
        
    except ImportError as e:
        logger.error(f"❌ Could not import ClubHub credentials or API client: {e}")
        return jsonify({'success': False, 'error': 'ClubHub API client or credentials not available'}), 500
        
    except Exception as e:
        logger.error(f"❌ Error getting prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prospects_bp.route('/api/prospects/paginated')  
def get_prospects_paginated():
    """API endpoint to get paginated prospects for frontend display."""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '').strip()
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get prospects from cache or fresh API
        if hasattr(current_app, 'data_cache') and current_app.data_cache.get('prospects'):
            all_prospects = current_app.data_cache['prospects']
        else:
            # Fallback: get fresh prospects with authentication
            from services.api.clubhub_api_client import ClubHubAPIClient
            
            # Use direct credentials to avoid import issues
            CLUBHUB_EMAIL = "mayo.jeremy2212@gmail.com"
            CLUBHUB_PASSWORD = "SruLEqp464_GLrF"
            
            client = ClubHubAPIClient()
            
            # Authenticate first
            auth_success = client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
            if not auth_success:
                logger.error("❌ ClubHub authentication failed in paginated route")
                return jsonify({'success': False, 'error': 'ClubHub authentication failed'}), 401
            
            all_prospects = client.get_all_prospects_paginated()
            
            # Cache the results
            if hasattr(current_app, 'data_cache'):
                current_app.data_cache['prospects'] = all_prospects
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            filtered_prospects = []
            for prospect in all_prospects:
                # Search in name, email, phone
                if (search_lower in prospect.get('full_name', '').lower() or
                    search_lower in prospect.get('email', '').lower() or
                    search_lower in prospect.get('mobilePhone', '').lower() or
                    search_lower in prospect.get('firstName', '').lower() or
                    search_lower in prospect.get('lastName', '').lower()):
                    filtered_prospects.append(prospect)
            all_prospects = filtered_prospects
        
        # Calculate pagination
        total_prospects = len(all_prospects)
        total_pages = (total_prospects + per_page - 1) // per_page
        
        # Get paginated subset
        paginated_prospects = all_prospects[offset:offset + per_page]
        
        return jsonify({
            'success': True,
            'prospects': paginated_prospects,
            'total_prospects': total_prospects,
            'page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'search': search
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting paginated prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


