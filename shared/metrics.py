import numpy as np
import pandas as pd

def calculate_cumulative_return(series):
    """Calculates final cumulative return (e.g., +150%)"""
    if series.empty: return 0.0
    return (series.iloc[-1] / series.iloc[0]) - 1

def calculate_annualized_volatility(daily_returns):
    """Calculates annualized volatility (252 trading days)"""
    return daily_returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(daily_returns, risk_free_rate=0.0):
    """Calculates Sharpe Ratio"""
    mean_return = daily_returns.mean()
    std_return = daily_returns.std()
    
    if std_return == 0:
        return 0.0
    
    # Simple annualization
    sharpe = (mean_return - risk_free_rate) / std_return
    return sharpe * np.sqrt(252)

def calculate_max_drawdown(price_series):
    """Calculates historical Maximum Drawdown"""
    rolling_max = price_series.cummax()
    drawdown = (price_series / rolling_max) - 1.0
    return drawdown.min()

def calculate_sortino_ratio(daily_returns, risk_free_rate=0.0, target_return=0.0):
    """
    Calculates Sortino Ratio.
    Unlike Sharpe, it only penalizes downside volatility (Downside Risk).
    """
    # 1. Keep only negative returns (losses)
    downside_returns = daily_returns[daily_returns < target_return]
    
    # 2. Calculate standard deviation of these losses (Downside Deviation)
    downside_std = downside_returns.std()
    
    mean_return = daily_returns.mean()
    
    # Division by zero safety
    if downside_std == 0 or pd.isna(downside_std):
        return 0.0
        
    # 3. Calculation and Annualization
    sortino = (mean_return - risk_free_rate) / downside_std
    return sortino * np.sqrt(252)

def calculate_hurst_exponent(price_series, max_lag=20):
    """
    Calculates the Hurst Exponent of a time series to determine its nature.
    H < 0.5: Mean Reverting
    H = 0.5: Random Walk
    H > 0.5: Trending
    """
    try:
        lags = range(2, max_lag)
        tau = [np.sqrt(np.std(np.subtract(price_series[lag:], price_series[:-lag]))) for lag in lags]
        
        # Calculate the slope of the log-log plot
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0] * 2.0 
    except:
        return 0.5 # Return neutral if calculation fails