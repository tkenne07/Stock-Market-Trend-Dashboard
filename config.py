"""Project settings. Change these to adjust the analysis."""

DATA_DIR = "data"      # folder with input CSVs
OUTPUT_DIR = "output"  # where chart PNGs are saved

FOCUS = None           # ticker for the detailed analysis, e.g. "AAPL"; None = first CSV
FAST, SLOW = 50, 200   # moving-average windows (trading days)
VOL_WINDOW = 21        # rolling volatility window (~1 trading month)
RISK_FREE = 0.04       # annual risk-free rate, used in the Sharpe ratio
TRADING_DAYS = 252     # trading days per year (annualization factor)
