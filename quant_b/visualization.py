"""
Visualization utilities for Quant B (Portfolio).

I keep plotting logic here to keep analysis_quantb.py clean.
Plotly charts look professional and are easy to embed in Streamlit.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def plot_prices(prices: pd.DataFrame, title: str = "Asset prices") -> go.Figure:
    """Multi-line chart for asset prices."""
    fig = go.Figure()
    for col in prices.columns:
        fig.add_trace(go.Scatter(x=prices.index, y=prices[col], mode="lines", name=str(col)))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Assets",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_portfolio_value(portfolio_value: pd.Series, title: str = "Portfolio value (base=1)") -> go.Figure:
    """Line chart for cumulative portfolio value."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value.values, mode="lines", name="Portfolio"))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Value",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_drawdown(drawdown: pd.Series, title: str = "Drawdown") -> go.Figure:
    """Drawdown chart (negative values)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown.values, mode="lines", name="Drawdown"))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Drawdown",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_corr_heatmap(corr: pd.DataFrame, title: str = "Correlation matrix") -> go.Figure:
    """Heatmap correlation matrix."""
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns.astype(str),
            y=corr.index.astype(str),
            zmin=-1,
            zmax=1,
            colorbar=dict(title="corr"),
        )
    )
    fig.update_layout(title=title, margin=dict(l=20, r=20, t=50, b=20))
    return fig
