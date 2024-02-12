import streamlit as st
import yfinance as yf
import pandas as pd
import cufflinks as cf
import datetime
import matplotlib.pyplot as plt

# App title
st.markdown('''
# Stocks Analyzer App
Get all important insights on yours Stocks! 

''')

st.write('---')


# Use datetime.date.today() to get today's date
today = datetime.date.today()

# Flexible start date but fixing the end date to today
start_date = st.sidebar.date_input("Start date", today - datetime.timedelta(days=365))  # Example: Default start date set to one year ago
end_date = st.sidebar.date_input("End date", today)  # End date fixed to today

# Retrieving tickers data
ticker_list = pd.read_csv('stock_list.txt')
tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list)  # Select ticker symbol
tickerData = yf.Ticker(tickerSymbol)  # Get ticker data
tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)  # Get the historical prices for this ticker
tickerDf_sorted = tickerDf.sort_index(ascending=False)

# Stock information
string_name = tickerData.info['longName']
st.header(f'**{string_name}**')

string_summary = tickerData.info['longBusinessSummary']
st.info(string_summary)

# Fetch the asset profile
asset_profile = tickerData.info.get('assetProfile', {})
if asset_profile:
    st.subheader(f'Asset Profile for {ticker_symbol}')
    for key, value in asset_profile.items():
        st.text(f'{key}: {value}')
else:
    st.write("Asset profile information is not available.")

# Financial metrics in a table
st.header('**Financial Metrics**')
metrics = {
    "Metric": ["Latest Price", "Previous Closing Price", "52 Week High Price", "52 Week Low Price", "Price to Earnings Ratio","Beta ratio: volatility indicator",
    "PEG Ratio", "Last Earnings Date", "Next Earnings Date", "Forward P/E Ratio"],
    "Value": [
        tickerData.info.get('regularMarketPrice', 'Not available'),
        tickerData.info.get('previousClose', None),
        tickerData.info.get('fiftyTwoWeekHigh', 'N/A'),
        tickerData.info.get('fiftyTwoWeekLow', 'N/A'),
        tickerData.info.get('trailingPE', 'N/A'), 
        tickerData.info.get('beta', 'N/A'),
        tickerData.info.get('pegRatio', 'N/A'),
        tickerData.info.get('lastEarningsDate', 'N/A'),
        tickerData.info.get('nextEarningsDate', 'N/A'),
        tickerData.info.get('forwardPE', 'N/A')
    ]
}
metrics_df = pd.DataFrame(metrics)
st.table(metrics_df)

# Bollinger bands
st.header('**Bollinger Bands**')
st.markdown('''
Bollinger Bands are a technical indicator that help traders determine entry and exit points for a trade. They can help traders identify overbought and oversold conditions. 
When the price of the asset breaks below the lower band of the Bollinger Bands®, prices have perhaps fallen too much and are due to bounce. On the other hand, when price breaks above the upper band, the market is perhaps overbought and due for a pullback.
''')
qf = cf.QuantFig(tickerDf, title='First Quant Figure', legend='top', name=tickerSymbol)
qf.add_bollinger_bands()
fig = qf.iplot(asFigure=True)
st.plotly_chart(fig)

# Moving Average Convergence Divergence (MACD)
st.header('**Moving Average Convergence Divergence (MACD)**')
st.markdown('''
The Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. The MACD is calculated by subtracting the 26-period Exponential Moving Average (EMA) from the 12-period EMA. 
A 9-day EMA of the MACD, called the "signal line," is then plotted on top of the MACD line, which can function as a trigger for buy and sell signals.
Traders might consider buying when the MACD line crosses above the signal line (bullish crossover) and selling or shorting when the MACD line crosses below the signal line (bearish crossover).
''')
qf_macd = cf.QuantFig(tickerDf, title="MACD", legend='top', name=tickerSymbol)
qf_macd.add_macd()
figure=qf_macd.iplot(asFigure=True)
st.plotly_chart(figure)

# Relative Strength Index
st.header('**Relative Strength Index**')
st.markdown('''
The RSI is calculated based on average price gains and losses over a specified period. 
The RSI is most commonly used to identify potential overbought or oversold conditions in a market. An RSI above 70 is typically considered overbought, while an RSI below 30 is considered oversold.
The RSI value of 50 acts as a centerline between bullish and bearish territories.
''')
qf_rsi = cf.QuantFig(tickerDf, title="RSI", legend='top', name=tickerSymbol)
qf_rsi.add_rsi(periods=14, showbands=False)
figure_rsi=qf_rsi.iplot(asFigure=True)
st.plotly_chart(figure_rsi)

# Show Analyst Rating

def show_analyst_ratings(ticker_symbol):
    # Fetch analyst ratings
    ticker = yf.Ticker(ticker_symbol)
    analyst_ratings = ticker.recommendations

    if analyst_ratings is not None and not analyst_ratings.empty:
        # Show the most recent 10 ratings
        st.write("### Most Recent Analyst Ratings", analyst_ratings.tail(10))
    else:
        st.write("No analyst ratings data available.")

st.header('**Analyst Rating**')
show_analyst_ratings(tickerSymbol)

# Trading Volume Chart
st.header('Trading Volume')
fig2 = tickerDf['Volume'].iplot(asFigure=True, kind='bar', xTitle='Date', yTitle='Volume', title='Trading Volume', theme='pearl')
st.plotly_chart(fig2, use_container_width=True)


# Income Statement 
annual_income_statement = tickerData.financials
quarterly_income_statement = tickerData.quarterly_financials

# Display the income statement data
st.write("### Annual Income Statement", annual_income_statement)
st.write("### Quarterly Income Statement", quarterly_income_statement)

# Ticker Data (Including Trading Volume Chart)

st.header('**Ticker data**')
st.write(tickerDf_sorted)

st.markdown('Stock Price App built by *Manish Ranjan Kashyap*')
st.write('---')
