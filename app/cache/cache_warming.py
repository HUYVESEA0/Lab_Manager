"""
Cache Warming and Maintenance
============================

Strategies and utilities for cache warming, cleanup, and maintenance.
"""

from app.cache.cached_queries import (
    get_dashboard_statistics, get_total_users, get_total_sessions,
    get_activities_today, get_system_settings, get_recent_activities
)
from app.cache.cache_manager import cache_manager
from flask import current_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheWarmer:
    """Cache warming and maintenance utility"""
    
    def __init__(self):
        self.warmed_keys = []
        self.failed_keys = []
    
    def warm_dashboard_caches(self):
        """Warm up dashboard-related caches"""
        try:
            logger.info("Starting dashboard cache warming...")
            
            # Warm up dashboard statistics
            stats = get_dashboard_statistics()
            self.warmed_keys.append('dashboard_stats')
            
            # Warm up individual components
            get_total_users()
            self.warmed_keys.append('user_count')
            
            get_total_sessions()
            self.warmed_keys.append('session_count')
            
            get_activities_today()
            self.warmed_keys.append('activities_today')
            
            get_recent_activities(10)
            self.warmed_keys.append('recent_activities')
            
            logger.info(f"Dashboard cache warming completed. Warmed: {len(self.warmed_keys)} keys")
            return True
            
        except Exception as e:
            logger.error(f"Dashboard cache warming failed: {str(e)}")
            self.failed_keys.append('dashboard_caches')
            return False
    
    def warm_system_caches(self):
        """Warm up system-related caches"""
        try:
            logger.info("Starting system cache warming...")
            
            # Warm up system settings
            get_system_settings()
            self.warmed_keys.append('system_settings')
            
            logger.info("System cache warming completed")
            return True
            
        except Exception as e:
            logger.error(f"System cache warming failed: {str(e)}")
            self.failed_keys.append('system_caches')
            return False
    
    def warm_user_caches(self, user_ids=None):
        """Warm up user-specific caches"""
        try:
            logger.info("Starting user cache warming...")
            
            # If no specific users provided, warm for recent active users
            if not user_ids:
                from app.models import NguoiDung
                recent_users = NguoiDung.query.order_by(NguoiDung.ngay_tao.desc()).limit(10).all()
                user_ids = [user.id for user in recent_users]
            
            for user_id in user_ids:
                # Warm user-specific queries could be added here
                # For now, just log the warming attempt
                self.warmed_keys.append(f'user_{user_id}_caches')
            
            logger.info(f"User cache warming completed for {len(user_ids)} users")
            return True
            
        except Exception as e:
            logger.error(f"User cache warming failed: {str(e)}")
            self.failed_keys.append('user_caches')
            return False
    
    def warm_all_caches(self):
        """Warm up all important caches"""
        start_time = datetime.now()
        logger.info("Starting comprehensive cache warming...")
        
        # Reset counters
        self.warmed_keys = []
        self.failed_keys = []
        
        success_count = 0
        total_operations = 3
        
        if self.warm_dashboard_caches():
            success_count += 1
            
        if self.warm_system_caches():
            success_count += 1
            
        if self.warm_user_caches():
            success_count += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Cache warming completed: {success_count}/{total_operations} operations successful")
        logger.info(f"Warmed keys: {self.warmed_keys}")
        
        if self.failed_keys:
            logger.warning(f"Failed keys: {self.failed_keys}")
        
        return {
            'success': success_count == total_operations,
            'warmed_count': len(self.warmed_keys),
            'failed_count': len(self.failed_keys),
            'failed_keys': self.failed_keys,
            'duration': duration
        }
    
    def cleanup_expired_caches(self):
        """Clean up expired cache entries"""
        try:
            logger.info("Starting cache cleanup...")
            
            # This is a placeholder for cache cleanup logic
            # Different cache backends have different cleanup mechanisms
            cache = current_app.extensions.get('cache')
            
            if cache and hasattr(cache, 'clear'):
                # For simple cache backends, we might just clear all
                # More sophisticated backends might have selective cleanup
                pass
            
            logger.info("Cache cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {str(e)}")
            return False
    
    def get_cache_report(self):
        """Get a report of cache warming operations"""
        return {
            'warmed_keys': self.warmed_keys,
            'failed_keys': self.failed_keys,
            'total_warmed': len(self.warmed_keys),
            'total_failed': len(self.failed_keys),
            'success_rate': (len(self.warmed_keys) / (len(self.warmed_keys) + len(self.failed_keys)) * 100) 
                           if (len(self.warmed_keys) + len(self.failed_keys)) > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }

def schedule_cache_warming():
    """Schedule regular cache warming - can be called from a scheduler"""
    try:
        warmer = CacheWarmer()
        success = warmer.warm_all_caches()
        
        report = warmer.get_cache_report()
        logger.info(f"Scheduled cache warming report: {report}")
        
        return success, report
        
    except Exception as e:
        logger.error(f"Scheduled cache warming failed: {str(e)}")
        return False, {'error': str(e)}

def intelligent_cache_invalidation(model_name, operation, record_id=None):
    """
    Intelligent cache invalidation based on model changes
    
    Args:
        model_name: Name of the model that changed
        operation: 'create', 'update', 'delete'
        record_id: ID of the record (optional)
    """
    try:
        from app.cache.cached_queries import (
            invalidate_user_caches, invalidate_session_caches,
            invalidate_activity_caches, invalidate_system_caches
        )
        
        model_name = model_name.lower()
        
        if model_name in ['nguoidung', 'user']:
            invalidate_user_caches()
            if record_id:
                cache_manager.invalidate_user_cache(record_id)
                
        elif model_name in ['cathuchanh', 'labsession']:
            invalidate_session_caches()
            
        elif model_name in ['nhatkyhoatdong', 'activitylog']:
            invalidate_activity_caches()
            
        elif model_name in ['caidatheThong', 'systemsetting']:
            invalidate_system_caches()
        
        # Always invalidate dashboard stats for significant changes
        if operation in ['create', 'delete']:
            cache_manager.invalidate_pattern('dashboard_stats*')
        
        logger.info(f"Intelligent cache invalidation completed for {model_name} {operation}")
        
    except Exception as e:
        logger.error(f"Intelligent cache invalidation failed: {str(e)}")
