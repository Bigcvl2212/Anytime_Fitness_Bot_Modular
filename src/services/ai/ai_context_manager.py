#!/usr/bin/env python3
"""
AI Context Manager
Manages conversation context, memory, and role-specific prompts
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Represents a conversation context with an AI agent"""
    session_id: str
    user_id: str
    agent_type: str  # 'admin' or 'sales'
    context_data: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    created_at: datetime
    last_updated: datetime
    expires_at: datetime

class AIContextManager:
    """
    Manages AI conversation contexts, memory, and role-specific prompts
    """

    def __init__(self, db_manager=None):
        """
        Initialize AI Context Manager

        Args:
            db_manager: Database manager for persistent storage
        """
        self.db_manager = db_manager
        self._active_contexts = {}  # In-memory cache for active conversations
        self._context_timeout = timedelta(hours=2)  # Conversations expire after 2 hours

        # Role-specific system prompts
        self._system_prompts = {
            'admin': self._get_admin_system_prompt(),
            'sales': self._get_sales_system_prompt()
        }

    def _get_admin_system_prompt(self) -> str:
        """Get system prompt for admin AI agent"""
        return """You are an intelligent administrative assistant for a gym management system called Gym Bot. Your role is to help administrators manage the system efficiently and securely.

Key responsibilities:
- User management (create, edit, delete admin users)
- System monitoring and health checks
- Security analysis and recommendations
- Data insights and reporting
- Administrative task automation

Important guidelines:
- Always prioritize security and data protection
- Confirm destructive actions before execution
- Provide clear, actionable recommendations
- Use natural language that's professional but friendly
- When asked to perform actions, provide specific steps or commands
- If unsure about permissions, ask for clarification

Available data includes:
- Admin users and permissions
- System health metrics
- Audit logs and activity
- Performance statistics
- Security events

Respond in a helpful, professional manner and always explain what you're doing and why."""

    def _get_sales_system_prompt(self) -> str:
        """Get system prompt for sales AI agent"""
        return """You are an intelligent sales and revenue assistant for a gym management system called Gym Bot. Your role is to drive revenue growth and improve member relationships.

Key responsibilities:
- Managing marketing campaigns and member outreach
- Handling past due accounts and collections
- Creating and sending Square invoices
- Member retention and engagement
- Sales analytics and optimization
- Automated follow-up sequences

Important guidelines:
- Always maintain a professional, helpful tone in member communications
- Prioritize member experience while driving revenue
- Be persistent but respectful with collections
- Personalize communications based on member data
- Track and optimize campaign performance
- Escalate serious issues appropriately

Available data includes:
- Member profiles and payment history
- Past due accounts and amounts
- Campaign performance metrics
- Payment and billing information
- Member engagement data
- Training client information

Focus on building relationships while achieving revenue goals. Always explain your reasoning and provide actionable recommendations."""

    def get_or_create_context(self, session_id: str, user_id: str,
                            agent_type: str, initial_data: Dict[str, Any] = None) -> ConversationContext:
        """
        Get existing context or create new one

        Args:
            session_id: Unique session identifier
            user_id: User requesting the context
            agent_type: Type of AI agent ('admin' or 'sales')
            initial_data: Initial context data

        Returns:
            ConversationContext object
        """
        try:
            # Check if context exists and is still valid
            if session_id in self._active_contexts:
                context = self._active_contexts[session_id]
                if datetime.now() < context.expires_at:
                    # Update last accessed time
                    context.last_updated = datetime.now()
                    return context
                else:
                    # Context expired, remove it
                    del self._active_contexts[session_id]

            # Create new context
            now = datetime.now()
            context = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                agent_type=agent_type,
                context_data=initial_data or {},
                conversation_history=[],
                created_at=now,
                last_updated=now,
                expires_at=now + self._context_timeout
            )

            # Store in memory cache
            self._active_contexts[session_id] = context

            # TODO: Store in database for persistence
            # self._save_context_to_db(context)

            logger.info(f"✅ Created new AI context for {agent_type} agent (session: {session_id})")
            return context

        except Exception as e:
            logger.error(f"❌ Error creating AI context: {e}")
            raise

    def update_context_data(self, session_id: str, data: Dict[str, Any]):
        """Update context data for a session"""
        try:
            if session_id in self._active_contexts:
                context = self._active_contexts[session_id]
                context.context_data.update(data)
                context.last_updated = datetime.now()
                logger.debug(f"📝 Updated context data for session {session_id}")
            else:
                logger.warning(f"⚠️ Attempted to update non-existent context: {session_id}")

        except Exception as e:
            logger.error(f"❌ Error updating context data: {e}")

    def add_message_to_history(self, session_id: str, role: str, content: str):
        """Add message to conversation history"""
        try:
            if session_id in self._active_contexts:
                context = self._active_contexts[session_id]
                context.conversation_history.append({
                    'role': role,
                    'content': content,
                    'timestamp': datetime.now().isoformat()
                })

                # Limit history to last 20 messages to manage memory
                if len(context.conversation_history) > 20:
                    context.conversation_history = context.conversation_history[-20:]

                context.last_updated = datetime.now()
                logger.debug(f"💬 Added {role} message to session {session_id}")

        except Exception as e:
            logger.error(f"❌ Error adding message to history: {e}")

    def get_system_prompt(self, agent_type: str, context_data: Dict[str, Any] = None) -> str:
        """
        Get system prompt for agent type with optional context

        Args:
            agent_type: Type of agent ('admin' or 'sales')
            context_data: Additional context to include

        Returns:
            Complete system prompt
        """
        try:
            base_prompt = self._system_prompts.get(agent_type, "You are a helpful AI assistant.")

            if context_data:
                # Add relevant context information
                context_additions = []

                # Add current user info
                if 'current_user' in context_data:
                    user = context_data['current_user']
                    context_additions.append(f"Current user: {user.get('username', 'Unknown')} (ID: {user.get('manager_id', 'Unknown')})")

                # Add system stats for admin
                if agent_type == 'admin' and 'system_stats' in context_data:
                    stats = context_data['system_stats']
                    context_additions.append(f"System status: {stats.get('total_members', 0)} members, {stats.get('health_status', 'Unknown')} health")

                # Add sales context
                if agent_type == 'sales' and 'sales_context' in context_data:
                    sales = context_data['sales_context']
                    if 'past_due_count' in sales:
                        context_additions.append(f"Past due accounts: {sales['past_due_count']}")
                    if 'active_campaigns' in sales:
                        context_additions.append(f"Active campaigns: {sales['active_campaigns']}")

                if context_additions:
                    base_prompt += f"\n\nCurrent context:\n" + "\n".join(f"- {item}" for item in context_additions)

            return base_prompt

        except Exception as e:
            logger.error(f"❌ Error building system prompt: {e}")
            return self._system_prompts.get(agent_type, "You are a helpful AI assistant.")

    def get_conversation_messages(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation messages for API request

        Args:
            session_id: Session identifier

        Returns:
            List of messages formatted for AI API
        """
        try:
            if session_id not in self._active_contexts:
                return []

            context = self._active_contexts[session_id]
            # Return messages without timestamp for API
            return [
                {
                    'role': msg['role'],
                    'content': msg['content']
                }
                for msg in context.conversation_history
                if msg['role'] in ['user', 'assistant']
            ]

        except Exception as e:
            logger.error(f"❌ Error getting conversation messages: {e}")
            return []

    def cleanup_expired_contexts(self):
        """Remove expired contexts from memory"""
        try:
            now = datetime.now()
            expired_sessions = [
                session_id for session_id, context in self._active_contexts.items()
                if now >= context.expires_at
            ]

            for session_id in expired_sessions:
                del self._active_contexts[session_id]
                logger.debug(f"🧹 Cleaned up expired context: {session_id}")

            if expired_sessions:
                logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired AI contexts")

        except Exception as e:
            logger.error(f"❌ Error cleaning up contexts: {e}")

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active conversation sessions"""
        try:
            return [
                {
                    'session_id': context.session_id,
                    'user_id': context.user_id,
                    'agent_type': context.agent_type,
                    'created_at': context.created_at.isoformat(),
                    'last_updated': context.last_updated.isoformat(),
                    'expires_at': context.expires_at.isoformat(),
                    'message_count': len(context.conversation_history)
                }
                for context in self._active_contexts.values()
            ]

        except Exception as e:
            logger.error(f"❌ Error getting active sessions: {e}")
            return []

    def extend_session(self, session_id: str, hours: int = 2):
        """Extend session expiration time"""
        try:
            if session_id in self._active_contexts:
                context = self._active_contexts[session_id]
                context.expires_at = datetime.now() + timedelta(hours=hours)
                context.last_updated = datetime.now()
                logger.info(f"⏰ Extended session {session_id} by {hours} hours")

        except Exception as e:
            logger.error(f"❌ Error extending session: {e}")

    def close_session(self, session_id: str):
        """Close and remove a conversation session"""
        try:
            if session_id in self._active_contexts:
                del self._active_contexts[session_id]
                logger.info(f"🔒 Closed AI session: {session_id}")

        except Exception as e:
            logger.error(f"❌ Error closing session: {e}")