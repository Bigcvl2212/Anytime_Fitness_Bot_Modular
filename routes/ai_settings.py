"""
AI Settings & Workflow Management Routes
=========================================
API endpoints for:
- AI workflow enable/disable toggles
- Knowledge base document management
- Payment plan exemption management
- Workflow execution history
"""

import logging
import json
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

blueprint = Blueprint('ai_settings', __name__, url_prefix='/api/ai')

# Module-level references (initialized by app)
_db_manager = None
_workflow_manager = None
_knowledge_base = None


def init_ai_settings(db_manager=None, workflow_manager=None, knowledge_base=None):
    """Initialize the AI settings module with dependencies"""
    global _db_manager, _workflow_manager, _knowledge_base
    _db_manager = db_manager
    _workflow_manager = workflow_manager
    _knowledge_base = knowledge_base
    logger.info("✅ AI Settings routes initialized")


# ============================================
# WORKFLOW MANAGEMENT
# ============================================

@blueprint.route('/workflows', methods=['GET'])
def get_all_workflows():
    """
    Get all registered workflows with their status.
    
    Returns:
        List of workflows with enabled/disabled status, config, last run time
    """
    try:
        if not _workflow_manager:
            return jsonify({
                "success": False,
                "error": "Workflow manager not initialized"
            }), 503
        
        workflows = _workflow_manager.get_all_workflow_statuses()
        
        return jsonify({
            "success": True,
            "workflows": workflows,
            "background_worker_running": _workflow_manager.is_running
        })
        
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/workflows/<workflow_name>', methods=['GET'])
def get_workflow(workflow_name: str):
    """Get details for a specific workflow"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        settings = _workflow_manager.get_workflow_settings(workflow_name)
        
        return jsonify({
            "success": True,
            "workflow_name": workflow_name,
            "settings": settings
        })
        
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/workflows/<workflow_name>/enable', methods=['POST'])
def enable_workflow(workflow_name: str):
    """Enable a workflow"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        success = _workflow_manager.enable_workflow(workflow_name)
        
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "enabled": True,
            "message": f"Workflow '{workflow_name}' enabled"
        })
        
    except Exception as e:
        logger.error(f"Error enabling workflow {workflow_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/workflows/<workflow_name>/disable', methods=['POST'])
def disable_workflow(workflow_name: str):
    """Disable a workflow"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        success = _workflow_manager.disable_workflow(workflow_name)
        
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "enabled": False,
            "message": f"Workflow '{workflow_name}' disabled"
        })
        
    except Exception as e:
        logger.error(f"Error disabling workflow {workflow_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/workflows/<workflow_name>/config', methods=['PUT'])
def update_workflow_config(workflow_name: str):
    """Update workflow configuration"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        data = request.get_json()
        config = data.get('config', {})
        
        success = _workflow_manager.update_workflow_settings(workflow_name, config=config)
        
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "message": f"Configuration updated for '{workflow_name}'"
        })
        
    except Exception as e:
        logger.error(f"Error updating workflow config {workflow_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/workflows/<workflow_name>/run', methods=['POST'])
def run_workflow_manually(workflow_name: str):
    """Manually trigger a workflow to run"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        data = request.get_json() or {}
        force = data.get('force', False)
        
        result = _workflow_manager.run_workflow(workflow_name, force=force)
        
        return jsonify({
            "success": result.get("success", False),
            "workflow_name": workflow_name,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error running workflow {workflow_name}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# KNOWLEDGE BASE MANAGEMENT
# ============================================

@blueprint.route('/knowledge-base', methods=['GET'])
def get_knowledge_base():
    """
    Get all knowledge base documents grouped by category.
    
    Returns:
        Documents organized by category with metadata
    """
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        all_docs = _knowledge_base.get_all_documents()
        categories = _knowledge_base.CATEGORIES
        
        return jsonify({
            "success": True,
            "documents": all_docs,
            "categories": categories,
            "total_count": sum(len(docs) for docs in all_docs.values())
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/knowledge-base/categories', methods=['GET'])
def get_kb_categories():
    """Get available knowledge base categories"""
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        return jsonify({
            "success": True,
            "categories": _knowledge_base.CATEGORIES
        })
        
    except Exception as e:
        logger.error(f"Error getting KB categories: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/knowledge-base/<category>', methods=['GET'])
def get_kb_category(category: str):
    """Get all documents in a category"""
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        docs = _knowledge_base.get_documents_by_category(category)
        
        return jsonify({
            "success": True,
            "category": category,
            "documents": docs
        })
        
    except Exception as e:
        logger.error(f"Error getting KB category {category}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/knowledge-base', methods=['POST'])
def add_kb_document():
    """
    Add a new document to the knowledge base.
    
    Request body:
        {
            "category": "sales_process",
            "title": "Membership Pricing 2024",
            "content": "Full document content...",
            "priority": 1
        }
    """
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        data = request.get_json()
        
        required = ['category', 'title', 'content']
        for field in required:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        success = _knowledge_base.add_document(
            category=data['category'],
            title=data['title'],
            content=data['content'],
            priority=data.get('priority', 1)
        )
        
        return jsonify({
            "success": success,
            "message": f"Document '{data['title']}' added to {data['category']}"
        })
        
    except Exception as e:
        logger.error(f"Error adding KB document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/knowledge-base/<category>/<title>', methods=['PUT'])
def update_kb_document(category: str, title: str):
    """Update an existing knowledge base document"""
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        data = request.get_json()
        
        success = _knowledge_base.update_document(
            category=category,
            title=title,
            content=data.get('content'),
            priority=data.get('priority'),
            active=data.get('active')
        )
        
        return jsonify({
            "success": success,
            "message": f"Document '{title}' updated"
        })
        
    except Exception as e:
        logger.error(f"Error updating KB document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/knowledge-base/<category>/<title>', methods=['DELETE'])
def delete_kb_document(category: str, title: str):
    """Delete a knowledge base document"""
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        success = _knowledge_base.delete_document(category, title)
        
        return jsonify({
            "success": success,
            "message": f"Document '{title}' deleted from {category}"
        })
        
    except Exception as e:
        logger.error(f"Error deleting KB document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/knowledge-base/context', methods=['GET'])
def get_ai_context():
    """
    Get the full AI context built from the knowledge base.
    Useful for previewing what the AI will see.
    """
    try:
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not initialized"}), 503
        
        context = _knowledge_base.build_ai_context()
        
        return jsonify({
            "success": True,
            "context": context,
            "character_count": len(context)
        })
        
    except Exception as e:
        logger.error(f"Error getting AI context: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# PAYMENT PLAN EXEMPTIONS
# ============================================

@blueprint.route('/payment-plan-exemptions', methods=['GET'])
def get_payment_plan_exemptions():
    """Get all members with payment plan exemptions"""
    try:
        if not _db_manager:
            return jsonify({"success": False, "error": "Database not initialized"}), 503
        
        # Query members with payment_plan_exempt = 1
        rows = _db_manager.execute_query(
            """
            SELECT member_id, name, email, phone, payment_plan_exempt, past_due_amount, past_due_days
            FROM members 
            WHERE payment_plan_exempt = 1
            ORDER BY name
            """,
            fetch_all=True
        )
        
        exempt_members = []
        for row in (rows or []):
            exempt_members.append({
                "member_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "exempt": bool(row[4]),
                "past_due_amount": row[5],
                "past_due_days": row[6]
            })
        
        return jsonify({
            "success": True,
            "exempt_members": exempt_members,
            "count": len(exempt_members)
        })
        
    except Exception as e:
        logger.error(f"Error getting payment plan exemptions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/payment-plan-exemptions/<member_id>', methods=['POST'])
def add_payment_plan_exemption(member_id: str):
    """Add payment plan exemption for a member"""
    try:
        if not _db_manager:
            return jsonify({"success": False, "error": "Database not initialized"}), 503
        
        data = request.get_json() or {}
        reason = data.get('reason', 'Added via AI settings')
        
        # Update member record
        _db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 1 WHERE member_id = ?",
            (member_id,)
        )
        
        logger.info(f"Added payment plan exemption for member {member_id}: {reason}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "exempt": True,
            "message": f"Payment plan exemption added for member {member_id}"
        })
        
    except Exception as e:
        logger.error(f"Error adding payment plan exemption: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/payment-plan-exemptions/<member_id>', methods=['DELETE'])
def remove_payment_plan_exemption(member_id: str):
    """Remove payment plan exemption for a member"""
    try:
        if not _db_manager:
            return jsonify({"success": False, "error": "Database not initialized"}), 503
        
        # Update member record
        _db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 0 WHERE member_id = ?",
            (member_id,)
        )
        
        logger.info(f"Removed payment plan exemption for member {member_id}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "exempt": False,
            "message": f"Payment plan exemption removed for member {member_id}"
        })
        
    except Exception as e:
        logger.error(f"Error removing payment plan exemption: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# EXECUTION HISTORY
# ============================================

@blueprint.route('/execution-history', methods=['GET'])
def get_execution_history():
    """Get workflow execution history"""
    try:
        if not _db_manager:
            return jsonify({"success": False, "error": "Database not initialized"}), 503
        
        workflow_name = request.args.get('workflow')
        limit = request.args.get('limit', 50, type=int)
        
        if workflow_name:
            query = """
                SELECT workflow_name, success, duration_seconds, result, executed_at
                FROM ai_workflow_execution_log
                WHERE workflow_name = ?
                ORDER BY executed_at DESC
                LIMIT ?
            """
            rows = _db_manager.execute_query(query, (workflow_name, limit), fetch_all=True)
        else:
            query = """
                SELECT workflow_name, success, duration_seconds, result, executed_at
                FROM ai_workflow_execution_log
                ORDER BY executed_at DESC
                LIMIT ?
            """
            rows = _db_manager.execute_query(query, (limit,), fetch_all=True)
        
        history = []
        for row in (rows or []):
            history.append({
                "workflow_name": row[0],
                "success": bool(row[1]),
                "duration_seconds": row[2],
                "result": json.loads(row[3]) if row[3] else None,
                "executed_at": row[4]
            })
        
        return jsonify({
            "success": True,
            "history": history,
            "count": len(history)
        })
        
    except Exception as e:
        logger.error(f"Error getting execution history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# BACKGROUND WORKER CONTROL
# ============================================

@blueprint.route('/worker/start', methods=['POST'])
def start_background_worker():
    """Start the background workflow worker"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        data = request.get_json() or {}
        interval = data.get('check_interval_seconds', 60)
        
        _workflow_manager.start_background_worker(interval)
        
        return jsonify({
            "success": True,
            "message": f"Background worker started (checking every {interval}s)",
            "running": True
        })
        
    except Exception as e:
        logger.error(f"Error starting background worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/worker/stop', methods=['POST'])
def stop_background_worker():
    """Stop the background workflow worker"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        _workflow_manager.stop_background_worker()
        
        return jsonify({
            "success": True,
            "message": "Background worker stopped",
            "running": False
        })
        
    except Exception as e:
        logger.error(f"Error stopping background worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route('/worker/status', methods=['GET'])
def get_worker_status():
    """Get background worker status"""
    try:
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not initialized"}), 503
        
        return jsonify({
            "success": True,
            "running": _workflow_manager.is_running
        })
        
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
