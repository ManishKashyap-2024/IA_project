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
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text

# Establish connection to SQLite database
engine = create_engine(st.secrets["connections"]["user_db"]["url"])

class UserAuth:
    def __init__(self):
        self.is_authenticated = st.session_state.get("is_authenticated", False)
        self.is_admin_authenticated = st.session_state.get("is_admin_authenticated", False)

    def validate_user_password(self):
        """Validate user credentials."""
        if self.is_authenticated:
            return True

        self.show_user_login_form()

        if "is_authenticated" in st.session_state and not st.session_state["is_authenticated"]:
            st.error("Invalid username or password.")

        return self.is_authenticated

    def validate_admin_password(self):
        """Validate admin credentials."""
        if self.is_admin_authenticated:
            return True

        self.show_admin_login_form()

        if "is_admin_authenticated" in st.session_state and not st.session_state["is_admin_authenticated"]:
            st.error("Invalid admin credentials.")

        return self.is_admin_authenticated

    def show_user_login_form(self):
        """Form for user login."""
        with st.form("User Login Form"):
            st.text_input("User ID", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=self.verify_user_password)

    def show_admin_login_form(self):
        """Form for admin login."""
        with st.form("Admin Login Form"):
            st.text_input("Admin ID", key="admin_username")
            st.text_input("Admin Password", type="password", key="admin_password")
            st.form_submit_button("Admin Log in", on_click=self.verify_admin_password)

    def verify_user_password(self):
        """Check user credentials."""
        # User credential verification logic
        if st.session_state["username"] == "correct_user" and st.session_state["password"] == "correct_password":
            st.session_state["is_authenticated"] = True
            self.is_authenticated = True
        else:
            st.session_state["is_authenticated"] = False
            self.is_authenticated = False

    def verify_admin_password(self):
        """Check admin credentials."""
        # Admin credential verification logic
        admin_id = st.secrets["admin"]["admin_id"]
        admin_password = st.secrets["admin"]["admin_password"]
        
        if st.session_state["admin_username"] == admin_id and st.session_state["admin_password"] == admin_password:
            st.session_state["is_admin_authenticated"] = True
            self.is_admin_authenticated = True
        else:
            st.session_state["is_admin_authenticated"] = False
            self.is_admin_authenticated = False

    def admin_dashboard(self):
        """Display admin dashboard with options for viewing the database."""
        st.sidebar.title("Admin Dashboard")
        st.sidebar.write("Welcome, Admin!")

        if st.sidebar.button("View All Users"):
            self.view_database()

    def view_database(self):
        """Allow the admin to view the database contents."""
        st.write("**Viewing Database Contents**")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users")).fetchall()
            if result:
                st.write("Contents of users table:")
                st.write(result)
            else:
                st.write("No data found in users table.")

class StockAnalysisApp:
    def __init__(self):
        self.auth = UserAuth()

    def run(self):
        st.sidebar.title("Login")
        app_mode = st.sidebar.selectbox("Select Mode", ["User Login", "Admin Login"])

        if app_mode == "User Login":
            if self.auth.validate_user_password():
                self.stock_analysis()
        elif app_mode == "Admin Login":
            if self.auth.validate_admin_password():
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
