import streamlit as st
import mysql.connector
from mysql.connector import Error
import bcrypt

def create_connection():
    try:
        connection = mysql.connector.connect(
            host     = st.secrets["mysql"]["host"],
            database = st.secrets["mysql"]["database"],
            user     = st.secrets["mysql"]["user"],
            password = st.secrets["mysql"]["password"],
            port     = st.secrets["mysql"]["port"]
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Function to check if a table exists
def check_table_exists(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        st.error(f"Error checking table: {e}")
        return False


def create_table(connection):
    try:
        cursor = connection.cursor()
        
        # Create the table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS user_accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            dob DATE NOT NULL,
            password VARCHAR(255) NOT NULL,
            date_of_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reset_token VARCHAR(255),
            token_expiry TIMESTAMP
        )
        '''
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        st.success("Table 'user_accounts' created successfully, with support for password reset tokens.")
    except Error as e:
        st.error(f"Error creating table: {e}")
        


# Function to insert data into the table
def insert_user(connection, username, first_name, last_name, email, dob, password):
    try:
        password = password.encode('utf-8')

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)

        cursor = connection.cursor()
        insert_query = '''
        INSERT INTO user_accounts (username, first_name, last_name, email, dob, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_query, (username, first_name, last_name, email, dob, hashed_password))
        connection.commit()
        cursor.close()
        st.success("User account created successfully.")
    except Error as e:
        st.error(f"Error inserting data: {e}")


# Function to check if Username already exists
def check_unique_username(connection, username):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_accounts WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        st.error(f"Error checking for existing user: {e}")
        return True


# Function to check if email already exists
def check_unique_email(connection, email):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_accounts WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        st.error(f"Error checking for existing user: {e}")
        return True

def check_unique_username_email(connection, username, email):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_accounts WHERE username = %s AND email = %s", (username, email))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        st.error(f"Error checking for existing user: {e}")
        return True 

def db_connection():
    st.title("MySQL Table Check and Creation")

    connection = create_connection()
    if connection:
        table_name = "user_accounts"
        if not check_table_exists(connection, table_name):
            create_table(connection)
        else:
            st.info(f"Table '{table_name}' already exists.")
        connection.close()


def check_login_credentials(connection, user_id, password):
    try:
        cursor = connection.cursor()
        query = "SELECT password FROM user_accounts WHERE email = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result is None:
            return False

        # Get the hashed password from the result
        stored_hashed_password = result[0]

        # Check if the provided password matches the hashed password
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            return True
        else:
            return False

    except Error as e:
        st.error(f"Error checking login credentials: {e}")
        return False

def get_user_info(connection, email):
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM user_accounts WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        return result
    except Error as e:
        st.error(f"Error retrieving user information: {e}")
        return None
    
def update_user_info(connection, email, first_name, last_name, dob):
    try:
        cursor = connection.cursor(dictionary=True)
        
        # First, check if the email exists
        query = "SELECT * FROM user_accounts WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        if result:
            # If the email exists, update the first_name, last_name, and dob
            update_query = """
                UPDATE user_accounts
                SET first_name = %s, last_name = %s, dob = %s
                WHERE email = %s
            """
            cursor.execute(update_query, (first_name, last_name, dob, email))
            connection.commit()  # Commit the transaction

            # Update Streamlit session state
            st.session_state['first_name'] = first_name
            st.session_state['last_name'] = last_name
            st.session_state['dob'] = dob      

            cursor.close()
            st.success("User information updated successfully")
            return f"User information updated successfully for email: {email}"
        else:
            cursor.close()
            return f"No user found with email: {email}"
    except Error as e:
        st.error(f"Error retrieving or updating user information: {e}")
        return None
    

def update_user_password(connection, email, password):
    try:

        cursor = connection.cursor(dictionary=True)
        
        # First, check if the email exists
        query = "SELECT * FROM user_accounts WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        if result:
            # If the email exists, update the password
            update_query = """
                UPDATE user_accounts
                SET password = %s
                WHERE email = %s
            """
            cursor.execute(update_query, (password, email))
            connection.commit()  # Commit the transaction

            # Update Streamlit session state
            st.session_state['password'] = password
   
            cursor.close()
            return f"User Password Updated Successfully For Email: {email}"
        else:
            cursor.close()
            return f"No user found with email: {email}"
    except Error as e:
        st.error(f"Error Retrieving Or Updating User Password: {e}")
        return None



    
def forgot_password(connection, email):
    try:
        cursor = connection.cursor(dictionary=True)
        query  = "SELECT * FROM user_accounts WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return True, result  # Email exists, return True and user data
        else:
            return False, None  # Email does not exist, return False and None
    except Error as e:
        st.error(f"Error retrieving user information: {e}")
        return False, None  # Return False and None in case of error



def get_user_emails(connection, first_name, last_name):
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Query to check if the first_name and last_name exist
        query = """
            SELECT first_name, last_name, email FROM user_accounts 
            WHERE first_name = %s OR last_name = %s
        """
        cursor.execute(query, (first_name, last_name))
        results = cursor.fetchall()
        
        cursor.close()
        
        if results:
            return results
        else:
            return None
    except Error as e:
        st.error(f"Error retrieving user information: {e}")
        return None