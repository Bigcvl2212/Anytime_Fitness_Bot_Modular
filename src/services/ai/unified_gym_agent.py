#!/usr/bin/env python3
"""
Unified Gym AI Agent
Combines Sales AI + Inbox AI into single autonomous system that:
- Monitors inbox in real-time
- Classifies message intent (Inbox AI)
- Injects member/payment context (Sales AI)
- Generates contextual responses
- Triggers workflows automatically
- Sends responses via ClubOS

Based on AUTONOMOUS_AI_AGENT_PLAN.md
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class UnifiedGymAgent:
    """
    Unified AI agent that combines Sales AI and Inbox AI capabilities
    into a single autonomous system for member communication and workflow automation
    """

    def __init__(
        self,
        sales_ai_agent,
        inbox_ai_agent,
        clubos_messaging_client,
        db_manager,
        workflow_runner=None
    ):
        """
        Initialize unified agent

        Args:
            sales_ai_agent: SalesAIAgent instance (revenue, collections, analytics)
            inbox_ai_agent: InboxAIAgent instance (message classification, responses)
            clubos_messaging_client: ClubOS client for sending messages
            db_manager: Database manager
            workflow_runner: Optional workflow runner for automatic triggers
        """
        self.sales_ai = sales_ai_agent
        self.inbox_ai = inbox_ai_agent
        self.clubos_client = clubos_messaging_client
        self.db_manager = db_manager
        self.workflow_runner = workflow_runner

        # Configuration
        self.auto_respond_enabled = True
        self.confidence_threshold = 0.80  # 80% confidence required
        self.max_auto_responses_per_hour = 50

        # Intent routing configuration
        self.sales_ai_intents = [
            'question_about_billing',
            'payment_inquiry',
            'invoice_question',
            'past_due_inquiry',
            'refund_request'
        ]

        self.workflow_trigger_intents = {
            'question_about_billing': 'collections_workflow',
            'payment_inquiry': 'collections_workflow',
            'past_due_inquiry': 'collections_workflow',
            'appointment_request': 'scheduling_workflow',
            'training_inquiry': 'training_upsell_workflow'
        }

        self.human_review_intents = [
            'complaint',
            'angry_customer',
            'refund_request',
            'cancel_request',
            'threatening_language'
        ]

        # Statistics
        self.stats = {
            'messages_processed': 0,
            'auto_responses_sent': 0,
            'workflows_triggered': 0,
            'human_reviews_flagged': 0,
            'last_response_time': None
        }

        logger.info("✅ Unified Gym AI Agent initialized")
        logger.info(f"📋 Sales AI intents: {self.sales_ai_intents}")
        logger.info(f"🎯 Workflow triggers: {list(self.workflow_trigger_intents.keys())}")
        logger.info(f"👤 Human review intents: {self.human_review_intents}")

    def _extract_name_from_content(self, content: str) -> Optional[str]:
        """
        Extract sender name from message content.
        ClubOS prepends sender name to content like "Jeremy MayoCan I setup an appointment?"
        The name typically appears at the start before the actual message.
        """
        if not content or len(content) < 5:
            return None
            
        import re
        
        # ClubOS format: "FirstName LastName" followed immediately by message (no space)
        # Examples:
        #   "Jeremy Mayocan I setup..." -> FirstName="Jeremy", LastName="Mayo"
        #   "Mary SiegmannOk otherwise" -> FirstName="Mary", LastName="Siegmann"
        
        # Strategy: Extract potential first word as first name,
        # then try different lengths for the last name
        words = content.split()
        if not words:
            return None
        
        first_word = words[0]
        
        # If first word is all lowercase or very short, not a name
        if first_word.islower() or len(first_word) < 2:
            return None
            
        # The second "word" might contain LastNameMessage (no space)
        # e.g., "Mayocan" = "Mayo" + "can"
        if len(words) >= 2:
            second_word = words[1]
            
            # Find where uppercase/titlecase ends and lowercase begins
            # This indicates where LastName ends and message begins
            # e.g., "Mayocan" -> split at transition from "o" to "c"? No...
            # Better: "MayoCan" -> split before "C"
            # But also: "Mayocan" -> need to find "Mayo" somehow
            
            # Try progressively longer substrings of second word as last name
            # Check each against database
            for last_name_len in range(len(second_word), 1, -1):
                potential_last_name = second_word[:last_name_len]
                potential_full_name = f"{first_word} {potential_last_name}"
                
                member_id = self._lookup_member_id_by_name_internal(potential_full_name)
                if member_id:
                    logger.info(f"📝 Extracted name '{potential_full_name}' from content")
                    return potential_full_name
            
            # Also try exact second word as last name (if there was a space)
            potential_full_name = f"{first_word} {second_word}"
            member_id = self._lookup_member_id_by_name_internal(potential_full_name)
            if member_id:
                logger.info(f"📝 Extracted name '{potential_full_name}' from content (exact)")
                return potential_full_name
        
        # Try just first word (single name)
        member_id = self._lookup_member_id_by_name_internal(first_word)
        if member_id:
            logger.info(f"📝 Extracted single name '{first_word}' from content")
            return first_word
            
        return None

    def _lookup_member_id_by_name_internal(self, name: str) -> Optional[str]:
        """Internal lookup - just checks database, no logging for failed lookups."""
        if not name or len(name) < 3:
            return None
            
        try:
            clean_name = name.strip()
            
            # Try members table - exact match on full_name
            result = self.db_manager.execute_query('''
                SELECT prospect_id, guid FROM members 
                WHERE LOWER(full_name) = LOWER(?) 
                   OR LOWER(first_name || ' ' || last_name) = LOWER(?)
                LIMIT 1
            ''', (clean_name, clean_name), fetch_one=True)
            
            if result:
                return result[0] or result[1]
            
            # Try partial match (first name + last name)
            name_parts = clean_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]
                
                result = self.db_manager.execute_query('''
                    SELECT prospect_id, guid FROM members 
                    WHERE LOWER(first_name) = LOWER(?) 
                      AND LOWER(last_name) = LOWER(?)
                    LIMIT 1
                ''', (first_name, last_name), fetch_one=True)
                
                if result:
                    return result[0] or result[1]
            
            # Try training_clients table
            result = self.db_manager.execute_query('''
                SELECT member_id FROM training_clients 
                WHERE LOWER(member_name) = LOWER(?)
                   OR LOWER(member_name) LIKE LOWER(?)
                LIMIT 1
            ''', (clean_name, f'%{clean_name}%'), fetch_one=True)
            
            if result and result[0]:
                return result[0]
            
            # Try prospects table
            result = self.db_manager.execute_query('''
                SELECT prospect_id FROM prospects 
                WHERE LOWER(full_name) = LOWER(?)
                   OR LOWER(first_name || ' ' || last_name) = LOWER(?)
                LIMIT 1
            ''', (clean_name, clean_name), fetch_one=True)
            
            if result and result[0]:
                return result[0]
                
            return None
            
        except Exception:
            return None

    def _lookup_member_id_by_name(self, sender_name: str, content: str = None) -> Optional[str]:
        """
        Look up member_id from sender's name in database.
        ClubOS messages often have sender name but no member_id.
        
        Args:
            sender_name: The from_user field from the message
            content: Message content (used to extract name if sender_name is Unknown)
            
        Returns:
            member_id (prospect_id) or None
        """
        member_id = None
        
        # Try direct lookup first if we have a valid name
        if sender_name and sender_name.lower() not in ['unknown', 'staff', 'admin', 'system', '']:
            member_id = self._lookup_member_id_by_name_internal(sender_name)
            if member_id:
                logger.info(f"✅ Found member_id {member_id} for '{sender_name}'")
                return member_id
        
        # If sender is Unknown or lookup failed, try extracting name from content
        if content and not member_id:
            extracted_name = self._extract_name_from_content(content)
            if extracted_name:
                member_id = self._lookup_member_id_by_name_internal(extracted_name)
                if member_id:
                    logger.info(f"✅ Found member_id {member_id} from content extraction '{extracted_name}'")
                    return member_id
        
        if sender_name and sender_name.lower() != 'unknown':
            logger.warning(f"⚠️ Could not find member_id for sender: '{sender_name}'")
        elif content:
            logger.warning(f"⚠️ Could not extract/find member from content: '{content[:50]}...'")
            
        return None

    async def process_new_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point - process new inbox message with full AI pipeline

        Args:
            message: ClubOS message dictionary

        Returns:
            Processing result with response details
        """
        try:
            message_id = message.get('id') or message.get('message_id')
            sender = message.get('from_user', 'Unknown')
            content = message.get('content', '')

            logger.info(f"🤖 Processing message from {sender}: {content[:60]}...")

            # CRITICAL: Ensure we have a member_id for sending responses
            # ClubOS messages often have sender name but no member_id
            # Pass BOTH sender and content so we can extract name from content if sender is Unknown
            member_id = message.get('member_id') or message.get('prospect_id')
            
            if not member_id:
                # Log what we're about to look up
                logger.info(f"🔍 Looking up member_id - sender='{sender}', content starts with: '{content[:30]}...'")
                member_id = self._lookup_member_id_by_name(sender, content)
                if member_id:
                    message['member_id'] = member_id  # Add to message for downstream use
                    # Log the resolved member for debugging
                    logger.info(f"📝 Resolved member_id: {member_id}")
                    # Verify this is the RIGHT member by checking the name
                    verify_result = self.db_manager.execute_query(
                        'SELECT full_name FROM members WHERE prospect_id = ? LIMIT 1',
                        (member_id,), fetch_one=True
                    )
                    if verify_result:
                        resolved_name = verify_result[0] if not isinstance(verify_result, dict) else verify_result.get('full_name')
                        logger.info(f"✅ WILL SEND RESPONSE TO: {resolved_name} (ID: {member_id})")

            # Step 1: Classify message intent (Inbox AI)
            intent, confidence = await self.inbox_ai.classify_intent(content)
            logger.info(f"📊 Intent: {intent} (confidence: {confidence:.2f})")

            # Step 2: Get member context if needed
            member_context = await self._get_member_context(message, intent)

            # Step 3: Route to appropriate handler
            result = await self._route_message(message, intent, confidence, member_context)

            # Update statistics
            self.stats['messages_processed'] += 1
            if result.get('responded'):
                self.stats['auto_responses_sent'] += 1
                self.stats['last_response_time'] = datetime.now().isoformat()
            if result.get('workflow_triggered'):
                self.stats['workflows_triggered'] += 1
            if result.get('flagged_for_review'):
                self.stats['human_reviews_flagged'] += 1

            # Log to database
            await self._log_ai_action(message, intent, confidence, result)

            return result

        except Exception as e:
            logger.error(f"❌ Error processing message {message.get('id')}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message_id': message.get('id')
            }

    async def _get_member_context(self, message: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Get member data from Sales AI for contextual responses

        Args:
            message: Message dict
            intent: Classified intent

        Returns:
            Member context dict
        """
        try:
            # Extract member ID from message
            member_id = message.get('member_id') or message.get('prospect_id')

            if not member_id:
                logger.debug("⚠️ No member ID found in message")
                return {}

            # Get member data from database (using actual columns that exist)
            member_data = self.db_manager.execute_query('''
                SELECT
                    prospect_id, full_name, email, mobile_phone,
                    status_message, status, amount_past_due,
                    date_of_next_payment, agreement_type
                FROM members
                WHERE prospect_id = ? OR guid = ?
                LIMIT 1
            ''', (member_id, member_id), fetch_one=True)  # FIXED: use fetch_one=True

            if not member_data:
                logger.debug(f"⚠️ No member data found for ID: {member_id}")
                return {}

            # Convert to dict if needed
            if not isinstance(member_data, dict):
                member_data = dict(member_data)

            # Derive payment_status from amount_past_due
            past_due = float(member_data.get('amount_past_due') or 0)
            member_data['payment_status'] = 'Past Due' if past_due > 0 else 'Current'
            member_data['past_due_amount'] = past_due

            # Get training client data if exists
            training_data = self.db_manager.execute_query('''
                SELECT
                    status_message, last_session_date
                FROM training_clients
                WHERE clubos_member_id = ?
                LIMIT 1
            ''', (member_id,), fetch_one=True)  # FIXED: use fetch_one=True

            if training_data:
                member_data['training'] = dict(training_data) if not isinstance(training_data, dict) else training_data

            logger.info(f"✅ Loaded context for member: {member_data.get('full_name')}")

            # Add financial context if billing-related intent
            if intent in self.sales_ai_intents:
                member_data['is_past_due'] = past_due > 0

            return member_data

        except Exception as e:
            logger.error(f"❌ Error getting member context: {e}")
            return {}

    async def _route_message(
        self,
        message: Dict[str, Any],
        intent: str,
        confidence: float,
        member_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route message to appropriate handler based on intent

        Args:
            message: Message dict
            intent: Classified intent
            confidence: Classification confidence
            member_context: Member data

        Returns:
            Processing result
        """
        # Check if human review required
        if intent in self.human_review_intents:
            return await self._flag_for_human_review(message, intent, member_context)

        # Check confidence threshold
        if confidence < self.confidence_threshold:
            logger.info(f"⚠️ Low confidence ({confidence:.2f}), flagging for review")
            return await self._flag_for_human_review(message, intent, member_context, reason="low_confidence")

        # Route to Sales AI if billing/collections related
        if intent in self.sales_ai_intents:
            return await self._handle_billing_inquiry(message, intent, member_context)

        # Trigger workflow if configured
        if intent in self.workflow_trigger_intents and self.workflow_runner:
            return await self._trigger_workflow(message, intent, member_context)

        # Default: Generate general response via Inbox AI
        return await self._handle_general_inquiry(message, intent, member_context)

    async def _handle_billing_inquiry(
        self,
        message: Dict[str, Any],
        intent: str,
        member_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle billing-related inquiries with Sales AI context

        This is the CORE integration point: Inbox message + Sales context
        """
        try:
            sender = message.get('from_user', 'Unknown')
            content = message.get('content', '')

            logger.info(f"💰 Handling billing inquiry from {sender}")

            # Build context-aware prompt
            system_prompt = self._build_billing_response_prompt(member_context)

            # Generate response using AI service
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Member message: {content}"}
            ]

            ai_result = await self.sales_ai.ai_service.send_message(messages)

            if not ai_result or 'response' not in ai_result:
                raise Exception("Failed to generate AI response")

            response_text = ai_result['response']

            # Send response via ClubOS
            if self.auto_respond_enabled:
                member_id = message.get('member_id') or message.get('prospect_id')
                # CRITICAL: Pass member_context for proper ClubOS delegation
                send_result = await self._send_response(member_id, response_text, member_context)

                if send_result:
                    logger.info(f"✅ Sent billing response to {sender}")

                    # Trigger collections workflow if past due > $50
                    workflow_triggered = False
                    if member_context.get('past_due_amount', 0) > 50:
                        workflow_triggered = await self._trigger_collections_workflow(member_context)

                    return {
                        'success': True,
                        'responded': True,
                        'intent': intent,
                        'response': response_text,
                        'workflow_triggered': workflow_triggered,
                        'timestamp': datetime.now().isoformat()
                    }

            return {
                'success': True,
                'responded': False,
                'intent': intent,
                'response': response_text,
                'reason': 'auto_respond_disabled',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error handling billing inquiry: {e}")
            return {'success': False, 'error': str(e)}

    def _build_billing_response_prompt(self, member_context: Dict[str, Any]) -> str:
        """Build system prompt with member billing context"""
        prompt = f"""You are a friendly gym staff member handling a billing inquiry.

Member Context:
- Name: {member_context.get('full_name', 'Unknown')}
- Status: {member_context.get('payment_status', 'Unknown')}
"""

        # Add past due context if applicable
        if member_context.get('is_past_due'):
            past_due_amount = member_context.get('past_due_amount', 0)
            prompt += f"""- Past Due Amount: ${past_due_amount:.2f}
- Account Status: Payment overdue

IMPORTANT: The member has a past due balance. Be friendly but clear about the outstanding amount.
Offer to help them set up a payment or update their payment method."""
        else:
            prompt += "- Account Status: Current (no past due amount)\n"

        prompt += """
Guidelines:
- Be friendly, professional, and helpful
- Answer their specific billing question
- If they have a past due balance, gently remind them and offer assistance
- Keep response concise (2-3 sentences)
- Don't make promises you can't keep (like waiving fees)
- If question requires manual review, acknowledge and say a manager will follow up
"""

        return prompt

    async def _handle_general_inquiry(
        self,
        message: Dict[str, Any],
        intent: str,
        member_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general inquiries using Inbox AI"""
        try:
            # Use Inbox AI to generate response
            content = message.get('content', '')
            
            # CRITICAL: Add resolved member name to message data for AI personalization
            # This ensures the AI addresses the RIGHT person, not someone mentioned in the message
            message_with_context = message.copy()
            if member_context and member_context.get('full_name'):
                message_with_context['resolved_member_name'] = member_context.get('full_name')
                logger.info(f"📝 Using resolved member name for AI: {member_context.get('full_name')}")
            
            response = await self.inbox_ai.generate_response(content, intent, message_with_context)

            if response and self.auto_respond_enabled:
                member_id = message.get('member_id') or message.get('prospect_id')
                # CRITICAL: Pass member_context to _send_response for proper ClubOS delegation
                send_result = await self._send_response(member_id, response, member_context)

                return {
                    'success': True,
                    'responded': send_result,
                    'intent': intent,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }

            return {
                'success': True,
                'responded': False,
                'response': response,
                'intent': intent,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error handling general inquiry: {e}")
            return {'success': False, 'error': str(e)}

    async def _trigger_workflow(
        self,
        message: Dict[str, Any],
        intent: str,
        member_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger configured workflow based on intent"""
        try:
            workflow_name = self.workflow_trigger_intents.get(intent)

            if not workflow_name or not self.workflow_runner:
                return await self._handle_general_inquiry(message, intent, member_context)

            logger.info(f"🎯 Triggering workflow: {workflow_name}")

            # Trigger the workflow
            workflow_result = await self.workflow_runner.trigger_workflow(
                workflow_name=workflow_name,
                trigger_data={
                    'message': message,
                    'intent': intent,
                    'member_context': member_context
                }
            )

            # Also send immediate response
            response_result = await self._handle_general_inquiry(message, intent, member_context)

            return {
                **response_result,
                'workflow_triggered': True,
                'workflow_name': workflow_name,
                'workflow_result': workflow_result
            }

        except Exception as e:
            logger.error(f"❌ Error triggering workflow: {e}")
            return {'success': False, 'error': str(e)}

    async def _trigger_collections_workflow(self, member_context: Dict[str, Any]) -> bool:
        """Trigger collections workflow for past due member"""
        try:
            if not self.workflow_runner:
                logger.debug("⚠️ No workflow runner configured")
                return False

            logger.info(f"🎯 Triggering collections workflow for {member_context.get('full_name')}")

            result = await self.workflow_runner.trigger_workflow(
                workflow_name='collections_workflow',
                trigger_data={
                    'member_id': member_context.get('prospect_id'),
                    'past_due_amount': member_context.get('past_due_amount', 0),
                    'trigger': 'inbox_billing_inquiry'
                }
            )

            return result.get('success', False)

        except Exception as e:
            logger.error(f"❌ Error triggering collections workflow: {e}")
            return False

    async def _flag_for_human_review(
        self,
        message: Dict[str, Any],
        intent: str,
        member_context: Dict[str, Any],
        reason: str = "sensitive_intent"
    ) -> Dict[str, Any]:
        """Flag message for human review instead of auto-responding"""
        try:
            logger.info(f"🚩 Flagging message for human review: {reason}")

            # Update message in database with review flag
            message_id = message.get('id') or message.get('message_id')

            self.db_manager.execute_query('''
                UPDATE messages
                SET requires_human_review = 1,
                    review_reason = ?
                WHERE id = ?
            ''', (reason, message_id))

            # TODO: Send notification to manager (Phase 4)

            return {
                'success': True,
                'responded': False,
                'flagged_for_review': True,
                'reason': reason,
                'intent': intent,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error flagging for review: {e}")
            return {'success': False, 'error': str(e)}

    async def _send_response(self, member_id: str, response_text: str, member_data: Dict[str, Any] = None) -> bool:
        """Send response to member via ClubOS
        
        Args:
            member_id: The prospect/member ID
            response_text: The message to send
            member_data: Member context dict with full_name etc. for proper ClubOS delegation
        """
        try:
            if not member_id:
                logger.error("❌ Cannot send response - no member_id provided")
                return False
                
            if not response_text:
                logger.error("❌ Cannot send response - no response text provided")
                return False
            
            # CRITICAL: Pass member_data so send_message can properly delegate
            # This matches the campaign code that works correctly
            logger.info(f"📤 Sending response to member_id={member_id}, name={member_data.get('full_name') if member_data else 'Unknown'}")
            
            result = self.clubos_client.send_message(
                member_id=member_id,
                message_text=response_text,
                channel="sms",
                member_data=member_data  # CRITICAL: Pass member data for proper delegation
            )
            
            if result:
                logger.info(f"✅ Successfully sent response to member {member_id}")
            else:
                logger.error(f"❌ Failed to send response to member {member_id}")

            return result

        except Exception as e:
            logger.error(f"❌ Error sending response: {e}")
            return False

    async def _log_ai_action(
        self,
        message: Dict[str, Any],
        intent: str,
        confidence: float,
        result: Dict[str, Any]
    ) -> None:
        """Log AI action to database for audit trail"""
        try:
            self.db_manager.execute_query('''
                INSERT INTO ai_response_log (
                    id, message_id, member_id, intent, confidence,
                    response_sent, sent_at, workflow_triggered, auto_sent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"ai_{int(datetime.now().timestamp())}_{message.get('id', 'unknown')}",
                message.get('id'),
                message.get('member_id'),
                intent,
                confidence,
                result.get('response', ''),
                datetime.now().isoformat() if result.get('responded') else None,
                result.get('workflow_triggered', False),
                result.get('responded', False)
            ))

        except Exception as e:
            logger.debug(f"⚠️ Could not log AI action: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get unified agent statistics"""
        return {
            **self.stats,
            'auto_respond_enabled': self.auto_respond_enabled,
            'confidence_threshold': self.confidence_threshold,
            'max_auto_responses_per_hour': self.max_auto_responses_per_hour
        }

    def enable_auto_response(self, enabled: bool = True):
        """Enable/disable automatic responses"""
        self.auto_respond_enabled = enabled
        logger.info(f"{'✅ Enabled' if enabled else '❌ Disabled'} automatic responses")

    def set_confidence_threshold(self, threshold: float):
        """Set minimum confidence threshold for auto-responses"""
        self.confidence_threshold = threshold
        logger.info(f"📊 Set confidence threshold to {threshold:.2f}")
