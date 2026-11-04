"""Financial calculations: returns, moving averages, volatility and risk metrics."""

import numpy as np

from config import TRADING_DAYS


# ---------------------------------------------------------------- returns
def simple_returns(prices):
    """r_t = P_t / P_(t-1) - 1"""
    return prices[1:] / prices[:-1] - 1


def log_returns(prices):
    """r_t = ln(P_t / P_(t-1)). These add up across days."""
    return np.diff(np.log(prices))


def cumulative_returns(prices):
    """Total gain since day 0: P_t / P_0 - 1"""
    return prices / prices[0] - 1


# ---------------------------------------------------------------- moving averages
def sma(x, window):
    """Simple moving average via cumulative sum (no loop).
    First window-1 values are NaN."""
    out = np.full(len(x), np.nan)
    if len(x) < window:
        return out
    c = np.cumsum(np.insert(x, 0, 0.0))
    out[window - 1:] = (c[window:] - c[:-window]) / window
    return out


def ema(x, span):
    """Exponential moving average: E_t = a*P_t + (1-a)*E_(t-1), a = 2/(span+1)."""
    alpha = 2 / (span + 1)
    out = np.empty(len(x))
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


def crossover_signals(prices, fast, slow):
    """Golden cross = fast SMA crosses above slow SMA; death cross = below.
    Returns (golden_indices, death_indices)."""
    diff = np.sign(sma(prices, fast) - sma(prices, slow))
    valid = ~np.isnan(diff)
    change = np.zeros(len(prices))
    change[1:] = np.where(valid[1:] & valid[:-1], np.diff(diff), 0)
    return np.where(change > 0)[0], np.where(change < 0)[0]


# ---------------------------------------------------------------- risk
def rolling_volatility(returns, window):
    """Annualized rolling std dev of returns. First window-1 values are NaN."""
    out = np.full(len(returns), np.nan)
    if len(returns) >= window:
        windows = np.lib.stride_tricks.sliding_window_view(returns, window)
        out[window - 1:] = windows.std(axis=1, ddof=1)
    return out * np.sqrt(TRADING_DAYS)


def drawdown(prices):
    """How far below the running peak price, at each point (<= 0)."""
    return prices / np.maximum.accumulate(prices) - 1


def summary_stats(prices, rf=0.0):
    """Headline metrics for one stock. rf = annual risk-free rate."""
    r = simple_returns(prices)
    years = len(r) / TRADING_DAYS
    excess = r - rf / TRADING_DAYS
    return {
        "total_return": prices[-1] / prices[0] - 1,
        "cagr": (prices[-1] / prices[0]) ** (1 / years) - 1,
        "ann_volatility": r.std(ddof=1) * np.sqrt(TRADING_DAYS),
        "sharpe": excess.mean() / excess.std(ddof=1) * np.sqrt(TRADING_DAYS),
        "max_drawdown": drawdown(prices).min(),
        "best_day": r.max(),
        "worst_day": r.min(),
        "pct_up_days": (r > 0).mean(),
    }


def skew_kurtosis(returns):
    """Shape of the return distribution. Normal = (0, 3)."""
    z = (returns - returns.mean()) / returns.std(ddof=1)
    return np.mean(z ** 3), np.mean(z ** 4)


def correlation_matrix(price_dict):
    """Correlation of daily returns across tickers, aligned on shared dates.
    Returns (tickers, matrix)."""
    tickers = list(price_dict)
    common = price_dict[tickers[0]][0]
    for t in tickers[1:]:
        common = np.intersect1d(common, price_dict[t][0])
    rets = [simple_returns(p[np.isin(d, common)]) for d, p in price_dict.values()]
    return tickers, np.corrcoef(np.vstack(rets))
