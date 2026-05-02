from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config
from flask_mail import Mail
from datetime import timedelta

# Extensions
mongo = PyMongo()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    
    # Initialize extensions
    mail.init_app(app)
    CORS(app, supports_credentials=True, origins="*")
    mongo.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Create index
    with app.app_context():
        try:
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
    
    return app