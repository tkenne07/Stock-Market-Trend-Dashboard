# Stock Market Trend Dashboard

Loads historical stock prices from CSV files, calculates returns, moving averages, volatility and risk metrics, and visualizes the trends. Built with NumPy and matplotlib only (no pandas), so every financial formula is written out by hand.

## Features

- **Returns:** simple, log, and cumulative returns
- **Moving averages:** 50/200-day SMA, EMA, and golden/death cross detection
- **Risk:** rolling annualized volatility, max drawdown, Sharpe ratio, CAGR
- **Distribution:** daily return histogram vs. a normal curve, skew and kurtosis
- **Multi-stock comparison:** growth of $100, return correlation heatmap, risk vs. return chart

## Project structure

```
├── main.py                  # entry point: run this
├── config.py                # settings (tickers, MA windows, risk-free rate)
├── data_loader.py           # reads the CSVs
├── analysis.py              # returns, moving averages, volatility, risk metrics
├── charts.py                # matplotlib charts
├── report.py                # terminal summaries
├── make_sample_data.py      # optional: generates synthetic test CSVs
├── requirements.txt
└── data/                    # put your CSVs here (one per ticker)
```

## Getting started

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Add stock price CSVs to the `data/` folder, one file per ticker, named after it (e.g. `data/AAPL.csv`). See **Getting data** below.
3. Set `FOCUS = "AAPL"` in `config.py` (optional; defaults to the first CSV).
4. Run:
   ```bash
   python main.py
   ```

The script prints a stats summary to the terminal, opens the charts, and saves them to `output/`.

## Getting data

CSVs need a `Date` column (`YYYY-MM-DD`) and a `Close` or `Adj Close` column. Free sources that work:

- **[Stooq](https://stooq.com):** search a ticker (e.g. `aapl.us`) and download the daily CSV.
- **[yfinance](https://pypi.org/project/yfinance/):**
  ```python
  import yfinance as yf
  yf.Ticker("AAPL").history(period="3y").to_csv("data/AAPL.csv")
  ```

Use at least ~1 year of daily data so the 200-day moving average has room to show up. With two or more CSVs in `data/`, the comparison, correlation, and risk-vs-return charts are generated too.

`make_sample_data.py` can generate synthetic CSVs if you want to test without real data.

## Settings

All in `config.py`:

| Setting | Default | Meaning |
|---|---|---|
| `FOCUS` | first CSV | Ticker for the detailed analysis |
| `FAST`, `SLOW` | 50, 200 | Moving-average windows (trading days) |
| `VOL_WINDOW` | 21 | Rolling volatility window (~1 month) |
| `RISK_FREE` | 0.04 | Annual risk-free rate for the Sharpe ratio |
