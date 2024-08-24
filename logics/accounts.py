import streamlit as st
from logics.database import *

from streamlit_extras.switch_page_button import switch_page

def login():
    # Create tabs
    tab1, tab2 = st.tabs(["User", "Admin"])

    # Tab 1: Login
    with tab1:
        # Input fields for User ID and Password
        with st.form("Login Form"):
            user_id_input       = st.text_input("User ID", key="user_id_input")
            user_password_input = st.text_input("Password", type="password", key="user_password_input")
            # Login button
            user_login_button = st.form_submit_button("Login")

        if user_login_button:
            connection = create_connection()
            if connection:
                print("\n\n\n\t\t Connection created with database for LOGIN")

                if check_login_credentials(connection, user_id_input, user_password_input):
                    st.success("Login successful!")

                    print("\n\t\t* Login Successfull\n")
                    # Set session state to indicate the user is logged in
                    st.session_state['logged_in'] = True
                    st.session_state['user_id']   = user_id_input

                    # Redirect to the home page
                    switch_page("Home")  # Assuming "Home" is the name of the target page  
                 

                else:
                    print("\n\t\t* Login Fail\n")
                    st.error("Invalid User ID or Password.")
                connection.close()




        

    # Tab 2: About
    with tab2:
        with st.form("Admin Login Form"):
            # Input fields for User ID and Password
            admin_id_input = st.text_input("Admin ID", key="admin_id_input")
            admin_password_input = st.text_input("Password", type="password", key="admin_password_input")
            # Login button
            admin_login_button = st.form_submit_button("Login")

        if admin_login_button:
            admin_id = st.secrets["admin"]["user_id"]
            admin_password = st.secrets["admin"]["password"]

            # Check if provided credentials match the stored credentials
            if admin_id_input == admin_id and admin_password_input == admin_password:
                st.success(f"Welcome, {admin_id_input}!")
            else:
                st.error("Invalid User ID or Password.")

def add_user(username, first_name, last_name, email, dob, password):
    connection = create_connection()
    if connection:
        table_name = "user_accounts"
        if not check_table_exists(connection, table_name):
            create_table(connection)

        # Validation checks
        if not (email and first_name and last_name and dob and username):
            st.error("All fields are required!")
        elif check_unique_username_email(connection, username, email):
            st.error("Username and Email already exists!")
        elif check_unique_username(connection, username):
            st.error("Username already exists!")
        elif check_unique_email(connection, email):
            st.error("Email already exists!")
        else:
            # Insert the data into the database
            insert_user(connection, username, first_name, last_name, email, dob, password)
    connection.close()
    


def forgot_user_password():
    st.warning("This will be added later")

def forgot_user_id():
    st.warning("This will be added later")