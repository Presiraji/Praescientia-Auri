import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests
from lxml import html

def get_stock_data(tickers, past_days):
    data = {}
    end_date = pd.to_datetime("today")
    start_date = end_date - pd.Timedelta(days=past_days)
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        data[ticker] = hist
    return data

def fetch_apy(ticker):
    try:
        url_etf = f"https://stockanalysis.com/etf/{ticker}/dividend/"
        url_stock = f"https://stockanalysis.com/stocks/{ticker}/dividend/"
        
        response_etf = requests.get(url_etf)
        tree_etf = html.fromstring(response_etf.content)
        apy_etf = tree_etf.xpath('/html/body/div/div[1]/div[2]/main/div[2]/div/div[2]/div[2]/div/text()')
        
        if apy_etf:
            return float(apy_etf[0].strip('%'))
        
        response_stock = requests.get(url_stock)
        tree_stock = html.fromstring(response_stock.content)
        apy_stock = tree_stock.xpath('/html/body/div/div[1]/div[2]/main/div[2]/div/div[2]/div[2]/div/text()')
        
        if apy_stock:
            return float(apy_stock[0].strip('%'))
        
        return 0.0
    except Exception as e:
        st.error(f"Error fetching APY for {ticker}: {e}")
        return 0.0

def plot_stock_data(data):
    fig, axes = plt.subplots(4, 2, figsize=(15, 10))
    axes = axes.flatten()

    for i, (ticker, hist) in enumerate(data.items()):
        if i >= 8:
            break
        ax = axes[i]
        hist['Close'].plot(ax=ax)
        apy = fetch_apy(ticker)
        ax.set_title(f"{ticker} - APY: {apy:.2f}%")
        ax.set_ylabel('Price')
        ax.set_xlabel('Date')

    for j in range(i+1, 8):
        fig.delaxes(axes[j])

    plt.tight_layout()
    st.pyplot(fig)

st.title("Multi-Function Charts with Dividend Yield (APY)")

tickers_input = st.text_area("Tickers Entry Box (separated by commas)", "AAPL, MSFT, GOOG")
past_days = st.number_input("Past days from today", min_value=1, value=90)

tickers = [ticker.strip() for ticker in tickers_input.split(",")]

if st.button("Generate Charts"):
    data = get_stock_data(tickers, past_days)
    plot_stock_data(data)
