import streamlit as st
from logics.database import create_connection, get_user_info
from streamlit_extras.switch_page_button import switch_page


st.set_page_config(layout="wide")


# Check if user is logged in
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    user_id = st.session_state.get('user_id', 'Guest')  # Retrieve user ID from session


    # Check if user_info is already stored in session state
    if 'user_info' not in st.session_state:    
        # Establish a database connection
        connection = create_connection()
        if connection:
            # Retrieve user info from the database
            user_info = get_user_info(connection, user_id)

            if user_info:
                st.sidebar.success(f"Welcome, {user_info['last_name']}!")

            else:
                st.error("User information could not be retrieved.")

            # Close the database connection
            connection.close()

            st.sidebar.page_link("pages/home.py",           label="Home",           icon="🏠")
            st.sidebar.page_link("pages/updateinfo.py",     label="Update Info",    icon="⚙️")
            st.sidebar.page_link("pages/reset_password.py", label="Reset Password", icon="🗝️")
            

            from logics.stock_prices import StockAnalysisApp
            import os
        
            app = StockAnalysisApp()

            app.init_state_variables()
            app.stock_analysis()


            logout = st.sidebar.button("LogOut")
            if logout:
                switch_page("Main")


        else:
            st.error("Failed to connect to the database.")
    else:
        # Use the stored user_info from session state
        user_info = st.session_state['user_info']

else:
    st.error("You must be logged in to access this page.")
    st.stop()  # Stop further execution of the page content

