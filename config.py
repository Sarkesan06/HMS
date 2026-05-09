import os


class Config:
    @staticmethod
    def _clean_env(name, default=""):
        value = os.getenv(name, default)
        if value is None:
            return default
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1].strip()
        return value

    SECRET_KEY = _clean_env.__func__("SECRET_KEY", "supersecretkey")
    MONGO_URI = _clean_env.__func__("MONGO_URI", "mongodb://localhost:27017/HMS")
    MONGO_DBNAME = os.getenv("MONGO_DBNAME", "HMS")
    JWT_SECRET_KEY = _clean_env.__func__("JWT_SECRET_KEY", "jwtsecretkey")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    _mail_username_raw = _clean_env.__func__("MAIL_USERNAME", "sharkroshan@gmail.com")
    _mail_password_raw = _clean_env.__func__("MAIL_PASSWORD", "tpcikcfngmtxmkov")
    _mail_default_sender_raw = _clean_env.__func__("MAIL_DEFAULT_SENDER", _mail_username_raw)

    MAIL_USERNAME = _mail_username_raw.strip()
    # Gmail app passwords are shown with spaces; SMTP expects a continuous token.
    MAIL_PASSWORD = _mail_password_raw.replace(" ", "").strip()
    MAIL_DEFAULT_SENDER = _mail_default_sender_raw.strip() or MAIL_USERNAME
    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", "10"))
    RECOVERY_DEV_MODE = os.getenv("RECOVERY_DEV_MODE", "false").lower() == "true"
    RECOVERY_EMAIL_MODE = os.getenv("RECOVERY_EMAIL_MODE", "async").lower()
    # Send recovery code to the entered account email by default to avoid confusion.
    RECOVERY_USE_DEDICATED_EMAIL = os.getenv("RECOVERY_USE_DEDICATED_EMAIL", "false").lower() == "true"


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

    # Force fast Mongo failover to prevent 30s worker hangs on unreachable clusters.
    if "mongodb" in MONGO_URI and "serverSelectionTimeoutMS" not in MONGO_URI:
        separator = "&" if "?" in MONGO_URI else "?"
        MONGO_URI = (
            f"{MONGO_URI}{separator}"
            "serverSelectionTimeoutMS=5000&connectTimeoutMS=5000&socketTimeoutMS=10000&timeoutMS=8000"
        )
