# app/email_utils.py
from flask_mail import Message
from app import mail
from config import Config
import logging

def send_email(to_email, subject, text_body, html_body=None):
    """
    Send email using configured method (Gmail SMTP or SendGrid)
    Works on Render.com deployment
    """
    
    if not to_email or '@' not in to_email:
        print(f"⚠️ Invalid email address: {to_email}")
        return False
    
    # Method 1: Try Gmail SMTP first
    if Config.MAIL_PASSWORD:
        try:
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=text_body,
                html=html_body,
                sender=Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
            )
            mail.send(msg)
            print(f"✅ Email sent via Gmail SMTP to {to_email}")
            return True
        except Exception as e:
            print(f"⚠️ Gmail SMTP failed: {str(e)}")
    
    # Method 2: Try SendGrid as fallback
    if Config.SENDGRID_API_KEY:
        try:
            from app.mail_service import send_transactional_email
            response = send_transactional_email(to_email, subject, text_body, html_body)
            if response and response.status_code in [200, 202]:
                print(f"✅ Email sent via SendGrid to {to_email}")
                return True
        except Exception as e:
            print(f"⚠️ SendGrid failed: {str(e)}")
    
    # Method 3: Log email (for debugging on Render)
    print(f"\n{'='*60}")
    print(f"📧 EMAIL (Would be sent in production)")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {text_body[:500]}")
    print(f"{'='*60}\n")
    
    return False