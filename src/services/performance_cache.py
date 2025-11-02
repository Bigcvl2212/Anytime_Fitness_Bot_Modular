#!/usr/bin/env python3
"""
Response Caching System
High-performance in-memory caching for API responses and database queries
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable
import threading
import hashlib

logger = logging.getLogger(__name__)

class PerformanceCache:
    """High-performance in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._ttl_cache = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def get(self, key: str, default=None) -> Any:
        """Get cached value with automatic TTL expiration"""
        with self._lock:
            # Check if key exists and is not expired
            if key in self._cache:
                ttl = self._ttl_cache.get(key, float('inf'))
                age = time.time() - self._timestamps[key]
                
                if age < ttl:
                    self._stats['hits'] += 1
                    return self._cache[key]
                else:
                    # Expired - remove from cache
                    self._remove_key(key)
                    self._stats['evictions'] += 1
            
            self._stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: float = 300) -> None:
        """Set cached value with TTL in seconds"""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._ttl_cache[key] = ttl
            self._stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        with self._lock:
            if key in self._cache:
                self._remove_key(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cached values"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._ttl_cache.clear()
            logger.info("🧹 Cache cleared")
    
    def _remove_key(self, key: str) -> None:
        """Internal method to remove a key from all dictionaries"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._ttl_cache.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                'hit_rate': hit_rate,
                'cache_size': len(self._cache),
                'total_requests': total_requests
            }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        expired_keys = []
        current_time = time.time()
        
        with self._lock:
            for key, timestamp in self._timestamps.items():
                ttl = self._ttl_cache.get(key, float('inf'))
                age = current_time - timestamp
                
                if age >= ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_key(key)
                self._stats['evictions'] += 1
        
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)

# Global cache instance
performance_cache = PerformanceCache()

def cache_response(ttl: float = 300, key_prefix: str = ""):
    """Decorator to cache function responses with TTL"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            
            # Add positional arguments to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
                else:
                    key_parts.append(str(type(arg).__name__))
            
            # Add keyword arguments to key
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}={v}")
                else:
                    key_parts.append(f"{k}={type(v).__name__}")
            
            # Create hash of key to avoid very long keys
            cache_key = hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache first
            cached_result = performance_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"📋 Cache HIT for {func.__name__}")
                return cached_result
            
            # Not in cache - execute function and cache result
            logger.debug(f"📋 Cache MISS for {func.__name__} - executing...")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            performance_cache.set(cache_key, result, ttl)
            logger.debug(f"📋 Cached {func.__name__} result (took {execution_time:.3f}s)")
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator

class QueryCache:
    """Specialized cache for database query results"""
    
    def __init__(self):
        self.cache = performance_cache
    
    def get_or_execute(self, sql: str, params: tuple, executor: Callable, ttl: float = 300) -> Any:
        """Get cached query result or execute and cache"""
        # Create cache key from SQL and parameters
        cache_key = hashlib.md5(f"{sql}|{str(params)}".encode()).hexdigest()
        
        # Try cache first
        result = self.cache.get(f"query:{cache_key}")
        if result is not None:
            logger.debug(f"📋 Database query cache HIT: {sql[:50]}...")
            return result
        
        # Execute query and cache result
        logger.debug(f"📋 Database query cache MISS - executing: {sql[:50]}...")
        start_time = time.time()
        result = executor(sql, params)
        execution_time = time.time() - start_time
        
        self.cache.set(f"query:{cache_key}", result, ttl)
        logger.debug(f"📋 Cached query result (took {execution_time:.3f}s)")
        
        return result

# Global query cache instance
query_cache = QueryCache()

def setup_cache_cleanup_task():
    """Setup background task to clean up expired cache entries"""
    def cleanup_task():
        while True:
            try:
                time.sleep(60)  # Run every minute
                performance_cache.cleanup_expired()
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    logger.info("🧹 Cache cleanup task started")

def get_cache_statistics() -> Dict[str, Any]:
    """Get comprehensive cache statistics"""
    stats = performance_cache.get_stats()
    
    # Add memory usage estimate
    cache_size_bytes = 0
    try:
        for value in performance_cache._cache.values():
            if isinstance(value, str):
                cache_size_bytes += len(value.encode('utf-8'))
            elif isinstance(value, (list, dict)):
                cache_size_bytes += len(json.dumps(value).encode('utf-8'))
            else:
                cache_size_bytes += 100  # Rough estimate
    except Exception:
        cache_size_bytes = 0
    
    stats['memory_usage_kb'] = cache_size_bytes / 1024
    
    return stats

# Pre-configured cache decorators for common use cases
cache_short = lambda func: cache_response(ttl=60)(func)        # 1 minute
cache_medium = lambda func: cache_response(ttl=300)(func)      # 5 minutes  
cache_long = lambda func: cache_response(ttl=900)(func)        # 15 minutes
cache_dashboard = lambda func: cache_response(ttl=30, key_prefix="dashboard")(func)  # 30 seconds for dashboard