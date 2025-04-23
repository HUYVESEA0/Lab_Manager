from flask import Flask, session, render_template_string
from flask_login import LoginManager, current_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'debug-key'
login_manager = LoginManager(app)

# Template HTML để hiển thị thông tin debug
DEBUG_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Session Debug</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #444; }
        .debug-box { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .key { font-weight: bold; color: #007bff; }
        pre { background: #f1f1f1; padding: 10px; border-radius: 4px; overflow-x: auto; }
        .auth-status { padding: 10px; margin-bottom: 15px; border-radius: 4px; }
        .logged-in { background-color: #d4edda; color: #155724; }
        .logged-out { background-color: #f8d7da; color: #721c24; }
        .action-btn { background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
        .action-btn:hover { background: #0069d9; }
        .danger-btn { background: #dc3545; }
        .danger-btn:hover { background: #c82333; }
    </style>
</head>
<body>
    <h1>Flask Session Debug Tool</h1>
    
    <div class="auth-status {% if current_user.is_authenticated %}logged-in{% else %}logged-out{% endif %}">
        Authentication Status: 
        <strong>{% if current_user.is_authenticated %}Logged In ({{ current_user.username }}){% else %}Logged Out{% endif %}</strong>
    </div>
    
    <div class="debug-box">
        <h2>Session Contents</h2>
        {% if session %}
            <ul>
                {% for key, value in session.items() %}
                    <li><span class="key">{{ key }}</span>: {{ value }}</li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No session data found.</p>
        {% endif %}
    </div>
    
    <div class="debug-box">
        <h2>Actions</h2>
        <form method="post" action="/debug/clear-session">
            <button type="submit" class="action-btn danger-btn">Clear Session</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def debug_index():
    """Hiển thị thông tin session hiện tại"""
    return render_template_string(DEBUG_TEMPLATE)

@app.route('/debug/clear-session', methods=['POST'])
def clear_session():
    """Xóa toàn bộ session data"""
    session.clear()
    return render_template_string(DEBUG_TEMPLATE + "<script>alert('Session cleared!');</script>")

if __name__ == '__main__':
    app.run(debug=True, port=5050)
