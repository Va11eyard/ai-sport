from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

from .config import OUTPUTS, TABLES

DEFAULT_WEIGHTS = {"fit": 0.55, "value": 0.25, "safety": 0.20}


def _score(df: pd.DataFrame, weights: dict) -> pd.Series:
    return df["fit"] * weights["fit"] + df["value"] * weights["value"] + df["safety"] * weights["safety"]


def select(
    candidates: pd.DataFrame,
    budget: float = 50_000_000,
    weights: dict | None = None,
    max_risk: float = 70,
    max_age: int = 29,
    require_all: bool = True,
) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    pool = candidates[(candidates["risk"] <= max_risk) & (candidates["age"] <= max_age)].copy()
    pool["score_w"] = _score(pool, weights)
    needs = sorted(pool["need"].unique())
    if pool.empty or not needs:
        return {"feasible": False, "reason": "no candidates after filters", "selected": pd.DataFrame()}

    index = list(pool.index)
    n = len(index)
    cost = pool["market_value"].to_numpy() / 1e6
    score = pool["score_w"].to_numpy()
    need_matrix = np.zeros((len(needs), n))
    for i, need in enumerate(needs):
        need_matrix[i] = (pool["need"] == need).astype(float).to_numpy()

    if require_all:
        rows = [LinearConstraint(need_matrix, lb=1, ub=1), LinearConstraint(cost, lb=-np.inf, ub=budget / 1e6)]
        constraints = rows
    else:
        rows = [LinearConstraint(need_matrix, lb=0, ub=1), LinearConstraint(cost, lb=-np.inf, ub=budget / 1e6)]
        rows.append(LinearConstraint(np.ones((1, n)), lb=1, ub=len(needs)))
        constraints = rows

    res = milp(
        c=-score,
        integrality=np.ones(n),
        bounds=Bounds(0, 1),
        constraints=constraints,
        options={"time_limit": 30},
    )
    if not res.success:
        if require_all:
            relaxed = select(
                candidates,
                budget=budget,
                weights=weights,
                max_risk=max_risk,
                max_age=max_age,
                require_all=False,
            )
            relaxed["relaxed"] = True
            return relaxed
        return {"feasible": False, "reason": str(res.message), "selected": pd.DataFrame()}

    chosen = pool.loc[np.array(index)[res.x > 0.5]].copy()
    chosen = chosen.sort_values("need")
    return {
        "feasible": True,
        "relaxed": not require_all,
        "selected": chosen,
        "cost": float(chosen["market_value"].sum()),
        "score": float(chosen["score_w"].sum()),
        "leftover": float(budget - chosen["market_value"].sum()),
        "needs_filled": int(chosen["need"].nunique()),
        "budget": float(budget),
        "weights": weights,
        "max_risk": max_risk,
        "max_age": max_age,
    }


def brute_force(candidates: pd.DataFrame, budget: float, weights: dict | None = None, top_n: int = 8) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    pool = candidates.copy()
    pool["score_w"] = _score(pool, weights)
    groups = []
    for need, group in pool.groupby("need"):
        groups.append(list(group.sort_values("score_w", ascending=False).head(top_n).index))
    best = None
    for combo in itertools.product(*groups):
        rows = pool.loc[list(combo)]
        if rows["market_value"].sum() > budget:
            continue
        value = rows["score_w"].sum()
        if best is None or value > best["score"]:
            best = {"score": float(value), "cost": float(rows["market_value"].sum()), "names": rows["display_name"].tolist(), "needs": rows["need"].tolist()}
    return best or {}


def scenarios(candidates: pd.DataFrame) -> pd.DataFrame:
    plans = [
        ("base", 50_000_000, DEFAULT_WEIGHTS, 70, 29),
        ("value_first", 50_000_000, {"fit": 0.35, "value": 0.45, "safety": 0.20}, 70, 29),
        ("quality_first", 50_000_000, {"fit": 0.75, "value": 0.10, "safety": 0.15}, 70, 29),
        ("safety_first", 50_000_000, {"fit": 0.40, "value": 0.20, "safety": 0.40}, 70, 29),
        ("budget_minus_20", 40_000_000, DEFAULT_WEIGHTS, 70, 29),
        ("budget_minus_40", 30_000_000, DEFAULT_WEIGHTS, 70, 29),
        ("youth_policy", 50_000_000, DEFAULT_WEIGHTS, 70, 24),
        ("risk_averse", 50_000_000, DEFAULT_WEIGHTS, 45, 29),
    ]
    rows = []
    for name, budget, weights, max_risk, max_age in plans:
        result = select(candidates, budget, weights, max_risk, max_age)
        sel = result.get("selected", pd.DataFrame())
        rows.append(
            {
                "scenario": name,
                "feasible": result.get("feasible", False),
                "relaxed": result.get("relaxed", False),
                "budget_m": budget / 1e6,
                "max_risk": max_risk,
                "max_age": max_age,
                "weights": json.dumps(weights),
                "cost_m": result.get("cost", np.nan) / 1e6 if result.get("feasible") else np.nan,
                "leftover_m": result.get("leftover", np.nan) / 1e6 if result.get("feasible") else np.nan,
                "score": result.get("score", np.nan),
                "needs_filled": result.get("needs_filled", 0),
                "players": "; ".join(f"{r['need']}: {r['display_name']} ({r['market_value']/1e6:.1f}m)" for _, r in sel.iterrows()) if len(sel) else "",
            }
        )
        if result.get("feasible"):
            sel.to_csv(TABLES / f"shortlist_{name}.csv", index=False)
    table = pd.DataFrame(rows)
    table.to_csv(TABLES / "scenarios.csv", index=False)
    return table


def sensitivity(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fit in np.arange(0.30, 0.81, 0.05):
        value = round(1 - fit - 0.20, 2)
        if value < 0:
            continue
        weights = {"fit": round(float(fit), 2), "value": value, "safety": 0.20}
        result = select(candidates, 50_000_000, weights)
        sel = result.get("selected", pd.DataFrame())
        rows.append(
            {
                "fit_weight": weights["fit"],
                "value_weight": weights["value"],
                "safety_weight": weights["safety"],
                "feasible": result.get("feasible", False),
                "cost_m": result.get("cost", np.nan) / 1e6 if result.get("feasible") else np.nan,
                "CM": "; ".join(sel[sel["need"] == "CM"]["display_name"]) if len(sel) else "",
                "CB": "; ".join(sel[sel["need"] == "CB"]["display_name"]) if len(sel) else "",
                "ST": "; ".join(sel[sel["need"] == "ST"]["display_name"]) if len(sel) else "",
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(TABLES / "sensitivity.csv", index=False)
    return table


def run() -> dict:
    candidates = pd.read_csv(TABLES / "candidates.csv")
    table = scenarios(candidates)
    sens = sensitivity(candidates)
    base = select(candidates)
    check = brute_force(candidates, 50_000_000)
    out = {
        "scenarios": table.to_dict(orient="records"),
        "base": {
            "cost": base.get("cost"),
            "score": base.get("score"),
            "leftover": base.get("leftover"),
            "players": base.get("selected", pd.DataFrame())[["need", "display_name", "team_name", "market_value", "fit", "value", "safety", "score_w"]].to_dict(orient="records") if base.get("feasible") else [],
        },
        "brute_force_check": check,
        "sensitivity_rows": len(sens),
    }
    (OUTPUTS / "optimizer_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    out = run()
    print(pd.DataFrame(out["scenarios"])[["scenario", "feasible", "cost_m", "leftover_m", "score", "players"]].to_string(index=False))
    print("\nBASE", json.dumps(out["base"], indent=2, ensure_ascii=False))
    print("\nBRUTE", out["brute_force_check"])
