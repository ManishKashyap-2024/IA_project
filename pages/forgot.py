import streamlit as st
from logics.accounts import forgot_user_id, reset_password
from logics.database import forgot_password
from logics.database import create_connection

st.sidebar.page_link("main.py",           label="Login",    icon="🔐")
st.sidebar.page_link("pages/register.py", label="Register", icon="👤")
st.sidebar.page_link("pages/forgot.py",   label="Forgot Credential",   icon="❓")

# Create tabs
tab1, tab2 = st.tabs(["Forgot Password", "Forgot ID"])

# Tab 1: Forgot Password
with tab1:
    with st.form("Forgot User Password Form"):
        email               = st.text_input("Email")
        forgot_email_button = st.form_submit_button("Forgot Password")

    if forgot_email_button:
        connection         = create_connection()
        success, user_data = forgot_password(connection, email)
        if success:
            reset_password(email,user_data, connection)  # Use the result in another function
        else:
            st.error("Email not found.")

        connection.close()
        


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
        forgot_user_id(first_name, last_name)


        