import numpy as np
import pandas as pd

from src.analysis import linear_trend_with_ci, percentile_rank, rolling_zscore


def test_percentile_rank_basic():
    s = pd.Series([1, 2, 3, 4])
    assert percentile_rank(s, 2) == 0.5


def test_rolling_zscore_outputs_series():
    s = pd.Series(range(100))
    z = rolling_zscore(s, window=20)
    assert len(z) == 100


def test_linear_trend_positive_slope():
    s = pd.Series(np.arange(60, dtype=float))
    res = linear_trend_with_ci(s, months=60)
    assert res.slope_per_month > 0
