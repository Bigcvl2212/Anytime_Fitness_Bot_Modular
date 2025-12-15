"""
AI Knowledge Base System
Manages instruction documents, sales processes, pricing, protocols, and policies
that the AI agents use to stay compliant and aligned with business goals.

Documents are stored in the database and can be managed through the admin UI.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AIKnowledgeBase:
    """
    Centralized knowledge base for AI agents.
    Stores and retrieves instruction documents, sales processes, pricing info,
    protocols, and policies that guide AI behavior.
    """
    
    # Document categories
    CATEGORIES = {
        # Core instruction bundles
        'system': {
            'name': 'System Instructions',
            'description': 'AI identity, tone, and operating rules'
        },
        'business': {
            'name': 'Business Policies',
            'description': 'Pricing, contracts, amenities, and partnerships'
        },
        'collections': {
            'name': 'Collections & Billing',
            'description': 'Past-due handling, payment plans, and recovery playbooks'
        },
        'sales': {
            'name': 'Sales Playbooks',
            'description': 'Prospect outreach, follow-up cadences, and scripts'
        },
        'brand': {
            'name': 'Brand Voice & Tone',
            'description': 'Voice, messaging, and content guardrails'
        },
        'promotions': {
            'name': 'Campaigns & Promotions',
            'description': 'Seasonal offers and marketing programs'
        },
        # Legacy/extended categories still used by tooling
        'sales_process': {
            'name': 'Sales Process & Scripts',
            'description': 'Legacy sales workflows and scripts'
        },
        'pricing': {
            'name': 'Plans, Programs & Pricing',
            'description': 'Membership and training price sheets'
        },
        'protocols': {
            'name': 'Gym Protocols & Procedures',
            'description': 'Operational SOPs and checklists'
        },
        'policies': {
            'name': 'Company Policies & Compliance',
            'description': 'Corporate policies, approvals, and compliance rules'
        },
        'templates': {
            'name': 'Message Templates',
            'description': 'Reusable outreach templates'
        },
        'faq': {
            'name': 'Frequently Asked Questions',
            'description': 'Member and prospect FAQs'
        },
        'escalation': {
            'name': 'Escalation Guidelines',
            'description': 'When and how to pull in humans'
        },
        'personas': {
            'name': 'Customer Personas & Handling',
            'description': 'Handling guidance by persona type'
        }
    }
    
    def __init__(self, db_manager):
        """
        Initialize Knowledge Base
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self._cache = {}
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
        
        # Initialize database tables
        self._init_tables()
        logger.info("✅ AI Knowledge Base initialized")
    
    def _init_tables(self):
        """Create knowledge base tables if they don't exist"""
        try:
            # Main knowledge documents table
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS ai_knowledge_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    tags TEXT,
                    metadata TEXT
                )
            ''')
            
            # Document versions for audit trail
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS ai_knowledge_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    version INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    changed_by TEXT,
                    change_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES ai_knowledge_documents(id)
                )
            ''')
            
            # Agent feature toggles and settings
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS ai_agent_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_key TEXT UNIQUE NOT NULL,
                    feature_name TEXT NOT NULL,
                    description TEXT,
                    is_enabled BOOLEAN DEFAULT 0,
                    settings TEXT,
                    last_run TIMESTAMP,
                    run_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Agent activity log
            self.db_manager.execute_query('''
                CREATE TABLE IF NOT EXISTS ai_agent_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_type TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target_id TEXT,
                    target_type TEXT,
                    summary TEXT,
                    details TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize default features if not exist
            self._init_default_features()
            
            # Seed default knowledge documents if empty
            self._seed_default_documents()
            
            logger.info("✅ Knowledge Base tables initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize knowledge base tables: {e}")
    
    def _init_default_features(self):
        """Initialize default agent features"""
        default_features = [
            {
                'feature_key': 'inbox_auto_reply',
                'feature_name': 'Inbox Auto-Reply Agent',
                'description': 'Automatically responds to member messages for billing questions, schedule changes, and general inquiries',
                'is_enabled': False,
                'settings': json.dumps({
                    'confidence_threshold': 0.80,
                    'max_responses_per_hour': 50,
                    'require_approval_for_refunds': True,
                    'escalate_complaints': True
                })
            },
            {
                'feature_key': 'prospect_outreach',
                'feature_name': 'Prospect Auto-Outreach Agent',
                'description': 'Monitors for new prospects and automatically reaches out to schedule gym visits',
                'is_enabled': False,
                'settings': json.dumps({
                    'delay_minutes_after_creation': 5,
                    'follow_up_intervals_hours': [24, 72, 168],
                    'max_outreach_attempts': 4,
                    'use_sales_process': True
                })
            },
            {
                'feature_key': 'collections_reminders',
                'feature_name': 'Collections Reminder Agent',
                'description': 'Sends daily payment reminders to past due members',
                'is_enabled': False,
                'settings': json.dumps({
                    'reminder_frequency': 'daily',
                    'min_past_due_days': 7,
                    'max_reminders_per_member': 5,
                    'escalation_days': [14, 30, 60]
                })
            },
            {
                'feature_key': 'auto_lock_access',
                'feature_name': 'Auto Lock/Unlock Gym Access',
                'description': 'Automatically locks gym access for past due members and unlocks when paid',
                'is_enabled': False,
                'settings': json.dumps({
                    'lock_after_days_past_due': 14,
                    'auto_unlock_on_payment': True,
                    'respect_payment_plans': True,
                    'notify_member_on_lock': True,
                    'notify_member_on_unlock': True
                })
            },
            {
                'feature_key': 'invoice_automation',
                'feature_name': 'Invoice Automation Agent',
                'description': 'Creates and sends Square invoices automatically when needed',
                'is_enabled': False,
                'settings': json.dumps({
                    'auto_send_past_due': True,
                    'min_amount_for_invoice': 25.00,
                    'include_payment_link': True,
                    'reminder_after_days': 7
                })
            },
            {
                'feature_key': 'campaign_automation',
                'feature_name': 'Campaign Automation Agent',
                'description': 'Runs scheduled marketing campaigns to prospects, green members, and PPV members',
                'is_enabled': False,
                'settings': json.dumps({
                    'campaign_time': '06:00',
                    'days_of_week': ['monday', 'wednesday', 'friday'],
                    'cooldown_days': 7,
                    'max_recipients_per_day': 100
                })
            }
        ]
        
        for feature in default_features:
            try:
                # Check if feature exists
                existing = self.db_manager.execute_query(
                    "SELECT id FROM ai_agent_features WHERE feature_key = ?",
                    (feature['feature_key'],),
                    fetch_one=True
                )
                
                if not existing:
                    self.db_manager.execute_query('''
                        INSERT INTO ai_agent_features 
                        (feature_key, feature_name, description, is_enabled, settings)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        feature['feature_key'],
                        feature['feature_name'],
                        feature['description'],
                        feature['is_enabled'],
                        feature['settings']
                    ))
                    logger.info(f"✅ Created feature: {feature['feature_key']}")
            except Exception as e:
                logger.warning(f"⚠️ Could not create feature {feature['feature_key']}: {e}")
    
    def _seed_default_documents(self):
        """Seed default knowledge documents if database is empty"""
        try:
            # Check if any documents exist
            count = self.db_manager.execute_query(
                "SELECT COUNT(*) as count FROM ai_knowledge_documents",
                fetch_one=True
            )
            
            if count and (count.get('count', 0) if isinstance(count, dict) else count[0]) > 0:
                return  # Documents already exist
            
            # Seed default documents
            default_docs = [
                {
                    'category': 'sales_process',
                    'title': 'New Prospect Sales Process',
                    'content': '''# New Prospect Sales Process

## Step 1: Initial Contact (Within 5 minutes of lead creation)
- Send warm welcome message introducing yourself
- Ask what brought them to Anytime Fitness
- Offer to schedule a tour/trial visit

## Step 2: Schedule Tour
- Offer specific time slots (morning, afternoon, evening)
- Confirm their availability
- Send calendar reminder

## Step 3: Tour Follow-up
- If no response in 24 hours, send friendly follow-up
- If no response in 72 hours, send value-focused message (amenities, classes)
- If no response in 1 week, send final outreach with limited-time offer

## Step 4: Closing
- After tour, send thank you message
- Present membership options
- Address any objections
- Close with clear call-to-action

## Key Points
- Always be friendly and helpful
- Never be pushy or aggressive
- Focus on their fitness goals
- Personalize based on their interests
''',
                    'priority': 10
                },
                {
                    'category': 'pricing',
                    'title': 'Membership Plans & Pricing',
                    'content': '''# Membership Plans & Pricing

## Standard Membership
- Monthly: $XX/month
- Annual: $XX/year (XX% savings)
- Includes: 24/7 access, all locations, basic equipment

## Premium Membership
- Monthly: $XX/month
- Annual: $XX/year (XX% savings)
- Includes: Everything in Standard + tanning, HydroMassage, guest privileges

## Personal Training Packages
- 4 sessions: $XXX
- 8 sessions: $XXX
- 12 sessions: $XXX (best value)

## Current Promotions
- [Update with current promotions]

## Important Notes
- All memberships require enrollment fee
- 30-day notice for cancellation
- Freeze options available (up to 3 months/year)

[UPDATE THIS DOCUMENT WITH YOUR ACTUAL PRICING]
''',
                    'priority': 9
                },
                {
                    'category': 'protocols',
                    'title': 'Member Communication Protocol',
                    'content': '''# Member Communication Protocol

## Response Time Standards
- New prospects: Within 5 minutes during business hours
- Member inquiries: Within 2 hours
- Billing questions: Within 1 hour
- Complaints: Within 30 minutes (escalate to manager)

## Communication Tone
- Always professional but friendly
- Use member's first name
- Be empathetic and understanding
- Never argue or be defensive
- Apologize when appropriate

## What to NEVER Say
- "That's not my department"
- "You should have read the contract"
- "That's our policy"
- Anything negative about competitors
- Personal opinions on political/social issues

## Escalation Triggers
- Member threatens legal action
- Member requests manager
- Member uses profanity
- Billing dispute over $100
- Any safety concern
''',
                    'priority': 8
                },
                {
                    'category': 'policies',
                    'title': 'Past Due & Collections Policy',
                    'content': '''# Past Due & Collections Policy

## Payment Grace Period
- 7 days grace period after due date
- No lock during grace period
- Friendly reminder sent on day 3

## Past Due Process
- Day 8-14: Firm reminder, offer payment plan
- Day 15-30: Access may be locked, urgent notice
- Day 31-60: Final notice, collections warning
- Day 60+: Refer to collections agency

## Payment Plans
- Available for balances over $50
- Maximum 3 monthly installments
- Members on payment plans KEEP gym access
- Payment plan must be approved

## Lock/Unlock Rules
- Auto-lock after 14 days past due (if enabled)
- EXCEPTION: Members on approved payment plans
- Auto-unlock immediately when paid
- Manual unlock available for special circumstances

## Important Notes
- Always try to work with members
- Offer payment plan before locking
- Document all communication
- Never threaten or be aggressive
''',
                    'priority': 10
                },
                {
                    'category': 'faq',
                    'title': 'Common Member Questions',
                    'content': '''# Common Member Questions & Answers

## Billing Questions

Q: When is my payment due?
A: Your payment is due on the [day] of each month.

Q: Can I change my payment date?
A: Yes, we can adjust your billing date. Contact us to make this change.

Q: Why was I charged twice?
A: Let me look into this for you. [Check billing history and explain]

## Membership Questions

Q: Can I freeze my membership?
A: Yes, you can freeze for up to 3 months per year. There's a $X/month freeze fee.

Q: How do I cancel my membership?
A: You can cancel with 30 days notice. Visit the gym or send written notice.

Q: Can I bring a guest?
A: [Premium members] Yes, you get X guest passes per month.
A: [Standard members] Guest passes can be purchased for $X.

## Facility Questions

Q: What are your hours?
A: We're open 24/7 for all members with key fob access.

Q: Do you have personal trainers?
A: Yes! We have certified personal trainers. Would you like info on training packages?

Q: Is there a class schedule?
A: [Provide class schedule or link]
''',
                    'priority': 7
                },
                {
                    'category': 'escalation',
                    'title': 'Escalation Guidelines',
                    'content': '''# Escalation Guidelines

## Immediate Escalation Required
- Member threatens legal action
- Member threatens physical harm
- Any discrimination complaint
- Any harassment report
- Safety incidents
- Medical emergencies
- Suspected fraud

## Escalate to Manager
- Refund requests over $50
- Cancellation with dispute
- Multiple billing issues
- Angry/upset member requesting manager
- Any situation you're unsure about

## How to Escalate
1. Acknowledge the member's concern
2. Apologize for any inconvenience
3. Explain you're getting a manager involved
4. Create detailed notes of the situation
5. Tag the conversation as "escalated"
6. Notify manager immediately

## After Escalation
- Do not continue the conversation
- Wait for manager direction
- Document everything
''',
                    'priority': 9
                }
            ]
            
            for doc in default_docs:
                self.db_manager.execute_query('''
                    INSERT INTO ai_knowledge_documents 
                    (category, title, content, priority, created_by)
                    VALUES (?, ?, ?, ?, ?)
                ''', (doc['category'], doc['title'], doc['content'], doc['priority'], 'system'))
            
            logger.info(f"✅ Seeded {len(default_docs)} default knowledge documents")
            
        except Exception as e:
            logger.error(f"❌ Failed to seed default documents: {e}")
    
    # ==========================================================================
    # Document Management
    # ==========================================================================
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM ai_knowledge_documents WHERE id = ?",
                (doc_id,),
                fetch_one=True
            )
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"❌ Error getting document {doc_id}: {e}")
            return None
    
    def get_documents_by_category(self, category: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all documents in a category"""
        try:
            query = "SELECT * FROM ai_knowledge_documents WHERE category = ?"
            params = [category]
            
            if active_only:
                query += " AND is_active = 1"
            
            query += " ORDER BY priority DESC, title ASC"
            
            results = self.db_manager.execute_query(query, params, fetch_all=True)
            return [dict(r) for r in results] if results else []
        except Exception as e:
            logger.error(f"❌ Error getting documents for category {category}: {e}")
            return []
    
    def get_all_documents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all knowledge documents"""
        try:
            query = "SELECT * FROM ai_knowledge_documents"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY category, priority DESC, title ASC"
            
            results = self.db_manager.execute_query(query, fetch_all=True)
            return [dict(r) for r in results] if results else []
        except Exception as e:
            logger.error(f"❌ Error getting all documents: {e}")
            return []
    
    def create_document(self, category: str, title: str, content: str,
                       priority: int = 0, created_by: str = None,
                       tags: List[str] = None) -> Optional[int]:
        """Create a new knowledge document"""
        try:
            self.db_manager.execute_query('''
                INSERT INTO ai_knowledge_documents 
                (category, title, content, priority, created_by, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, title, content, priority, created_by, json.dumps(tags or [])))
            
            # Get the ID of the inserted document
            result = self.db_manager.execute_query(
                "SELECT id FROM ai_knowledge_documents WHERE category = ? AND title = ? ORDER BY id DESC LIMIT 1",
                (category, title),
                fetch_one=True
            )
            
            doc_id = result['id'] if isinstance(result, dict) else result[0]
            self._invalidate_cache()
            logger.info(f"✅ Created document: {title} (ID: {doc_id})")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Error creating document: {e}")
            return None
    
    def update_document(self, doc_id: int, title: str = None, content: str = None,
                       priority: int = None, is_active: bool = None,
                       change_reason: str = None, changed_by: str = None) -> bool:
        """Update an existing document (with version history)"""
        try:
            # Get current document for versioning
            current = self.get_document(doc_id)
            if not current:
                return False
            
            # Save version history if content changed
            if content and content != current.get('content'):
                self.db_manager.execute_query('''
                    INSERT INTO ai_knowledge_versions 
                    (document_id, version, content, changed_by, change_reason)
                    VALUES (?, ?, ?, ?, ?)
                ''', (doc_id, current.get('version', 1), current.get('content'),
                      changed_by, change_reason))
            
            # Build update query
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if content is not None:
                updates.append("content = ?")
                params.append(content)
                updates.append("version = version + 1")
            
            if priority is not None:
                updates.append("priority = ?")
                params.append(priority)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(doc_id)
            
            query = f"UPDATE ai_knowledge_documents SET {', '.join(updates)} WHERE id = ?"
            self.db_manager.execute_query(query, params)
            
            self._invalidate_cache()
            logger.info(f"✅ Updated document ID {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating document {doc_id}: {e}")
            return False
    
    def delete_document(self, doc_id: int, soft_delete: bool = True) -> bool:
        """Delete a document (soft delete by default)"""
        try:
            if soft_delete:
                self.db_manager.execute_query(
                    "UPDATE ai_knowledge_documents SET is_active = 0 WHERE id = ?",
                    (doc_id,)
                )
            else:
                self.db_manager.execute_query(
                    "DELETE FROM ai_knowledge_documents WHERE id = ?",
                    (doc_id,)
                )
            
            self._invalidate_cache()
            logger.info(f"✅ Deleted document ID {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting document {doc_id}: {e}")
            return False
    
    # ==========================================================================
    # Agent Features
    # ==========================================================================
    
    def get_feature(self, feature_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent feature"""
        try:
            result = self.db_manager.execute_query(
                "SELECT * FROM ai_agent_features WHERE feature_key = ?",
                (feature_key,),
                fetch_one=True
            )
            if result:
                data = dict(result)
                if data.get('settings'):
                    data['settings'] = json.loads(data['settings'])
                return data
            return None
        except Exception as e:
            logger.error(f"❌ Error getting feature {feature_key}: {e}")
            return None
    
    def get_all_features(self) -> List[Dict[str, Any]]:
        """Get all agent features with their status"""
        try:
            results = self.db_manager.execute_query(
                "SELECT * FROM ai_agent_features ORDER BY feature_name",
                fetch_all=True
            )
            features = []
            for r in (results or []):
                data = dict(r)
                if data.get('settings'):
                    data['settings'] = json.loads(data['settings'])
                features.append(data)
            return features
        except Exception as e:
            logger.error(f"❌ Error getting all features: {e}")
            return []
    
    def is_feature_enabled(self, feature_key: str) -> bool:
        """Check if a specific feature is enabled"""
        feature = self.get_feature(feature_key)
        return feature.get('is_enabled', False) if feature else False
    
    def toggle_feature(self, feature_key: str, enabled: bool) -> bool:
        """Enable or disable a feature"""
        try:
            self.db_manager.execute_query('''
                UPDATE ai_agent_features 
                SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE feature_key = ?
            ''', (enabled, feature_key))
            
            logger.info(f"✅ Feature {feature_key} {'enabled' if enabled else 'disabled'}")
            return True
        except Exception as e:
            logger.error(f"❌ Error toggling feature {feature_key}: {e}")
            return False
    
    def update_feature_settings(self, feature_key: str, settings: Dict[str, Any]) -> bool:
        """Update settings for a feature"""
        try:
            self.db_manager.execute_query('''
                UPDATE ai_agent_features 
                SET settings = ?, updated_at = CURRENT_TIMESTAMP
                WHERE feature_key = ?
            ''', (json.dumps(settings), feature_key))
            
            logger.info(f"✅ Updated settings for feature {feature_key}")
            return True
        except Exception as e:
            logger.error(f"❌ Error updating feature settings {feature_key}: {e}")
            return False
    
    def record_feature_run(self, feature_key: str, success: bool) -> None:
        """Record that a feature ran (for stats)"""
        try:
            if success:
                self.db_manager.execute_query('''
                    UPDATE ai_agent_features 
                    SET last_run = CURRENT_TIMESTAMP,
                        run_count = run_count + 1,
                        success_count = success_count + 1
                    WHERE feature_key = ?
                ''', (feature_key,))
            else:
                self.db_manager.execute_query('''
                    UPDATE ai_agent_features 
                    SET last_run = CURRENT_TIMESTAMP,
                        run_count = run_count + 1,
                        error_count = error_count + 1
                    WHERE feature_key = ?
                ''', (feature_key,))
        except Exception as e:
            logger.warning(f"⚠️ Could not record feature run: {e}")
    
    # ==========================================================================
    # Activity Logging
    # ==========================================================================
    
    def log_activity(self, agent_type: str, action_type: str,
                    target_id: str = None, target_type: str = None,
                    summary: str = None, details: Dict = None,
                    success: bool = True, error_message: str = None) -> None:
        """Log an agent activity"""
        try:
            self.db_manager.execute_query('''
                INSERT INTO ai_agent_activity 
                (agent_type, action_type, target_id, target_type, summary, details, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_type, action_type, target_id, target_type,
                summary, json.dumps(details) if details else None,
                success, error_message
            ))
        except Exception as e:
            logger.warning(f"⚠️ Could not log activity: {e}")
    
    def get_recent_activity(self, limit: int = 50, agent_type: str = None) -> List[Dict[str, Any]]:
        """Get recent agent activity"""
        try:
            query = "SELECT * FROM ai_agent_activity"
            params = []
            
            if agent_type:
                query += " WHERE agent_type = ?"
                params.append(agent_type)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.db_manager.execute_query(query, params, fetch_all=True)
            activities = []
            for r in (results or []):
                data = dict(r)
                if data.get('details'):
                    try:
                        data['details'] = json.loads(data['details'])
                    except:
                        pass
                activities.append(data)
            return activities
        except Exception as e:
            logger.error(f"❌ Error getting activity: {e}")
            return []
    
    # ==========================================================================
    # Context Generation for AI
    # ==========================================================================
    
    def build_ai_context(self, categories: List[str] = None, max_tokens: int = 8000) -> str:
        """Alias for get_context_for_agent for backwards compatibility"""
        return self.get_context_for_agent(categories=categories, max_tokens=max_tokens)
    
    def get_context_for_agent(self, categories: List[str] = None, 
                              max_tokens: int = 8000) -> str:
        """
        Generate context string for AI agent from knowledge documents
        
        Args:
            categories: Optional list of categories to include (default: all)
            max_tokens: Approximate max tokens to include
            
        Returns:
            Formatted context string for AI prompt
        """
        try:
            # Check cache
            cache_key = f"context_{'-'.join(sorted(categories or []))}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            docs = []
            if categories:
                for cat in categories:
                    docs.extend(self.get_documents_by_category(cat))
            else:
                docs = self.get_all_documents()
            
            if not docs:
                return ""
            
            # Sort by priority
            docs.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            # Build context string
            context_parts = ["### KNOWLEDGE BASE ###\n"]
            current_length = 0
            char_limit = max_tokens * 4  # Rough estimate: 4 chars per token
            
            for doc in docs:
                doc_text = f"\n## {doc['title']} ({doc['category']})\n{doc['content']}\n"
                
                if current_length + len(doc_text) > char_limit:
                    break
                
                context_parts.append(doc_text)
                current_length += len(doc_text)
            
            context = "\n".join(context_parts)
            
            # Cache it
            self._cache[cache_key] = context
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Error generating AI context: {e}")
            return ""
    
    def _invalidate_cache(self):
        """Invalidate the cache when documents change"""
        self._cache = {}
        self._cache_timestamp = None
