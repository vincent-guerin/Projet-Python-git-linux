import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from shared.plotting import get_theme_layout

def plot_quant_a_performance(strategy_df, forecast_mean=None, conf_int=None, future_dates=None):
    """Plot Momentum vs Buy & Hold performance."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=strategy_df.index,
        y=strategy_df['Cum_Strat'],
        name='Momentum Strategy',
        line=dict(color='green', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=strategy_df.index,
        y=strategy_df['Cum_BH'],
        name='Buy & Hold (Asset)',
        line=dict(color='gray', width=2)
    ))

    if forecast_mean is not None and future_dates is not None:
        last_cum_bh_value = strategy_df['Cum_BH'].iloc[-1]
        last_real_price = strategy_df['Close'].iloc[-1]
        scale_factor = last_cum_bh_value / last_real_price
        
        scaled_forecast = forecast_mean * scale_factor
        scaled_upper = conf_int.iloc[:, 1] * scale_factor
        scaled_lower = conf_int.iloc[:, 0] * scale_factor
        
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=scaled_forecast,
            name="ARIMA Forecast (Extrapolated)",
            line=dict(color='red', width=2, dash='dash')
        ))
        
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

    theme_layout = get_theme_layout(
        title="Performance & Forecast", 
        xaxis_title="Date", 
        yaxis_title="Cumulative Performance (Base 1.0)"
    )
    fig.update_layout(theme_layout)
    
    st.plotly_chart(fig, width='stretch')
