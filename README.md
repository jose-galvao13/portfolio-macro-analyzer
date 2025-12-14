# 📈 Macro & Portfolio Analytics Suite

### Overview
A Python-based web application designed for **real-time market monitoring** and **quantitative risk analysis**. Built to bridge the gap between financial theory and data science, this tool allows users to benchmark major asset classes (Equities, Fixed Income, Forex, Commodities, and Crypto) and analyze their risk-adjusted returns.

### 🚀 Key Features
* **Real-Time Data Extraction:** Automated data fetching using `yfinance` API with caching mechanisms for performance optimization.
* **Interactive Visualization:** Professional "Dark Mode" financial charting using `Plotly`, featuring dynamic time-range filtering (1M, YTD, Max).
* **Quantitative Risk Engine:** Automatic calculation of key financial metrics for any selected timeframe:
  * **Sharpe Ratio** (Risk-adjusted performance).
  * **Maximum Drawdown** (Downside risk assessment).
  * **Annualized Volatility**.
  * **Total Return (ROI)**.
* **Interactive UI:** Fully responsive web interface built with `Streamlit`, allowing for column sorting and asset filtering.

### 🛠️ Tech Stack
* **Core:** Python 3.10+
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly Graph Objects
* **Frontend/Deployment:** Streamlit Cloud
* **Financial Data:** Yahoo Finance API
