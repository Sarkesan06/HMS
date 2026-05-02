class Config:
    SECRET_KEY = "supersecretkey"
    MONGO_URI = "mongodb://localhost:27017/HMS"
    JWT_SECRET_KEY = "jwtsecretkey"
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = 'sharkroshan@gmail.com'

    # ✅ REMOVE SPACES
    MAIL_PASSWORD = 'hlbf hqus gplx wryc'
    MAIL_DEFAULT_SENDER = 'sharkroshan@gmail.com'

        # Advanced Recovery Settings
    RECOVERY_CODE_EXPIRY_MINUTES = 2
    BACKUP_CODE_EXPIRY_DAYS = 365
    MAX_RECOVERY_ATTEMPTS = 5
    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_DURATION_MINUTES = 30
    TRUSTED_DEVICE_TOKEN_EXPIRY_DAYS = 30