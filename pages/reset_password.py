import streamlit as st
import bcrypt
from logics.database import create_connection, get_user_info, update_user_password
import time

st.set_page_config(layout="centered")

# Check if user is logged in
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    user_id = st.session_state.get('user_id', 'Guest')  # Retrieve user ID from session
    # Check if user_info is available in session state
    if 'user_info' in st.session_state:
        user_info     = st.session_state['user_info']  # Access the stored user info
        st.sidebar.success(f"Welcome, {user_info['first_name']}!")
    else:
        # Establish a database connection
        connection = create_connection()
        # Assume this function gets user information from the database
        user_info = get_user_info(connection, user_id)
        if user_info:
            st.sidebar.success(f"Welcome, {user_info['first_name']}!")

            user_password = user_info['password']  # Access the stored hashed password
            print("\n\n\n\t\t\t* HASHED PASSWORD from DATABASE ", user_password)

            # Input for current password
            current_password = st.text_input("Current Password", type="password")

            col1, col2 = st.columns([1, 1])
            with col1:
                password         = st.text_input("New Password", type="password")
            with col2:
                confirm_password = st.text_input("Confirm New Password", type="password")

            update_password_button = st.button("Update")
            # If the current password is provided, validate it
            if current_password and update_password_button:
                # Verify that the entered current password matches the stored hashed password
                if bcrypt.checkpw(current_password.encode('utf-8'), user_password.encode('utf-8')):
                    # Now you can proceed to check if the new passwords match and process the password change
                    if password and confirm_password:
                        if password == confirm_password:
                            # Hash the new password before storing it in the database
                            hashed_new_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                            # Update the password in the database (you need to implement this function)
                            update_user_password(connection, user_id, hashed_new_password)
                             # Display progress bar for 3 seconds
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.03)
                                progress_bar.progress(i + 1) 
                            st.success("Password has been successfully updated!")
                        else:
                            # Display progress bar for 3 seconds
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.03)
                                progress_bar.progress(i + 1) 
                            st.error("New passwords do not match.")
                else:
                    # Display progress bar for 3 seconds
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.03)
                        progress_bar.progress(i + 1) 
                    st.error("Current password is incorrect.")


        else:
            # Display progress bar for 3 seconds
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                progress_bar.progress(i + 1) 

            st.error("User information could not be retrieved.")

            # Close the database connection
            connection.close()

        st.sidebar.page_link("pages/home.py",           label="Home",           icon="🏠")
        st.sidebar.page_link("pages/updateinfo.py",     label="Update Info",    icon="⚙️")
        st.sidebar.page_link("pages/reset_password.py", label="Reset Password", icon="🗝️")

        st.markdown("""
        <style>
            [data-testid=stSidebar] {
                background-color: #3e3e40;
            }
        </style>
        """, unsafe_allow_html=True)
        with st.sidebar:
                st.image("./Animations/stock2.jpg", 
                        #caption="Your PNG caption",
                        width=350) 



else:
    st.error("You must be logged in to access this page.")
    st.stop()
