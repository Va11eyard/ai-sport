"""Print and save the evidence used in the report.

Run from the project root:
    python scripts/verify.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from transfer_lab.optimize import brute_force, select  # noqa: E402


def main() -> int:
    processed = ROOT / "data" / "processed"
    tables = ROOT / "outputs" / "tables"
    outputs = ROOT / "outputs"

    players = pd.read_csv(processed / "sb_players.csv")
    matches = pd.read_csv(processed / "sb_matches.csv")
    pm = pd.read_csv(processed / "sb_player_matches.csv")
    cand = pd.read_csv(tables / "candidates.csv")
    scen = pd.read_csv(tables / "scenarios.csv")
    value = json.loads((outputs / "value_model_summary.json").read_text(encoding="utf-8"))
    decision = json.loads((outputs / "decision_summary.json").read_text(encoding="utf-8"))

    plan = select(cand, 50_000_000)
    check = brute_force(cand, 50_000_000)
    local_bt = pd.DataFrame(value["local_backtest"])

    lines = []
    lines.append("Assignment 5 verification")
    lines.append("")
    lines.append(f"StatsBomb matches: {len(matches)}")
    lines.append(f"StatsBomb players: {len(players)}")
    lines.append(f"Player-match rows: {len(pm):,}")
    lines.append(f"Market player-seasons: {len(pd.read_csv(processed / 'market_players.csv')):,}")
    lines.append("")
    lines.append("Global model (holdout 2021/22 to 2024/25)")
    for key in ("baseline_role_median", "ridge", "lightgbm"):
        m = value["global_metrics"][key]
        lines.append(f"  {key:22} MAE {m['mae']:.3f}  R2 {m['r2']:.3f}  Spearman {m['spearman']:.3f}")
    lines.append("")
    lines.append("Local model (5-fold out-of-fold, 2015/16 Premier League)")
    for key in ("baseline", "full"):
        m = value["local_metrics"][key]
        lines.append(f"  {key:22} MAE {m['mae']:.3f}  R2 {m['r2']:.3f}  Spearman {m['spearman']:.3f}")
    lines.append("")
    lines.append("Local backtest")
    lines.append(local_bt.round(3).to_string(index=False))
    lines.append("")
    lines.append("Candidate pool")
    lines.append(cand.groupby("need").size().to_string())
    lines.append("")
    lines.append("Base optimizer")
    lines.append(f"  cost EUR {plan['cost']/1e6:.1f}m, score {plan['score']:.2f}, leftover EUR {plan['leftover']/1e6:.1f}m")
    lines.append(f"  brute force score {check['score']:.2f}, match {abs(check['score']-plan['score']) < 1e-6}")
    lines.append("")
    lines.append("Recommended plan")
    for p in decision["recommended"]["players"]:
        lines.append(f"  {p['need']:2} {p['display_name']:18} {p['team_name']:18} EUR {p['market_value']/1e6:.1f}m")
    lines.append(
        f"  total EUR {decision['recommended']['cost_m']:.1f}m, "
        f"2-year value EUR {decision['recommended']['future_value_2y_m']:.1f}m, "
        f"growth {decision['recommended']['growth_2y_pct']:+.1f}%"
    )
    lines.append("")
    lines.append("Scenarios")
    lines.append(scen[["scenario", "feasible", "cost_m", "leftover_m", "score", "players"]].to_string(index=False))
    lines.append("")
    for name in ("report/Assignment5_Report.pdf", "presentation/Assignment5_Presentation.pdf"):
        path = ROOT / name
        lines.append(f"{name}: {'present' if path.exists() else 'missing'}")
    text = "\n".join(lines)
    (outputs / "verification.txt").write_text(text, encoding="utf-8")
    print(text)

    tests = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT)
    return tests.returncode


if __name__ == "__main__":
    raise SystemExit(main())
