import streamlit as st
from logics.accounts import add_user
from logics.database import db_connection

st.sidebar.page_link("main.py",           label="Login",    icon="🔐")
st.sidebar.page_link("pages/register.py", label="Register", icon="👤")
st.sidebar.page_link("pages/forgot.py",   label="Forgot",   icon="❓")


check_database_connectivity = st.checkbox('Database Connectivity')

if check_database_connectivity:
    db_connection()

with st.form("Sign Up Form"):
    email            = st.text_input("Email")
    col1, col2 = st.columns([1,1])
    with col1:
        first_name = st.text_input("First Name")
    with col2:
        last_name  = st.text_input("Last Name")
    dob              = st.date_input("Date of Birth")
    username         = st.text_input("Username (User ID)")
    col1, col2 = st.columns([1,1])
    with col1:
        password         = st.text_input("Password", type="password")
    with col2:
        confirm_password = st.text_input("Confirm Password", type="password")
    signup_button    = st.form_submit_button("Sign Up")

if signup_button and password == confirm_password:
    add_user(username, first_name, last_name, email, dob, password)
elif signup_button:
    st.error("Passwords do not match!")



