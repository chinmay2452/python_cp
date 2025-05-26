import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Function to fetch stock data
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
    else:
        return None


# Function to fetch high momentum stocks
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
    else:
        return None


# Function to plot stock data
def plot_stock_data(df, stock_symbol):
    st.subheader(f"📊 Stock Price Chart for {stock_symbol}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name='Close Price', line=dict(color='blue')))
    fig.update_layout(title=f"Closing Price Trend of {stock_symbol}", xaxis_title="Date", yaxis_title="Price (USD)",
                          template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


# Function to plot additional graphs
def plot_additional_graphs(df, stock_symbol):
    st.subheader(f"📈 Additional Graphs for {stock_symbol}")

    # Volume Traded
    fig = px.bar(df, x=df.index, y="Volume",
                 title=f"Volume Traded for {stock_symbol}")

    fig.update_layout(xaxis_title="Date",
                      yaxis_title="Volume",
                      template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

    # Moving Averages
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index,
                             y=df['Close'],
                             mode='lines',
                             name='Close Price',
                             line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index,
                             y=df['MA_50'],
                             mode='lines',
                             name='50-Day MA',
                             line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index,
                             y=df['MA_200'],
                             mode='lines',
                             name='200-Day MA',
                             line=dict(color='red')))
    fig.update_layout(title=f"Moving Averages for {stock_symbol}",
                      xaxis_title="Date",
                      yaxis_title="Price (USD)",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Opening Prices
    fig = px.line(df, x=df.index,
                  y="Open",
                  title=f"Opening Price Trend of {stock_symbol}",
                  labels={'Open': 'Opening Price (USD)'})
    fig.update_layout(xaxis_title="Date",
                      yaxis_title="Opening Price (USD)",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


# Function for SIP Calculator
def sip_calculator():
    st.subheader("💰 SIP Calculator")
    monthly_investment = st.number_input("Monthly Investment (USD):", min_value=0.0, value=100.0)
    annual_return_rate = st.number_input("Expected Annual Return Rate (%):", min_value=0.0, value=8.0)
    investment_period = st.number_input("Investment Period (Years):", min_value=1, value=10)

    # Standard rate for comparison (e.g., 6%)
    standard_rate = 8.0

    if st.button("Calculate SIP"):
        # Calculate future value with given rate
        monthly_return_rate = (annual_return_rate / 100) / 12
        total_months = investment_period * 12
        future_value_given_rate = monthly_investment * (
                    ((1 + monthly_return_rate) ** total_months - 1) / monthly_return_rate) * (1 + monthly_return_rate)

        # Calculate future value with standard rate
        monthly_standard_rate = (standard_rate / 100) / 12
        future_value_standard_rate = monthly_investment * (
                    ((1 + monthly_standard_rate) ** total_months - 1) / monthly_standard_rate) * (
                                                 1 + monthly_standard_rate)

        # Calculate total invested amount
        total_invested_amount = monthly_investment * total_months

        # Display results
        st.success(f"*Total Invested Amount:* ${total_invested_amount:,.2f}")
        st.success(f"*Future Value (Standard Rate of {standard_rate}%):* ${future_value_standard_rate:,.2f}")
        st.success(f"*Future Value (Given Rate of {annual_return_rate}%):* ${future_value_given_rate:,.2f}")


# Main function
def main():
    st.set_page_config(page_title="Stock Price Tracker", layout="wide")

    # Custom CSS for background image and styling
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

    st.title("📈 ACCESS YOUR STOCK DATA HERE")

    currency = st.selectbox("Select Currency", ["USD", "INR", "EUR"])
    currency_symbol = {"USD": "$", "INR": "₹", "EUR": "€"}[currency]

    name = st.text_input("Enter Your Name:", "")
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, MSFT):", "AAPL")

    if st.button("Get Data"):
        if name:
            st.markdown(f"<p class='big-font'>Hi, {name}! Here's the stock data:</p>", unsafe_allow_html=True)
        else:
            st.warning("Please enter your name.")
            return

        with st.spinner("Fetching data..."):
            data = get_stock_data(stock_symbol, "PVXV2XVF2LIILL8I")  # Replace with your API Key

            if data is not None:
                st.success(f"Stock Data for {stock_symbol}")
                st.dataframe(data.head())
                plot_stock_data(data, stock_symbol)
                plot_additional_graphs(data, stock_symbol)
            else:
                st.error("Failed to retrieve data. Please check the stock symbol and API key.")

    # Add SIP Calculator
    sip_calculator()

    # Add High Momentum Stocks Feature
    st.subheader("🚀 High Momentum Stocks")
    if st.button("Show High Momentum Stocks"):
        with st.spinner("Fetching high momentum stocks..."):
            momentum_stocks = get_high_momentum_stocks("F4TQSKERMZZL1M1T")  # Replace with your API Key
            if momentum_stocks is not None:
                st.success("Top High Momentum Stocks (Top Gainers)")
                st.dataframe(momentum_stocks)
            else:
                st.error("Failed to fetch high momentum stocks. Please check your API key.")


if __name__ == "__main__":
    main()