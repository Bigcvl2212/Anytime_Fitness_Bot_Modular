"""
AI Settings Routes Blueprint
Provides the AI settings page and API endpoints
"""

from flask import Blueprint, render_template, jsonify, request
import logging
import json

logger = logging.getLogger(__name__)

ai_settings_bp = Blueprint('ai_settings', __name__)

# Module-level references (initialized by register function)
_db_manager = None
_workflow_manager = None
_knowledge_base = None


def init_ai_settings_routes(db_manager=None, workflow_manager=None, knowledge_base=None):
    """Initialize AI settings with dependencies"""
    global _db_manager, _workflow_manager, _knowledge_base
    _db_manager = db_manager
    _workflow_manager = workflow_manager
    _knowledge_base = knowledge_base
    logger.info("✅ AI Settings routes initialized with dependencies")


@ai_settings_bp.route('/ai-settings')
def ai_settings_page():
    """Display AI settings and workflow management page."""
    return render_template('ai_settings.html')


@ai_settings_bp.route('/api/ai/workflows', methods=['GET'])
def api_get_workflows():
    """Get all registered workflows with their status."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
        if not _workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not available"}), 503
        
        workflows = _workflow_manager.get_all_workflow_statuses()
        
        return jsonify({
            "success": True,
            "workflows": workflows,
            "background_worker_running": _workflow_manager.is_running
        })
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/workflows/<workflow_name>/enable', methods=['POST'])
def api_enable_workflow(workflow_name):
    """Enable a workflow."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
        success = _workflow_manager.enable_workflow(workflow_name)
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "enabled": True,
            "message": f"Workflow '{workflow_name}' enabled"
        })
    except Exception as e:
        logger.error(f"Error enabling workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/workflows/<workflow_name>/disable', methods=['POST'])
def api_disable_workflow(workflow_name):
    """Disable a workflow."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
        success = _workflow_manager.disable_workflow(workflow_name)
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "enabled": False,
            "message": f"Workflow '{workflow_name}' disabled"
        })
    except Exception as e:
        logger.error(f"Error disabling workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/workflows/<workflow_name>/run', methods=['POST'])
def api_run_workflow(workflow_name):
    """Manually trigger a workflow to run."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
        data = request.get_json() or {}
        force = data.get('force', False)
        
        result = _workflow_manager.run_workflow(workflow_name, force=force)
        
        return jsonify({
            "success": result.get("success", False),
            "workflow_name": workflow_name,
            "result": result
        })
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/workflows/<workflow_name>/config', methods=['POST'])
def api_update_workflow_config(workflow_name):
    """Update workflow configuration."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
        data = request.get_json() or {}
        config = data.get('config', {})
        
        if not config:
            return jsonify({"success": False, "error": "No configuration provided"}), 400
        
        success = _workflow_manager.update_workflow_settings(
            workflow_name=workflow_name,
            config=config
        )
        
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "message": f"Configuration updated for '{workflow_name}'"
        })
    except Exception as e:
        logger.error(f"Error updating workflow config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/knowledge-base', methods=['GET'])
def api_get_knowledge_base():
    """Get all knowledge base documents grouped by category."""
    try:
        if not _knowledge_base:
            _init_knowledge_base()
        
        if not _knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not available"}), 503
        
        all_docs = _knowledge_base.get_all_documents()
        categories = _knowledge_base.CATEGORIES
        
        # Group documents by category
        docs_by_category = {}
        for cat in categories:
            docs_by_category[cat] = []
        
        # all_docs is a list of dicts
        for doc in (all_docs if isinstance(all_docs, list) else []):
            cat = doc.get('category', 'general')
            if cat not in docs_by_category:
                docs_by_category[cat] = []
            docs_by_category[cat].append(doc)
        
        return jsonify({
            "success": True,
            "documents": docs_by_category,
            "categories": categories,
            "total_count": len(all_docs) if isinstance(all_docs, list) else 0
        })
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/knowledge-base', methods=['POST'])
def api_add_kb_document():
    """Add a new document to the knowledge base."""
    try:
        if not _knowledge_base:
            _init_knowledge_base()
        
        data = request.get_json()
        
        required = ['category', 'title', 'content']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
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


@ai_settings_bp.route('/api/ai/knowledge-base/<category>/<title>', methods=['DELETE'])
def api_delete_kb_document(category, title):
    """Delete a knowledge base document."""
    try:
        if not _knowledge_base:
            _init_knowledge_base()
        
        success = _knowledge_base.delete_document(category, title)
        
        return jsonify({
            "success": success,
            "message": f"Document '{title}' deleted from {category}"
        })
    except Exception as e:
        logger.error(f"Error deleting KB document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/payment-plans', methods=['GET'])
def api_get_payment_plans():
    """Get all active payment plans with installments."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        # Get all payment plans
        rows = _db_manager.execute_query(
            """
            SELECT pp.id, pp.member_id, pp.member_name, pp.plan_name, pp.total_amount,
                   pp.balance_remaining, pp.installments_total, pp.installments_paid,
                   pp.frequency_days, pp.start_date, pp.status, pp.notes, pp.created_at
            FROM payment_plans pp
            WHERE pp.status IN ('active', 'completed')
            ORDER BY pp.status ASC, pp.created_at DESC
            """,
            fetch_all=True
        )
        
        plans = []
        for row in (rows or []):
            plan_id = row[0] if isinstance(row, (list, tuple)) else row.get('id')
            member_id = row[1] if isinstance(row, (list, tuple)) else row.get('member_id')
            
            # Get installments for this plan
            installments = _db_manager.execute_query(
                """
                SELECT id, installment_number, amount, due_date, status, paid_date, amount_paid
                FROM payment_plan_installments
                WHERE plan_id = ?
                ORDER BY installment_number
                """,
                (plan_id,),
                fetch_all=True
            )
            
            installments_list = []
            for inst in (installments or []):
                installments_list.append({
                    "id": inst[0] if isinstance(inst, (list, tuple)) else inst.get('id'),
                    "installment_number": inst[1] if isinstance(inst, (list, tuple)) else inst.get('installment_number'),
                    "amount": inst[2] if isinstance(inst, (list, tuple)) else inst.get('amount'),
                    "due_date": inst[3] if isinstance(inst, (list, tuple)) else inst.get('due_date'),
                    "status": inst[4] if isinstance(inst, (list, tuple)) else inst.get('status'),
                    "paid_date": inst[5] if isinstance(inst, (list, tuple)) else inst.get('paid_date'),
                    "amount_paid": inst[6] if isinstance(inst, (list, tuple)) else inst.get('amount_paid')
                })
            
            plans.append({
                "id": plan_id,
                "member_id": member_id,
                "member_name": row[2] if isinstance(row, (list, tuple)) else row.get('member_name'),
                "plan_name": row[3] if isinstance(row, (list, tuple)) else row.get('plan_name'),
                "total_amount": row[4] if isinstance(row, (list, tuple)) else row.get('total_amount'),
                "balance_remaining": row[5] if isinstance(row, (list, tuple)) else row.get('balance_remaining'),
                "installments_total": row[6] if isinstance(row, (list, tuple)) else row.get('installments_total'),
                "installments_paid": row[7] if isinstance(row, (list, tuple)) else row.get('installments_paid'),
                "frequency_days": row[8] if isinstance(row, (list, tuple)) else row.get('frequency_days'),
                "start_date": row[9] if isinstance(row, (list, tuple)) else row.get('start_date'),
                "status": row[10] if isinstance(row, (list, tuple)) else row.get('status'),
                "notes": row[11] if isinstance(row, (list, tuple)) else row.get('notes'),
                "created_at": row[12] if isinstance(row, (list, tuple)) else row.get('created_at'),
                "installments": installments_list
            })
        
        return jsonify({
            "success": True,
            "plans": plans,
            "count": len(plans)
        })
    except Exception as e:
        logger.error(f"Error getting payment plans: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/payment-plans', methods=['POST'])
def api_create_payment_plan():
    """Create a new payment plan for a member."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        from datetime import datetime, timedelta
        
        data = request.get_json() or {}
        member_name = data.get('member_name', '').strip()
        member_id = data.get('member_id')
        total_amount = float(data.get('total_amount', 0))
        installments_total = int(data.get('installments_total', 1))
        frequency_days = int(data.get('frequency_days', 14))
        start_date_str = data.get('start_date')
        notes = data.get('notes', '')
        
        if not member_name:
            return jsonify({"success": False, "error": "Member name is required"}), 400
        if total_amount <= 0:
            return jsonify({"success": False, "error": "Total amount must be greater than zero"}), 400
        if installments_total <= 0:
            return jsonify({"success": False, "error": "Number of payments must be at least 1"}), 400
        
        # If no member_id, try to find by exact name
        if not member_id:
            member_row = _db_manager.execute_query(
                "SELECT prospect_id FROM members WHERE LOWER(full_name) = LOWER(?) LIMIT 1",
                (member_name,),
                fetch_all=True
            )
            if member_row:
                member_id = member_row[0][0] if isinstance(member_row[0], (list, tuple)) else member_row[0].get('prospect_id')
        
        if not member_id:
            # Use name as identifier if no ID found
            member_id = member_name.lower().replace(' ', '_')
        
        # Parse start date
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = datetime.now()
        else:
            start_date = datetime.now()
        
        # Calculate installment amount
        installment_amount = round(total_amount / installments_total, 2)
        
        # Insert the payment plan
        _db_manager.execute_query(
            """
            INSERT INTO payment_plans (member_id, member_name, plan_name, total_amount, 
                                       balance_remaining, installment_amount, installments_total, installments_paid,
                                       frequency_days, start_date, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (member_id, member_name, f"Payment Plan - {member_name}", total_amount,
             total_amount, installment_amount, installments_total, 0, frequency_days,
             start_date.strftime('%Y-%m-%d'), 'active', notes, datetime.now().isoformat())
        )
        
        # Get the inserted plan ID
        plan_rows = _db_manager.execute_query(
            "SELECT id FROM payment_plans WHERE member_id = ? ORDER BY id DESC LIMIT 1",
            (member_id,),
            fetch_all=True
        )
        plan_id = plan_rows[0][0] if plan_rows and isinstance(plan_rows[0], (list, tuple)) else (plan_rows[0].get('id') if plan_rows else None)
        
        if plan_id:
            # Create installment records
            for i in range(installments_total):
                due_date = start_date + timedelta(days=i * frequency_days)
                _db_manager.execute_query(
                    """
                    INSERT INTO payment_plan_installments (plan_id, installment_number, amount, due_date, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (plan_id, i + 1, installment_amount, due_date.strftime('%Y-%m-%d'), 'pending')
                )
        
        # Mark member as exempt from auto-lock
        _db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 1 WHERE prospect_id = ? OR guid = ? OR LOWER(full_name) = LOWER(?)",
            (member_id, member_id, member_name)
        )
        
        logger.info(f"Created payment plan for {member_name}: ${total_amount} in {installments_total} payments")
        
        return jsonify({
            "success": True,
            "plan_id": plan_id,
            "member_name": member_name,
            "message": f"Payment plan created for {member_name}"
        })
    except Exception as e:
        logger.error(f"Error creating payment plan: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/payment-plans/<member_id>/payments', methods=['POST'])
def api_record_payment(member_id):
    """Record a payment for a payment plan installment."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        from datetime import datetime
        
        data = request.get_json() or {}
        installment_id = int(data.get('installment_id', 0))
        amount_paid = float(data.get('amount_paid', 0))
        paid_date_str = data.get('paid_date')
        
        if not installment_id:
            return jsonify({"success": False, "error": "Installment ID is required"}), 400
        if amount_paid <= 0:
            return jsonify({"success": False, "error": "Payment amount must be greater than zero"}), 400
        
        if paid_date_str:
            try:
                paid_date = datetime.strptime(paid_date_str, '%Y-%m-%d')
            except ValueError:
                paid_date = datetime.now()
        else:
            paid_date = datetime.now()
        
        # Update the installment
        _db_manager.execute_query(
            """
            UPDATE payment_plan_installments 
            SET status = 'paid', amount_paid = ?, paid_date = ?
            WHERE id = ?
            """,
            (amount_paid, paid_date.strftime('%Y-%m-%d'), installment_id)
        )
        
        # Get the payment plan for this installment
        plan_rows = _db_manager.execute_query(
            """
            SELECT ppi.plan_id, pp.total_amount, pp.installments_total
            FROM payment_plan_installments ppi
            JOIN payment_plans pp ON pp.id = ppi.plan_id
            WHERE ppi.id = ?
            """,
            (installment_id,),
            fetch_all=True
        )
        
        if plan_rows:
            plan_id = plan_rows[0][0] if isinstance(plan_rows[0], (list, tuple)) else plan_rows[0].get('plan_id')
            
            # Count paid installments and total paid
            paid_stats = _db_manager.execute_query(
                """
                SELECT COUNT(*), COALESCE(SUM(amount_paid), 0)
                FROM payment_plan_installments
                WHERE plan_id = ? AND status = 'paid'
                """,
                (plan_id,),
                fetch_all=True
            )
            
            if paid_stats:
                installments_paid = paid_stats[0][0] if isinstance(paid_stats[0], (list, tuple)) else paid_stats[0].get('COUNT(*)', 0)
                total_paid = paid_stats[0][1] if isinstance(paid_stats[0], (list, tuple)) else paid_stats[0].get('COALESCE(SUM(amount_paid), 0)', 0)
                
                total_amount = plan_rows[0][1] if isinstance(plan_rows[0], (list, tuple)) else plan_rows[0].get('total_amount', 0)
                installments_total = plan_rows[0][2] if isinstance(plan_rows[0], (list, tuple)) else plan_rows[0].get('installments_total', 0)
                balance_remaining = max(0, total_amount - total_paid)
                
                # Update payment plan totals
                new_status = 'completed' if installments_paid >= installments_total else 'active'
                _db_manager.execute_query(
                    """
                    UPDATE payment_plans
                    SET installments_paid = ?, balance_remaining = ?, status = ?
                    WHERE id = ?
                    """,
                    (installments_paid, balance_remaining, new_status, plan_id)
                )
                
                # If completed, optionally remove exemption
                if new_status == 'completed':
                    logger.info(f"Payment plan {plan_id} completed! All installments paid.")
        
        logger.info(f"Recorded payment of ${amount_paid} for installment {installment_id}")
        
        return jsonify({
            "success": True,
            "installment_id": installment_id,
            "amount_paid": amount_paid,
            "message": "Payment recorded successfully"
        })
    except Exception as e:
        logger.error(f"Error recording payment: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/payment-plans/<member_id>', methods=['DELETE'])
def api_remove_payment_plan(member_id):
    """Remove a payment plan and clear the member's exemption."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        # Get the plan(s) for this member
        plan_rows = _db_manager.execute_query(
            "SELECT id FROM payment_plans WHERE member_id = ?",
            (member_id,),
            fetch_all=True
        )
        
        for row in (plan_rows or []):
            plan_id = row[0] if isinstance(row, (list, tuple)) else row.get('id')
            # Delete installments first
            _db_manager.execute_query(
                "DELETE FROM payment_plan_installments WHERE payment_plan_id = ?",
                (plan_id,)
            )
        
        # Delete the payment plan(s)
        _db_manager.execute_query(
            "DELETE FROM payment_plans WHERE member_id = ?",
            (member_id,)
        )
        
        # Remove member exemption
        _db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 0 WHERE prospect_id = ? OR guid = ?",
            (member_id, member_id)
        )
        
        logger.info(f"Removed payment plan for member {member_id}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "message": f"Payment plan removed for member {member_id}"
        })
    except Exception as e:
        logger.error(f"Error removing payment plan: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Legacy exemption endpoints (kept for backward compatibility)
@ai_settings_bp.route('/api/ai/payment-plan-exemptions', methods=['GET'])
def api_get_payment_exemptions():
    """Get all members with payment plan exemptions (legacy endpoint)."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        rows = _db_manager.execute_query(
            """
            SELECT prospect_id, full_name, email, mobile_phone, payment_plan_exempt, amount_past_due
            FROM members 
            WHERE payment_plan_exempt = 1
            ORDER BY full_name
            """,
            fetch_all=True
        )
        
        exempt_members = []
        for row in (rows or []):
            exempt_members.append({
                "member_id": row[0] if isinstance(row, (list, tuple)) else row.get('prospect_id'),
                "name": row[1] if isinstance(row, (list, tuple)) else row.get('full_name'),
                "email": row[2] if isinstance(row, (list, tuple)) else row.get('email'),
                "phone": row[3] if isinstance(row, (list, tuple)) else row.get('mobile_phone'),
                "exempt": True,
                "past_due_amount": row[5] if isinstance(row, (list, tuple)) else row.get('amount_past_due')
            })
        
        return jsonify({
            "success": True,
            "exempt_members": exempt_members,
            "count": len(exempt_members)
        })
    except Exception as e:
        logger.error(f"Error getting payment exemptions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/payment-plan-exemptions/<member_id>', methods=['POST'])
def api_add_payment_exemption(member_id):
    """Add payment plan exemption for a member (legacy endpoint)."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        _db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 1 WHERE prospect_id = ? OR guid = ?",
            (member_id, member_id)
        )
        
        logger.info(f"Added payment plan exemption for member {member_id}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "exempt": True,
            "message": f"Payment plan exemption added for member {member_id}"
        })
    except Exception as e:
        logger.error(f"Error adding payment exemption: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/payment-plan-exemptions/<member_id>', methods=['DELETE'])
def api_remove_payment_exemption(member_id):
    """Remove payment plan exemption for a member (legacy endpoint)."""
    try:
        global _db_manager
        if not _db_manager:
            from src.services.database_manager import DatabaseManager
            _db_manager = DatabaseManager()
        
        _db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 0 WHERE prospect_id = ? OR guid = ?",
            (member_id, member_id)
        )
        
        logger.info(f"Removed payment plan exemption for member {member_id}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "exempt": False,
            "message": f"Payment plan exemption removed for member {member_id}"
        })
    except Exception as e:
        logger.error(f"Error removing payment exemption: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/worker/status', methods=['GET'])
def api_get_worker_status():
    """Get background worker status."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
        return jsonify({
            "success": True,
            "running": _workflow_manager.is_running if _workflow_manager else False
        })
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@ai_settings_bp.route('/api/ai/worker/start', methods=['POST'])
def api_start_worker():
    """Start the background workflow worker."""
    try:
        if not _workflow_manager:
            _init_workflow_manager()
        
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


@ai_settings_bp.route('/api/ai/worker/stop', methods=['POST'])
def api_stop_worker():
    """Stop the background workflow worker."""
    try:
        if not _workflow_manager:
            return jsonify({"success": True, "running": False})
        
        _workflow_manager.stop_background_worker()
        
        return jsonify({
            "success": True,
            "message": "Background worker stopped",
            "running": False
        })
    except Exception as e:
        logger.error(f"Error stopping background worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def _init_workflow_manager():
    """Lazy initialization of workflow manager"""
    global _workflow_manager, _knowledge_base, _db_manager
    try:
        from src.services.ai.knowledge_base import AIKnowledgeBase
        from src.services.ai.unified_workflow_manager import UnifiedWorkflowManager
        from src.services.database_manager import DatabaseManager
        
        if not _db_manager:
            _db_manager = DatabaseManager()
        
        if not _knowledge_base:
            _knowledge_base = AIKnowledgeBase(_db_manager)
        
        if not _workflow_manager:
            _workflow_manager = UnifiedWorkflowManager(_db_manager, _knowledge_base)
        
        logger.info("✅ AI modules lazy-initialized")
    except Exception as e:
        logger.error(f"Failed to initialize AI modules: {e}")


def _init_knowledge_base():
    """Lazy initialization of knowledge base"""
    global _knowledge_base, _db_manager
    try:
        from src.services.ai.knowledge_base import AIKnowledgeBase
        from src.services.database_manager import DatabaseManager
        
        if not _db_manager:
            _db_manager = DatabaseManager()
        
        if not _knowledge_base:
            _knowledge_base = AIKnowledgeBase(_db_manager)
        
        logger.info("✅ Knowledge base lazy-initialized")
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}")
