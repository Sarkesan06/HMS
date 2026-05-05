from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from config import Config
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.mail_service import send_transactional_email

# ================= EXTENSIONS =================
mongo = PyMongo()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()


# ================= CREATE APP =================
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # ================= DATABASE INDEX =================
    with app.app_context():
        try:
            mongo.db.appointments.create_index(
                [("doctor_id", 1), ("date", 1), ("time", 1)],
                unique=True
            )
        except Exception as e:
            print("Index creation error:", e)

    # ================= IMPORT BLUEPRINTS =================
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.doctor import doctor_bp
    from app.routes.patient import patient_bp
    from app.routes.appointment import appointment_bp
    from app.routes.consultation import consultation_bp
    from app.routes.chat import chat_bp

    # ================= REGISTER BLUEPRINTS =================
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(doctor_bp, url_prefix="/doctors")
    app.register_blueprint(patient_bp, url_prefix="/patients")
    app.register_blueprint(appointment_bp, url_prefix="/appointment")
    app.register_blueprint(consultation_bp, url_prefix="/consultation")
    app.register_blueprint(chat_bp, url_prefix="/chat")

    return app
def check_appointments():
    print("Checking appointments...")



from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_mail import Message
from app import mail

# ================= ROLE REQUIRED =================
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user = get_jwt_identity()

                if not current_user or current_user.get("role") != required_role:
                    return jsonify({"msg": "Access denied"}), 403

                return fn(*args, **kwargs)

            except Exception as e:
                return jsonify({"msg": "Invalid token", "error": str(e)}), 401

        return decorator
    return wrapper


# ================= GET CURRENT USER ROLE =================
def get_current_user_role():
    try:
        verify_jwt_in_request()
        current_user = get_jwt_identity()

        if current_user and "role" in current_user:
            return current_user["role"]

        return None

    except Exception:
        return None


# ================= SEND EMAIL =================
def send_email(to_email, subject, body):
    try:
        send_transactional_email(to_email=to_email, subject=subject, text_body=body)
        return True
    except Exception as e:
        print("Email Error:", e)
        return False
