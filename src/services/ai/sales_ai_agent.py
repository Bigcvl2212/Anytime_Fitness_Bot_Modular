#!/usr/bin/env python3
"""
Sales AI Agent
Intelligent sales assistant for revenue generation, collections, and member engagement
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SalesAIAgent:
    """
    Intelligent AI agent for sales automation, collections, and member engagement
    """

    def __init__(self, ai_service_manager, context_manager, db_adapter,
                 campaign_service, square_client, messaging_client, db_manager):
        """
        Initialize Sales AI Agent

        Args:
            ai_service_manager: Core AI service for API calls
            context_manager: Context manager for conversations
            db_adapter: Database AI adapter for queries
            campaign_service: Campaign management service
            square_client: Square payment integration
            messaging_client: ClubOS messaging client
            db_manager: Database manager
        """
        self.ai_service = ai_service_manager
        self.context_manager = context_manager
        self.db_adapter = db_adapter
        self.campaign_service = campaign_service
        self.square_client = square_client
        self.messaging_client = messaging_client
        self.db_manager = db_manager

        # Sales command patterns
        self.command_patterns = {
            'collections': [
                r'(past due|overdue|collections?)',
                r'(invoice|billing|payment)',
                r'(send invoice|create invoice)',
                r'(follow up|reminder)',
                r'(payment status|balance)'
            ],
            'campaigns': [
                r'(campaign|marketing|outreach)',
                r'(send message|broadcast)',
                r'(start campaign|launch)',
                r'(campaign (status|performance))',
                r'(member engagement)'
            ],
            'analytics': [
                r'(revenue|sales|income)',
                r'(analytics|performance|metrics)',
                r'(conversion|retention)',
                r'(roi|return on investment)',
                r'(trends|patterns)'
            ],
            'member_management': [
                r'(member|client) (status|info)',
                r'(training (client|package))',
                r'(upgrade|upsell)',
                r'(retention|churn)',
                r'(member (engagement|activity))'
            ]
        }

    async def process_command(self, command: str, user_info: Dict[str, Any],
                            session_id: str = None) -> Dict[str, Any]:
        """
        Process natural language sales command

        Args:
            command: Natural language command
            user_info: User making the request
            session_id: Optional session ID for context

        Returns:
            Response with action results and recommendations
        """
        try:
            logger.info(f"🤖 Sales AI processing command: {command}")

            # Get or create conversation context
            if not session_id:
                session_id = f"sales_{user_info.get('manager_id', 'unknown')}_{int(datetime.now().timestamp())}"

            context = self.context_manager.get_or_create_context(
                session_id=session_id,
                user_id=user_info.get('manager_id', 'unknown'),
                agent_type='sales',
                initial_data={
                    'current_user': user_info,
                    'sales_context': await self._get_sales_context()
                }
            )

            # Add user message to conversation
            self.context_manager.add_message_to_history(session_id, 'user', command)

            # Determine command intent
            intent = self._analyze_sales_intent(command)

            # Process based on intent
            if intent['category'] == 'collections':
                result = await self._handle_collections(command, user_info, intent)
            elif intent['category'] == 'campaigns':
                result = await self._handle_campaigns(command, user_info, intent)
            elif intent['category'] == 'analytics':
                result = await self._handle_analytics(command, user_info, intent)
            elif intent['category'] == 'member_management':
                result = await self._handle_member_management(command, user_info, intent)
            else:
                # General sales conversation
                result = await self._handle_general_sales_conversation(command, session_id, context)

            # Add AI response to conversation
            if result.get('response'):
                self.context_manager.add_message_to_history(session_id, 'assistant', result['response'])

            return {
                'success': True,
                'session_id': session_id,
                'intent': intent,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error processing sales command: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command,
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_sales_intent(self, command: str) -> Dict[str, Any]:
        """Analyze command to determine sales intent"""
        try:
            command_lower = command.lower()

            for category, patterns in self.command_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, command_lower):
                        return {
                            'category': category,
                            'confidence': 'high',
                            'matched_pattern': pattern
                        }

            return {
                'category': 'general',
                'confidence': 'low',
                'matched_pattern': None
            }

        except Exception as e:
            logger.error(f"❌ Error analyzing sales intent: {e}")
            return {'category': 'general', 'confidence': 'low', 'matched_pattern': None}

    async def _handle_collections(self, command: str, user_info: Dict[str, Any],
                                intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collections and past due management"""
        try:
            logger.info("💰 Processing collections command")

            # Get past due data
            past_due_data = await self._get_past_due_members()

            # Use AI to understand specific collections action
            system_prompt = """You are a collections specialist for a gym. Analyze the command and determine:

1. What collections action is requested (list past due, send invoices, send reminders, etc.)
2. Any specific criteria or filters mentioned
3. Recommended approach for member communication

Available actions:
- list_past_due: Show past due members
- send_invoices: Create and send Square invoices
- send_reminders: Send payment reminder messages
- analyze_accounts: Analyze payment patterns
- priority_follow_up: Identify priority accounts

Return JSON with: {"action": "action_name", "criteria": {}, "response": "explanation"}"""

            user_message = f"""Command: {command}

Current Past Due Summary:
- Total past due members: {len(past_due_data)}
- Total amount: ${sum(m.get('amount_past_due', 0) for m in past_due_data):.2f}

Please analyze and recommend the best approach."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            if ai_response['success']:
                try:
                    parsed = json.loads(ai_response['response'])
                    action = parsed.get('action')
                    criteria = parsed.get('criteria', {})
                    response = parsed.get('response', '')

                    # Execute the collections action
                    action_result = await self._execute_collections_action(action, criteria, past_due_data)

                    return {
                        'response': response + '\n\n' + action_result.get('message', ''),
                        'action': action,
                        'data': action_result.get('data'),
                        'actionable': True
                    }

                except json.JSONDecodeError:
                    pass

            # Fallback response
            return {
                'response': f"Found {len(past_due_data)} past due members totaling ${sum(m.get('amount_past_due', 0) for m in past_due_data):.2f}. What would you like me to do?",
                'data': past_due_data[:10],  # Show first 10
                'actionable': True
            }

        except Exception as e:
            logger.error(f"❌ Error handling collections: {e}")
            return {'response': f"Error processing collections request: {str(e)}"}

    async def _handle_campaigns(self, command: str, user_info: Dict[str, Any],
                              intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle campaign management and messaging"""
        try:
            logger.info("📢 Processing campaign command")

            # Get campaign data
            campaign_data = await self._get_campaign_context()

            # Use AI to understand campaign action
            system_prompt = """You are a marketing specialist for a gym. Analyze the command and determine:

1. What campaign action is requested (create, launch, status, optimize, etc.)
2. Target audience or member segment
3. Message type and content suggestions
4. Timing and delivery preferences

Available actions:
- create_campaign: Create new marketing campaign
- launch_campaign: Start an existing campaign
- campaign_status: Check campaign performance
- optimize_message: Improve campaign messaging
- segment_members: Create targeted member lists

Return JSON with: {"action": "action_name", "details": {}, "response": "explanation"}"""

            user_message = f"""Command: {command}

Current Campaign Context:
{json.dumps(campaign_data, indent=2)}

Please analyze and recommend the best campaign approach."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            if ai_response['success']:
                try:
                    parsed = json.loads(ai_response['response'])
                    action = parsed.get('action')
                    details = parsed.get('details', {})
                    response = parsed.get('response', '')

                    # Execute campaign action
                    action_result = await self._execute_campaign_action(action, details)

                    return {
                        'response': response + '\n\n' + action_result.get('message', ''),
                        'action': action,
                        'data': action_result.get('data'),
                        'actionable': True
                    }

                except json.JSONDecodeError:
                    pass

            return {
                'response': ai_response['response'] if ai_response['success'] else "Campaign management tools are ready.",
                'data': campaign_data,
                'actionable': True
            }

        except Exception as e:
            logger.error(f"❌ Error handling campaigns: {e}")
            return {'response': f"Error processing campaign request: {str(e)}"}

    async def _handle_analytics(self, command: str, user_info: Dict[str, Any],
                              intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sales analytics and performance metrics"""
        try:
            logger.info("📊 Processing analytics command")

            # Get analytics data
            analytics_data = await self._get_analytics_context()

            # Use AI to generate analytics insights
            system_prompt = """You are a sales analyst for a gym. Provide insights on:

1. Revenue trends and patterns
2. Member acquisition and retention
3. Campaign performance
4. Payment collection efficiency
5. Growth opportunities

Focus on actionable recommendations."""

            user_message = f"""Command: {command}

Analytics Data:
{json.dumps(analytics_data, indent=2)}

Please provide sales analytics insights and recommendations."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            return {
                'response': ai_response['response'] if ai_response['success'] else "Analytics data analyzed.",
                'analytics_data': analytics_data,
                'insights_type': 'sales_analytics'
            }

        except Exception as e:
            logger.error(f"❌ Error handling analytics: {e}")
            return {'response': f"Error generating analytics: {str(e)}"}

    async def _handle_member_management(self, command: str, user_info: Dict[str, Any],
                                      intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle member management and engagement"""
        try:
            logger.info("👥 Processing member management command")

            # Process as database query if it looks like member lookup
            if any(keyword in command.lower() for keyword in ['show', 'find', 'list', 'member']):
                db_result = await self.db_adapter.process_natural_query(command)
                if db_result['success']:
                    return {
                        'response': db_result['interpretation'],
                        'query_result': db_result,
                        'data_type': 'member_query'
                    }

            # General member management response
            member_data = await self._get_member_context()

            system_prompt = """You are a member relations specialist. Provide insights on:

1. Member engagement and activity
2. Retention strategies
3. Upselling opportunities
4. Training package sales
5. Member satisfaction

Focus on revenue-generating recommendations."""

            user_message = f"""Command: {command}

Member Context:
{json.dumps(member_data, indent=2)}

Please provide member management insights."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            return {
                'response': ai_response['response'] if ai_response['success'] else "Member data analyzed.",
                'member_data': member_data,
                'actionable': True
            }

        except Exception as e:
            logger.error(f"❌ Error handling member management: {e}")
            return {'response': f"Error processing member request: {str(e)}"}

    async def _handle_general_sales_conversation(self, command: str, session_id: str,
                                               context) -> Dict[str, Any]:
        """Handle general sales AI conversation"""
        try:
            # Get system prompt with sales context
            system_prompt = self.context_manager.get_system_prompt(
                'sales',
                context.context_data
            )

            # Get conversation history
            conversation_messages = self.context_manager.get_conversation_messages(session_id)
            conversation_messages.append({"role": "user", "content": command})

            ai_response = await self.ai_service.send_message(conversation_messages, system_prompt)

            return {
                'response': ai_response['response'] if ai_response['success'] else "I'm here to help with sales and revenue.",
                'conversation_type': 'general_sales'
            }

        except Exception as e:
            logger.error(f"❌ Error in general sales conversation: {e}")
            return {'response': "I'm sorry, I encountered an error processing your request."}

    async def _execute_collections_action(self, action: str, criteria: Dict[str, Any],
                                        past_due_data: List[Dict]) -> Dict[str, Any]:
        """Execute specific collections action"""
        try:
            if action == 'list_past_due':
                # Filter and prioritize past due members
                sorted_members = sorted(past_due_data, key=lambda x: x.get('amount_past_due', 0), reverse=True)
                return {
                    'message': f"Prioritized list of {len(sorted_members)} past due members (highest amounts first).",
                    'data': sorted_members[:20]  # Top 20
                }

            elif action == 'send_invoices':
                # This would integrate with the existing Square invoice system
                eligible_members = [m for m in past_due_data if m.get('amount_past_due', 0) >= 25]
                return {
                    'message': f"Ready to send invoices to {len(eligible_members)} members. Would you like to proceed?",
                    'data': eligible_members,
                    'requires_confirmation': True
                }

            elif action == 'send_reminders':
                # This would integrate with the ClubOS messaging system
                return {
                    'message': f"Ready to send payment reminders to {len(past_due_data)} members via ClubOS messaging.",
                    'data': past_due_data,
                    'requires_confirmation': True
                }

            else:
                return {'message': f"Action '{action}' is ready to execute."}

        except Exception as e:
            logger.error(f"❌ Error executing collections action: {e}")
            return {'message': f"Error executing action: {str(e)}"}

    async def _execute_campaign_action(self, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific campaign action"""
        try:
            if action == 'create_campaign':
                return {
                    'message': "Campaign creation wizard ready. Please specify target audience and message content.",
                    'data': {'action': 'create_campaign', 'details': details}
                }

            elif action == 'campaign_status':
                # Get campaign status from existing service
                campaigns = ['good_standing', 'past_due_6_30', 'past_due_30_plus']
                status_data = []
                for campaign in campaigns:
                    status = self.campaign_service.get_campaign_status(campaign)
                    status_data.append({
                        'category': campaign,
                        'status': status.get('status', 'none'),
                        'progress': status.get('progress', 0)
                    })

                return {
                    'message': "Current campaign status retrieved.",
                    'data': status_data
                }

            else:
                return {'message': f"Campaign action '{action}' is ready to execute."}

        except Exception as e:
            logger.error(f"❌ Error executing campaign action: {e}")
            return {'message': f"Error executing campaign action: {str(e)}"}

    async def _get_sales_context(self) -> Dict[str, Any]:
        """Get sales-specific context data"""
        try:
            past_due_data = await self._get_past_due_members()
            return {
                'past_due_count': len(past_due_data),
                'total_past_due_amount': sum(m.get('amount_past_due', 0) for m in past_due_data),
                'active_campaigns': 'unknown'  # Would integrate with campaign service
            }
        except:
            return {}

    async def _get_past_due_members(self) -> List[Dict[str, Any]]:
        """Get list of past due members"""
        try:
            query = """
                SELECT prospect_id, first_name, last_name, email, mobile_phone,
                       amount_past_due, last_payment_date, status
                FROM members
                WHERE amount_past_due > 0
                ORDER BY amount_past_due DESC
                LIMIT 100
            """
            results = self.db_manager.execute_query(query, fetch_all=True)
            return [dict(row) for row in results] if results else []

        except Exception as e:
            logger.error(f"❌ Error getting past due members: {e}")
            return []

    async def _get_campaign_context(self) -> Dict[str, Any]:
        """Get campaign management context"""
        try:
            # This would integrate with existing campaign service
            return {
                'active_campaigns': 0,
                'scheduled_campaigns': 0,
                'last_campaign_date': 'unknown',
                'campaign_performance': 'unknown'
            }
        except:
            return {}

    async def _get_analytics_context(self) -> Dict[str, Any]:
        """Get sales analytics context"""
        try:
            # Basic revenue analytics from database
            return {
                'total_revenue': 'unknown',
                'monthly_growth': 'unknown',
                'collection_rate': 'unknown',
                'campaign_roi': 'unknown'
            }
        except:
            return {}

    async def _get_member_context(self) -> Dict[str, Any]:
        """Get member management context"""
        try:
            stats = self.db_adapter.get_quick_stats()
            return stats.get('stats', {}) if stats['success'] else {}
        except:
            return {}

    async def handle_past_due_clients(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle past due client management with AI optimization"""
        try:
            logger.info("🔍 AI handling past due clients")

            # Get past due data
            past_due_members = await self._get_past_due_members()

            # Apply filters if provided
            if filters:
                if 'min_amount' in filters:
                    past_due_members = [m for m in past_due_members if m.get('amount_past_due', 0) >= filters['min_amount']]

            # Use AI to prioritize and recommend actions
            system_prompt = """You are a collections specialist. Analyze past due accounts and recommend:

1. Priority order for collection efforts
2. Recommended communication approach for each account
3. Optimal timing for follow-ups
4. Invoice amounts and payment terms

Focus on maximizing collection success while maintaining member relationships."""

            user_message = f"""Past Due Analysis Request:
- Total accounts: {len(past_due_members)}
- Total amount: ${sum(m.get('amount_past_due', 0) for m in past_due_members):.2f}

Account Data (sample):
{json.dumps(past_due_members[:5], indent=2, default=str)}

Please provide prioritized recommendations."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            return {
                'success': True,
                'total_accounts': len(past_due_members),
                'total_amount': sum(m.get('amount_past_due', 0) for m in past_due_members),
                'ai_recommendations': ai_response['response'] if ai_response['success'] else '',
                'priority_accounts': past_due_members[:10],  # Top 10
                'suggested_actions': await self._generate_collection_actions(past_due_members)
            }

        except Exception as e:
            logger.error(f"❌ Error handling past due clients: {e}")
            return {'success': False, 'error': str(e)}

    async def _generate_collection_actions(self, past_due_members: List[Dict]) -> List[Dict]:
        """Generate AI-powered collection action recommendations"""
        try:
            actions = []

            for member in past_due_members[:5]:  # Top 5 priority
                amount = member.get('amount_past_due', 0)

                if amount >= 100:
                    actions.append({
                        'member_id': member.get('prospect_id'),
                        'member_name': f"{member.get('first_name', '')} {member.get('last_name', '')}",
                        'action': 'send_invoice',
                        'priority': 'high',
                        'recommended_approach': 'Immediate Square invoice with payment plan option'
                    })
                elif amount >= 50:
                    actions.append({
                        'member_id': member.get('prospect_id'),
                        'member_name': f"{member.get('first_name', '')} {member.get('last_name', '')}",
                        'action': 'send_reminder',
                        'priority': 'medium',
                        'recommended_approach': 'Friendly payment reminder via ClubOS'
                    })

            return actions

        except Exception as e:
            logger.error(f"❌ Error generating collection actions: {e}")
            return []