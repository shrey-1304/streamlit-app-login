from utils import save_session
import streamlit as st
import pandas as pd
import os
import hashlib
import random
import smtplib
from email.message import EmailMessage
import time
USERS_FILE = "users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=["Username", "Email", "Password"])

def send_otp(to_email, purpose="login"):
    otp = f"{random.randint(100000, 999999):06d}"
    sender_email = "smudrarag.work@gmail.com"
    app_password = "kejk seao givp zvvt"  

    msg = EmailMessage()

    # Customize subject and body based on purpose
    if purpose == "login":
        msg["Subject"] = "Your Login OTP 🔐"
        msg.set_content(f"Your login OTP is: {otp}\n\nIf this wasn’t you, ignore this email.")
    elif purpose == "signup":
        msg["Subject"] = "Verify Your Account ✨"
        msg.set_content(f"Welcome! 🎉\nYour signup OTP is: {otp}\n\nEnter this to complete your registration.")
    elif purpose == "reset":
        msg["Subject"] = "Reset Your Password 🔑"
        msg.set_content(f"Your password reset OTP is: {otp}\n\nUse this to set a new password.")
    else:
        msg["Subject"] = "Your OTP Code"
        msg.set_content(f"Your OTP is: {otp}")

    msg["From"] = sender_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    return otp


def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c in "@!#$&*" for c in password):
        return False, "Password must contain at least one special character (@!#$&*)."
    return True, ""

def reset_password():
    users_df = load_users()
    st.info("Reset your password 🔑")

    # Step 0: Initialize
    if "fp_step" not in st.session_state:
        st.session_state.fp_step = "input"


    # Step 1: Enter username OR email
    if st.session_state.fp_step == "input":
        fp_user = st.text_input("Enter Username or Registered Email", key="fp_user")
        col1, col2 = st.columns([9,3])
        with col2:
            if st.button("Next", key="fp_next"):
                if not fp_user:
                    st.warning("Enter something!")
                else:
                    # Find user by username or email
                    user_row = users_df[(users_df["Username"]==fp_user) | (users_df["Email"]==fp_user)]
                    if user_row.empty:
                        st.error("No user found with this Username or Email!")
                    else:
                        st.session_state.fp_username_value = user_row.iloc[0]["Username"]
                        st.session_state.fp_email_value = user_row.iloc[0]["Email"]
                        
                        # ✅ Proper spinner context
                        with st.spinner():
                            time.sleep(1)  # simulate delay
                            st.session_state.generated_otp = send_otp(st.session_state.fp_email_value, purpose="reset")
                        
                        st.success(f"✅ OTP sent to {st.session_state.fp_email_value}")
                        st.session_state.fp_step = "verify_otp"
                        st.rerun()

        with col1:
            if st.button("Back to Login"):
                st.session_state.fp = False
                st.rerun()

    # Step 2: Verify OTP
    elif st.session_state.fp_step == "verify_otp":
        
        otp_input = st.text_input("Enter OTP", key="fp_otp_input")
        if st.button("Verify OTP", key="fp_verify_btn"):
            if otp_input == st.session_state.generated_otp:
                st.session_state.fp_step = "reset_password"
                st.rerun()
            else:
                st.error("Incorrect OTP!")

    # Step 3: Reset Password
    elif st.session_state.fp_step == "reset_password":
        fp_new_password = st.text_input("New Password", type="password", key="fp_new_password")
        fp_confirm_password = st.text_input("Confirm New Password", type="password", key="fp_confirm_password")
        if st.button("Reset Password", key="fp_reset_btn"):
            if fp_new_password and fp_confirm_password:
                if fp_new_password != fp_confirm_password:
                    st.error("Passwords do not match!")
                else:
                    valid, msg = is_valid_password(fp_new_password)
                    if not valid:
                        st.error(f"Invalid password: {msg}")
                    else:
                        # Update password in CSV
                        users_df.loc[users_df["Username"]==st.session_state.fp_username_value, "Password"] = hash_password(fp_new_password)
                        users_df.to_csv(USERS_FILE, index=False)

                        # ✅ Auto-login
                        st.session_state.username = st.session_state.fp_username_value
                        save_session(st.session_state.username)
                        st.success("✅ Password reset successful! You are now logged in.")

                        # Clean temp vars
                        for key in ["fp_username_value","fp_email_value","generated_otp","fp_step"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
            else:
                st.warning("Fill in both fields!")



