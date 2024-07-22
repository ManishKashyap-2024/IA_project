import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime
import matplotlib.pyplot as plt
import hmac

class UserAuth:
    def __init__(self):
        self.is_authenticated = st.session_state.get("is_authenticated", False)

    def validate_password(self):
        """Checks if the user has provided the correct password."""
        if self.is_authenticated:
            return True

        self.show_login_form()

        if "is_authenticated" in st.session_state and not st.session_state["is_authenticated"]:
            st.error("Invalid username or password.")

        return self.is_authenticated

    def show_login_form(self):
        """Displays the login form for user authentication."""
        with st.form("Login Form"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=self.verify_password)

    def verify_password(self):
        """Verifies the password entered by the user."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["is_authenticated"] = True
            self.is_authenticated = True
            del st.session_state["password"]  
            del st.session_state["username"]
        else:
            st.session_state["is_authenticated"] = False
            self.is_authenticated = False

class StockAnalysisApp:
    def __init__(self):
        self.auth = UserAuth()
        self.today = datetime.date.today()
        self.start_date = self.today - datetime.timedelta(days=365)
        self.end_date = self.today
        self.ticker_list = pd.read_csv('stock_list.txt')
        self.selected_ticker = None

    def init_state_variables(self):
        # Initialize session state variables for each analysis feature
        features = ['bollinger_bands', 'macd', 'rsi', 'analyst_ratings', 'trading_volume', 'income_statement', 'ticker_data']
        for feature in features:
            if feature not in st.session_state:
                st.session_state[feature] = False

    def run(self):
        if not self.auth.validate_password():
            st.stop()
        self.show_app_title()
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

    def show_app_title(self):
        st.markdown('''
        # Stock Analysis Application
        Get all the essential insights on your selected stocks!
        ''')
        st.write('---')

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
            "Metric": ["Latest Price", "Previous Close", "52 Week High", "52 Week Low",
                       "Trailing P/E Ratio", "Beta", "PEG Ratio", "Forward P/E Ratio"],
            "Value": [
                self.ticker_info.info.get('regularMarketPrice', 'N/A'),
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
        Bollinger Bands help traders identify entry and exit points for a trade. They indicate overbought and oversold conditions. 
        When the price falls below the lower band, it may be a sign of oversold conditions and a potential bounce. When the price rises above the upper band, it may indicate overbought conditions and a potential pullback.
        ''')
        quant_fig = cf.QuantFig(self.ticker_history, title='Bollinger Bands Chart', legend='top', name=self.selected_ticker)
        quant_fig.add_bollinger_bands()
        fig = quant_fig.iplot(asFigure=True)
        st.plotly_chart(fig)

    def show_macd(self):
        st.header('**MACD (Moving Average Convergence Divergence)**')
        st.markdown('''
        The MACD is a momentum indicator that shows the relationship between two moving averages of a stock’s price. The MACD is calculated by subtracting the 26-period EMA from the 12-period EMA. 
        A 9-day EMA of the MACD, called the "signal line," is plotted on top of the MACD line, indicating buy and sell signals.
        Traders might buy when the MACD crosses above the signal line (bullish) and sell when it crosses below the signal line (bearish).
        ''')
        quant_fig_macd = cf.QuantFig(self.ticker_history, title="MACD Chart", legend='top', name=self.selected_ticker)
        quant_fig_macd.add_macd()
        fig_macd = quant_fig_macd.iplot(asFigure=True)
        st.plotly_chart(fig_macd)

    def show_rsi(self):
        st.header('**Relative Strength Index (RSI)**')
        st.markdown('''
        The RSI is a momentum oscillator that measures the speed and change of price movements. It ranges from 0 to 100. An RSI above 70 is considered overbought, while an RSI below 30 is considered oversold.
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

        st.markdown('Stock Analysis App by *Your Name*')
        st.write('---')

if __name__ == "__main__":
    app = StockAnalysisApp()
    app.run()
