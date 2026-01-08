# Quantitative Finance Dashboard

This project is a **Streamlit-based quantitative finance dashboard**
developed in Python.

It provides two main modules:
- **Quant A**: single asset analysis
- **Quant B**: portfolio management

The project also includes an **automated daily financial report**
generated via a Linux cron job.

---

## Project Objectives

The objectives of this project are to:
- Analyse financial market data using quantitative methods
- Perform **single-asset analysis** (Quant A)
- Perform **multi-asset portfolio analysis** (Quant B)
- Visualise financial data through an interactive dashboard
- Automate daily reporting using a cron job

---

## Technology Stack

- **Language**: Python 3
- **Framework**: Streamlit
- **Data processing**: Pandas, NumPy
- **Visualisation**: Plotly
- **Financial data**: Yahoo Finance (yfinance)
- **Automation**: Linux cron

---

## Dashboard Overview

The dashboard is accessible at:

http://34.56.136.238:8501/

It provides an interactive interface allowing the user to switch between
Quant A and Quant B modules and configure the analysis parameters.

---

## Project Structure

```bash
.
├── main.py                 # Streamlit application entry point
├── requirements.txt        # Python dependencies
├── instructions.txt        # Project guidelines/notes
├── .gitignore              # Files excluded from Git
├── README.md               # Project documentation
├── quant_a/                # Module A: Single Asset Analysis
│   ├── __init__.py
│   ├── analysis_quanta.py  # Indicators and metrics logic
│   └── visualization.py    # Visualizations for Quant A
├── quant_b/                # Module B: Portfolio Management
│   ├── __init__.py
│   ├── analysis_quantb.py  # Portfolio analysis and metrics
│   └── visualization.py    # Portfolio-specific charts
├── shared/                 # Shared utilities and configuration
│   ├── __init__.py
│   ├── config.py           # Global settings and configuration
│   ├── data_manager.py     # Data fetching and API management
│   ├── metrics.py          # Financial metric formulas
│   ├── plotting.py         # Shared plotting utilities
│   └── ui.py               # Shared UI components for Streamlit
└── scripts/
    ├── daily_report.py     # Automated report generation script
    └── cron_job.txt        # Cron configuration for automated daily financial report

```

## Quant A – Single Asset Analysis

Quant A focuses on the analysis of **one financial asset**.

Implemented features include:
- Price evolution and returns
- Volatility analysis
- Basic financial indicators
- Visual exploration of market behaviour

This module serves as an introduction to quantitative analysis techniques
applied to a single asset.

---

## Quant B – Portfolio Management

Quant B focuses on **multi-asset portfolio analysis** (minimum 3 assets).

Implemented features include:
- Portfolio returns
- Annualised volatility
- Open and close prices
- Maximum drawdown
- Correlation matrix
- Interactive visualisations using Plotly

Quant B extends the project from single-asset analysis to portfolio-level
risk and performance evaluation.

---

## Daily Financial Report (Cron Job)

A **daily financial report** is automatically generated for the portfolio
(Quant B).

### Metrics included
- Portfolio volatility
- Open price
- Close price
- Maximum drawdown

### Script
scripts/daily_report.py

csharp
Copier le code

The report is stored locally on the Linux VM in a `reports/` directory with the format:
daily_report_YYYY-MM-DD.txt

yaml
Copier le code

---

## Cron Configuration

The daily report is generated at a **fixed time (8:00 PM)** using a cron job.

Example configuration on the Linux VM:
```bash
0 20 * * * /usr/bin/python3 /path/to/project/scripts/daily_report.py

The cron configuration and script are included in the repository.

## Authors

- Vincent Guerin  
- Valentin Gempp 
— IF3