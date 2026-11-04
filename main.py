"""Stock Market Trend Dashboard: run this file.

Loads every CSV in data/, prints stats, and saves/shows the charts.
Settings live in config.py.
"""

import os

import matplotlib.pyplot as plt

import analysis
import charts
import config as cfg
import report
from data_loader import load_folder


def main():
    prices = load_folder(cfg.DATA_DIR)
    if not prices:
        raise SystemExit(f"No CSV files found in '{cfg.DATA_DIR}/'.")

    focus = cfg.FOCUS.upper() if cfg.FOCUS and cfg.FOCUS.upper() in prices else next(iter(prices))
    dates, px = prices[focus]
    out = lambda name: os.path.join(cfg.OUTPUT_DIR, name)

    # Detailed analysis of one stock
    report.print_focus(focus, dates, px, cfg.FAST, cfg.SLOW, cfg.VOL_WINDOW)
    charts.dashboard(focus, dates, px, cfg.FAST, cfg.SLOW, cfg.VOL_WINDOW,
                     rf=cfg.RISK_FREE, save_to=out(f"{focus}_dashboard.png"))
    charts.return_histogram(focus, px, save_to=out(f"{focus}_returns_hist.png"))

    # Comparison across all stocks
    stats = {t: analysis.summary_stats(p, cfg.RISK_FREE) for t, (_, p) in prices.items()}
    report.print_table(stats, cfg.RISK_FREE)

    if len(prices) > 1:
        charts.comparison(prices, save_to=out("comparison.png"))
        charts.correlation_heatmap(*analysis.correlation_matrix(prices),
                                   save_to=out("correlation.png"))
        charts.risk_return(stats, rf=cfg.RISK_FREE, save_to=out("risk_return.png"))

    print(f"\nCharts saved to '{cfg.OUTPUT_DIR}/'")
    plt.show()


if __name__ == "__main__":
    main()
