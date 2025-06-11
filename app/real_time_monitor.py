"""
Real-time System Monitoring Module
==================================

Provides real-time monitoring of system metrics and user activities.
Uses SocketIO to push updates to connected admin clients.
"""

import threading
import time
import psutil
import logging
from datetime import datetime, timedelta
from flask import current_app
from flask_socketio import emit
from .models import NguoiDung as User, CaThucHanh as LabSession, NhatKyHoatDong as ActivityLog, db
from sqlalchemy import func

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Real-time system monitoring class"""
    
    def __init__(self, socketio, update_interval=30, max_history=50):
        self.socketio = socketio
        self.update_interval = update_interval
        self.max_history = max_history
        self.is_monitoring = False
        self.monitoring_thread = None
        self.metrics_history = []
        
    def start_monitoring(self):
        """Start real-time monitoring in background thread"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Real-time monitoring started")
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop running in background"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = self._get_system_metrics()
                user_metrics = self._get_user_activity_metrics()
                
                # Combine metrics
                combined_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system': system_metrics,
                    'users': user_metrics
                }
                
                # Store in history
                self.metrics_history.append(combined_metrics)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Emit to connected admin clients
                self.socketio.emit(
                    'system_metrics_update', 
                    combined_metrics, 
                    room='admin_dashboard'
                )
                
                # Sleep until next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def _get_system_metrics(self):
        """Collect current system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total
            
            # Disk usage
            try:
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                disk_used = disk.used
                disk_total = disk.total
            except:
                # Fallback for Windows
                try:
                    disk = psutil.disk_usage('C:')
                    disk_percent = (disk.used / disk.total) * 100
                    disk_used = disk.used
                    disk_total = disk.total
                except:
                    disk_percent = 0
                    disk_used = 0
                    disk_total = 0
            
            # Network I/O
            try:
                network = psutil.net_io_counters()
                network_sent = network.bytes_sent
                network_recv = network.bytes_recv
            except:
                network_sent = 0
                network_recv = 0
            
            return {
                'cpu': {
                    'percent': round(cpu_percent, 2),
                    'count': cpu_count
                },
                'memory': {
                    'percent': round(memory_percent, 2),
                    'used': memory_used,
                    'total': memory_total,
                    'available': memory.available
                },
                'disk': {
                    'percent': round(disk_percent, 2),
                    'used': disk_used,
                    'total': disk_total
                },
                'network': {
                    'bytes_sent': network_sent,
                    'bytes_recv': network_recv
                }
            }
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {
                'cpu': {'percent': 0, 'count': 1},
                'memory': {'percent': 0, 'used': 0, 'total': 0, 'available': 0},
                'disk': {'percent': 0, 'used': 0, 'total': 0},
                'network': {'bytes_sent': 0, 'bytes_recv': 0}
            }
    
    def _get_user_activity_metrics(self):
        """Collect current user activity metrics"""
        try:
            with current_app.app_context():
                # Total users
                total_users = User.query.count()
                
                # Active users (logged in within last 30 minutes)
                thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
                active_users = User.query.filter(
                    User.last_login >= thirty_minutes_ago
                ).count()
                  # Online users (active and enabled)
                online_users = User.query.filter(
                    User.last_login >= thirty_minutes_ago,
                    User.is_active == True
                ).count()
                
                # Current lab sessions
                current_sessions = LabSession.query.filter(
                    LabSession.dang_hoat_dong == True
                ).count()
                
                # Today's sessions
                today = datetime.utcnow().date()
                today_sessions = LabSession.query.filter(
                    func.date(LabSession.gio_bat_dau) == today
                ).count()
                
                # Recent activities (last hour)
                one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                recent_activities = ActivityLog.query.filter(
                    ActivityLog.thoi_gian >= one_hour_ago
                ).count()
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'online_users': online_users,
                    'current_sessions': current_sessions,
                    'today_sessions': today_sessions,
                    'recent_activities': recent_activities
                }
                
        except Exception as e:
            logger.error(f"Error collecting user activity metrics: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'online_users': 0,
                'current_sessions': 0,
                'today_sessions': 0,
                'recent_activities': 0
            }
    
    def get_historical_data(self, hours=24):
        """Get historical metrics data"""
        try:
            # Return recent history
            return self.metrics_history[-hours:] if len(self.metrics_history) > hours else self.metrics_history
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return []
    
    def get_current_metrics(self):
        """Get current system metrics snapshot"""
        return {
            'system': self._get_system_metrics(),
            'users': self._get_user_activity_metrics(),
            'timestamp': datetime.now().isoformat()
        }

# Global monitor instance
system_monitor = None

def init_real_time_monitor(socketio, update_interval=30):
    """Initialize real-time monitoring system"""
    global system_monitor
    
    if system_monitor is None:
        system_monitor = SystemMonitor(socketio, update_interval)
        logger.info("Real-time monitor initialized")
    
    return system_monitor

def get_system_monitor():
    """Get the global system monitor instance"""
    return system_monitor
