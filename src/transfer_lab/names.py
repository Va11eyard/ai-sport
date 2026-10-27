from __future__ import annotations

import json

import pandas as pd

from .config import OUTPUTS, TABLES

KNOWN = {
    "Francis Joseph Coquelin": "Francis Coquelin",
    "Odion Jude Ighalo": "Odion Ighalo",
    "Idrissa Gana Gueye": "Idrissa Gueye",
    "José Ramiro Funes Mori": "Ramiro Funes Mori",
    "Christian Benteke Liolo": "Christian Benteke",
    "Yann Gérard M'Vila": "Yann M'Vila",
    "Andrew Philip King": "Andy King",
    "José Leonardo Ulloa": "Leonardo Ulloa",
    "Marcin Ryszard Wasilewski": "Marcin Wasilewski",
    "Gilbert Gianelli Imbula Wanga": "Giannelli Imbula",
    "Pedro Mba Obiang Avomo": "Pedro Obiang",
    "Tetchi Jores Charlemagne Ulrich Okore": "Jores Okore",
    "Chancel Mbemba Mangulu": "Chancel Mbemba",
    "José Salomón Rondón Giménez": "Salomón Rondón",
    "Enner Remberto Valencia Lastra": "Enner Valencia",
    "José Luis Sanmartín Mato": "Joselu",
    "André Ayew Pelé": "André Ayew",
    "Sergio Leonel Agüero del Castillo": "Sergio Agüero",
    "Romelu Lukaku Menama": "Romelu Lukaku",
    "Faustino Marcos Alberto Rojo": "Marcos Rojo",
    "Cheik Ismaël Tioté": "Cheik Tioté",
    "Bafétimbi Gomis": "Bafétimbi Gomis",
    "Dame N''Doye": "Dame N'Doye",
}


def clean_name(name: object) -> str:
    value = str(name).replace("''", "'")
    return KNOWN.get(value, value)


def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ("display_name", "player_name", "tm_player_name", "sb_player_name"):
        if col in out.columns:
            out[col] = out[col].map(clean_name)
    return out


PLANS = {
    "recommended": "shortlist_safety_first.csv",
    "value": "shortlist_base.csv",
    "fit": "shortlist_quality_first.csv",
}


def build_decision() -> pd.DataFrame:
    backtest = pd.read_csv(TABLES / "case_backtest_players.csv")
    keep = ["player_id", "value_1y", "value_2y", "growth_1y", "growth_2y"]
    rows = []
    for plan, file in PLANS.items():
        path = TABLES / file
        if not path.exists():
            continue
        sel = pd.read_csv(path)
        sel = sel.merge(backtest[keep], on="player_id", how="left")
        sel["plan"] = plan
        sel["display_name"] = sel["display_name"].map(clean_name)
        rows.append(sel)
    out = pd.concat(rows, ignore_index=True)
    cols = [
        "plan",
        "need",
        "display_name",
        "team_name",
        "age",
        "market_value",
        "fit",
        "value",
        "safety",
        "score_w",
        "value_1y",
        "value_2y",
        "growth_2y",
    ]
    out = out[[c for c in cols if c in out.columns]]
    out.to_csv(TABLES / "decision.csv", index=False)
    return out


def summarize_plans(decision: pd.DataFrame) -> dict:
    summary = {}
    for plan, group in decision.groupby("plan"):
        cost = float(group["market_value"].sum())
        future = float(group["value_2y"].sum()) if group["value_2y"].notna().all() else None
        summary[plan] = {
            "players": group[["need", "display_name", "team_name", "market_value", "fit", "value", "safety", "score_w"]].round(2).to_dict(orient="records"),
            "cost": cost,
            "cost_m": round(cost / 1e6, 2),
            "future_value_2y": future,
            "future_value_2y_m": round(future / 1e6, 2) if future else None,
            "growth_2y_pct": round((future / cost - 1) * 100, 1) if future else None,
            "leftover": 50_000_000 - cost,
        }
    return summary


def main() -> dict:
    decision = build_decision()
    summary = summarize_plans(decision)
    (OUTPUTS / "decision_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


if __name__ == "__main__":
    main()
