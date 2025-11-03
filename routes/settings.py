"""
Settings API Routes
RESTful API for bot configuration management
"""

import logging
from flask import Blueprint, request, jsonify
from src.services.settings_manager import get_settings_manager

logger = logging.getLogger(__name__)

# Create blueprint
blueprint = Blueprint('settings', __name__, url_prefix='/api/settings')


@blueprint.route('', methods=['GET'])
def get_all_settings():
    """Get all settings grouped by category"""
    try:
        settings_manager = get_settings_manager()
        all_settings = settings_manager.get_all()
        
        return jsonify({
            "success": True,
            "settings": all_settings
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting all settings: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<category>', methods=['GET'])
def get_settings_by_category(category):
    """Get all settings for a specific category"""
    try:
        settings_manager = get_settings_manager()
        category_settings = settings_manager.get_category(category)
        
        return jsonify({
            "success": True,
            "category": category,
            "settings": category_settings
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting settings for {category}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<category>/<key>', methods=['GET'])
def get_setting(category, key):
    """Get a single setting value"""
    try:
        settings_manager = get_settings_manager()
        value = settings_manager.get(category, key)
        
        return jsonify({
            "success": True,
            "category": category,
            "key": key,
            "value": value
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting setting {category}.{key}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<category>/<key>', methods=['PUT'])
def update_setting(category, key):
    """Update a single setting"""
    try:
        data = request.get_json()
        value = data.get('value')
        user = data.get('user', 'web_user')
        reason = data.get('reason')
        
        if value is None:
            return jsonify({
                "success": False,
                "error": "Missing 'value' in request body"
            }), 400
        
        settings_manager = get_settings_manager()
        success = settings_manager.set(category, key, value, user, reason)
        
        if success:
            return jsonify({
                "success": True,
                "category": category,
                "key": key,
                "value": value,
                "message": f"Setting {category}.{key} updated successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to update setting"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Error updating setting {category}.{key}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<category>', methods=['PUT'])
def update_category_settings(category):
    """Bulk update settings in a category"""
    try:
        data = request.get_json()
        settings = data.get('settings', {})
        user = data.get('user', 'web_user')
        reason = data.get('reason', f'Bulk update {category}')
        
        if not settings:
            return jsonify({
                "success": False,
                "error": "Missing 'settings' in request body"
            }), 400
        
        settings_manager = get_settings_manager()
        updated_count = 0
        failed_count = 0
        errors = []
        
        for key, value in settings.items():
            success = settings_manager.set(category, key, value, user, reason)
            if success:
                updated_count += 1
            else:
                failed_count += 1
                errors.append(f"Failed to update {key}")
        
        return jsonify({
            "success": failed_count == 0,
            "category": category,
            "updated": updated_count,
            "failed": failed_count,
            "errors": errors if errors else None,
            "message": f"Updated {updated_count}/{len(settings)} settings in {category}"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error bulk updating {category}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/reset/<category>', methods=['POST'])
def reset_category_to_defaults(category):
    """Reset a category to default values"""
    try:
        data = request.get_json() or {}
        user = data.get('user', 'web_user')
        
        settings_manager = get_settings_manager()
        success = settings_manager.reset_category(category, user)
        
        if success:
            return jsonify({
                "success": True,
                "category": category,
                "message": f"Category {category} reset to defaults"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to reset category {category}"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Error resetting category {category}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/history/<category>/<key>', methods=['GET'])
def get_setting_history(category, key):
    """Get change history for a setting"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        settings_manager = get_settings_manager()
        history = settings_manager.get_history(category, key, limit)
        
        return jsonify({
            "success": True,
            "category": category,
            "key": key,
            "history": history
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting history for {category}.{key}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/export', methods=['GET'])
def export_settings():
    """Export all settings as JSON"""
    try:
        settings_manager = get_settings_manager()
        json_str = settings_manager.export_settings()
        
        return jsonify({
            "success": True,
            "settings_json": json_str
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error exporting settings: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/import', methods=['POST'])
def import_settings():
    """Import settings from JSON"""
    try:
        data = request.get_json()
        json_str = data.get('settings_json')
        user = data.get('user', 'web_user')
        
        if not json_str:
            return jsonify({
                "success": False,
                "error": "Missing 'settings_json' in request body"
            }), 400
        
        settings_manager = get_settings_manager()
        success = settings_manager.import_settings(json_str, user)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Settings imported successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to import settings"
            }), 400
        
    except Exception as e:
        logger.error(f"❌ Error importing settings: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/defaults', methods=['GET'])
def get_defaults():
    """Get default settings for all categories"""
    try:
        settings_manager = get_settings_manager()
        defaults = settings_manager.DEFAULTS
        
        return jsonify({
            "success": True,
            "defaults": defaults
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting defaults: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/defaults/<category>', methods=['GET'])
def get_category_defaults(category):
    """Get default settings for a specific category"""
    try:
        settings_manager = get_settings_manager()
        defaults = settings_manager.DEFAULTS.get(category, {})
        
        return jsonify({
            "success": True,
            "category": category,
            "defaults": defaults
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error getting defaults for {category}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
