"""
Workflow Runner
Implements the 6 autonomous AI workflows that run on schedules

Each workflow uses the AI agent to intelligently chain tools together
to complete complex multi-step tasks without human intervention.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import traceback

from .agent_core import GymAgentCore
from .agent_config import AgentConfig

logger = logging.getLogger(__name__)


class WorkflowRunner:
    """Executes autonomous AI workflows"""
    
    def __init__(self):
        """Initialize workflow runner"""
        self.agent = GymAgentCore()
        self.config = AgentConfig
        self.execution_history = []
        
        logger.info("✅ Workflow Runner initialized")
    
    # ============================================
    # WORKFLOW 1: Daily Campaigns (6 AM Daily)
    # ============================================
    
    def run_daily_campaigns_workflow(self) -> Dict[str, Any]:
        """
        Send targeted marketing campaigns to prospects, green members, and PPV members
        
        Agent Task:
        1. Get counts of prospects, green members, PPV members
        2. Select appropriate campaign templates for each group
        3. Send bulk campaigns to each group
        4. Report results (sent counts, delivery status)
        
        Returns:
            Workflow execution result with success/failure, metrics
        """
        workflow_name = "daily_campaigns"
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        if not self.config.DAILY_CAMPAIGNS_ENABLED:
            return self._skip_workflow(workflow_name, "Workflow disabled in config")
        
        # Build the task for the AI agent
        task = f"""
        Execute the daily marketing campaigns workflow:
        
        1. Check how many active prospects we have (use get_campaign_prospects tool)
        2. Check how many green members we have (use get_green_members tool)
        3. Check how many PPV members we have (use get_ppv_members tool)
        4. Get available campaign templates (use get_campaign_templates tool)
        5. Send appropriate campaigns to each group (use send_bulk_campaign tool)
        
        Rules:
        - Only send campaigns if there are recipients (count > 0)
        - Select templates appropriate for each audience type
        - Don't send to same group within {self.config.CAMPAIGN_COOLDOWN_DAYS} days
        - Maximum {self.config.MAX_CAMPAIGN_RECIPIENTS} recipients per batch
        
        Provide a summary of:
        - How many recipients in each group
        - Which campaigns were sent
        - Delivery success/failure counts
        """
        
        return self._execute_workflow(workflow_name, task)
    
    # ============================================
    # WORKFLOW 2: Hourly Past Due Monitoring
    # ============================================
    
    def run_past_due_monitoring_workflow(self) -> Dict[str, Any]:
        """
        Monitor past due accounts and send payment reminders
        
        Agent Task:
        1. Get list of past due members (7+ days)
        2. Categorize by urgency (7-30 days warning, 30-60 days urgent)
        3. Send appropriate payment reminders
        4. Track which members were contacted
        
        Returns:
            Workflow execution result
        """
        workflow_name = "past_due_monitoring"
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        if not self.config.PAST_DUE_MONITORING_ENABLED:
            return self._skip_workflow(workflow_name, "Workflow disabled in config")
        
        task = f"""
        Execute the past due monitoring workflow:
        
        1. Get all past due members (use get_past_due_members tool)
        2. Get all past due training clients (use get_past_due_training_clients tool)
        3. Categorize members by urgency:
           - Warning: {self.config.PAST_DUE_WARNING_DAYS}+ days past due
           - Urgent: {self.config.PAST_DUE_URGENT_DAYS}+ days past due
        4. Send payment reminders to appropriate members (use send_payment_reminder tool)
        5. Log collection attempts (use get_collection_attempts to check recent attempts)
        
        Rules:
        - Don't send reminder if already contacted within 7 days
        - Use different message urgency based on days past due
        - Skip members under ${self.config.MIN_PAST_DUE_AMOUNT}
        
        Provide a summary of:
        - Total past due members and training clients
        - How many reminders sent (warning vs urgent)
        - Total amount past due
        """
        
        return self._execute_workflow(workflow_name, task)
    
    # ============================================
    # WORKFLOW 3: Daily Escalation (8 AM Daily)
    # ============================================
    
    def run_daily_escalation_workflow(self) -> Dict[str, Any]:
        """
        Escalate severely past due accounts (60+ days) to collections
        
        Agent Task:
        1. Get members 60+ days past due
        2. Generate collections referral list
        3. Report escalation candidates
        
        Returns:
            Workflow execution result
        """
        workflow_name = "daily_escalation"
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        if not self.config.DAILY_ESCALATION_ENABLED:
            return self._skip_workflow(workflow_name, "Workflow disabled in config")
        
        task = f"""
        Execute the daily escalation workflow:
        
        1. Get all past due members (use get_past_due_members tool)
        2. Filter for members {self.config.PAST_DUE_ESCALATION_DAYS}+ days past due
        3. Generate collections referral list (use generate_collections_referral_list tool)
        
        Rules:
        - Only escalate if past due >= {self.config.PAST_DUE_ESCALATION_DAYS} days
        - Only escalate if amount >= ${self.config.MIN_PAST_DUE_AMOUNT}
        - Check collection attempts to avoid duplicate referrals
        
        Important: This is a HIGH RISK operation. In production, this should require
        human confirmation before actually sending to collections. For now, just
        GENERATE the list and report who would be referred.
        
        Provide a summary of:
        - How many accounts qualify for escalation
        - Total amount being referred to collections
        - List of members (names and amounts)
        """
        
        return self._execute_workflow(workflow_name, task)
    
    # ============================================
    # WORKFLOW 4: Bi-weekly Referral Checks
    # ============================================
    
    def run_referral_checks_workflow(self) -> Dict[str, Any]:
        """
        Check for members with referral credits and send thank you messages
        
        Agent Task:
        1. Query members with referral credits
        2. Send thank you messages
        3. Track referral engagement
        
        Returns:
            Workflow execution result
        """
        workflow_name = "referral_checks"
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        if not self.config.REFERRAL_CHECKS_ENABLED:
            return self._skip_workflow(workflow_name, "Workflow disabled in config")
        
        task = """
        Execute the bi-weekly referral checks workflow:
        
        1. Get member profiles to identify those with referral credits
           (use get_member_profile tool for sample members)
        2. For members with referral activity, send thank you messages
           (use send_message_to_member tool)
        3. Add notes to member profiles about referral engagement
           (use add_member_note tool)
        
        Rules:
        - Only message members who have made successful referrals
        - Don't message same member within 14 days
        - Keep messages personalized and appreciative
        
        Provide a summary of:
        - How many members have active referral credits
        - How many thank you messages sent
        - Top referrers (if identifiable)
        """
        
        return self._execute_workflow(workflow_name, task)
    
    # ============================================
    # WORKFLOW 5: Monthly Invoice Review
    # ============================================
    
    def run_monthly_invoice_review_workflow(self) -> Dict[str, Any]:
        """
        Review unpaid training package invoices and send reminders
        
        Agent Task:
        1. Get past due training clients
        2. Send payment reminders for unpaid packages
        3. Report outstanding invoices
        
        Returns:
            Workflow execution result
        """
        workflow_name = "monthly_invoice_review"
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        if not self.config.MONTHLY_INVOICE_REVIEW_ENABLED:
            return self._skip_workflow(workflow_name, "Workflow disabled in config")
        
        task = """
        Execute the monthly invoice review workflow:
        
        1. Get all past due training clients (use get_past_due_training_clients tool)
        2. For each past due client, send payment reminder (use send_payment_reminder tool)
        3. Track collection attempts (use get_collection_attempts tool)
        
        Rules:
        - Focus on training package invoices (PT, small group training)
        - Send polite reminders for invoices 7+ days overdue
        - Escalate invoices 30+ days overdue with urgent tone
        
        Provide a summary of:
        - Total training clients past due
        - Total amount outstanding in training invoices
        - How many reminders sent
        """
        
        return self._execute_workflow(workflow_name, task)
    
    # ============================================
    # WORKFLOW 6: Hourly Door Access Management
    # ============================================
    
    def run_door_access_management_workflow(self) -> Dict[str, Any]:
        """
        Automatically manage door access based on payment status
        
        Agent Task:
        1. Check members with past due accounts
        2. Lock doors for members 14+ days past due
        3. Unlock doors when payment received
        4. Report access changes
        
        Returns:
            Workflow execution result
        """
        workflow_name = "door_access_management"
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        if not self.config.DOOR_ACCESS_MANAGEMENT_ENABLED:
            return self._skip_workflow(workflow_name, "Workflow disabled in config")
        
        task = f"""
        Execute the hourly door access management workflow:
        
        1. Get past due members (use get_past_due_members tool)
        2. For members {self.config.AUTO_LOCK_PAST_DUE_DAYS}+ days past due:
           - Check current access status (use check_member_access_status tool)
           - If unlocked, lock door access (use lock_door_for_member tool)
        3. Optionally: Use auto_manage_access_by_payment_status tool to handle both
           locking past due accounts AND unlocking paid accounts
        
        Rules:
        - Only lock after {self.config.AUTO_LOCK_PAST_DUE_DAYS}+ days past due
        - Unlock immediately when payment received (if AUTO_UNLOCK_ON_PAYMENT=True)
        - Add note to member profile when access changed
        
        Important: This is a HIGH RISK operation. In production, require confirmation
        before actually locking doors. For now, just REPORT who would be locked/unlocked.
        
        Provide a summary of:
        - How many members need door access changes
        - How many doors locked vs unlocked
        - Any errors or issues
        """
        
        return self._execute_workflow(workflow_name, task)
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _execute_workflow(self, workflow_name: str, task: str) -> Dict[str, Any]:
        """
        Execute a workflow task using the AI agent
        
        Args:
            workflow_name: Name of workflow for logging
            task: Task description for the AI agent
            
        Returns:
            Workflow result with success status, metrics, errors
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"📋 Workflow '{workflow_name}' - Sending task to AI agent...")
            
            # Execute autonomous task
            result = self.agent.execute_task(
                task,
                max_iterations=self.config.MAX_AGENT_ITERATIONS
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Build workflow result
            workflow_result = {
                "workflow_name": workflow_name,
                "success": result.get("success", False),
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration,
                "agent_result": result.get("result", "No result"),
                "tool_calls": len(result.get("tool_calls", [])),
                "iterations": result.get("iterations", 0),
                "error": result.get("error")
            }
            
            # Log execution
            if result.get("success"):
                logger.info(f"✅ Workflow '{workflow_name}' completed successfully in {duration:.2f}s")
                logger.info(f"   Result: {result.get('result', '')[:200]}...")
            else:
                logger.error(f"❌ Workflow '{workflow_name}' failed: {result.get('error')}")
            
            # Store in history
            self._store_execution_result(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_result = {
                "workflow_name": workflow_name,
                "success": False,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            logger.error(f"❌ Workflow '{workflow_name}' crashed: {e}")
            logger.error(traceback.format_exc())
            
            self._store_execution_result(error_result)
            
            return error_result
    
    def _skip_workflow(self, workflow_name: str, reason: str) -> Dict[str, Any]:
        """Skip a workflow (disabled or conditions not met)"""
        logger.info(f"⏭️  Skipping workflow '{workflow_name}': {reason}")
        
        result = {
            "workflow_name": workflow_name,
            "success": True,
            "skipped": True,
            "reason": reason,
            "completed_at": datetime.now().isoformat()
        }
        
        self._store_execution_result(result)
        return result
    
    def _store_execution_result(self, result: Dict[str, Any]):
        """Store workflow execution result for monitoring"""
        self.execution_history.append(result)
        
        # Keep only last 100 executions in memory
        if len(self.execution_history) > 100:
            self.execution_history.pop(0)
        
        # TODO: Store in database if STORE_EXECUTION_HISTORY enabled
        if self.config.STORE_EXECUTION_HISTORY:
            try:
                # Would store to database here
                pass
            except Exception as e:
                logger.error(f"Failed to store execution result: {e}")
    
    def get_execution_history(self, workflow_name: Optional[str] = None) -> list:
        """Get execution history, optionally filtered by workflow name"""
        if workflow_name:
            return [r for r in self.execution_history if r.get('workflow_name') == workflow_name]
        return self.execution_history
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get statistics about workflow executions"""
        total_executions = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.get('success') and not r.get('skipped'))
        failed = sum(1 for r in self.execution_history if not r.get('success') and not r.get('skipped'))
        skipped = sum(1 for r in self.execution_history if r.get('skipped'))
        
        avg_duration = 0
        if self.execution_history:
            durations = [r.get('duration_seconds', 0) for r in self.execution_history if 'duration_seconds' in r]
            avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "average_duration_seconds": avg_duration
        }
