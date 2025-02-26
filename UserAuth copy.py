import streamlit as st
import hashlib
import hmac
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import mysql.connector
from db_connection import table, supabase, cursor

cursor = cursor
supabase = supabase

class UserAuth:
    def __init__(self):
        self.is_authenticated = st.session_state.get("is_authenticated", False)
        self.is_admin_authenticated = st.session_state.get("is_admin_authenticated", False)
        self.admin_email = st.secrets["admin"]["email"]
        self.admin_password_hash = self.hash_password(st.secrets["admin"]["password"])  # Store the hash of the admin password
        self.admin_user_id = st.secrets["admin"]["user_id"]

    def hash_password(self, password):
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def send_email(self, to_email, subject, body):
        """Send an email using smtplib."""
        msg = MIMEMultipart()
        msg['From'] = self.admin_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.admin_email, st.secrets["admin"]["password"])
            text = msg.as_string()
            server.sendmail(self.admin_email, to_email, text)
            server.quit()
        except Exception as e:
            st.error(f"Failed to send email: {e}")

    def validate_user_password(self):
        """Validate the user's password."""
        if self.is_authenticated:
            return True

        self.show_login_form()

        if "is_authenticated" in st.session_state and not st.session_state["is_authenticated"]:
            st.error("Invalid User ID or password.")

        return self.is_authenticated

    def validate_admin_password(self):
        """Validate the admin's password."""
        if self.is_admin_authenticated:
            return True

        self.show_admin_login_form()

        if "is_admin_authenticated" in st.session_state and not st.session_state["is_admin_authenticated"]:
            st.error("Invalid Admin ID or password.")

        return self.is_admin_authenticated

    def show_login_form(self):
        """Show the login form for regular users."""
        with st.form("Login Form"):
            st.text_input("User ID", key="username")
            st.text_input("Password", type="password", key="password")
            login_button = st.form_submit_button("Log in")

        if login_button:
            self.verify_user_password()

        st.button("New User? Sign Up", on_click=self.show_signup_form)
        st.button("Forgot Password?", on_click=self.show_reset_password_form)
        st.button("Forgot User ID?", on_click=self.show_retrieve_user_id_form)

    def show_admin_login_form(self):
        """Show the login form for the admin."""
        with st.form("Admin Login Form"):
            st.text_input("Admin ID", key="admin_username")
            st.text_input("Password", type="password", key="admin_password")
            admin_login_button = st.form_submit_button("Log in")

        if admin_login_button:
            self.verify_admin_password()

    def verify_user_password(self):
        """Verify the user's password."""
        username = st.session_state.get("username")
        password = st.session_state.get("password")

        if username == self.admin_user_id and hmac.compare_digest(self.hash_password(password), self.admin_password_hash):
            st.session_state["is_authenticated"] = True
            self.is_authenticated = True
            st.session_state["is_admin_authenticated"] = False
            self.is_admin_authenticated = False
        else:
            result = supabase.table("users").select("*").eq("username", username).single().execute()
            user = result.data
            if user:
                stored_password = user.get("password")
                if hmac.compare_digest(self.hash_password(password), stored_password):
                    st.session_state["is_authenticated"] = True
                    self.is_authenticated = True
                else:
                    st.error("Password mismatch.")
                    st.session_state["is_authenticated"] = False
                    self.is_authenticated = False
            else:
                st.error("Username not found in database.")
                st.session_state["is_authenticated"] = False
                self.is_authenticated = False

    def verify_admin_password(self):
        """Verify the admin's password."""
        admin_username = st.session_state.get("admin_username")
        admin_password = st.session_state.get("admin_password")

        if admin_username == self.admin_user_id and hmac.compare_digest(self.hash_password(admin_password), self.admin_password_hash):
            st.session_state["is_admin_authenticated"] = True
            self.is_admin_authenticated = True
            st.session_state["is_authenticated"] = False
            self.is_authenticated = False
        else:
            st.error("Invalid Admin ID or password.")
            st.session_state["is_admin_authenticated"] = False
            self.is_admin_authenticated = False

    def show_signup_form(self):
        st.write("Signup Form is Calling")
        """Show the sign-up form for new users."""
        with st.form("Sign Up Form"):
            email            = st.text_input("Email")
            dob              = st.text_input("Date of Birth (ddmmyy)")
            username         = st.text_input("Choose a Username (User ID)")
            password         = st.text_input("Choose a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button    = st.form_submit_button("Sign Up")

        if signup_button and password == confirm_password:
            self.add_user(username, email, dob, password)
        elif signup_button:
            st.error("Passwords do not match.")

    def add_user(self, username, email, dob, password):
        st.write("Add User is Calling")
        """ Add a new user to the Supabase database."""
        try:
            hashed_password = self.hash_password(password)
            
            # Insert the new user into Supabase
            data = {
                'username': username,
                'email': email,
                'dob': dob,
                'password': hashed_password
            }
            
            # Debugging: Print data being inserted
            st.write("Inserting data:", data)
            
            response = supabase.table("users").insert(data).execute()
            
            # Debugging: Check the response from Supabase
            st.write("Supabase response:", response)
            
            if response.status_code == 201:
                st.success("User registered successfully!")
                self.send_email(email, "Registration Successful", f"Dear {username},\n\nYour registration was successful.")
            else:
                st.error(f"User registration failed with error: {response.error_message}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    def show_reset_password_form(self):
        """Show the form to reset the password."""
        st.session_state["show_signup_form"] = False
        with st.form("Reset Password Form"):
            email = st.text_input("User Email")
            dob = st.text_input("Date of Birth (ddmmyy)")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            reset_button = st.form_submit_button("Reset Password")

        if reset_button and new_password == confirm_password:
            self.reset_password(email, dob, new_password)
        elif reset_button:
            st.error("Passwords do not match.")

    def reset_password(self, email, dob, new_password):
        """Reset a user's password."""
        user_query = supabase.table("users").select("*").eq("email", email).eq("dob", dob).single().execute()
        user = user_query.data
        if user:
            hashed_password = self.hash_password(new_password)
            supabase.table("users").update({"password": hashed_password}).eq("email", email).execute()
            st.success("Password reset successfully.")
        else:
            st.error("Invalid Email or Date of Birth.")

    def show_retrieve_user_id_form(self):
        """Show the form to retrieve a user ID based on the date of birth."""
        st.session_state["show_signup_form"] = False
        with st.form("Retrieve User ID Form"):
            st.write("RETRIVE USER ID FORM")
            dob = st.text_input("Date of Birth (ddmmyy)")
            retrieve_button = st.form_submit_button("Retrieve User ID")

        if retrieve_button:
            self.retrieve_user_id(dob)
        

    def retrieve_user_id(self, dob):
        """Retrieve and display the user ID(s) associated with the given date of birth."""
        user_query = supabase.table("users").select("username").eq("dob", dob).execute()
        found_users = user_query.data
        if found_users:
            user_ids = ", ".join([user["username"] for user in found_users])
            st.success(f"User ID(s) found: {user_ids}")
        else:
            st.error("No user found with the given Date of Birth.")

    def admin_view_all_users(self):
        """Allow the admin to view all users in the MySQL database."""

        try:
            cursor = supabase.cursor()  # Create a cursor
            cursor.execute(f"SELECT username, email, dob FROM {table}")  # Fetch data
            users = cursor.fetchall()  # Get all rows

            if users:
                st.write("Current Users in the Database:")
                for user in users:
                    st.write(f"Username: {user[0]}, Email: {user[1]}, DOB: {user[2]}")  # Use tuple indexing
            else:
                st.warning("No users found in the database.")

        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")

        finally:
            cursor.close()  # Close the cursor

    def admin_dashboard(self):
        """Show the admin dashboard in the sidebar."""
        st.sidebar.write("## Admin Dashboard")
        if st.sidebar.button("View All Users"):
            self.admin_view_all_users()


