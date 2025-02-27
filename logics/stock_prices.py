import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime
import os
import plotly.graph_objs as go
from logics.utils import calculate_rsi, calculate_bollinger_bands, calculate_macd

class StockAnalysisApp:
    def __init__(self):
        self.today = datetime.date.today()
        self.start_date      = self.today - datetime.timedelta(days=365)
        self.end_date        = self.today
        self.ticker_list     = self.load_ticker_list()  # Use cached method to load ticker list
        self.selected_ticker = None

    def load_ticker_list(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'stock_list.txt')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return pd.read_csv(file_path)


    def init_state_variables(self):
        features = ['bollinger_bands', 'macd', 'rsi', 'analyst_ratings', 'trading_volume', 'income_statement', 'ticker_data']
        for feature in features:
            if feature not in st.session_state:
                st.session_state[feature] = False

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


        col1, col2, col3, col4 = st.columns([1,1,1,1])
        with col1:
            if st.button('Show Bollinger Bands'):
                st.session_state.bollinger_bands = True
        with col2:
            if st.button('Show MACD Chart'):
                st.session_state.macd = True
        with col3:
            if st.button('Show RSI'):
                st.session_state.rsi = True
        with col4:
            if st.button('Show Trading Volume Chart'):
                st.session_state.trading_volume = True

        st.divider()


        if st.sidebar.toggle('Show Analyst Ratings'):
                self.show_analyst_ratings()

        if st.sidebar.toggle('Show Income Statement'):
            self.show_income_statement()

        if st.sidebar.toggle('Show Ticker Data'):
            self.show_ticker_data()



        if st.session_state.bollinger_bands:
            self.show_bollinger_bands()

        if st.session_state.macd:
            self.show_macd()

        if st.session_state.rsi:
            self.show_rsi()



        if st.session_state.trading_volume:
            self.show_trading_volume_chart()

            



    def set_date_inputs(self):
        col1, col2 = st.sidebar.columns([1,1])
        with col1:
            self.start_date = st.date_input("Start Date", self.start_date)
        with col2:
            self.end_date   = st.date_input("End Date", self.end_date)

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
        
        # Calculate Bollinger Bands
        rolling_mean, upper_band, lower_band = calculate_bollinger_bands(self.ticker_history)
        
        # Create the Plotly figure
        fig = go.Figure()
        
        # Add traces
        fig.add_trace(go.Scatter(x=self.ticker_history.index, y=self.ticker_history['Close'], name='Close Price'))
        fig.add_trace(go.Scatter(x=self.ticker_history.index, y=upper_band, name='Upper Band', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=self.ticker_history.index, y=rolling_mean, name='Rolling Mean', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=self.ticker_history.index, y=lower_band, name='Lower Band', line=dict(color='green')))
        
        # Update layout
        fig.update_layout(
            title='Bollinger Bands',
            xaxis_title='Date',
            yaxis_title='Price',
            legend_title='Legend'
        )
        
        # Display the figure in Streamlit
        st.plotly_chart(fig)

    def show_macd(self):
        st.header('**MACD (Moving Average Convergence Divergence)**')
        
        # Calculate MACD components
        macd_line, signal_line, macd_histogram = calculate_macd(self.ticker_history)
        
        # Create the Plotly figure
        fig = go.Figure()
        
        # Add MACD line
        fig.add_trace(go.Scatter(
            x=self.ticker_history.index,
            y=macd_line,
            name='MACD Line',
            line=dict(color='blue')
        ))
        
        # Add Signal line
        fig.add_trace(go.Scatter(
            x=self.ticker_history.index,
            y=signal_line,
            name='Signal Line',
            line=dict(color='red')
        ))
        
        # Add MACD Histogram
        fig.add_trace(go.Bar(
            x=self.ticker_history.index,
            y=macd_histogram,
            name='MACD Histogram',
            marker=dict(color='green')
        )
        )
        
        # Update layout
        fig.update_layout(
            title='MACD Chart',
            xaxis_title='Date',
            yaxis_title='MACD',
            legend_title='Legend',
            hovermode='x unified'
        )
        
        # Display the figure in Streamlit
        st.plotly_chart(fig)


    def show_rsi(self):
        st.header('**Relative Strength Index (RSI)**')
        
        # Calculate RSI
        rsi = calculate_rsi(self.ticker_history, periods=14)
        
        # Create the Plotly figure
        fig = go.Figure()
        
        # Add RSI line
        fig.add_trace(go.Scatter(
            x=self.ticker_history.index,
            y=rsi,
            name='RSI',
            line=dict(color='purple')
        ))
        
        # Add overbought and oversold levels
        fig.add_trace(go.Scatter(
            x=self.ticker_history.index,
            y=[70] * len(self.ticker_history),
            name='Overbought (70)',
            line=dict(color='red', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=self.ticker_history.index,
            y=[30] * len(self.ticker_history),
            name='Oversold (30)',
            line=dict(color='green', dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            title='RSI Chart',
            xaxis_title='Date',
            yaxis_title='RSI',
            legend_title='Legend',
            hovermode='x unified'
        )
        
        # Display the figure in Streamlit
        st.plotly_chart(fig)


    def show_trading_volume_chart(self):
        st.header('**Trading Volume**')
        
        # Create the Plotly figure
        fig = go.Figure()
        
        # Add volume bars
        fig.add_trace(go.Bar(
            x=self.ticker_history.index,
            y=self.ticker_history['Volume'],
            name='Volume',
            marker=dict(color='rgba(255, 153, 51, 1.0)')  # Use a valid color format
        ))
        
        # Update layout
        fig.update_layout(
            title='Trading Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            hovermode='x unified'
        )
        
        # Display the figure in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def show_analyst_ratings(self):
        st.header('**Analyst Ratings**')
        recommendations = self.ticker_info.recommendations
        if recommendations is not None and not recommendations.empty:
            st.write("### Latest Analyst Ratings", recommendations.tail(10))
        else:
            st.write("No analyst ratings available.")

    def show_trading_volume_chart(self):
        st.header('**Trading Volume**')
        
        # Create the Plotly figure
        fig = go.Figure()
        
        # Add volume bars
        fig.add_trace(go.Bar(
            x=self.ticker_history.index,
            y=self.ticker_history['Volume'],
            name='Volume',
            marker=dict(color='rgba(255, 153, 51, 1.0)')  # Use a valid color format
        ))
        
        # Update layout
        fig.update_layout(
            title='Trading Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            hovermode='x unified'
        )
        
        # Display the figure in Streamlit
        st.plotly_chart(fig, use_container_width=True)

    def show_income_statement(self):
        annual_income = self.ticker_info.financials
        quarterly_income = self.ticker_info.quarterly_financials

        st.write("### Annual Income Statement", annual_income)
        st.write("### Quarterly Income Statement", quarterly_income)

    def show_ticker_data(self):
        st.header('**Ticker Data**')
        st.write(self.sorted_ticker_history)
