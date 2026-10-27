from __future__ import annotations

import json
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import FIGURES, OUTPUTS, PROCESSED, RANDOM_STATE, TABLES
from .tm import value_at


def role_from_position(value: str) -> str:
    p = str(value).lower()
    if "goalkeeper" in p:
        return "GK"
    if "center back" in p or "centre-back" in p:
        return "CB"
    if "wing back" in p or "back" in p:
        return "FB"
    if "defensive midfield" in p:
        return "DM"
    if "attacking midfield" in p:
        return "AM"
    if "midfield" in p:
        return "CM"
    if "wing" in p:
        return "W"
    if "forward" in p or "striker" in p:
        return "ST"
    return "OTHER"


GLOBAL_NUM = [
    "age",
    "appearances",
    "starts",
    "sub_apps",
    "goals_per_app",
    "assists_per_app",
    "np_goals_per_app",
    "cards_per_app",
    "injury_days_log",
    "height",
    "club_rank",
]
GLOBAL_CAT = ["league", "position_group", "role", "foot"]


def _metrics(y: np.ndarray, pred: np.ndarray) -> dict:
    rho = spearmanr(y, pred).correlation if len(y) > 2 else np.nan
    return {
        "n": int(len(y)),
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "r2": float(r2_score(y, pred)) if len(y) > 2 else np.nan,
        "spearman": float(rho) if np.isfinite(rho) else np.nan,
    }


def _prepare_global(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["role"] = out["detailed_position"].map(role_from_position)
    out["height"] = pd.to_numeric(out["height"], errors="coerce")
    out.loc[out["height"] <= 0, "height"] = np.nan
    out["height"] = out.groupby("role")["height"].transform(lambda s: s.fillna(s.median()))
    out["height"] = out["height"].fillna(out["height"].median())
    out["foot"] = out["foot"].fillna("unknown").astype(str).str.lower()
    out["injury_days_log"] = np.log1p(out["injury_days"].fillna(0).clip(lower=0))
    out["club_rank"] = pd.to_numeric(out["club_rank"], errors="coerce").fillna(10)
    return out


def _design(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train = _prepare_global(train)
    test = _prepare_global(test)
    full = pd.concat([train[GLOBAL_NUM + GLOBAL_CAT], test[GLOBAL_NUM + GLOBAL_CAT]], ignore_index=True)
    full = pd.get_dummies(full, columns=GLOBAL_CAT, dummy_na=False)
    X_train = full.iloc[: len(train)].copy()
    X_test = full.iloc[len(train) :].copy()
    X_train = X_train.fillna(0)
    X_test = X_test.fillna(0)
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
    return X_train, X_test, list(X_train.columns)


def _fit_lgbm(X_train, y_train, X_valid=None, y_valid=None) -> lgb.LGBMRegressor:
    model = lgb.LGBMRegressor(
        n_estimators=600,
        learning_rate=0.035,
        num_leaves=31,
        min_child_samples=40,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=1.5,
        random_state=RANDOM_STATE,
        n_jobs=2,
        verbose=-1,
    )
    model.fit(X_train, y_train)
    return model


def _fit_ridge(X_train, y_train) -> Pipeline:
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("ridge", RidgeCV(alphas=np.logspace(-2, 3, 25))),
        ]
    )
    model.fit(X_train, y_train)
    return model


def train_global(market: pd.DataFrame) -> dict:
    market = market.copy()
    train = market[market["end_year"] <= 2021].copy()
    test = market[market["end_year"] >= 2022].copy()
    train["role"] = train["detailed_position"].map(role_from_position)
    test["role"] = test["detailed_position"].map(role_from_position)
    X_train, X_test, cols = _design(train, test)
    y_train = train["log_value_rel"].to_numpy()
    y_test = test["log_value_rel"].to_numpy()

    print("global train", X_train.shape, "test", X_test.shape, flush=True)
    lgbm = _fit_lgbm(X_train, y_train)
    pred_lgbm = lgbm.predict(X_test)
    ridge = _fit_ridge(X_train, y_train)
    pred_ridge = ridge.predict(X_test)

    # A simple baseline: the median relative value of the same role.
    role_med = train.groupby("role")["log_value_rel"].median()
    pred_base = test["role"].map(role_med).fillna(train["log_value_rel"].median()).to_numpy()

    metrics = {
        "baseline_role_median": _metrics(y_test, pred_base),
        "ridge": _metrics(y_test, pred_ridge),
        "lightgbm": _metrics(y_test, pred_lgbm),
    }
    by_season = []
    for season, idx in test.groupby("season_name").groups.items():
        pos = test.index.get_indexer(idx)
        by_season.append(
            {
                "season": season,
                **_metrics(y_test[pos], pred_lgbm[pos]),
                "mae_ridge": mean_absolute_error(y_test[pos], pred_ridge[pos]),
            }
        )
    by_season = pd.DataFrame(by_season)

    importance = pd.DataFrame(
        {
            "feature": cols,
            "gain": lgbm.booster_.feature_importance(importance_type="gain"),
            "split": lgbm.booster_.feature_importance(importance_type="split"),
        }
    ).sort_values("gain", ascending=False)
    importance.to_csv(TABLES / "global_feature_importance.csv", index=False)
    by_season.to_csv(TABLES / "global_metrics_by_season.csv", index=False)

    # Predictions on the held-out seasons, useful for the parity figure and report.
    holdout = test[
        ["player_id", "player_name", "season_name", "league", "team_name", "role", "age", "market_value", "log_value_rel"]
    ].copy()
    holdout["pred_lgbm"] = pred_lgbm
    holdout["pred_ridge"] = pred_ridge
    holdout["pred_baseline"] = pred_base
    holdout.to_csv(TABLES / "global_holdout_predictions.csv", index=False)

    # Refit on seasons through 2014/15 and score the 2015/16 Premier League.
    # This is a genuine forward test for the case study.
    case_train = market[market["end_year"] <= 2015].copy()
    case_test = market[(market["season_name"] == "15/16") & (market["league"] == "GB1")].copy()
    case_test["role"] = case_test["detailed_position"].map(role_from_position)
    Xc_train, Xc_test, ccols = _design(case_train, case_test)
    case_model = _fit_lgbm(Xc_train, case_train["log_value_rel"].to_numpy())
    case_pred = case_model.predict(Xc_test)
    case_out = case_test[
        ["player_id", "player_name", "team_name", "role", "position_group", "age", "market_value", "log_value_rel"]
    ].copy()
    case_out["display_name"] = (
        case_out["player_name"].astype(str)
        .str.replace(r"\s*\(\d+\)$", "", regex=True)
        .str.replace("''", "'", regex=False)
    )
    case_out["global_pred_rel"] = case_pred
    case_out["global_residual"] = case_out["log_value_rel"] - case_out["global_pred_rel"]
    case_out["global_median"] = float(
        market[(market["season_name"] == "15/16") & (market["league"] == "GB1")]["league_value_median"].iloc[0]
    )
    case_out["global_fair_value"] = np.exp(case_out["global_pred_rel"] + np.log(case_out["global_median"]))
    case_out["global_discount_pct"] = (1 - case_out["market_value"] / case_out["global_fair_value"]) * 100
    case_out.to_csv(TABLES / "global_case_predictions.csv", index=False)

    joblib.dump({"model": case_model, "columns": ccols}, OUTPUTS / "global_case_model.joblib")
    joblib.dump({"model": lgbm, "columns": cols}, OUTPUTS / "global_model.joblib")

    return {
        "metrics": metrics,
        "by_season": by_season,
        "importance": importance,
        "case": case_out,
        "holdout": holdout,
    }


LOCAL_BASE = ["age", "minutes", "starts", "club_rank"]
LOCAL_EVENTS = [
    "passes_p90",
    "pass_completion",
    "progressive_passes_p90",
    "final_third_passes_p90",
    "passes_into_box_p90",
    "key_passes_p90",
    "xa_p90",
    "shots_p90",
    "xg_p90",
    "shots_in_box_p90",
    "touches_box_p90",
    "progressive_carries_p90",
    "carries_into_box_p90",
    "pressures_p90",
    "tackles_p90",
    "interceptions_p90",
    "blocks_p90",
    "clearances_p90",
    "recoveries_p90",
    "aerials_lost_p90",
    "dribbles_completed_p90",
    "dispossessed_p90",
    "miscontrols_p90",
    "fouls_committed_p90",
    "fouls_won_p90",
    "defensive_actions_p90",
    "ball_winning_p90",
    "pressing_p90",
    "security_p90",
    "avg_pass_start_x",
    "avg_def_action_x",
]


def _local_design(case: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame, list[str]]:
    data = case.copy()
    data["role"] = data["position"].map(role_from_position)
    data = pd.get_dummies(data, columns=["role"], dummy_na=False)
    role_cols = [c for c in data.columns if c.startswith("role_")]
    cols = features + role_cols
    X = data[cols].apply(pd.to_numeric, errors="coerce")
    X = X.fillna(X.median())
    return X, cols


def train_local(case: pd.DataFrame) -> dict:
    case = case[(case["minutes"] >= 900) & (case["position_group"] != "GK")].copy()
    case["role"] = case["position"].map(role_from_position)
    y = case["log_value_rel"].to_numpy()
    kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    base_X, base_cols = _local_design(case, LOCAL_BASE)
    base_model = Pipeline([("scale", StandardScaler()), ("ridge", RidgeCV(alphas=np.logspace(-2, 3, 25)))])
    base_pred = cross_val_predict(base_model, base_X, y, cv=kf)

    full_X, full_cols = _local_design(case, LOCAL_BASE + LOCAL_EVENTS)
    full_model = Pipeline([("scale", StandardScaler()), ("ridge", RidgeCV(alphas=np.logspace(-2, 3, 25)))])
    full_pred = cross_val_predict(full_model, full_X, y, cv=kf)

    metrics = {
        "baseline": _metrics(y, base_pred),
        "full": _metrics(y, full_pred),
    }
    out = case[
        [
            "player_id",
            "display_name",
            "team_name",
            "position",
            "position_group",
            "age",
            "minutes",
            "starts",
            "market_value",
            "league_value_median",
            "log_value_rel",
            "club_rank",
        ]
    ].copy()
    out["local_pred_rel"] = full_pred
    out["local_residual"] = y - full_pred
    out["local_fair_value"] = np.exp(full_pred + np.log(out["league_value_median"]))
    out["local_discount_pct"] = (1 - out["market_value"] / out["local_fair_value"]) * 100
    out["local_discount_pct"] = out["local_discount_pct"].clip(-90, 300)
    out["local_residual_pct"] = out["local_residual"].rank(pct=True) * 100
    out["baseline_pred_rel"] = base_pred

    full_model.fit(full_X, y)
    coef = pd.DataFrame(
        {
            "feature": full_cols,
            "coef": full_model.named_steps["ridge"].coef_,
            "mean": full_X.mean().values,
            "std": full_X.std().values,
        }
    ).sort_values("coef")
    coef.to_csv(TABLES / "local_coefficients.csv", index=False)

    out.to_csv(TABLES / "case_predictions.csv", index=False)
    return {
        "metrics": metrics,
        "predictions": out,
        "coefficients": coef,
        "n": len(case),
    }


def backtest_local(case_pred: pd.DataFrame) -> pd.DataFrame:
    mv = pd.read_csv(PROCESSED.parent / "raw" / "transfermarkt" / "player_market_value.csv")
    mv["date"] = pd.to_datetime(mv["date_unix"], errors="coerce")
    mv = mv.dropna(subset=["date", "value"])[["player_id", "date", "value"]]
    futures = []
    for years in (1, 2, 3):
        target = pd.Timestamp(f"2016-07-01") + pd.DateOffset(years=years)
        snap = value_at(mv, target).rename(columns={"market_value": f"value_{years}y"})
        futures.append(snap[["player_id", f"value_{years}y"]])
    fut = futures[0]
    for part in futures[1:]:
        fut = fut.merge(part, on="player_id", how="outer")
    out = case_pred.merge(fut, on="player_id", how="left")
    for years in (1, 2, 3):
        ratio = out[f"value_{years}y"] / out["market_value"]
        out[f"growth_{years}y"] = np.where(ratio > 0, np.log(ratio), np.nan)
    out["residual_pct_role"] = out.groupby("position_group")["local_residual"].rank(pct=True)
    out["undervalued"] = out["residual_pct_role"] <= 0.2
    rows = []
    for years in (1, 2, 3):
        sub = out.dropna(subset=[f"growth_{years}y"])
        if sub.empty:
            continue
        rows.append(
            {
                "horizon_years": years,
                "n": len(sub),
                "undervalued_n": int(sub["undervalued"].sum()),
                "median_growth_undervalued": float(sub.loc[sub["undervalued"], f"growth_{years}y"].median()),
                "median_growth_rest": float(sub.loc[~sub["undervalued"], f"growth_{years}y"].median()),
                "hit_rate_undervalued": float((sub.loc[sub["undervalued"], f"growth_{years}y"] > 0).mean()),
                "hit_rate_rest": float((sub.loc[~sub["undervalued"], f"growth_{years}y"] > 0).mean()),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(TABLES / "backtest_local.csv", index=False)
    out.to_csv(TABLES / "case_backtest_players.csv", index=False)
    return table


def backtest_global(market: pd.DataFrame) -> pd.DataFrame:
    market = market.copy()
    mv = pd.read_csv(PROCESSED.parent / "raw" / "transfermarkt" / "player_market_value.csv")
    mv["date"] = pd.to_datetime(mv["date_unix"], errors="coerce")
    mv = mv.dropna(subset=["date", "value"])[["player_id", "date", "value"]]
    rows = []
    for season in sorted(market["end_year"].unique()):
        if season < 2014 or season > 2023:
            continue
        train = market[market["end_year"] < season]
        test = market[market["end_year"] == season].copy()
        if len(train) < 3000 or test.empty:
            continue
        X_train, X_test, _ = _design(train, test)
        model = _fit_lgbm(X_train, train["log_value_rel"].to_numpy())
        test["pred"] = model.predict(X_test)
        test["residual"] = test["log_value_rel"] - test["pred"]
        target = pd.Timestamp(f"{season + 2}-07-01")
        snap = value_at(mv, target).rename(columns={"market_value": "future_value"})
        test = test.merge(snap[["player_id", "future_value"]], on="player_id", how="left")
        ratio = test["future_value"] / test["market_value"]
        test["growth"] = np.where(ratio > 0, np.log(ratio), np.nan)
        test = test.replace([np.inf, -np.inf], np.nan).dropna(subset=["growth"])
        if len(test) < 50:
            continue
        test["residual_pct_role"] = test.groupby("position_group")["residual"].rank(pct=True)
        test["undervalued"] = test["residual_pct_role"] <= 0.2
        rows.append(
            {
                "season": f"{season - 1}/{str(season)[-2:]}",
                "n": len(test),
                "undervalued_n": int(test["undervalued"].sum()),
                "median_growth_undervalued": float(test.loc[test["undervalued"], "growth"].median()),
                "median_growth_rest": float(test.loc[~test["undervalued"], "growth"].median()),
                "hit_rate_undervalued": float((test.loc[test["undervalued"], "growth"] > 0).mean()),
                "hit_rate_rest": float((test.loc[~test["undervalued"], "growth"] > 0).mean()),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(TABLES / "backtest_global.csv", index=False)
    return table


def run() -> dict:
    market = pd.read_csv(PROCESSED / "market_players.csv")
    case = pd.read_csv(PROCESSED / "case_players.csv")
    global_res = train_global(market)
    local_res = train_local(case)
    local_bt = backtest_local(local_res["predictions"])
    global_bt = backtest_global(market)
    summary = {
        "global_metrics": global_res["metrics"],
        "local_metrics": local_res["metrics"],
        "local_n": local_res["n"],
        "local_backtest": local_bt.to_dict(orient="records"),
        "global_backtest": global_bt.to_dict(orient="records"),
        "global_top_features": global_res["importance"].head(12).to_dict(orient="records"),
    }
    (OUTPUTS / "value_model_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    run()
