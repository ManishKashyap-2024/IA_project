import streamlit as st
from logics.database import create_connection  # Import your connection function
from mysql.connector import Error
import bcrypt
from streamlit_extras.switch_page_button import switch_page
import time

st.set_page_config(layout='centered')


def verify_token(connection, token):
    try:
        cursor = connection.cursor(dictionary=True)
        query = '''
        SELECT * FROM user_accounts WHERE reset_token = %s AND token_expiry > CURRENT_TIMESTAMP
        '''
        cursor.execute(query, (token,))
        result = cursor.fetchone()
        cursor.close()
        return result  # Return user data if token is valid
    except Error as e:
        st.error(f"Error verifying token: {e}")
        return None


def reset_password_page():
    # Get the token from the URL
    token = st.experimental_get_query_params().get("token")
    
    if not token:
        st.error("No token provided.")
        return

    connection = create_connection()
    user_data = verify_token(connection, token[0])

    if user_data:
        st.success("Token verified. Please reset your password.")
        new_password     = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        if st.button("Reset Password"):
            if new_password == confirm_password:
                try:
                    # Hash the password before storing it
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                    cursor = connection.cursor()
                    update_query = '''
                    UPDATE user_accounts
                    SET password = %s, reset_token = NULL, token_expiry = NULL
                    WHERE id = %s
                    '''
                    cursor.execute(update_query, (hashed_password, user_data['id']))
                    connection.commit()
                    st.success("Password has been reset successfully.")
                    time.sleep(5)  # Sleep for 2 seconds
                    switch_page("Main")
                except Error as e:
                    st.error(f"Error resetting password: {e}")
            else:
                st.error("Passwords do not match.")
    else:
        st.error("Invalid or expired token.")

    connection.close()

if __name__ == "__main__":
    reset_password_page()