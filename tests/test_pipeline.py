from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from transfer_lab.config import OUTPUTS, PROCESSED, TABLES
from transfer_lab.optimize import brute_force, select
from transfer_lab.value_model import GLOBAL_CAT, GLOBAL_NUM, LOCAL_BASE, LOCAL_EVENTS


ROOT = Path(__file__).resolve().parents[1]


def test_statsbomb_counts():
    players = pd.read_csv(PROCESSED / "sb_players.csv")
    matches = pd.read_csv(PROCESSED / "sb_matches.csv")
    player_matches = pd.read_csv(PROCESSED / "sb_player_matches.csv")
    assert len(matches) == 380
    assert len(players) == 548
    assert len(player_matches) == 10385
    lei = pd.read_csv(PROCESSED / "sb_team_matches.csv")
    assert len(lei[lei["team_name"] == "Leicester City"]) == 38


def test_kante_profile():
    players = pd.read_csv(PROCESSED / "sb_players.csv")
    kante = players[players["player_name"].str.contains("Kant", na=False)].iloc[0]
    assert 3000 < kante["minutes"] < 3030
    assert kante["ball_winning_p90"] > 16
    assert kante["pressures_p90"] > 25


def test_mapping_and_candidates():
    mapping = pd.read_csv(PROCESSED / "player_map.csv")
    kante = mapping[mapping["sb_player_name"].str.contains("Kant", na=False)].iloc[0]
    assert int(kante["tm_player_id"]) == 225083
    cand = pd.read_csv(TABLES / "candidates.csv")
    counts = cand.groupby("need").size().to_dict()
    assert counts["CM"] >= 15
    assert counts["CB"] >= 10
    assert counts["ST"] >= 6
    assert cand["market_value"].min() >= 1_000_000
    assert cand["market_value"].max() <= 30_000_000
    assert (cand["minutes"] >= 1500).all()


def test_value_model_beats_baseline():
    summary = json.loads((OUTPUTS / "value_model_summary.json").read_text(encoding="utf-8"))
    g = summary["global_metrics"]
    l = summary["local_metrics"]
    assert g["lightgbm"]["r2"] > g["baseline_role_median"]["r2"] + 0.2
    assert g["lightgbm"]["mae"] < g["baseline_role_median"]["mae"]
    assert l["full"]["r2"] > l["baseline"]["r2"]
    assert l["full"]["mae"] < l["baseline"]["mae"]


def test_no_future_columns_in_features():
    forbidden = {"market_value", "future_value", "value_1y", "value_2y", "growth_2y", "local_discount_pct"}
    assert not forbidden & set(GLOBAL_NUM + GLOBAL_CAT)
    assert not forbidden & set(LOCAL_BASE + LOCAL_EVENTS)


def test_optimizer_respects_budget_and_needs():
    cand = pd.read_csv(TABLES / "candidates.csv")
    plan = select(cand, 50_000_000)
    assert plan["feasible"]
    sel = plan["selected"]
    assert set(sel["need"]) == {"CM", "CB", "ST"}
    assert sel["market_value"].sum() <= 50_000_000
    check = brute_force(cand, 50_000_000)
    assert abs(check["score"] - plan["score"]) < 1e-6


def test_low_budget_relaxes_or_fails_cleanly():
    cand = pd.read_csv(TABLES / "candidates.csv")
    plan = select(cand, 12_000_000)
    assert not plan["feasible"] or plan["cost"] <= 12_000_000


def test_scenarios_and_decision():
    scen = pd.read_csv(TABLES / "scenarios.csv")
    assert scen["feasible"].all()
    assert (scen["cost_m"] <= scen["budget_m"] + 1e-9).all()
    dec = json.loads((OUTPUTS / "decision_summary.json").read_text(encoding="utf-8"))
    rec = dec["recommended"]
    assert rec["cost_m"] == 24.0
    assert {p["display_name"] for p in rec["players"]} == {"Steve Cook", "Idrissa Gueye", "Odion Ighalo"}


def test_generated_text_rules():
    paths = [ROOT / "README.md", ROOT / "report" / "report.html", ROOT / "presentation" / "presentation.html"]
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert "\u2014" not in text, f"em dash in {path}"
        assert "\u2192" not in text, f"arrow glyph in {path}"
