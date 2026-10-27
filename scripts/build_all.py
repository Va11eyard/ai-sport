"""Build every processed table, model, figure and decision artifact.

Run from the project root:
    python scripts/build_all.py

Raw data must be downloaded first with scripts/download_data.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer_lab import names, optimize, plots, scouting, statsbomb, tm, value_model  # noqa: E402


def main() -> None:
    required = [
        ROOT / "data" / "raw" / "statsbomb" / "matches" / "premier_league_1516.json",
        ROOT / "data" / "raw" / "transfermarkt" / "player_performances.csv",
        ROOT / "data" / "raw" / "transfermarkt" / "player_market_value.csv",
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("Missing raw data. Run scripts/download_data.py first.")
        for path in missing:
            print(f"  {path}")
        raise SystemExit(1)

    print("1/8 StatsBomb events", flush=True)
    statsbomb.build()
    print("2/8 Transfermarkt market table", flush=True)
    tm.build_market_dataset()
    print("3/8 Case table and player mapping", flush=True)
    tm.build_case_dataset()
    print("4/8 Value models", flush=True)
    value_model.run()
    print("5/8 Candidate scores", flush=True)
    scouting.build_candidates()
    print("6/8 Budget optimisation", flush=True)
    optimize.run()
    print("7/8 Decision summary", flush=True)
    names.main()
    print("8/8 Figures", flush=True)
    plots.make_all()
    print("Done")


if __name__ == "__main__":
    main()
