import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime
import hashlib
import hmac
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

# Create the SQL connection to user_db as specified in your secrets file.
conn = st.connection('user_db', type='sql')

# Create users table if it doesn't exist
with conn.session as s:
    s.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            dob TEXT,
            password TEXT
        );
    ''')
    s.commit()

st.write("Users table has been created.")

class UserAuth:
    def __init__(self):
        self.is_authenticated = st.session_state.get("is_authenticated", False)
        self.is_admin_authenticated = st.session_state.get("is_admin_authenticated", False)
        self.admin_email = st.secrets["admin"]["email"]
        self.admin_password = st.secrets["admin"]["password"]
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
            server.login(self.admin_email, self.admin_password)
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
            st.form_submit_button("Log in", on_click=self.verify_user_password)

        st.button("New User? Sign Up", on_click=self.show_signup_form)
        st.button("Forgot Password?", on_click=self.show_reset_password_form)
        st.button("Forgot User ID?", on_click=self.show_retrieve_user_id_form)

    def show_admin_login_form(self):
        """Show the login form for the admin."""
        with st.form("Admin Login Form"):
            st.text_input("Admin ID", key="admin_username")
            st.text_input("Password", type="password", key="admin_password")
            st.form_submit_button("Log in", on_click=self.verify_admin_password)

    def verify_user_password(self):
        """Verify the user's password."""
        username = st.session_state.get("username")
        password = st.session_state.get("password")

        if username == self.admin_user_id and hmac.compare_digest(password, self.admin_password):
            # Admin logs in through the user tab, but we treat this as a user login
            st.session_state["is_authenticated"] = True
            self.is_authenticated = True
            # Ensure admin dashboard and admin login tab do not appear in the user login
            st.session_state["is_admin_authenticated"] = False
            self.is_admin_authenticated = False
        else:
            query = "SELECT password FROM users WHERE username = :username"
            result = conn.session.execute(query, {'username': username}).fetchone()

            if result:
                st.write(f"Password hash stored in DB: {result.password}")
                if hmac.compare_digest(self.hash_password(password), result.password):
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

        if admin_username == self.admin_user_id and hmac.compare_digest(admin_password, self.admin_password):
            st.session_state["is_admin_authenticated"] = True
            self.is_admin_authenticated = True
            # Reset user authentication if admin logs in directly
            st.session_state["is_authenticated"] = False
            self.is_authenticated = False
        else:
            st.session_state["is_admin_authenticated"] = False
            self.is_admin_authenticated = False

    def show_signup_form(self):
        """Show the sign-up form for new users."""
        with st.form("Sign Up Form"):
            email = st.text_input("Email")
            dob = st.text_input("Date of Birth (ddmmyy)")
            username = st.text_input("Choose a Username (User ID)")
            password = st.text_input("Choose a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Sign Up"):
                if password == confirm_password:
                    self.add_user(username, email, dob, password)
                else:
                    st.error("Passwords do not match.")

    def add_user(self, username, email, dob, password):
        """ Add a new user to the database."""
        try:
            hashed_password = self.hash_password(password)
            
            # Insert the new user
            query = '''
                INSERT INTO users (username, email, dob, password)
                VALUES (:username, :email, :dob, :password);
            '''
            conn.session.execute(query, {
                'username': username,
                'email': email,
                'dob': dob,
                'password': hashed_password
            })
            conn.session.commit()
    
            # Display the added user
            user_check = conn.session.execute("SELECT * FROM users WHERE username = :username", {'username': username}).fetchone()
            
            st.write(f"Inserted user: {user_check}")
            
            if user_check:
                st.success("User registered successfully!")
                self.send_email(email, "Registration Successful", f"Dear {username},\n\nYour registration was successful.")
            else:
                st.error("User registration failed.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


    def show_reset_password_form(self):
        """ Show the form to reset the password."""
        st.session_state["show_signup_form"] = False
        with st.form("Reset Password Form"):
            email = st.text_input("User Email")
            dob = st.text_input("Date of Birth (ddmmyy)")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Reset Password"):
                if new_password == confirm_password:
                    self.reset_password(email, dob, new_password)
                else:
                    st.error("Passwords do not match.")

    def reset_password(self, email, dob, new_password):
        """ Reset a user's password."""
        query = "SELECT * FROM users WHERE email = :email AND dob = :dob"
        user = conn.session.execute(query, {'email': email, 'dob': dob}).fetchone()

        if user:
            update_query = 'UPDATE users SET password = :password WHERE email = :email'
            conn.session.execute(update_query, {
                'password': self.hash_password(new_password),
                'email': email
            })
            conn.session.commit()
            st.success("Password reset successfully.")
        else:
            st.error("Invalid Email or Date of Birth.")

    def show_retrieve_user_id_form(self):
        """ Show the form to retrieve a user ID based on the date of birth."""
        st.session_state["show_signup_form"] = False
        with st.form("Retrieve User ID Form"):
            dob = st.text_input("Date of Birth (ddmmyy)")
            if st.form_submit_button("Retrieve User ID"):
                self.retrieve_user_id(dob)

    def retrieve_user_id(self, dob):
        """Retrieve and display the user ID(s) associated with the given date of birth."""
        query = 'SELECT username FROM users WHERE dob = :dob'
        found_users = conn.session.execute(query, {'dob': dob}).fetchall()

        if found_users:
            user_ids = ", ".join([user.username for user in found_users])
            st.success(f"User ID(s) found: {user_ids}")
        else:
            st.error("No user found with the given Date of Birth.")

    def admin_view_all_users(self):
        """Allow the admin to view all users in the database."""
        query = 'SELECT username, email, dob FROM users'
        users = conn.session.execute(query).fetchall()
    
        # Check the actual contents returned
        st.write(f"Fetched users: {users}")
    
        if users:
            st.write("Current Users in the Database:")
            for user in users:
                st.write(f"Username: {user.username}, Email: {user.email}, DOB: {user.dob}")
        else:
            st.warning("No users found in the database.")

    def admin_dashboard(self):
        """Show the admin dashboard in the sidebar."""
        st.sidebar.write("## Admin Dashboard")
        if st.sidebar.button("View All Users"):
            self.admin_view_all_users()


class StockAnalysisApp:
    def __init__(self):
        self.auth = UserAuth()
        self.today = datetime.date.today()
        self.start_date = self.today - datetime.timedelta(days=365)
        self.end_date = self.today
        self.ticker_list = pd.read_csv('stock_list.txt')
        self.selected_ticker = None

    def init_state_variables(self):
        # Initialize session state variables for each feature
        features = ['bollinger_bands', 'macd', 'rsi', 'analyst_ratings', 'trading_volume', 'income_statement', 'ticker_data']
        for feature in features:
            if feature not in st.session_state:
                st.session_state[feature] = False

    def run(self):
        # Only show tabs if no one is authenticated
        if not st.session_state.get("is_authenticated") and not st.session_state.get("is_admin_authenticated"):
            tab1, tab2 = st.tabs(["User Login", "Admin Login"])

            with tab1:
                self.auth.validate_user_password()

                if st.session_state.get("is_authenticated"):
                    # If the admin logs in as a user, they should not see the admin dashboard
                    st.session_state["is_admin_authenticated"] = False
                    self.stock_analysis()

            with tab2:
                if self.auth.validate_admin_password():
                    # Admin-specific functionality here, only visible after admin login
                    self.auth.admin_dashboard()

        elif st.session_state.get("is_authenticated"):
            # Show the stock analysis only if user is authenticated
            self.stock_analysis()

        elif st.session_state.get("is_admin_authenticated"):
            # Show the admin dashboard if admin is authenticated
            self.auth.admin_dashboard()

    def stock_analysis(self):
        st.markdown('''
        # Stock Analysis Application
        One-stop shop for getting the key insights on your selected stocks at your fingertips!
        ''')
        st.write('---')
        self.set_date_inputs()
        self.choose_ticker()
        self.fetch_ticker_data()
        self.show_stock_info()
        self.show_financial_metrics()

        self.init_state_variables()

        if st.button('Show Bollinger Bands'):
            st.session_state.bollinger_bands = True
        
        if st.session_state.bollinger_bands:
            self.show_bollinger_bands()

        if st.button('Show MACD Chart'):
            st.session_state.macd = True

        if st.session_state.macd:
            self.show_macd()

        if st.button('Show RSI'):
            st.session_state.rsi = True

        if st.session_state.rsi:
            self.show_rsi()

        if st.button('Show Analyst Ratings'):
            st.session_state.analyst_ratings = True

        if st.session_state.analyst_ratings:
            self.show_analyst_ratings()

        if st.button('Show Trading Volume Chart'):
            st.session_state.trading_volume = True

        if st.session_state.trading_volume:
            self.show_trading_volume_chart()

        if st.button('Show Income Statement'):
            st.session_state.income_statement = True

        if st.session_state.income_statement:
            self.show_income_statement()

        if st.button('Show Ticker Data'):
            st.session_state.ticker_data = True
            
        if st.session_state.ticker_data:
            self.show_ticker_data()

    def set_date_inputs(self):
        self.start_date = st.sidebar.date_input("Start Date", self.start_date)
        self.end_date = st.sidebar.date_input("End Date", self.end_date)

    def choose_ticker(self):
        self.selected_ticker = st.sidebar.selectbox('Stock Ticker', self.ticker_list)

    def fetch_ticker_data(self):
        self.ticker_info = yf.Ticker(self.selected_ticker)
        self.ticker_history = self.ticker_info.history(period='1d', start=self.start_date, end=self.end_date)
        self.sorted_ticker_history = self.ticker_history.sort_index(ascending=False)

    def show_stock_info(self):
        stock_name = self.ticker_info.info['longName']
        st.header(f'**{stock_name}**')

        stock_summary = self.ticker_info.info['longBusinessSummary']
        st.info(stock_summary)

        asset_profile = self.ticker_info.info.get('assetProfile', {})
        if asset_profile:
            st.subheader(f'Asset Profile for {self.selected_ticker}')
            for key, value in asset_profile.items():
                st.text(f'{key}: {value}')
        else:
            st.write("Asset profile information is not available.")

    def show_financial_metrics(self):
        st.header('**Financial Metrics**')
        metrics = {
            "Metric": ["Previous Close", "Highest in 52 wks", "Lowest in 52 wks",
                       "PE Ratio", "Beta", "PEG Ratio", "Forward PE Ratio"],
            "Value": [
                self.ticker_info.info.get('previousClose', 'N/A'),
                self.ticker_info.info.get('fiftyTwoWeekHigh', 'N/A'),
                self.ticker_info.info.get('fiftyTwoWeekLow', 'N/A'),
                self.ticker_info.info.get('trailingPE', 'N/A'),
                self.ticker_info.info.get('beta', 'N/A'),
                self.ticker_info.info.get('pegRatio', 'N/A'),
                self.ticker_info.info.get('forwardPE', 'N/A')
            ]
        }
        metrics_df = pd.DataFrame(metrics)
        st.table(metrics_df)

    def show_bollinger_bands(self):
        st.header('**Bollinger Bands**')
        st.markdown('''
        Bollinger Bands are one of the useful tools in stock analysis to decide when to buy or sell a stock. They show if the stock is priced too high or too low. If the stock price falls below the lower band, it might mean the stock is too cheap and could go up soon. 
        If the price rises above the upper band, it might mean the stock is too expensive and could drop in price.
        ''')
        quant_fig = cf.QuantFig(self.ticker_history, title='Bollinger Bands Chart', legend='top', name=self.selected_ticker)
        quant_fig.add_bollinger_bands()
        fig = quant_fig.iplot(asFigure=True)
        st.plotly_chart(fig)

    def show_macd(self):
        st.header('**MACD (Moving Average Convergence Divergence)**')
        st.markdown('''
        The Moving Average Convergence Divergence (MACD) is a tool that helps investors know when to buy or sell stocks. 
        To get the MACD line, subtract the 26-day Exponential Moving Average (EMA) from the 12-day EMA. Then, the signal line is made by taking a 9-day EMA of the MACD line.
        When the MACD line crosses above the signal line, it means that the price might go up potentially. 
        And when the MACD line goes below the signal line, it means that the price may potentially go down and traders can sell the stock.
        ''')
        quant_fig_macd = cf.QuantFig(self.ticker_history, title="MACD Chart", legend='top', name=self.selected_ticker)
        quant_fig_macd.add_macd()
        fig_macd = quant_fig_macd.iplot(asFigure=True)
        st.plotly_chart(fig_macd)

    def show_rsi(self):
        st.header('**Relative Strength Index (RSI)**')
        st.markdown('''
        The RSI is a tool that tracks how fast and how much prices change. It has a scale from 0 to 100. 
        If the RSI goes above 70, it means that the stock may be overpriced which happens when it is overbought. 
        If the RSI is below 30, it means that the stock price may be too low or oversold.
        ''')
        quant_fig_rsi = cf.QuantFig(self.ticker_history, title="RSI Chart", legend='top', name=self.selected_ticker)
        quant_fig_rsi.add_rsi(periods=14, showbands=False)
        fig_rsi = quant_fig_rsi.iplot(asFigure=True)
        st.plotly_chart(fig_rsi)

    def show_analyst_ratings(self):
        st.header('**Analyst Ratings**')
        recommendations = self.ticker_info.recommendations
        if recommendations is not None and not recommendations.empty:
            st.write("### Latest Analyst Ratings", recommendations.tail(10))
        else:
            st.write("No analyst ratings available.")

    def show_trading_volume_chart(self):
        st.header('**Trading Volume**')
        volume_chart = self.ticker_history['Volume'].iplot(asFigure=True, kind='bar', xTitle='Date', yTitle='Volume',
                                                           title='Trading Volume', theme='pearl')
        st.plotly_chart(volume_chart, use_container_width=True)

    def show_income_statement(self):
        annual_income = self.ticker_info.financials
        quarterly_income = self.ticker_info.quarterly_financials

        st.write("### Annual Income Statement", annual_income)
        st.write("### Quarterly Income Statement", quarterly_income)

    def show_ticker_data(self):
        st.header('**Ticker Data**')
        st.write(self.sorted_ticker_history)

if __name__ == "__main__":
    app = StockAnalysisApp()
    app.run()
