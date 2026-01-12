from __future__ import annotations

import logging

import matplotlib.pyplot as plt
import pandas as pd

from . import config
from .utils import ensure_dirs, setup_logging


logger = logging.getLogger(__name__)


def savefig(path):
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_unemployment_by_age(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["unemp_rate_20_24"], label="20–24")
    plt.plot(df["date"], df["unemp_rate_25_34"], label="25–34")
    plt.plot(df["date"], df["unemp_rate_35_44"], label="35–44")
    plt.title("Unemployment rate (U-3) by cohort")
    plt.ylabel("Percent")
    plt.legend()
    savefig(config.FIGURES_DIR / "01_unemployment_by_age.png")


def plot_unemployment_hist_percentile(df: pd.DataFrame) -> None:
    s = df["unemp_rate_20_24"].dropna().astype(float)
    current = float(s.iloc[-1])
    plt.figure(figsize=(8, 5))
    plt.hist(s, bins=40)
    plt.axvline(current, color="black", linewidth=2, label="Current")
    plt.title("20–24 unemployment: historical distribution")
    plt.xlabel("Percent")
    plt.ylabel("Months")
    plt.legend()
    savefig(config.FIGURES_DIR / "02_unemployment_hist_percentile.png")


def plot_involuntary_part_time(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["involuntary_part_time_rate"] * 100.0)
    plt.title("Underemployment proxy: involuntary part-time rate (overall fallback)")
    plt.ylabel("Percent of employed")
    savefig(config.FIGURES_DIR / "03_involuntary_part_time_rate.png")


def plot_lfpr_20_24(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["lfpr_20_24"])
    plt.title("Labor force participation rate: ages 20–24")
    plt.ylabel("Percent")
    savefig(config.FIGURES_DIR / "04_lfpr_20_24.png")


def plot_earnings(earnings: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(earnings["date"], earnings["earnings_20_24_q"], label="20–24")
    plt.plot(earnings["date"], earnings["earnings_25_34_q"], label="25–34")
    plt.title("Median usual weekly earnings (nominal, quarterly)")
    plt.ylabel("USD")
    plt.legend()
    savefig(config.FIGURES_DIR / "05_earnings_20_24_vs_25_34.png")


def plot_u6_overlay(df: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["unemp_rate_20_24"], label="U-3 (20–24)")
    plt.plot(df["date"], df["u6_overall"], label="U-6 (overall)")
    plt.title("U-3 vs U-6 (context)")
    plt.ylabel("Percent")
    plt.legend()
    savefig(config.FIGURES_DIR / "06_u3_vs_u6.png")


def main() -> None:
    setup_logging()
    ensure_dirs(config.FIGURES_DIR)
    features_path = config.PROCESSED_DIR / "monthly_labor_market_features.csv"
    df = pd.read_csv(features_path)
    df["date"] = pd.to_datetime(df["date"])
    earnings = pd.read_csv(config.EARNINGS_OUTPUT_FILE)
    earnings["date"] = pd.to_datetime(earnings["date"])

    plot_unemployment_by_age(df)
    plot_unemployment_hist_percentile(df)
    plot_involuntary_part_time(df)
    plot_lfpr_20_24(df)
    plot_earnings(earnings)
    plot_u6_overlay(df)

    logger.info("Wrote figures to %s", config.FIGURES_DIR)


if __name__ == "__main__":
    main()
