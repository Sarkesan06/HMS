from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import mongo, bcrypt
from datetime import timedelta, datetime
import re
import random
import string
import hashlib
import uuid
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo, bcrypt, mail
from flask_mail import Message
import re
from bson.objectid import ObjectId
from config import Config
from threading import Thread
import resend
# Add these imports at the top of auth.py
import google.oauth2.id_token
from google.auth.transport import requests
from datetime import datetime, timedelta


auth_bp = Blueprint("auth", __name__)


# ================= GOOGLE LOGIN FOR ALL ROLES =================
# Add these imports at the top
import google.oauth2.id_token
from google.auth.transport import requests

# Google Login Endpoint
@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'message': 'No token provided'}), 400
        
        GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
        
        try:
            # Verify Google token
            idinfo = google.oauth2.id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            email = idinfo.get('email')
            name = idinfo.get('name', email.split('@')[0])
            
            # Check in all collections
            doctor = mongo.db.doctors.find_one({"email": email})
            if doctor:
                access_token = create_access_token(identity=email, expires_delta=timedelta(hours=24))
                return jsonify({
                    'access_token': access_token,
                    'role': 'doctor',
                    'email': email,
                    'name': doctor.get('name', name)
                }), 200
            
            admin = mongo.db.admins.find_one({"email": email})
            if admin:
                access_token = create_access_token(identity=email, expires_delta=timedelta(hours=24))
                return jsonify({
                    'access_token': access_token,
                    'role': 'admin',
                    'email': email,
                    'name': admin.get('name', name)
                }), 200
            
            # Check or create patient
            patient = mongo.db.patients.find_one({"email": email})
            if not patient:
                patient_data = {
                    "name": name,
                    "email": email,
                    "role": "patient",
                    "password": "",
                    "age": "Not specified",
                    "gender": "Not specified",
                    "phone": "Not specified",
                    "auth_type": "google",
                    "created_at": datetime.utcnow()
                }
                mongo.db.patients.insert_one(patient_data)
            
            access_token = create_access_token(identity=email, expires_delta=timedelta(hours=24))
            return jsonify({
                'access_token': access_token,
                'role': 'patient',
                'email': email,
                'name': name
            }), 200
            
        except ValueError as e:
            return jsonify({'message': 'Invalid Google token'}), 400
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Password validation function
def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"

# ----------------- REGISTER -----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        
        # Validate required fields
        if not name or not email or not password:
            return jsonify({"message": "Name, email and password are required"}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"message": message}), 400
        
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        
        # Check if user already exists based on role
        if role == "patient":
            if mongo.db.patients.find_one({"email": email}):
                return jsonify({"message": "Patient already exists"}), 400
            
            patient_data = {
                "name": name,
                "email": email,
                "password": hashed_pw,
                "role": "patient",
                "age": data.get("age", "Not specified"),
                "gender": data.get("gender", "Not specified"),
                "phone": data.get("phone", "Not specified"),
                "created_at": datetime.utcnow()
            }
            mongo.db.patients.insert_one(patient_data)
            
        elif role == "doctor":
            if mongo.db.doctors.find_one({"email": email}):
                return jsonify({"message": "Doctor already exists"}), 400
            
            doctor_data = {
                "name": name,
                "email": email,
                "password": hashed_pw,
                "role": "doctor",
                "specialization": data.get("specialization", "Not specified"),
                "available_slots": data.get("available_slots", "Not available"),
                "created_at": datetime.utcnow()
            }
            mongo.db.doctors.insert_one(doctor_data)
            
        elif role == "admin":
            if mongo.db.admins.find_one({"email": email}):
                return jsonify({"message": "Admin already exists"}), 400
            
            admin_data = {
                "name": name,
                "email": email,
                "password": hashed_pw,
                "role": "admin",
                "created_at": datetime.utcnow()
            }
            mongo.db.admins.insert_one(admin_data)
        else:
            return jsonify({"message": "Invalid role"}), 400
        
        return jsonify({"message": f"{role} registered successfully"}), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"message": str(e)}), 500

# ----------------- LOGIN -----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({"message": "Email and password required"}), 400
        
        user = None
        role = None
        user_id = None
        
        # Check admin collection
        user = mongo.db.admins.find_one({"email": email})
        if user:
            role = "admin"
            user_id = str(user["_id"])
        else:
            # Check doctor collection
            user = mongo.db.doctors.find_one({"email": email})
            if user:
                role = "doctor"
                user_id = str(user["_id"])
            else:
                # Check patient collection
                user = mongo.db.patients.find_one({"email": email})
                if user:
                    role = "patient"
                    user_id = str(user["_id"])
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Verify password
        if bcrypt.check_password_hash(user["password"], password):
            # Create access token
            access_token = create_access_token(
                identity=email,
                expires_delta=timedelta(hours=24)
            )
            
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "role": role,
                "email": email,
                "user_id": user_id
            }), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"message": str(e)}), 500
    

# ================= ADVANCED ACCOUNT RECOVERY =================



# ================= HELPER FUNCTIONS =================

def generate_backup_codes():
    """Generate 10 one-time backup codes"""
    codes = []
    for _ in range(10):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        codes.append({
            "code": code,
            "used": False,
            "created_at": datetime.utcnow()
        })
    return codes

def generate_recovery_code():
    """Generate 6-digit recovery code"""
    return ''.join(random.choices(string.digits, k=6))

def log_security_event(email, event_type, details, ip_address=None, user_agent=None):
    """Log security events for audit trail"""
    try:
        mongo.db.security_logs.insert_one({
            "email": email,
            "event_type": event_type,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print(f"Security log warning: {e}")

def send_advanced_recovery_email(email, code, name, recovery_method):
    """Send advanced recovery email with multiple options"""
    
    subject = f"🔐 Account Recovery - {recovery_method} - Hospital Management System"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1d3557, #457b9d); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
            .code {{ background: #e9ecef; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; border-radius: 10px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin: 15px 0; }}
            .button {{ background: #2a9d8f; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🏥 Hospital Management System</h2>
                <p>Account Recovery - {recovery_method}</p>
            </div>
            <div class="content">
                <p>Dear <strong>{name}</strong>,</p>
                
                <p>We received a request to recover your account using <strong>{recovery_method}</strong>.</p>
                
                <div class="code">
                    {code}
                </div>
                
                <div class="warning">
                    <strong>⚠️ Security Alert:</strong>
                    <ul style="margin: 10px 0 0 20px;">
                        <li>This code will expire in 15 minutes</li>
                        <li>Do not share this code with anyone</li>
                        <li>If you didn't request this, your account may be at risk</li>
                        <li><a href="{Config.FRONTEND_URL}/security-alert.html?email={email}" class="button">🔒 Report Suspicious Activity</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>© 2024 Hospital Management System | All Rights Reserved</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    def _send():
        try:
            from_email = Config.RESEND_FROM_EMAIL or "Hospital Management System <onboarding@resend.dev>"
            if not Config.RESEND_API_KEY:
                print("Resend API key is missing; recovery email was not sent")
                return

            resend.api_key = Config.RESEND_API_KEY
            print(f"Recovery email send attempt -> to: {email}, sender: {from_email}")
            response = resend.Emails.send({
                "from": from_email,
                "to": [email],
                "subject": subject,
                "html": html_body,
            })
            print(f"Recovery email sent via Resend to {email}: {response}")
        except Exception as e:
            print(f"Error sending Resend email: {e}")

    try:
        app_obj = current_app._get_current_object()
        Thread(target=lambda: _send_email_in_app_context(app_obj, _send), daemon=True).start()
        return True
    except Exception as e:
        print(f"Error queueing email: {e}")
        return False


def _send_email_in_app_context(app_obj, send_fn):
    with app_obj.app_context():
        send_fn()

# ================= 1. INITIATE RECOVERY WITH MULTIPLE METHODS =================

@auth_bp.route("/recovery/initiate-advanced", methods=["POST"])
def initiate_advanced_recovery():
    try:
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
        
        # Check for too many failed attempts
        failed_attempts = mongo.db.recovery_attempts.count_documents({
            "email": email,
            "status": "failed",
            "created_at": {"$gt": datetime.utcnow() - timedelta(minutes=30)}
        })
        
        if failed_attempts >= Config.MAX_FAILED_ATTEMPTS:
            return jsonify({
                "success": False, 
                "message": f"Too many failed attempts. Please try again after {Config.LOCKOUT_DURATION_MINUTES} minutes."
            }), 429
        
        # Find user
        user = None
        user_collection = None
        user_name = None
        security_questions = []
        
        for collection in ["patients", "doctors", "admins"]:
            user = mongo.db[collection].find_one({"email": email})
            if user:
                user_collection = collection
                user_name = user.get("name", "User")
                security_questions = user.get("security_questions", [])
                break
        
        if not user:
            # Security: Don't reveal if email exists
            print(f"Recovery requested for unregistered email: {email}")
            return jsonify({
                "success": True,
                "message": "If your email is registered, you will receive recovery options",
                "available_methods": []
            }), 200
        
        # Get available recovery methods
        available_methods = ["email"]
        
        # Check for security questions
        if security_questions and len(security_questions) >= 2:
            available_methods.append("security_questions")
        
        # Check for backup codes
        backup_codes = mongo.db.backup_codes.find_one({"email": email, "used": False})
        if backup_codes:
            available_methods.append("backup_code")
        
        # Check for trusted devices
        trusted_device = mongo.db.trusted_devices.find_one({
            "email": email,
            "last_used": {"$gt": datetime.utcnow() - timedelta(days=30)}
        })
        if trusted_device:
            available_methods.append("trusted_device")
        
        # Create recovery session
        recovery_id = str(uuid.uuid4())
        recovery_code = generate_recovery_code()
        
        mongo.db.recovery_attempts.insert_one({
            "recovery_id": recovery_id,
            "email": email,
            "collection": user_collection,
            "code": recovery_code,
            "available_methods": available_methods,
            "selected_method": None,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "attempts": 0
        })
        
        # Send email with code
        send_advanced_recovery_email(email, recovery_code, user_name, "Email Verification")
        
        log_security_event(email, "recovery_initiated", 
                          f"Recovery initiated with methods: {available_methods}",
                          ip_address, user_agent)
        
        return jsonify({
            "success": True,
            "message": "Recovery session created",
            "recovery_id": recovery_id,
            "available_methods": available_methods,
            "has_security_questions": len(security_questions) > 0,
            "expires_in": 900  # 15 minutes in seconds
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 2. VERIFY USING DIFFERENT METHODS =================

@auth_bp.route("/recovery/verify", methods=["POST"])
def verify_recovery():
    try:
        data = request.get_json(silent=True) or {}
        recovery_id = data.get("recovery_id")
        verification_type = data.get("verification_type")  # email, security_questions, backup_code, trusted_device
        verification_data = data.get("verification_data")
        
        # Find recovery session
        recovery = mongo.db.recovery_attempts.find_one({
            "recovery_id": recovery_id,
            "expires_at": {"$gt": datetime.utcnow()},
            "status": "pending"
        })
        
        if not recovery:
            return jsonify({"success": False, "message": "Recovery session expired or invalid"}), 400
        
        email = recovery["email"]
        verified = False
        
        # Method 1: Email Code Verification
        if verification_type == "email":
            if verification_data == recovery.get("code"):
                verified = True
            else:
                mongo.db.recovery_attempts.update_one(
                    {"recovery_id": recovery_id},
                    {"$inc": {"attempts": 1}}
                )
        
        # Method 2: Security Questions
        elif verification_type == "security_questions":
            questions = (verification_data or {}).get("questions", [])
            user = mongo.db[recovery["collection"]].find_one({"email": email})
            if not user:
                return jsonify({"success": False, "message": "User account not found"}), 404
            stored_questions = user.get("security_questions", [])
            
            # Verify answers
            correct_count = 0
            for q in questions:
                for sq in stored_questions:
                    if sq["question"] == q["question"] and sq["answer"].lower() == q["answer"].lower():
                        correct_count += 1
                        break
            
            if correct_count >= 2:
                verified = True
        
        # Method 3: Backup Code
        elif verification_type == "backup_code":
            backup = mongo.db.backup_codes.find_one({
                "email": email,
                "codes.code": verification_data,
                "codes.used": False
            })
            
            if backup:
                # Mark backup code as used
                mongo.db.backup_codes.update_one(
                    {"email": email, "codes.code": verification_data},
                    {"$set": {"codes.$.used": True, "codes.$.used_at": datetime.utcnow()}}
                )
                verified = True
        
        # Method 4: Trusted Device
        elif verification_type == "trusted_device":
            device_token = (verification_data or {}).get("device_token")
            if not device_token:
                return jsonify({"success": False, "message": "Device token is required"}), 400
            trusted = mongo.db.trusted_devices.find_one({
                "email": email,
                "device_token": device_token,
                "last_used": {"$gt": datetime.utcnow() - timedelta(days=30)}
            })
            
            if trusted:
                verified = True
                # Update last used
                mongo.db.trusted_devices.update_one(
                    {"_id": trusted["_id"]},
                    {"$set": {"last_used": datetime.utcnow()}}
                )
        
        if verified:
            # Generate recovery token for password reset
            reset_token = str(uuid.uuid4())
            mongo.db.recovery_attempts.update_one(
                {"recovery_id": recovery_id},
                {"$set": {
                    "status": "verified",
                    "reset_token": reset_token,
                    "verified_at": datetime.utcnow()
                }}
            )
            
            log_security_event(email, "recovery_verified", 
                              f"Verified using {verification_type}",
                              recovery.get("ip_address"))
            
            return jsonify({
                "success": True,
                "message": "Identity verified",
                "reset_token": reset_token,
                "recovery_id": recovery_id
            }), 200
        else:
            # Check if too many attempts
            attempts = recovery.get("attempts", 0) + 1
            if attempts >= Config.MAX_RECOVERY_ATTEMPTS:
                mongo.db.recovery_attempts.update_one(
                    {"recovery_id": recovery_id},
                    {"$set": {"status": "locked"}}
                )
                return jsonify({
                    "success": False,
                    "message": "Too many failed attempts. Recovery session locked."
                }), 403
            
            return jsonify({
                "success": False,
                "message": f"Verification failed. {Config.MAX_RECOVERY_ATTEMPTS - attempts} attempts remaining."
            }), 401
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 3. RESET PASSWORD AFTER VERIFICATION =================

@auth_bp.route("/recovery/advanced-reset", methods=["POST"])
def advanced_reset_password():
    try:
        data = request.get_json(silent=True) or {}
        recovery_id = data.get("recovery_id")
        reset_token = data.get("reset_token")
        new_password = data.get("new_password")
        
        # Find verified recovery session
        recovery = mongo.db.recovery_attempts.find_one({
            "recovery_id": recovery_id,
            "reset_token": reset_token,
            "status": "verified"
        })
        
        if not recovery:
            return jsonify({"success": False, "message": "Invalid recovery session"}), 400

        if not new_password:
            return jsonify({"success": False, "message": "New password is required"}), 400
        
        # Validate password strength
        if len(new_password) < 8:
            return jsonify({"success": False, "message": "Password must be at least 8 characters"}), 400
        
        if not re.search(r'[A-Z]', new_password):
            return jsonify({"success": False, "message": "Password must contain uppercase letter"}), 400
        
        if not re.search(r'[a-z]', new_password):
            return jsonify({"success": False, "message": "Password must contain lowercase letter"}), 400
        
        if not re.search(r'[0-9]', new_password):
            return jsonify({"success": False, "message": "Password must contain a number"}), 400
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            return jsonify({"success": False, "message": "Password must contain special character"}), 400
        
        # Hash new password
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        
        # Update password
        collection = mongo.db[recovery["collection"]]
        result = collection.update_one(
            {"email": recovery["email"]},
            {"$set": {"password": hashed_password}}
        )
        
        if result.modified_count > 0:
            # Mark recovery as completed
            mongo.db.recovery_attempts.update_one(
                {"recovery_id": recovery_id},
                {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
            )
            
            # Invalidate all existing sessions (optional - implement with JWT blacklist)
            # Invalidate backup codes (optional)
            mongo.db.backup_codes.update_one(
                {"email": recovery["email"]},
                {"$set": {"invalidated": True}}
            )
            
            log_security_event(recovery["email"], "password_reset", 
                              "Password reset via account recovery",
                              recovery.get("ip_address"))
            
            # Send confirmation email
            send_password_changed_alert(recovery["email"], recovery.get("ip_address"))
            
            return jsonify({
                "success": True,
                "message": "Password reset successful! You can now login with your new password."
            }), 200
        else:
            return jsonify({"success": False, "message": "Failed to reset password"}), 500
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 4. MANAGE SECURITY SETTINGS (LOGGED IN USERS) =================

@auth_bp.route("/security/setup", methods=["POST"])
@jwt_required()
def setup_security():
    try:
        email = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        
        # Setup Security Questions
        if "security_questions" in data:
            questions = data["security_questions"]
            if len(questions) >= 2:
                for collection in ["patients", "doctors", "admins"]:
                    result = mongo.db[collection].update_one(
                        {"email": email},
                        {"$set": {"security_questions": questions}}
                    )
                    if result.modified_count > 0:
                        break
        
        # Generate Backup Codes
        if "generate_backup_codes" in data and data["generate_backup_codes"]:
            backup_codes = generate_backup_codes()
            mongo.db.backup_codes.update_one(
                {"email": email},
                {"$set": {"codes": backup_codes, "generated_at": datetime.utcnow()}},
                upsert=True
            )
            
            # Return codes for user to save
            codes_list = [code["code"] for code in backup_codes]
            return jsonify({
                "success": True,
                "message": "Backup codes generated. Save them securely.",
                "backup_codes": codes_list
            }), 200
        
        # Register Trusted Device
        if "register_device" in data:
            device_name = data.get("device_name")
            device_token = str(uuid.uuid4())
            
            mongo.db.trusted_devices.insert_one({
                "email": email,
                "device_name": device_name,
                "device_token": device_token,
                "last_used": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "ip_address": request.remote_addr
            })
            
            return jsonify({
                "success": True,
                "message": "Device registered as trusted",
                "device_token": device_token
            }), 200
        
        return jsonify({"success": True, "message": "Security settings updated"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= 5. GET RECOVERY OPTIONS FOR USER =================

@auth_bp.route("/security/recovery-options", methods=["GET"])
@jwt_required()
def get_recovery_options():
    try:
        email = get_jwt_identity()
        
        # Get user's security settings
        user = None
        for collection in ["patients", "doctors", "admins"]:
            user = mongo.db[collection].find_one({"email": email})
            if user:
                break
        
        security_questions = user.get("security_questions", []) if user else []
        has_backup_codes = mongo.db.backup_codes.find_one({"email": email}) is not None
        trusted_devices = list(mongo.db.trusted_devices.find({"email": email}))
        
        return jsonify({
            "success": True,
            "has_security_questions": len(security_questions) >= 2,
            "security_questions_count": len(security_questions),
            "has_backup_codes": has_backup_codes,
            "trusted_devices_count": len(trusted_devices),
            "recovery_email": user.get("recovery_email") if user else None,
            "recovery_phone": user.get("recovery_phone") if user else None
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ================= HELPER: SEND PASSWORD CHANGE ALERT =================

def send_password_changed_alert(email, ip_address):
    subject = "🔒 Password Changed - Hospital Management System"
    
    body = f"""
    Hospital Management System - Security Alert
    
    Your password was recently changed.
    
    Details:
    📅 Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
    🌐 IP Address: {ip_address}
    
    If this was you, you can ignore this message.
    
    If you did NOT change your password, please contact support immediately.
    
    Thank you,
    Hospital Management System
    """
    
    try:
        if not Config.RESEND_API_KEY:
            return

        from_email = Config.RESEND_FROM_EMAIL or "Hospital Management System <onboarding@resend.dev>"
        resend.api_key = Config.RESEND_API_KEY
        resend.Emails.send({
            "from": from_email,
            "to": [email],
            "subject": subject,
            "text": body,
        })
    except Exception as e:
        print(f"Error sending password change alert: {e}")
