import streamlit as st
import yfinance as yf
import pandas as pd

# Title of the app
st.title('Stock Information and Financials App')

# User input for the stock ticker
ticker_symbol = st.text_input("Enter the stock ticker:", "AAPL")

# Fetching the stock information
stock_info = yf.Ticker(ticker_symbol)

# Displaying the company name and other basic information
st.write(f"**Company Name:** {stock_info.info['longName']}")
st.write("**Sector:**", stock_info.info['sector'])
st.write("**Full Time Employees:**", stock_info.info['fullTimeEmployees'])
st.write("**Business Summary:**", stock_info.info['longBusinessSummary'])

# Displaying stock statistics
st.subheader("Stock Statistics")
st.write(stock_info.stats())

# Displaying financials
st.subheader("Financials")
financials = stock_info.financials
st.dataframe(financials)

# Displaying balance sheet
st.subheader("Balance Sheet")
balance_sheet = stock_info.balance_sheet
st.dataframe(balance_sheet)
