"""
Notification Service
==================

Service for handling user notifications and real-time alerts.
"""

from flask import current_app
from datetime import datetime
from typing import List, Optional
from ..models import db, ThongBao, NguoiDung


class NotificationService:
    """Service for managing user notifications"""
    
    @staticmethod
    def create_notification(
        user_id: int,
        title: str,
        content: str,
        notification_type: str = "info",
        link: Optional[str] = None
    ) -> ThongBao:
        """Create a new notification"""
        try:
            notification = ThongBao(
                nguoi_nhan=user_id,
                tieu_de=title,
                noi_dung=content,
                loai=notification_type,
                lien_ket=link,
                ngay_tao=datetime.utcnow()
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Emit real-time notification if SocketIO is available
            try:
                from flask_socketio import emit
                emit('new_notification', {
                    'id': notification.id,
                    'title': title,
                    'content': content,
                    'type': notification_type,
                    'link': link,
                    'timestamp': notification.ngay_tao.isoformat()
                }, room=f'user_{user_id}')
            except:
                pass  # SocketIO not available
            
            return notification
            
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False, limit: int = 50) -> List[ThongBao]:
        """Get notifications for a user"""
        query = ThongBao.query.filter_by(nguoi_nhan=user_id)
        
        if unread_only:
            query = query.filter_by(da_doc=False)
            
        return query.order_by(ThongBao.ngay_tao.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            notification = ThongBao.query.filter_by(
                id=notification_id, 
                nguoi_nhan=user_id
            ).first()
            
            if notification and not notification.da_doc:
                notification.da_doc = True
                notification.ngay_doc = datetime.utcnow()
                db.session.commit()
                return True
                
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """Mark all notifications as read for a user"""
        try:
            unread_notifications = ThongBao.query.filter_by(
                nguoi_nhan=user_id,
                da_doc=False
            ).all()
            
            count = 0
            for notification in unread_notifications:
                notification.da_doc = True
                notification.ngay_doc = datetime.utcnow()
                count += 1
            
            db.session.commit()
            return count
            
        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
            db.session.rollback()
            return 0
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications"""
        try:
            return ThongBao.query.filter_by(
                nguoi_nhan=user_id,
                da_doc=False
            ).count()
        except:
            return 0
    
    @staticmethod
    def delete_notification(notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            notification = ThongBao.query.filter_by(
                id=notification_id,
                nguoi_nhan=user_id
            ).first()
            
            if notification:
                db.session.delete(notification)
                db.session.commit()
                return True
                
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error deleting notification: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def broadcast_to_role(
        role: str,
        title: str,
        content: str,
        notification_type: str = "info",
        link: Optional[str] = None
    ) -> int:
        """Broadcast notification to all users with a specific role"""
        try:
            users = NguoiDung.query.filter_by(vai_tro=role).all()
            count = 0
            
            for user in users:
                NotificationService.create_notification(
                    user_id=user.id,
                    title=title,
                    content=content,
                    notification_type=notification_type,
                    link=link
                )
                count += 1
            
            return count
            
        except Exception as e:
            current_app.logger.error(f"Error broadcasting to role {role}: {str(e)}")
            return 0
    
    @staticmethod
    def broadcast_to_all(
        title: str,
        content: str,
        notification_type: str = "info",
        link: Optional[str] = None
    ) -> int:
        """Broadcast notification to all users"""
        try:
            users = NguoiDung.query.all()
            count = 0
            
            for user in users:
                NotificationService.create_notification(
                    user_id=user.id,
                    title=title,
                    content=content,
                    notification_type=notification_type,
                    link=link
                )
                count += 1
            
            return count
            
        except Exception as e:
            current_app.logger.error(f"Error broadcasting to all users: {str(e)}")
            return 0


# Convenience functions for common notification types
def notify_lab_registration(user_id: int, session_title: str):
    """Notify user about successful lab registration"""
    return NotificationService.create_notification(
        user_id=user_id,
        title="Đăng ký ca thực hành thành công",
        content=f"Bạn đã đăng ký thành công ca thực hành: {session_title}",
        notification_type="success",
        link="/lab/my-sessions"
    )

def notify_lab_reminder(user_id: int, session_title: str, start_time: str):
    """Notify user about upcoming lab session"""
    return NotificationService.create_notification(
        user_id=user_id,
        title="Nhắc nhở ca thực hành",
        content=f"Ca thực hành '{session_title}' sẽ bắt đầu lúc {start_time}",
        notification_type="warning",
        link="/lab/my-sessions"
    )

def notify_system_maintenance(message: str):
    """Notify all users about system maintenance"""
    return NotificationService.broadcast_to_all(
        title="Bảo trì hệ thống",
        content=message,
        notification_type="warning",
        link="/"
    )

def notify_new_feature(feature_description: str):
    """Notify all users about new features"""
    return NotificationService.broadcast_to_all(
        title="Tính năng mới",
        content=feature_description,
        notification_type="info",
        link="/user/dashboard"
    )
