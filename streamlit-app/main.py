import streamlit as st
from login_module import auth_ui, clear_session  # import login/signup module
import time
import os

# ------------------------------
# Run authentication UI
# ------------------------------
if "redirect_to_chat" not in st.session_state:
    st.session_state.redirect_to_chat = False

# auth_ui() sets st.session_state.username
auth_ui()

# If just logged in, show spinner then redirect
if st.session_state.username and not st.session_state.redirect_to_chat:
    with st.spinner("🌊 Logging in..."):
        time.sleep(2)  # simulate processing time
    st.session_state.redirect_to_chat = True
    st.rerun()  # refresh app to show main chat UI

# ------------------------------
# Main chat app code
# ------------------------------
if st.session_state.username and st.session_state.redirect_to_chat:
    st.title("🌊 SamudraRAG Chat")

    # Initialize message history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🌊 Welcome to SamudraRAG! How can I help you explore the ocean today?"}
        ]

    # Mock AI response function
    def generate_response(user_input):
        time.sleep(0.5)
        import random
        responses = [
            f"That's an interesting question about '{user_input}'! Let me help you with that.",
            f"I understand you're asking about '{user_input}'. Here's what I know...",
            f"Great question! Regarding '{user_input}', I can tell you that..."
        ]
        return random.choice(responses)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Explore the Ocean..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("🌊 Thinking..."):
                response = generate_response(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Sidebar
    with st.sidebar:
        st.subheader(f"👤 {st.session_state.username}")
        st.markdown("---")
        
        st.subheader("Chat History")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [{"role": "assistant", "content": "🌊 Chat cleared! How can I help you?"}]
            st.rerun()
        
        st.markdown("----")
    
        # Logout button
        if st.button("🚪 Logout"):
            keys_to_clear = [
                "username", "messages",
                # forgot password flow
                "fp_step", "fp_username_value", "fp_email_value", "generated_otp",
                # signup flow
                "signup_step", "signup_data", "otp_step",
                # login flow
                "login_user", "login_email"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
    
            clear_session()  # clears session.txt file
            st.rerun()
        
        st.markdown("---")
    
    # Delete Account modal
    # Sidebar Delete Account button
    if "show_delete_form" not in st.session_state:
        st.session_state.show_delete_form = False

    if st.sidebar.button("🗑️ Delete Account") and st.session_state.username != "admin":
        st.session_state.show_delete_form = True

    # Delete Account form modal
    if st.session_state.show_delete_form:
        with st.form("delete_account_form"):
            st.error("⚠️ This action is permanent! Once deleted, your account **cannot be recovered**.")

            allow_delete = st.checkbox("✅ Allow account deletion")

            confirm = st.form_submit_button("Confirm Delete")

            if confirm:
                if allow_delete:
                    with st.spinner("Deleting your account... ⏳"):
                        import pandas as pd
                        time.sleep(2)

                        # Delete account from CSV
                        users_df = pd.read_csv("users.csv")
                        username = st.session_state.username
                        users_df = users_df[users_df["Username"] != username]
                        users_df.to_csv("users.csv", index=False)

                        # Clear session and username
                        clear_session()
                        if "username" in st.session_state:
                            del st.session_state["username"]

                        st.success("Your account has been deleted permanently 😢")
                        st.rerun()  # this will redirect them to login
                else:
                    st.warning("You must check 'Allow account deletion' before confirming!")

