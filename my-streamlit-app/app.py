"""Streamlit entrypoint.

Run from this folder:
  streamlit run app.py

This keeps the CLI simple and avoids path/import issues.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_syspath() -> None:
    repo_root = Path(__file__).resolve().parent
    src_dir = repo_root / "src"
    sys.path.insert(0, str(src_dir))


_ensure_src_on_syspath()

# Import after sys.path update.
import app as app_module  # type: ignore  # noqa: E402


if __name__ == "__main__":
    app_module.main()
