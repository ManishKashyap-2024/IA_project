import streamlit as st
from logics.accounts import forgot_user_password, forgot_user_id

st.sidebar.page_link("main.py",           label="Login",    icon="🔐")
st.sidebar.page_link("pages/register.py", label="Register", icon="👤")
st.sidebar.page_link("pages/forgot.py",   label="Forgot",   icon="❓")

# Create tabs
tab1, tab2 = st.tabs(["Forgot Password", "Forgot ID"])

# Tab 1: Forgot Password
with tab1:
    with st.form("Forgot User Password Form"):
        email               = st.text_input("Email")
        forgot_email_button = st.form_submit_button("Forgot Password")

    if forgot_email_button:
        forgot_user_password()


# Tab 2: Forgot ID
with tab2:
    with st.form("Forgot User ID Form"):
        col1, col2 = st.columns([1,1])
        with col1:
            first_name  = st.text_input("First Name")
        with col2:
            last_name   = st.text_input("Last Name")
        forgot_id_button = st.form_submit_button("Forgot ID")

    if forgot_id_button:
        forgot_user_id()
        