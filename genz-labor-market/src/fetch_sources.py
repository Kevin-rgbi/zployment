from __future__ import annotations

import logging
from pathlib import Path

from . import config
from .utils import download_to_file, ensure_dirs, setup_logging, write_metadata_json


logger = logging.getLogger(__name__)


def fetch_one(key: str, out_dir: Path) -> Path:
    spec = config.SERIES[key]
    out_path = out_dir / f"{key}__{spec.series_id}.csv"
    logger.info("Downloading %s (%s)", key, spec.series_id)
    download_to_file(spec.url, out_path)
    write_metadata_json(
        dataset_key=key,
        source_url=spec.url,
        out_csv_path=out_path,
        metadata_dir=config.METADATA_DIR,
        extra={
            "series_id": spec.series_id,
            "name": spec.name,
            "frequency": spec.frequency,
            "units": spec.units,
        },
    )
    return out_path


def main() -> None:
    setup_logging()
    ensure_dirs(config.RAW_DIR, config.METADATA_DIR, config.INTERIM_DIR, config.PROCESSED_DIR)

    # Download all configured series.
    for key in config.SERIES.keys():
        fetch_one(key, config.RAW_DIR)

    logger.info("Done. Raw files in %s", config.RAW_DIR)


if __name__ == "__main__":
    main()
