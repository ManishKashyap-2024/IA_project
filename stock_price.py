import streamlit as stl
import yfinance as yfin
import pandas as pd
import cufflinks as cff
import datetime
import matplotlib.pyplot as plt
import hmac

class UserAuth:
    def __init__(self):
        self.is_authenticated = stl.session_state.get("is_authenticated", False)

    def validate_password(self):
        """This part checks if the user has put in the correct password."""
        if self.is_authenticated:
            return True

        self.show_login_form()

        if "is_authenticated" in stl.session_state and not stl.session_state["is_authenticated"]:
            stl.error("Invalid username or password.")

        return self.is_authenticated

    def show_login_form(self):
        """This part shows the login form to the user for authentication purpose."""
        with stl.form("Login Form"):
            stl.text_input("Username", key="username")
            stl.text_input("Password", type="password", key="password")
            stl.form_submit_button("Log in", on_click=self.verify_password)

    def verify_password(self):
        """This part verifies the password entered."""
        if stl.session_state["username"] in stl.secrets["passwords"] and hmac.compare_digest(
            stl.session_state["password"],
            stl.secrets.passwords[stl.session_state["username"]],
        ):
            stl.session_state["is_authenticated"] = True
            self.is_authenticated = True
            del stl.session_state["password"]  
            del stl.session_state["username"]
        else:
            stl.session_state["is_authenticated"] = False
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
        # Initialize session state variables for each feature
        features = ['bollinger_bands', 'macd', 'rsi', 'analyst_ratings', 'trading_volume', 'income_statement', 'ticker_data']
        for feature in features:
            if feature not in stl.session_state:
                stl.session_state[feature] = False

    def run(self):
        if not self.auth.validate_password():
            stl.stop()
        self.show_app_title()
        self.set_date_inputs()
        self.choose_ticker()
        self.fetch_ticker_data()
        self.show_stock_info()
        self.show_financial_metrics()

        self.init_state_variables()

        if stl.button('Show Bollinger Bands'):
            stl.session_state.bollinger_bands = True
        
        if stl.session_state.bollinger_bands:
            self.show_bollinger_bands()

        if stl.button('Show MACD Chart'):
            stl.session_state.macd = True

        if stl.session_state.macd:
            self.show_macd()

        if stl.button('Show RSI'):
            stl.session_state.rsi = True

        if stl.session_state.rsi:
            self.show_rsi()

        if stl.button('Show Analyst Ratings'):
            stl.session_state.analyst_ratings = True

        if stl.session_state.analyst_ratings:
            self.show_analyst_ratings()

        if stl.button('Show Trading Volume Chart'):
            stl.session_state.trading_volume = True

        if stl.session_state.trading_volume:
            self.show_trading_volume_chart()

        if stl.button('Show Income Statement'):
            stl.session_state.income_statement = True

        if stl.session_state.income_statement:
            self.show_income_statement()

        if stl.button('Show Ticker Data'):
            stl.session_state.ticker_data = True
            
        if stl.session_state.ticker_data:
            self.show_ticker_data()

    def show_app_title(self):
        stl.markdown('''
        # Stock Analysis Application
        One-stop shop for getting the key insights on your selected stocks at your fingertips!
        ''')
        stl.write('---')

    def set_date_inputs(self):
        self.start_date = stl.sidebar.date_input("Start Date", self.start_date)
        self.end_date = stl.sidebar.date_input("End Date", self.end_date)

    def choose_ticker(self):
        self.selected_ticker = stl.sidebar.selectbox('Stock Ticker', self.ticker_list)

    def fetch_ticker_data(self):
        self.ticker_info = yfin.Ticker(self.selected_ticker)
        self.ticker_history = self.ticker_info.history(period='1d', start=self.start_date, end=self.end_date)
        self.sorted_ticker_history = self.ticker_history.sort_index(ascending=False)

    def show_stock_info(self):
        stock_name = self.ticker_info.info['longName']
        stl.header(f'**{stock_name}**')

        stock_summary = self.ticker_info.info['longBusinessSummary']
        stl.info(stock_summary)

        asset_profile = self.ticker_info.info.get('assetProfile', {})
        if asset_profile:
            stl.subheader(f'Asset Profile for {self.selected_ticker}')
            for key, value in asset_profile.items():
                stl.text(f'{key}: {value}')
        else:
            stl.write("Asset profile information is not available.")

    def show_financial_metrics(self):
        stl.header('**Financial Metrics**')
        metrics = {
            "Metric": ["Current Price", "Previous Close", "Highest in 52 wks", "Lowest in 52 wks",
                       "PE Ratio", "Beta", "PEG Ratio", "Forward PE Ratio"],
            "Value": [
                self.ticker_info.info.get('regularMarketPrice', 'N/A'),
                self.ticker_info.info.get('previousClose', 'N/A'),
                self.ticker_info.info.get('fiftyTwoWeekHigh', 'N/A'),
                self.ticker_info.info.get('fiftyTwoWeekLow', 'N/A'),
                self.ticker_info.get('trailingPE', 'N/A'),
                self.ticker_info.get('beta', 'N/A'),
                self.ticker_info.get('pegRatio', 'N/A'),
                self.ticker_info.get('forwardPE', 'N/A')
            ]
        }
        metrics_df = pd.DataFrame(metrics)
        stl.table(metrics_df)

    def show_bollinger_bands(self):
        stl.header('**Bollinger Bands**')
        stl.markdown('''
        Bollinger Bands are one of the useful tools in stock analysis to decide when to buy or sell a stock. They show if the stock is priced too high or too low. If the stock price falls below the lower band, it might mean the stock is too cheap and could go up soon. 
        If the price rises above the upper band, it might mean the stock is too expensive and could drop in price.
        ''')
        quant_fig = cff.QuantFig(self.ticker_history, title='Bollinger Bands Chart', legend='top', name=self.selected_ticker)
        quant_fig.add_bollinger_bands()
        fig = quant_fig.iplot(asFigure=True)
        stl.plotly_chart(fig)

    def show_macd(self):
        stl.header('**MACD (Moving Average Convergence Divergence)**')
        stl.markdown('''
        The Moving Average Convergence Divergence (MACD) is a tool that helps investors know when to buy or sell stocks. 
        To get the MACD line, subtract the 26-day Exponential Moving Average (EMA) from the 12-day EMA. Then, the signal line is made by taking a 9-day EMA of the MACD line.
        When the MACD line crosses above the signal line, it means that the price might go up potentially. 
        And when the MACD line goes below the signal line, it means that the price may potentially go down and traders can sell the stock.
        ''')
        quant_fig_macd = cff.QuantFig(self.ticker_history, title="MACD Chart", legend='top', name=self.selected_ticker)
        quant_fig_macd.add_macd()
        fig_macd = quant_fig_macd.iplot(asFigure=True)
        stl.plotly_chart(fig_macd)

    def show_rsi(self):
        stl.header('**Relative Strength Index (RSI)**')
        stl.markdown('''
        The RSI is a tool that tracks how fast and how much prices change. It has a scale from 0 to 100. 
        If the RSI goes above 70, it means that the stock may be overpriced which happens when it is overbought. 
        If the RSI is below 30, it means that the stock price may be too low or oversold.
        ''')
        quant_fig_rsi = cff.QuantFig(self.ticker_history, title="RSI Chart", legend='top', name=self.selected_ticker)
        quant_fig_rsi.add_rsi(periods=14, showbands=False)
        fig_rsi = quant_fig_rsi.iplot(asFigure=True)
        stl.plotly_chart(fig_rsi)

    def show_analyst_ratings(self):
        stl.header('**Analyst Ratings**')
        recommendations = self.ticker_info.recommendations
        if recommendations is not None and not recommendations.empty:
            stl.write("### Latest Analyst Ratings", recommendations.tail(10))
        else:
            stl.write("No analyst ratings available.")

    def show_trading_volume_chart(self):
        stl.header('**Trading Volume**')
        volume_chart = self.ticker_history['Volume'].iplot(asFigure=True, kind='bar', xTitle='Date', yTitle='Volume',
                                                           title='Trading Volume', theme='pearl')
        stl.plotly_chart(volume_chart, use_container_width=True)

    def show_income_statement(self):
        annual_income = self.ticker_info.financials
        quarterly_income = self.ticker_info.quarterly_financials

        stl.write("### Annual Income Statement", annual_income)
        stl.write("### Quarterly Income Statement", quarterly_income)

    def show_ticker_data(self):
        stl.header('**Ticker Data**')
        stl.write(self.sorted_ticker_history)

        stl.markdown('Stock Analysis App by *Your Name*')
        stl.write('---')

if __name__ == "__main__":
    app = StockAnalysisApp()
    app.run()
