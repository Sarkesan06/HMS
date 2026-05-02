"""
OAuth Authentication Handlers for Google and Facebook
Add this to your app/routes/auth.py file
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import os
from datetime import datetime
import google.oauth2.id_token
from google.auth.transport import requests
from datetime import datetime, timedelta

# Assuming you have a User model and db instance imported
# from app.models import User
# from app import db

def setup_oauth_routes(auth_bp, User, db):
    """
    Setup OAuth routes for Google and Facebook login
    
    Usage in your app/__init__.py:
    from app.routes.oauth_handlers import setup_oauth_routes
    setup_oauth_routes(auth_bp, User, db)
    """
    
    # Google Login Endpoint
    # Add this to your app/routes/auth.py

    # Add these imports at the top of auth.py


# ================= GOOGLE LOGIN FOR ALL ROLES =================
    @auth_bp.route('/google-login', methods=['POST'])
    def google_login():
        try:
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({'message': 'No token provided'}), 400
            
            GOOGLE_CLIENT_ID = '633988002854-tea7qq18oigrdg0kqen1l7ohupoibl04.apps.googleusercontent.com'
            
            try:
                # Verify the token with Google
                idinfo = google.oauth2.id_token.verify_oauth2_token(
                    token, 
                    requests.Request(), 
                    GOOGLE_CLIENT_ID
                )
                
                email = idinfo.get('email')
                name = idinfo.get('name', email.split('@')[0])
                picture = idinfo.get('picture', '')
                
                # ========== CHECK IN ALL COLLECTIONS IN ORDER ==========
                
                # 1. Check DOCTOR collection first
                doctor = mongo.db.doctors.find_one({"email": email})
                if doctor:
                    # Update last login
                    mongo.db.doctors.update_one(
                        {"email": email},
                        {"$set": {
                            "last_login": datetime.utcnow(),
                            "profile_picture": picture
                        }}
                    )
                    # Create access token with doctor role
                    access_token = create_access_token(
                        identity=email,
                        expires_delta=timedelta(hours=24),
                        additional_claims={"role": "doctor"}
                    )
                    return jsonify({
                        'access_token': access_token,
                        'role': 'doctor',
                        'email': email,
                        'name': doctor.get('name', name),
                        'message': 'Doctor login successful'
                    }), 200
                
                # 2. Check ADMIN collection
                admin = mongo.db.admins.find_one({"email": email})
                if admin:
                    # Update last login
                    mongo.db.admins.update_one(
                        {"email": email},
                        {"$set": {
                            "last_login": datetime.utcnow(),
                            "profile_picture": picture
                        }}
                    )
                    # Create access token with admin role
                    access_token = create_access_token(
                        identity=email,
                        expires_delta=timedelta(hours=24),
                        additional_claims={"role": "admin"}
                    )
                    return jsonify({
                        'access_token': access_token,
                        'role': 'admin',
                        'email': email,
                        'name': admin.get('name', name),
                        'message': 'Admin login successful'
                    }), 200
                
                # 3. Check PATIENT collection
                patient = mongo.db.patients.find_one({"email": email})
                
                if patient:
                    # Update existing patient
                    mongo.db.patients.update_one(
                        {"email": email},
                        {"$set": {
                            "name": name,
                            "profile_picture": picture,
                            "last_login": datetime.utcnow()
                        }}
                    )
                    role = 'patient'
                    user_id = str(patient['_id'])
                else:
                    # Create NEW patient
                    patient_data = {
                        "name": name,
                        "email": email,
                        "role": "patient",
                        "password": "",
                        "age": "Not specified",
                        "gender": "Not specified",
                        "phone": "Not specified",
                        "profile_picture": picture,
                        "auth_type": "google",
                        "created_at": datetime.utcnow(),
                        "last_login": datetime.utcnow()
                    }
                    result = mongo.db.patients.insert_one(patient_data)
                    role = 'patient'
                    user_id = str(result.inserted_id)
                
                # Create access token with patient role
                access_token = create_access_token(
                    identity=email,
                    expires_delta=timedelta(hours=24),
                    additional_claims={"role": role}
                )
                
                return jsonify({
                    'access_token': access_token,
                    'role': role,
                    'email': email,
                    'name': name,
                    'user_id': user_id,
                    'message': f'{role.capitalize()} login successful'
                }), 200
                
            except ValueError as e:
                print(f"Invalid Google token: {e}")
                return jsonify({'message': 'Invalid Google token'}), 400
                
        except Exception as e:
            print(f"Google login error: {str(e)}")
            return jsonify({'message': str(e)}), 500
        

    # Facebook Login Endpoint
    @auth_bp.route('/facebook-login', methods=['POST'])
    def facebook_login():
        """
        Handle Facebook OAuth login
        
        Expected JSON body:
        {
            "token": "facebook_access_token",
            "email": "user@example.com",
            "name": "User Name",
            "picture": "https://...",
            "facebook_id": "123456789"
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'No data provided'}), 400
            
            token = data.get('token')
            email = data.get('email')
            name = data.get('name')
            picture = data.get('picture')
            facebook_id = data.get('facebook_id')
            
            if not all([token, email, name, facebook_id]):
                return jsonify({'message': 'Missing required fields'}), 400
            
            # Get Facebook App ID from environment or config
            facebook_app_id = os.getenv('FACEBOOK_APP_ID', 'YOUR_FACEBOOK_APP_ID')
            facebook_app_secret = os.getenv('FACEBOOK_APP_SECRET', 'YOUR_FACEBOOK_APP_SECRET')
            
            try:
                # Verify token with Facebook Graph API
                import requests
                
                verify_url = f"https://graph.facebook.com/me?fields=id,email,name&access_token={token}"
                response = requests.get(verify_url)
                profile_data = response.json()
                
                if 'error' in profile_data:
                    return jsonify({'message': 'Invalid Facebook token'}), 400
                
                if profile_data.get('id') != facebook_id:
                    return jsonify({'message': 'Facebook ID mismatch'}), 400
                
            except Exception as e:
                return jsonify({'message': f'Facebook verification failed: {str(e)}'}), 400
            
            # Check if user exists by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Check if user exists by facebook_id (if field exists)
                if hasattr(User, 'facebook_id'):
                    user = User.query.filter_by(facebook_id=facebook_id).first()
            
            if not user:
                # Create new user from Facebook OAuth
                try:
                    user = User(
                        email=email,
                        name=name,
                        auth_type='facebook',
                        profile_picture=picture,
                        facebook_id=facebook_id,
                        password='oauth_user',  # Dummy password for OAuth users
                        role='patient'  # Default role
                    )
                    db.session.add(user)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': f'Error creating user: {str(e)}'}), 500
            else:
                # Update user if they sign in with Facebook
                if user.auth_type is None:
                    user.auth_type = 'facebook'
                if hasattr(user, 'facebook_id') and not user.facebook_id:
                    user.facebook_id = facebook_id
                if not user.profile_picture:
                    user.profile_picture = picture
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': f'Error updating user: {str(e)}'}), 500
            
            # Generate JWT access token
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'access_token': access_token,
                'role': user.role,
                'message': 'Facebook login successful',
                'user_id': user.id,
                'email': user.email
            }), 200
            
        except Exception as e:
            print(f"Facebook login error: {str(e)}")
            return jsonify({'message': f'Facebook login failed: {str(e)}'}), 500
    
    return auth_bp
