from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .config import NEEDS, OUTPUTS, PROCESSED, TABLES

MIN_MINUTES = 1500
MAX_VALUE = 30_000_000
MIN_VALUE = 1_000_000
CLUSTER_FEATURES = [
    "ball_winning_p90",
    "pressures_p90",
    "progressive_passes_p90",
    "progressive_carries_p90",
    "xg_p90",
    "shots_p90",
    "touches_box_p90",
    "clearances_p90",
    "aerials_lost_p90",
    "pass_completion",
]
FEATURE_LABEL = {
    "ball_winning_p90": "Ball winning",
    "pressures_p90": "Pressing",
    "progressive_passes_p90": "Progressive passing",
    "progressive_carries_p90": "Carrying",
    "xg_p90": "Box threat",
    "shots_p90": "Shooting",
    "touches_box_p90": "Box presence",
    "clearances_p90": "Clearing",
    "aerials_lost_p90": "Aerial duels",
    "pass_completion": "Passing security",
}
PROFILE_WEIGHTS = {
    "CB": {
        "clearances_p90": 0.20,
        "blocks_p90": 0.15,
        "interceptions_p90": 0.12,
        "recoveries_p90": 0.08,
        "aerials_lost_p90": -0.10,
        "progressive_passes_p90": 0.15,
        "pass_completion": 0.10,
        "minutes_pct": 0.10,
    },
    "ST": {
        "xg_p90": 0.30,
        "shots_p90": 0.15,
        "touches_box_p90": 0.15,
        "progressive_carries_p90": 0.10,
        "pressures_p90": 0.10,
        "pass_completion": 0.05,
        "minutes_pct": 0.10,
        "shot_conversion": 0.05,
    },
}
KANTE_FEATURES = [
    "ball_winning_p90",
    "pressures_p90",
    "progressive_passes_p90",
    "progressive_carries_p90",
    "pass_completion",
    "recoveries_p90",
    "tackles_p90",
    "interceptions_p90",
    "xg_p90",
    "shots_p90",
]


def load_merged() -> pd.DataFrame:
    case = pd.read_csv(PROCESSED / "case_players.csv")
    pred = pd.read_csv(TABLES / "case_predictions.csv")
    glob = pd.read_csv(TABLES / "global_case_predictions.csv")
    df = case.merge(
        pred[["player_id", "local_discount_pct", "local_residual", "local_residual_pct"]],
        on="player_id",
        how="inner",
    )
    df = df.merge(glob[["player_id", "global_discount_pct", "global_fair_value"]], on="player_id", how="left")
    df["minutes_pct"] = (df["minutes"] / 3420).clip(0, 1)
    return df


def assign_clusters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    outfield = out[(out["position_group"] != "GK") & (out["minutes"] >= 900)].copy()
    X = outfield[CLUSTER_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
    scaler = StandardScaler()
    Z = scaler.fit_transform(X)
    model = KMeans(n_clusters=6, random_state=42, n_init=10)
    labels = model.fit_predict(Z)
    outfield["cluster"] = labels

    centroids = pd.DataFrame(scaler.inverse_transform(model.cluster_centers_), columns=CLUSTER_FEATURES)
    means = X.mean()
    stds = X.std(ddof=0).replace(0, 1)
    cluster_label = {}
    for cid, row in centroids.iterrows():
        z = (row - means) / stds
        top = z.sort_values(ascending=False).head(2).index
        cluster_label[cid] = " + ".join(FEATURE_LABEL[f] for f in top)
    outfield["cluster_label"] = outfield["cluster"].map(cluster_label)
    out = out.merge(outfield[["player_id", "cluster", "cluster_label"]], on="player_id", how="left")
    return out


def _pct(series: pd.Series) -> pd.Series:
    return series.rank(pct=True)


def _kante_similarity(pool: pd.DataFrame, kante: pd.Series) -> pd.Series:
    X = pool[KANTE_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
    mean = X.mean()
    std = X.std(ddof=0).replace(0, 1)
    Z = (X - mean) / std
    kz = (kante[KANTE_FEATURES].astype(float) - mean) / std
    numerator = Z.values @ kz.values
    denominator = np.linalg.norm(Z.values, axis=1) * np.linalg.norm(kz.values) + 1e-9
    return pd.Series(numerator / denominator, index=pool.index)


def _risk(pool: pd.DataFrame) -> pd.Series:
    availability = (pool["minutes"] / 3420).clip(0, 1)
    injury = (pool["injury_days"].fillna(0) / 90).clip(0, 1)
    age = pool["age"]
    age_risk = np.where(age < 23, (23 - age) * 8, np.where(age > 27, (age - 27) * 7, 0))
    age_risk = np.clip(age_risk, 0, 100)
    cards = (pool["yellow_cards"].fillna(0) + 2 * pool["red_cards"].fillna(0)) / pool["minutes"].clip(lower=1) * 90
    discipline = (cards / 0.5).clip(0, 1) * 100
    risk = 0.40 * (1 - availability) * 100 + 0.30 * injury * 100 + 0.20 * age_risk + 0.10 * discipline
    return risk.clip(0, 100)


def _fit_profile(pool: pd.DataFrame, weights: dict) -> pd.Series:
    score = pd.Series(0.0, index=pool.index)
    for metric, weight in weights.items():
        pct = _pct(pool[metric].fillna(0))
        score += (1 - pct if weight < 0 else pct) * abs(weight)
    return score * 100


def build_candidates() -> pd.DataFrame:
    df = load_merged()
    df = assign_clusters(df)
    kante = df[df["player_id"] == 225083].iloc[0]

    frames = []
    for key, need in NEEDS.items():
        pool = df[
            (df["position"].isin(need.positions))
            & (df["minutes"] >= MIN_MINUTES)
            & (df["age"] <= need.max_age)
            & (df["market_value"] >= MIN_VALUE)
            & (df["market_value"] <= MAX_VALUE)
            & (~df["team_name"].str.contains("Leicester", na=False))
        ].copy()
        if pool.empty:
            continue
        pool["need"] = key
        pool["need_label"] = need.label
        pool["minutes_pct"] = (pool["minutes"] / 3420).clip(0, 1)

        if key == "CM":
            pool["kante_sim"] = _kante_similarity(pool, kante)
            pool["kante_sim_pct"] = _pct(pool["kante_sim"]) * 100
            pool["fit"] = (
                0.75 * pool["kante_sim_pct"]
                + 0.15 * _pct(pool["minutes"]) * 100
                + 0.10 * _pct(pool["pass_completion"]) * 100
            )
        else:
            pool["kante_sim"] = np.nan
            pool["kante_sim_pct"] = np.nan
            pool["fit"] = _fit_profile(pool, PROFILE_WEIGHTS[key])

        pool["local_v"] = _pct(pool["local_discount_pct"]) * 100
        pool["global_v"] = _pct(pool["global_discount_pct"].fillna(pool["local_discount_pct"])) * 100
        pool["value"] = 0.6 * pool["local_v"] + 0.4 * pool["global_v"]
        pool["risk"] = _risk(pool)
        pool["safety"] = 100 - pool["risk"]
        pool["score"] = 0.55 * pool["fit"] + 0.25 * pool["value"] + 0.20 * pool["safety"]
        pool["cost_m"] = pool["market_value"] / 1e6
        frames.append(pool)

    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values(["need", "score"], ascending=[True, False])
    out.to_csv(TABLES / "candidates.csv", index=False)

    summary = {
        "pool": out.groupby("need").size().to_dict(),
        "top": out.sort_values("score", ascending=False)
        .groupby("need")
        .head(3)[
            ["need", "display_name", "team_name", "age", "market_value", "fit", "value", "safety", "score", "cluster_label"]
        ]
        .round(2)
        .to_dict(orient="records"),
    }
    (OUTPUTS / "scouting_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    c = build_candidates()
    print(c.groupby("need").size())
    print(c.sort_values(["need", "score"], ascending=[True, False]).groupby("need").head(5)[
        ["need", "display_name", "team_name", "age", "cost_m", "fit", "value", "safety", "score", "cluster_label"]
    ].to_string(index=False))
