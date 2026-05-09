from flask_mail import Message
from app import mail
from config import Config


def send_email(to_email, subject, text_body, html_body=None):
    """Send email using SMTP only (no Resend)."""

    if not to_email or '@' not in to_email:
        print(f"Invalid email address: {to_email}")
        return False

    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        print("Email not configured: MAIL_USERNAME or MAIL_PASSWORD is missing")
        return False

    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=text_body,
            html=html_body,
            sender=Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME,
        )
        mail.send(msg)
        print(f"Email sent successfully via SMTP to {to_email}")
        return True
    except Exception as e:
        print(f"SMTP email error: {str(e)}")
        return False


def send_recovery_email(email, code, name):
    """Simplified recovery email function"""

    subject = "Account Recovery - Hospital Management System"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1d3557; color: white; padding: 20px; text-align: center; }}
            .code {{ background: #f0f0f0; padding: 20px; font-size: 28px; font-weight: bold; text-align: center; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Hospital Management System</h2>
                <p>Account Recovery</p>
            </div>
            <div class="content">
                <p>Dear <strong>{name}</strong>,</p>
                <p>Your account recovery code is:</p>
                <div class="code">{code}</div>
                <p>This code will expire in <strong>15 minutes</strong>.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>Hospital Management System</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
Hospital Management System - Account Recovery

Dear {name},

Your account recovery code is: {code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Thank you,
Hospital Management System
"""

    return send_email(email, subject, text_body, html_body)
