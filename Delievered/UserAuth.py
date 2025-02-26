import streamlit as st
import hashlib
import hmac
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector
from db_connection import table, db_credentials
from smtp_connections import *

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
        try:
            # Create a multipart email
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = to_email

            # Attach the email body
            msg.attach(MIMEText(body, "plain"))

            # Connect to SMTP Server
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Start TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            # Send the email
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
            server.quit()

            st.success("✅ Email sent successfully!")
        
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

        new_user        = st.toggle("New User? Sign Up")
        if new_user:
            self.show_signup_form()
        forgot_password = st.toggle("Forgot Password?")
        if forgot_password:
            self.show_reset_password_form()
        forgot_user_id  = st.toggle("Forgot User ID?")
        if forgot_user_id:
            self.show_retrieve_user_id_form()

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

        if not username or not password:
            st.error("Please enter username and password.")
            return

        # Admin Authentication
        if username == self.admin_user_id and hmac.compare_digest(self.hash_password(password), self.admin_password_hash):
            st.session_state["is_authenticated"] = True
            self.is_authenticated = True
            st.session_state["is_admin_authenticated"] = False
            self.is_admin_authenticated = False
            return

        connection = None
        cursor = None
        try:
            # Establish database connection
            connection = db_credentials()  # Your MySQL connection function
            cursor = connection.cursor(dictionary=True)

            # Fetch user credentials
            cursor.execute(f"SELECT * FROM {table} WHERE username = %s", (username,))
            user = cursor.fetchone()  # Fetch only one result to avoid unread errors

            # Ensure all results are consumed before closing cursor
            cursor.fetchall()  # This prevents "Unread result found" if multiple rows exist

            if user:
                stored_password = user.get("password")
                if stored_password and hmac.compare_digest(self.hash_password(password), stored_password):
                    st.session_state["is_authenticated"] = True
                    self.is_authenticated = True
                    st.success("Login successful! Redirecting to dashboard...")
                else:
                    st.error("Incorrect password.")
                    st.session_state["is_authenticated"] = False
                    self.is_authenticated = False
            else:
                st.error("User not found.")
                st.session_state["is_authenticated"] = False
                self.is_authenticated = False

        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

        finally:
            # Ensure cursor and connection are properly closed
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()






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
        """ Add a new user to the MySQL database."""
        try:
            hashed_password = self.hash_password(password)
            
            # Create a database connection
            connection = db_credentials()
            cursor = connection.cursor()  # Create a cursor

            if username and email and dob and password:
                # SQL Query to insert user data
                query = f"INSERT INTO {table} (username, email, dob, password) VALUES (%s, %s, %s, %s)"
                values = (username, email, dob, hashed_password)

                cursor.execute(query, values)
                connection.commit()

                # Close connection
                cursor.close()
                connection.close()
                
                st.success("User registered successfully!")
                self.send_email(email, "Registration Successful", f"Dear {username},\n\nYour registration was successful.")
            else:
                st.warning("Please fill up the form")

        except mysql.connector.Error as e:
            st.error(f"MySQL Error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")


    def show_reset_password_form(self):
        """Show the form to reset the password."""
        st.session_state["show_signup_form"] = False
        with st.form("Reset Password Form"):
            email            = st.text_input("User Email")
            dob              = st.text_input("Date of Birth (ddmmyy)")
            new_password     = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            reset_button     = st.form_submit_button("Reset Password")

        if reset_button and new_password == confirm_password:
            self.reset_password(email, dob, new_password)
        elif reset_button:
            st.error("Passwords do not match.")


    def reset_password(self, email, dob, new_password):
        """Reset a user's password in MySQL."""
        try:
            # Create database connection
            connection = db_credentials()  # Assuming this function gives a valid MySQL connection
            cursor = connection.cursor(dictionary=True)  # Use dictionary cursor for easier access

            # Check if user exists
            cursor.execute(f"SELECT * FROM {table} WHERE email = %s AND dob = %s", (email, dob))
            user = cursor.fetchone()  # Fetch the first matching row

            if user:
                # Hash the new password
                hashed_password = self.hash_password(new_password)
                
                # Update password in the database
                cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
                connection.commit()  # Save changes
                
                st.success("Password reset successfully.")
            else:
                st.error("Invalid Email or Date of Birth.")

        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

        finally:
            # Close cursor and connection safely
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()




    def show_retrieve_user_id_form(self):
        """Show the form to retrieve a user ID based on the date of birth."""
        st.session_state["show_signup_form"] = False
        with st.form("Retrieve User ID Form"):
            st.write("RETRIVE USER ID FORM")
            dob = st.text_input("Date of Birth (yyyy/mm/dd)")
            retrieve_button = st.form_submit_button("Retrieve User ID")

        if retrieve_button:
            self.retrieve_user_id(dob)


    def retrieve_user_id(self, dob):
        """Retrieve and display the user ID(s) associated with the given date of birth."""
        try:
            # Create a database connection
            connection = db_credentials()
            cursor = connection.cursor()  # Create a cursor

            # Execute SQL query
            cursor.execute(f"SELECT username FROM {table} WHERE dob = %s", (dob,))
            found_users = cursor.fetchall()  # Fetch data

            if found_users:
                # Extract usernames from tuples
                user_ids = ", ".join(user[0] for user in found_users)
                st.success(f"User ID(s) found: {user_ids}")
            else:
                st.error("No user found with the given Date of Birth.")

        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Close cursor and connection safely
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()




    def admin_view_all_users(self):
        """Allow the admin to view all users in the MySQL database."""

        try:
            # Create a database connection
            connection = db_credentials()
            cursor = connection.cursor()  # Create a cursor
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
            # Ensure cursor and connection are closed only if they exist
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()


    def admin_dashboard(self):
        """Show the admin dashboard in the sidebar."""
        st.sidebar.write("## Admin Dashboard")
        if st.sidebar.button("View All Users"):
            self.admin_view_all_users()


