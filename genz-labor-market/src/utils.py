from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
import requests


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_to_file(url: str, out_path: Path, timeout_s: int = 30) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout_s) as r:
        r.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)


def write_metadata_json(
    *,
    dataset_key: str,
    source_url: str,
    out_csv_path: Path,
    metadata_dir: Path,
    extra: Mapping[str, object] | None = None,
) -> Path:
    metadata_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "dataset_key": dataset_key,
        "source_url": source_url,
        "downloaded_at_utc": utc_now_iso(),
        "local_path": str(out_csv_path),
        "sha256": sha256_file(out_csv_path),
    }
    if extra:
        meta.update(dict(extra))
    out_path = metadata_dir / f"{dataset_key}.metadata.json"
    out_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    return out_path


def read_fred_csv(path: Path, value_col: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "observation_date" not in df.columns or value_col not in df.columns:
        raise ValueError(f"Unexpected FRED CSV schema in {path.name}: {df.columns.tolist()}")
    out = df.rename(columns={"observation_date": "date", value_col: "value"})
    out["date"] = pd.to_datetime(out["date"], utc=False)
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out


def assert_monthly_continuity(df: pd.DataFrame, date_col: str = "date") -> None:
    if df.empty:
        raise ValueError("DataFrame is empty")
    dates = pd.to_datetime(df[date_col]).sort_values().dropna().unique()
    if len(dates) < 2:
        return
    expected = pd.date_range(dates[0], dates[-1], freq="MS")
    missing = expected.difference(pd.DatetimeIndex(dates))
    if len(missing) > 0:
        raise ValueError(f"Monthly continuity check failed; missing {len(missing)} months")


def assert_no_duplicate_dates(df: pd.DataFrame, date_col: str = "date") -> None:
    dupes = df[date_col].duplicated().sum()
    if dupes:
        raise ValueError(f"Found {dupes} duplicated {date_col} values")


def assert_schema(df: pd.DataFrame, required_cols: Iterable[str]) -> None:
    required = list(required_cols)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def stable_sort_columns(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    cols = [date_col] + sorted([c for c in df.columns if c != date_col])
    return df.loc[:, cols]
