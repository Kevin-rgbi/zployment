from __future__ import annotations

import subprocess
import sys


def run(module: str) -> None:
    cmd = [sys.executable, "-m", module]
    print("\n$", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    for module in [
        "src.fetch_sources",
        "src.clean",
        "src.features",
        "src.analysis",
        "src.viz",
    ]:
        run(module)


if __name__ == "__main__":
    main()
