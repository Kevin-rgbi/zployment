# Gen Z Labor Market Report (Reproducible)
## Executive summary
This report is generated from public FRED time series (no API keys). All statistics below are computed from the downloaded data as of 2025-11-01.
## Metric definitions
- **Unemployment rate (U-3)**: unemployed / labor force (percent).
- **LFPR (20–24)**: labor force / population (percent).
- **Underemployment proxy (involuntary part-time rate)**: part-time for economic reasons / employed. In this environment we compute the **overall** rate as a documented fallback (BLS endpoints blocked).
## Data sources (URLs + download dates)
Pipeline writes one metadata JSON per dataset under `data/metadata/`.
- **unemp_rate_20_24**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNS14000036 (downloaded_at_utc: 2026-01-05T13:53:58+00:00)
- **unemp_rate_16_24**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNS14024887 (downloaded_at_utc: 2026-01-05T13:53:59+00:00)
- **unemp_rate_25_34**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNS14000089 (downloaded_at_utc: 2026-01-05T13:54:00+00:00)
- **unemp_rate_35_44**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNS14000091 (downloaded_at_utc: 2026-01-05T13:54:02+00:00)
- **lfpr_20_24**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNS11300036 (downloaded_at_utc: 2026-01-05T13:54:03+00:00)
- **u6_overall**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=U6RATE (downloaded_at_utc: 2026-01-05T13:54:04+00:00)
- **employed_20_24**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNS12000036 (downloaded_at_utc: 2026-01-05T13:54:04+00:00)
- **population_20_24**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNU00000036 (downloaded_at_utc: 2026-01-05T13:54:04+00:00)
- **employed_overall**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=CE16OV (downloaded_at_utc: 2026-01-05T13:54:05+00:00)
- **pt_econ_reasons_overall**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LNU02032194 (downloaded_at_utc: 2026-01-05T13:54:07+00:00)
- **earnings_20_24_q**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LEU0252887100Q (downloaded_at_utc: 2026-01-05T13:54:08+00:00)
- **earnings_25_34_q**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=LEU0252888500Q (downloaded_at_utc: 2026-01-05T13:54:08+00:00)
- **cpi_u**: https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL (downloaded_at_utc: 2026-01-05T13:54:09+00:00)

## Methodology
### Historic benchmark (unemployment_20_24)
- **Percentile rank**: fraction of historical months with value ≤ current.
- **Peaks**: max within 2007–2009 window and within 2020 calendar year.
- **Rolling z-score**: 60-month rolling standard score.

### Gaining ground
- **Trend**: simple linear trend over last 24 and 60 months with 95% CI.
- **Gap analysis**: (20–24 minus 25–34) unemployment rate.

## Key findings (populated after execution)
- **Unemployment (20–24)** is **8.3%** and sits at the **38th percentile** of its historical monthly distribution.
- **Great Recession peak (20–24)**: 16.0% (2009-11-01).
- **2020 peak (20–24)**: 25.5% (2020-04-01).
- **24-month trend (20–24 unemployment)**: +0.094 pp/month (95% CI: [+0.069, +0.118]).
- **60-month trend (20–24 unemployment)**: -0.022 pp/month (95% CI: [-0.040, -0.005]).
- **Cohort gap (20–24 minus 25–34), 24-month trend**: +0.076 pp/month (95% CI: [+0.052, +0.101]).
- **Underemployment proxy (overall involuntary part-time rate), 24-month trend**: +0.0001 per month (95% CI: [+0.0000, +0.0002]).

## Limitations
- Age cohorts are proxies for Gen Z and do not capture education status or enrollment.
- Seasonality and survey design changes can affect comparability across decades.
- Underemployment by age ideally uses age-specific ‘part-time for economic reasons’ numerator; BLS access restrictions in this environment force an overall-rate fallback.

## Reproducibility
Run:
```bash
python -m src.fetch_sources
python -m src.clean
python -m src.features
python -m src.analysis
python -m src.viz
```
