from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import NguoiDung

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        flash('Vui lòng nhập ít nhất 2 ký tự để tìm kiếm', 'warning')
        return redirect(url_for('user.dashboard'))
    
    # Search for users by username or email
    users = NguoiDung.query.filter(
        (NguoiDung.ten_nguoi_dung.contains(query)) | 
        (NguoiDung.email.contains(query))
    ).limit(20).all()
    
    return render_template('search_results.html', query=query, users=users)
