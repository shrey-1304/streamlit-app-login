# login_module.py
import streamlit as st
import pandas as pd
import os
import hashlib
import re
import time
from datetime import datetime, timedelta
from fp import reset_password
import smtplib
import random
from email.message import EmailMessage
from utils import load_session, save_session, clear_session

USERS_FILE = "users.csv"
SESSION_FILE = "session.txt"
AUTO_LOGIN_DAYS = 2
prop_em= ""

# ----------------- Initialize session state -----------------
def send_otp(to_email, purpose="generic"):
    otp = f"{random.randint(100000, 999999):06d}"  # 6-digit OTP
    sender_email = "smudrarag.work@gmail.com"
    app_password = "kejk seao givp zvvt"  # 16-char App Password

    # Custom email subjects
    subjects = {
        "login": "🔐 Your Login OTP",
        "signup": "✨ Verify Your Account",
        "generic": "Your OTP Code"
    }

    # Custom email bodies
    bodies = {
        "login": f"Hello!\n\nUse this OTP to log in securely:\n\n{otp}\n\nIf you didn’t request this, ignore this email.",
        "signup": f"Welcome to SamudraRAG! 🎉\n\nUse this OTP to verify your account:\n\n{otp}\n\nGlad to have you onboard!",
        "generic": f"Your OTP is: {otp}"
    }

    msg = EmailMessage()
    msg["Subject"] = subjects.get(purpose, subjects["generic"])
    msg["From"] = sender_email
    msg["To"] = to_email
    msg.set_content(bodies.get(purpose, bodies["generic"]))

    with st.spinner("Sending OTP... ⏳"):
        time.sleep(1)  # simulate sending delay
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

    return otp

# ----------------- Helpers -----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        return pd.DataFrame(columns=["Username", "Email", "Password"])


def save_session(username):
    with open(SESSION_FILE, "w") as f:
        f.write(f"{username},{datetime.now().isoformat()}")

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# ----------------- Validation -----------------
def is_valid_username(username):
    return bool(re.match(r'^[A-Za-z0-9_]+$', username))

def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[@!#$&*]', password):
        return False, "Password must contain at least one special character (@!#$&*)."
    return True, ""

def is_valid_email(email):
    # Only allow Gmail addresses
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email))


# ----------------- Auth UI -----------------
def auth_ui():
    users_df = load_users()
    if "otp_step" not in st.session_state:
        st.session_state.otp_step = "none"

    if "username" not in st.session_state:
        st.session_state.username = None


    # Load session if available
    if st.session_state.username is None:
        session_user = load_session()
        if session_user:
            st.session_state.username = session_user

    if st.session_state.username:
        return  # already logged in, don’t show login UI

    st.title("🌊 SamudraRAG Login")
    st.markdown("<i>*Enter your credentials to continue*</i>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    # ----------------- Signup -----------------
    with tab2:
        st.subheader("Create a new account")

        if "signup_step" not in st.session_state:
            st.session_state.signup_step = "input"

        if st.session_state.signup_step == "input":
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
            if new_email != "" and  not is_valid_email(new_email):
                        st.error("Enter a valid Gmail address!")
            if st.button("Sign Up"):
                if new_username and new_email and new_password and confirm_password:
                    # Validate email first
                    if not is_valid_email(new_email):
                        st.error("Enter a valid Gmail address!")
                    elif len(new_username) < 4:
                        st.error("Username should be at least 4 letters long")
                    elif not is_valid_username(new_username):
                        st.error("Username can only contain letters, digits, and underscores.")
                    elif new_username in users_df["Username"].values:
                        st.error("Username already exists! Pick another one.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match! 🔒")
                    elif new_email in users_df["Email"].values:
                        st.error("Email is already registered! Use another one.")
                    else:
                        valid, message = is_valid_password(new_password)
                        if not valid:
                            st.error(f"Invalid password: {message}")
                        else:
                            # Only now send OTP
                            try:
                                st.session_state.generated_otp = send_otp(new_email, purpose="signup")
                            except Exception:
                                st.error("Failed to send OTP. Make sure this Gmail exists!")
                                st.stop()
                            
                            st.session_state.signup_data = {
                                "Username": new_username,
                                "Email": new_email,
                                "Password": new_password
                            }
                            st.session_state.signup_step = "otp"
                            prop_em = new_email
                            st.rerun()

                        
                else:
                    st.warning("Fill in all fields!")

        elif st.session_state.signup_step == "otp":
            st.success(f"✅ OTP sent to {st.session_state.signup_data['Email']}")
            otp_input = st.text_input("Enter OTP:", key=f"otp_{st.session_state.otp_step}")
            
            if st.button("Verify OTP"):
                if otp_input == st.session_state.generated_otp:
                    # Hash password & save user
                    hashed_pw = hash_password(st.session_state.signup_data["Password"])
                    users_df = pd.concat([
                        users_df,
                        pd.DataFrame([{
                            "Username": st.session_state.signup_data["Username"],
                            "Email": st.session_state.signup_data["Email"],
                            "Password": hashed_pw
                        }])
                    ], ignore_index=True)
                    users_df.to_csv(USERS_FILE, index=False)

                    # Spinner + auto-login
                    with st.spinner("Account created... logging in ⏳"):
                        time.sleep(2)
                    st.success("Signup & login successful! ✅")

                    st.session_state.username = st.session_state.signup_data["Username"]
                    save_session(st.session_state.username)

                    # Clean up OTP & temp data
                    del st.session_state.signup_data
                    del st.session_state.generated_otp
                    del st.session_state.signup_step

                    st.rerun()
                else:
                    st.error("Incorrect OTP!")

    # ----------------- Login -----------------
    with tab1:
        if "fp" not in st.session_state:
            st.session_state.fp = False

        if st.session_state.fp:
            # Only show forgot password UI
            reset_password()
        else:
            # Login form only shows when fp is False
            username_input = st.text_input("Username", key="login_username")
            password_input = st.text_input("Password", type="password", key="login_password")
            col1, col2 = st.columns([7,2])
            with col2:
                if st.button("Forgot password?"):
                    st.session_state.fp = True
                    st.rerun()
                
            with col1:
                if st.button("Login"):
                    if username_input and password_input:
                        hashed_input = hash_password(password_input)
                        user_row = users_df[(users_df["Username"]==username_input) & 
                                            (users_df["Password"]==hashed_input)]
                        if not user_row.empty:
                            st.session_state.otp_step = "send"
                            st.session_state.login_user = username_input
                            st.session_state.login_email = user_row.iloc[0]["Email"]
                            try:
                                st.session_state.generated_otp = send_otp(st.session_state.login_email, purpose="login")
                            except Exception as e:
                                st.error("Failed to send OTP. Check the email!")
                                st.stop()

                            st.rerun()
                        else:
                            st.error("Invalid username or password!")


        # OTP flow
        if "otp_step" in st.session_state:
            if st.session_state.otp_step == "send":
                st.session_state.generated_otp = send_otp(st.session_state.login_email, purpose="login")  # spinner + custom email
                
                st.session_state.otp_step = "verify"
                st.rerun()
            elif st.session_state.otp_step == "verify":
                st.success(f"OTP sent to {st.session_state.login_email}")  
                otp_input = st.text_input("Enter OTP:", key=f"otp_{st.session_state.otp_step}")
                if st.button("Verify OTP"):
                    if otp_input == st.session_state.generated_otp:
                        with st.spinner("Logging in... ⏳"):
                            time.sleep(2)
                        st.success("Login successful! ✅")
                        st.session_state.username = st.session_state.login_user
                        save_session(st.session_state.username)
                        del st.session_state.otp_step
                        del st.session_state.generated_otp
                        st.rerun()
                    else:
                        st.error("Incorrect OTP!")
        st.stop()
