#!/usr/bin/env python3
from app import create_app
from app.services.notification_service import NotificationService

app, socketio = create_app()
ctx = app.app_context()
ctx.push()

print("=== TESTING NOTIFICATION SYSTEM ===")

# Test creating a notification
try:
    notif = NotificationService.create_notification(
        user_id=1,
        title="Test Notification",
        content="This is a test notification to verify the system is working.",
        notification_type="info",
        link="/user/dashboard"
    )
    print(f"✅ Created notification ID: {notif.id}")
except Exception as e:
    print(f"❌ Error creating notification: {e}")

# Test getting notifications
try:
    notifications = NotificationService.get_user_notifications(user_id=1)
    print(f"✅ User has {len(notifications)} total notifications")
    
    unread_count = NotificationService.get_unread_count(user_id=1)
    print(f"✅ User has {unread_count} unread notifications")
except Exception as e:
    print(f"❌ Error getting notifications: {e}")

print("=== NOTIFICATION SYSTEM TEST COMPLETE ===")
