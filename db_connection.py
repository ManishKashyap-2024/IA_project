import streamlit as st
import mysql.connector
import toml


# Extract database credentials
db_config = st.secrets["connections"]["freesqldatabase"]

# Use credentials in your script
# url = db_config["host"]
key = {
    "host": db_config["host"],
    "database": db_config["database"],
    "user": db_config["user"],
    "password": db_config["password"],
    "port": db_config["port"]
}

table = 'user_accounts' 

def db_connection():
    # Establishing MySQL Connection
    try:
        supabase = mysql.connector.connect(
            host=key["host"],
            user=key["user"],
            password=key["password"],
            database=key["database"],
            port=key["port"]
        )
        cursor = supabase.cursor()

        return cursor
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")