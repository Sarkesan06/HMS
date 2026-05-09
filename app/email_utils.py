# app/email_utils.py
from flask_mail import Message
from app import mail
from config import Config

def send_email(to_email, subject, text_body, html_body=None):
    """
    Send email using Gmail SMTP only
    No SendGrid dependency
    """
    
    if not to_email or '@' not in to_email:
        print(f"⚠️ Invalid email address: {to_email}")
        return False
    
    # Check if email is configured
    if not Config.MAIL_PASSWORD:
        print(f"⚠️ Email not configured. MAIL_PASSWORD is missing")
        print(f"📧 Would have sent to: {to_email}")
        print(f"   Subject: {subject}")
        return False
    
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=text_body,
            html=html_body,
            sender=Config.MAIL_DEFAULT_SENDER
        )
        mail.send(msg)
        print(f"✅ Email sent via Gmail to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        
        # Helpful error messages
        error_msg = str(e).lower()
        if "authentication" in error_msg:
            print("   → Fix: Generate a new App Password at https://myaccount.google.com/apppasswords")
            print("   → Make sure 2-Step Verification is ON")
        elif "sender" in error_msg:
            print("   → Fix: Check MAIL_USERNAME and MAIL_DEFAULT_SENDER in config")
        elif "connection" in error_msg:
            print("   → Fix: Check internet connection or Render network settings")
        
        return False