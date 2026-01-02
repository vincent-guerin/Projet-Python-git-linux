import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def plot_quant_a_performance(strategy_df, forecast_mean=None, conf_int=None, future_dates=None):
    """
    Plot Momentum vs Buy & Hold performance.
    If forecast_mean is provided, extend Buy & Hold curve with ARIMA prediction.
    """
    fig = go.Figure()

    # 1. Momentum Strategy (Green)
    fig.add_trace(go.Scatter(
        x=strategy_df.index,
        y=strategy_df['Cum_Strat'],
        name='Momentum Strategy',
        line=dict(color='green', width=2)
    ))

    # 2. Buy & Hold (Gray - Solid line)
    fig.add_trace(go.Scatter(
        x=strategy_df.index,
        y=strategy_df['Cum_BH'],
        name='Buy & Hold (Asset)',
        line=dict(color='gray', width=2)
    ))

    # 3. Add ARIMA Prediction (If enabled)
    if forecast_mean is not None and future_dates is not None:
        # --- Normalization ---
        last_cum_bh_value = strategy_df['Cum_BH'].iloc[-1]
        last_real_price = strategy_df['Close'].iloc[-1]
        scale_factor = last_cum_bh_value / last_real_price
        
        scaled_forecast = forecast_mean * scale_factor
        scaled_upper = conf_int.iloc[:, 1] * scale_factor
        scaled_lower = conf_int.iloc[:, 0] * scale_factor
        
        # Plot Prediction (Red dashed to differentiate from real)
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=scaled_forecast,
            name="ARIMA Forecast (Extrapolated)",
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Confidence Interval
        fig.add_trace(go.Scatter(
            x=future_dates, y=scaled_upper,
            mode='lines', line=dict(width=0), showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=future_dates, y=scaled_lower,
            mode='lines', line=dict(width=0),
            fill='tonexty', fillcolor='rgba(255, 0, 0, 0.1)',
            name="Confidence Interval"
        ))

    fig.update_layout(title="Performance & Forecast", xaxis_title="Date", yaxis_title="Cumulative Performance (Base 1.0)")
    st.plotly_chart(fig, width='stretch')
