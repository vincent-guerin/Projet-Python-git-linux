"""
Daily Report (cron-ready)

Requirements covered:
- open/close prices
- volatility
- max drawdown
- stored locally (reports/)
- can be scheduled via cron at fixed time

Output:
- reports/daily_report_YYYY-MM-DD.txt
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd

TRADING_DAYS = 252

# Choose 3 assets (portfolio-ish) to match Quant B spirit
TICKERS: List[str] = ["AAPL", "MSFT", "GOOGL"]
PERIOD = "6mo"
INTERVAL = "1d"


def _load_prices(tickers: List[str], period: str, interval: str) -> pd.DataFrame:
    """
    Loads adjusted close prices.
    Tries yfinance (common in these projects).
    """
    try:
        import yfinance as yf  # type: ignore
    except Exception as e:
        raise RuntimeError("yfinance is required on the VM: pip install yfinance") from e

    data = yf.download(
        tickers=tickers,
        period=period,
        interval=interval,
        auto_adjust=True,
        group_by="ticker",
        progress=False,
        threads=True,
    )

    if isinstance(data.columns, pd.MultiIndex):
        close = pd.DataFrame({t: data[t]["Close"] for t in tickers if t in data.columns.levels[0]})
        open_ = pd.DataFrame({t: data[t]["Open"] for t in tickers if t in data.columns.levels[0]})
    else:
        # single ticker case
        t = tickers[0]
        close = pd.DataFrame({t: data["Close"]})
        open_ = pd.DataFrame({t: data["Open"]})

    close = close.dropna(how="all").ffill().dropna()
    open_ = open_.reindex(close.index).dropna(how="all").ffill().dropna()
    close.index = pd.to_datetime(close.index)
    open_.index = pd.to_datetime(open_.index)

    return open_, close


def annualized_vol(returns: pd.Series) -> float:
    return float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS)) if not returns.empty else float("nan")


def max_drawdown(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    cum = (1.0 + returns).cumprod()
    peak = cum.cummax()
    dd = (cum / peak) - 1.0
    return float(dd.min())


def generate_report() -> str:
    os.makedirs("reports", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = os.path.join("reports", f"daily_report_{today}.txt")

    open_, close = _load_prices(TICKERS, PERIOD, INTERVAL)

    # daily returns from close
    returns = close.pct_change().dropna()

    lines = []
    lines.append("=" * 70)
    lines.append("DAILY FINANCIAL REPORT")
    lines.append("=" * 70)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Tickers: {', '.join(list(close.columns))}")
    lines.append(f"Data window: {close.index.min().date()} -> {close.index.max().date()}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("OPEN / CLOSE (latest trading day)")
    lines.append("-" * 70)

    last_date = close.index.max()
    lines.append(f"Last date: {last_date.date()}\n")
    for t in close.columns:
        o = float(open_.loc[last_date, t]) if t in open_.columns else float("nan")
        c = float(close.loc[last_date, t])
        lines.append(f"{t:6s} | Open: {o:10.4f} | Close: {c:10.4f}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("RISK METRICS (based on daily returns)")
    lines.append("-" * 70)
    for t in close.columns:
        r = returns[t].dropna()
        vol = annualized_vol(r)
        mdd = max_drawdown(r)
        lines.append(f"{t:6s} | Vol (ann.): {vol:8.2%} | Max Drawdown: {mdd:8.2%}")
    lines.append("")

    # BONUS: equal-weight portfolio metrics
    lines.append("-" * 70)
    lines.append("BONUS: EQUAL-WEIGHT PORTFOLIO")
    lines.append("-" * 70)
    w = np.ones(returns.shape[1]) / returns.shape[1]
    port_ret = (returns * w).sum(axis=1)
    port_vol = annualized_vol(port_ret)
    port_mdd = max_drawdown(port_ret)
    lines.append(f"Portfolio | Vol (ann.): {port_vol:8.2%} | Max Drawdown: {port_mdd:8.2%}")
    lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path


if __name__ == "__main__":
    path = generate_report()
    print(f"Report written to: {path}")
