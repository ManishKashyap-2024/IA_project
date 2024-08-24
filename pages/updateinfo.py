import streamlit as st
from logics.database import create_connection, get_user_info, update_user_info
# Check if user is logged in

if 'logged_in' in st.session_state and st.session_state['logged_in']:
    user_id = st.session_state.get('user_id', 'Guest')  # Retrieve user ID from session
    # Check if user_info is available in session state
    if 'user_info' in st.session_state:
        user_info = st.session_state['user_info']  # Access the stored user info
        st.sidebar.success(f"Welcome, {user_info['last_name']}!")
    else:
        # Establish a database connection
        connection = create_connection()
        # Retrieve user info from the database
        user_info = get_user_info(connection, user_id)
        if user_info:
            st.sidebar.success(f"Welcome, {user_info['last_name']}!")

            col1, col2 = st.columns([1,3])
            with col1:
                username = st.text_input("Username (User ID)", value=user_info['username'], disabled=True)
            with col2:
                email    = st.text_input("Email", value=user_info['email'], disabled=True)

            col1, col2 = st.columns([1,1])
            with col1:
                first_name = st.text_input("First Name", value=user_info['first_name'])
            with col2:
                last_name  = st.text_input("Last Name", value=user_info['last_name'])

            dob  = st.date_input("Date of Birth", value=user_info['dob'])    

            update_info_button = st.button("Update", key="update_info_button")

            if update_info_button:
                update_user_info(connection, user_id, first_name, last_name, dob)


        else:
            st.error("User information could not be retrieved.")

            # Close the database connection
            connection.close()

        st.sidebar.page_link("pages/home.py",           label="Home",           icon="🏠")
        st.sidebar.page_link("pages/updateinfo.py",     label="Update Info",    icon="⚙️")
        st.sidebar.page_link("pages/reset_password.py", label="Reset Password", icon="🗝️")


else:
    st.error("You must be logged in to access this page.")
    st.stop()
