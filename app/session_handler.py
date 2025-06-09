
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
        @app.before_request
        def ensure_session_consistency():
            self._ensure_session_consistency()

    def _ensure_session_consistency(self):
        try:
            if current_user.is_authenticated and "user_email" not in session:
                session["user_email"] = current_user.email
                session["login_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Fixed missing session data for authenticated user: {current_user.email}")
                if "_flashes" in session:
                    updated_flashes = []
                    for cat, msg in session["_flashes"]:
                        if "Please log in to access this page" not in msg:
                            updated_flashes.append((cat, msg))
                    session["_flashes"] = updated_flashes
            elif not current_user.is_authenticated and "user_email" in session:
                important_keys = ["visits", "last_visit", "next_url", "next"]
                flask_login_keys = ["_user_id", "_id", "_fresh", "_remember", "csrf_token"]
                important_keys.extend(flask_login_keys)
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
                if "_flashes" in session:
                    preserved_values["_flashes"] = session["_flashes"]
                session.clear()
                for k, v in preserved_values.items():
                    session[k] = v
                print("Cleaned session data for unauthenticated user")
        except Exception as e:
            print(f"Session consistency error: {str(e)}")
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
            session["next_url"] = request.url
            from flask import flash, redirect, url_for
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view
