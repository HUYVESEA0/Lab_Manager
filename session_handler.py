import datetime
import functools

from flask import g, request, session
from flask_login import current_user


class SessionHandler:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the session handler with Flask app"""
        self.app = app

        # Register a before_request handler to ensure session consistency
        @app.before_request
        def ensure_session_consistency():
            self._ensure_session_consistency()

    def _ensure_session_consistency(self):
        """Đảm bảo session phù hợp với trạng thái đăng nhập hiện tại"""
        try:
            # Đã đăng nhập nhưng không có thông tin session
            if current_user.is_authenticated and "user_email" not in session:
                session["user_email"] = current_user.email
                session["login_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Fixed missing session data for authenticated user: {current_user.email}")

                # Nếu có thông báo "Please log in", xóa nó vì người dùng đã đăng nhập
                if "_flashes" in session:
                    updated_flashes = []
                    for cat, msg in session["_flashes"]:
                        if "Please log in to access this page" not in msg:
                            updated_flashes.append((cat, msg))
                    session["_flashes"] = updated_flashes

            # Chưa đăng nhập nhưng session vẫn còn thông tin user
            elif not current_user.is_authenticated and "user_email" in session:
                # FIXED: Expanded list of important session keys to preserve
                important_keys = ["visits", "last_visit", "next_url", "next"]

                # Ensure all Flask-Login related keys are preserved
                flask_login_keys = ["_user_id", "_id", "_fresh", "_remember", "csrf_token"]
                important_keys.extend(flask_login_keys)

                # Always preserve CSRF tokens
                csrf_keys = ["csrf_token"]
                if self.app:
                    wtf_csrf_key = self.app.config.get("WTF_CSRF_FIELD_NAME", "csrf_token")
                    if wtf_csrf_key not in csrf_keys:
                        csrf_keys.append(wtf_csrf_key)
                important_keys.extend(csrf_keys)

                preserved_values = {}
                for k in important_keys:
                    if k in session:
                        preserved_values[k] = session[k]

                # Preserve flash messages
                if "_flashes" in session:
                    preserved_values["_flashes"] = session["_flashes"]

                # Xóa session hiện tại
                session.clear()

                # Khôi phục các giá trị cần giữ lại
                for k, v in preserved_values.items():
                    session[k] = v

                print("Cleaned session data for unauthenticated user")

        except Exception as e:
            # Ghi lại lỗi nhưng không gây lỗi cho request
            print(f"Session consistency error: {str(e)}")
            # Trong trường hợp lỗi nghiêm trọng, xóa toàn bộ session
            try:
                session.clear()
                print("Session cleared due to error")
            except:
                pass


# Additional functions
def login_required_with_redirect(view_func):
    """Decorator mở rộng login_required, lưu URL hiện tại để chuyển hướng sau đăng nhập"""

    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            # Lưu URL hiện tại vào session để chuyển hướng sau khi đăng nhập
            session["next_url"] = request.url
            from flask import flash, redirect, url_for

            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view
