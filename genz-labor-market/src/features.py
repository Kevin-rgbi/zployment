from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from . import config
from .utils import assert_schema, setup_logging, stable_sort_columns


logger = logging.getLogger(__name__)


def compute_involuntary_part_time_rate(df: pd.DataFrame) -> pd.Series:
    """Underemployment proxy.

    Ideal definition (prompt):
      part_time_for_economic_reasons_20_24 / employed_20_24

    Implemented fallback (documented):
      pt_econ_reasons_overall / employed_overall

    Reason: BLS endpoints are blocked in this environment, and FRED does not expose a
    20–24 breakdown for the part-time-for-economic-reasons numerator.
    """

    num = df["pt_econ_reasons_overall"]
    den = df["employed_overall"]
    rate = num / den
    return rate.replace([np.inf, -np.inf], np.nan)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    required = config.REQUIRED_MONTHLY_COLUMNS
    assert_schema(df, required)

    out = df.copy()

    out["unemp_gap_20_24_minus_25_34"] = out["unemp_rate_20_24"] - out["unemp_rate_25_34"]
    out["unemp_gap_20_24_minus_35_44"] = out["unemp_rate_20_24"] - out["unemp_rate_35_44"]
    out["involuntary_part_time_rate"] = compute_involuntary_part_time_rate(out)

    # Employment rate (in labor force terms): employed / labor force = 1 - unemployment_rate.
    out["employment_rate_lf_20_24"] = 100.0 - out["unemp_rate_20_24"]

    # EPOP (employment-population ratio): employed / population.
    epop = (out["employed_20_24"] / out["population_20_24"]) * 100.0
    out["epop_20_24"] = epop.replace([np.inf, -np.inf], np.nan)

    return stable_sort_columns(out, date_col="date")


def main() -> None:
    setup_logging()
    df = pd.read_csv(config.MONTHLY_OUTPUT_FILE)
    df["date"] = pd.to_datetime(df["date"])
    out = add_features(df)
    out_path = config.PROCESSED_DIR / "monthly_labor_market_features.csv"
    out.to_csv(out_path, index=False)
    logger.info("Wrote %s (%d rows)", out_path, len(out))


if __name__ == "__main__":
    main()
