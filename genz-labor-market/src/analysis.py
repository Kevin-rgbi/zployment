from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config
from .utils import setup_logging


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrendResult:
    months: int
    slope_per_month: float
    slope_ci95: tuple[float, float]


def percentile_rank(series: pd.Series, value: float) -> float:
    s = series.dropna().astype(float)
    if len(s) == 0:
        return float("nan")
    return float((s <= value).mean())


def rolling_zscore(series: pd.Series, window: int = 60) -> pd.Series:
    s = series.astype(float)
    mean = s.rolling(window=window, min_periods=max(12, window // 3)).mean()
    std = s.rolling(window=window, min_periods=max(12, window // 3)).std(ddof=0)
    return (s - mean) / std


def linear_trend_with_ci(y: pd.Series, months: int) -> TrendResult:
    y = y.dropna().astype(float)
    if len(y) < max(12, months // 2):
        return TrendResult(months=months, slope_per_month=float("nan"), slope_ci95=(float("nan"), float("nan")))
    y = y.iloc[-months:]
    x = np.arange(len(y), dtype=float)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y.to_numpy(), rcond=None)[0]
    y_hat = slope * x + intercept
    resid = y.to_numpy() - y_hat
    dof = max(len(y) - 2, 1)
    s_err = np.sqrt(np.sum(resid**2) / dof)
    x_mean = x.mean()
    sxx = np.sum((x - x_mean) ** 2)
    if sxx == 0:
        return TrendResult(months=months, slope_per_month=float("nan"), slope_ci95=(float("nan"), float("nan")))
    slope_se = s_err / np.sqrt(sxx)
    # 95% CI using normal approx (recruiter-friendly; avoids scipy dependency)
    z = 1.96
    lo = slope - z * slope_se
    hi = slope + z * slope_se
    return TrendResult(months=months, slope_per_month=float(slope), slope_ci95=(float(lo), float(hi)))


def peak_in_window(df: pd.DataFrame, col: str, start: str, end: str) -> tuple[pd.Timestamp, float] | None:
    mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
    s = df.loc[mask, ["date", col]].dropna()
    if s.empty:
        return None
    idx = s[col].astype(float).idxmax()
    row = s.loc[idx]
    return pd.to_datetime(row["date"]), float(row[col])


def build_report(md_path: str, summary: dict[str, object]) -> None:
    lines: list[str] = []
    lines.append("# Gen Z Labor Market Report (Reproducible)\n")
    lines.append("## Executive summary\n")
    current_date = summary.get("current_date")
    lines.append(
        "This report is generated from public FRED time series (no API keys). "
        f"All statistics below are computed from the downloaded data as of {current_date}.\n"
    )

    lines.append("## Metric definitions\n")
    lines.append("- **Unemployment rate (U-3)**: unemployed / labor force (percent).\n")
    lines.append("- **LFPR (20–24)**: labor force / population (percent).\n")
    lines.append(
        "- **Underemployment proxy (involuntary part-time rate)**: part-time for economic reasons / employed. "
        "In this environment we compute the **overall** rate as a documented fallback (BLS endpoints blocked).\n"
    )

    lines.append("## Data sources (URLs + download dates)\n")
    lines.append("Pipeline writes one metadata JSON per dataset under `data/metadata/`.\n")
    for k, v in summary["sources"].items():
        lines.append(f"- **{k}**: {v['url']} (downloaded_at_utc: {v['downloaded_at_utc']})\n")

    lines.append("\n## Methodology\n")
    lines.append("### Historic benchmark (unemployment_20_24)\n")
    lines.append("- **Percentile rank**: fraction of historical months with value ≤ current.\n")
    lines.append("- **Peaks**: max within 2007–2009 window and within 2020 calendar year.\n")
    lines.append("- **Rolling z-score**: 60-month rolling standard score.\n")

    lines.append("\n### Gaining ground\n")
    lines.append("- **Trend**: simple linear trend over last 24 and 60 months with 95% CI.\n")
    lines.append("- **Gap analysis**: (20–24 minus 25–34) unemployment rate.\n")

    lines.append("\n## Key findings (populated after execution)\n")
    pct = summary.get("percentile_rank_unemp_20_24")
    cur = summary.get("current_unemp_20_24")
    trend24 = summary.get("trend_24m")
    trend60 = summary.get("trend_60m")
    gr_peak = summary.get("great_recession_peak")
    p2020 = summary.get("peak_2020")
    u_gap24 = summary.get("gap_trend_24m")
    u_pt24 = summary.get("underemployment_trend_24m")

    if isinstance(pct, (int, float)) and isinstance(cur, (int, float)):
        lines.append(f"- **Unemployment (20–24)** is **{cur:.1f}%** and sits at the **{pct * 100:.0f}th percentile** of its historical monthly distribution.\n")
    if isinstance(gr_peak, dict) and "value" in gr_peak and "date" in gr_peak:
        lines.append(f"- **Great Recession peak (20–24)**: {gr_peak['value']:.1f}% ({gr_peak['date']}).\n")
    if isinstance(p2020, dict) and "value" in p2020 and "date" in p2020:
        lines.append(f"- **2020 peak (20–24)**: {p2020['value']:.1f}% ({p2020['date']}).\n")
    if isinstance(trend24, dict):
        lines.append(
            f"- **24-month trend (20–24 unemployment)**: {trend24['slope_per_month']:+.3f} pp/month "
            f"(95% CI: [{trend24['ci95_lo']:+.3f}, {trend24['ci95_hi']:+.3f}]).\n"
        )
    if isinstance(trend60, dict):
        lines.append(
            f"- **60-month trend (20–24 unemployment)**: {trend60['slope_per_month']:+.3f} pp/month "
            f"(95% CI: [{trend60['ci95_lo']:+.3f}, {trend60['ci95_hi']:+.3f}]).\n"
        )
    if isinstance(u_gap24, dict):
        lines.append(
            f"- **Cohort gap (20–24 minus 25–34), 24-month trend**: {u_gap24['slope_per_month']:+.3f} pp/month "
            f"(95% CI: [{u_gap24['ci95_lo']:+.3f}, {u_gap24['ci95_hi']:+.3f}]).\n"
        )
    if isinstance(u_pt24, dict):
        lines.append(
            f"- **Underemployment proxy (overall involuntary part-time rate), 24-month trend**: {u_pt24['slope_per_month']:+.4f} per month "
            f"(95% CI: [{u_pt24['ci95_lo']:+.4f}, {u_pt24['ci95_hi']:+.4f}]).\n"
        )

    lines.append("\n## Limitations\n")
    lines.append("- Age cohorts are proxies for Gen Z and do not capture education status or enrollment.\n")
    lines.append("- Seasonality and survey design changes can affect comparability across decades.\n")
    lines.append(
        "- Underemployment by age ideally uses age-specific ‘part-time for economic reasons’ numerator; "
        "BLS access restrictions in this environment force an overall-rate fallback.\n"
    )

    lines.append("\n## Reproducibility\n")
    lines.append("Run:\n")
    lines.append("```bash\npython -m src.fetch_sources\npython -m src.clean\npython -m src.features\npython -m src.analysis\npython -m src.viz\n```\n")

    config.REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.REPORT_FILE.write_text("".join(lines))


def main() -> None:
    setup_logging()
    features_path = config.PROCESSED_DIR / "monthly_labor_market_features.csv"
    if not features_path.exists():
        raise SystemExit(
            "Missing required file: data/processed/monthly_labor_market_features.csv\n"
            "Run the pipeline steps first:\n"
            "  python -m src.fetch_sources\n"
            "  python -m src.clean\n"
            "  python -m src.features\n"
            "Then re-run:\n"
            "  python -m src.analysis\n"
        )
    df = pd.read_csv(features_path)
    df["date"] = pd.to_datetime(df["date"])

    col = "unemp_rate_20_24"
    current_date = df["date"].max()
    current_value = float(df.loc[df["date"] == current_date, col].iloc[0])

    pct = percentile_rank(df[col], current_value)
    z = rolling_zscore(df[col], window=60)
    df["unemp_20_24_z60"] = z

    trend24 = linear_trend_with_ci(df[col], months=24)
    trend60 = linear_trend_with_ci(df[col], months=60)

    # Additional trend diagnostics
    gap_col = "unemp_gap_20_24_minus_25_34" if "unemp_gap_20_24_minus_25_34" in df.columns else None
    gap24 = None if gap_col is None else linear_trend_with_ci(df[gap_col], months=24)

    u_pt_col = "involuntary_part_time_rate" if "involuntary_part_time_rate" in df.columns else None
    u_pt24 = None if u_pt_col is None else linear_trend_with_ci(df[u_pt_col], months=24)

    gr_peak = peak_in_window(df, col, "2007-01-01", "2009-12-01")
    p2020 = peak_in_window(df, col, "2020-01-01", "2020-12-01")

    # Save analysis table for downstream use
    out_path = config.PROCESSED_DIR / "analysis_summary.json"
    sources = {}
    for key, spec in config.SERIES.items():
        meta_path = config.METADATA_DIR / f"{key}.metadata.json"
        if meta_path.exists():
            meta = pd.read_json(meta_path, typ="series")
            sources[key] = {"url": spec.url, "downloaded_at_utc": str(meta.get("downloaded_at_utc"))}
        else:
            sources[key] = {"url": spec.url, "downloaded_at_utc": "(missing)"}

    summary = {
        "current_date": str(current_date.date()),
        "current_unemp_20_24": current_value,
        "percentile_rank_unemp_20_24": pct,
        "trend_24m": {
            "slope_per_month": trend24.slope_per_month,
            "ci95_lo": trend24.slope_ci95[0],
            "ci95_hi": trend24.slope_ci95[1],
        },
        "trend_60m": {
            "slope_per_month": trend60.slope_per_month,
            "ci95_lo": trend60.slope_ci95[0],
            "ci95_hi": trend60.slope_ci95[1],
        },
        "great_recession_peak": None if gr_peak is None else {"date": str(gr_peak[0].date()), "value": gr_peak[1]},
        "peak_2020": None if p2020 is None else {"date": str(p2020[0].date()), "value": p2020[1]},
        "gap_trend_24m": None
        if gap24 is None
        else {
            "slope_per_month": gap24.slope_per_month,
            "ci95_lo": gap24.slope_ci95[0],
            "ci95_hi": gap24.slope_ci95[1],
        },
        "underemployment_trend_24m": None
        if u_pt24 is None
        else {
            "slope_per_month": u_pt24.slope_per_month,
            "ci95_lo": u_pt24.slope_ci95[0],
            "ci95_hi": u_pt24.slope_ci95[1],
        },
        "sources": sources,
    }
    import json

    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    logger.info("Wrote %s", out_path)

    build_report(str(config.REPORT_FILE), summary)
    logger.info("Wrote %s", config.REPORT_FILE)


if __name__ == "__main__":
    main()
