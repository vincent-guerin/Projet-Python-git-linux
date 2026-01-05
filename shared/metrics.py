import numpy as np
import pandas as pd

def calculate_cumulative_return(series):
    """Calculates final cumulative return."""
    if series.empty: return 0.0
    return (series.iloc[-1] / series.iloc[0]) - 1

def calculate_annualized_volatility(daily_returns):
    """Calculates annualized volatility."""
    return daily_returns.std() * np.sqrt(252)

def calculate_sharpe_ratio(daily_returns, risk_free_rate=0.0):
    """Calculates Sharpe Ratio."""
    mean_return = daily_returns.mean()
    std_return = daily_returns.std()
    
    if std_return == 0:
        return 0.0
    
    sharpe = (mean_return - risk_free_rate) / std_return
    return sharpe * np.sqrt(252)

def calculate_max_drawdown(price_series):
    """Calculates historical Max Drawdown."""
    rolling_max = price_series.cummax()
    drawdown = (price_series / rolling_max) - 1.0
    return drawdown.min()

def calculate_sortino_ratio(daily_returns, risk_free_rate=0.0, target_return=0.0):
    """Calculates Sortino Ratio."""
    downside_returns = daily_returns[daily_returns < target_return]
    downside_std = downside_returns.std()
    
    mean_return = daily_returns.mean()
    
    if downside_std == 0 or pd.isna(downside_std):
        return 0.0
        
    sortino = (mean_return - risk_free_rate) / downside_std
    return sortino * np.sqrt(252)

def calculate_hurst_exponent(price_series, max_lag=20):
    """Calculates Hurst Exponent."""
    try:
        lags = range(2, max_lag)
        tau = [np.sqrt(np.std(np.subtract(price_series[lag:], price_series[:-lag]))) for lag in lags]
        
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0] * 2.0 
    except:
        return 0.5