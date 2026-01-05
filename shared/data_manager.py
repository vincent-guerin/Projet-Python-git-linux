import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=60)
def get_financial_data(tickers, period="1y", interval="1d", start=None, end=None):
    """Retrieves adjusted close prices."""
    if isinstance(tickers, list):
        tickers = " ".join(tickers)

    try:
        if start and end:
             df = yf.download(tickers, start=start, end=end, interval=interval, auto_adjust=True)
        else:
             df = yf.download(tickers, period=period, interval=interval, auto_adjust=True)
        
        if 'Close' in df.columns:
            if isinstance(df.columns, pd.MultiIndex):
                return df['Close']
            else:
                return df
        else:
            return df

    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame()

def get_asset_info(ticker):
    """Retrieves asset info safely."""
    try:
        tick = yf.Ticker(ticker)
        return tick.info
    except:
        return {}