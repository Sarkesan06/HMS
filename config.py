import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/HMS")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecretkey")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "sharkroshan@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "change-me")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID",
        "633988002854-tea7qq18oigrdg0kqen1l7ohupoibl04.apps.googleusercontent.com",
    )

    # Advanced Recovery Settings
    RECOVERY_CODE_EXPIRY_MINUTES = 2
    BACKUP_CODE_EXPIRY_DAYS = 365
    MAX_RECOVERY_ATTEMPTS = 5
    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_DURATION_MINUTES = 30
    TRUSTED_DEVICE_TOKEN_EXPIRY_DAYS = 30
