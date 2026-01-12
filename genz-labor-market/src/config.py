from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


@dataclass(frozen=True)
class SeriesSpec:
    series_id: str
    name: str
    frequency: str
    units: str

    @property
    def url(self) -> str:
        return FRED_CSV_URL.format(series_id=self.series_id)


# --- Required cohorts and metrics ---
# Cohorts per prompt:
# - Primary: 20–24
# - Secondary: 16–24
# - Comparators: 25–34 and 35–44

SERIES: dict[str, SeriesSpec] = {
    # Unemployment rate (U-3) by age
    "unemp_rate_20_24": SeriesSpec(
        series_id="LNS14000036",
        name="Unemployment Rate - 20-24 Yrs.",
        frequency="monthly",
        units="percent",
    ),
    "unemp_rate_16_24": SeriesSpec(
        series_id="LNS14024887",
        name="Unemployment Rate - 16-24 Yrs.",
        frequency="monthly",
        units="percent",
    ),
    "unemp_rate_25_34": SeriesSpec(
        series_id="LNS14000089",
        name="Unemployment Rate - 25-34 Yrs.",
        frequency="monthly",
        units="percent",
    ),
    "unemp_rate_35_44": SeriesSpec(
        series_id="LNS14000091",
        name="Unemployment Rate - 35-44 Yrs.",
        frequency="monthly",
        units="percent",
    ),

    # LFPR (required only for 20–24)
    "lfpr_20_24": SeriesSpec(
        series_id="LNS11300036",
        name="Labor Force Participation Rate - 20-24 Yrs.",
        frequency="monthly",
        units="percent",
    ),

    # Context: U-6 overall
    "u6_overall": SeriesSpec(
        series_id="U6RATE",
        name="Unemployment Rate (U-6) - Overall",
        frequency="monthly",
        units="percent",
    ),

    # Underemployment proxy numerator/denominator.
    # Prompt requirement (ideal): ages 20–24, monthly:
    #   involuntary_part_time_rate_20_24 = part_time_for_economic_reasons_20_24 / employed_20_24
    #
    # Constraint reality in this environment: BLS pages and download endpoints return Access Denied.
    # FRED provides an involuntary part-time series (all ages), but not a 20–24 breakdown.
    # We therefore default to an overall involuntary part-time rate as a documented fallback.
    "employed_20_24": SeriesSpec(
        series_id="LNS12000036",
        name="Employment Level - 20-24 Yrs.",
        frequency="monthly",
        units="thousands",
    ),
    "population_20_24": SeriesSpec(
        series_id="LNU00000036",
        name="Population Level - 20-24 Yrs.",
        frequency="monthly",
        units="thousands",
    ),
    "employed_overall": SeriesSpec(
        series_id="CE16OV",
        name="Employment Level (civilian, 16+)",
        frequency="monthly",
        units="thousands",
    ),
    "pt_econ_reasons_overall": SeriesSpec(
        series_id="LNU02032194",
        name="Employment Level - Persons At Work 1-34 Hours, Economic Reasons, All Industries",
        frequency="monthly",
        units="thousands",
    ),

    # Earnings (quarterly): wage & salary workers, full time, median usual weekly nominal
    "earnings_20_24_q": SeriesSpec(
        series_id="LEU0252887100Q",
        name="Median usual weekly earnings (nominal), 20-24 years (quarterly)",
        frequency="quarterly",
        units="dollars",
    ),
    "earnings_25_34_q": SeriesSpec(
        series_id="LEU0252888500Q",
        name="Median usual weekly earnings (nominal), 25-34 years (quarterly)",
        frequency="quarterly",
        units="dollars",
    ),

    # Optional deflator for real earnings (monthly CPI)
    "cpi_u": SeriesSpec(
        series_id="CPIAUCSL",
        name="Consumer Price Index for All Urban Consumers: All Items",
        frequency="monthly",
        units="index",
    ),
}


MONTHLY_OUTPUT_FILE = PROCESSED_DIR / "monthly_labor_market.csv"
EARNINGS_OUTPUT_FILE = PROCESSED_DIR / "earnings_quarterly.csv"
REPORT_FILE = REPORTS_DIR / "genz_labor_market_report.md"


REQUIRED_MONTHLY_COLUMNS = [
    "date",
    "unemp_rate_20_24",
    "unemp_rate_16_24",
    "unemp_rate_25_34",
    "unemp_rate_35_44",
    "lfpr_20_24",
    "u6_overall",
    "employed_20_24",
    "population_20_24",
    "employed_overall",
    "pt_econ_reasons_overall",
]
