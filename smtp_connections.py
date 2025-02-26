import streamlit as st

# Extract database credentials
smtp_config = st.secrets["connections"]["smpt_server"]

SMTP_SERVER    = smtp_config["SMTP_SERVER"]
SMTP_PORT      = smtp_config["SMTP_PORT"]
EMAIL_ADDRESS  = smtp_config["EMAIL_ADDRESS"]
EMAIL_PASSWORD = smtp_config["EMAIL_PASSWORD"]
