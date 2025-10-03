# utils.py
import os
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import random

SESSION_FILE = "session.txt"
AUTO_LOGIN_DAYS = 2

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            content = f.read().strip()
            if content:
                username, login_time_str = content.split(",")
                login_time = datetime.fromisoformat(login_time_str)
                if datetime.now() - login_time < timedelta(days=AUTO_LOGIN_DAYS):
                    return username
    return None

def save_session(username):
    with open(SESSION_FILE, "w") as f:
        f.write(f"{username},{datetime.now().isoformat()}")

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def send_otp(to_email, purpose="general"):
    otp = f"{random.randint(100000, 999999):06d}"  # 6-digit OTP
    sender_email = "smudrarag.work@gmail.com"
    app_password = "kejk seao givp zvvt"  # 16-char App Password

    # Purpose-based customization
    if purpose == "login":
        subject = "Your Login OTP"
        body = f"Your login OTP is: {otp}\n\nUse this to securely log in to your SamudraRAG account."
    elif purpose == "signup":
        subject = "Your Signup OTP"
        body = f"Welcome aboard! 🎉\n\nYour signup OTP is: {otp}\n\nEnter this to finish creating your account."
    elif purpose == "reset":
        subject = "Reset Password OTP"
        body = f"We got a request to reset your password.\n\nYour OTP is: {otp}\n\nIf this wasn't you, ignore this email."
    else:
        subject = "Your OTP Code"
        body = f"Your OTP is: {otp}"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    return otp
