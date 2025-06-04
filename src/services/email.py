import smtplib
from email.mime.text import MIMEText
from src.core.config import settings

def send_register_otp_email(email: str, otp: str):
    msg = MIMEText(f"Your OTP for registration is: {otp}\nThis OTP will expire in {settings.OTP_EXPIRED_TIME} minutes.")
    msg['Subject'] = 'Registration OTP'
    msg['From'] = f"{settings.ADMIN_NAME} <{settings.ADMIN_EMAIL}>"
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(settings.ADMIN_EMAIL, settings.ADMIN_GMAIL_APP_PASSWORD)
        server.send_message(msg)