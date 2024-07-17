import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# App title
st.set_page_config(page_title="Enhanced Stock Trading App", layout="wide")
st.title('Enhanced Stock Trading App')

# Sidebar for user input
st.sidebar.header('User Input')
ticker = st.sidebar.text_input('Enter stock ticker', 'AAPL')
start_date = st.sidebar.date_input('Start date', pd.to_datetime('2021-01-01'))
end_date = st.sidebar.date_input('End date', pd.to_datetime('today'))
timeframe = st.sidebar.selectbox('Select timeframe', ['1d', '1wk', '1mo'])

# Function to load data
@st.cache_data
def load_data(ticker, start, end, timeframe):
    try:
        data = yf.download(ticker, start, end, interval=timeframe)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Fetch data
data = load_data(ticker, start_date, end_date, timeframe)

if data is not None and not data.empty:
    # Display data
    st.subheader(f'{ticker} Stock Data')
    st.dataframe(data.tail())

    # Calculate additional metrics
    data['Returns'] = data['Close'].pct_change()
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()

    # Create interactive chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Price and SMA lines
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close Price', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA20'], name='SMA20', line=dict(color='orange')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA50'], name='SMA50', line=dict(color='red')), row=1, col=1)

    # Volume bars
    fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume', marker_color='lightblue'), row=2, col=1)

    # Update layout
    fig.update_layout(title=f'{ticker} Stock Price and Volume', height=800, showlegend=True)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # Display performance metrics
    st.subheader('Performance Metrics')
    total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
    volatility = data['Returns'].std() * (252 ** 0.5) * 100  # Annualized volatility

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Return", f"{total_return:.2f}%")
    with col2:
        st.metric("Annualized Volatility", f"{volatility:.2f}%")

else:
    st.warning("No data available for the selected ticker and date range.")

# Add a note about data source
st.sidebar.markdown("---")
st.sidebar.markdown("Data provided by Yahoo Finance")