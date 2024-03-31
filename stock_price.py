import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import yaml

# Load credentials from YAML file

with open("cred.yaml", "r") as file:
    credentials = yaml.safe_load(file)

# Authentication component

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_button = st.sidebar.button("Login")

# Check authentication

authenticated = False
if login_button:
    if username in credentials["usernames"]:
        if password == credentials["usernames"][username]["password"]:
            st.sidebar.success(f"Logged in successfully as {username}")
            authenticated = True
        else:
            st.sidebar.error("Invalid password")
    else:
        st.sidebar.error("Invalid username")

if not authenticated:
    st.error("Please login to access the application.")
    st.stop()


class StocksAnalyzerApp:
    def __init__(self):
        self.today = datetime.date.today()
        self.start_date = self.today - datetime.timedelta(days=365)
        self.end_date = self.today
        self.ticker_list = pd.read_csv('stock_list.txt')
        self.ticker_symbol = None

    def run(self):
        self.display_app_title()
        self.display_date_inputs()
        self.select_ticker_symbol()
        self.retrieve_ticker_data()
        self.display_stock_information()
        self.display_financial_metrics()
        self.display_bollinger_bands()
        self.display_macd()
        self.display_rsi()
        self.display_analyst_ratings()
        self.display_trading_volume_chart()
        self.display_income_statement()
        self.display_ticker_data()

    def display_app_title(self):
        st.markdown('''
        # Stocks Analyzer App
        Get all important insights on yours Stocks! 
        ''')
        st.write('---')

    def display_date_inputs(self):
        self.start_date = st.sidebar.date_input("Start date", self.start_date)
        self.end_date = st.sidebar.date_input("End date", self.end_date)

    def select_ticker_symbol(self):
        self.ticker_symbol = st.sidebar.selectbox('Stock ticker', self.ticker_list)

    def retrieve_ticker_data(self):
        self.ticker_data = yf.Ticker(self.ticker_symbol)
        self.ticker_df = self.ticker_data.history(period='1d', start=self.start_date, end=self.end_date)
        self.ticker_df_sorted = self.ticker_df.sort_index(ascending=False)

    def display_stock_information(self):
        string_name = self.ticker_data.info['longName']
        st.header(f'**{string_name}**')

        string_summary = self.ticker_data.info['longBusinessSummary']
        st.info(string_summary)

        asset_profile = self.ticker_data.info.get('assetProfile', {})
        if asset_profile:
            st.subheader(f'Asset Profile for {self.ticker_symbol}')
            for key, value in asset_profile.items():
                st.text(f'{key}: {value}')
        else:
            st.write("Asset profile information is not available.")

    def display_financial_metrics(self):
        st.header('**Financial Metrics**')
        metrics = {
            "Metric": ["Latest Price", "Previous Closing Price", "52 Week High Price", "52 Week Low Price",
                       "Trailing Price to Earnings Ratio", "Beta ratio: volatility indicator",
                       "PEG Ratio", "Forward P/E Ratio"],
            "Value": [
                self.ticker_data.info.get('regularMarketPrice', 'Not available'),
                self.ticker_data.info.get('previousClose', None),
                self.ticker_data.info.get('fiftyTwoWeekHigh', 'N/A'),
                self.ticker_data.info.get('fiftyTwoWeekLow', 'N/A'),
                self.ticker_data.info.get('trailingPE', 'N/A'),
                self.ticker_data.info.get('beta', 'N/A'),
                self.ticker_data.info.get('pegRatio', 'N/A'),
                self.ticker_data.info.get('forwardPE', 'N/A')
            ]
        }
        metrics_df = pd.DataFrame(metrics)
        st.table(metrics_df)

    def display_bollinger_bands(self):
        st.header('**Bollinger Bands**')
        st.markdown('''
        Bollinger Bands are a technical indicator that help traders determine entry and exit points for a trade. They can help traders identify overbought and oversold conditions. 
        When the price of the asset breaks below the lower band of the Bollinger Bands®, prices have perhaps fallen too much and are due to bounce. On the other hand, when price breaks above the upper band, the market is perhaps overbought and due for a pullback.
        ''')
        qf = cf.QuantFig(self.ticker_df, title='First Quant Figure', legend='top', name=self.ticker_symbol)
        qf.add_bollinger_bands()
        fig = qf.iplot(asFigure=True)
        st.plotly_chart(fig)

    def display_macd(self):
        st.header('**Moving Average Convergence Divergence (MACD)**')
        st.markdown('''
        The Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. The MACD is calculated by subtracting the 26-period Exponential Moving Average (EMA) from the 12-period EMA. 
        A 9-day EMA of the MACD, called the "signal line," is then plotted on top of the MACD line, which can function as a trigger for buy and sell signals.
        Traders might consider buying when the MACD line crosses above the signal line (bullish crossover) and selling or shorting when the MACD line crosses below the signal line (bearish crossover).
        ''')
        qf_macd = cf.QuantFig(self.ticker_df, title="MACD", legend='top', name=self.ticker_symbol)
        qf_macd.add_macd()
        figure = qf_macd.iplot(asFigure=True)
        st.plotly_chart(figure)

    def display_rsi(self):
        st.header('**Relative Strength Index**')
        st.markdown('''
        The RSI is calculated based on average price gains and losses over a specified period. 
        The RSI is most commonly used to identify potential overbought or oversold conditions in a market. An RSI above 70 is typically considered overbought, while an RSI below 30 is considered oversold.
        The RSI value of 50 acts as a centerline between bullish and bearish territories.
        ''')
        qf_rsi = cf.QuantFig(self.ticker_df, title="RSI", legend='top', name=self.ticker_symbol)
        qf_rsi.add_rsi(periods=14, showbands=False)
        figure_rsi = qf_rsi.iplot(asFigure=True)
        st.plotly_chart(figure_rsi)

    def display_analyst_ratings(self):
        st.header('**Analyst Rating**')
        analyst_ratings = self.ticker_data.recommendations
        if analyst_ratings is not None and not analyst_ratings.empty:
            st.write("### Most Recent Analyst Ratings", analyst_ratings.tail(10))
        else:
            st.write("No analyst ratings data available.")

    def display_trading_volume_chart(self):
        st.header('Trading Volume')
        fig2 = self.ticker_df['Volume'].iplot(asFigure=True, kind='bar', xTitle='Date', yTitle='Volume',
                                               title='Trading Volume', theme='pearl')
        st.plotly_chart(fig2, use_container_width=True)

    def display_income_statement(self):
        annual_income_statement = self.ticker_data.financials
        quarterly_income_statement = self.ticker_data.quarterly_financials

        st.write("### Annual Income Statement", annual_income_statement)
        st.write("### Quarterly Income Statement", quarterly_income_statement)

    def display_ticker_data(self):
        st.header('**Ticker data**')
        st.write(self.ticker_df_sorted)

        st.markdown('Stock Price App built by *Manish Ranjan Kashyap*')
        st.write('---')

if __name__ == "__main__":
    app = StocksAnalyzerApp()
    app.run()
