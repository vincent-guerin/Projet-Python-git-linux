# Quantitative Finance Dashboard

This project is a high-performance web application designed for quantitative asset management. Built with **Python** and **Streamlit**, it provides a robust platform for real-time financial monitoring, strategy backtesting, and portfolio simulation. The system is designed to run 24/7 on a Linux architecture, ensuring continuous data availability.

## Project Objectives

The primary goal is to support fundamental and quantitative portfolio managers with advanced tools:
- **Real-Time Data**: Live fetching of market data for equities, forex, and cryptocurrencies.
- **Univariate Analysis (Quant A)**: Deep dive into single-asset performance, applying trend-following strategies and forecasting models.
- **Portfolio Optimization (Quant B)**: Construction of efficient portfolios using Markowitz theory and risk management metrics (Integration pending).
- **Automation**: Fully automated workflows including data refreshing and daily reporting via Cron jobs.

## Technology Stack

- **Core Framework**: Python 3.10+, Streamlit
- **Data Manipulation**: Pandas, NumPy
- **Visualization**: Plotly Interactive Charts
- **Financial Data**: Yahoo Finance API (`yfinance`)
- **Analysis**: Statsmodels (ARIMA), Scipy
- **Deployment**: Linux (Ubuntu), Systemd, Crontab

## Key Features

### 1. Interactive Dashboard
- **Dark/Light Mode**: The UI automatically adapts, featuring a custom-built dark mode for low-light environments (inspired by professional trading terminals).
- **Responsive Design**: optimized for various screen sizes using Streamlit's wide layout.

### 2. Module A: Single Asset Analysis
Focuses on individual instrument performance.
- **Momentum Strategy**: Implements a dual Moving Average Crossover system (Short/Long MA).
- **ADX Trend Strategy**: Uses the Average Directional Index to filter strong trends and Directional Indicators (DI+/DI-) for entry signals.
- **Forecasting**: An integrated ARIMA (AutoRegressive Integrated Moving Average) model provides 7-day price forecasts with confidence intervals.
- **Performance Metrics**: Automatically calculates Sharpe Ratio, Sortino Ratio, Max Drawdown, and Cumulative Returns compared to a Buy & Hold benchmark.

### 3. Automated Reporting
- **PDF Reports**: A dedicated script generates daily summaries of market activity.
- **Scheduling**: Configured via Linux `cron` to run every evening at 11:00 PM, ensuring managers have the latest data before the next trading day.

## Project Structure

The project follows a modular architecture to ensure scalability and maintain separation of concerns:

```bash
.
├── main.py                # Application entry point & Navigation
├── quant_a/               # [Module A] Single Asset Logic
│   ├── analysis_quanta.py # Strategy logic (Momentum, ADX, ARIMA)
│   └── visualization.py   # Plotly charting functions for Module A
├── quant_b/               # [Module B] Portfolio Logic
│   ├── analysis_quantb.py # Markowitz optimization & metrics
│   └── visualization.py   # Plotly charting for portfolios
├── shared/                # Shared Utilities & UI Components
│   ├── data_manager.py    # Centralized data fetching & caching
│   ├── metrics.py         # Financial calculations (Sharpe, Volatility)
│   ├── plotting.py        # Theme-aware plotting overrides
│   └── ui.py              # CSS styling and theme management
├── README.md              # Project documentation
└── requirements.txt       # Project dependencies
```
