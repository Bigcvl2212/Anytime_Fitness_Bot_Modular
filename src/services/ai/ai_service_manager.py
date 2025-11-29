#!/usr/bin/env python3
"""
AI Service Manager
Core AI service for handling Claude API integration and request management
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
import os

logger = logging.getLogger(__name__)

class AIServiceManager:
    """
    Core AI service manager for handling Groq API requests
    Provides secure, rate-limited access to AI capabilities
    """

    def __init__(self, api_key: str = None):
        """
        Initialize AI Service Manager

        Args:
            api_key: Groq API key (if None, will try to get from secrets manager)
        """
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        # Using Groq's Llama model - get from env or use default
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Groq Llama 3.3 70B
        self.max_tokens = 4000
        self.temperature = 0.7

        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum 1 second between requests
        self._request_count = 0
        self._daily_limit = 1000  # Adjust based on your API limits

        # Request tracking for monitoring
        self._request_history = []

        if not self.api_key:
            self._load_api_key()

    def _load_api_key(self):
        """Load Groq API key from secrets manager"""
        try:
            from ..authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            self.api_key = secrets_manager.get_secret("groq-api-key")

            if not self.api_key:
                # Try environment variable as fallback
                self.api_key = os.getenv("GROQ_API_KEY")

            if not self.api_key:
                logger.error("❌ Groq API key not found in secrets manager or environment")
                raise ValueError("Groq API key not configured")

            logger.info("✅ Groq API key loaded successfully")

        except Exception as e:
            logger.error(f"❌ Error loading Groq API key: {e}")
            raise

    async def _rate_limit_check(self):
        """Ensure we don't exceed rate limits"""
        current_time = time.time()

        # Check minimum interval between requests
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)

        # Check daily limit
        if self._request_count >= self._daily_limit:
            logger.warning("⚠️ Daily API request limit reached")
            raise Exception("Daily API request limit exceeded")

        self._last_request_time = time.time()
        self._request_count += 1

    async def send_message(self, messages: List[Dict[str, str]],
                          system_prompt: str = None,
                          max_tokens: int = None,
                          temperature: float = None) -> Dict[str, Any]:
        """
        Send message to Groq API

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to set context
            max_tokens: Override default max tokens
            temperature: Override default temperature

        Returns:
            Response dictionary with AI response and metadata
        """
        try:
            await self._rate_limit_check()

            # Add system message to beginning if provided
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({"role": "system", "content": system_prompt})
            formatted_messages.extend(messages)

            # Prepare request payload (OpenAI-compatible format)
            payload = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "messages": formatted_messages
            }

            # Headers for Groq
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url,
                                      json=payload,
                                      headers=headers) as response:

                    if response.status == 200:
                        result = await response.json()

                        # Track successful request
                        self._track_request(True, len(str(payload)), len(str(result)))

                        # Parse Groq's OpenAI-compatible response format
                        response_text = ''
                        if result.get('choices') and len(result['choices']) > 0:
                            response_text = result['choices'][0].get('message', {}).get('content', '')

                        return {
                            'success': True,
                            'response': response_text,
                            'usage': result.get('usage', {}),
                            'model': result.get('model', self.model),
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Groq API error {response.status}: {error_text}")

                        # Track failed request
                        self._track_request(False, len(str(payload)), 0, error_text)

                        return {
                            'success': False,
                            'error': f"API error {response.status}: {error_text}",
                            'timestamp': datetime.now().isoformat()
                        }

        except Exception as e:
            logger.error(f"❌ Error sending message to Groq: {e}")
            self._track_request(False, 0, 0, str(e))

            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _track_request(self, success: bool, input_size: int, output_size: int, error: str = None):
        """Track request for monitoring and analytics"""
        request_record = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'input_size': input_size,
            'output_size': output_size,
            'error': error
        }

        self._request_history.append(request_record)

        # Keep only last 100 requests in memory
        if len(self._request_history) > 100:
            self._request_history.pop(0)

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        successful_requests = sum(1 for r in self._request_history if r['success'])
        failed_requests = len(self._request_history) - successful_requests
        total_input_size = sum(r['input_size'] for r in self._request_history)
        total_output_size = sum(r['output_size'] for r in self._request_history)

        return {
            'total_requests': len(self._request_history),
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': successful_requests / len(self._request_history) if self._request_history else 0,
            'total_input_tokens': total_input_size,
            'total_output_tokens': total_output_size,
            'daily_requests_used': self._request_count,
            'daily_limit': self._daily_limit,
            'last_request_time': self._last_request_time
        }

    async def simple_query(self, question: str, context: str = None) -> str:
        """
        Simple query interface for basic AI interactions

        Args:
            question: The question to ask
            context: Optional context to provide

        Returns:
            AI response as string
        """
        try:
            system_prompt = "You are a helpful AI assistant for a gym management system."
            if context:
                system_prompt += f" Context: {context}"

            messages = [{"role": "user", "content": question}]

            result = await self.send_message(messages, system_prompt)

            if result['success']:
                return result['response']
            else:
                logger.error(f"AI query failed: {result['error']}")
                return f"I'm sorry, I encountered an error: {result['error']}"

        except Exception as e:
            logger.error(f"❌ Error in simple query: {e}")
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"

    def is_available(self) -> bool:
        """Check if AI service is available and configured"""
        return bool(self.api_key and self._request_count < self._daily_limit)

    def reset_daily_count(self):
        """Reset daily request count (should be called daily)"""
        self._request_count = 0
        logger.info("🔄 Daily AI request count reset")