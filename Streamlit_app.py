import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(page_title="Cosmic Stock Analyzer", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# App title
st.markdown("<h1 style='text-align: center; color: #00FFFF;'>Cosmic Stock Analyzer</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #FF00FF;'>Control Panel</h3>", unsafe_allow_html=True)
    ticker = st.text_input('Enter stock ticker', 'AAPL')
    start_date = st.date_input('Start date', pd.to_datetime('2021-01-01'))
    end_date = st.date_input('End date', pd.to_datetime('today'))
    timeframe = st.selectbox('Select timeframe', ['1d', '1wk', '1mo'])

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
    # Display data in an expander
    with st.expander("View Raw Data"):
        st.dataframe(data.tail(), use_container_width=True)

    # Calculate additional metrics
    data['Returns'] = data['Close'].pct_change()
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA50'] = data['Close'].rolling(window=50).mean()

    # Create interactive chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Price and SMA lines
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close Price', line=dict(color='#00FFFF')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA20'], name='SMA20', line=dict(color='#FF00FF')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA50'], name='SMA50', line=dict(color='#FF8C00')), row=1, col=1)

    # Volume bars
    fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume', marker_color='rgba(0, 255, 255, 0.5)'), row=2, col=1)

    # Update layout
    fig.update_layout(
        title=f'{ticker} Stock Analysis',
        height=800,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0.5)',
        plot_bgcolor='rgba(0,0,0,0.3)',
        font=dict(color='#FFFFFF'),
    )
    fig.update_xaxes(title_text="Date", row=2, col=1, showgrid=False, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="Price", row=1, col=1, showgrid=False, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="Volume", row=2, col=1, showgrid=False, gridcolor='rgba(255,255,255,0.1)')

    st.plotly_chart(fig, use_container_width=True)

    # Display performance metrics
    st.markdown("<h3 style='text-align: center; color: #FF00FF;'>Performance Metrics</h3>", unsafe_allow_html=True)
    total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
    volatility = data['Returns'].std() * (252 ** 0.5) * 100  # Annualized volatility

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Return", f"{total_return:.2f}%", delta=f"{total_return:.2f}%", delta_color="normal")
    with col2:
        st.metric("Annualized Volatility", f"{volatility:.2f}%")

else:
    st.warning("No data available for the selected ticker and date range.")

# Add a futuristic footer
st.markdown(
    """
    <div style='position: fixed; bottom: 0; left: 0; right: 0; text-align: center; padding: 10px; background-color: rgba(0,0,0,0.5);'>
        <p style='color: #00FFFF;'>Powered by Cosmic AI • Real-time Galactic Market Analysis • &copy; 2024 Cosmic Stock Analyzer</p>
    </div>
    """,
    unsafe_allow_html=True
)