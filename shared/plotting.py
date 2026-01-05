import streamlit as st

def get_theme_layout(title, xaxis_title=None, yaxis_title=None):
    """Returns a theme-adapted Plotly layout."""
    theme_mode = st.session_state.get('theme_mode', 'light')
    
    layout_args = {
        "title": dict(
            text=title,
            font=dict(size=20)
        ),
        "margin": dict(l=20, r=20, t=50, b=20),
        "hovermode": "x unified"
    }
    
    if xaxis_title:
        layout_args["xaxis_title"] = xaxis_title
    if yaxis_title:
        layout_args["yaxis_title"] = yaxis_title

    if theme_mode == 'dark':
        layout_args.update({
            "template": "plotly_dark",
            "paper_bgcolor": "#131722",
            "plot_bgcolor": "#131722",
            "font": dict(color="#ffffff"),
            "title": dict(
                text=title,
                font=dict(color="#ffffff", size=20)
            ),
            "legend": dict(font=dict(color="#ffffff")),
            "xaxis": dict(
                title_font=dict(color="#ffffff"),
                tickfont=dict(color="#ffffff"),
                gridcolor="#2a2e39",
                showgrid=True,
                zerolinecolor="#2a2e39"
            ),
            "yaxis": dict(
                title_font=dict(color="#ffffff"),
                tickfont=dict(color="#ffffff"),
                gridcolor="#2a2e39", 
                showgrid=True,
                zerolinecolor="#2a2e39"
            ),
        })
    else:
        layout_args.update({
            "paper_bgcolor": "#ffffff",
            "plot_bgcolor": "#ffffff",
            "font": dict(color="#131722"),
             "xaxis": dict(
                gridcolor="#e0e3eb",
                showgrid=True
            ),
            "yaxis": dict(
                gridcolor="#e0e3eb", 
                showgrid=True
            ),
        })
        
    return layout_args

import plotly.graph_objects as go
import pandas as pd
import quant_b.visualization
import quant_b.analysis_quantb

def apply_theme(fig, title, xaxis_title=None, yaxis_title=None):
    """Applies theme to a figure."""
    layout = get_theme_layout(title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    fig.update_layout(layout)
    return fig

def _themed_plot_prices(prices, title="Asset prices"):
    fig = quant_b.visualization.plot_prices(prices, title)
    return apply_theme(fig, title, xaxis_title="Date", yaxis_title="Price")

def _themed_plot_portfolio_value(port_val, title="Portfolio value (base=1)"):
    fig = quant_b.visualization.plot_portfolio_value(port_val, title)
    return apply_theme(fig, title, xaxis_title="Date", yaxis_title="Value")

def _themed_plot_drawdown(dd, title="Portfolio drawdown"):
    fig = quant_b.visualization.plot_drawdown(dd, title)
    return apply_theme(fig, title, xaxis_title="Date", yaxis_title="Drawdown")

def _themed_plot_corr_heatmap(corr, title="Correlation matrix"):
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns.astype(str),
            y=corr.index.astype(str),
            zmin=-1,
            zmax=1,
            colorscale="RdBu",
            colorbar=dict(title="Correlation"),
        )
    )
    return apply_theme(fig, title)

def apply_quant_b_overrides():
    """Applies overrides to Quant B."""
    quant_b.analysis_quantb.plot_prices = _themed_plot_prices
    quant_b.analysis_quantb.plot_portfolio_value = _themed_plot_portfolio_value
    quant_b.analysis_quantb.plot_drawdown = _themed_plot_drawdown
    quant_b.analysis_quantb.plot_corr_heatmap = _themed_plot_corr_heatmap
