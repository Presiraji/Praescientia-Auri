import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from lxml import html
import math

# Set Streamlit to always run in wide mode
st.set_page_config(layout="wide")

@st.cache_data
def get_stock_data(tickers, past_days):
    data = {}
    end_date = pd.to_datetime("today")
    start_date = end_date - pd.Timedelta(days=past_days)
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                data[ticker] = hist
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")
    return data

@st.cache_data
def get_dividend_info(ticker):
    urls = [
        f"https://stockanalysis.com/etf/{ticker}/dividend/",
        f"https://stockanalysis.com/stocks/{ticker}/dividend/"
    ]
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            dividend_xpath = '//div[contains(text(),"Annual Dividend")]/following-sibling::div'
            apy_xpath = '//div[contains(text(),"APY")]/following-sibling::div'
            dividend = tree.xpath(dividend_xpath)
            apy = tree.xpath(apy_xpath)
            if dividend and apy:
                return dividend[0].text_content(), apy[0].text_content()
    return "N/A", "N/A"

def plot_stock_data(data, show_volume, moving_avg_window):
    num_tickers = len(data)
    num_cols = 2
    num_rows = math.ceil(num_tickers / num_cols)
    
    fig = make_subplots(rows=num_rows, cols=num_cols, subplot_titles=[
        f"{ticker} - Annual Dividend: {get_dividend_info(ticker)[0]}, APY: {get_dividend_info(ticker)[1]}" 
        for ticker in data.keys()
    ])

    row = 1
    col = 1

    for ticker, hist in data.items():
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name=f"{ticker} Close"), row=row, col=col)
        
        if show_volume:
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name=f"{ticker} Volume", yaxis='y2'), row=row, col=col)
            fig.update_layout({f'yaxis{row}{col}': dict(title='Volume', overlaying='y', side='right')})
        
        if moving_avg_window > 1:
            hist[f'MA{moving_avg_window}'] = hist['Close'].rolling(window=moving_avg_window).mean()
            fig.add_trace(go.Scatter(x=hist.index, y=hist[f'MA{moving_avg_window}'], mode='lines', name=f"{ticker} MA{moving_avg_window}"), row=row, col=col)
        
        if col == num_cols:
            row += 1
            col = 1
        else:
            col += 1

    fig.update_layout(height=300*num_rows, width=1200, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.title("Advanced Stock Charts with Dividend Yield (Annual Dividend and APY)")

tickers_input = st.text_area("Tickers Entry Box (separated by commas)", "BXMT, MFA, SCM, PUTW, PFRL, CLOZ, TYLG, PULS, MFC, IAUF, SPYI, ZIVB")
past_days = st.number_input("Past days from today", min_value=1, value=90)
show_volume = st.checkbox("Show Volume", value=True)
moving_avg_window = st.slider("Moving Average Window", min_value=1, max_value=50, value=20)

tickers = [ticker.strip() for ticker in tickers_input.split(",")]

if st.button("Generate Charts"):
    data = get_stock_data(tickers, past_days)
    if data:
        plot_stock_data(data, show_volume, moving_avg_window)
    else:
        st.error("No data available for the given tickers and date range.")
