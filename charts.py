"""Matplotlib charts for the dashboard. Each function returns the figure
and saves a PNG if save_to is given."""

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import analysis as an


def _style(ax):
    ax.grid(alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)


def _format_dates(ax):
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))


def _save(fig, save_to):
    if save_to:
        os.makedirs(os.path.dirname(save_to) or ".", exist_ok=True)
        fig.savefig(save_to, dpi=130, bbox_inches="tight")


def dashboard(ticker, dates, prices, fast, slow, vol_window, rf=0.0, save_to=None):
    """4 panels: price + moving averages + crosses, cumulative return,
    rolling volatility, drawdown."""
    r = an.simple_returns(prices)
    golden, death = an.crossover_signals(prices, fast, slow)
    s = an.summary_stats(prices, rf)

    fig, axes = plt.subplots(4, 1, figsize=(12, 13), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.4, 1.4, 1.4]})
    fig.suptitle(
        f"{ticker}   |   Total {s['total_return']:+.1%}   CAGR {s['cagr']:+.1%}   "
        f"Vol {s['ann_volatility']:.1%}   Sharpe {s['sharpe']:.2f}   "
        f"Max DD {s['max_drawdown']:.1%}", fontsize=12, fontweight="bold")

    ax = axes[0]
    ax.plot(dates, prices, color="#1f2937", lw=1.2, label="Price")
    ax.plot(dates, an.sma(prices, fast), color="#2563eb", lw=1.3, label=f"SMA {fast}")
    ax.plot(dates, an.ema(prices, fast), color="#16a34a", lw=1.1, ls="--", label=f"EMA {fast}")
    ax.plot(dates, an.sma(prices, slow), color="#ea580c", lw=1.3, label=f"SMA {slow}")
    ax.scatter(dates[golden], prices[golden], marker="^", s=90, color="#16a34a",
               zorder=5, label="Golden cross")
    ax.scatter(dates[death], prices[death], marker="v", s=90, color="#dc2626",
               zorder=5, label="Death cross")
    ax.set_ylabel("Price ($)")
    ax.legend(loc="upper left", fontsize=9, frameon=False, ncol=3)

    ax = axes[1]
    cum = an.cumulative_returns(prices) * 100
    ax.plot(dates, cum, color="#7c3aed", lw=1.2)
    ax.fill_between(dates, cum, 0, where=cum >= 0, color="#7c3aed", alpha=0.12)
    ax.fill_between(dates, cum, 0, where=cum < 0, color="#dc2626", alpha=0.12)
    ax.axhline(0, color="gray", lw=0.6)
    ax.set_ylabel("Cumulative\nreturn (%)")

    ax = axes[2]
    ax.plot(dates[1:], an.rolling_volatility(r, vol_window) * 100, color="#0891b2", lw=1.2)
    ax.axhline(s["ann_volatility"] * 100, color="gray", ls="--", lw=0.8,
               label=f"Full-period {s['ann_volatility']:.1%}")
    ax.set_ylabel(f"{vol_window}d ann.\nvol (%)")
    ax.legend(loc="upper left", fontsize=9, frameon=False)

    ax = axes[3]
    ax.fill_between(dates, an.drawdown(prices) * 100, 0, color="#dc2626", alpha=0.35)
    ax.set_ylabel("Drawdown (%)")

    for ax in axes:
        _style(ax)
    _format_dates(axes[-1])
    fig.tight_layout()
    _save(fig, save_to)
    return fig


def return_histogram(ticker, prices, save_to=None):
    """Daily return distribution vs. a normal curve with the same mean/std."""
    r = an.simple_returns(prices) * 100
    mu, sd = r.mean(), r.std(ddof=1)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.hist(r, bins=60, density=True, color="#2563eb", alpha=0.6, edgecolor="white")
    x = np.linspace(r.min(), r.max(), 300)
    ax.plot(x, np.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi)),
            color="#ea580c", lw=2, label=f"Normal (mean {mu:.2f}%, std {sd:.2f}%)")
    ax.set_xlabel("Daily return (%)")
    ax.set_ylabel("Density")
    ax.set_title(f"{ticker} daily return distribution", fontweight="bold")
    ax.legend(frameon=False)
    _style(ax)
    fig.tight_layout()
    _save(fig, save_to)
    return fig


def comparison(price_dict, save_to=None):
    """Growth of $100 for every ticker."""
    fig, ax = plt.subplots(figsize=(12, 5))
    for t, (d, p) in price_dict.items():
        ax.plot(d, 100 * p / p[0], lw=1.4, label=t)
    ax.axhline(100, color="gray", lw=0.6)
    ax.set_ylabel("Value of $100")
    ax.set_title("Growth of $100", fontweight="bold")
    ax.legend(frameon=False)
    _style(ax)
    _format_dates(ax)
    fig.tight_layout()
    _save(fig, save_to)
    return fig


def correlation_heatmap(tickers, corr, save_to=None):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(tickers)), tickers)
    ax.set_yticks(range(len(tickers)), tickers)
    for i in range(len(tickers)):
        for j in range(len(tickers)):
            ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr[i, j]) > 0.6 else "black")
    ax.set_title("Daily return correlation", fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    _save(fig, save_to)
    return fig


def risk_return(stats, rf=0.0, save_to=None):
    """CAGR vs. volatility per ticker; bubble size = max drawdown."""
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for t, s in stats.items():
        x, y = s["ann_volatility"] * 100, s["cagr"] * 100
        ax.scatter(x, y, s=abs(s["max_drawdown"]) * 2500, alpha=0.5)
        ax.annotate(t, (x, y), ha="center", va="center", fontweight="bold")
    ax.axhline(rf * 100, color="gray", ls="--", lw=0.8, label=f"Risk-free {rf:.0%}")
    ax.set_xlabel("Annualized volatility (%)")
    ax.set_ylabel("CAGR (%)")
    ax.set_title("Risk vs. return", fontweight="bold")
    ax.legend(frameon=False)
    _style(ax)
    fig.tight_layout()
    _save(fig, save_to)
    return fig
