"""
Generate synthetic stock CSVs (Yahoo Finance format) so the dashboard runs
offline. Prices follow geometric Brownian motion with a shared market factor
plus a couple of regime shifts, so you get real-looking trends, crashes,
and MA crossovers. NOT real market data.

Swap in real data anytime: download a CSV from finance.yahoo.com
(Historical Data -> Download) and drop it in data/.
"""

import csv
import os
from datetime import date, timedelta

import numpy as np

rng = np.random.default_rng(42)
N_DAYS = 252 * 3  # ~3 years

# Trading calendar (weekdays only)
days, d = [], date(2023, 11, 1)
while len(days) < N_DAYS:
    if d.weekday() < 5:
        days.append(d)
    d += timedelta(days=1)

# Shared market shock, with a drawdown regime in the middle
market = rng.normal(0, 0.010, N_DAYS)
market[300:350] -= 0.003   # sell-off
market[350:420] += 0.0025  # rebound

# ticker: (start price, annual drift, idiosyncratic vol, market beta)
tickers = {
    "TECH": (150.0, 0.22, 0.016, 1.4),
    "BANK": (45.0,  0.08, 0.011, 1.1),
    "UTIL": (70.0,  0.05, 0.007, 0.4),
    "MKT":  (400.0, 0.10, 0.002, 1.0),
}

os.makedirs("data", exist_ok=True)
for t, (p0, mu, sigma, beta) in tickers.items():
    r = mu / 252 + beta * market + rng.normal(0, sigma, N_DAYS)
    close = p0 * np.exp(np.cumsum(r - 0.5 * (sigma**2 + (beta * 0.01)**2)))
    open_ = close * (1 + rng.normal(0, 0.004, N_DAYS))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, N_DAYS)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, N_DAYS)))
    vol = rng.integers(2_000_000, 30_000_000, N_DAYS)

    with open(f"data/{t}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"])
        for i, day in enumerate(days):
            w.writerow([day.isoformat(), f"{open_[i]:.2f}", f"{high[i]:.2f}",
                        f"{low[i]:.2f}", f"{close[i]:.2f}", f"{close[i]:.2f}", vol[i]])
    print(f"wrote data/{t}.csv  ({N_DAYS} rows, {close[0]:.2f} -> {close[-1]:.2f})")
