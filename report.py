"""Text summaries printed to the terminal."""

import numpy as np

import analysis as an
from config import TRADING_DAYS


def print_focus(ticker, dates, prices, fast, slow, vol_window):
    """Detailed stats for one ticker."""
    r = an.simple_returns(prices)
    f_sma, s_sma = an.sma(prices, fast)[-1], an.sma(prices, slow)[-1]
    golden, death = an.crossover_signals(prices, fast, slow)
    dd = an.drawdown(prices)
    trough = dd.argmin()
    peak = prices[:trough + 1].argmax()
    skew, kurt = an.skew_kurtosis(r)

    print(f"\n=== {ticker} ===")
    print(f"Total return     : {an.cumulative_returns(prices)[-1]:+.2%}")
    print(f"Latest price     : ${prices[-1]:.2f}")
    print(f"SMA {fast} / SMA {slow} : ${f_sma:.2f} / ${s_sma:.2f}", end="")
    print("" if np.isnan(s_sma) else f"  ({'above' if f_sma > s_sma else 'below'})")
    print(f"Golden crosses   : {[str(dates[i]) for i in golden]}")
    print(f"Death crosses    : {[str(dates[i]) for i in death]}")
    print(f"Annualized vol   : {r.std(ddof=1) * np.sqrt(TRADING_DAYS):.2%}")
    print(f"Current {vol_window}d vol  : {an.rolling_volatility(r, vol_window)[-1]:.2%}")
    print(f"Max drawdown     : {dd[trough]:.2%}  ({dates[peak]} -> {dates[trough]})")
    print(f"Skew / kurtosis  : {skew:+.3f} / {kurt:.3f}  (normal = 0 / 3)")


def print_table(stats, rf):
    """One row per ticker, sorted by Sharpe ratio."""
    print(f"\n{'Ticker':<7}{'Total':>9}{'CAGR':>9}{'Vol':>8}{'Sharpe':>8}"
          f"{'MaxDD':>9}{'Best':>8}{'Worst':>8}{'Up%':>7}")
    print("-" * 73)
    for t, s in sorted(stats.items(), key=lambda kv: -kv[1]["sharpe"]):
        print(f"{t:<7}{s['total_return']:>+9.1%}{s['cagr']:>+9.1%}"
              f"{s['ann_volatility']:>8.1%}{s['sharpe']:>8.2f}{s['max_drawdown']:>9.1%}"
              f"{s['best_day']:>+8.1%}{s['worst_day']:>+8.1%}{s['pct_up_days']:>7.1%}")
    print(f"(sorted by Sharpe, risk-free = {rf:.0%})")
