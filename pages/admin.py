import streamlit as st
from mysql.connector import Error
from logics.database import create_connection
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")


def display_users(connection):
    try:
        cursor = connection.cursor()
        
        # Fetch user details
        fetch_users_query = '''
        SELECT first_name, last_name, username, email, date_of_creation, dob 
        FROM user_accounts
        '''
        cursor.execute(fetch_users_query)
        users = cursor.fetchall()

        if users:
            # Displaying the results in a table format
            st.write("### User Accounts")
            st.table(pd.DataFrame(users, columns=["First Name", "Last Name", "Username", "Email", "Account Creation Date", "DOB"]))
        else:
            st.warning("No users found in the database.")
        
        cursor.close()
    except Error as e:
        st.error(f"Error retrieving user data: {e}")


def admin_login():

    if 'admin_email' in st.session_state:
        admin_email = st.session_state['admin_email']
        st.sidebar.success(f"Welcome, {admin_email}")  

        st.sidebar.page_link("pages/admin.py",      label="Admin", icon="👤")
        st.sidebar.page_link("pages/admin_home.py", label="Home",  icon="🏠")

    connection = create_connection()
    if connection:
        try:
            display_users(connection)
        finally:
            connection.close()
    else:
        print("Failed to establish a connection to the database.")





if "__main__":
    admin_login()


