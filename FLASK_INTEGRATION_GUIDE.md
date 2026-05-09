# Quick Integration Guide for Flask App

## Step 1: Update requirements.txt
Add the following packages:
```
pip install -r OAUTH_REQUIREMENTS.txt
```

## Step 2: Update your auth route file (app/routes/auth.py)

If you're using a Blueprint pattern, add this to your existing auth blueprint:

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import User
from app import db

# Your existing imports...

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Your existing auth routes (login, register, etc.)...

# Add Google Login
@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token
        import os
        
        data = request.get_json()
        token = data.get('token')
        email = data.get('email')
        name = data.get('name')
        picture = data.get('picture')
        
        if not all([token, email, name]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Verify token with Google
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com')
        
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
        except ValueError:
            return jsonify({'message': 'Invalid Google token'}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                email=email,
                name=name,
                auth_type='google',
                profile_picture=picture,
                password='oauth_user',
                role='patient'
            )
            db.session.add(user)
            db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'role': user.role
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Google login failed: {str(e)}'}), 500

# Add Facebook Login
@auth_bp.route('/facebook-login', methods=['POST'])
def facebook_login():
    try:
        import requests
        
        data = request.get_json()
        token = data.get('token')
        email = data.get('email')
        name = data.get('name')
        picture = data.get('picture')
        facebook_id = data.get('facebook_id')
        
        if not all([token, email, name, facebook_id]):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Verify token with Facebook
        verify_url = f"https://graph.facebook.com/me?fields=id,email,name&access_token={token}"
        response = requests.get(verify_url)
        profile_data = response.json()
        
        if 'error' in profile_data or profile_data.get('id') != facebook_id:
            return jsonify({'message': 'Invalid Facebook token'}), 400
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                email=email,
                name=name,
                auth_type='facebook',
                profile_picture=picture,
                facebook_id=facebook_id,
                password='oauth_user',
                role='patient'
            )
            db.session.add(user)
            db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'role': user.role
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Facebook login failed: {str(e)}'}), 500
```

## Step 3: Update your User model (app/models.py)

Make sure your User model has these additional fields:

```python
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password = db.Column(db.String(255))
    
    # OAuth fields
    auth_type = db.Column(db.String(20), nullable=True)  # 'email', 'google', 'facebook'
    profile_picture = db.Column(db.String(500), nullable=True)
    facebook_id = db.Column(db.String(120), unique=True, nullable=True)
    google_id = db.Column(db.String(250), unique=True, nullable=True)
    
    # User role
    role = db.Column(db.String(20), default='patient')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ... rest of your model
```

## Step 4: Create/Update your .env file

```
# Google OAuth
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com

# Facebook OAuth
FACEBOOK_APP_ID=YOUR_FACEBOOK_APP_ID
FACEBOOK_APP_SECRET=YOUR_FACEBOOK_APP_SECRET

# URLs
FRONTEND_URL=http://10.169.250.191:3000
BACKEND_URL=http://10.169.250.191:5000
```

## Step 5: Update your app/__init__.py

Make sure you're loading environment variables:

```python
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # ... your existing config ...
    
    # Register blueprints
    from app.routes import auth
    app.register_blueprint(auth.auth_bp)
    
    return app
```

## Troubleshooting

### Issue: Google SDK not loading
- Check that you have the correct Client ID
- Verify your domain is in authorized origins
- Check browser console for errors

### Issue: Facebook SDK not loading
- Verify you have the correct App ID
- Check that your domain is in App Domains
- Ensure cookies are enabled

### Issue: "Invalid token" error
- Make sure the token is being passed correctly from frontend
- Verify token hasn't expired
- Check that credentials match on both frontend and backend

### Issue: CORS errors
- Add CORS headers to your Flask app:
```python
from flask_cors import CORS
CORS(app)
```

## Testing

1. **Test Google Login:**
   - Open the page in a browser
   - Click the Google login button
   - Select your Google account
   - Check browser console for any errors
   - Should redirect to dashboard if successful

2. **Test Facebook Login:**
   - Open the page in a browser
   - Click the Facebook login button
   - Login with Facebook account
   - Grant required permissions
   - Should redirect to dashboard if successful

3. **Backend Testing:**
   ```bash
   # Test Google endpoint
   curl -X POST http://localhost:5000/auth/google-login \
     -H "Content-Type: application/json" \
     -d '{"token": "YOUR_GOOGLE_TOKEN", "email": "user@gmail.com", "name": "User Name", "picture": "URL"}'
   
   # Test Facebook endpoint
   curl -X POST http://localhost:5000/auth/facebook-login \
     -H "Content-Type: application/json" \
     -d '{"token": "YOUR_FB_TOKEN", "email": "user@fb.com", "name": "User Name", "picture": "URL", "facebook_id": "123456"}'
   ```
