# Quant Backtesting Platform

A professional-grade dashboard for financial data analysis, backtesting, and portfolio management.

## Features
- **Real-time Data**: Fetches financial data using Yahoo Finance API.
- **Auto-Refresh**: Dashboard updates automatically every 5 minutes.
- **Quant A (Univariate)**: Single asset analysis, momentum & ADX strategies, ARIMA forecasting.
- **Quant B (Multivariate)**: Portfolio optimization (Markowitz), correlation matrix, multi-asset simulation.
- **Daily Reports**: Automated daily reporting via cron.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Projet_python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit application:
```bash
streamlit run main.py
```
The application will open in your default web browser (usually at `http://localhost:8501`).

## Deployment (Linux VM)

### 1. Run as a Service (Systemd)
To keep the app running 24/7, create a systemd service.

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/quant_app.service
   ```

2. Add the following content (adjust paths and user):
   ```ini
   [Unit]
   Description=Quant Streamlit App
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/Projet_python
   ExecStart=/path/to/venv/bin/streamlit run main.py --server.port 8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Start and enable the service:
   ```bash
   sudo systemctl start quant_app
   sudo systemctl enable quant_app
   ```

### 2. Daily Report (Cron Job)
To generate a daily report at 8:00 PM:

1. Open crontab:
   ```bash
   crontab -e
   ```

2. Add the following line:
   ```bash
   0 20 * * * /path/to/venv/bin/python /path/to/Projet_python/scripts/daily_report.py >> /path/to/Projet_python/cron.log 2>&1
   ```

## Project Structure
## Project Structure
- `main.py`: Entry point of the application.
- `quant_a/`: Module for single asset analysis.
    - `analysis_quanta.py`: Core logic for Quant A.
    - `visualization.py`: Visualization for Quant A.
- `quant_b/`: Module for portfolio management.
    - `analysis_quantb.py`: Core logic for Quant B.
    - `visualization.py`: Visualization for Quant B.
- `shared/`: Shared utilities (Data fetching, Metrics).
    - `data_manager.py`: Data fetching utilities.
    - `metrics.py`: Quantitative metrics.
- `scripts/`: Standalone scripts.
    - `daily_report.py`: Script for generating daily reports.
- `requirements.txt`: Python dependencies.
- `requirements.txt`: Python dependencies.
