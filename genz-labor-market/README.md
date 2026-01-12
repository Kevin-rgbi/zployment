# Gen Z Labor Market: Unemployment vs Underemployment

## Problem statement
This project answers:

> “Is Gen Z underemployed, facing historic unemployment, gaining ground in getting jobs, or something else?”

It builds a fully reproducible, resume-ready pipeline that downloads public labor market time series (no API keys, no paid datasets), constructs a clean monthly dataset, computes interpretable metrics, and produces a short report + figures.

## Cohort definition (explicit)
- **Primary cohort (Gen Z early-career proxy):** ages **20–24**
- **Secondary cohort (youth context):** ages **16–24**
- **Comparators (gap analysis):** **25–34** and **35–44**

## Metrics produced
Monthly (from FRED keyless CSV endpoints):
1. **Unemployment rate (U-3)** for 20–24 and 16–24 (and comparators 25–34, 35–44)
2. **Labor force participation rate (LFPR)** for 20–24
3. **Employment rate (two common definitions)**
   - **Employment rate within the labor force** (sometimes what people mean informally): `100 - unemployment_rate`.
   - **Employment-population ratio (EPOP)**: `employed_20_24 / population_20_24 * 100` (computed from FRED employment + population levels).
3. **Underemployment proxy**: “involuntary part-time rate”
   - Definition: `part_time_for_economic_reasons / employed`.
   - **Important note:** in this environment, direct BLS downloads and BLS HTML tables are blocked (Access Denied). The pipeline therefore defaults to an **overall** involuntary part-time rate (all ages) as a documented fallback.
4. Recommended context series:
   - **U-6** (overall)
   - **Median weekly earnings (quarterly)**: 20–24 vs 25–34

## Data sources
All data comes from **FRED** keyless CSV endpoints (HTTP download):

- FRED CSV template: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES_ID>`
- Series IDs are defined and documented in `src/config.py`.

Each download writes a metadata JSON file (URL + download date + sha256) under `data/metadata/`.

## Repo layout
- `src/` pipeline modules with `python -m src.<module>` entrypoints
- `data/raw/` raw downloads (one CSV per series)
- `data/processed/` analytic datasets
- `reports/figures/` saved charts
- `reports/genz_labor_market_report.md` generated narrative report
- `dashboard/` optional Streamlit app
- `tests/` pytest unit tests

## How to run end-to-end
From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m src.fetch_sources
python -m src.clean
python -m src.features
python -m src.analysis
python -m src.viz

pytest -q
```

Optional dashboard:

```bash
streamlit run streamlit_app.py
```

(You can still run `streamlit run dashboard/app.py`; `streamlit_app.py` is just a convenient repo-root entrypoint.)

## Outputs you’ll get
- Processed monthly dataset: `data/processed/monthly_labor_market.csv`
- Earnings dataset (quarterly): `data/processed/earnings_quarterly.csv`
- Report: `reports/genz_labor_market_report.md`
- Figures: `reports/figures/*.png`

## Sample figures
After you run the pipeline, see:
- `reports/figures/01_unemployment_by_age.png`
- `reports/figures/02_unemployment_hist_percentile.png`
- `reports/figures/03_involuntary_part_time_rate.png`
- `reports/figures/04_lfpr_20_24.png`
- `reports/figures/05_earnings_20_24_vs_25_34.png`

## Resume bullets (template; do not paste numbers you didn’t compute)
- Built a reproducible Python data pipeline (pandas/requests) to quantify early-career Gen Z labor-market outcomes using public FRED labor statistics; produced a clean monthly analytic dataset and automated quality checks.
- Implemented interpretable time-series analytics (historic percentiles, rolling z-scores, 24/60-month trends with confidence intervals) and cohort gap analysis to contextualize unemployment dynamics.
- Authored an end-to-end reporting workflow that generates figures and a markdown report from raw sources with metadata provenance (source URLs, download timestamps, sha256 checksums).
