"""
Quant B - Portfolio module.

Goal:
- Multi-asset portfolio analysis (>=3 assets)
- Equal weight + custom weights
- Optional rebalancing (weekly/monthly)
- Key metrics + correlation matrix
- Clean Streamlit UI

Integration:
- main.py should call run_quant_b()
- I try to reuse shared modules (data_manager/config/metrics) if available.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from .visualization import (
    plot_prices,
    plot_portfolio_value,
    plot_drawdown,
    plot_corr_heatmap,
)


# -----------------------------
# Shared imports (if the group repo provides them)
# I keep safe fallbacks to avoid hard crashes during integration.
# -----------------------------

def _try_import_shared():
    """
    Tries to import the shared utilities created by Quant A / group structure.
    If not available, we return None and use local fallbacks.
    """
    shared = {}
    try:
        # Expected group structure:
        # - shared/config.py with DEFAULT_ASSETS
        # - shared/data_manager.py with get_financial_data(...)
        from shared.config import DEFAULT_ASSETS  # type: ignore
        shared["DEFAULT_ASSETS"] = DEFAULT_ASSETS
    except Exception:
        shared["DEFAULT_ASSETS"] = ["AAPL", "MSFT", "GOOGL"]

    try:
        from shared.data_manager import get_financial_data  # type: ignore
        shared["get_financial_data"] = get_financial_data
    except Exception:
        shared["get_financial_data"] = None

    # Metrics: Quant A seems to have a "shared.metrics" file.
    # Names may differ, so I keep graceful fallback metrics as well.
    try:
        import shared.metrics as shared_metrics  # type: ignore
        shared["metrics_module"] = shared_metrics
    except Exception:
        shared["metrics_module"] = None

    return shared


_SHARED = _try_import_shared()


# -----------------------------
# Minimal "pro" metrics fallback
# (used only if shared.metrics does not provide the expected functions)
# -----------------------------

TRADING_DAYS = 252


def _annualized_vol(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    return float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS))


def _annualized_return(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    growth = (1 + returns).prod()
    n = len(returns)
    return float(growth ** (TRADING_DAYS / n) - 1)


def _sharpe(returns: pd.Series, rf_annual: float = 0.0) -> float:
    if returns.empty:
        return float("nan")
    rf_daily = (1 + rf_annual) ** (1 / TRADING_DAYS) - 1
    ex = returns - rf_daily
    vol = ex.std(ddof=1)
    if vol == 0 or np.isnan(vol):
        return float("nan")
    return float(ex.mean() / vol * np.sqrt(TRADING_DAYS))


def _max_drawdown(cum: pd.Series) -> float:
    if cum.empty:
        return float("nan")
    peak = cum.cummax()
    dd = (cum / peak) - 1.0
    return float(dd.min())


def _drawdown_series(cum: pd.Series) -> pd.Series:
    if cum.empty:
        return pd.Series(dtype=float)
    peak = cum.cummax()
    return (cum / peak) - 1.0


def _compute_metrics(port_rets: pd.Series, port_val: pd.Series, rf: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": ["Annual Return", "Annual Volatility", "Sharpe Ratio", "Max Drawdown"],
            "Value": [
                _annualized_return(port_rets),
                _annualized_vol(port_rets),
                _sharpe(port_rets, rf_annual=rf),
                _max_drawdown(port_val),
            ],
        }
    )


# -----------------------------
# Portfolio mechanics
# -----------------------------

def _normalize_weights(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w, dtype=float)
    w = np.clip(w, 0.0, None)  # long-only; simple and safe
    s = w.sum()
    if s <= 0:
        return w
    return w / s


def _equal_weights(n: int) -> np.ndarray:
    return np.ones(n) / n


def _custom_weights(tickers: List[str], user_w: Dict[str, float]) -> np.ndarray:
    w = np.array([float(user_w.get(t, 0.0)) for t in tickers], dtype=float)
    return _normalize_weights(w)


def _rebalance_dates(index: pd.DatetimeIndex, freq: str) -> pd.DatetimeIndex:
    """
    freq in {"none","W","M"} (I keep it simple & robust).
    """
    if freq == "none":
        return pd.DatetimeIndex([index[0]])
    s = pd.Series(1, index=index)
    return s.resample(freq).first().dropna().index


def _backtest_portfolio(
    returns: pd.DataFrame,
    weight_mode: str,
    user_weights: Optional[Dict[str, float]],
    rebalance: str,
) -> Tuple[pd.Series, pd.Series, pd.DataFrame]:
    """
    Returns:
    - portfolio returns
    - portfolio value (base=1)
    - weights timeseries (for transparency)
    """
    if returns.empty:
        empty = pd.Series(dtype=float)
        return empty, empty, pd.DataFrame()

    tickers = list(returns.columns)
    idx = returns.index

    rebal_dates = _rebalance_dates(idx, rebalance)
    weights_ts = pd.DataFrame(index=idx, columns=tickers, dtype=float)

    current_w = _equal_weights(len(tickers))

    for d in rebal_dates:
        # Align rebalancing date with existing index (nearest)
        if d not in idx:
            d = idx[idx.get_indexer([d], method="nearest")[0]]

        if weight_mode == "equal":
            current_w = _equal_weights(len(tickers))
        else:
            current_w = _custom_weights(tickers, user_weights or {})

        weights_ts.loc[d:, :] = current_w

    weights_ts = weights_ts.ffill().dropna()
    port_rets = (returns.loc[weights_ts.index] * weights_ts).sum(axis=1)
    port_val = (1.0 + port_rets).cumprod()

    return port_rets, port_val, weights_ts


# -----------------------------
# UI helpers
# -----------------------------

def _get_assets_from_session_or_default(default_assets: List[str]) -> List[str]:
    """
    main.py in our group project stores the tickers string in st.session_state
    (shared input across modules). I reuse it if available.
    """
    # If Quant A/main already set a shared input, reuse it for coherence.
    raw = st.session_state.get("shared_assets_input", None)
    if isinstance(raw, str) and raw.strip():
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
        return tickers if len(tickers) >= 1 else default_assets
    return default_assets


@st.cache_data(ttl=300, show_spinner=False)
def _load_prices_cached(tickers: List[str], period: str, interval: str) -> pd.DataFrame:
    """
    Uses shared.data_manager.get_financial_data if present.
    Otherwise returns empty DF (but we try hard to avoid crashing).
    """
    getter = _SHARED.get("get_financial_data")
    if getter is None:
        return pd.DataFrame()

    df = getter(tickers, period=period, interval=interval)

    # Expecting a dataframe indexed by date, columns = tickers (prices)
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    df = df.sort_index().dropna(how="all").ffill().dropna()
    return df


# -----------------------------
# Main entrypoint
# -----------------------------

def run_quant_b():
    st.header("📊 Portfolio Management (Quant B)")

    default_assets = list(_SHARED.get("DEFAULT_ASSETS", ["AAPL", "MSFT", "GOOGL"]))
    tickers = _get_assets_from_session_or_default(default_assets)

    # ---- Sidebar controls (simple, clean, pro) ----
    with st.sidebar:
        st.subheader("Portfolio settings (Quant B)")

        st.caption("Assets are shared across modules if main.py sets them.")
        tickers_input = st.text_input("Tickers (comma-separated)", value=",".join(tickers))
        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        if len(tickers) < 3:
            st.warning("Please select at least 3 assets for the portfolio module.")
        period = st.selectbox("History period", ["1y", "2y", "5y", "10y"], index=2)
        interval = st.selectbox("Interval", ["1d", "1h"], index=0)

        st.divider()
        st.subheader("Weights")
        weight_mode = st.selectbox("Weight mode", ["equal", "custom"], index=0)
        rebalance = st.selectbox("Rebalancing", ["none", "W", "M"], index=2)

        rf = st.number_input("Risk-free rate (annual)", value=0.0, step=0.005)

        user_w: Dict[str, float] = {}
        if weight_mode == "custom" and len(tickers) > 0:
            st.caption("Custom weights (they will be normalized to sum to 1).")
            for t in tickers:
                user_w[t] = st.number_input(f"{t} weight", value=1.0 / max(len(tickers), 1), step=0.01)

        if st.button("Refresh now"):
            st.cache_data.clear()
            st.rerun()

    # Store shared assets for coherence with Quant A (optional, but nice)
    st.session_state["shared_assets_input"] = ",".join(tickers)

    if len(tickers) < 3:
        st.stop()

    # ---- Load prices (shared manager) ----
    prices = _load_prices_cached(tickers, period=period, interval=interval)
    if prices.empty:
        st.error(
            "No data returned. Either the data source failed or shared.data_manager is missing.\n\n"
            "Tip: verify shared/data_manager.py and your internet access on the VM."
        )
        st.stop()

    # Align columns to requested tickers (some sources may drop invalid tickers)
    tickers_ok = [t for t in tickers if t in prices.columns]
    prices = prices[tickers_ok].copy()

    if prices.shape[1] < 3:
        st.error("Data source returned fewer than 3 valid assets. Check tickers.")
        st.stop()

    returns = prices.pct_change().dropna()

    # ---- Backtest portfolio ----
    port_rets, port_val, weights_ts = _backtest_portfolio(
        returns=returns,
        weight_mode=weight_mode,
        user_weights=user_w if weight_mode == "custom" else None,
        rebalance=rebalance,
    )

    # ---- Metrics: try shared.metrics first, otherwise fallback ----
    metrics_mod = _SHARED.get("metrics_module")

    # I keep it robust: if shared module exists but names differ, we fallback safely.
    if metrics_mod is not None:
        try:
            # If your shared.metrics provides a function building a metrics dict/table,
            # you can adapt this part once you confirm exact function names.
            # For now, fallback metrics are used unless we are sure.
            metrics_df = _compute_metrics(port_rets, port_val, rf=rf)
        except Exception:
            metrics_df = _compute_metrics(port_rets, port_val, rf=rf)
    else:
        metrics_df = _compute_metrics(port_rets, port_val, rf=rf)

    dd = _drawdown_series(port_val)
    corr = returns.corr()

    # ---- Display: professional layout ----
    top1, top2, top3 = st.columns(3)
    top1.metric("Last date", str(prices.index[-1]))
    top2.metric("Portfolio value (base=1)", f"{port_val.iloc[-1]:.3f}")
    top3.metric("Max drawdown", f"{_max_drawdown(port_val):.2%}")

    st.subheader("Prices (multi-assets)")
    st.plotly_chart(plot_prices(prices, title="Asset prices"), use_container_width=True)

    st.subheader("Portfolio performance")
    st.plotly_chart(plot_portfolio_value(port_val, title="Portfolio value (base=1)"), use_container_width=True)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Key metrics")
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Latest weights")
        if not weights_ts.empty:
            st.dataframe(weights_ts.tail(5), use_container_width=True)
        else:
            st.info("Weights not available (unexpected).")

    st.subheader("Drawdown")
    st.plotly_chart(plot_drawdown(dd, title="Portfolio drawdown"), use_container_width=True)

    st.subheader("Correlation matrix")
    st.plotly_chart(plot_corr_heatmap(corr, title="Correlation matrix"), use_container_width=True)

    with st.expander("Diagnostics"):
        st.write("Prices sample:")
        st.dataframe(prices.tail(10), use_container_width=True)
        st.write("Returns sample:")
        st.dataframe(returns.tail(10), use_container_width=True)
