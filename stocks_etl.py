import pandas as pd
import yfinance as yf
import sqlite3
import plotly.express as px
import argparse

def extract_data(ticker, start_date, end_date):
    print(f"[*] Fetching data for {ticker} from {start_date} to {end_date}...")
    df = yf.download(ticker, start=start_date, end=end_date)
    
    if df.empty:
        raise ValueError(f"No data found for {ticker}. Check the ticker symbol or dates.")
    
    # התיקון שלנו: השטחת כותרות כפולות (MultiIndex) של yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df.reset_index(inplace=True)
    
    # Save raw data to SQLite (Bonus)
    print("[*] Saving raw data to SQLite database...")
    conn = sqlite3.connect('stocks_database.db')
    df.to_sql(f'{ticker}_raw_data', conn, if_exists='replace', index=False)
    conn.close()
    
    return df

def transform_data(df):
    print("[*] Starting data transformation...")
    
    # Data Cleaning
    df_clean = df.dropna().copy()
    
    # Manipulation 1: Daily Return percentage
    df_clean['Daily_Return_%'] = df_clean['Close'].pct_change() * 100
    
    # Manipulation 2: 7-Day Moving Average
    df_clean['MA_7_Days'] = df_clean['Close'].rolling(window=7).mean()
    
    # Drop rows with NaN created by rolling mean
    df_clean = df_clean.dropna()
    
    print("[*] Data transformation complete.")
    return df_clean

def load_and_present(df, ticker):
    print("[*] Saving processed data and generating charts...")
    
    # Storage: Save to CSV
    output_filename = f"{ticker}_processed_data.csv"
    df.to_csv(output_filename, index=False)
    print(f"[*] Processed data saved to {output_filename}")
    
    # Presentation (Textual)
    max_price = float(df['Close'].max().iloc[0]) if isinstance(df['Close'].max(), pd.Series) else float(df['Close'].max())
    
    print(f"\n=== Analysis Summary for {ticker} ===")
    print(f"Highest Close Price: {max_price:.2f} USD")
    print(f"Average Daily Return: {float(df['Daily_Return_%'].mean()):.2f}%\n")
    
    # Presentation (Visual) - Saving as HTML for Docker
    fig = px.line(df, x='Date', y=['Close', 'MA_7_Days'], 
                  title=f'{ticker} Stock Price and 7-Day Moving Average',
                  labels={'value': 'Price (USD)', 'Date': 'Date'})
    
    html_filename = f"{ticker}_stock_chart.html"
    fig.write_html(html_filename)
    print(f"[*] Chart saved successfully to {html_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stocks ETL Process using Pandas")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol (e.g., AAPL, TSLA, MSFT)")
    parser.add_argument("--start", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end", type=str, required=True, help="End date in YYYY-MM-DD format")
    
    args = parser.parse_args()
    
    try:
        raw_df = extract_data(args.ticker, args.start, args.end)
        processed_df = transform_data(raw_df)
        load_and_present(processed_df, args.ticker)
        print("\n[*] ETL Pipeline completed successfully! :)")
    except Exception as e:
        print(f"\n[!] An error occurred: {e}")