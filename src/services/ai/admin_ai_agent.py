#!/usr/bin/env python3
"""
Admin AI Agent
Intelligent administrative assistant for system management and automation
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AdminAIAgent:
    """
    Intelligent AI agent for administrative tasks and system management
    """

    def __init__(self, ai_service_manager, context_manager, db_adapter, admin_service):
        """
        Initialize Admin AI Agent

        Args:
            ai_service_manager: Core AI service for API calls
            context_manager: Context manager for conversations
            db_adapter: Database AI adapter for queries
            admin_service: Admin service for system operations
        """
        self.ai_service = ai_service_manager
        self.context_manager = context_manager
        self.db_adapter = db_adapter
        self.admin_service = admin_service

        # Command patterns for quick recognition
        self.command_patterns = {
            'user_management': [
                r'(create|add|new) (user|admin)',
                r'(delete|remove) (user|admin)',
                r'(list|show|display) (users?|admins?)',
                r'(edit|modify|update) (user|admin)',
                r'(lock|unlock|activate|deactivate) (user|admin)'
            ],
            'system_monitoring': [
                r'(system|health) (status|check)',
                r'(performance|metrics|stats)',
                r'(errors?|issues?|problems?)',
                r'(database|db) (status|health)',
                r'(cache|memory) (clear|status)'
            ],
            'security_analysis': [
                r'(security|audit) (report|log)',
                r'(login|access) (attempts?|failures?)',
                r'(suspicious|unusual) (activity|behavior)',
                r'(permissions?|roles?|access)',
                r'(vulnerabilities?|threats?)'
            ],
            'data_insights': [
                r'(analytics?|insights?|trends?)',
                r'(members?|users?) (statistics?|stats?)',
                r'(revenue|financial|billing)',
                r'(activity|usage) (patterns?|data)',
                r'(generate|create) (report|summary)'
            ]
        }

    async def process_command(self, command: str, admin_user: Dict[str, Any],
                            session_id: str = None) -> Dict[str, Any]:
        """
        Process natural language admin command

        Args:
            command: Natural language command from admin
            admin_user: Admin user making the request
            session_id: Optional session ID for context

        Returns:
            Response with action results and recommendations
        """
        try:
            logger.info(f"🤖 Admin AI processing command: {command}")

            # Get or create conversation context
            if not session_id:
                session_id = f"admin_{admin_user['manager_id']}_{int(datetime.now().timestamp())}"

            context = self.context_manager.get_or_create_context(
                session_id=session_id,
                user_id=admin_user['manager_id'],
                agent_type='admin',
                initial_data={
                    'current_user': admin_user,
                    'system_stats': await self._get_system_context()
                }
            )

            # Add user message to conversation
            self.context_manager.add_message_to_history(session_id, 'user', command)

            # Determine command category and intent
            intent = self._analyze_command_intent(command)

            # Process based on intent
            if intent['category'] == 'user_management':
                result = await self._handle_user_management(command, admin_user, intent)
            elif intent['category'] == 'system_monitoring':
                result = await self._handle_system_monitoring(command, admin_user, intent)
            elif intent['category'] == 'security_analysis':
                result = await self._handle_security_analysis(command, admin_user, intent)
            elif intent['category'] == 'data_insights':
                result = await self._handle_data_insights(command, admin_user, intent)
            else:
                # General AI conversation
                result = await self._handle_general_conversation(command, session_id, context)

            # Add AI response to conversation
            if result.get('response'):
                self.context_manager.add_message_to_history(session_id, 'assistant', result['response'])

            # Log admin action
            self._log_ai_action(admin_user['manager_id'], command, result)

            return {
                'success': True,
                'session_id': session_id,
                'intent': intent,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error processing admin command: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command,
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_command_intent(self, command: str) -> Dict[str, Any]:
        """Analyze command to determine intent and category"""
        try:
            command_lower = command.lower()

            # Check against patterns
            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, command_lower):
                        return {
                            'category': category,
                            'confidence': 'high',
                            'matched_pattern': pattern
                        }

            # Fallback to general conversation
            return {
                'category': 'general',
                'confidence': 'low',
                'matched_pattern': None
            }

        except Exception as e:
            logger.error(f"❌ Error analyzing command intent: {e}")
            return {'category': 'general', 'confidence': 'low', 'matched_pattern': None}

    async def _handle_user_management(self, command: str, admin_user: Dict[str, Any],
                                    intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user management commands"""
        try:
            logger.info("👥 Processing user management command")

            # Use AI to understand specific user management action
            system_prompt = """You are an admin assistant for user management. Analyze the command and determine:
1. What specific action is requested (list, create, edit, delete, etc.)
2. What user details are provided (username, email, permissions)
3. What response should be given

Return JSON with: {"action": "action_name", "details": {}, "response": "natural_language_response"}

Available actions: list_users, create_user, edit_user, delete_user, reset_access, show_permissions"""

            messages = [
                {
                    "role": "user",
                    "content": f"Command: {command}\nCurrent admin: {admin_user['username']}"
                }
            ]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            if not ai_response['success']:
                return {'response': "I'm sorry, I couldn't process that user management command."}

            try:
                parsed = json.loads(ai_response['response'])
                action = parsed.get('action')
                details = parsed.get('details', {})
                response = parsed.get('response', '')

                # Execute the requested action
                if action == 'list_users':
                    users = self.admin_service.admin_schema.get_all_admin_users()
                    response += f"\n\nFound {len(users)} admin users:"
                    for user in users[:10]:  # Limit to 10 for display
                        status = "Active" if user.get('is_active') else "Inactive"
                        role = "Super Admin" if user.get('is_super_admin') else "Admin"
                        response += f"\n• {user['username']} ({user['email']}) - {role}, {status}"

                elif action == 'show_permissions':
                    # Get admin permissions info
                    permissions = self.admin_service.get_admin_permissions(admin_user['manager_id'])
                    response += f"\n\nYour current permissions:"
                    for perm, value in permissions.items():
                        if value:
                            response += f"\n• {perm.replace('_', ' ').title()}"

                return {
                    'action': action,
                    'details': details,
                    'response': response,
                    'actionable': action in ['create_user', 'edit_user', 'delete_user']
                }

            except json.JSONDecodeError:
                return {'response': ai_response['response']}

        except Exception as e:
            logger.error(f"❌ Error handling user management: {e}")
            return {'response': f"Error processing user management command: {str(e)}"}

    async def _handle_system_monitoring(self, command: str, admin_user: Dict[str, Any],
                                      intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system monitoring and health commands"""
        try:
            logger.info("🔧 Processing system monitoring command")

            # Get current system stats
            system_stats = await self._get_detailed_system_stats()

            # Use AI to generate monitoring response
            system_prompt = """You are a system monitoring assistant. Analyze system data and provide insights.

Focus on:
- System health and performance
- Database status and connectivity
- Service availability
- Performance metrics
- Recommendations for improvements

Provide clear, actionable information."""

            user_message = f"""Command: {command}

Current System Status:
{json.dumps(system_stats, indent=2)}

Please provide a comprehensive system analysis and any recommendations."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            if ai_response['success']:
                response = ai_response['response']
            else:
                response = "System monitoring data retrieved. See details below."

            return {
                'response': response,
                'system_data': system_stats,
                'health_score': self._calculate_health_score(system_stats)
            }

        except Exception as e:
            logger.error(f"❌ Error handling system monitoring: {e}")
            return {'response': f"Error retrieving system monitoring data: {str(e)}"}

    async def _handle_security_analysis(self, command: str, admin_user: Dict[str, Any],
                                      intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security analysis and audit commands"""
        try:
            logger.info("🔒 Processing security analysis command")

            # Get security-related data
            security_data = await self._get_security_context()

            # Use AI to analyze security data
            system_prompt = """You are a security analyst for a gym management system. Analyze security data and provide:

1. Security assessment and risk analysis
2. Unusual activity patterns
3. Recommended security improvements
4. Compliance status

Focus on actionable security insights."""

            user_message = f"""Command: {command}

Security Data:
{json.dumps(security_data, indent=2)}

Please provide a security analysis and recommendations."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            return {
                'response': ai_response['response'] if ai_response['success'] else "Security analysis completed.",
                'security_data': security_data,
                'risk_level': self._assess_security_risk(security_data)
            }

        except Exception as e:
            logger.error(f"❌ Error handling security analysis: {e}")
            return {'response': f"Error performing security analysis: {str(e)}"}

    async def _handle_data_insights(self, command: str, admin_user: Dict[str, Any],
                                  intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data insights and analytics commands"""
        try:
            logger.info("📊 Processing data insights command")

            # Try to process as database query first
            db_result = await self.db_adapter.process_natural_query(command)

            if db_result['success']:
                return {
                    'response': db_result['interpretation'],
                    'query_result': db_result,
                    'data_type': 'database_query'
                }
            else:
                # Generate general insights
                insights_data = await self._get_insights_context()

                system_prompt = """You are a data analyst for a gym management system. Provide insights based on available data.

Focus on:
- Member trends and patterns
- Revenue analysis
- Operational efficiency
- Growth opportunities
- Data-driven recommendations"""

                user_message = f"""Command: {command}

Available Data Summary:
{json.dumps(insights_data, indent=2)}

Please provide relevant insights and recommendations."""

                messages = [{"role": "user", "content": user_message}]

                ai_response = await self.ai_service.send_message(messages, system_prompt)

                return {
                    'response': ai_response['response'] if ai_response['success'] else "Data insights generated.",
                    'insights_data': insights_data,
                    'data_type': 'general_insights'
                }

        except Exception as e:
            logger.error(f"❌ Error handling data insights: {e}")
            return {'response': f"Error generating data insights: {str(e)}"}

    async def _handle_general_conversation(self, command: str, session_id: str,
                                         context) -> Dict[str, Any]:
        """Handle general AI conversation"""
        try:
            # Get system prompt with context
            system_prompt = self.context_manager.get_system_prompt(
                'admin',
                context.context_data
            )

            # Get conversation history
            conversation_messages = self.context_manager.get_conversation_messages(session_id)

            # Add current message
            conversation_messages.append({"role": "user", "content": command})

            ai_response = await self.ai_service.send_message(conversation_messages, system_prompt)

            return {
                'response': ai_response['response'] if ai_response['success'] else "I'm here to help with admin tasks.",
                'conversation_type': 'general'
            }

        except Exception as e:
            logger.error(f"❌ Error in general conversation: {e}")
            return {'response': "I'm sorry, I encountered an error processing your request."}

    async def _get_system_context(self) -> Dict[str, Any]:
        """Get basic system context for AI"""
        try:
            stats = self.db_adapter.get_quick_stats()
            return stats.get('stats', {}) if stats['success'] else {}
        except:
            return {}

    async def _get_detailed_system_stats(self) -> Dict[str, Any]:
        """Get detailed system statistics"""
        try:
            # This would integrate with existing monitoring
            return {
                'database_health': 'healthy',
                'api_status': 'operational',
                'cache_status': 'active',
                'last_backup': 'unknown',
                'uptime': 'unknown'
            }
        except Exception as e:
            logger.error(f"❌ Error getting system stats: {e}")
            return {}

    async def _get_security_context(self) -> Dict[str, Any]:
        """Get security-related context"""
        try:
            # Get recent audit logs and security events
            return {
                'recent_logins': 'data_placeholder',
                'failed_attempts': 'data_placeholder',
                'permission_changes': 'data_placeholder'
            }
        except Exception as e:
            logger.error(f"❌ Error getting security context: {e}")
            return {}

    async def _get_insights_context(self) -> Dict[str, Any]:
        """Get data insights context"""
        try:
            stats = self.db_adapter.get_quick_stats()
            return stats.get('stats', {}) if stats['success'] else {}
        except:
            return {}

    def _calculate_health_score(self, system_stats: Dict[str, Any]) -> int:
        """Calculate overall system health score (0-100)"""
        # Simple health scoring logic
        return 85  # Placeholder

    def _assess_security_risk(self, security_data: Dict[str, Any]) -> str:
        """Assess security risk level"""
        # Simple risk assessment
        return 'low'  # Placeholder

    def _log_ai_action(self, admin_id: str, command: str, result: Dict[str, Any]):
        """Log AI action to audit trail"""
        try:
            self.admin_service.log_admin_action(
                admin_id, 'ai_command',
                f'AI Assistant: {command[:100]}',
                'ai_agent', 'admin_ai',
                success=result.get('success', True)
            )
        except Exception as e:
            logger.error(f"❌ Error logging AI action: {e}")

    async def generate_insights(self, data_type: str, admin_user: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights for specific data types"""
        try:
            if data_type == 'system_health':
                return await self._generate_system_insights(admin_user)
            elif data_type == 'security':
                return await self._generate_security_insights(admin_user)
            elif data_type == 'user_activity':
                return await self._generate_user_insights(admin_user)
            else:
                return {'error': f'Unknown data type: {data_type}'}

        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            return {'error': str(e)}

    async def suggest_actions(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest admin actions based on current context"""
        try:
            suggestions = []

            # Add context-based suggestions
            if context.get('system_issues'):
                suggestions.append({
                    'action': 'run_health_check',
                    'description': 'Run comprehensive system health check',
                    'priority': 'high'
                })

            if context.get('security_alerts'):
                suggestions.append({
                    'action': 'review_security',
                    'description': 'Review recent security events',
                    'priority': 'medium'
                })

            # Always suggest regular maintenance
            suggestions.append({
                'action': 'maintenance_check',
                'description': 'Perform routine system maintenance',
                'priority': 'low'
            })

            return suggestions

        except Exception as e:
            logger.error(f"❌ Error generating action suggestions: {e}")
            return []