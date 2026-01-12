import numpy as np
import pandas as pd

from src.features import add_features, compute_involuntary_part_time_rate


def base_df():
    dates = pd.date_range("2020-01-01", "2020-03-01", freq="MS")
    return pd.DataFrame(
        {
            "date": dates,
            "unemp_rate_20_24": [10.0, 9.0, 8.0],
            "unemp_rate_16_24": [12.0, 11.0, 10.0],
            "unemp_rate_25_34": [5.0, 4.5, 4.0],
            "unemp_rate_35_44": [4.0, 3.5, 3.0],
            "lfpr_20_24": [70.0, 70.2, 70.1],
            "u6_overall": [14.0, 13.0, 12.0],
            "employed_20_24": [100.0, 100.0, 100.0],
            "population_20_24": [200.0, 200.0, 200.0],
            "employed_overall": [1000.0, 1000.0, 1000.0],
            "pt_econ_reasons_overall": [50.0, 40.0, 30.0],
        }
    )


def test_underemployment_proxy_calc_overall_fallback():
    df = base_df()
    rate = compute_involuntary_part_time_rate(df)
    assert np.allclose(rate.values, np.array([0.05, 0.04, 0.03]))


def test_add_features_creates_gap_columns_and_rate():
    df = base_df()
    out = add_features(df)
    assert "unemp_gap_20_24_minus_25_34" in out.columns
    assert "involuntary_part_time_rate" in out.columns
    assert "employment_rate_lf_20_24" in out.columns
    assert "epop_20_24" in out.columns
    assert np.isclose(out["unemp_gap_20_24_minus_25_34"].iloc[0], 5.0)
    assert np.isclose(out["employment_rate_lf_20_24"].iloc[0], 90.0)
    assert np.isclose(out["epop_20_24"].iloc[0], 50.0)


def test_missingness_handling_does_not_inf():
    df = base_df()
    df.loc[0, "employed_overall"] = 0.0
    out = add_features(df)
    assert np.isnan(out["involuntary_part_time_rate"].iloc[0])


def test_reproducibility_same_input_same_output():
    df = base_df()
    out1 = add_features(df)
    out2 = add_features(df)
    pd.testing.assert_frame_equal(out1, out2)
