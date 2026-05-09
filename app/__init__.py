from flask import Flask, send_from_directory, abort
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config
from flask_mail import Mail
from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Rest of your imports...
from flask import Flask, send_from_directory, abort
from flask_pymongo import PyMongo

# Extensions
# Fail fast on Mongo connectivity issues to avoid 30s worker hangs/502s.
mongo = PyMongo(serverSelectionTimeoutMS=5000, connectTimeoutMS=5000, socketTimeoutMS=10000)
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MONGO_DBNAME"] = Config.MONGO_DBNAME
    frontend_dir = Path(app.root_path).parent / "frontend"
    frontend_dir_str = str(frontend_dir)
    
    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    
    # Initialize extensions
    mail.init_app(app)
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    if cors_origins != "*":
        cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    CORS(app, supports_credentials=True, origins=cors_origins)
    mongo.init_app(app)
    mongo.db = mongo.cx.get_database(Config.MONGO_DBNAME)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Create index
    with app.app_context():
        try:
            if mongo.db is None:
                raise RuntimeError(
                    "MongoDB database is not configured. Set MONGO_URI to a valid MongoDB connection string and MONGO_DBNAME to your database name, for example: MONGO_DBNAME=HMS"
                )
            mongo.db.appointments.create_index(
                [("doctor_id", 1), ("date", 1), ("time", 1)],
                unique=True
            )
            print("✅ Database index created successfully")
        except Exception as e:
            print("⚠️ Index creation error:", e)

    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.doctor import doctor_bp
    from app.routes.patient import patient_bp
    from app.routes.appointment import appointment_bp
    from app.routes.consultation import consultation_bp
    from app.routes.chat import chat_bp
    from app.routes.ml_routes import ml_bp 

    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(doctor_bp, url_prefix="/doctors")
    app.register_blueprint(patient_bp, url_prefix="/patients")
    app.register_blueprint(appointment_bp, url_prefix="/appointment")
    app.register_blueprint(consultation_bp, url_prefix="/consultation")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(ml_bp, url_prefix="/ml")  

    @app.route("/")
    def serve_index():
        return send_from_directory(frontend_dir_str, "index.html")

    @app.route("/health")
    def health_check():
        mongo_uri = app.config.get("MONGO_URI", "")
        return {
            "status": "ok",
            "backend": "running",
            "mongo_configured": bool(mongo_uri and mongo_uri.startswith(("mongodb://", "mongodb+srv://"))),
        }

    @app.route("/dashboard.html")
    def serve_dashboard():
        return send_from_directory(frontend_dir_str, "dashboard.html")

    @app.route("/advanced-recovery.html")
    def serve_advanced_recovery():
        return send_from_directory(frontend_dir_str, "advanced-recovery.html")

    @app.route("/security-alert.html")
    def serve_security_alert():
        return send_from_directory(frontend_dir_str, "security-alert.html")

    @app.route("/<path:filename>")
    def serve_frontend_assets(filename):
        file_path = frontend_dir / filename
        if file_path.exists() and file_path.is_file():
            return send_from_directory(frontend_dir_str, filename)
        abort(404)
    
    return app
