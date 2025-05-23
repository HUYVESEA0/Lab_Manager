import datetime

from flask import current_app, request, session
from flask_login import current_user

from models import ActivityLog, db


def log_activity(action, details, user=None):
    if user is None:
        user = current_user if current_user.is_authenticated else None

    log = ActivityLog(user_id=user.id if user else None, action=action, details=details, ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()


def ensure_session_consistency():
    """Kiểm tra và đảm bảo tính nhất quán của session"""
    try:
        # Đã đăng nhập nhưng không có thông tin session
        if current_user.is_authenticated and "user_email" not in session:
            session["user_email"] = current_user.email
            session["login_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_app.logger.info(f"Fixed missing session data for authenticated user: {current_user.email}")
    except Exception as e:
        current_app.logger.error(f"Session consistency error: {str(e)}")

    # Nếu người dùng không đăng nhập nhưng session vẫn còn thông tin user
    if not current_user.is_authenticated and "user_email" in session:
        session.pop("user_email", None)
        session.pop("login_time", None)


def clear_auth_session():
    """Xóa các session liên quan đến xác thực"""
    # Các khóa này không được sử dụng trong hàm
    # auth_keys = ["user_email", "login_time", "_user_id", "_fresh", "_id", "_remember"]

    # Lưu lại các thông tin session quan trọng và các flash message không phải login
    important_keys = [
        "visits",
        "last_visit",
        "csrf_token",
        "next_url",
    ]  # Make sure we explicitly include the WTF CSRF token with current Flask-WTF config
    wtf_csrf_key = current_app.config.get("WTF_CSRF_FIELD_NAME", "csrf_token")
    if wtf_csrf_key not in important_keys:
        important_keys.append(wtf_csrf_key)

    preserved_values = {}
    for k in important_keys:
        if k in session:
            preserved_values[k] = session[k]

    # Lưu flash messages không liên quan đến đăng nhập
    if "_flashes" in session:
        flashes = []
        for cat, msg in session["_flashes"]:
            if cat != "info" or ("logged out" not in msg.lower() and "log in" not in msg.lower()):
                flashes.append((cat, msg))
        if flashes:
            preserved_values["_flashes"] = flashes

    session.clear()

    # Khôi phục các giá trị cần giữ lại
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

    # Import inside function to avoid circular imports
    from urllib.parse import urlparse

    url_info = urlparse(url)

    # If there's no netloc, it's a relative URL which is safe
    if not url_info.netloc:
        return True

    # If there is a netloc (domain), check if it's our domain
    return url_info.netloc == host
