import streamlit as st
from logics.accounts import add_user
from logics.database import db_connection
import time

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #3e3e40;
    }
</style>
""", unsafe_allow_html=True)
with st.sidebar:
        st.image("./Animations/stock.png", 
                #caption="Your PNG caption",
                width=350)

st.sidebar.page_link("main.py",           label="Login",    icon="🔐")
st.sidebar.page_link("pages/register.py", label="Register", icon="👤")
st.sidebar.page_link("pages/forgot.py",   label="Forgot Credential",   icon="❓")

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
    # Display progress bar for 3 seconds
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.03)
        progress_bar.progress(i + 1) 
    st.error("Passwords do not match!")



