#!/usr/bin/env python3
"""
Test Individual Autonomous Workflows
Test each workflow manually before scheduling them
"""

import os
import sys
from dotenv import load_dotenv

# Load environment FIRST
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.ai.workflow_runner import WorkflowRunner
from src.services.ai.workflow_scheduler import WorkflowScheduler
from src.services.ai.agent_config import AgentConfig
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_header(title):
    """Print a nice header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_workflow_runner_init():
    """Test that workflow runner initializes correctly"""
    print_header("TEST 1: Workflow Runner Initialization")
    
    try:
        runner = WorkflowRunner()
        print("✅ WorkflowRunner initialized")
        print(f"   Agent ready: {runner.agent.client is not None}")
        print(f"   Config loaded: {runner.config is not None}")
        print(f"   Execution history: {len(runner.execution_history)} items")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize WorkflowRunner: {e}")
        return False


def test_workflow_scheduler_init():
    """Test that workflow scheduler initializes correctly"""
    print_header("TEST 2: Workflow Scheduler Initialization")
    
    try:
        scheduler = WorkflowScheduler()
        print("✅ WorkflowScheduler initialized")
        print(f"   Scheduler created: {scheduler.scheduler is not None}")
        print(f"   Runner ready: {scheduler.runner is not None}")
        
        scheduler.setup_all_schedules()
        jobs = scheduler.get_scheduled_jobs()
        print(f"   Scheduled jobs: {len(jobs)}")
        
        for job in jobs:
            print(f"      • {job['name']}")
            print(f"        Next run: {job['next_run_time']}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize scheduler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_workflow():
    """Test running a single workflow manually"""
    print_header("TEST 3: Manual Workflow Execution")
    
    print("Available workflows:")
    print("1. Daily Campaigns")
    print("2. Past Due Monitoring")
    print("3. Daily Escalation")
    print("4. Referral Checks")
    print("5. Monthly Invoice Review")
    print("6. Door Access Management")
    print("0. Skip test")
    
    choice = input("\nSelect workflow to test (0-6): ").strip()
    
    if choice == '0':
        print("⏭️  Skipped workflow test")
        return True
    
    runner = WorkflowRunner()
    
    workflows = {
        '1': ('Daily Campaigns', runner.run_daily_campaigns_workflow),
        '2': ('Past Due Monitoring', runner.run_past_due_monitoring_workflow),
        '3': ('Daily Escalation', runner.run_daily_escalation_workflow),
        '4': ('Referral Checks', runner.run_referral_checks_workflow),
        '5': ('Monthly Invoice Review', runner.run_monthly_invoice_review_workflow),
        '6': ('Door Access Management', runner.run_door_access_management_workflow)
    }
    
    if choice not in workflows:
        print("❌ Invalid choice")
        return False
    
    workflow_name, workflow_func = workflows[choice]
    
    print(f"\n🚀 Executing workflow: {workflow_name}")
    print("⚠️  This will make actual API calls to Claude and may take 30-60 seconds...")
    
    confirm = input("\nContinue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("⏭️  Cancelled")
        return True
    
    print("\n" + "-" * 70)
    result = workflow_func()
    print("-" * 70)
    
    print(f"\n📊 WORKFLOW RESULT:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Duration: {result.get('duration_seconds', 0):.2f}s")
    
    if result.get('success'):
        print(f"   Tool calls: {result.get('tool_calls', 0)}")
        print(f"   Iterations: {result.get('iterations', 0)}")
        print(f"\n   Agent Result:")
        print(f"   {result.get('agent_result', 'No result')[:500]}...")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    return result.get('success', False)


def view_config():
    """View current workflow configuration"""
    print_header("WORKFLOW CONFIGURATION")
    
    print("📋 Schedule Settings:")
    print(f"   Daily Campaigns: {'✅ Enabled' if AgentConfig.DAILY_CAMPAIGNS_ENABLED else '❌ Disabled'}")
    print(f"      Schedule: {AgentConfig.DAILY_CAMPAIGNS_HOUR}:{AgentConfig.DAILY_CAMPAIGNS_MINUTE:02d} daily")
    
    print(f"\n   Past Due Monitoring: {'✅ Enabled' if AgentConfig.PAST_DUE_MONITORING_ENABLED else '❌ Disabled'}")
    print(f"      Schedule: Every {AgentConfig.PAST_DUE_CHECK_INTERVAL_MINUTES} minutes")
    
    print(f"\n   Daily Escalation: {'✅ Enabled' if AgentConfig.DAILY_ESCALATION_ENABLED else '❌ Disabled'}")
    print(f"      Schedule: {AgentConfig.DAILY_ESCALATION_HOUR}:{AgentConfig.DAILY_ESCALATION_MINUTE:02d} daily")
    
    print(f"\n   Referral Checks: {'✅ Enabled' if AgentConfig.REFERRAL_CHECKS_ENABLED else '❌ Disabled'}")
    print(f"      Schedule: Every {AgentConfig.REFERRAL_CHECK_WEEK_INTERVAL} weeks, {AgentConfig.REFERRAL_CHECK_DAY} at {AgentConfig.REFERRAL_CHECK_HOUR}:{AgentConfig.REFERRAL_CHECK_MINUTE:02d}")
    
    print(f"\n   Monthly Invoice Review: {'✅ Enabled' if AgentConfig.MONTHLY_INVOICE_REVIEW_ENABLED else '❌ Disabled'}")
    print(f"      Schedule: Day {AgentConfig.INVOICE_REVIEW_DAY} of month at {AgentConfig.INVOICE_REVIEW_HOUR}:{AgentConfig.INVOICE_REVIEW_MINUTE:02d}")
    
    print(f"\n   Door Access Management: {'✅ Enabled' if AgentConfig.DOOR_ACCESS_MANAGEMENT_ENABLED else '❌ Disabled'}")
    print(f"      Schedule: Every {AgentConfig.DOOR_ACCESS_CHECK_INTERVAL_MINUTES} minutes")
    
    print("\n📋 Behavior Settings:")
    print(f"   Past Due Warning Threshold: {AgentConfig.PAST_DUE_WARNING_DAYS} days")
    print(f"   Past Due Urgent Threshold: {AgentConfig.PAST_DUE_URGENT_DAYS} days")
    print(f"   Collections Escalation: {AgentConfig.PAST_DUE_ESCALATION_DAYS} days")
    print(f"   Auto-Lock Past Due: {AgentConfig.AUTO_LOCK_PAST_DUE_DAYS} days")
    print(f"   Max Campaign Recipients: {AgentConfig.MAX_CAMPAIGN_RECIPIENTS}")
    
    print("\n📋 Safety Settings:")
    print(f"   Dry Run Mode: {'✅ ON' if AgentConfig.DRY_RUN_MODE else '❌ OFF'}")
    print(f"   Require Confirmation (Bulk): {'✅ ON' if AgentConfig.REQUIRE_CONFIRMATION_FOR_BULK_ACTIONS else '❌ OFF'}")
    print(f"   Require Confirmation (Door): {'✅ ON' if AgentConfig.REQUIRE_CONFIRMATION_FOR_DOOR_LOCK else '❌ OFF'}")
    print(f"   Require Confirmation (Collections): {'✅ ON' if AgentConfig.REQUIRE_CONFIRMATION_FOR_COLLECTIONS_REFERRAL else '❌ OFF'}")


def main():
    """Main test menu"""
    print("\n🤖 ANYTIME FITNESS BOT - AUTONOMOUS WORKFLOW TESTING")
    
    while True:
        print("\n" + "=" * 70)
        print("MENU:")
        print("  1. Test WorkflowRunner initialization")
        print("  2. Test WorkflowScheduler initialization")
        print("  3. Run single workflow manually")
        print("  4. View configuration")
        print("  0. Exit")
        print("=" * 70)
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == '1':
            test_workflow_runner_init()
        elif choice == '2':
            test_workflow_scheduler_init()
        elif choice == '3':
            test_single_workflow()
        elif choice == '4':
            view_config()
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
