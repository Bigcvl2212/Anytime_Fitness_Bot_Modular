#!/usr/bin/env python3
"""
Inbox AI Agent
Autonomous AI agent for processing ClubOS inbox messages and generating auto-responses
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class InboxAIAgent:
    """
    AI agent for inbox message processing and auto-response generation
    Integrates with AIServiceManager for Claude API access
    """

    def __init__(self, ai_service_manager, clubos_client, inbox_db_schema):
        """
        Initialize AI agent

        Args:
            ai_service_manager: AIServiceManager instance
            clubos_client: ClubOSMessagingClient instance
            inbox_db_schema: InboxDatabaseSchema instance
        """
        self.ai_service = ai_service_manager
        self.clubos_client = clubos_client
        self.inbox_db = inbox_db_schema

        # AI configuration
        self.auto_response_enabled = True
        self.confidence_threshold = 0.7  # Minimum confidence to auto-respond
        self.max_responses_per_hour = 20  # Rate limiting

        # Intent classification categories
        self.intent_categories = [
            'question_about_membership',
            'question_about_training',
            'question_about_billing',
            'question_about_schedule',
            'appointment_request',
            'appointment_cancellation',
            'complaint',
            'praise',
            'general_inquiry',
            'spam',
            'requires_human_response'
        ]

    async def process_new_messages(self, messages: List[Dict]):
        """
        Process new messages and generate AI responses if appropriate

        Args:
            messages: List of new message dictionaries
        """
        logger.info(f"🤖 AI Agent processing {len(messages)} new messages")

        for message in messages:
            try:
                await self.process_single_message(message)
            except Exception as e:
                logger.error(f"❌ Error processing message {message.get('id')}: {e}")

    async def process_single_message(self, message: Dict):
        """
        Process a single message and generate response if appropriate

        Args:
            message: Message dictionary
        """
        try:
            message_id = message.get('id') or message.get('message_id')
            sender_name = message.get('sender_name', 'Unknown')
            content = message.get('content') or message.get('snippet', '')

            logger.info(f"🔍 Analyzing message from {sender_name}: {content[:50]}...")

            # Step 1: Classify intent
            intent, confidence = await self.classify_intent(content)
            logger.info(f"📊 Intent: {intent} (confidence: {confidence:.2f})")

            # Step 2: Decide if auto-response is appropriate
            should_respond = self.should_auto_respond(intent, confidence)

            if not should_respond:
                logger.info(f"⏭️ Skipping auto-response for message {message_id}")
                return

            # Step 3: Generate response
            ai_response = await self.generate_response(content, intent, message)

            if not ai_response:
                logger.warning(f"⚠️ Failed to generate response for message {message_id}")
                return

            # Step 4: Send response via ClubOS
            success = await self.send_response(message, ai_response)

            # Step 5: Log the AI response
            await self.log_ai_response(
                original_message_id=message_id,
                conversation_id=message.get('conversation_id'),
                member_id=message.get('sender_id'),
                member_name=sender_name,
                ai_response=ai_response,
                ai_intent=intent,
                ai_confidence=confidence,
                sent_successfully=success
            )

            if success:
                logger.info(f"✅ AI auto-response sent successfully to {sender_name}")
            else:
                logger.warning(f"⚠️ Failed to send AI response to {sender_name}")

        except Exception as e:
            logger.error(f"❌ Error in process_single_message: {e}")

    async def classify_intent(self, message_content: str) -> Tuple[str, float]:
        """
        Classify message intent using AI

        Args:
            message_content: Message text

        Returns:
            Tuple of (intent, confidence_score)
        """
        try:
            system_prompt = f"""You are an AI assistant helping classify gym member messages.
Analyze the message and classify it into one of these categories:
{', '.join(self.intent_categories)}

Respond with a JSON object containing:
- intent: the category name
- confidence: a score from 0.0 to 1.0
- reasoning: brief explanation

Example response:
{{"intent": "question_about_billing", "confidence": 0.85, "reasoning": "Member asking about payment status"}}
"""

            messages = [{
                "role": "user",
                "content": f"Classify this message:\n\n{message_content}"
            }]

            result = await self.ai_service.send_message(messages, system_prompt)

            if result['success']:
                response_text = result['response']
                # Parse JSON response
                try:
                    classification = json.loads(response_text)
                    intent = classification.get('intent', 'general_inquiry')
                    confidence = float(classification.get('confidence', 0.5))
                    return intent, confidence
                except json.JSONDecodeError:
                    # Fallback parsing
                    logger.warning("Failed to parse JSON response, using fallback")
                    return 'general_inquiry', 0.5
            else:
                logger.error(f"AI classification failed: {result.get('error')}")
                return 'general_inquiry', 0.0

        except Exception as e:
            logger.error(f"❌ Error classifying intent: {e}")
            return 'general_inquiry', 0.0

    def should_auto_respond(self, intent: str, confidence: float) -> bool:
        """
        Determine if auto-response should be sent

        Args:
            intent: Classified intent
            confidence: Confidence score

        Returns:
            True if should auto-respond, False otherwise
        """
        # Don't auto-respond if disabled
        if not self.auto_response_enabled:
            return False

        # Don't auto-respond to low confidence classifications
        if confidence < self.confidence_threshold:
            logger.info(f"⏭️ Confidence too low ({confidence:.2f} < {self.confidence_threshold})")
            return False

        # Never auto-respond to these intents
        no_auto_response_intents = [
            'complaint',
            'requires_human_response',
            'spam'
        ]

        if intent in no_auto_response_intents:
            logger.info(f"⏭️ Intent '{intent}' requires human response")
            return False

        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("⚠️ Rate limit exceeded for auto-responses")
            return False

        return True

    async def generate_response(self, original_message: str, intent: str,
                               message_data: Dict) -> Optional[str]:
        """
        Generate AI response to message

        Args:
            original_message: Original message content
            intent: Classified intent
            message_data: Full message data dictionary

        Returns:
            Generated response text or None if failed
        """
        try:
            # CRITICAL: Use resolved_member_name from database lookup (most reliable)
            # Fall back to from_user, then sender_name, then generic "Member"
            sender_name = (
                message_data.get('resolved_member_name') or  # From database lookup
                message_data.get('from_user') or             # ClubOS field
                message_data.get('sender_name') or           # Legacy field
                'Member'
            )
            
            # Clean up name - extract first name for personalization
            # If name is 'Unknown', use generic greeting
            if sender_name.lower() == 'unknown':
                first_name = 'there'
            else:
                first_name = sender_name.split()[0].title() if sender_name else 'there'
            
            logger.info(f"📝 AI will address member as: {first_name} (full: {sender_name})")

            system_prompt = f"""You are a helpful AI assistant for a gym/fitness center.
You're responding to a member message on behalf of the gym staff.

Guidelines:
- Be friendly, professional, and helpful
- Keep responses concise (2-3 sentences max)
- ALWAYS address the member as "{first_name}" - this is their verified name
- Do NOT use any other names that might appear in the message content
- For billing/account issues, acknowledge and say a staff member will follow up
- For appointments, provide general guidance but say staff will confirm
- Never make promises or commitments without human approval

Member's verified name: {first_name}
Message intent: {intent}

IMPORTANT: The message content might contain other names (like previous conversation history). 
ONLY address this member as "{first_name}". Ignore any other names in the message.
"""

            messages = [{
                "role": "user",
                "content": f"Generate a helpful response to this member message:\n\n{original_message}"
            }]

            result = await self.ai_service.send_message(
                messages,
                system_prompt,
                max_tokens=300  # Keep responses short
            )

            if result['success']:
                return result['response']
            else:
                logger.error(f"AI response generation failed: {result.get('error')}")
                return None

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return None

    async def send_response(self, original_message: Dict, ai_response: str) -> bool:
        """
        Send AI-generated response via ClubOS

        Args:
            original_message: Original message dictionary
            ai_response: AI-generated response text

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            member_id = original_message.get('sender_id')
            if not member_id:
                logger.error("❌ Cannot send response: missing member_id")
                return False

            # Send via ClubOS messaging client
            success = self.clubos_client.send_sms_message(
                member_id=member_id,
                message=ai_response,
                notes="Auto-response generated by AI agent"
            )

            return success

        except Exception as e:
            logger.error(f"❌ Error sending AI response: {e}")
            return False

    async def log_ai_response(self, original_message_id: str, conversation_id: str,
                             member_id: str, member_name: str, ai_response: str,
                             ai_intent: str, ai_confidence: float,
                             sent_successfully: bool, error: str = None):
        """
        Log AI response to database

        Args:
            original_message_id: ID of original message
            conversation_id: Conversation ID
            member_id: Member ID
            member_name: Member name
            ai_response: AI-generated response
            ai_intent: Classified intent
            ai_confidence: Confidence score
            sent_successfully: Whether response was sent successfully
            error: Error message if failed
        """
        try:
            with self.inbox_db.db_manager.get_cursor() as cursor:
                if self.inbox_db.db_manager.db_type == 'postgresql':
                    sql = """
                        INSERT INTO ai_response_log (
                            original_message_id, conversation_id, member_id, member_name,
                            ai_response, ai_intent, ai_confidence, sent_successfully, error
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                else:  # SQLite
                    sql = """
                        INSERT INTO ai_response_log (
                            original_message_id, conversation_id, member_id, member_name,
                            ai_response, ai_intent, ai_confidence, sent_successfully, error
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """

                cursor.execute(sql, (
                    original_message_id,
                    conversation_id,
                    member_id,
                    member_name,
                    ai_response,
                    ai_intent,
                    ai_confidence,
                    1 if sent_successfully else 0,
                    error
                ))
                cursor.connection.commit()

        except Exception as e:
            logger.error(f"❌ Error logging AI response: {e}")

    def _check_rate_limit(self) -> bool:
        """
        Check if rate limit for auto-responses is exceeded

        Returns:
            True if within limit, False if exceeded
        """
        try:
            # Query recent AI responses from last hour
            with self.inbox_db.db_manager.get_cursor() as cursor:
                sql = """
                    SELECT COUNT(*) FROM ai_response_log
                    WHERE created_at > datetime('now', '-1 hour')
                    AND sent_successfully = 1
                """
                cursor.execute(sql)
                count = cursor.fetchone()[0]

                return count < self.max_responses_per_hour

        except Exception as e:
            logger.error(f"❌ Error checking rate limit: {e}")
            # Allow on error to be safe
            return True

    def set_auto_response_enabled(self, enabled: bool):
        """Enable or disable auto-responses"""
        self.auto_response_enabled = enabled
        logger.info(f"🤖 Auto-response {'enabled' if enabled else 'disabled'}")

    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for auto-responses"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"📊 Confidence threshold set to {self.confidence_threshold:.2f}")

    def get_ai_stats(self) -> Dict:
        """Get AI agent statistics"""
        try:
            with self.inbox_db.db_manager.get_cursor() as cursor:
                # Get total responses
                cursor.execute("SELECT COUNT(*) FROM ai_response_log")
                total_responses = cursor.fetchone()[0]

                # Get successful responses
                cursor.execute("SELECT COUNT(*) FROM ai_response_log WHERE sent_successfully = 1")
                successful_responses = cursor.fetchone()[0]

                # Get responses in last hour
                cursor.execute("""
                    SELECT COUNT(*) FROM ai_response_log
                    WHERE created_at > datetime('now', '-1 hour')
                """)
                responses_last_hour = cursor.fetchone()[0]

                return {
                    'auto_response_enabled': self.auto_response_enabled,
                    'confidence_threshold': self.confidence_threshold,
                    'total_responses': total_responses,
                    'successful_responses': successful_responses,
                    'failed_responses': total_responses - successful_responses,
                    'success_rate': successful_responses / total_responses if total_responses > 0 else 0,
                    'responses_last_hour': responses_last_hour,
                    'rate_limit': self.max_responses_per_hour,
                    'rate_limit_remaining': self.max_responses_per_hour - responses_last_hour
                }

        except Exception as e:
            logger.error(f"❌ Error getting AI stats: {e}")
            return {}
