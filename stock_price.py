import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime
from UserAuth import UserAuth
import mysql.connector
import streamlit as st


class StockAnalysisApp:
    def __init__(self):
        self.auth = UserAuth()
        self.today = datetime.date.today()
        self.start_date = self.today - datetime.timedelta(days=365)
        self.end_date = self.today
        # self.ticker_list = pd.read_csv('stock_list.txt')
        self.ticker_list = pd.read_csv('stock_list.txt', header=None).squeeze("columns")

        self.selected_ticker = None

    def init_state_variables(self):
        features = ['bollinger_bands', 'macd', 'rsi', 'analyst_ratings', 'trading_volume', 'income_statement', 'ticker_data']
        for feature in features:
            if feature not in st.session_state:
                st.session_state[feature] = False

    def run(self):
        if not st.session_state.get("is_authenticated") and not st.session_state.get("is_admin_authenticated"):
            tab1, tab2 = st.tabs(["User Login", "Admin Login"])

            with tab1:
                self.auth.validate_user_password()

                if st.session_state.get("is_authenticated"):
                    st.session_state["is_admin_authenticated"] = False
                    self.stock_analysis()

            with tab2:
                if self.auth.validate_admin_password():
                    self.auth.admin_dashboard()

        elif st.session_state.get("is_authenticated"):
            self.stock_analysis()

        elif st.session_state.get("is_admin_authenticated"):
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
        # self.selected_ticker = st.sidebar.selectbox('Stock Ticker', self.ticker_list)
        self.selected_ticker = st.sidebar.selectbox('Stock Ticker', self.ticker_list.tolist())

    def fetch_ticker_data(self):
        self.ticker_info = yf.Ticker(self.selected_ticker)
        self.ticker_history = self.ticker_info.history(period='1d', start=self.start_date, end=self.end_date)
        self.sorted_ticker_history = self.ticker_history.sort_index(ascending=False)


    def show_stock_info(self):
        st.write("Working")
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
        quant_fig = cf.QuantFig(self.ticker_history, title='Bollinger Bands Chart', legend='top', name=self.selected_ticker)
        quant_fig.add_bollinger_bands()
        fig = quant_fig.iplot(asFigure=True)
        st.plotly_chart(fig)

    def show_macd(self):
        st.header('**MACD (Moving Average Convergence Divergence)**')
        quant_fig_macd = cf.QuantFig(self.ticker_history, title="MACD Chart", legend='top', name=self.selected_ticker)
        quant_fig_macd.add_macd()
        fig_macd = quant_fig_macd.iplot(asFigure=True)
        st.plotly_chart(fig_macd)

    def show_rsi(self):
        st.header('**Relative Strength Index (RSI)**')
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
        volume_chart = self.ticker_history['Volume'].iplot(asFigure=True, kind='bar', xTitle='Date', yTitle='Volume', title='Trading Volume', theme='pearl')
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
