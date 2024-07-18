import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from datetime import datetime, timedelta
import requests

# Set page config
st.set_page_config(page_title="Cosmic Market Analyzer", layout="wide", initial_sidebar_state="expanded")

# Function to add background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/jpeg;base64,{encoded_string.decode()});
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# Add background image
add_bg_from_local(r"C:\Users\Administrator.MSI\Desktop\appbackground.jpeg")

# Custom CSS
st.markdown("""
<style>
body {color: #FFFFFF;}
.stApp {background-color: rgba(0,0,0,0.7);}
.stButton > button {
    color: #00FFFF;
    border-radius: 20px;
    border: 2px solid #FF00FF;
    background-color: rgba(0,0,0,0.5);
}
.stTextInput > div > div > input {
    color: #00FFFF;
    background-color: rgba(0,0,0,0.5);
    border: 2px solid #FF00FF;
    border-radius: 20px;
}
.stSelectbox > div > div > select {
    color: #00FFFF;
    background-color: rgba(0,0,0,0.5);
    border: 2px solid #FF00FF;
    border-radius: 20px;
}
.stDateInput > div > div > input {
    color: #00FFFF;
    background-color: rgba(0,0,0,0.5);
    border: 2px solid #FF00FF;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h1 style='text-align: center; color: #00FFFF;'>Cosmic Market Analyzer</h1>", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Stocks", "Cryptocurrencies", "Market Trends"])

# Function to load data
@st.cache_data
def load_data(symbol, start, end):
    try:
        data = yf.download(symbol, start, end)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Function to create candlestick chart
def create_candlestick_chart(data, title):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=data['Date'], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume'), row=2, col=1)
    fig.update_layout(title=title, height=600, showlegend=False, 
                      paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0.5)', 
                      font=dict(color='#00FFFF'))
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig

if page == "Stocks":
    st.markdown("<h2 style='color: #00FFFF;'>Stock Analysis</h2>", unsafe_allow_html=True)
    
    ticker = st.text_input('Enter stock ticker', 'AAPL')
    start_date = st.date_input('Start date', pd.to_datetime('2021-01-01'))
    end_date = st.date_input('End date', pd.to_datetime('today'))

    data = load_data(ticker, start_date, end_date)

    if data is not None and not data.empty:
        st.plotly_chart(create_candlestick_chart(data, f'{ticker} Stock Analysis'), use_container_width=True)
        
        st.markdown("<h3 style='color: #00FFFF;'>Key Metrics</h3>", unsafe_allow_html=True)
        current_price = data['Close'].iloc[-1]
        price_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
        price_change_percent = (price_change / data['Close'].iloc[-2]) * 100
        st.metric("Current Price", f"${current_price:.2f}", f"{price_change:.2f} ({price_change_percent:.2f}%)")

elif page == "Cryptocurrencies":
    st.markdown("<h2 style='color: #00FFFF;'>Cryptocurrency Analysis</h2>", unsafe_allow_html=True)
    
    crypto = st.text_input('Enter cryptocurrency symbol', 'BTC-USD')
    crypto_start_date = st.date_input('Start date', pd.to_datetime('2021-01-01'))
    crypto_end_date = st.date_input('End date', pd.to_datetime('today'))

    crypto_data = load_data(crypto, crypto_start_date, crypto_end_date)

    if crypto_data is not None and not crypto_data.empty:
        st.plotly_chart(create_candlestick_chart(crypto_data, f'{crypto} Price'), use_container_width=True)
        
        st.markdown("<h3 style='color: #00FFFF;'>Key Metrics</h3>", unsafe_allow_html=True)
        current_price = crypto_data['Close'].iloc[-1]
        price_change = crypto_data['Close'].iloc[-1] - crypto_data['Close'].iloc[-2]
        price_change_percent = (price_change / crypto_data['Close'].iloc[-2]) * 100
        st.metric("Current Price", f"${current_price:.2f}", f"{price_change:.2f} ({price_change_percent:.2f}%)")

elif page == "Market Trends":
    st.markdown("<h2 style='color: #00FFFF;'>Market Trends</h2>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: #00FFFF;'>Major Indices</h3>", unsafe_allow_html=True)
    indices = ['^GSPC', '^DJI', '^IXIC']
    index_names = ['S&P 500', 'Dow Jones', 'NASDAQ']
    
    for idx, name in zip(indices, index_names):
        data = yf.download(idx, period="1d")
        if not data.empty:
            current_value = data['Close'].iloc[-1]
            previous_close = data['Close'].iloc[-2] if len(data) > 1 else data['Open'].iloc[-1]
            change = current_value - previous_close
            change_percent = (change / previous_close) * 100
            st.metric(name, f"{current_value:.2f}", f"{change:.2f} ({change_percent:.2f}%)")

# Add a futuristic footer
st.markdown(
    """
    <div style='position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 10px; background-color: rgba(0,0,0,0.5);'>
        <p style='color: #00FFFF;'>Powered by Cosmic AI • Real-time Galactic Market Analysis • &copy; 2024 Cosmic Market Analyzer</p>
    </div>
    """,
    unsafe_allow_html=True
)