"""
Comprehensive Cache Management System
===================================

Triệt để (comprehensive) and ổn định (stable) caching implementation
for Flask Lab Manager application.

Features:
- Route caching decorators
- Database query caching
- API response caching  
- Cache invalidation strategies
- Cache monitoring and metrics
- Performance optimization
"""

from functools import wraps
from datetime import datetime, timedelta
from flask import current_app, request, jsonify, g
from flask_login import current_user
from typing import Optional, Dict, Any, Union, Callable
import hashlib
import json
import time
import logging

# Type hints for cache objects
try:
    from flask_caching import Cache
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        CacheInstance = Cache
    else:
        CacheInstance = Any
except ImportError:
    CacheInstance = Any

logger = logging.getLogger(__name__)

class CacheManager:
    """Centralized cache management system"""
    
    def __init__(self, cache=None):
        self.cache = cache
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'errors': 0        }
    
    def get_cache(self) -> Optional[Any]:
        """Get cache instance from current app"""
        if self.cache:
            return self.cache
        
        try:
            from flask import current_app
            
            # Try to get cache from Flask-Caching extension
            cache_ext = current_app.extensions.get('cache')
            if cache_ext and isinstance(cache_ext, dict):
                # Flask-Caching stores cache as {Cache_instance: Backend_instance}
                # We need the Cache instance (key) which has get/set/delete methods
                for cache_instance in cache_ext.keys():
                    if hasattr(cache_instance, 'get') and hasattr(cache_instance, 'set') and hasattr(cache_instance, 'delete'):
                        return cache_instance
            
            # If cache_ext is the cache instance itself
            if cache_ext and hasattr(cache_ext, 'get') and hasattr(cache_ext, 'set') and hasattr(cache_ext, 'delete'):
                return cache_ext
            
            # Fallback: try to create cache from config
            from flask_caching import Cache
            fallback_cache = Cache(current_app)
            logger.warning("Using fallback cache instance")
            return fallback_cache
            
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set a value in cache"""
        cache = self.get_cache()
        if cache and hasattr(cache, 'set'):
            try:
                cache.set(key, value, timeout=timeout)
                return True
            except Exception as e:
                self.record_error()
                logger.error(f"Error setting cache key {key}: {e}")
                return False
        return False
    
    def get(self, key: str) -> Any:
        """Get a value from cache"""
        cache = self.get_cache()
        if cache:
            try:
                result = cache.get(key)
                if result is not None:
                    self.record_hit()
                else:
                    self.record_miss()
                return result
            except Exception as e:
                self.record_error()
                logger.error(f"Error getting cache key {key}: {e}")
                return None
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        cache = self.get_cache()
        if cache and hasattr(cache, 'delete'):
            try:
                cache.delete(key)
                return True
            except Exception as e:
                self.record_error()
                logger.error(f"Error deleting cache key {key}: {e}")
                return False
        return False
    
    def get_cache_metrics(self):
        """Get cache metrics and status"""
        cache = self.get_cache()
        return {
            'cache_type': type(cache).__name__ if cache else 'None',
            'cache_available': cache is not None,
            'hit_rate': self.get_hit_rate(),
            'total_hits': self.metrics['hits'],
            'total_misses': self.metrics['misses'],
            'total_errors': self.metrics['errors'],
            'total_invalidations': self.metrics['invalidations'],
            'timestamp': datetime.now().isoformat()
        }
    
    def record_hit(self):
        """Record cache hit"""
        self.metrics['hits'] += 1
        
    def record_miss(self):
        """Record cache miss"""
        self.metrics['misses'] += 1
        
    def record_invalidation(self):
        """Record cache invalidation"""
        self.metrics['invalidations'] += 1
        
    def record_error(self):
        """Record cache error"""
        self.metrics['errors'] += 1
    
    def get_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.metrics['hits'] + self.metrics['misses']
        if total == 0:
            return 0
        return (self.metrics['hits'] / total) * 100
    
    def generate_cache_key(self, prefix, *args, **kwargs):
        """Generate consistent cache key"""
        key_parts = [prefix]
        
        # Add user context if available
        if hasattr(g, 'current_user') and current_user.is_authenticated:
            key_parts.append(f"user_{current_user.id}")
        
        # Add arguments
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            else:
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}_{v}")
        
        return "_".join(key_parts)
    
    def cached_route(self, timeout=300, key_prefix=None, unless=None):
        """
        Decorator for caching route responses
        
        Args:
            timeout: Cache timeout in seconds (default 5 minutes)
            key_prefix: Custom cache key prefix
            unless: Function that returns True to skip caching
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache = self.get_cache()
                if not cache:
                    logger.warning("Cache not available, executing function directly")
                    return func(*args, **kwargs)
                
                # Check if caching should be skipped
                if unless and unless():
                    return func(*args, **kwargs)
                
                # Generate cache key
                prefix = key_prefix or f"route_{func.__name__}"
                cache_key = self.generate_cache_key(
                    prefix, 
                    request.method,
                    request.path,
                    request.args.to_dict(),
                    *args, 
                    **kwargs
                )
                
                try:
                    # Try to get from cache
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        self.record_hit()
                        logger.debug(f"Cache hit for key: {cache_key}")
                        return cached_result
                      # Cache miss - execute function
                    self.record_miss()
                    logger.debug(f"Cache miss for key: {cache_key}")
                    result = func(*args, **kwargs)
                    
                    # Store in cache
                    cache.set(cache_key, result, timeout=timeout)
                    return result
                    
                except Exception as e:
                    self.record_error()
                    logger.error(f"Cache error for key {cache_key}: {e}")
                    return func(*args, **kwargs)
                    
            return wrapper
        return decorator
    
    def cached_query(self, timeout=600, key_prefix=None):
        """
        Decorator for caching database queries
        
        Args:
            timeout: Cache timeout in seconds (default 10 minutes)
            key_prefix: Custom cache key prefix
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache = self.get_cache()
                if not cache:
                    return func(*args, **kwargs)
                
                # Generate cache key
                prefix = key_prefix or f"query_{func.__name__}"
                cache_key = self.generate_cache_key(prefix, *args, **kwargs)
                
                try:
                    # Try to get from cache
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        self.record_hit()
                        logger.debug(f"Query cache hit: {cache_key}")
                        return cached_result
                      # Cache miss - execute query
                    self.record_miss()
                    logger.debug(f"Query cache miss: {cache_key}")
                    result = func(*args, **kwargs)
                    
                    # Store in cache
                    cache.set(cache_key, result, timeout=timeout)
                    return result
                    
                except Exception as e:
                    self.record_error()
                    logger.error(f"Query cache error: {e}")
                    return func(*args, **kwargs)
                    
            return wrapper
        return decorator
    
    
    def invalidate_pattern(self, pattern):
        """
        Invalidate cache keys matching a pattern
        
        Args:
            pattern: Pattern to match (supports wildcards)
        """
        cache = self.get_cache()
        if not cache:
            logger.warning(f"Cache not available, skipping invalidation for pattern: {pattern}")
            return
        
        try:            # Flask-Caching doesn't support pattern-based deletion
            # For now, we clear all cache as a safe fallback
            # In production, you might want to track keys in Redis
            if hasattr(cache, 'clear'):
                cache.clear()
                logger.info(f"Cleared all cache for pattern: {pattern}")
            else:
                logger.warning(f"Cache clear not available for pattern: {pattern}")
            self.record_invalidation()
        except Exception as e:
            self.record_error()
            logger.error(f"Cache invalidation error: {e}")
    
    def invalidate_user_cache(self, user_id):
        """Invalidate all cache entries for a specific user"""
        patterns = [
            f"*user_{user_id}*",
            f"route_*user_{user_id}*",
            f"query_*user_{user_id}*",
            f"api_*user_{user_id}*"
        ]
        for pattern in patterns:
            self.invalidate_pattern(pattern)
    
    def invalidate_model_cache(self, model_name):
        """Invalidate cache entries related to a model"""
        patterns = [
            f"query_*{model_name.lower()}*",
            f"api_*{model_name.lower()}*",
            f"route_*{model_name.lower()}*"
        ]
        for pattern in patterns:
            self.invalidate_pattern(pattern)
    
    def clear_all_cache(self):
        """Clear all cache entries"""
        cache = self.get_cache()
        if cache and hasattr(cache, 'clear'):
            try:
                cache.clear()
                logger.info("All cache cleared")
            except Exception as e:
                logger.error(f"Error clearing cache: {e}")
        else:
            logger.warning("Cache not available or clear method not supported")
    
    def get_cache_info(self):
        """Get cache information and metrics"""
        cache = self.get_cache()
        info = {
            'metrics': self.metrics.copy(),
            'hit_rate': self.get_hit_rate(),
            'cache_available': cache is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        if cache:
            try:
                # Try to get cache backend info
                backend_info = getattr(cache, 'cache', None)
                if backend_info and hasattr(backend_info, 'get_stats'):
                    info['backend_stats'] = backend_info.get_stats()
            except:
                pass
        
        return info

# Global cache manager instance - will be initialized in app context
cache_manager = None

def get_cache_manager():
    """Get or create global cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = CacheManager()
    return cache_manager

# Convenience decorators
def cached_route(timeout=300, key_prefix=None, unless=None):
    """Route caching decorator"""
    return get_cache_manager().cached_route(timeout, key_prefix, unless)

def cached_query(timeout=600, key_prefix=None):
    """Query caching decorator"""
    return get_cache_manager().cached_query(timeout, key_prefix)

def invalidate_user_cache(user_id=None):
    """Invalidate user-specific cache"""
    return get_cache_manager().invalidate_user_cache(user_id)

def invalidate_model_cache(model_name):
    """Invalidate model-specific cache"""
    return get_cache_manager().invalidate_model_cache(model_name)

def invalidate_cache(pattern):
    """Invalidate cache by pattern"""
    return get_cache_manager().invalidate_pattern(pattern)

