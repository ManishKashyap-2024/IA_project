import streamlit as st
from logics.database import *

from streamlit_extras.switch_page_button import switch_page

from logics.send_email import send_email
from pages.admin import admin_login
def login():
    # Create tabs
    tab1, tab2 = st.tabs(["User", "Admin"])

    # Tab 1: Login
    with tab1:
        # Input fields for User ID and Password
        with st.form("Login Form"):
            user_id_input       = st.text_input("User Email", key="user_email_input")
            user_password_input = st.text_input("Password", type="password", key="user_password_input")
            # Login button
            user_login_button = st.form_submit_button("Login")

        if user_login_button:
            connection = create_connection()
            if connection:
                if check_login_credentials(connection, user_id_input, user_password_input):
                    # Display progress bar for 3 seconds
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)  
                    time.sleep(5)                       
                    st.success("Login successful!")
                    # Set session state to indicate the user is logged in
                    st.session_state['logged_in'] = True
                    st.session_state['user_id']   = user_id_input

                    # Redirect to the home page
                    switch_page("Home")  # Assuming "Home" is the name of the target page  
                 

                else:
                    # Display progress bar for 3 seconds
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.03)
                        progress_bar.progress(i + 1) 
                    st.error("Invalid User ID or Password.")
                connection.close()


    # Tab 2: Admin
    with tab2:
        with st.form("Admin Login Form"):
            # Input fields for User ID and Password
            admin_id_input = st.text_input("Admin ID", key="admin_id_input")
            admin_password_input = st.text_input("Password", type="password", key="admin_password_input")
            # Login button
            admin_login_button = st.form_submit_button("Login")

        if admin_login_button:
            admin_id       = st.secrets["admin"]["user_id"]
            admin_password = st.secrets["admin"]["password"]
            admin_email    = st.secrets["admin"]["email"]

            # Check if provided credentials match the stored credentials
            if admin_id_input == admin_id and admin_password_input == admin_password:
                st.session_state['user_id']   = admin_id
                # Store admin_email in session state
                st.session_state['admin_email'] = admin_email
                switch_page("Admin")  # No need to pass admin_email as an argument now
            else:
                # Display progress bar for 3 seconds
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)
                    progress_bar.progress(i + 1) 

                st.error("Invalid User ID or Password.")

def add_user(username, first_name, last_name, email, dob, password):
    connection = create_connection()
    if connection:
        table_name = "user_accounts"
        if not check_table_exists(connection, table_name):
            create_table(connection)

        # Display progress bar for 3 seconds
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03)
            progress_bar.progress(i + 1) 

        # Validation checks
        if not (email and first_name and last_name and dob and username):
            st.error("All fields are required!")
        elif check_unique_username_email(connection, username, email):
            st.error("Username and Email already exist!")
        elif check_unique_username(connection, username):
            st.error("Username already exists!")
        elif check_unique_email(connection, email):
            st.error("Email already exists!")
        else:
            # Insert the data into the database
            insert_user(connection, username, first_name, last_name, email, dob, password)
        
        # Close the connection only if it's not None
        connection.close()
    else:
        st.error("Failed to connect to the database!")
    

import uuid
from datetime import datetime, timedelta

def generate_reset_token():
    return str(uuid.uuid4())

def reset_password(email, user_data, connection):
    # Generate a secure token and expiry time
    reset_token = generate_reset_token()
    token_expiry = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

    # Update the user's record with the reset token and expiry
    try:
        cursor = connection.cursor()
        update_query = '''
        UPDATE user_accounts
        SET reset_token = %s, token_expiry = %s
        WHERE email = %s
        '''
        cursor.execute(update_query, (reset_token, token_expiry, email))
        connection.commit()
        cursor.close()
    except Error as e:
        st.error(f"Error updating reset token: {e}")
        return

    # Send email with reset token link
    first_name = user_data['first_name']
    last_name = user_data['last_name']
    username = user_data['username']
    date_of_creation = user_data['date_of_creation']

    subject = "Password Reset Request"
    reset_link = f"https://stockmarketinsight.streamlit.app/reset?token={reset_token}"
    body = f"""
    Dear {first_name} {last_name},

    We have received a request to reset the password for your account (Username: {username}) created on {date_of_creation}.

    Please click the link below to reset your password:

    {reset_link}

    This link will expire in 1 hour. If you did not request this password reset, please contact our support team immediately.

    Thank you for your prompt attention to this matter.
    
    Best regards,
    Manish Kashyap
    CEO
    Stock Analysis
    """
    send_email(email, subject, body)
    st.success("Password reset link has been sent to your email.")


def forgot_user_id(first_name, last_name):
    connection         = create_connection()
    if connection:
      user_info = get_user_emails(connection, first_name, last_name)
    else:
        connection.close()

    if user_info:
        formatted_info = []
        for row in user_info:
            formatted_info.append(f"{row['first_name']} {row['last_name']} - {row['email']}")

        # Display progress bar for 3 seconds
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03)
            progress_bar.progress(i + 1)  

        st.success(f"Found {len(formatted_info)} user(s) with the specified first and last name")
        st.write("\n".join(formatted_info))
        return f"Matching users:\n" + "\n".join(formatted_info)
    else:
        # Display progress bar for 3 seconds
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03)
            progress_bar.progress(i + 1)  

        st.warning("No user found with the specified first name and last name")
        return "No user found with the specified first name and last name"
