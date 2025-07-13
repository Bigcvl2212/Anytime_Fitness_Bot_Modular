"""
Enhanced AI Conversation Triage - VERIFIED AI INTEGRATION FROM EXPERIMENTAL CODE
Uses the proven AI patterns from worker.py for intelligent conversation analysis and routing.
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ...config.constants import GEMINI_API_KEY_SECRET
from ...utils.debug_helpers import debug_page_state


class EnhancedConversationTriage:
    """
    Enhanced conversation triage using AI to analyze member messages and determine appropriate responses.
    Based on VERIFIED AI INTEGRATION from worker.py
    """
    
    def __init__(self, gemini_model=None):
        """Initialize conversation triage with AI model"""
        self.gemini_model = gemini_model or self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            from google.cloud import secretmanager
            import google.generativeai as genai
            
            # Get API key from secret manager
            client = secretmanager.SecretManagerServiceClient()
            name = f"{GEMINI_API_KEY_SECRET}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            api_key = response.payload.data.decode("UTF-8")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            print("✅ Gemini AI initialized for conversation triage")
            return model
            
        except Exception as e:
            print(f"❌ Error initializing Gemini AI: {e}")
            return None
    
    def get_ai_triage(self, conversation_history: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Uses Gemini to analyze the conversation and determine the user's intent.
        
        VERIFIED AI INTEGRATION FROM WORKER.PY
        """
        print("   INFO: Performing AI Triage to determine intent...")
        
        if not self.gemini_model:
            print("   WARN: Gemini model not available, using fallback analysis")
            return {"intent": "GENERAL_QUESTION", "data_needed": "NONE"}
        
        try:
            # Build conversation history for AI analysis
            prompt_history = "\n".join([
                f"{msg['sender']}: {msg['text']}" 
                for msg in conversation_history
            ])
            
            # Enhanced prompt based on experimental code
            prompt = f"""
            You are a triage assistant for Anytime Fitness. Analyze the last message from the "Member" in the context of the conversation.
            Classify the intent and determine if external data is required.

            **Possible Intents:**
            - "PAYMENT_PROBLEM": The member explicitly states they have an issue paying, their card was declined, or they cannot make a payment.
            - "BILLING_QUESTION": The member is asking a question about a bill, a charge, or a payment date.
            - "SCHEDULING_REQUEST": The member wants to book, change, or cancel an appointment.
            - "CANCELLATION_INQUIRY": The member asks how to cancel their membership.
            - "TRAINING_INQUIRY": The member asks about personal training, group training, or fitness programs.
            - "GENERAL_QUESTION": Any other general question about gym services.
            - "SIMPLE_ACKNOWLEDGEMENT": The message is just "ok", "thanks", etc.

            **Data Needed Rules:**
            - If intent is "PAYMENT_PROBLEM", you MUST request "CURRENT_BALANCE".
            - If intent is "BILLING_QUESTION", you MUST request "CURRENT_BALANCE".
            - If intent is "SCHEDULING_REQUEST", you MUST request "CALENDAR_AVAILABILITY".
            - For ALL OTHER intents, the data needed is "NONE".

            You MUST respond with only a JSON object in the format: {{"intent": "CLASSIFICATION", "data_needed": "DATA_TYPE"}}

            **Conversation History:**
            ---
            {prompt_history}
            ---
            **JSON Response:**
            """
            
            response = self.gemini_model.generate_content(prompt)
            cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
            analysis = json.loads(cleaned_response_text)
            
            print(f"   SUCCESS: AI Triage complete. Intent: {analysis.get('intent')}, Data Needed: {analysis.get('data_needed')}")
            return analysis
            
        except Exception as e:
            print(f"   ERROR: Could not parse AI Triage response. Error: {e}")
            return {"intent": "ERROR", "data_needed": "NONE"}
    
    def generate_ai_response(self, intent: str, member_data: Optional[Dict] = None, 
                           conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate appropriate AI response based on intent and available data.
        
        ENHANCED WITH EXPERIMENTAL AI PATTERNS
        """
        print(f"   INFO: Generating AI response for intent: {intent}")
        
        if not self.gemini_model:
            return self._get_fallback_response(intent)
        
        try:
            # Build context for AI response
            context = {
                "intent": intent,
                "member_data": member_data or {},
                "conversation_history": conversation_history or []
            }
            
            # Enhanced prompt based on experimental patterns
            prompt = f"""
            You are an AI assistant for Anytime Fitness Fond du Lac. Generate a helpful, professional response based on the following context:

            **Intent:** {intent}
            **Member Data:** {json.dumps(member_data, indent=2) if member_data else "None"}
            **Recent Conversation:** {json.dumps(conversation_history[-3:], indent=2) if conversation_history else "None"}

            **Response Guidelines:**
            - Be professional but friendly
            - Keep responses concise (under 200 words)
            - If payment issues, offer to help resolve
            - If scheduling, offer to check availability
            - If training questions, highlight our programs
            - Always encourage them to reach out if they need more help

            **Business Policies:**
            - Late fees: $19.50 for payments over 1 day late
            - Cancellation: Must call Abc Financial at 501-515-5000
            - Training: Personal and group training available
            - HSA/FSA accepted for memberships and training

            Generate a helpful response:
            """
            
            response = self.gemini_model.generate_content(prompt)
            ai_response = response.text.strip()
            
            print(f"   SUCCESS: AI response generated ({len(ai_response)} characters)")
            return ai_response
            
        except Exception as e:
            print(f"   ERROR: Could not generate AI response. Error: {e}")
            return self._get_fallback_response(intent)
    
    def _get_fallback_response(self, intent: str) -> str:
        """Get fallback response when AI is not available"""
        fallback_responses = {
            "PAYMENT_PROBLEM": "I understand you're having payment issues. Let me check your account balance and help resolve this. Can you call us at (920) 921-4800 or visit the gym to discuss payment options?",
            "BILLING_QUESTION": "I'd be happy to help with your billing question. Please call us at (920) 921-4800 or visit the gym to review your account details.",
            "SCHEDULING_REQUEST": "I'd be happy to help you schedule an appointment. Please call us at (920) 921-4800 or visit the gym to check our availability.",
            "CANCELLATION_INQUIRY": "I'm sorry to hear you're considering leaving. Please call Abc Financial at 501-515-5000 to discuss cancellation options. We'd love to help you stay!",
            "TRAINING_INQUIRY": "We offer excellent personal and group training programs! Please call us at (920) 921-4800 or visit the gym to learn more about our training options.",
            "GENERAL_QUESTION": "Thank you for your question. Please call us at (920) 921-4800 or visit the gym for assistance.",
            "SIMPLE_ACKNOWLEDGEMENT": "You're welcome! Let us know if you need anything else.",
            "ERROR": "I apologize for the confusion. Please call us at (920) 921-4800 or visit the gym for assistance."
        }
        
        return fallback_responses.get(intent, fallback_responses["GENERAL_QUESTION"])
    
    def analyze_conversation_sentiment(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze conversation sentiment and urgency.
        
        ENHANCED WITH EXPERIMENTAL AI PATTERNS
        """
        print("   INFO: Analyzing conversation sentiment...")
        
        if not self.gemini_model:
            return {"sentiment": "neutral", "urgency": "low", "confidence": 0.5}
        
        try:
            # Build conversation for analysis
            conversation_text = "\n".join([
                f"{msg['sender']}: {msg['text']}" 
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            
            prompt = f"""
            Analyze the sentiment and urgency of this gym member conversation:

            **Conversation:**
            {conversation_text}

            **Analysis Guidelines:**
            - Sentiment: positive, neutral, negative, or frustrated
            - Urgency: low, medium, high, or critical
            - Confidence: 0.0 to 1.0 (how confident in the analysis)

            Respond with JSON only:
            {{"sentiment": "classification", "urgency": "level", "confidence": 0.0}}
            """
            
            response = self.gemini_model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            analysis = json.loads(cleaned_response)
            
            print(f"   SUCCESS: Sentiment analysis complete. Sentiment: {analysis.get('sentiment')}, Urgency: {analysis.get('urgency')}")
            return analysis
            
        except Exception as e:
            print(f"   ERROR: Could not analyze sentiment. Error: {e}")
            return {"sentiment": "neutral", "urgency": "low", "confidence": 0.5}
    
    def determine_response_priority(self, intent: str, sentiment: str, urgency: str) -> str:
        """
        Determine response priority based on intent, sentiment, and urgency.
        
        ENHANCED WITH EXPERIMENTAL AI PATTERNS
        """
        # Priority scoring based on experimental patterns
        priority_scores = {
            "PAYMENT_PROBLEM": 10,
            "BILLING_QUESTION": 8,
            "SCHEDULING_REQUEST": 7,
            "CANCELLATION_INQUIRY": 9,
            "TRAINING_INQUIRY": 6,
            "GENERAL_QUESTION": 4,
            "SIMPLE_ACKNOWLEDGEMENT": 2,
            "ERROR": 5
        }
        
        sentiment_multipliers = {
            "negative": 1.5,
            "frustrated": 2.0,
            "neutral": 1.0,
            "positive": 0.8
        }
        
        urgency_multipliers = {
            "critical": 2.0,
            "high": 1.5,
            "medium": 1.2,
            "low": 1.0
        }
        
        base_score = priority_scores.get(intent, 5)
        sentiment_mult = sentiment_multipliers.get(sentiment, 1.0)
        urgency_mult = urgency_multipliers.get(urgency, 1.0)
        
        final_score = base_score * sentiment_mult * urgency_mult
        
        # Determine priority level
        if final_score >= 15:
            return "CRITICAL"
        elif final_score >= 10:
            return "HIGH"
        elif final_score >= 6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def process_conversation(self, conversation_history: List[Dict[str, str]], 
                           member_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete conversation processing workflow.
        
        ENHANCED WITH EXPERIMENTAL AI PATTERNS FROM WORKER.PY
        """
        print("🧠 Processing conversation with AI triage...")
        
        try:
            # Step 1: AI Intent Analysis
            intent_analysis = self.get_ai_triage(conversation_history)
            
            # Step 2: Sentiment Analysis
            sentiment_analysis = self.analyze_conversation_sentiment(conversation_history)
            
            # Step 3: Determine Priority
            priority = self.determine_response_priority(
                intent_analysis.get('intent', 'GENERAL_QUESTION'),
                sentiment_analysis.get('sentiment', 'neutral'),
                sentiment_analysis.get('urgency', 'low')
            )
            
            # Step 4: Generate Response
            ai_response = self.generate_ai_response(
                intent_analysis.get('intent', 'GENERAL_QUESTION'),
                member_data,
                conversation_history
            )
            
            # Step 5: Compile Results
            result = {
                'intent': intent_analysis.get('intent'),
                'data_needed': intent_analysis.get('data_needed'),
                'sentiment': sentiment_analysis.get('sentiment'),
                'urgency': sentiment_analysis.get('urgency'),
                'priority': priority,
                'ai_response': ai_response,
                'confidence': sentiment_analysis.get('confidence', 0.5),
                'processed_at': datetime.now().isoformat()
            }
            
            print(f"✅ Conversation processing complete:")
            print(f"   - Intent: {result['intent']}")
            print(f"   - Priority: {result['priority']}")
            print(f"   - Data Needed: {result['data_needed']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing conversation: {e}")
            return {
                'intent': 'ERROR',
                'data_needed': 'NONE',
                'sentiment': 'neutral',
                'urgency': 'low',
                'priority': 'LOW',
                'ai_response': self._get_fallback_response('ERROR'),
                'confidence': 0.0,
                'processed_at': datetime.now().isoformat()
            }


# Convenience functions for backward compatibility
def get_ai_triage(conversation_history: List[Dict[str, str]], gemini_model=None) -> Dict[str, str]:
    """Get AI triage analysis"""
    triage = EnhancedConversationTriage(gemini_model)
    return triage.get_ai_triage(conversation_history)


def generate_ai_response(intent: str, member_data: Optional[Dict] = None, 
                       conversation_history: Optional[List[Dict]] = None,
                       gemini_model=None) -> str:
    """Generate AI response"""
    triage = EnhancedConversationTriage(gemini_model)
    return triage.generate_ai_response(intent, member_data, conversation_history)


def process_conversation(conversation_history: List[Dict[str, str]], 
                        member_data: Optional[Dict] = None,
                        gemini_model=None) -> Dict[str, Any]:
    """Process conversation with complete AI analysis"""
    triage = EnhancedConversationTriage(gemini_model)
    return triage.process_conversation(conversation_history, member_data) 