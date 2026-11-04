"""Load stock price CSVs (Yahoo Finance format) into NumPy arrays."""

import csv
import glob
import os
from datetime import datetime

import numpy as np


def load_csv(path, price_col="Adj Close"):
    """Return (dates, prices) for one CSV, sorted oldest -> newest.

    Uses 'Adj Close' if present, otherwise 'Close'. Skips blank/null rows.
    """
    dates, prices = [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        col = price_col if price_col in reader.fieldnames else "Close"
        if col not in reader.fieldnames:
            raise ValueError(f"{path}: no '{price_col}' or 'Close' column")
        for row in reader:
            raw = (row.get(col) or "").strip()
            if raw in ("", "null", "NaN"):
                continue
            dates.append(datetime.strptime(row["Date"].strip()[:10], "%Y-%m-%d"))
            prices.append(float(raw))

    dates = np.array(dates, dtype="datetime64[D]")
    prices = np.array(prices, dtype=float)
    order = np.argsort(dates)
    return dates[order], prices[order]


def load_folder(folder):
    """Load every CSV in a folder. Returns {ticker: (dates, prices)}.

    The ticker is the file name, e.g. data/AAPL.csv -> "AAPL".
    """
    paths = sorted(glob.glob(os.path.join(folder, "*.csv")))
    return {
        os.path.splitext(os.path.basename(p))[0].upper(): load_csv(p)
        for p in paths
    }
