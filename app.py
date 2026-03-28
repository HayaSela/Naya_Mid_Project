import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import datetime

# --- ETL Functions ---
def extract_data(ticker_symbol, start_date, end_date):
    ticker_obj = yf.Ticker(ticker_symbol)
    df = ticker_obj.history(start=start_date, end=end_date)
    
    if df.empty:
        st.error(f"No data found for {ticker_symbol}.")
        return None, None
    
    # ????? ?????? ?? ?????? (????? ?-MultiIndex ?? yfinance)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df.reset_index(inplace=True)
    return df, ticker_obj

def transform_data(df):
    df_clean = df.copy()
    # ??????? ?-Pandas
    df_clean['Daily_Return'] = df_clean['Close'].pct_change()
    df_clean['Cumulative_Return'] = (1 + df_clean['Daily_Return']).cumprod() - 1
    df_clean['MA_20'] = df_clean['Close'].rolling(window=20).mean()
    return df_clean.dropna()

# --- UI Setup ---
st.set_page_config(page_title="Professional Stock Analytics", layout="wide")

# ????? ?????? :chart_with_upwards_trend: ?????? ????? ????
st.title(":chart_with_upwards_trend: Advanced Stock ETL & Business Insights")

# Sidebar
st.sidebar.header("User Input")
ticker_input = st.sidebar.text_input("Stock Symbol", "TSLA").upper()
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date.today())

if st.sidebar.button("Run Analysis"):
    with st.spinner('Analyzing market data...'):
        raw_df, ticker_obj = extract_data(ticker_input, start_date, end_date)
        
        if raw_df is not None:
            df = transform_data(raw_df)
            
            # --- Business Metrics ---
            col1, col2, col3 = st.columns(3)
            current_price = df['Close'].iloc[-1]
            total_ret = df['Cumulative_Return'].iloc[-1] * 100
            
            col1.metric("Current Price", f"${current_price:.2f}")
            col2.metric("Period Return", f"{total_ret:.2f}%")
            col3.metric("Volatility (Std)", f"{df['Daily_Return'].std():.4f}")

            # --- Candlestick Chart ---
            # ????? ?????? :candle:
            st.subheader(f":candle: {ticker_input} Candlestick Chart")
            fig_candle = go.Figure(data=[go.Candlestick(x=df['Date'],
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'], name='Market Data')])
            fig_candle.update_layout(xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig_candle, use_container_width=True)

            # --- Cumulative Return Chart ---
            # ????? ?????? :rocket:
            st.subheader(":rocket: Investment Growth (Cumulative Return)")
            fig_cum = px.area(df, x='Date', y='Cumulative_Return', title="Growth of $1 Investment")
            st.plotly_chart(fig_cum, use_container_width=True)

            # --- Analyst Recommendations ---
            # ????? ?????? :bank:
            st.subheader(":bank: Analyst Sentiments")
            recs = ticker_obj.recommendations
            if recs is not None and not recs.empty:
                st.dataframe(recs.tail(5))
            else:
                st.write("No recent analyst recommendations found for this ticker.")

            # --- Raw Data ---
            with st.expander("View Processed Data Table"):
                st.write(df)