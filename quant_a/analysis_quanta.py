import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from statsmodels.tsa.arima.model import ARIMA
from shared.data_manager import get_financial_data
from shared.metrics import calculate_sharpe_ratio, calculate_max_drawdown, calculate_cumulative_return, calculate_sortino_ratio
from .visualization import plot_quant_a_performance 

# 1. Momentum Strategy (Trend)
def calculate_momentum_strategy_performance(price_series, short_window=20, long_window=100):
    """
    Trend Following Strategy using SMA Crossover.
    """
    df_strat = price_series.to_frame(name='Close').copy()
    df_strat['Returns'] = df_strat['Close'].pct_change()
    df_strat['Short_SMA'] = df_strat['Close'].rolling(window=short_window).mean()
    df_strat['Long_SMA'] = df_strat['Close'].rolling(window=long_window).mean()
    
    # Signal: 1 = Buy, 0 = Cash
    df_strat['Signal'] = np.where(df_strat['Short_SMA'] > df_strat['Long_SMA'], 1.0, 0.0)
    
    df_strat['Strategy_Returns'] = df_strat['Returns'] * df_strat['Signal'].shift(1)
    df_strat.dropna(inplace=True)
    df_strat['Cumulative_Value'] = (1 + df_strat['Strategy_Returns']).cumprod()
    return df_strat['Cumulative_Value']

# 2. ADX Strategy (Trend Strength)
def calculate_adx_components(df, window=14):
    """
    Calculates Average Directional Index (ADX) and its components (+DI and -DI).
    Requires 'High', 'Low', and 'Close' columns.
    """
    
    # Attempt to adapt if only close series is passed
    if isinstance(df, pd.Series):
        df = df.to_frame(name='Close')
        df['High'] = df['Close']
        df['Low'] = df['Close']
        
    df['Returns'] = df['Close'].pct_change()
    
    # 1. True Range (TR) Calculation
    df['Prev_Close'] = df['Close'].shift(1)
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = np.abs(df['High'] - df['Prev_Close'])
    df['TR3'] = np.abs(df['Low'] - df['Prev_Close'])
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)

    # 2. Directional Movement (+DM and -DM) Calculation
    df['DM_plus'] = np.where((df['High'] > df['High'].shift(1)) & \
                             (df['High'] - df['High'].shift(1) > df['Low'].shift(1) - df['Low']),
                             df['High'] - df['High'].shift(1), 0)
    df['DM_minus'] = np.where((df['Low'].shift(1) > df['Low']) & \
                               (df['Low'].shift(1) - df['Low'] > df['High'] - df['High'].shift(1)),
                               df['Low'].shift(1) - df['Low'], 0)
    
    # 4. Filter (Wilder's Smoothing Method - Modified EMA)
    def wilder_smooth(series, period):
        return series.ewm(alpha=1/period, adjust=False).mean()

    df['TR_Smooth'] = wilder_smooth(df['TR'], window)
    df['DM_plus_Smooth'] = wilder_smooth(df['DM_plus'], window)
    df['DM_minus_Smooth'] = wilder_smooth(df['DM_minus'], window)
    
    # 5. Directional Indicator Calculation (+DI and -DI)
    df['DI_plus'] = (df['DM_plus_Smooth'] / df['TR_Smooth']) * 100
    df['DI_minus'] = (df['DM_minus_Smooth'] / df['TR_Smooth']) * 100
    
    # 6. Directional Movement Index (DX) Calculation
    df['DX'] = (np.abs(df['DI_plus'] - df['DI_minus']) / (df['DI_plus'] + df['DI_minus'])) * 100
    
    # 7. Average Directional Index (ADX) Calculation
    df['ADX'] = wilder_smooth(df['DX'], window)
    
    return df[['Close', 'Returns', 'ADX', 'DI_plus', 'DI_minus']]

def calculate_adx_strategy_performance(price_series, window=14, adx_threshold=25):
    """
    Trend Following Strategy based on DI+/DI- crossover filtered by ADX.
    Buys when DI+ > DI- AND ADX > Threshold.
    """
    df_adx = calculate_adx_components(price_series, window)
    
    # Signal Logic: 1 = Long, 0 = Cash
    
    # 1. Strong Trend Condition: ADX > Threshold (e.g., 25)
    trend_filter = df_adx['ADX'] > adx_threshold
    
    # 2. Buy Condition (Uptrend): DI+ > DI-
    buy_signal = df_adx['DI_plus'] > df_adx['DI_minus']
    
    # 3. Sell Condition (Downtrend or End of Trend): DI- > DI+
    sell_signal = df_adx['DI_minus'] > df_adx['DI_plus']
    
    # Signal: 1 if Strong Trend AND Uptrend, 0 if Downtrend.
    
    conditions = [
        buy_signal & trend_filter,
        sell_signal # Exit even if ADX is high, if DI- takes over
    ]
    choices = [1.0, 0.0] 
    
    df_adx['Signal_Trigger'] = np.select(conditions, choices, default=np.nan)
    df_adx['Signal'] = df_adx['Signal_Trigger'].ffill().fillna(0.0)
    
    df_adx['Strategy_Returns'] = df_adx['Returns'] * df_adx['Signal'].shift(1)
    df_adx.dropna(inplace=True)
    df_adx['Cumulative_Value'] = (1 + df_adx['Strategy_Returns']).cumprod()
    
    return df_adx['Cumulative_Value']

# 3. Market Analysis (Kaufman)
def calculate_kaufman_efficiency_ratio(price_series, period=30):
    """
    Kaufman Efficiency Ratio (ER).
    Measures market noise.
    """
    change = np.abs(price_series - price_series.shift(period))
    volatility = price_series.diff().abs().rolling(window=period).sum()
    er = change / volatility
    return er.iloc[-1]

# 4. Main Function
def run_quant_a():
    st.header("Module A: Analyse Univariée & Backtesting")

    # --- INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        asset = st.text_input("Asset (Ticker)", value="BTC-USD")
    
    use_custom_dates = st.checkbox("Use Custom Dates")
    
    if use_custom_dates:
        with col2:
            c_start, c_end = st.columns(2)
            start_input = c_start.date_input("Start", value=datetime.now() - timedelta(days=365))
            end_input = c_end.date_input("End", value=datetime.now())
            period = "max" 
    else:
        with col2:
            period = st.selectbox("Periodicity", ["1mo", "6mo", "1y", "2y", "5y", "10y", "max"], index=3)

    # --- DATA ---
    with st.spinner(f"Loading data for {asset}..."):
        data = get_financial_data(asset, period=period)
    
    if data.empty:
        st.error(f"❌ Ticker **'{asset}'** not found or no data available. Please check spelling.")
        return

    if isinstance(data, pd.DataFrame):
        if 'Close' in data.columns and 'High' in data.columns and 'Low' in data.columns: 
            df = data[['Close', 'High', 'Low']].copy()
        elif 'Close' in data.columns: 
            df = data[['Close']].copy()
        else: 
            df = data.iloc[:, 0].to_frame(name='Close')
            df['High'] = df['Close']
            df['Low'] = df['Close']
    elif isinstance(data, pd.Series):
        df = data.to_frame(name='Close')
        df['High'] = df['Close']
        df['Low'] = df['Close']
    else:
        st.error("❌ Data format not recognized.")
        return

    if use_custom_dates:
        df.index = pd.to_datetime(df.index)
        mask = (df.index >= pd.to_datetime(start_input)) & (df.index <= pd.to_datetime(end_input))
        df = df.loc[mask]
        if df.empty: st.error("No data."); return

    current_price = df['Close'].iloc[-1]
    st.metric(label=f"Current Price ({asset})", value=f"{current_price:.2f}")

    er = calculate_kaufman_efficiency_ratio(df['Close'], period=30)
    reco_strat = "Momentum (Trend)" if er > 0.3 else "ADX (Trend Strength)"
    reco_index = 0 if er > 0.3 else 1
    reco_color = "green" if er > 0.3 else "blue" 

    with st.expander("🧠 AI Analysis & Recommendation", expanded=True):
        st.metric("Kaufman Efficiency (ER)", f"{er:.2f}", help="Close to 1 = Trend, Close to 0 = Noise")
        st.markdown(f"💡 Market seems to be in **{reco_strat.split('(')[1][:-1]}**.")
        st.markdown(f"👉 Suggested Strategy: **:{reco_color}[{reco_strat}]**")

    st.subheader("⚙️ Strategy Configuration")
    strat_choice = st.selectbox(
        "Select Trading Model", 
        ["Momentum (Moving Avg Crossover)", "ADX (Directional Crossover)"],
        index=reco_index
    )

    cum_strat = pd.Series(dtype=float)

    if strat_choice == "Momentum (Moving Avg Crossover)":
        c1, c2 = st.columns(2)
        smooth_factor = (1 - er)
        s_short = int(5 + 45 * smooth_factor)
        s_long = int(20 + 180 * smooth_factor)
        if s_long <= s_short: s_long = s_short + 10
        
        short_window = c1.slider("Short MA", 5, 100, s_short)
        long_window = c2.slider("Long MA", short_window+1, 365, s_long)
        
        cum_strat = calculate_momentum_strategy_performance(df['Close'], short_window, long_window)
    else: 
        st.caption("Buy if DI+ > DI- AND ADX > Threshold. Sell if DI- > DI+.")
        c1, c2 = st.columns(2)
        adx_win = c1.slider("Window (Smoothing)", 5, 30, 14)
        adx_thresh = c2.slider("ADX Strength Threshold", 15, 50, 25) 
        cum_strat = calculate_adx_strategy_performance(df, adx_win, adx_thresh)

    strategy_df = df.copy()
    strategy_df['Returns_BH'] = strategy_df['Close'].pct_change()
    strategy_df['Cum_BH'] = (1 + strategy_df['Returns_BH']).cumprod()

    if cum_strat.empty:
        st.warning("Not enough signals to calculate performance.")
        strategy_df['Cum_Strat'] = 1.0
        strategy_df['Returns_Strat'] = 0.0
    else:
        strategy_df = strategy_df.loc[cum_strat.index].copy()
        strategy_df['Cum_Strat'] = cum_strat
        strategy_df['Returns_Strat'] = strategy_df['Cum_Strat'].pct_change().fillna(0)

    forecast_mean, conf_int, future_dates = None, None, None
    if st.checkbox("Show ARIMA Forecast (7d)", value=True):
        with st.spinner("Calculating ARIMA..."):
            try:
                model = ARIMA(df['Close'], order=(5,1,0)).fit()
                res = model.get_forecast(7)
                forecast_mean = res.predicted_mean
                conf_int = res.conf_int()
                future_dates = [df.index[-1] + timedelta(days=i) for i in range(1, 8)]
            except: pass

    plot_quant_a_performance(strategy_df, forecast_mean, conf_int, future_dates)

    sharpe_s = calculate_sharpe_ratio(strategy_df['Returns_Strat'])
    sortino_s = calculate_sortino_ratio(strategy_df['Returns_Strat'])
    max_dd_s = calculate_max_drawdown(strategy_df['Cum_Strat'])
    tot_s = calculate_cumulative_return(strategy_df['Cum_Strat'])
    
    bh_series = strategy_df['Cum_BH'] / strategy_df['Cum_BH'].iloc[0]
    returns_bh = bh_series.pct_change().fillna(0)
    sharpe_b = calculate_sharpe_ratio(returns_bh)
    sortino_b = calculate_sortino_ratio(returns_bh)
    max_dd_b = calculate_max_drawdown(bh_series)
    tot_b = calculate_cumulative_return(bh_series)

    st.markdown("### 🏆 Performance vs Buy & Hold")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Return", f"{tot_s:+.2%}", delta=f"{tot_s - tot_b:+.2%}")
    c2.metric("Sharpe Ratio", f"{sharpe_s:.2f}", delta=f"{sharpe_s - sharpe_b:.2f}")
    c3.metric("Sortino Ratio", f"{sortino_s:.2f}", delta=f"{sortino_s - sortino_b:.2f}")
    c4.metric("Max Drawdown", f"{max_dd_s:.2%}", delta=f"{max_dd_s - max_dd_b:.2%}")
