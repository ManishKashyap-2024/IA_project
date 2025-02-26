import streamlit as st
import mysql.connector

# Extract database credentials
db_config = st.secrets["connections"]["freesqldatabase"]

key = {
    "host": db_config["host"],
    "database": db_config["database"],
    "user": db_config["user"],
    "password": db_config["password"],
    "port": db_config["port"]
}

table = 'user_accounts' 

try:
    db_credentials = mysql.connector.connect(
        host=key["host"],
        user=key["user"],
        password=key["password"],
        database=key["database"],
        port=key["port"]
    )
    cursor = db_credentials.cursor()
except mysql.connector.Error as err:
    st.error(f"Error: {err}")
