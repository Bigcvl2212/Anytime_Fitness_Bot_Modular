"""
Workflow Scheduler
Sets up APScheduler to run autonomous workflows on configured schedules

Schedules:
1. Daily Campaigns - 6 AM daily
2. Past Due Monitoring - Every hour
3. Daily Escalation - 8 AM daily
4. Referral Checks - Bi-weekly (every other Monday at 9 AM)
5. Monthly Invoice Review - 1st of month at 10 AM
6. Door Access Management - Every hour
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .workflow_runner import WorkflowRunner
from .agent_config import AgentConfig

logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """Manages scheduled execution of autonomous workflows"""
    
    def __init__(self):
        """Initialize the workflow scheduler"""
        self.scheduler = BackgroundScheduler()
        self.runner = WorkflowRunner()
        self.config = AgentConfig
        
        logger.info("✅ Workflow Scheduler initialized")
    
    def setup_all_schedules(self):
        """Set up all workflow schedules based on config"""
        logger.info("🔧 Setting up workflow schedules...")
        
        # 1. Daily Campaigns (6 AM daily)
        if self.config.DAILY_CAMPAIGNS_ENABLED:
            self.scheduler.add_job(
                func=self.runner.run_daily_campaigns_workflow,
                trigger=CronTrigger(
                    hour=self.config.DAILY_CAMPAIGNS_HOUR,
                    minute=self.config.DAILY_CAMPAIGNS_MINUTE
                ),
                id='daily_campaigns',
                name='Daily Campaigns Workflow',
                replace_existing=True
            )
            logger.info(f"   ✅ Daily Campaigns: Every day at {self.config.DAILY_CAMPAIGNS_HOUR}:{self.config.DAILY_CAMPAIGNS_MINUTE:02d}")
        
        # 2. Hourly Past Due Monitoring
        if self.config.PAST_DUE_MONITORING_ENABLED:
            self.scheduler.add_job(
                func=self.runner.run_past_due_monitoring_workflow,
                trigger=IntervalTrigger(
                    minutes=self.config.PAST_DUE_CHECK_INTERVAL_MINUTES
                ),
                id='past_due_monitoring',
                name='Past Due Monitoring Workflow',
                replace_existing=True
            )
            logger.info(f"   ✅ Past Due Monitoring: Every {self.config.PAST_DUE_CHECK_INTERVAL_MINUTES} minutes")
        
        # 3. Daily Escalation (8 AM daily)
        if self.config.DAILY_ESCALATION_ENABLED:
            self.scheduler.add_job(
                func=self.runner.run_daily_escalation_workflow,
                trigger=CronTrigger(
                    hour=self.config.DAILY_ESCALATION_HOUR,
                    minute=self.config.DAILY_ESCALATION_MINUTE
                ),
                id='daily_escalation',
                name='Daily Escalation Workflow',
                replace_existing=True
            )
            logger.info(f"   ✅ Daily Escalation: Every day at {self.config.DAILY_ESCALATION_HOUR}:{self.config.DAILY_ESCALATION_MINUTE:02d}")
        
        # 4. Bi-weekly Referral Checks (every other Monday at 9 AM)
        if self.config.REFERRAL_CHECKS_ENABLED:
            self.scheduler.add_job(
                func=self.runner.run_referral_checks_workflow,
                trigger=CronTrigger(
                    day_of_week=self.config.REFERRAL_CHECK_DAY,
                    hour=self.config.REFERRAL_CHECK_HOUR,
                    minute=self.config.REFERRAL_CHECK_MINUTE,
                    week=f'*/{self.config.REFERRAL_CHECK_WEEK_INTERVAL}'  # Every 2 weeks
                ),
                id='referral_checks',
                name='Referral Checks Workflow',
                replace_existing=True
            )
            logger.info(f"   ✅ Referral Checks: Every {self.config.REFERRAL_CHECK_WEEK_INTERVAL} weeks on {self.config.REFERRAL_CHECK_DAY} at {self.config.REFERRAL_CHECK_HOUR}:{self.config.REFERRAL_CHECK_MINUTE:02d}")
        
        # 5. Monthly Invoice Review (1st of month at 10 AM)
        if self.config.MONTHLY_INVOICE_REVIEW_ENABLED:
            self.scheduler.add_job(
                func=self.runner.run_monthly_invoice_review_workflow,
                trigger=CronTrigger(
                    day=self.config.INVOICE_REVIEW_DAY,
                    hour=self.config.INVOICE_REVIEW_HOUR,
                    minute=self.config.INVOICE_REVIEW_MINUTE
                ),
                id='monthly_invoice_review',
                name='Monthly Invoice Review Workflow',
                replace_existing=True
            )
            logger.info(f"   ✅ Monthly Invoice Review: Day {self.config.INVOICE_REVIEW_DAY} of month at {self.config.INVOICE_REVIEW_HOUR}:{self.config.INVOICE_REVIEW_MINUTE:02d}")
        
        # 6. Hourly Door Access Management
        if self.config.DOOR_ACCESS_MANAGEMENT_ENABLED:
            self.scheduler.add_job(
                func=self.runner.run_door_access_management_workflow,
                trigger=IntervalTrigger(
                    minutes=self.config.DOOR_ACCESS_CHECK_INTERVAL_MINUTES
                ),
                id='door_access_management',
                name='Door Access Management Workflow',
                replace_existing=True
            )
            logger.info(f"   ✅ Door Access Management: Every {self.config.DOOR_ACCESS_CHECK_INTERVAL_MINUTES} minutes")
        
        logger.info("✅ All workflow schedules configured")
    
    def start(self):
        """Start the scheduler"""
        try:
            # Setup all workflow schedules before starting
            self.setup_all_schedules()
            
            # Start the scheduler
            self.scheduler.start()
            logger.info("🚀 Workflow Scheduler STARTED")
            logger.info(f"   Scheduled jobs: {len(self.scheduler.get_jobs())}")
            
            # Print next run times
            self._print_next_run_times()
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("🛑 Workflow Scheduler STOPPED")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
    
    def pause_workflow(self, workflow_id: str):
        """Pause a specific workflow"""
        try:
            self.scheduler.pause_job(workflow_id)
            logger.info(f"⏸️  Paused workflow: {workflow_id}")
        except Exception as e:
            logger.error(f"❌ Failed to pause workflow {workflow_id}: {e}")
    
    def resume_workflow(self, workflow_id: str):
        """Resume a paused workflow"""
        try:
            self.scheduler.resume_job(workflow_id)
            logger.info(f"▶️  Resumed workflow: {workflow_id}")
        except Exception as e:
            logger.error(f"❌ Failed to resume workflow {workflow_id}: {e}")
    
    def run_workflow_now(self, workflow_name: str):
        """Manually trigger a workflow to run immediately"""
        logger.info(f"🔥 Manually triggering workflow: {workflow_name}")
        
        # Built-in scheduled workflows
        workflow_methods = {
            'daily_campaigns': self.runner.run_daily_campaigns_workflow,
            'past_due_monitoring': self.runner.run_past_due_monitoring_workflow,
            'daily_escalation': self.runner.run_daily_escalation_workflow,
            'referral_checks': self.runner.run_referral_checks_workflow,
            'monthly_invoice_review': self.runner.run_monthly_invoice_review_workflow,
            'door_access_management': self.runner.run_door_access_management_workflow
        }
        
        if workflow_name in workflow_methods:
            result = workflow_methods[workflow_name]()
            logger.info(f"   Result: {result.get('success', False)}")
            return result
        
        # Check UnifiedWorkflowManager for additional workflows
        try:
            from .unified_workflow_manager import get_workflow_manager
            unified_manager = get_workflow_manager()
            if unified_manager and workflow_name in unified_manager._workflows:
                logger.info(f"   Running via UnifiedWorkflowManager: {workflow_name}")
                result = unified_manager.run_workflow(workflow_name, force=True)
                return result
        except ImportError:
            logger.warning("UnifiedWorkflowManager not available")
        except Exception as e:
            logger.error(f"Error running unified workflow: {e}")
            return {"success": False, "error": str(e)}
        
        logger.error(f"❌ Unknown workflow: {workflow_name}")
        return {"success": False, "error": f"Unknown workflow: {workflow_name}"}
    
    def get_scheduled_jobs(self):
        """Get list of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            # Safely access next_run_time (may be None before scheduler starts)
            try:
                # APScheduler Job objects may not have next_run_time until scheduler starts
                # Use get_next_run_time() method instead
                next_run_obj = job.next_run_time if hasattr(job, 'next_run_time') else None
                next_run = next_run_obj.isoformat() if next_run_obj else "Pending (start scheduler)"
            except (AttributeError, TypeError):
                next_run = "Pending (start scheduler)"
            
            jobs.append({
                'id': job.id,
                'name': job.name if hasattr(job, 'name') else job.id,
                'next_run_time': next_run,
                'trigger': str(job.trigger) if hasattr(job, 'trigger') else "Unknown"
            })
        return jobs
    
    def _print_next_run_times(self):
        """Print next run times for all scheduled workflows"""
        logger.info("\n📅 Next Scheduled Runs:")
        for job in self.scheduler.get_jobs():
            try:
                if job.next_run_time:
                    logger.info(f"   • {job.name}: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.info(f"   • {job.name}: Not scheduled")
            except AttributeError:
                logger.info(f"   • {job.name}: Schedule pending (start scheduler)")
    
    def get_workflow_stats(self):
        """Get execution statistics from the runner"""
        return self.runner.get_workflow_stats()
    
    def get_execution_history(self, workflow_name: str = None):
        """Get execution history from the runner"""
        return self.runner.get_execution_history(workflow_name)


# ============================================
# STANDALONE SCHEDULER RUNNER
# ============================================

def start_scheduler():
    """
    Start the autonomous workflow scheduler
    This keeps the scheduler running in the foreground
    """
    import signal
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("=" * 60)
    logger.info("ANYTIME FITNESS BOT - AUTONOMOUS WORKFLOW SCHEDULER")
    logger.info("=" * 60)
    
    # Create and start scheduler
    scheduler = WorkflowScheduler()
    scheduler.setup_all_schedules()
    scheduler.start()
    
    # Set up graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n🛑 Shutdown signal received...")
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("\n✅ Scheduler is running. Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    # Keep running
    try:
        import time
        while True:
            time.sleep(60)  # Sleep 60 seconds between checks
    except KeyboardInterrupt:
        logger.info("\n🛑 Keyboard interrupt received...")
        scheduler.stop()


if __name__ == "__main__":
    start_scheduler()
