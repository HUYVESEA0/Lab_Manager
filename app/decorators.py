
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (hasattr(current_user, 'is_admin') and current_user.is_admin()):
            flash("Bạn cần quyền quản trị viên để truy cập trang này.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

def admin_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (hasattr(current_user, 'is_admin_manager') and current_user.is_admin_manager()):
            flash("Bạn cần quyền quản trị hệ thống để truy cập trang này.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function
