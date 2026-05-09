from flask_mail import Message
from app import mail
from config import Config
import base64
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests


def _send_email_via_gmail_api(to_email, subject, text_body, html_body=None):
    """
    Send email via Gmail REST API using OAuth refresh token flow.
    Required env vars:
    - GMAIL_CLIENT_ID
    - GMAIL_CLIENT_SECRET
    - GMAIL_REFRESH_TOKEN
    - GMAIL_SENDER_EMAIL (optional; defaults to MAIL_USERNAME)
    """
    client_id = os.getenv("GMAIL_CLIENT_ID", "").strip()
    client_secret = os.getenv("GMAIL_CLIENT_SECRET", "").strip()
    refresh_token = os.getenv("GMAIL_REFRESH_TOKEN", "").strip()
    sender = (os.getenv("GMAIL_SENDER_EMAIL", "") or Config.MAIL_USERNAME).strip()

    if not client_id or not client_secret or not refresh_token or not sender:
        return False

    try:
        token_res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10,
        )
        if token_res.status_code != 200:
            print(f"Gmail API token error {token_res.status_code}: {token_res.text}")
            return False

        access_token = token_res.json().get("access_token")
        if not access_token:
            print("Gmail API token error: access_token missing")
            return False

        msg = MIMEMultipart("alternative")
        msg["To"] = to_email
        msg["From"] = sender
        msg["Subject"] = subject
        msg.attach(MIMEText(text_body or "", "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        send_res = requests.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            data=json.dumps({"raw": raw_message}),
            timeout=10,
        )

        if 200 <= send_res.status_code < 300:
            print(f"Email sent via Gmail API to {to_email}")
            return True

        print(f"Gmail API send error {send_res.status_code}: {send_res.text}")
        return False
    except Exception as exc:
        print(f"Gmail API exception: {exc}")
        return False


def send_email(to_email, subject, text_body, html_body=None):
    """Send email using SMTP only (no Resend)."""

    if not to_email or '@' not in to_email:
        print(f"Invalid email address: {to_email}")
        return False

    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        # Try Gmail API path first when SMTP credentials are not configured/reachable.
        if _send_email_via_gmail_api(to_email, subject, text_body, html_body):
            return True
        print("Email not configured: SMTP and Gmail API credentials missing")
        return False

    # Prefer Gmail API on cloud hosts to avoid SMTP egress/network blocks.
    if _send_email_via_gmail_api(to_email, subject, text_body, html_body):
        return True

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
