from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config


def send_transactional_email(to_email, subject, text_body=None, html_body=None):
    """Send a transactional email using SendGrid Single Sender."""
    if not Config.SENDGRID_API_KEY:
        raise ValueError("SENDGRID_API_KEY is missing")

    if not Config.SENDGRID_FROM_EMAIL:
        raise ValueError("SENDGRID_FROM_EMAIL is missing")

    message = Mail(
        from_email=Config.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=text_body or "",
        html_content=html_body or "",
    )
    client = SendGridAPIClient(Config.SENDGRID_API_KEY)
    return client.send(message)
