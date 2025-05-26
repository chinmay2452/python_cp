import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Page configuration (must be first Streamlit command)
st.set_page_config(page_title="Stock Price Tracker", layout="wide")

# Load external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Custom background and styling
st.markdown("""
    <style>
        body {
            background-image: url('https://source.unsplash.com/1600x900/?stock,finance');
            background-size: cover;
        }
        .big-font {
            font-size:24px !important;
            font-weight:bold;
            color: #2E86C1;
        }
    </style>
""", unsafe_allow_html=True)

# Fetch stock data
def get_stock_data(symbol, api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if "Time Series (Daily)" in data:
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        df = df.astype(float)
        return df
    return None

# Fetch high momentum stocks
def get_high_momentum_stocks(api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": api_key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if "top_gainers" in data:
        top_gainers = data["top_gainers"]
        df = pd.DataFrame(top_gainers)
        df = df.rename(columns={
            "ticker": "Symbol",
            "price": "Price",
            "change_amount": "Change Amount",
            "change_percentage": "Change Percentage",
            "volume": "Volume"
        })
        return df
    return None

# Stock closing price chart
def plot_stock_data(df, stock_symbol):
    st.subheader(f"📊 Stock Price Chart for {stock_symbol}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name='Close Price', line=dict(color='blue')))
    fig.update_layout(title=f"Closing Price Trend of {stock_symbol}",
                      xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# Additional graphs
def plot_additional_graphs(df, stock_symbol):
    st.subheader(f"📈 Additional Graphs for {stock_symbol}")

    # Volume
    fig = px.bar(df, x=df.index, y="Volume", title=f"Volume Traded for {stock_symbol}")
    fig.update_layout(xaxis_title="Date", yaxis_title="Volume", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Moving Averages
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_50'], mode='lines', name='50-Day MA', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_200'], mode='lines', name='200-Day MA', line=dict(color='red')))
    fig.update_layout(title=f"Moving Averages for {stock_symbol}",
                      xaxis_title="Date", yaxis_title="Price (USD)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Opening Prices
    fig = px.line(df, x=df.index, y="Open", title=f"Opening Price Trend of {stock_symbol}",
                  labels={'Open': 'Opening Price (USD)'})
    fig.update_layout(xaxis_title="Date", yaxis_title="Opening Price (USD)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# SIP calculator
def sip_calculator():
    st.subheader("💰 SIP Calculator")
    monthly_investment = st.number_input("Monthly Investment (USD):", min_value=0.0, value=100.0)
    annual_return_rate = st.number_input("Expected Annual Return Rate (%):", min_value=0.0, value=8.0)
    investment_period = st.number_input("Investment Period (Years):", min_value=1, value=10)

    if st.button("Calculate SIP"):
        monthly_return_rate = (annual_return_rate / 100) / 12
        total_months = investment_period * 12
        future_value = monthly_investment * (((1 + monthly_return_rate) ** total_months - 1) / monthly_return_rate) * (1 + monthly_return_rate)
        total_invested = monthly_investment * total_months

        st.success(f"💸 Total Invested: ${total_invested:,.2f}")
        st.success(f"📈 Future Value: ${future_value:,.2f}")

# App entry point
def main():
    st.title("📈 ACCESS YOUR STOCK DATA HERE")
    st.sidebar.title("User Settings")
    name = st.sidebar.text_input("Enter Your Name")
    stock_symbol = st.sidebar.text_input("Stock Symbol", "AAPL")
    page = st.sidebar.radio("Navigate", ["📈 Stock Data", "💰 SIP Calculator"])

    if page == "📈 Stock Data":
        if st.sidebar.button("Get Data"):
            if not name:
                st.warning("⚠️ Please enter your name.")
                return
            st.markdown(f"<p class='big-font'>Hi, {name}! Here's the stock data for <b>{stock_symbol}</b>:</p>",
                        unsafe_allow_html=True)
            with st.spinner("🔄 Fetching stock data..."):
                data = get_stock_data(stock_symbol, "PVXV2XVF2LIILL8I")
                if data is not None:
                    st.success(f"✅ Stock Data for {stock_symbol}")
                    st.dataframe(data.head())
                    plot_stock_data(data, stock_symbol)
                    plot_additional_graphs(data, stock_symbol)
                else:
                    st.error("❌ Failed to retrieve data. Please check the stock symbol and API key.")

        # Show high momentum stocks inside stock data page
        if st.button("🚀 Show High Momentum Stocks"):
            with st.spinner("Fetching high momentum stocks..."):
                momentum_stocks = get_high_momentum_stocks("F4TQSKERMZZL1M1T")
                if momentum_stocks is not None:
                    st.success("Top High Momentum Stocks (Top Gainers)")
                    st.dataframe(momentum_stocks)
                else:
                    st.error("❌ Failed to fetch high momentum stocks.")

    elif page == "💰 SIP Calculator":
        sip_calculator()

if __name__ == "__main__":
    main()