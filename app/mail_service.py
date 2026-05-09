# app/mail_service.py
from flask_mail import Message
from app import mail
from config import Config

def send_transactional_email(to_email, subject, text_body=None, html_body=None):
    """Send email using Gmail SMTP"""
    
    if not Config.MAIL_PASSWORD:
        print(f"⚠️ Email not configured. Would have sent to {to_email}")
        return None
    
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=text_body or "",
            html=html_body or "",
            sender=Config.MAIL_DEFAULT_SENDER
        )
        mail.send(msg)
        print(f"✅ Email sent to {to_email}")
        return type('Response', (), {'status_code': 200})()
        
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return None