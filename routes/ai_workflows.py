"""
AI Workflow Management Routes

API endpoints for managing autonomous workflows, execution history,
and real-time status updates.
"""

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.ai.workflow_scheduler import WorkflowScheduler
from src.services.ai.workflow_runner import WorkflowRunner
from src.services.ai.agent_config import AgentConfig

logger = logging.getLogger(__name__)

blueprint = Blueprint('ai_workflows', __name__, url_prefix='/api/ai/workflows')

# Global scheduler instance (initialized by app)
_scheduler = None

def init_scheduler(scheduler: WorkflowScheduler):
    """Initialize the global scheduler instance"""
    global _scheduler
    _scheduler = scheduler


# ============================================
# WORKFLOW STATUS & MANAGEMENT
# ============================================

@blueprint.route('/status', methods=['GET'])
def get_workflows_status():
    """Get status of all scheduled workflows
    
    Returns:
        {
            "success": True,
            "workflows": [
                {
                    "id": "daily_campaigns",
                    "name": "Daily Campaigns",
                    "enabled": True,
                    "status": "running",
                    "next_run": "2025-10-12T06:00:00",
                    "last_run": {
                        "timestamp": "2025-10-11T06:00:00",
                        "duration": 604.35,
                        "success": True,
                        "tool_calls": 8,
                        "iterations": 9
                    },
                    "stats": {
                        "total_runs": 45,
                        "success_rate": 0.94,
                        "avg_duration": 598.2
                    }
                }
            ]
        }
    """
    try:
        if not _scheduler:
            return jsonify({
                "success": False,
                "error": "Workflow scheduler not initialized"
            }), 503
        
        # Get scheduled jobs
        jobs = _scheduler.get_scheduled_jobs()
        
        # Get execution history
        history = _scheduler.get_workflow_stats()
        
        # Build workflow status list
        workflows = []
        
        workflow_configs = {
            'daily_campaigns': {
                'name': 'Daily Campaigns',
                'description': 'Analyze prospects and send targeted campaigns daily'
            },
            'past_due_monitoring': {
                'name': 'Past Due Monitoring',
                'description': 'Monitor and alert on past due accounts hourly'
            },
            'daily_escalation': {
                'name': 'Daily Escalation',
                'description': 'Escalate high-value past due accounts daily'
            },
            'referral_checks': {
                'name': 'Referral Checks',
                'description': 'Check if members should be referred to collections bi-weekly'
            },
            'monthly_invoice_review': {
                'name': 'Monthly Invoice Review',
                'description': 'Review training invoices and send reminders monthly'
            },
            'door_access_management': {
                'name': 'Door Access Management',
                'description': 'Manage door access based on payment status hourly'
            }
        }
        
        for job in jobs:
            workflow_id = job['id']
            config = workflow_configs.get(workflow_id, {})
            
            # Get stats for this workflow
            workflow_history = history.get(workflow_id, {})
            
            workflows.append({
                'id': workflow_id,
                'name': config.get('name', workflow_id),
                'description': config.get('description', ''),
                'enabled': True,
                'next_run': job['next_run_time'],
                'trigger': job['trigger'],
                'last_run': workflow_history.get('last_execution'),
                'stats': workflow_history.get('stats', {})
            })
        
        return jsonify({
            "success": True,
            "workflows": workflows,
            "scheduler_running": _scheduler.scheduler.running if _scheduler else False
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting workflow status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<workflow_id>/history', methods=['GET'])
def get_workflow_history(workflow_id: str):
    """Get execution history for a specific workflow
    
    Args:
        workflow_id: Workflow identifier
    
    Query params:
        limit: Maximum number of executions to return (default 20)
    
    Returns:
        {
            "success": True,
            "workflow_id": "daily_campaigns",
            "executions": [
                {
                    "timestamp": "2025-10-11T06:00:00",
                    "duration": 604.35,
                    "success": True,
                    "iterations": 9,
                    "tool_calls": [...]
                }
            ]
        }
    """
    try:
        if not _scheduler:
            return jsonify({
                "success": False,
                "error": "Workflow scheduler not initialized"
            }), 503
        
        limit = request.args.get('limit', 20, type=int)
        
        history = _scheduler.get_execution_history(workflow_id)
        
        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "executions": history[:limit] if history else []
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting workflow history: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<workflow_id>/run', methods=['POST'])
def run_workflow_now(workflow_id: str):
    """Manually trigger a workflow to run immediately
    
    Args:
        workflow_id: Workflow identifier
    
    Returns:
        {
            "success": True,
            "workflow_id": "daily_campaigns",
            "execution": {
                "started_at": "2025-10-11T14:30:00",
                "status": "running"
            }
        }
    """
    try:
        logger.info(f"🔥 Manually triggering workflow: {workflow_id}")
        
        result = None
        
        # First try the UnifiedWorkflowManager (handles auto_reply_messages, prospect_outreach, etc.)
        try:
            from src.services.ai.unified_workflow_manager import get_workflow_manager
            unified_manager = get_workflow_manager()
            if unified_manager and workflow_id in unified_manager._workflows:
                logger.info(f"   Running via UnifiedWorkflowManager: {workflow_id}")
                result = unified_manager.run_workflow(workflow_id, force=True)
        except Exception as e:
            logger.warning(f"UnifiedWorkflowManager not available: {e}")
        
        # Fall back to scheduler for scheduled workflows (daily_campaigns, etc.)
        if result is None and _scheduler:
            result = _scheduler.run_workflow_now(workflow_id)
        elif result is None:
            return jsonify({
                "success": False,
                "error": "Workflow scheduler not initialized"
            }), 503
        
        if result.get('success'):
            return jsonify({
                "success": True,
                "workflow_id": workflow_id,
                "execution": {
                    "started_at": datetime.now().isoformat(),
                    "duration": result.get('duration_seconds') or result.get('duration'),
                    "success": result.get('success'),
                    "result": result.get('result')
                }
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Workflow execution failed')
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error running workflow {workflow_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<workflow_id>/pause', methods=['POST'])
def pause_workflow(workflow_id: str):
    """Pause a scheduled workflow
    
    Args:
        workflow_id: Workflow identifier
    
    Returns:
        {
            "success": True,
            "workflow_id": "daily_campaigns",
            "status": "paused"
        }
    """
    try:
        if not _scheduler:
            return jsonify({
                "success": False,
                "error": "Workflow scheduler not initialized"
            }), 503
        
        _scheduler.pause_workflow(workflow_id)
        
        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "status": "paused"
        })
        
    except Exception as e:
        logger.error(f"❌ Error pausing workflow {workflow_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/<workflow_id>/resume', methods=['POST'])
def resume_workflow(workflow_id: str):
    """Resume a paused workflow
    
    Args:
        workflow_id: Workflow identifier
    
    Returns:
        {
            "success": True,
            "workflow_id": "daily_campaigns",
            "status": "running"
        }
    """
    try:
        if not _scheduler:
            return jsonify({
                "success": False,
                "error": "Workflow scheduler not initialized"
            }), 503
        
        _scheduler.resume_workflow(workflow_id)
        
        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "status": "running"
        })
        
    except Exception as e:
        logger.error(f"❌ Error resuming workflow {workflow_id}: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# WORKFLOW CONFIGURATION
# ============================================

@blueprint.route('/<workflow_id>/config', methods=['GET'])
def get_workflow_config(workflow_id: str):
    """Get configuration for a specific workflow
    
    Returns:
        {
            "success": True,
            "workflow_id": "daily_campaigns",
            "config": {
                "dry_run": True,
                "max_iterations": 10,
                "require_approval": True
            }
        }
    """
    try:
        config = AgentConfig()
        
        workflow_configs = {
            'daily_campaigns': {
                'enabled': config.DAILY_CAMPAIGNS_ENABLED,
                'schedule': f"{config.DAILY_CAMPAIGNS_HOUR}:{config.DAILY_CAMPAIGNS_MINUTE:02d}",
                'dry_run': config.DRY_RUN_MODE,
                'max_iterations': config.MAX_AGENT_ITERATIONS,
                'require_approval': False
            },
            'past_due_monitoring': {
                'enabled': config.PAST_DUE_MONITORING_ENABLED,
                'interval_minutes': config.MONITORING_INTERVAL_MINUTES,
                'dry_run': config.DRY_RUN_MODE,
                'alert_threshold': config.PAST_DUE_ALERT_THRESHOLD,
                'require_approval': False
            },
            'daily_escalation': {
                'enabled': config.DAILY_ESCALATION_ENABLED,
                'schedule': f"{config.DAILY_ESCALATION_HOUR}:{config.DAILY_ESCALATION_MINUTE:02d}",
                'dry_run': config.DRY_RUN_MODE,
                'escalation_threshold': config.ESCALATION_THRESHOLD,
                'require_approval': True
            },
            'referral_checks': {
                'enabled': config.REFERRAL_CHECKS_ENABLED,
                'schedule': f"Every {config.REFERRAL_CHECK_WEEK_INTERVAL} weeks on {config.REFERRAL_CHECK_DAY}",
                'dry_run': config.DRY_RUN_MODE,
                'min_attempts': config.MIN_COLLECTION_ATTEMPTS,
                'require_approval': True
            },
            'monthly_invoice_review': {
                'enabled': config.MONTHLY_INVOICE_REVIEW_ENABLED,
                'schedule': f"Day {config.INVOICE_REVIEW_DAY} at {config.INVOICE_REVIEW_HOUR}:{config.INVOICE_REVIEW_MINUTE:02d}",
                'dry_run': config.DRY_RUN_MODE,
                'require_approval': False
            },
            'door_access_management': {
                'enabled': config.DOOR_ACCESS_MANAGEMENT_ENABLED,
                'interval_minutes': config.DOOR_ACCESS_CHECK_INTERVAL_MINUTES,
                'dry_run': config.DRY_RUN_MODE,
                'require_approval': True
            }
        }
        
        if workflow_id not in workflow_configs:
            return jsonify({
                "success": False,
                "error": f"Unknown workflow: {workflow_id}"
            }), 404
        
        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "config": workflow_configs[workflow_id]
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting workflow config: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# HEALTH CHECK
# ============================================

@blueprint.route('/health', methods=['GET'])
def health_check():
    """Check workflow system health
    
    Returns:
        {
            "success": True,
            "scheduler_running": True,
            "workflows_count": 6,
            "agent_available": True
        }
    """
    try:
        return jsonify({
            "success": True,
            "scheduler_running": _scheduler.scheduler.running if _scheduler else False,
            "workflows_count": len(_scheduler.get_scheduled_jobs()) if _scheduler else 0,
            "agent_available": True  # TODO: Check if Claude API key is set
        })
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================
# AUTO-REPLY CONTROL
# ============================================

@blueprint.route('/auto-reply/status', methods=['GET'])
def get_auto_reply_status():
    """Get the current status of AI auto-reply
    
    Returns:
        {
            "success": True,
            "enabled": True,
            "stats": {
                "messages_processed": 150,
                "auto_responses_sent": 45,
                "last_response_time": "2025-12-01T10:30:00"
            }
        }
    """
    try:
        from flask import current_app
        
        message_sync = getattr(current_app, 'message_poller', None)
        unified_agent = None
        
        if message_sync:
            unified_agent = getattr(message_sync, 'unified_ai_agent', None)
        
        stats = {}
        if unified_agent:
            stats = unified_agent.stats
        
        return jsonify({
            "success": True,
            "enabled": message_sync.ai_enabled if message_sync else False,
            "message_sync_running": message_sync.running if message_sync else False,
            "poll_interval": message_sync.poll_interval if message_sync else 0,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting auto-reply status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/auto-reply/enable', methods=['POST'])
def enable_auto_reply():
    """Enable AI auto-reply for incoming messages
    
    Returns:
        {
            "success": True,
            "message": "AI auto-reply enabled"
        }
    """
    try:
        from flask import current_app
        
        message_sync = getattr(current_app, 'message_poller', None)
        
        if not message_sync:
            return jsonify({
                "success": False,
                "error": "Message sync service not available"
            }), 503
        
        message_sync.enable_ai()
        
        return jsonify({
            "success": True,
            "message": "AI auto-reply enabled",
            "enabled": True
        })
        
    except Exception as e:
        logger.error(f"❌ Error enabling auto-reply: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/auto-reply/disable', methods=['POST'])
def disable_auto_reply():
    """Disable AI auto-reply for incoming messages
    
    Returns:
        {
            "success": True,
            "message": "AI auto-reply disabled"
        }
    """
    try:
        from flask import current_app
        
        message_sync = getattr(current_app, 'message_poller', None)
        
        if not message_sync:
            return jsonify({
                "success": False,
                "error": "Message sync service not available"
            }), 503
        
        message_sync.disable_ai()
        
        return jsonify({
            "success": True,
            "message": "AI auto-reply disabled",
            "enabled": False
        })
        
    except Exception as e:
        logger.error(f"❌ Error disabling auto-reply: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/auto-reply/test', methods=['POST'])
def test_auto_reply():
    """Test auto-reply with a specific message (doesn't actually send)
    
    Request body:
        {
            "message": "What are your hours?",
            "from_user": "Test User"
        }
    
    Returns:
        {
            "success": True,
            "intent": "business_hours",
            "confidence": 0.92,
            "would_respond": True,
            "draft_response": "Our gym is open 24/7 for members..."
        }
    """
    try:
        from flask import current_app
        import asyncio
        
        data = request.get_json() or {}
        test_message = data.get('message', 'What are your hours?')
        from_user = data.get('from_user', 'Test User')
        
        message_sync = getattr(current_app, 'message_poller', None)
        
        if not message_sync:
            return jsonify({
                "success": False,
                "error": "Message sync service not available"
            }), 503
        
        unified_agent = getattr(message_sync, 'unified_ai_agent', None)
        
        if not unified_agent:
            return jsonify({
                "success": False,
                "error": "AI agent not available"
            }), 503
        
        # Create test message
        test_msg = {
            'id': f'test_{int(datetime.now().timestamp())}',
            'content': test_message,
            'from_user': from_user,
            'owner_id': '187032782',
            'timestamp': datetime.now().isoformat(),
            'member_id': 'test_member'
        }
        
        # Check if AI would respond
        would_respond = message_sync._should_ai_respond(test_msg)
        
        # Get intent classification
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        intent, confidence = loop.run_until_complete(
            unified_agent.inbox_ai.classify_intent(test_message)
        )
        
        loop.close()
        
        return jsonify({
            "success": True,
            "test_message": test_message,
            "from_user": from_user,
            "intent": intent,
            "confidence": confidence,
            "would_respond": would_respond,
            "note": "This is a test - no message was sent"
        })
        
    except Exception as e:
        logger.error(f"❌ Error testing auto-reply: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
