"""
Rate Limiter for Claude API

Handles Claude's 20,000 input tokens/minute rate limit by:
1. Tracking token usage across calls
2. Adding delays between iterations when needed
3. Providing backoff strategies
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class ClaudeRateLimiter:
    """
    Rate limiter for Claude API
    
    Limits:
    - 20,000 input tokens per minute
    - Tracks usage in rolling 60-second window
    """
    
    def __init__(self, tokens_per_minute: int = 20000):
        self.tokens_per_minute = tokens_per_minute
        self.token_history = []  # List of (timestamp, token_count) tuples
        self.total_tokens_used = 0
        
    def add_request(self, input_tokens: int, output_tokens: int = 0):
        """Record a request's token usage"""
        now = datetime.now()
        self.token_history.append((now, input_tokens))
        self.total_tokens_used += (input_tokens + output_tokens)
        
        # Clean old entries (> 60 seconds ago)
        cutoff = now - timedelta(seconds=60)
        self.token_history = [(ts, tokens) for ts, tokens in self.token_history if ts > cutoff]
    
    def get_current_usage(self) -> int:
        """Get input tokens used in the last 60 seconds"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=60)
        
        # Sum tokens from last 60 seconds
        recent_tokens = sum(tokens for ts, tokens in self.token_history if ts > cutoff)
        return recent_tokens
    
    def check_limit(self, requested_tokens: int) -> tuple[bool, Optional[float]]:
        """
        Check if we can make a request
        
        Returns:
            (can_proceed, delay_seconds)
        """
        current_usage = self.get_current_usage()
        
        if current_usage + requested_tokens <= self.tokens_per_minute:
            return True, None
        
        # Calculate required delay
        # Find oldest request timestamp
        if self.token_history:
            oldest_ts = min(ts for ts, _ in self.token_history)
            time_since_oldest = (datetime.now() - oldest_ts).total_seconds()
            delay = 60 - time_since_oldest + 1  # +1 for safety margin
            return False, max(0, delay)
        
        return True, None
    
    def wait_if_needed(self, estimated_tokens: int = 5000):
        """Wait if needed to respect rate limit"""
        can_proceed, delay = self.check_limit(estimated_tokens)
        
        if not can_proceed and delay:
            logger.warning(f"⏳ Rate limit approaching - waiting {delay:.1f}s...")
            time.sleep(delay)
            logger.info("✅ Rate limit window reset, proceeding")
    
    def get_stats(self) -> dict:
        """Get usage statistics"""
        current_usage = self.get_current_usage()
        return {
            'current_window_tokens': current_usage,
            'tokens_per_minute_limit': self.tokens_per_minute,
            'utilization_pct': (current_usage / self.tokens_per_minute) * 100,
            'total_tokens_used': self.total_tokens_used,
            'requests_in_window': len(self.token_history)
        }


# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter() -> ClaudeRateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = ClaudeRateLimiter()
    return _rate_limiter
