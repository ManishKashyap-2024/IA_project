import streamlit as st
from logics.database import create_connection, get_user_info, update_user_info
from streamlit_lottie import st_lottie, st_lottie_spinner
import requests
import json
import time

st.set_page_config(layout="centered")

@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Check if user is logged in
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    user_id = st.session_state.get('user_id', 'Guest')  # Retrieve user ID from session
    # Check if user_info is available in session state
    if 'user_info' in st.session_state:
        user_info = st.session_state['user_info']  # Access the stored user info
        st.sidebar.success(f"Welcome, {user_info['first_name']}!")
    else:
        # Establish a database connection
        connection = create_connection()
        # Retrieve user info from the database
        user_info = get_user_info(connection, user_id)
        if user_info:
            st.sidebar.success(f"Welcome, {user_info['first_name']}!")



            col1, col2 = st.columns([1, 2.1])
            with col1:
                lottie_file4 = './Animations/update.json'
                lottie_json4 = load_lottiefile(lottie_file4)
                st_lottie(
                    lottie_json4,
                    speed=1,
                    reverse=False,
                    loop=True,
                    quality="low",
                    height=300,
                    width=240,
                    key='update'
                )
            with col2:
                col1, col2 = st.columns([1,1])
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

            st.write("--------------------------------------------------------")
            update_info_button = st.button("Update", key="update_info_button")

            if update_info_button:
                update_user_info(connection, user_id, first_name, last_name, dob)


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
