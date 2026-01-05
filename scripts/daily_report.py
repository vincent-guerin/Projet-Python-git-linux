import sys
import os
from datetime import datetime
import pandas as pd

# Add parent path to import from 'shared'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.data_manager import get_financial_data
from shared.config import DEFAULT_ASSETS, REPORTS_DIR_NAME

# Configuration
ASSETS = DEFAULT_ASSETS
# Relative path to project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORT_DIR = os.path.join(BASE_DIR, REPORTS_DIR_NAME)
REPORT_FILE = os.path.join(REPORT_DIR, f"daily_report_{datetime.now().strftime('%Y-%m-%d')}.txt")

def generate_report():
    # Ensure report directory exists
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    print(f"Generating report for {datetime.now().strftime('%Y-%m-%d')}...")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"DAILY FINANCIAL REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")

        # Fetch data
        data = get_financial_data(ASSETS, period="1mo", interval="1d")
        
        if data.empty:
            f.write("ERROR: No data retrieved.\n")
            return

        # Handle MultiIndex columns if necessary
        if isinstance(data.columns, pd.MultiIndex):
            close_prices = data['Close']
        else:
            close_prices = data

        for ticker in ASSETS:
            try:
                if ticker not in close_prices.columns:
                    f.write(f"[{ticker}] Data not available.\n")
                    continue

                series = close_prices[ticker].dropna()
                if series.empty:
                    f.write(f"[{ticker}] No data points.\n")
                    continue

                current_price = series.iloc[-1]
                prev_price = series.iloc[-2]
                change = (current_price - prev_price) / prev_price
                
                # Volatility (30 days annualized)
                returns = series.pct_change().dropna()
                volatility = returns.std() * (252 ** 0.5)

                # Max Drawdown (30 days)
                rolling_max = series.cummax()
                drawdown = (series - rolling_max) / rolling_max
                max_dd = drawdown.min()

                f.write(f"Asset: {ticker}\n")
                f.write(f"  Close Price:   ${current_price:.2f}\n")
                f.write(f"  Daily Change:  {change:+.2%}\n")
                f.write(f"  Volatility:    {volatility:.2%}\n")
                f.write(f"  Max Drawdown:  {max_dd:.2%}\n")
                f.write("-" * 30 + "\n")

            except Exception as e:
                f.write(f"[{ticker}] Error calculating metrics: {e}\n")

    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()
