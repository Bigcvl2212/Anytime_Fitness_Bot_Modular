#!/usr/bin/env python3
"""
Club Selection Screen - Allow users to choose which clubs to sync data from
"""

from flask import render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask import Blueprint
import logging
from src.services.multi_club_manager import multi_club_manager

logger = logging.getLogger(__name__)

club_selection_bp = Blueprint('club_selection', __name__)

@club_selection_bp.route('/club-selection')
def club_selection():
    """Display club selection screen"""
    try:
        # Check if user is logged in
        if 'manager_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('auth.login'))
        
        # Get available clubs from multi_club_manager
        available_clubs = multi_club_manager.get_available_clubs_for_selection()
        user_summary = multi_club_manager.get_user_summary()
        
        if not available_clubs:
            flash('No clubs available. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # If user only has one club, skip selection and redirect to dashboard
        if len(available_clubs) == 1:
            single_club = available_clubs[0]
            multi_club_manager.set_selected_clubs([single_club['id']])
            session['selected_clubs'] = [single_club['id']]
            flash(f'Welcome to {single_club["name"]}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        
        return render_template('club_selection.html', 
                             available_clubs=available_clubs,
                             user_summary=user_summary)
        
    except Exception as e:
        logger.error(f"❌ Error in club selection: {e}")
        flash('Error loading club selection. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@club_selection_bp.route('/select-clubs', methods=['POST'])
def select_clubs():
    """Handle club selection submission"""
    try:
        # Check if user is logged in
        if 'manager_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        data = request.get_json()
        selected_club_ids = data.get('club_ids', [])
        
        if not selected_club_ids:
            return jsonify({'error': 'Please select at least one club'}), 400
        
        # Validate and set selected clubs
        valid_clubs = multi_club_manager.set_selected_clubs(selected_club_ids)
        
        if not valid_clubs:
            return jsonify({'error': 'No valid clubs selected'}), 400
        
        # Store in session
        session['selected_clubs'] = valid_clubs
        
        # Get club names for display
        club_names = [multi_club_manager.get_club_name(club_id) for club_id in valid_clubs]
        
        logger.info(f"✅ User selected clubs: {club_names}")
        
        # Trigger startup sync for selected clubs
        try:
            import threading
            from src.services.multi_club_startup_sync import enhanced_startup_sync
            
            logger.info(f"🔄 Attempting to start data sync for clubs: {club_names}")
            
            # Create and start sync thread
            sync_thread = threading.Thread(
                target=enhanced_startup_sync, 
                args=(current_app._get_current_object(),), 
                daemon=True,
                name=f"DataSync-{'-'.join(map(str, valid_clubs))}"
            )
            sync_thread.start()
            
            logger.info(f"✅ Successfully started sync thread '{sync_thread.name}' for clubs: {club_names}")
            
        except ImportError as import_error:
            logger.error(f"❌ Failed to import sync module: {import_error}")
        except Exception as sync_error:
            logger.error(f"❌ Failed to start post-selection sync: {sync_error}")
            import traceback
            logger.error(f"Sync error traceback: {traceback.format_exc()}")
        
        return jsonify({
            'success': True,
            'selected_clubs': valid_clubs,
            'club_names': club_names,
            'redirect_url': url_for('dashboard.dashboard')
        })
        
    except Exception as e:
        logger.error(f"❌ Error selecting clubs: {e}")
        return jsonify({'error': 'Error selecting clubs'}), 500

@club_selection_bp.route('/club-selection/api/clubs')
def api_get_clubs():
    """API endpoint to get available clubs"""
    try:
        if 'manager_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        available_clubs = multi_club_manager.get_available_clubs_for_selection()
        user_summary = multi_club_manager.get_user_summary()
        
        return jsonify({
            'clubs': available_clubs,
            'user': user_summary['user_info'],
            'is_multi_club': user_summary['is_multi_club']
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting clubs API: {e}")
        return jsonify({'error': 'Error loading clubs'}), 500

@club_selection_bp.route('/change-clubs')
def change_clubs():
    """Allow user to change club selection"""
    try:
        if 'manager_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('auth.login'))
        
        # Clear current selection
        if 'selected_clubs' in session:
            del session['selected_clubs']
        multi_club_manager.set_selected_clubs([])
        
        flash('Club selection cleared. Please select clubs again.', 'info')
        return redirect(url_for('club_selection.club_selection'))
        
    except Exception as e:
        logger.error(f"❌ Error changing clubs: {e}")
        flash('Error changing clubs. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard'))
