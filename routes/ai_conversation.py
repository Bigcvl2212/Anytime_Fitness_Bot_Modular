"""
AI Conversation Management Routes

API endpoints for AI conversation history, manual commands,
and approval workflows.
"""

import logging
from flask import Blueprint, jsonify, request, Response
from datetime import datetime
from typing import Dict, Any
import json
import uuid

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.ai.agent_core import GymAgentCore
from services.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

blueprint = Blueprint('ai_conversation', __name__, url_prefix='/api/ai/conversation')

# Global agent instance
_agent = None

def init_agent(agent: GymAgentCore):
    """Initialize the global agent instance"""
    global _agent
    _agent = agent


# ============================================
# CONVERSATION HISTORY
# ============================================

@blueprint.route('/history', methods=['GET'])
def get_conversation_history():
    """Get recent AI conversation messages
    
    Query params:
        limit: Maximum messages to return (default 50)
        workflow_id: Filter by workflow (optional)
    
    Returns:
        {
            "success": True,
            "messages": [
                {
                    "id": "...",
                    "type": "workflow_notification",
                    "workflow_id": "daily_campaigns",
                    "timestamp": "2025-10-11T06:00:00",
                    "content": {...}
                }
            ]
        }
    """
    try:
        db = DatabaseManager()
        
        limit = request.args.get('limit', 50, type=int)
        workflow_id = request.args.get('workflow_id')
        
        # Query conversation history
        if workflow_id:
            query = """
                SELECT * FROM ai_conversations
                WHERE workflow_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            rows = db.execute_query(query, (workflow_id, limit), fetch_all=True)
        else:
            query = """
                SELECT * FROM ai_conversations
                ORDER BY timestamp DESC
                LIMIT ?
            """
            rows = db.execute_query(query, (limit,), fetch_all=True)
        
        messages = [dict(row) for row in rows] if rows else []
        
        return jsonify({
            "success": True,
            "messages": messages,
            "count": len(messages)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting conversation history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/add', methods=['POST'])
def add_conversation_message():
    """Add a message to conversation history
    
    Body:
        {
            "type": "workflow_notification",
            "workflow_id": "daily_campaigns",
            "content": {...}
        }
    
    Returns:
        {
            "success": True,
            "message_id": "..."
        }
    """
    try:
        data = request.json
        db = DatabaseManager()
        
        # Ensure table exists
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                workflow_id TEXT,
                timestamp TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """, fetch_all=False)
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        db.execute_query("""
            INSERT INTO ai_conversations (id, type, workflow_id, timestamp, content)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message_id,
            data.get('type', 'generic'),
            data.get('workflow_id'),
            timestamp,
            json.dumps(data.get('content', {}))
        ), fetch_all=False)
        
        return jsonify({
            "success": True,
            "message_id": message_id,
            "timestamp": timestamp
        })
        
    except Exception as e:
        logger.error(f"❌ Error adding conversation message: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# MANUAL COMMANDS
# ============================================

@blueprint.route('/command', methods=['POST'])
def execute_ai_command():
    """Execute a manual AI command
    
    Body:
        {
            "command": "Show top 10 past due accounts",
            "session_id": "..."
        }
    
    Returns:
        {
            "success": True,
            "result": "...",
            "tool_calls": [...],
            "iterations": 3
        }
    """
    try:
        if not _agent:
            return jsonify({
                "success": False,
                "error": "AI agent not initialized"
            }), 503
        
        data = request.json
        command = data.get('command')
        
        if not command:
            return jsonify({
                "success": False,
                "error": "Command is required"
            }), 400
        
        logger.info(f"🤖 Executing manual command: {command[:100]}...")
        
        # Execute command with agent
        result = _agent.execute_task(command, max_iterations=10)
        
        # Log to conversation history
        try:
            db = DatabaseManager()
            db.execute_query("""
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    workflow_id TEXT,
                    timestamp TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """, fetch_all=False)
            
            message_id = str(uuid.uuid4())
            db.execute_query("""
                INSERT INTO ai_conversations (id, type, workflow_id, timestamp, content)
                VALUES (?, ?, ?, ?, ?)
            """, (
                message_id,
                'manual_command',
                None,
                datetime.now().isoformat(),
                json.dumps({
                    'command': command,
                    'result': result
                })
            ), fetch_all=False)
        except Exception as log_error:
            logger.warning(f"Failed to log conversation: {log_error}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error executing command: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# APPROVAL SYSTEM
# ============================================

@blueprint.route('/approvals/pending', methods=['GET'])
def get_pending_approvals():
    """Get actions requiring manager approval
    
    Returns:
        {
            "success": True,
            "approvals": [
                {
                    "id": "...",
                    "workflow_id": "door_access_management",
                    "action": "lock_members",
                    "details": {...},
                    "created_at": "...",
                    "expires_at": "..."
                }
            ]
        }
    """
    try:
        db = DatabaseManager()
        
        # Ensure table exists
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS approval_requests (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                decided_by TEXT,
                decided_at TEXT
            )
        """, fetch_all=False)
        
        # Get pending approvals (not expired)
        query = """
            SELECT * FROM approval_requests
            WHERE status = 'pending'
            AND expires_at > ?
            ORDER BY created_at DESC
        """
        
        rows = db.execute_query(query, (datetime.now().isoformat(),), fetch_all=True)
        
        approvals = []
        for row in rows:
            approvals.append({
                'id': row['id'],
                'workflow_id': row['workflow_id'],
                'action': row['action'],
                'details': json.loads(row['details']),
                'created_at': row['created_at'],
                'expires_at': row['expires_at']
            })
        
        return jsonify({
            "success": True,
            "approvals": approvals,
            "count": len(approvals)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting pending approvals: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/approvals/<approval_id>/decide', methods=['POST'])
def decide_approval(approval_id: str):
    """Approve or deny a pending action
    
    Body:
        {
            "decision": "approve" | "deny",
            "manager_id": "...",
            "reason": "..." (optional, for denial)
        }
    
    Returns:
        {
            "success": True,
            "approval_id": "...",
            "status": "approved" | "denied"
        }
    """
    try:
        data = request.json
        decision = data.get('decision')
        manager_id = data.get('manager_id', 'unknown')
        reason = data.get('reason')
        
        if decision not in ['approve', 'deny']:
            return jsonify({
                "success": False,
                "error": "Decision must be 'approve' or 'deny'"
            }), 400
        
        db = DatabaseManager()
        
        # Update approval status
        db.execute_query("""
            UPDATE approval_requests
            SET status = ?,
                decided_by = ?,
                decided_at = ?
            WHERE id = ?
        """, (
            'approved' if decision == 'approve' else 'denied',
            manager_id,
            datetime.now().isoformat(),
            approval_id
        ), fetch_all=False)
        
        # If approved, execute the action
        if decision == 'approve':
            # Get the approval details
            approval = db.execute_query("""
                SELECT * FROM approval_requests WHERE id = ?
            """, (approval_id,), fetch_all=True)
            
            if approval:
                approval = dict(approval[0])
                # TODO: Execute the approved action
                logger.info(f"✅ Executing approved action: {approval['action']}")
        else:
            logger.info(f"❌ Denied action: {reason}")
        
        return jsonify({
            "success": True,
            "approval_id": approval_id,
            "status": 'approved' if decision == 'approve' else 'denied'
        })
        
    except Exception as e:
        logger.error(f"❌ Error deciding approval: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# AVAILABLE TOOLS
# ============================================

@blueprint.route('/tools', methods=['GET'])
def get_available_tools():
    """Get list of all available AI tools
    
    Returns:
        {
            "success": True,
            "tools": [
                {
                    "name": "get_past_due_members",
                    "category": "collections",
                    "description": "...",
                    "risk_level": "safe"
                }
            ]
        }
    """
    try:
        if not _agent:
            return jsonify({
                "success": False,
                "error": "AI agent not initialized"
            }), 503
        
        tools = _agent.list_available_tools()
        
        return jsonify({
            "success": True,
            "tools": tools,
            "count": len(tools)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting available tools: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
