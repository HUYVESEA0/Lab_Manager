# Utility functions for Lab Manager Flask app

import datetime
from flask import current_app, request, session, url_for
from flask_login import current_user
from .models import NhatKyHoatDong, db
from flask_mail import Message, Mail
import threading

def log_activity(action, details, user=None):
    if user is None:
        user = current_user if current_user.is_authenticated else None
    # Sử dụng user.id để đồng bộ với model mới
    log = NhatKyHoatDong(nguoi_dung_ma=user.id if user else None, hanh_dong=action, chi_tiet=details, dia_chi_ip=request.remote_addr)
    db.session.add(log)
    db.session.commit()

def ensure_session_consistency():
    """Kiểm tra và đảm bảo tính nhất quán của session"""
    try:
        if current_user.is_authenticated and "user_email" not in session:
            session["user_email"] = current_user.email
            session["login_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_app.logger.info(f"Fixed missing session data for authenticated user: {current_user.email}")
    except Exception as e:
        current_app.logger.error(f"Session consistency error: {str(e)}")
    if not current_user.is_authenticated and "user_email" in session:
        session.pop("user_email", None)
        session.pop("login_time", None)

def clear_auth_session():
    """Xóa các session liên quan đến xác thực"""
    important_keys = [
        "visits",
        "last_visit",
        "csrf_token",
        "next_url",
    ]
    wtf_csrf_key = current_app.config.get("WTF_CSRF_FIELD_NAME", "csrf_token")
    if wtf_csrf_key not in important_keys:
        important_keys.append(wtf_csrf_key)
    preserved_values = {}
    for k in important_keys:
        if k in session:
            preserved_values[k] = session[k]
    if "_flashes" in session:
        flashes = []
        for cat, msg in session["_flashes"]:
            if cat != "info" or ("logged out" not in msg.lower() and "log in" not in msg.lower()):
                flashes.append((cat, msg))
        if flashes:
            preserved_values["_flashes"] = flashes
    session.clear()
    for k, v in preserved_values.items():
        session[k] = v

def debug_session_data():
    """Debug function to log current session data"""
    if not current_app.debug:
        return
    session_data = {key: session[key] for key in session}
    user_info = (
        {
            "is_authenticated": current_user.is_authenticated,
            "email": getattr(current_user, "email", "Not available"),
            "id": getattr(current_user, "id", "Not available"),
            "is_active": getattr(current_user, "is_active", False),
        }
        if current_user
        else {"No current_user": True}
    )
    current_app.logger.debug(f"SESSION DATA: {session_data}")
    current_app.logger.debug(f"CURRENT USER: {user_info}")
    current_app.logger.debug(f"REQUEST PATH: {request.path}")
    return {
        "session": session_data,
        "user": user_info,
        "request": {"path": request.path, "method": request.method, "endpoint": request.endpoint},
    }

def url_has_allowed_host_and_scheme(url, host):
    """
    Validate that the redirect URL is safe to use
    """
    if url is None:
        return False
    from urllib.parse import urlparse
    url_info = urlparse(url)
    if not url_info.netloc:
        return True
    return url_info.netloc == host

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail = Mail(app)
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, recipient, text_body, html_body=None):
    """Send email with subject, recipient, and body"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=text_body,
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send email asynchronously to avoid blocking the request
        if current_app.config.get('TESTING'):
            # For testing, send synchronously
            mail = Mail(current_app)
            mail.send(msg)
        else:
            # For production, send asynchronously
            from flask import copy_current_request_context
            
            @copy_current_request_context
            def send_async():
                try:
                    mail = Mail(current_app)
                    mail.send(msg)
                except Exception as e:
                    current_app.logger.error(f"Failed to send async email: {str(e)}")
            
            threading.Thread(target=send_async).start()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False

def send_password_reset_email(user):
    """Send password reset email to user"""
    try:
        token = user.get_reset_password_token()
        
        # For testing, use a placeholder URL
        if current_app.config.get('TESTING'):
            reset_url = f"http://localhost:5000/auth/reset-password/{token}"
        else:
            reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        subject = "Lab Manager - Đặt lại mật khẩu"
        
        text_body = f"""
Xin chào {user.ten_nguoi_dung},

Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Lab Manager của mình.

Vui lòng nhấp vào liên kết sau để đặt lại mật khẩu:
{reset_url}

Liên kết này sẽ hết hiệu lực sau 1 giờ.

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.

Trân trọng,
Đội ngũ Lab Manager
        """.strip()
        
        html_body = f"""
<html>
<body>
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
            <h2 style="color: #007bff; text-align: center;">Lab Manager</h2>
            <h3 style="color: #333;">Đặt lại mật khẩu</h3>
            
            <p>Xin chào <strong>{user.ten_nguoi_dung}</strong>,</p>
            
            <p>Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản Lab Manager của mình.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #007bff; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Đặt lại mật khẩu
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                <strong>Lưu ý:</strong> Liên kết này sẽ hết hiệu lực sau 1 giờ.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                Trân trọng,<br>
                Đội ngũ Lab Manager
            </p>
        </div>
    </div>
</body>
</html>
        """.strip()
        
        return send_email(subject, user.email, text_body, html_body)
        
    except Exception as e:
        current_app.logger.error(f"Error sending password reset email: {str(e)}")
        return False
