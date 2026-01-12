from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_data() -> pd.DataFrame:
    repo_root = Path(__file__).resolve().parents[1]
    features_path = repo_root / "data" / "processed" / "monthly_labor_market_features.csv"
    df = pd.read_csv(features_path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _latest_and_change(df: pd.DataFrame, col: str, months: int) -> tuple[float | None, float | None]:
    s = df[["date", col]].dropna().sort_values("date")
    if s.empty:
        return None, None
    latest = float(s[col].iloc[-1])
    if len(s) <= months:
        return latest, None
    prev = float(s[col].iloc[-(months + 1)])
    return latest, latest - prev


def main() -> None:
    st.set_page_config(page_title="Gen Z Labor Market Dashboard", layout="wide")
    st.title("Gen Z Labor Market Dashboard")
    st.caption("Reproducible, keyless pipeline using public FRED series")

    try:
        df = load_data()
    except FileNotFoundError:
        st.error("Missing required file: data/processed/monthly_labor_market_features.csv")
        st.write("Run the pipeline first from the repo root:")
        st.code(
            "python -m src.fetch_sources\n"
            "python -m src.clean\n"
            "python -m src.features\n"
            "python -m src.analysis\n"
            "python -m src.viz\n",
            language="bash",
        )
        st.stop()

    min_date, max_date = df["date"].min(), df["date"].max()
    start, end = st.date_input(
        "Date range",
        value=(max_date.date() - pd.DateOffset(years=10), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )
    mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
    view = df.loc[mask].copy()

    st.subheader("Headlines")
    kpi_cols = st.columns(4)
    kpis = [
        ("Unemployment (20–24)", "unemp_rate_20_24", "pp"),
        ("EPOP (20–24)", "epop_20_24", "pp"),
        ("Employment rate in LF (20–24)", "employment_rate_lf_20_24", "pp"),
        ("LFPR (20–24)", "lfpr_20_24", "pp"),
    ]
    for i, (label, col, unit) in enumerate(kpis):
        latest, delta12 = _latest_and_change(df, col, months=12)
        if latest is None:
            kpi_cols[i].metric(label, value="NA")
        else:
            delta_str = None if delta12 is None else f"{delta12:+.2f} {unit} (YoY)"
            kpi_cols[i].metric(label, value=f"{latest:.2f}", delta=delta_str)

    st.subheader("Charts")
    preset = st.selectbox(
        "Quick view",
        [
            "Unemployment by cohort",
            "Employment + participation (20–24)",
            "Underemployment proxy (overall)",
            "Custom",
        ],
    )

    if preset == "Unemployment by cohort":
        metrics = ["unemp_rate_20_24", "unemp_rate_16_24", "unemp_rate_25_34", "unemp_rate_35_44"]
    elif preset == "Employment + participation (20–24)":
        metrics = ["epop_20_24", "employment_rate_lf_20_24", "lfpr_20_24", "unemp_rate_20_24"]
    elif preset == "Underemployment proxy (overall)":
        metrics = ["involuntary_part_time_rate", "unemp_rate_20_24", "u6_overall"]
    else:
        metrics = st.multiselect(
            "Metrics",
            [
                "unemp_rate_20_24",
                "unemp_rate_16_24",
                "unemp_rate_25_34",
                "unemp_rate_35_44",
                "lfpr_20_24",
                "employment_rate_lf_20_24",
                "epop_20_24",
                "u6_overall",
                "involuntary_part_time_rate",
                "unemp_gap_20_24_minus_25_34",
            ],
            default=["unemp_rate_20_24"],
        )

    if metrics:
        st.line_chart(view.set_index("date")[metrics])
    else:
        st.info("Select at least one metric to plot.")

    with st.expander("Data preview (latest 24 rows)"):
        st.dataframe(df.sort_values("date").tail(24), use_container_width=True)

    st.subheader("Notes")
    st.write(
        "Underemployment is computed as an overall fallback (BLS access restricted in this environment). "
        "See `src/config.py` and the generated report for details."
    )


if __name__ == "__main__":
    main()
