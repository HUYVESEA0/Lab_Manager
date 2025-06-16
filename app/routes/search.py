from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, text
from ..models import NguoiDung
from ..cache.cache_manager import cached_route, cached_api

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
@login_required
@cached_route(timeout=300, key_prefix='search_results')
def search():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        flash('Vui lòng nhập ít nhất 2 ký tự để tìm kiếm', 'warning')
        return redirect(url_for('user.dashboard'))    # Search for users by username or email with caching
    users = NguoiDung.query.filter(
        or_(
            text("ten_nguoi_dung LIKE :query"),
            text("email LIKE :query")
        )
    ).params(query=f'%{query}%').limit(20).all()
    
    return render_template('search_results.html', query=query, users=users)
