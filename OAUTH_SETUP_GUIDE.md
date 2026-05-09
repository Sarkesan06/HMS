# Google and Facebook OAuth Setup Guide

This guide will help you set up Google and Facebook login for your Hospital Management System.

## 1. Google OAuth Setup

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name (e.g., "Hospital Management System")
5. Click "CREATE"

### Step 2: Enable Google Sign-In API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Identity Services API"
3. Click on it and press "ENABLE"

### Step 3: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" > "OAuth client ID"
3. If prompted to set up consent screen:
   - Click "Configure Consent Screen"
   - Select "External" for user type
   - Fill in the required fields:
     - App name: "Hospital Management System"
     - User support email: your email
     - Developer contact: your email
   - Click "SAVE AND CONTINUE"
   - Add scopes: `email`, `profile`
   - Click "SAVE AND CONTINUE"
   - Review and click "BACK TO DASHBOARD"

4. Now create the OAuth client ID:
   - Application type: "Web application"
   - Name: "Hospital Management System Web Client"
   - Authorized JavaScript origins: 
     - `http://localhost:3000`
     - `http://10.169.250.191:5000`
     - `http://yourdomain.com`
   - Authorized redirect URIs:
     - `http://localhost:3000/`
     - `http://10.169.250.191:5000/`
     - `http://yourdomain.com/`
   - Click "CREATE"

5. Copy your **Client ID** and replace `YOUR_GOOGLE_CLIENT_ID` in `frontend/index.html` at line 8

### Step 4: Update Frontend
In `frontend/index.html`, replace:
```javascript
client_id: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'
```

---

## 2. Facebook OAuth Setup

### Step 1: Create a Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" > "Create App"
3. Select "Consumer" as the app type
4. Fill in the app details:
   - App Name: "Hospital Management System"
   - App Purpose: Select relevant category
   - App Contact Email: your email
5. Click "Create App"

### Step 2: Add Facebook Login Product
1. In your app dashboard, click "Add Product"
2. Find "Facebook Login" and click "Set Up"
3. Choose "Web" as your platform
4. Click "Next"

### Step 3: Configure Facebook Login Settings
1. Go to Settings > Basic (copy your App ID)
2. Go to Settings > Basic and add:
   - App Domains: 
     - `localhost`
     - `10.169.250.191`
     - `yourdomain.com`
   - Privacy Policy URL: (if you have one)
   - Terms of Service URL: (if you have one)

3. Go to Facebook Login > Settings:
   - Valid OAuth Redirect URIs:
     - `http://localhost:3000/`
     - `http://10.169.250.191:5000/`
     - `http://yourdomain.com/`
   - Deselected Redirect URL Validation (for development)
   - Click "Save Changes"

### Step 4: Update Frontend
In `frontend/index.html`:
- Replace `YOUR_FACEBOOK_APP_ID` with your Facebook App ID (2 places)

---

## 3. Backend Setup (Python/Flask)

Add these endpoints to your Flask application (`app/routes/auth.py`):

```python
from flask import request, jsonify
from google.auth.transport import requests
from google.oauth2 import id_token
import facebook
import requests as http_requests
from app.models import User  # Adjust based on your model
from app import db

# Google Login Endpoint
@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        token = data.get('token')
        email = data.get('email')
        name = data.get('name')
        picture = data.get('picture')
        
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com'
        )
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user with OAuth
            user = User(
                email=email,
                name=name,
                auth_type='google',
                profile_picture=picture,
                password='oauth'  # Set a dummy password for OAuth users
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update user if they sign in with Google
            if not user.auth_type:
                user.auth_type = 'google'
            if not user.profile_picture:
                user.profile_picture = picture
            db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'role': user.role,
            'message': 'Google login successful'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Google login failed: {str(e)}'}), 400

# Facebook Login Endpoint
@auth_bp.route('/facebook-login', methods=['POST'])
def facebook_login():
    try:
        data = request.get_json()
        token = data.get('token')
        email = data.get('email')
        name = data.get('name')
        picture = data.get('picture')
        facebook_id = data.get('facebook_id')
        
        # Verify token with Facebook
        graph = facebook.GraphAPI(access_token=token)
        profile = graph.get_object(id='me', fields='id,email,name')
        
        if profile.get('id') != facebook_id:
            return jsonify({'message': 'Invalid Facebook token'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user with OAuth
            user = User(
                email=email,
                name=name,
                auth_type='facebook',
                profile_picture=picture,
                facebook_id=facebook_id,
                password='oauth'  # Set a dummy password for OAuth users
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update user if they sign in with Facebook
            if not user.auth_type:
                user.auth_type = 'facebook'
            if not user.facebook_id:
                user.facebook_id = facebook_id
            if not user.profile_picture:
                user.profile_picture = picture
            db.session.commit()
        
        # Generate JWT token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'role': user.role,
            'message': 'Facebook login successful'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Facebook login failed: {str(e)}'}), 400
```

### Required Python Packages
Add to `requirements.txt`:
```
google-auth>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=0.4.0
facebook-sdk>=3.0.0
```

### Update User Model
Make sure your `User` model in `app/models.py` has these fields:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password = db.Column(db.String(255))
    auth_type = db.Column(db.String(20))  # 'email', 'google', 'facebook'
    profile_picture = db.Column(db.String(500))
    facebook_id = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(20), default='patient')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 4. Installation & Configuration

### Install Dependencies
```bash
pip install -r requirements.txt
pip install google-auth google-auth-httplib2 google-auth-oauthlib facebook-sdk
```

### Environment Variables (Optional but Recommended)
Create a `.env` file:
```
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com
FACEBOOK_APP_ID=YOUR_FACEBOOK_APP_ID
FRONTEND_URL=http://10.169.250.191:3000
BACKEND_URL=http://10.169.250.191:5000
```

---

## 5. Testing

1. **Google Login Test:**
   - Click "Google" button on login page
   - Select your Google account
   - You should be logged in and redirected to dashboard

2. **Facebook Login Test:**
   - Click "Facebook" button on login page
   - Enter Facebook credentials
   - Grant permissions
   - You should be logged in and redirected to dashboard

---

## 6. Troubleshooting

### Google Login Issues
- **"Invalid Client ID"**: Check that client ID matches in frontend and backend
- **"Redirect URI mismatch"**: Add all your URLs to Google Cloud Console
- **CORS errors**: Ensure frontend URL is in authorized origins

### Facebook Login Issues
- **"Invalid App ID"**: Check that App ID is correct
- **"Redirect URI mismatch"**: Add URL to Facebook app settings
- **"Permission denied"**: User hasn't granted email permission

### General Issues
- Check browser console for errors (F12)
- Check Flask server logs
- Verify API keys and tokens are valid
- Clear browser cookies and try again

---

## 7. Security Notes

1. **Never expose client secrets** in frontend code
2. **Always verify tokens** on the backend
3. **Use HTTPS in production** (not just HTTP)
4. **Store user data securely** with proper encryption
5. **Implement rate limiting** on auth endpoints
6. **Log suspicious login attempts**

---

## Additional Resources

- [Google Sign-In Documentation](https://developers.google.com/identity/gsi/web)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
