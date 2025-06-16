
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from app import create_app
from app.models import db, NguoiDung

def create_user_from_env():
    load_dotenv()
    users = [
        {
            "username": os.getenv("SYSTEM_ADMIN_USERNAME"),
            "email": os.getenv("SYSTEM_ADMIN_EMAIL"),
            "password": os.getenv("SYSTEM_ADMIN_PASSWORD"),
            "role": "quan_tri_he_thong"
        },
        {
            "username": os.getenv("ADMIN_USERNAME"),
            "email": os.getenv("ADMIN_EMAIL"),
            "password": os.getenv("ADMIN_PASSWORD"),
            "role": "quan_tri_vien"
        },
        {
            "username": os.getenv("USER_USERNAME"),
            "email": os.getenv("USER_EMAIL"),
            "password": os.getenv("USER_PASSWORD"),
            "role": "nguoi_dung"
        }
    ]
    app, socketio = create_app()
    with app.app_context():
        for u in users:
            if not u["username"] or not u["email"] or not u["password"]:
                continue
            existing = NguoiDung.query.filter_by(ten_nguoi_dung=u["username"]).first()
            if not existing:
                user = NguoiDung(ten_nguoi_dung=u["username"], email=u["email"], vai_tro=u["role"])
                user.dat_mat_khau(u["password"])
                db.session.add(user)
                print(f"Created user: {u['username']} ({u['role']})")
        db.session.commit()
        print("User initialization complete.")

if __name__ == "__main__":
    create_user_from_env()
