import yfinance as yf
import pandas as pd
import streamlit as st

# Cache data for 5 minutes (300 seconds)
# If user refreshes before 5 min, do not recall Yahoo.
@st.cache_data(ttl=300)
def get_financial_data(tickers, period="1y", interval="1d"):
    """
    Retrieves adjusted close prices for one or more assets.
    Returns a clean DataFrame.
    """
    if isinstance(tickers, list):
        tickers = " ".join(tickers)

    try:
        # Bulk download
        df = yf.download(tickers, period=period, interval=interval, auto_adjust=True)
        
        # Handle return format based on number of assets
        if 'Close' in df.columns:
            # Multi-index or simple case
            if isinstance(df.columns, pd.MultiIndex):
                return df['Close']
            else:
                return df['Close']
        else:
            return df

    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame()

def get_asset_info(ticker):
    """Retrieves info (sector, etc.) without crashing the app."""
    try:
        tick = yf.Ticker(ticker)
        return tick.info
    except:
        return {}