import pandas as pd

from src.utils import assert_monthly_continuity, assert_no_duplicate_dates, read_fred_csv


def test_read_fred_csv_parses_dates_and_values(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("observation_date,ABC\n2020-01-01,1.5\n2020-02-01,.\n")
    df = read_fred_csv(p, value_col="ABC")
    assert list(df.columns) == ["date", "value"]
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["value"].isna().iloc[1]


def test_monthly_continuity_passes_for_complete_range():
    df = pd.DataFrame({"date": pd.date_range("2020-01-01", "2020-06-01", freq="MS")})
    assert_monthly_continuity(df)


def test_duplicate_dates_raises():
    df = pd.DataFrame({"date": ["2020-01-01", "2020-01-01"]})
    df["date"] = pd.to_datetime(df["date"])
    try:
        assert_no_duplicate_dates(df)
        assert False, "expected ValueError"
    except ValueError:
        assert True
