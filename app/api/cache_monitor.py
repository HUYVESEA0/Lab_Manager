"""
Cache Monitoring API
==================

API endpoints for monitoring cache performance and management.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.decorators import admin_required
from app.cache.cache_manager import get_cache_metrics, cache_manager
from datetime import datetime

cache_monitor_bp = Blueprint('cache_monitor', __name__, url_prefix='/api/v1/cache')

@cache_monitor_bp.route('/metrics', methods=['GET'])
@login_required
@admin_required
def get_cache_metrics_api():
    """Get comprehensive cache metrics"""
    try:
        metrics = get_cache_metrics()
        
        # Add additional computed metrics
        metrics['performance'] = {
            'hit_rate_percentage': round(metrics.get('hit_rate', 0), 2),
            'miss_rate_percentage': round(100 - metrics.get('hit_rate', 0), 2),
            'total_requests': metrics['metrics']['hits'] + metrics['metrics']['misses'],
            'efficiency_score': 'Excellent' if metrics.get('hit_rate', 0) > 80 else 
                               'Good' if metrics.get('hit_rate', 0) > 60 else 
                               'Poor' if metrics.get('hit_rate', 0) > 30 else 'Critical'
        }
        
        # Add cache health status
        metrics['health'] = {
            'status': 'healthy' if metrics['cache_available'] else 'unavailable',
            'last_checked': datetime.now().isoformat(),
            'recommendations': []
        }
        
        # Add recommendations based on performance
        if metrics.get('hit_rate', 0) < 50:
            metrics['health']['recommendations'].append("Consider increasing cache timeouts")
        if metrics['metrics']['errors'] > 0:
            metrics['health']['recommendations'].append("Investigate cache errors")
        if not metrics['cache_available']:
            metrics['health']['recommendations'].append("Cache system is not available - check configuration")
            
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get cache metrics',
            'message': str(e),
            'cache_available': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@cache_monitor_bp.route('/clear', methods=['POST'])
@login_required
@admin_required
def clear_cache_api():
    """Clear all cache entries"""
    try:
        cache_manager.clear_all_cache()
        
        return jsonify({
            'message': 'Cache cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to clear cache',
            'message': str(e)
        }), 500

@cache_monitor_bp.route('/invalidate', methods=['POST'])
@login_required
@admin_required  
def invalidate_cache_pattern():
    """Invalidate cache entries by pattern"""
    try:
        data = request.get_json()
        pattern = data.get('pattern') if data else None
        
        if not pattern:
            return jsonify({'error': 'Pattern is required'}), 400
            
        cache_manager.invalidate_pattern(pattern)
        
        return jsonify({
            'message': f'Cache pattern "{pattern}" invalidated successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to invalidate cache pattern',
            'message': str(e)
        }), 500

@cache_monitor_bp.route('/status', methods=['GET'])
@login_required
@admin_required
def get_cache_status_api():
    """Get cache system status"""
    return jsonify(get_cache_status())

def get_cache_status():
    """Get cache system status (can be called with or without request context)"""
    try:
        from flask import current_app, has_request_context
        
        # Only access current_app if we're in a request context
        if has_request_context():
            cache = current_app.extensions.get('cache')
            cache_config = {
                'type': current_app.config.get('CACHE_TYPE', 'unknown'),
                'default_timeout': current_app.config.get('CACHE_DEFAULT_TIMEOUT', 300),
                'available': cache is not None
            }
        else:
            # Fallback when no request context
            cache_config = {
                'type': 'SimpleCache',  # Default from config.py
                'default_timeout': 300,
                'available': True  # Assume available
            }
        
        metrics = get_cache_metrics()
        
        status = {
            'system': cache_config,
            'metrics': metrics,
            'uptime': 'N/A',  # Could be enhanced with actual uptime tracking
            'memory_usage': 'N/A',  # Could be enhanced with actual memory tracking
            'timestamp': datetime.now().isoformat()
        }
        
        return status
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get cache status',
            'message': str(e)
        }), 500

@cache_monitor_bp.route('/warm', methods=['POST'])
@login_required
@admin_required
def warm_cache_api():
    """Warm up cache entries"""
    try:
        from app.cache.cache_warming import CacheWarmer
        
        data = request.get_json() if request.is_json else {}
        cache_type = data.get('type', 'all')  # 'all', 'dashboard', 'system', 'user'
        
        warmer = CacheWarmer()
        
        if cache_type == 'dashboard':
            success = warmer.warm_dashboard_caches()
        elif cache_type == 'system':
            success = warmer.warm_system_caches()
        elif cache_type == 'user':
            user_ids = data.get('user_ids')
            success = warmer.warm_user_caches(user_ids)
        else:  # 'all'
            success = warmer.warm_all_caches()
        
        report = warmer.get_cache_report()
        
        return jsonify({
            'success': success,
            'message': f'Cache warming {"completed successfully" if success else "completed with errors"}',
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to warm cache',
            'message': str(e)
        }), 500

@cache_monitor_bp.route('/health', methods=['GET'])
def get_cache_health():
    """Get cache health check - public endpoint for monitoring"""
    try:
        metrics = get_cache_metrics()
        
        health_status = {
            'status': 'healthy' if metrics['cache_available'] else 'unhealthy',
            'cache_available': metrics['cache_available'],
            'hit_rate': metrics.get('hit_rate', 0),
            'total_requests': metrics['metrics']['hits'] + metrics['metrics']['misses'],
            'errors': metrics['metrics']['errors'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Determine overall health
        if not metrics['cache_available']:
            health_status['status'] = 'critical'
        elif metrics.get('hit_rate', 0) < 30:
            health_status['status'] = 'warning'
        elif metrics['metrics']['errors'] > 10:
            health_status['status'] = 'warning'
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'cache_available': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@cache_monitor_bp.route('/test', methods=['GET'])
@login_required
@admin_required
def run_cache_test():
    """Run comprehensive caching system test"""
    try:
        # Import with relative path to avoid import issues
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        try:
            # Import the test module
            test_module_path = os.path.join(os.path.dirname(__file__), '..', '..', 'test', 'caching_system_test.py')
            if os.path.exists(test_module_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("caching_system_test", test_module_path)
                if spec and spec.loader:
                    test_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(test_module)
                    report = test_module.run_caching_system_test()
                else:
                    raise ImportError("Could not create module spec")
            else:
                raise ImportError("Test module not found")
        except ImportError:
            # Fallback to basic cache metrics if test module not available
            metrics = get_cache_metrics()
            report = {
                'summary': {
                    'total_tests': 1,
                    'passed_tests': 1 if metrics['cache_available'] else 0,
                    'failed_tests': 0 if metrics['cache_available'] else 1,
                    'success_rate': 100 if metrics['cache_available'] else 0,
                    'overall_status': 'PASS' if metrics['cache_available'] else 'FAIL'
                },
                'test_results': [{
                    'test_name': 'Basic Cache Availability',
                    'passed': metrics['cache_available'],
                    'message': 'Cache system is available' if metrics['cache_available'] else 'Cache not available',
                    'timestamp': datetime.now().isoformat()
                }],
                'note': 'Full test suite not available, showing basic cache check'
            }
        
        return jsonify({
            'success': True,
            'message': 'Caching system test completed',
            'report': report
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to run caching system test',
            'message': str(e)
        }), 500
