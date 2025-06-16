import os

class Config:
    # Core Flask config
    SECRET_KEY = os.getenv("SECRET_KEY", "lab-manager-development-secret-key-change-in-production-2025")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF Configuration
    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "true").lower() in ['true', '1', 'yes', 'on']
    WTF_CSRF_TIME_LIMIT = int(os.getenv("WTF_CSRF_TIME_LIMIT", 3600))
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", SECRET_KEY)

    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ['true', '1', 'yes', 'on']
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in ['true', '1', 'yes', 'on']
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@labmanager.com")
    
    # Password Reset Configuration
    RESET_TOKEN_EXPIRATION = int(os.getenv("RESET_TOKEN_EXPIRATION", 3600))  # 1 hour in seconds

    # Session
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", 1800))    # Caching
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    # Thông tin tài khoản mẫu (dùng cho khởi tạo ban đầu, tiếng Việt)
    QUAN_TRI_HE_THONG_TEN = os.getenv("QUAN_TRI_HE_THONG_TEN", "HUYVIESEA")
    QUAN_TRI_HE_THONG_EMAIL = os.getenv("QUAN_TRI_HE_THONG_EMAIL", "hhuy0847@gmail.com")
    QUAN_TRI_HE_THONG_MATKHAU = os.getenv("QUAN_TRI_HE_THONG_MATKHAU", "huyviesea@manager")
    QUAN_TRI_VIEN_TEN = os.getenv("QUAN_TRI_VIEN_TEN", "ADMIN")
    QUAN_TRI_VIEN_EMAIL = os.getenv("QUAN_TRI_VIEN_EMAIL", "hhuy0847@gmail.com")
    QUAN_TRI_VIEN_MATKHAU = os.getenv("QUAN_TRI_VIEN_MATKHAU", "huyviesea@admin")
    NGUOI_DUNG_TEN = os.getenv("NGUOI_DUNG_TEN", "USER")
    NGUOI_DUNG_EMAIL = os.getenv("NGUOI_DUNG_EMAIL", "hhuy0847@gmail.com")
    NGUOI_DUNG_MATKHAU = os.getenv("NGUOI_DUNG_MATKHAU", "huyviesea@nguoidung")

    # SocketIO and Real-time settings
    SOCKETIO_ASYNC_MODE = os.getenv("SOCKETIO_ASYNC_MODE", "threading")
    SOCKETIO_LOGGER = True if os.getenv("SOCKETIO_LOGGER", "true").lower() == "true" else False
    SOCKETIO_ENGINEIO_LOGGER = True if os.getenv("SOCKETIO_ENGINEIO_LOGGER", "true").lower() == "true" else False
    
    # Real-time monitoring settings
    REALTIME_UPDATE_INTERVAL = int(os.getenv("REALTIME_UPDATE_INTERVAL", "2"))  # seconds
    REALTIME_MAX_HISTORY = int(os.getenv("REALTIME_MAX_HISTORY", "50"))  # data points
    
    # Optional: Other config (add as needed)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
