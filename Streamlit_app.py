import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Set page config
st.set_page_config(page_title="Enhanced Cosmic Market Analyzer", layout="wide", initial_sidebar_state="expanded")

# ... [Keep the existing background image and styling code] ...

# App title
st.markdown("<h1 style='text-align: center; color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>Enhanced Cosmic Market Analyzer</h1>", unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["US Stocks", "Cryptocurrencies", "Market Trends", "Comparison Tool"])

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

# Function to calculate technical indicators
def calculate_indicators(data):
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    return data

# Function to fetch news (placeholder - replace with actual API call)
def fetch_news(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = soup.find_all('li', class_='js-stream-content')
    news = []
    for item in news_items[:5]:  # Get top 5 news items
        title = item.find('h3').text if item.find('h3') else "No title"
        link = item.find('a')['href'] if item.find('a') else "#"
        news.append({"title": title, "link": f"https://finance.yahoo.com{link}"})
    return news

# Placeholder function for sentiment analysis
def analyze_sentiment(text):
    # This is a placeholder. In a real scenario, you'd use a sentiment analysis model or API
    return np.random.choice(['Positive', 'Neutral', 'Negative'])

if page == "US Stocks":
    st.markdown("<h2 style='color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>US Stock Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.text_input('Enter stock ticker', 'AAPL')
    with col2:
        start_date = st.date_input('Start date', pd.to_datetime('2021-01-01'))
    with col3:
        end_date = st.date_input('End date', pd.to_datetime('today'))

    # Time range slider
    days_to_plot = st.slider('Select time range (days)', 30, 365, 180)
    start_date = end_date - timedelta(days=days_to_plot)

    data = load_data(ticker, start_date, end_date)

    if data is not None and not data.empty:
        data = calculate_indicators(data)
        
        st.plotly_chart(create_candlestick_chart(data, f'{ticker} Stock Analysis'), use_container_width=True)
        
        # Technical Indicators
        st.markdown("<h3 style='color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>Technical Indicators</h3>", unsafe_allow_html=True)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.25, 0.25])
        
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA20'], name='SMA20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA50'], name='SMA50'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=data['Date'], y=data['RSI'], name='RSI'), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        fig.add_trace(go.Scatter(x=data['Date'], y=data['MACD'], name='MACD'), row=3, col=1)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Signal_Line'], name='Signal Line'), row=3, col=1)
        
        fig.update_layout(height=800, title_text="Technical Indicators", 
                          paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0.5)', 
                          font=dict(color='#00FFFF'))
        st.plotly_chart(fig, use_container_width=True)
        
        # News Integration
        st.markdown("<h3 style='color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>Recent News</h3>", unsafe_allow_html=True)
        news = fetch_news(ticker)
        for item in news:
            sentiment = analyze_sentiment(item['title'])
            st.markdown(f"[{item['title']}]({item['link']}) - Sentiment: {sentiment}")

elif page == "Cryptocurrencies":
    st.markdown("<h2 style='color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>Cryptocurrency Analysis</h2>", unsafe_allow_html=True)
    
    # ... [Keep existing cryptocurrency analysis code and add similar enhancements as in the US Stocks section] ...

elif page == "Market Trends":
    st.markdown("<h2 style='color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>Market Trends</h2>", unsafe_allow_html=True)
    
    # ... [Keep existing market trends code] ...

elif page == "Comparison Tool":
    st.markdown("<h2 style='color: #00FFFF; background-color: rgba(0,0,0,0.7); padding: 10px;'>Comparison Tool</h2>", unsafe_allow_html=True)
    
    symbols = st.multiselect('Select symbols to compare', ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB', 'TSLA'])
    start_date = st.date_input('Start date', pd.to_datetime('2021-01-01'))
    end_date = st.date_input('End date', pd.to_datetime('today'))
    
    if symbols:
        comparison_data = pd.DataFrame()
        for symbol in symbols:
            data = load_data(symbol, start_date, end_date)
            if data is not None:
                comparison_data[symbol] = data['Close']
        
        if not comparison_data.empty:
            normalized_data = comparison_data / comparison_data.iloc[0] * 100
            
            fig = go.Figure()
            for column in normalized_data.columns:
                fig.add_trace(go.Scatter(x=normalized_data.index, y=normalized_data[column], name=column))
            
            fig.update_layout(title='Normalized Price Comparison', xaxis_title='Date', yaxis_title='Normalized Price (%)',
                              paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0.5)', 
                              font=dict(color='#00FFFF'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected symbols and date range.")
    else:
        st.warning("Please select at least one symbol to compare.")

# ... [Keep the existing footer] ...