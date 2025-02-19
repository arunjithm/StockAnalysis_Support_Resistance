import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd

# Mapping for stock symbols and names
stock_options = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Larsen & Toubro": "LT.NS",
    "Axis Bank": "AXISBANK.NS",
    "ITC": "ITC.NS"
}

# Timeframe options
timeframe_options = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y"
}

# Interval options
interval_options = {
    "1 Day": "1d",
    "1 Week": "1wk",
    "1 Month": "1mo"
}

# Function to check for support
def is_support(prices, i):
    return prices[i] < prices[i-1] and prices[i] < prices[i+1]

# Function to check for resistance
def is_resistance(prices, i):
    return prices[i] > prices[i-1] and prices[i] > prices[i+1]

# Function to calculate support and resistance levels
def calculate_sr(data, min_touches, distance, tolerance):
    sr_levels = []
    prices = data['Close'].values
    
    # Loop through the data to find support and resistance levels
    for i in range(2, len(prices) - 2):
        if is_support(prices, i):
            level = prices[i]
            if is_significant_level(level, prices, sr_levels, min_touches, distance, tolerance):
                sr_levels.append(level)
        elif is_resistance(prices, i):
            level = prices[i]
            if is_significant_level(level, prices, sr_levels, min_touches, distance, tolerance):
                sr_levels.append(level)
    
    return sr_levels

# Function to check if the level is significant
def is_significant_level(level, prices, sr_levels, min_touches, distance, tolerance):
    touches = 0
    for i in range(len(prices)):
        if abs(level - prices[i]) < level * tolerance:
            touches += 1

    if touches >= min_touches:
        for existing_level in sr_levels:
            if abs(level - existing_level) < distance:
                return False
        return True
    return False

# Function to display support and resistance levels in a clean DataFrame
def display_sr_levels(sr_levels):
    supports = sorted([lvl for lvl in sr_levels if lvl < np.mean(sr_levels)])
    resistances = sorted([lvl for lvl in sr_levels if lvl > np.mean(sr_levels)], reverse=True)

    # Balance the lengths for display
    max_len = max(len(supports), len(resistances))
    supports += [None] * (max_len - len(supports))
    resistances += [None] * (max_len - len(resistances))

    sr_df = pd.DataFrame({
        'Support Levels': supports,
        'Resistance Levels': resistances
    })

    return sr_df

# Streamlit Layout
st.title("Support and Resistance Levels for Indian Stocks")

# Sidebar for Inputs
st.sidebar.header("Stock Selection and Settings")

# Dropdown for Stock Selection
selected_stock = st.sidebar.selectbox(
    "Select a Stock:",
    options=list(stock_options.keys()),
    index=0
)
stock_symbol = stock_options[selected_stock]

# Timeframe and Interval Selection
selected_timeframe = st.sidebar.selectbox(
    "Select Timeframe:",
    options=list(timeframe_options.keys()),
    index=2
)
period = timeframe_options[selected_timeframe]

selected_interval = st.sidebar.selectbox(
    "Select Interval:",
    options=list(interval_options.keys()),
    index=0
)
interval = interval_options[selected_interval]

# Parameters for Support/Resistance Calculation
min_touches = st.sidebar.slider(
    "Minimum Touches:",
    min_value=2,
    max_value=5,
    value=3,
    help="Minimum number of times the price should touch a level to consider it as support or resistance."
)

distance = st.sidebar.slider(
    "Distance Between Levels:",
    min_value=1,
    max_value=10,
    value=5,
    help="Minimum distance required between two levels to consider them as separate support or resistance."
)

tolerance = st.sidebar.slider(
    "Tolerance:",
    min_value=0.001,
    max_value=0.01,
    value=0.005,
    step=0.001,
    help="Tolerance percentage for considering prices as touching a level."
)

# Fetching Data
st.subheader(f"{selected_stock} ({stock_symbol}) - {selected_timeframe}")
data = yf.download(stock_symbol, period=period, interval=interval)

if not data.empty:
    # Calculate Support and Resistance Levels
    sr_levels = calculate_sr(data, min_touches, distance, tolerance)

    # Display the Support and Resistance Levels
    sr_df = display_sr_levels(sr_levels)
    st.dataframe(sr_df)
else:
    st.warning("No data available for the selected options.")
