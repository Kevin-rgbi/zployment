from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from . import config
from .utils import (
    assert_monthly_continuity,
    assert_no_duplicate_dates,
    assert_schema,
    read_fred_csv,
    setup_logging,
    stable_sort_columns,
)


logger = logging.getLogger(__name__)


def _raw_csv_path(dataset_key: str) -> Path:
    spec = config.SERIES[dataset_key]
    return config.RAW_DIR / f"{dataset_key}__{spec.series_id}.csv"


def build_monthly_dataset() -> pd.DataFrame:
    monthly_keys = [k for k, s in config.SERIES.items() if s.frequency == "monthly"]
    frames: list[pd.DataFrame] = []

    for key in monthly_keys:
        spec = config.SERIES[key]
        df = read_fred_csv(_raw_csv_path(key), value_col=spec.series_id)
        df = df.rename(columns={"value": key})
        # Standardize to month start.
        df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp(how="start")
        frames.append(df)

    out = frames[0]
    for df in frames[1:]:
        out = out.merge(df, on="date", how="outer")

    out = out.sort_values("date").reset_index(drop=True)
    out = stable_sort_columns(out, date_col="date")

    assert_schema(out, config.REQUIRED_MONTHLY_COLUMNS)
    assert_no_duplicate_dates(out)
    assert_monthly_continuity(out)

    return out


def build_earnings_quarterly_dataset() -> pd.DataFrame:
    keys = ["earnings_20_24_q", "earnings_25_34_q"]
    frames: list[pd.DataFrame] = []
    for key in keys:
        spec = config.SERIES[key]
        df = read_fred_csv(_raw_csv_path(key), value_col=spec.series_id)
        df = df.rename(columns={"value": key})
        # Standardize to quarter end.
        df["date"] = pd.to_datetime(df["date"]).dt.to_period("Q").dt.to_timestamp(how="end")
        frames.append(df)

    out = frames[0]
    for df in frames[1:]:
        out = out.merge(df, on="date", how="outer")
    out = out.sort_values("date").reset_index(drop=True)
    return stable_sort_columns(out, date_col="date")


def main() -> None:
    setup_logging()
    logger.info("Building monthly dataset")
    monthly = build_monthly_dataset()
    config.MONTHLY_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(config.MONTHLY_OUTPUT_FILE, index=False)
    logger.info("Wrote %s (%d rows)", config.MONTHLY_OUTPUT_FILE, len(monthly))

    logger.info("Building quarterly earnings dataset")
    earnings = build_earnings_quarterly_dataset()
    config.EARNINGS_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    earnings.to_csv(config.EARNINGS_OUTPUT_FILE, index=False)
    logger.info("Wrote %s (%d rows)", config.EARNINGS_OUTPUT_FILE, len(earnings))


if __name__ == "__main__":
    main()
