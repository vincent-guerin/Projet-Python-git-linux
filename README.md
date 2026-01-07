# Quant B – Portfolio Module

This repository contains my **Quant B** implementation, focused on
**multi-asset portfolio analysis** and an **automated daily financial report**.

The objective of this module is to analyse a portfolio of several assets,
compute key financial metrics, and generate a daily report automatically
using a cron job on the Linux VM.

---

## Project Structure

quant_b/
├── analysis_quantb.py # Portfolio analysis and metrics
├── visualization.py # Plotly visualizations
└── init.py

scripts/
└── daily_report.py # Daily report script (used by cron)

README.md


---

## Quant B – Portfolio Analysis

The Quant B module performs **multi-asset portfolio analysis** (minimum 3 assets).

Implemented features:
- Portfolio returns
- Annualized volatility
- Open and close prices
- Maximum drawdown
- Correlation matrix
- Interactive visualizations using Plotly

The portfolio logic is implemented in `analysis_quantb.py` and is designed
to be integrated into a Streamlit application via a `run_quant_b()` function.

---

## Daily Financial Report

A **daily financial report** is generated automatically for the portfolio.

### Metrics included
- Portfolio volatility
- Open price
- Close price
- Maximum drawdown

### Script location

scripts/daily_report.py

The report is saved locally on the VM in a `reports/` directory with the name:

daily_report_YYYY-MM-DD.txt

---

## Cron Job Configuration

The daily report is generated at a **fixed time (8:00 PM)** using a cron job.

Example cron configuration (Linux VM):

```bash
0 20 * * * /usr/bin/python3 /home/user/Projet-Python-git-linux/scripts/daily_report.py

The cron configuration is documented in the repository.
