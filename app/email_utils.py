# app/email_utils.py
from flask_mail import Message
from app import mail
from config import Config

def send_email(to_email, subject, text_body, html_body=None):
    """
    Send email using Gmail SMTP
    """
    if not Config.MAIL_PASSWORD:
        print("⚠️ Email not configured. Set MAIL_PASSWORD in .env")
        print(f"\n📧 Would have sent to: {to_email}")
        print(f"   Subject: {subject}")
        print(f"   Body: {text_body[:200]}...")
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
        print(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        
        # Show helpful error messages
        if "authentication" in str(e).lower():
            print("   → Check your Gmail app password (use 16-char code, not regular password)")
            print("   → Enable 2-Step Verification in Google Account")
        elif "recipient" in str(e).lower():
            print("   → Check recipient email address")
        elif "connection" in str(e).lower():
            print("   → Check internet connection")
        
        return False