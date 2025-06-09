"""
Real-time System Monitor for Lab Manager
Provides live system metrics, user activity, and performance data
"""

import os
import psutil
import json
import time
import threading
from datetime import datetime, timedelta
from flask import current_app
from flask_socketio import SocketIO, emit, rooms
from sqlalchemy import func
from app.models import NguoiDung, CaThucHanh, db
import logging

class RealTimeSystemMonitor:
    def __init__(self, socketio):
        self.socketio = socketio
        self.is_monitoring = False
        self.monitoring_thread = None
        self.update_interval = 2  # seconds
        self.metrics_history = []
        self.max_history = 50  # Keep last 50 data points
        
    def start_monitoring(self):
        """Start real-time monitoring in background thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            current_app.logger.info("Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        current_app.logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop running in background"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = self._get_system_metrics()
                user_metrics = self._get_user_activity_metrics()
                
                # Store in history
                timestamp = datetime.now().isoformat()
                metrics_data = {
                    'timestamp': timestamp,
                    'system': system_metrics,
                    'users': user_metrics
                }
                
                self.metrics_history.append(metrics_data)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Emit to all connected admin clients
                self.socketio.emit('system_metrics_update', metrics_data, room='admin_dashboard')
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                current_app.logger.error(f"Monitoring error: {str(e)}")
                time.sleep(5)  # Wait longer on error
    
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
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used
            disk_total = disk.total
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'cpu': {
                    'percent': round(cpu_percent, 1),
                    'count': cpu_count,
                    'status': self._get_performance_status(cpu_percent)
                },
                'memory': {
                    'percent': round(memory_percent, 1),
                    'used': self._format_bytes(memory_used),
                    'total': self._format_bytes(memory_total),
                    'status': self._get_performance_status(memory_percent)
                },
                'disk': {
                    'percent': round(disk_percent, 1),
                    'used': self._format_bytes(disk_used),
                    'total': self._format_bytes(disk_total),
                    'status': self._get_performance_status(disk_percent)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },                'processes': process_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"System metrics error: {str(e)}")
            return self._get_default_metrics()
    
    def _get_user_activity_metrics(self):
        """Collect user activity metrics from database"""
        try:
            now = datetime.now()
            today = now.date()
            hour_ago = now - timedelta(hours=1)
            
            # Total users
            total_users = NguoiDung.query.count()
            
            # Active users (logged in within last hour)
            active_users = NguoiDung.query.filter(
                NguoiDung.last_seen >= hour_ago
            ).count()
            
            # Today's logins (approximate based on last_seen)
            today_logins = NguoiDung.query.filter(
                func.date(NguoiDung.last_seen) == today
            ).count()
              # Active lab sessions
            active_sessions = CaThucHanh.query.filter(
                CaThucHanh.dang_hoat_dong == True
            ).count()
            
            # Recent user activities (last 10)
            recent_users = NguoiDung.query.filter(
                NguoiDung.last_seen >= hour_ago            ).order_by(NguoiDung.last_seen.desc()).limit(10).all()
            
            recent_activities = []
            for user in recent_users:
                time_diff = now - user.last_seen
                minutes_ago = int(time_diff.total_seconds() / 60)
                
                if minutes_ago < 1:
                    time_str = "vừa xong"
                elif minutes_ago < 60:
                    time_str = f"{minutes_ago} phút trước"
                else:
                    hours_ago = int(minutes_ago / 60)
                    time_str = f"{hours_ago} giờ trước"
                
                recent_activities.append({
                    'user': user.ten_nguoi_dung,
                    'time': time_str,
                    'action': 'đăng nhập'
                })
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'today_logins': today_logins,
                'active_sessions': active_sessions,
                'recent_activities': recent_activities,
                'online_status': {
                    'current': active_users,
                    'trend': 'up' if active_users > 20 else 'stable'
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"User metrics error: {str(e)}")
            return self._get_default_user_metrics()
    
    def _get_performance_status(self, percent):
        """Get performance status based on percentage"""
        if percent < 60:
            return 'good'
        elif percent < 80:
            return 'warning'
        else:
            return 'critical'
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    def _get_default_metrics(self):
        """Return default metrics when system metrics fail"""
        return {
            'cpu': {'percent': 0, 'count': 1, 'status': 'unknown'},
            'memory': {'percent': 0, 'used': '0 MB', 'total': '0 MB', 'status': 'unknown'},
            'disk': {'percent': 0, 'used': '0 GB', 'total': '0 GB', 'status': 'unknown'},
            'network': {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0},
            'processes': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_default_user_metrics(self):
        """Return default user metrics when database query fails"""
        return {
            'total_users': 0,
            'active_users': 0,
            'today_logins': 0,
            'active_sessions': 0,
            'recent_activities': [],
            'online_status': {'current': 0, 'trend': 'stable'}
        }
    
    def get_metrics_history(self):
        """Get historical metrics data"""
        return self.metrics_history
    
    def emit_user_update(self, user_id, update_type, data):
        """Emit real-time updates to specific user"""
        try:
            user_room = f'user_{user_id}'
            self.socketio.emit(f'user_{update_type}_update', data, room=user_room)
        except Exception as e:
            current_app.logger.error(f"Error emitting user update: {str(e)}")
    
    def emit_lab_session_update(self, session_data):
        """Emit lab session updates to all relevant users"""
        try:
            # Emit to admin dashboard
            self.socketio.emit('lab_session_update', session_data, room='admin_dashboard')
            
            # Emit to all users (for their personal dashboards)
            self.socketio.emit('lab_session_update', session_data, room='user_dashboard')
            
        except Exception as e:
            current_app.logger.error(f"Error emitting lab session update: {str(e)}")
    
    def get_user_dashboard_data(self, user_id):
        """Get personalized dashboard data for a specific user"""
        try:
            from app.models import NguoiDung, CaThucHanh, DangKyCa
            
            user = NguoiDung.query.get(user_id)
            if not user:
                return None
              # Get user's upcoming sessions
            upcoming_sessions = db.session.query(CaThucHanh).join(
                DangKyCa
            ).filter(
                DangKyCa.nguoi_dung_id == user_id,
                CaThucHanh.ngay >= datetime.now().date()
            ).order_by(CaThucHanh.ngay.asc()).limit(5).all()
            
            # Get user's completed sessions count
            completed_sessions = db.session.query(CaThucHanh).join(
                DangKyCa
            ).filter(
                DangKyCa.nguoi_dung_id == user_id,
                CaThucHanh.ngay < datetime.now().date()
            ).count()
            
            # Format session data
            sessions_data = []
            for session in upcoming_sessions:
                sessions_data.append({
                    'id': session.id,
                    'title': session.tieu_de,
                    'date': session.ngay.strftime('%d/%m/%Y'),
                    'time': f"{session.gio_bat_dau.strftime('%H:%M')} - {session.gio_ket_thuc.strftime('%H:%M')}",
                    'status': self._get_session_status(session),
                    'location': session.dia_diem or 'TBA'
                })
            
            return {
                'user_id': user_id,
                'username': user.ten_nguoi_dung,
                'upcoming_sessions': len(upcoming_sessions),
                'completed_sessions': completed_sessions,
                'sessions': sessions_data,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user dashboard data: {str(e)}")
            return None
    
    def _get_session_status(self, session):
        """Determine session status based on current time"""
        now = datetime.now()
        session_start = datetime.combine(session.ngay, session.gio_bat_dau)
        session_end = datetime.combine(session.ngay, session.gio_ket_thuc)
        
        if now < session_start:
            return 'Sắp diễn ra'
        elif session_start <= now <= session_end:
            return 'Đang diễn ra'
        else:
            return 'Đã kết thúc'


# Global monitor instance
system_monitor = None

def init_real_time_monitor(socketio):
    """Initialize real-time monitoring system"""
    global system_monitor
    system_monitor = RealTimeSystemMonitor(socketio)
    return system_monitor

def get_system_monitor():
    """Get the global system monitor instance"""
    return system_monitor
