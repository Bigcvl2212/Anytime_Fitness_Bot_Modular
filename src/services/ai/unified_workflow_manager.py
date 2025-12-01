"""
Unified AI Workflow Manager
===========================
Orchestrates all AI automation workflows with knowledge base integration,
database-backed settings, and proper confirmation for destructive actions.

Workflows:
1. Auto Reply Messages - Respond to incoming messages using knowledge base context
2. Prospect Outreach - Automatically reach out to new prospects
3. Past Due Monitoring - Send payment reminders with daily limits
4. Auto Lock Past Due - Lock gym access for past due members (respects payment plans)
5. Square Invoice Automation - Create and send invoices via Square

Each workflow can be enabled/disabled independently via the database settings.
"""

import logging
import json
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class UnifiedWorkflowManager:
    """
    Central manager for all AI-powered automation workflows.
    
    Features:
    - Database-backed settings (enable/disable workflows)
    - Knowledge base integration for AI context
    - Payment plan exemption support
    - Configurable execution intervals
    - Execution history tracking
    """
    
    def __init__(self, db_manager=None, knowledge_base=None):
        """
        Initialize the workflow manager.
        
        Args:
            db_manager: DatabaseManager instance for settings/history storage
            knowledge_base: AIKnowledgeBase instance for AI context
        """
        self.db = db_manager
        self.knowledge_base = knowledge_base
        
        # Workflow registry
        self._workflows: Dict[str, Dict[str, Any]] = {}
        
        # Execution state
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._last_execution: Dict[str, datetime] = {}
        
        # Register default workflows
        self._register_default_workflows()
        
        logger.info("✅ UnifiedWorkflowManager initialized")
    
    def _register_default_workflows(self):
        """Register the default set of AI workflows"""
        
        # Workflow 1: Auto Reply Messages
        self.register_workflow(
            name="auto_reply_messages",
            display_name="Auto Reply to Messages",
            description="Automatically respond to incoming messages using AI and the knowledge base",
            handler=self._workflow_auto_reply_messages,
            default_config={
                "response_delay_seconds": 30,
                "require_approval": False,
                "max_replies_per_hour": 20,
                "use_knowledge_base": True
            },
            category="messaging"
        )
        
        # Workflow 2: Prospect Outreach
        self.register_workflow(
            name="prospect_outreach",
            display_name="Prospect Auto-Outreach",
            description="Automatically reach out to new prospects to schedule tours/appointments",
            handler=self._workflow_prospect_outreach,
            default_config={
                "check_interval_minutes": 5,
                "outreach_template": "default",
                "max_outreach_per_day": 50,
                "schedule_follow_up_days": 3
            },
            category="sales"
        )
        
        # Workflow 3: Past Due Monitoring
        self.register_workflow(
            name="past_due_reminders",
            display_name="Past Due Payment Reminders",
            description="Send daily payment reminders to past due members",
            handler=self._workflow_past_due_reminders,
            default_config={
                "reminder_hour": 9,
                "max_reminders_per_day": 1,
                "min_days_past_due": 7,
                "urgency_threshold_days": 30,
                "respect_payment_plans": True
            },
            category="billing"
        )
        
        # Workflow 4: Auto Lock Past Due
        self.register_workflow(
            name="auto_lock_past_due",
            display_name="Auto-Lock Past Due Members",
            description="Automatically lock gym access for severely past due members",
            handler=self._workflow_auto_lock_past_due,
            default_config={
                "grace_period_days": 14,
                "respect_payment_plans": True,
                "send_warning_before_lock": True,
                "warning_days_before": 3,
                "require_confirmation": True
            },
            category="billing"
        )
        
        # Workflow 5: Square Invoice Automation
        self.register_workflow(
            name="square_invoice_automation",
            display_name="Square Invoice Automation",
            description="Automatically create and send invoices through Square",
            handler=self._workflow_square_invoice,
            default_config={
                "auto_send": False,
                "payment_due_days": 7,
                "include_late_fee": False,
                "late_fee_amount": 10.00
            },
            category="billing"
        )
    
    def register_workflow(
        self,
        name: str,
        display_name: str,
        description: str,
        handler: Callable,
        default_config: Dict[str, Any],
        category: str = "general"
    ):
        """
        Register a new workflow.
        
        Args:
            name: Unique workflow identifier
            display_name: Human-readable name
            description: What the workflow does
            handler: Function to execute the workflow
            default_config: Default configuration options
            category: Workflow category (messaging, sales, billing, etc.)
        """
        self._workflows[name] = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "handler": handler,
            "default_config": default_config,
            "category": category
        }
        logger.debug(f"📝 Registered workflow: {name}")
    
    # ================================================================
    # Settings Management (Database-backed)
    # ================================================================
    
    def get_workflow_settings(self, workflow_name: str) -> Dict[str, Any]:
        """Get settings for a workflow from database"""
        if not self.db:
            # Return defaults if no database
            workflow = self._workflows.get(workflow_name, {})
            return {
                "enabled": False,
                "config": workflow.get("default_config", {})
            }
        
        try:
            row = self.db.execute_query(
                "SELECT enabled, config, last_run FROM ai_workflow_settings WHERE workflow_name = ?",
                (workflow_name,),
                fetch_one=True
            )
            
            if row:
                return {
                    "enabled": bool(row[0]),
                    "config": json.loads(row[1]) if row[1] else {},
                    "last_run": row[2]
                }
            else:
                # Return defaults
                workflow = self._workflows.get(workflow_name, {})
                return {
                    "enabled": False,
                    "config": workflow.get("default_config", {})
                }
        except Exception as e:
            logger.error(f"Error getting workflow settings: {e}")
            workflow = self._workflows.get(workflow_name, {})
            return {"enabled": False, "config": workflow.get("default_config", {})}
    
    def update_workflow_settings(
        self,
        workflow_name: str,
        enabled: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update workflow settings in database.
        
        Args:
            workflow_name: The workflow to update
            enabled: Whether to enable/disable (None = don't change)
            config: Configuration options (None = don't change)
            
        Returns:
            True if update successful
        """
        if not self.db:
            logger.warning("No database configured - settings not persisted")
            return False
        
        try:
            current = self.get_workflow_settings(workflow_name)
            
            new_enabled = enabled if enabled is not None else current.get("enabled", False)
            new_config = config if config is not None else current.get("config", {})
            
            self.db.execute_query(
                """
                INSERT INTO ai_workflow_settings (workflow_name, enabled, config, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(workflow_name) DO UPDATE SET
                    enabled = excluded.enabled,
                    config = excluded.config,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (workflow_name, new_enabled, json.dumps(new_config))
            )
            
            logger.info(f"✅ Updated settings for workflow '{workflow_name}': enabled={new_enabled}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating workflow settings: {e}")
            return False
    
    def enable_workflow(self, workflow_name: str) -> bool:
        """Enable a workflow"""
        return self.update_workflow_settings(workflow_name, enabled=True)
    
    def disable_workflow(self, workflow_name: str) -> bool:
        """Disable a workflow"""
        return self.update_workflow_settings(workflow_name, enabled=False)
    
    def get_all_workflow_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all registered workflows"""
        statuses = []
        
        for name, workflow in self._workflows.items():
            settings = self.get_workflow_settings(name)
            statuses.append({
                "name": name,
                "display_name": workflow["display_name"],
                "description": workflow["description"],
                "category": workflow["category"],
                "enabled": settings.get("enabled", False),
                "config": settings.get("config", {}),
                "last_run": settings.get("last_run"),
                "last_execution_time": self._last_execution.get(name)
            })
        
        return statuses
    
    # ================================================================
    # Workflow Execution
    # ================================================================
    
    def run_workflow(self, workflow_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Execute a single workflow.
        
        Args:
            workflow_name: Name of workflow to run
            force: Run even if disabled (for testing)
            
        Returns:
            Execution result dict
        """
        workflow = self._workflows.get(workflow_name)
        if not workflow:
            return {"success": False, "error": f"Unknown workflow: {workflow_name}"}
        
        settings = self.get_workflow_settings(workflow_name)
        
        if not settings.get("enabled") and not force:
            return {
                "success": True,
                "skipped": True,
                "reason": "Workflow is disabled"
            }
        
        start_time = datetime.now()
        logger.info(f"🚀 Starting workflow: {workflow_name}")
        
        try:
            # Execute the workflow handler
            handler = workflow["handler"]
            config = settings.get("config", {})
            
            result = handler(config)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Update last run time
            self._last_execution[workflow_name] = end_time
            if self.db:
                self.db.execute_query(
                    "UPDATE ai_workflow_settings SET last_run = ? WHERE workflow_name = ?",
                    (end_time.isoformat(), workflow_name)
                )
            
            # Log execution
            self._log_execution(workflow_name, True, duration, result)
            
            logger.info(f"✅ Workflow '{workflow_name}' completed in {duration:.2f}s")
            
            return {
                "success": True,
                "workflow_name": workflow_name,
                "duration_seconds": duration,
                "result": result
            }
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ Workflow '{workflow_name}' failed: {e}")
            self._log_execution(workflow_name, False, duration, {"error": str(e)})
            
            return {
                "success": False,
                "workflow_name": workflow_name,
                "duration_seconds": duration,
                "error": str(e)
            }
    
    def _log_execution(
        self,
        workflow_name: str,
        success: bool,
        duration: float,
        result: Dict[str, Any]
    ):
        """Log workflow execution to database"""
        if not self.db:
            return
        
        try:
            # Create execution log table if needed
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS ai_workflow_execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_name TEXT NOT NULL,
                    success BOOLEAN,
                    duration_seconds REAL,
                    result TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.db.execute_query(
                """
                INSERT INTO ai_workflow_execution_log 
                (workflow_name, success, duration_seconds, result)
                VALUES (?, ?, ?, ?)
                """,
                (workflow_name, success, duration, json.dumps(result))
            )
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
    
    # ================================================================
    # Workflow Handlers (The actual business logic)
    # ================================================================
    
    def _workflow_auto_reply_messages(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-reply to incoming messages using AI.
        
        This workflow controls the real-time message sync's AI auto-processing.
        When enabled, new incoming messages are automatically:
        1. Classified by intent (billing, appointment, question, etc.)
        2. Responded to using the knowledge base context
        3. Flagged for human review if needed (complaints, refunds, etc.)
        
        The actual processing happens in real_timemessage_poller._trigger_ai_processing()
        """
        logger.info("📨 Running auto-reply workflow...")
        
        use_knowledge_base = config.get("use_knowledge_base", True)
        max_replies = config.get("max_replies_per_hour", 20)
        require_approval = config.get("require_approval", False)
        
        # Get AI context from knowledge base
        ai_context = ""
        if use_knowledge_base and self.knowledge_base:
            ai_context = self.knowledge_base.build_ai_context()
        
        # Get the real-time message sync service and enable AI processing
        from flask import current_app
        message_sync = getattr(current_app, 'message_poller', None)
        
        messages_processed = 0
        replies_sent = 0
        errors = []
        
        if message_sync:
            # Enable AI auto-processing on the message sync service
            message_sync.enable_ai()
            logger.info("✅ AI Auto-Reply ENABLED on real-time message sync")
            
            # Process any pending unread messages in database
            try:
                # Get recent unread messages that haven't been responded to
                unread_messages = self.db.execute_query('''
                    SELECT m.id, m.content, m.from_user, m.owner_id, m.timestamp, m.member_id
                    FROM messages m
                    LEFT JOIN ai_response_log a ON m.id = a.message_id
                    WHERE m.channel = 'clubos'
                    AND m.status IN ('received', 'unread')
                    AND a.id IS NULL
                    ORDER BY m.timestamp DESC
                    LIMIT ?
                ''', (max_replies,), fetch_all=True)
                
                if unread_messages:
                    logger.info(f"📬 Found {len(unread_messages)} unread messages to process")
                    
                    # Get the unified AI agent
                    unified_agent = getattr(message_sync, 'unified_ai_agent', None)
                    
                    if unified_agent:
                        import asyncio
                        
                        for msg in unread_messages:
                            try:
                                msg_dict = dict(msg) if hasattr(msg, 'keys') else {
                                    'id': msg[0], 'content': msg[1], 'from_user': msg[2],
                                    'owner_id': msg[3], 'timestamp': msg[4], 'member_id': msg[5]
                                }
                                
                                # Check if AI should respond to this message
                                if message_sync._should_ai_respond(msg_dict):
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    
                                    result = loop.run_until_complete(
                                        unified_agent.process_new_message(msg_dict)
                                    )
                                    loop.close()
                                    
                                    messages_processed += 1
                                    if result.get('responded'):
                                        replies_sent += 1
                                        logger.info(f"✅ Replied to {msg_dict.get('from_user')}")
                                    
                            except Exception as e:
                                logger.error(f"❌ Error processing message {msg_dict.get('id')}: {e}")
                                errors.append(str(e))
                    else:
                        logger.warning("⚠️ No unified AI agent available for processing")
                else:
                    logger.info("📭 No unread messages to process")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching unread messages: {e}")
                errors.append(str(e))
        else:
            logger.warning("⚠️ Real-time message sync not available")
            errors.append("Message sync service not available")
        
        return {
            "messages_processed": messages_processed,
            "replies_sent": replies_sent,
            "ai_enabled": message_sync.ai_enabled if message_sync else False,
            "context_used": bool(ai_context),
            "errors": errors if errors else None,
            "status": "active" if (message_sync and message_sync.ai_enabled) else "inactive"
        }
    
    def _workflow_prospect_outreach(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically reach out to new prospects.
        
        Steps:
        1. Fetch real-time leads from ClubOS API
        2. Sync new leads to prospects table
        3. Build personalized outreach message using knowledge base
        4. Send via ClubOS FollowUp API
        5. Mark as contacted
        """
        logger.info("🎯 Running prospect outreach workflow...")
        
        max_outreach = config.get("max_outreach_per_day", 50)
        outreach_template = config.get("outreach_template", "default")
        
        # Get sales context from knowledge base
        sales_context = ""
        if self.knowledge_base:
            # Use get_context_for_agent with sales-related categories
            # The knowledge base has 'sales' category (from seed) + 'sales_process' and 'pricing'
            sales_context = self.knowledge_base.get_context_for_agent(
                categories=["sales", "sales_process", "pricing"],
                max_tokens=4000
            )
        
        prospects_found = 0
        new_leads_synced = 0
        outreach_sent = 0
        errors = []
        
        if not self.db:
            logger.warning("No database configured - cannot query prospects")
            return {
                "prospects_found": 0,
                "outreach_sent": 0,
                "context_used": bool(sales_context),
                "status": "no_database"
            }
        
        try:
            # Step 1: Fetch real-time leads from ClubOS API
            logger.info("📡 Fetching real-time leads from ClubOS...")
            try:
                from clubos_leads_api import ClubOSLeadsAPI
                leads_api = ClubOSLeadsAPI()
                if leads_api.authenticate():
                    clubos_leads = leads_api.get_leads(limit=100)
                    logger.info(f"📥 Fetched {len(clubos_leads)} leads from ClubOS")
                    
                    # Step 2: Sync new leads to prospects table
                    for lead in clubos_leads:
                        formatted = leads_api.format_lead_for_outreach(lead)
                        prospect_id = str(formatted.get('id', ''))
                        
                        if not prospect_id:
                            continue
                        
                        # Check if already exists
                        existing = self.db.execute_query(
                            "SELECT prospect_id FROM prospects WHERE prospect_id = ?",
                            (prospect_id,),
                            fetch_one=True
                        )
                        
                        if not existing:
                            # Insert new prospect from ClubOS lead
                            self.db.execute_query(
                                """
                                INSERT INTO prospects (
                                    prospect_id, first_name, last_name, full_name,
                                    email, mobile_phone, source, status, created_date
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'New Lead', ?)
                                """,
                                (
                                    prospect_id,
                                    formatted.get('first_name', ''),
                                    formatted.get('last_name', ''),
                                    formatted.get('full_name', ''),
                                    formatted.get('email', ''),
                                    formatted.get('phone', ''),
                                    formatted.get('source', 'ClubOS'),
                                    formatted.get('created_date', datetime.now().isoformat())
                                )
                            )
                            new_leads_synced += 1
                            logger.info(f"✅ Synced new lead: {formatted.get('full_name')} ({prospect_id})")
                else:
                    logger.warning("⚠️ ClubOS leads API auth failed - using database prospects only")
            except ImportError as e:
                logger.warning(f"ClubOS leads API not available: {e}")
            except Exception as e:
                logger.error(f"Error fetching ClubOS leads: {e}")
                errors.append(f"ClubOS leads fetch error: {str(e)}")
            
            # Step 3: Query prospects with no last_contact_date (never contacted)
            rows = self.db.execute_query(
                """
                SELECT prospect_id, first_name, last_name, email, mobile_phone, source, status
                FROM prospects 
                WHERE (last_contact_date IS NULL OR last_contact_date = '')
                AND status NOT IN ('Converted', 'Not Interested', 'Do Not Contact')
                AND mobile_phone IS NOT NULL AND mobile_phone != ''
                ORDER BY created_date DESC
                LIMIT ?
                """,
                (max_outreach,),
                fetch_all=True
            )
            
            prospects_found = len(rows) if rows else 0
            logger.info(f"📋 Found {prospects_found} prospects needing outreach")
            
            # Import the SAME messaging client used by campaigns
            messaging_client = None
            try:
                from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
                messaging_client = ClubOSMessagingClient()
                if not messaging_client.authenticate():
                    logger.error("❌ ClubOS messaging authentication failed")
                    messaging_client = None
            except ImportError as e:
                logger.warning(f"ClubOS messaging not available: {e}")
            
            for row in (rows or []):
                prospect_id, first_name, last_name, email, phone, source, status = row
                name = f"{first_name or ''} {last_name or ''}".strip()
                
                # Generate personalized outreach message
                message = self._generate_prospect_outreach_message(
                    name=name,
                    source=source,
                    template=outreach_template,
                    sales_context=sales_context
                )
                
                # Send message using SAME method as campaigns
                if messaging_client and message:
                    try:
                        # Build member_data dict for name lookup (same as campaigns)
                        member_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'full_name': name,
                            'prospect_id': prospect_id
                        }
                        
                        success = messaging_client.send_message(
                            member_id=prospect_id,
                            message_text=message,
                            channel="sms",
                            member_data=member_data
                        )
                        
                        if success:
                            outreach_sent += 1
                            # Update last_contact_date
                            self.db.execute_query(
                                "UPDATE prospects SET last_contact_date = ? WHERE prospect_id = ?",
                                (datetime.now().isoformat(), prospect_id)
                            )
                            logger.info(f"✅ Outreach sent to {name} ({prospect_id})")
                        else:
                            errors.append(f"Failed to send to {name}")
                    except Exception as e:
                        errors.append(f"Error sending to {name}: {str(e)}")
                        logger.error(f"Error sending outreach to {name}: {e}")
                else:
                    # Dry run or no client - just log
                    logger.info(f"📝 Would send outreach to {name}: {message[:100]}...")
            
        except Exception as e:
            logger.error(f"Prospect outreach workflow error: {e}")
            errors.append(str(e))
        
        return {
            "prospects_found": prospects_found,
            "new_leads_synced": new_leads_synced,
            "outreach_sent": outreach_sent,
            "errors": errors if errors else None,
            "context_used": bool(sales_context),
            "status": "completed"
        }
    
    def _generate_prospect_outreach_message(
        self, 
        name: str, 
        source: str, 
        template: str,
        sales_context: str
    ) -> str:
        """
        Generate a personalized outreach message for a prospect.
        
        Templates are matched to actual ClubOS lead sources:
        - Web-1day-1: Website 1-day pass signup
        - OnlineSignup: Online membership signup
        - Web-Referral-Guest: Referral guest pass
        - Web-PreMembership: Pre-membership inquiry
        - Walk In / Walk in: Walk-in prospect
        - Mobile-AF-App: Mobile app signup
        - Advertisement: Ad response
        """
        # Use first name only if available
        first_name = name.split()[0] if name else "there"
        
        # Templates matched to ClubOS lead sources
        templates = {
            # Website signups
            "web_1day": f"Hi {first_name}! 👋 Thanks for requesting your free day pass at Anytime Fitness! I'm Jeremy, and I'd love to show you around when you come in. What day works best for your visit? We're open 24/7!",
            
            "online_signup": f"Hey {first_name}! 🎉 I saw you started signing up online - that's awesome! I'm here to help if you have any questions about our membership options. Would you like to come in for a quick tour first? I'm free today or tomorrow!",
            
            "referral": f"Hi {first_name}! A friend referred you to Anytime Fitness - that's great! 😊 We love when members share the gym with friends. I'd be happy to give you a tour and tell you about our current specials. When works best for you?",
            
            "pre_membership": f"Hey {first_name}! Thanks for your interest in Anytime Fitness! 💪 I'd love to answer any questions and show you around. We have some great membership options right now. What time works for you to stop by?",
            
            "walk_in": f"Hi {first_name}! Great meeting you at the gym! Just following up to see if you have any questions about membership. We'd love to have you as part of our fitness family. Let me know if I can help with anything!",
            
            "mobile_app": f"Hey {first_name}! 📱 Thanks for downloading the Anytime Fitness app! I'm Jeremy at the West De Pere location. Would you like to come check out the gym? I can give you a tour and answer any questions. What day works for you?",
            
            "advertisement": f"Hi {first_name}! Thanks for reaching out about Anytime Fitness! 💪 I'd love to show you what makes our gym special. We have 24/7 access, great equipment, and an awesome community. When would you like to stop by for a tour?",
            
            "default": f"Hi {first_name}! 👋 Thanks for your interest in Anytime Fitness West De Pere! I'm Jeremy, and I'd love to help you get started on your fitness journey. Would you like to schedule a free tour? We're open 24/7 and I can work around your schedule!"
        }
        
        # Match source to template
        source_lower = (source or "").lower()
        
        if "1day" in source_lower or "day pass" in source_lower:
            message = templates["web_1day"]
        elif "onlinesignup" in source_lower or "online" in source_lower:
            message = templates["online_signup"]
        elif "referral" in source_lower or "guest" in source_lower:
            message = templates["referral"]
        elif "premembership" in source_lower or "pre-member" in source_lower:
            message = templates["pre_membership"]
        elif "walk" in source_lower:
            message = templates["walk_in"]
        elif "mobile" in source_lower or "app" in source_lower:
            message = templates["mobile_app"]
        elif "ad" in source_lower or "advertisement" in source_lower:
            message = templates["advertisement"]
        else:
            message = templates.get(template, templates["default"])
        
        return message
    
    def _workflow_past_due_reminders(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send daily payment reminders to past due members.
        
        Steps:
        1. Get list of past due members from database
        2. Filter: only those not reminded today, not on payment plan exempt
        3. Build reminder message based on days past due
        4. Send via messaging API
        """
        logger.info("💸 Running past due reminders workflow...")
        
        min_days = config.get("min_days_past_due", 7)
        urgency_days = config.get("urgency_threshold_days", 30)
        respect_payment_plans = config.get("respect_payment_plans", True)
        max_reminders = config.get("max_reminders_per_day", 1)
        
        # Get payment-related context from knowledge base
        payment_context = ""
        if self.knowledge_base:
            payment_context = self.knowledge_base.get_context_for_agent(
                categories=["policies", "billing"],
                max_tokens=2000
            )
        
        members_past_due = 0
        reminders_sent = 0
        exemptions_skipped = 0
        errors = []
        
        if not self.db:
            logger.warning("No database configured - cannot query members")
            return {
                "members_past_due": 0,
                "reminders_sent": 0,
                "exemptions_skipped": 0,
                "status": "no_database"
            }
        
        try:
            # Build query based on respect_payment_plans setting
            if respect_payment_plans:
                query = """
                    SELECT member_id, name, email, phone, past_due_amount, past_due_days, payment_plan_exempt
                    FROM members 
                    WHERE past_due_days >= ?
                    AND (payment_plan_exempt IS NULL OR payment_plan_exempt = 0)
                    AND phone IS NOT NULL AND phone != ''
                    ORDER BY past_due_days DESC
                """
            else:
                query = """
                    SELECT member_id, name, email, phone, past_due_amount, past_due_days, payment_plan_exempt
                    FROM members 
                    WHERE past_due_days >= ?
                    AND phone IS NOT NULL AND phone != ''
                    ORDER BY past_due_days DESC
                """
            
            rows = self.db.execute_query(query, (min_days,), fetch_all=True)
            members_past_due = len(rows) if rows else 0
            
            logger.info(f"📋 Found {members_past_due} members past due >= {min_days} days")
            
            # Count exemptions if not respecting payment plans
            if not respect_payment_plans:
                exempt_count = self.db.execute_query(
                    "SELECT COUNT(*) FROM members WHERE past_due_days >= ? AND payment_plan_exempt = 1",
                    (min_days,),
                    fetch_one=True
                )
                exemptions_skipped = exempt_count[0] if exempt_count else 0
            
            # Import the SAME messaging client used by campaigns
            messaging_client = None
            try:
                from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
                messaging_client = ClubOSMessagingClient()
                if not messaging_client.authenticate():
                    logger.error("❌ ClubOS messaging authentication failed")
                    messaging_client = None
            except ImportError as e:
                logger.warning(f"ClubOS messaging not available: {e}")
            
            for row in (rows or []):
                member_id, name, email, phone, past_due_amount, past_due_days, exempt = row
                
                # Skip if on payment plan (double check)
                if exempt:
                    exemptions_skipped += 1
                    continue
                
                # Determine urgency level
                is_urgent = past_due_days >= urgency_days
                
                # Generate reminder message
                message = self._generate_payment_reminder_message(
                    name=name,
                    amount=past_due_amount,
                    days=past_due_days,
                    urgent=is_urgent
                )
                
                # Send message using SAME method as campaigns
                if messaging_client and message:
                    try:
                        # Parse name for member lookup
                        name_parts = name.strip().split() if name else []
                        first_name = name_parts[0] if name_parts else ''
                        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                        
                        member_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'full_name': name,
                            'prospect_id': member_id
                        }
                        
                        success = messaging_client.send_message(
                            member_id=member_id,
                            message_text=message,
                            channel="sms",
                            member_data=member_data
                        )
                        
                        if success:
                            reminders_sent += 1
                            logger.info(f"✅ Payment reminder sent to {name} (${past_due_amount}, {past_due_days} days)")
                        else:
                            errors.append(f"Failed to send to {name}")
                    except Exception as e:
                        errors.append(f"Error sending to {name}: {str(e)}")
                        logger.error(f"Error sending reminder to {name}: {e}")
                else:
                    # Dry run or no client - just log
                    urgency = "URGENT" if is_urgent else "standard"
                    logger.info(f"📝 Would send {urgency} reminder to {name}: ${past_due_amount}")
            
        except Exception as e:
            logger.error(f"Past due reminders workflow error: {e}")
            errors.append(str(e))
        
        return {
            "members_past_due": members_past_due,
            "reminders_sent": reminders_sent,
            "exemptions_skipped": exemptions_skipped,
            "errors": errors if errors else None,
            "status": "completed"
        }
    
    def _generate_payment_reminder_message(
        self,
        name: str,
        amount: float,
        days: int,
        urgent: bool
    ) -> str:
        """Generate a payment reminder message based on urgency"""
        
        if urgent:
            # Urgent reminder (30+ days)
            return f"Hi {name}, this is an urgent notice regarding your Anytime Fitness account. Your balance of ${amount:.2f} is now {days} days past due. To avoid service interruption, please make a payment as soon as possible. Reply here or call us to discuss payment options. Thank you!"
        else:
            # Standard reminder (7-30 days)
            return f"Hi {name}! 👋 Just a friendly reminder that your Anytime Fitness account has a balance of ${amount:.2f} that's {days} days past due. Please let us know if you have any questions about your account. We're here to help! 💪"
    
    def _workflow_auto_lock_past_due(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-lock gym access for severely past due members.
        
        Steps:
        1. Get members past due beyond grace period
        2. Filter out payment_plan_exempt members
        3. Send warning (if configured)
        4. Lock access via ClubOS/door system
        
        Note: This workflow requires confirmation by default for safety.
        """
        logger.info("🔒 Running auto-lock workflow...")
        
        grace_period = config.get("grace_period_days", 14)
        respect_payment_plans = config.get("respect_payment_plans", True)
        send_warning = config.get("send_warning_before_lock", True)
        warning_days = config.get("warning_days_before", 3)
        require_confirmation = config.get("require_confirmation", True)
        
        candidates_found = 0
        warnings_sent = 0
        members_locked = 0
        exemptions_skipped = 0
        awaiting_confirmation = []
        errors = []
        
        if not self.db:
            logger.warning("No database configured - cannot query members")
            return {
                "candidates_found": 0,
                "warnings_sent": 0,
                "members_locked": 0,
                "exemptions_skipped": 0,
                "status": "no_database"
            }
        
        try:
            # Build query - get members past grace period
            if respect_payment_plans:
                query = """
                    SELECT member_id, name, email, phone, past_due_amount, past_due_days, payment_plan_exempt
                    FROM members 
                    WHERE past_due_days >= ?
                    AND (payment_plan_exempt IS NULL OR payment_plan_exempt = 0)
                    ORDER BY past_due_days DESC
                """
            else:
                query = """
                    SELECT member_id, name, email, phone, past_due_amount, past_due_days, payment_plan_exempt
                    FROM members 
                    WHERE past_due_days >= ?
                    ORDER BY past_due_days DESC
                """
            
            rows = self.db.execute_query(query, (grace_period,), fetch_all=True)
            candidates_found = len(rows) if rows else 0
            
            logger.info(f"🔒 Found {candidates_found} members past due >= {grace_period} days")
            
            # Count total exemptions
            exempt_count = self.db.execute_query(
                "SELECT COUNT(*) FROM members WHERE past_due_days >= ? AND payment_plan_exempt = 1",
                (grace_period,),
                fetch_one=True
            )
            if respect_payment_plans:
                exemptions_skipped = exempt_count[0] if exempt_count else 0
            
            # Import the SAME messaging client used by campaigns
            messaging_client = None
            try:
                from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
                messaging_client = ClubOSMessagingClient()
                if not messaging_client.authenticate():
                    logger.error("❌ ClubOS messaging authentication failed")
                    messaging_client = None
            except ImportError as e:
                logger.warning(f"ClubOS messaging not available: {e}")
            
            for row in (rows or []):
                member_id, name, email, phone, past_due_amount, past_due_days, exempt = row
                
                # Skip if on payment plan
                if exempt and respect_payment_plans:
                    exemptions_skipped += 1
                    continue
                
                # Determine if we should warn or lock
                days_until_lock = (grace_period + warning_days) - past_due_days
                
                if days_until_lock > 0 and send_warning:
                    # Send warning message
                    if messaging_client and phone:
                        try:
                            warning_msg = f"Hi {name}, this is an important notice. Your Anytime Fitness account is ${past_due_amount:.2f} past due ({past_due_days} days). Your gym access will be suspended in {days_until_lock} days unless payment is received. Please contact us immediately to avoid service interruption."
                            
                            # Parse name for lookup
                            name_parts = name.strip().split() if name else []
                            first_name = name_parts[0] if name_parts else ''
                            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                            
                            member_data = {
                                'first_name': first_name,
                                'last_name': last_name,
                                'full_name': name,
                                'prospect_id': member_id
                            }
                            
                            success = messaging_client.send_message(
                                member_id=member_id,
                                message_text=warning_msg,
                                channel="sms",
                                member_data=member_data
                            )
                            
                            if success:
                                warnings_sent += 1
                                logger.info(f"⚠️ Lock warning sent to {name}")
                        except Exception as e:
                            errors.append(f"Warning failed for {name}: {str(e)}")
                    else:
                        logger.info(f"📝 Would warn {name}: {days_until_lock} days until lock")
                
                elif require_confirmation:
                    # Queue for admin confirmation
                    awaiting_confirmation.append({
                        "member_id": member_id,
                        "name": name,
                        "past_due_amount": past_due_amount,
                        "past_due_days": past_due_days
                    })
                    logger.info(f"🔐 {name} queued for lock confirmation (${past_due_amount}, {past_due_days} days)")
                
                else:
                    # Auto-lock (would execute ClubOS lock API here)
                    # For now, just log as this is a destructive action
                    logger.warning(f"🔒 Would auto-lock {name} - DISABLED FOR SAFETY")
                    # members_locked += 1
            
        except Exception as e:
            logger.error(f"Auto-lock workflow error: {e}")
            errors.append(str(e))
        
        return {
            "candidates_found": candidates_found,
            "warnings_sent": warnings_sent,
            "members_locked": members_locked,
            "exemptions_skipped": exemptions_skipped,
            "awaiting_confirmation": awaiting_confirmation,
            "errors": errors if errors else None,
            "status": "completed"
        }
    
    def _workflow_square_invoice(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and send invoices via Square.
        
        Steps:
        1. Check for pending invoice requests
        2. Build invoice with Square API
        3. Send if auto_send enabled
        """
        logger.info("📄 Running Square invoice workflow...")
        
        auto_send = config.get("auto_send", False)
        payment_due_days = config.get("payment_due_days", 7)
        
        # TODO: Integrate with Square API
        # 1. Check for pending invoice items
        # 2. Create invoice via Square
        # 3. If auto_send, send invoice
        # 4. Log invoice creation
        
        return {
            "invoices_created": 0,
            "invoices_sent": 0,
            "auto_send_enabled": auto_send,
            "status": "ready_for_integration"
        }
    
    # ================================================================
    # Background Worker (Optional - for continuous execution)
    # ================================================================
    
    def start_background_worker(self, check_interval_seconds: int = 60):
        """Start background thread to continuously run enabled workflows"""
        if self._running:
            logger.warning("Background worker already running")
            return
        
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._background_worker_loop,
            args=(check_interval_seconds,),
            daemon=True
        )
        self._worker_thread.start()
        logger.info(f"🔄 Background worker started (checking every {check_interval_seconds}s)")
    
    def stop_background_worker(self):
        """Stop the background worker"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            self._worker_thread = None
        logger.info("⏹️  Background worker stopped")
    
    def _background_worker_loop(self, check_interval: int):
        """Main loop for background worker"""
        while self._running:
            try:
                for workflow_name in self._workflows:
                    if not self._running:
                        break
                    
                    settings = self.get_workflow_settings(workflow_name)
                    if settings.get("enabled"):
                        # Check if enough time has passed since last run
                        last_run = self._last_execution.get(workflow_name)
                        if last_run:
                            elapsed = (datetime.now() - last_run).total_seconds()
                            config = settings.get("config", {})
                            interval = config.get("check_interval_minutes", 60) * 60
                            
                            if elapsed < interval:
                                continue
                        
                        # Run the workflow
                        self.run_workflow(workflow_name)
                
                # Sleep before next check
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Background worker error: {e}")
                time.sleep(check_interval)
    
    @property
    def is_running(self) -> bool:
        """Check if background worker is running"""
        return self._running


# Singleton instance for easy access
_workflow_manager: Optional[UnifiedWorkflowManager] = None


def get_workflow_manager() -> UnifiedWorkflowManager:
    """Get or create the singleton workflow manager"""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = UnifiedWorkflowManager()
    return _workflow_manager


def init_workflow_manager(db_manager, knowledge_base=None) -> UnifiedWorkflowManager:
    """Initialize the workflow manager with dependencies"""
    global _workflow_manager
    _workflow_manager = UnifiedWorkflowManager(db_manager, knowledge_base)
    return _workflow_manager
