from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from .config import CASE_CUTOFF, CASE_LEAGUE, PROCESSED, TM_RAW, TOP5

TEAM_MAP = {
    "Arsenal": "Arsenal FC",
    "Aston Villa": "Aston Villa",
    "AFC Bournemouth": "AFC Bournemouth",
    "Chelsea": "Chelsea FC",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton FC",
    "Leicester City": "Leicester City",
    "Liverpool": "Liverpool FC",
    "Manchester City": "Manchester City",
    "Manchester United": "Manchester United",
    "Newcastle United": "Newcastle United",
    "Norwich City": "Norwich City",
    "Southampton": "Southampton FC",
    "Stoke City": "Stoke City",
    "Sunderland": "Sunderland AFC",
    "Swansea City": "Swansea City",
    "Tottenham Hotspur": "Tottenham Hotspur",
    "Watford": "Watford FC",
    "West Bromwich Albion": "West Bromwich Albion",
    "West Ham United": "West Ham United",
}


def _key(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    value = str(value).replace("''", "'").replace("`", "'")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    value = re.sub(r"[^a-z0-9' ]", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def _slug_key(value: str) -> str:
    return re.sub(r"[^a-z0-9' ]", " ", str(value).replace("-", " ").lower()).strip()


def season_end_year(season: str) -> int:
    parts = str(season).split("/")
    if len(parts) == 2:
        return 2000 + int(parts[1])
    return int(parts[0])


def load_profiles() -> pd.DataFrame:
    prof = pd.read_csv(TM_RAW / "player_profiles.csv", low_memory=False)
    prof["name_key"] = prof["player_name"].map(_key)
    prof["slug_key"] = prof["player_slug"].map(_slug_key)
    prof["alt_key"] = prof["name_in_home_country"].map(_key)
    birth = pd.to_datetime(prof["date_of_birth"], errors="coerce")
    prof["birth_date"] = birth
    prof["position_group"] = prof["position"].fillna("").str.split(" - ").str[0].map(
        {"Goalkeeper": "GK", "Defender": "DF", "Midfield": "MF", "Attack": "FW"}
    ).fillna("OTHER")
    prof["detailed_position"] = prof["position"].fillna("").str.split(" - ").str[-1]
    return prof


def load_performances() -> pd.DataFrame:
    perf = pd.read_csv(TM_RAW / "player_performances.csv", low_memory=False)
    perf["end_year"] = perf["season_name"].map(season_end_year)
    perf["appearances"] = perf["nb_on_pitch"].fillna(0).astype(float)
    perf["sub_apps"] = perf["subed_in"].fillna(0).astype(float)
    perf["starts"] = (perf["appearances"] - perf["sub_apps"]).clip(lower=0)
    return perf


def load_market_values() -> pd.DataFrame:
    mv = pd.read_csv(TM_RAW / "player_market_value.csv")
    mv["date"] = pd.to_datetime(mv["date_unix"], errors="coerce")
    mv = mv.dropna(subset=["date", "value"])
    return mv[["player_id", "date", "value"]].sort_values(["player_id", "date"])


def value_at(mv: pd.DataFrame, cutoff: pd.Timestamp, extra: pd.DataFrame | None = None) -> pd.DataFrame:
    snap = mv[mv["date"] <= cutoff].sort_values("date").groupby("player_id").tail(1)
    snap = snap.rename(columns={"value": "market_value", "date": "value_date"})
    if extra is not None:
        snap = snap.merge(extra, on="player_id", how="left")
    snap["stale_days"] = (cutoff - snap["value_date"]).dt.days
    return snap


def _league_rank(team_seasons: pd.DataFrame, season: str, league: str) -> dict[str, float]:
    sub = team_seasons[
        (team_seasons["season_season"] == season) & (team_seasons["competition_id"] == league)
    ]
    return dict(zip(sub["team_name"], sub["season_rank"]))


def build_market_dataset() -> pd.DataFrame:
    print("loading profiles and performances", flush=True)
    prof = load_profiles()
    perf = load_performances()
    mv = load_market_values()
    injuries = pd.read_csv(TM_RAW / "player_injuries.csv", low_memory=False)
    team_seasons = pd.read_csv(TM_RAW / "team_competitions_seasons.csv", low_memory=False)

    top = perf[perf["competition_id"].isin(TOP5)].copy()
    top = top[top["season_name"].between("10/11", "24/25")]
    # One row per player and season. A mid-season transfer can create two rows;
    # the club with more appearances is the primary club.
    top["primary_team"] = top["team_name"]
    idx = top.groupby(["player_id", "season_name"])["appearances"].idxmax()
    main = top.loc[idx].copy()
    agg = (
        top.groupby(["player_id", "season_name"])
        .agg(
            appearances=("appearances", "sum"),
            starts=("starts", "sum"),
            sub_apps=("sub_apps", "sum"),
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            penalty_goals=("penalty_goals", "sum"),
            yellow=("yellow_cards", "sum"),
            red=("direct_red_cards", "sum"),
            clean_sheets=("clean_sheets", "sum"),
            goals_conceded=("goals_conceded", "sum"),
        )
        .reset_index()
    )
    agg = agg.merge(
        main[["player_id", "season_name", "competition_id", "team_name", "primary_team"]],
        on=["player_id", "season_name"],
        how="left",
    )
    agg = agg[agg["appearances"] >= 5].copy()
    agg["league"] = agg["competition_id"]
    agg["end_year"] = agg["season_name"].map(season_end_year)
    agg["cutoff"] = pd.to_datetime(agg["end_year"].astype(str) + "-07-01")

    print("profiles merge", flush=True)
    agg = agg.merge(
        prof[
            [
                "player_id",
                "player_name",
                "birth_date",
                "position_group",
                "detailed_position",
                "height",
                "foot",
                "citizenship",
            ]
        ],
        on="player_id",
        how="left",
    )
    agg["age"] = (
        (agg["cutoff"] - agg["birth_date"]).dt.days / 365.25
    )
    agg = agg[agg["age"].between(15, 42)].copy()

    print("market value snapshots", flush=True)
    snaps = []
    for year, group in agg.groupby("end_year"):
        cutoff = pd.Timestamp(f"{year}-07-01")
        snap = value_at(mv, cutoff)
        snap["end_year"] = year
        snaps.append(snap)
    snap = pd.concat(snaps, ignore_index=True)
    agg = agg.merge(
        snap[["player_id", "end_year", "market_value", "value_date", "stale_days"]],
        on=["player_id", "end_year"],
        how="left",
    )
    agg = agg[agg["market_value"].fillna(0) > 0].copy()
    agg = agg[agg["stale_days"].fillna(9999) <= 550].copy()

    print("injuries and ranks", flush=True)
    inj = (
        injuries.groupby(["player_id", "season_name"])["days_missed"].sum().reset_index()
        .rename(columns={"days_missed": "injury_days"})
    )
    agg = agg.merge(inj, on=["player_id", "season_name"], how="left")
    agg["injury_days"] = agg["injury_days"].fillna(0)

    ranks = []
    for (season, league), group in agg.groupby(["season_name", "league"]):
        mapping = _league_rank(team_seasons, season, league)
        group = group.copy()
        group["club_rank"] = group["team_name"].map(mapping)
        ranks.append(group)
    agg = pd.concat(ranks, ignore_index=True)
    agg["club_rank"] = agg["club_rank"].fillna(
        agg.groupby(["season_name", "league"])["club_rank"].transform("median")
    )

    agg["goals_per_app"] = agg["goals"] / agg["appearances"].clip(lower=1)
    agg["assists_per_app"] = agg["assists"] / agg["appearances"].clip(lower=1)
    agg["contrib_per_app"] = (agg["goals"] + agg["assists"]) / agg["appearances"].clip(lower=1)
    agg["non_penalty_goals"] = agg["goals"] - agg["penalty_goals"].fillna(0)
    agg["np_goals_per_app"] = agg["non_penalty_goals"] / agg["appearances"].clip(lower=1)
    agg["cards_per_app"] = (agg["yellow"] + 2 * agg["red"]) / agg["appearances"].clip(lower=1)

    med = (
        agg.groupby(["season_name", "league"])["market_value"]
        .median()
        .rename("league_value_median")
        .reset_index()
    )
    agg = agg.merge(med, on=["season_name", "league"], how="left")
    agg["log_value_rel"] = np.log(agg["market_value"]) - np.log(agg["league_value_median"])

    keep = [
        "player_id",
        "player_name",
        "season_name",
        "end_year",
        "league",
        "team_name",
        "club_rank",
        "age",
        "position_group",
        "detailed_position",
        "height",
        "foot",
        "citizenship",
        "appearances",
        "starts",
        "sub_apps",
        "goals",
        "assists",
        "penalty_goals",
        "non_penalty_goals",
        "goals_per_app",
        "assists_per_app",
        "contrib_per_app",
        "np_goals_per_app",
        "cards_per_app",
        "clean_sheets",
        "goals_conceded",
        "injury_days",
        "market_value",
        "value_date",
        "stale_days",
        "league_value_median",
        "log_value_rel",
    ]
    out = agg[keep].copy()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROCESSED / "market_players.csv", index=False)
    print("market players", out.shape, flush=True)
    return out


def map_statsbomb_to_tm() -> pd.DataFrame:
    sb = pd.read_csv(PROCESSED / "sb_players.csv")
    sb = sb[sb["minutes"] >= 300].copy()
    prof = load_profiles()
    perf = load_performances()
    tm = perf[
        (perf["competition_id"] == CASE_LEAGUE) & (perf["season_name"] == "15/16")
    ].copy()
    tm = tm.merge(
        prof[
            [
                "player_id",
                "player_name",
                "player_slug",
                "name_key",
                "slug_key",
                "alt_key",
                "birth_date",
                "position_group",
                "citizenship",
            ]
        ],
        on="player_id",
        how="left",
    )
    tm["team_key"] = tm["team_name"].map(TEAM_MAP)
    tm["search_key"] = tm["name_key"].where(tm["name_key"].notna(), tm["slug_key"])

    rows = []
    for _, player in sb.sort_values("minutes", ascending=False).iterrows():
        team = TEAM_MAP.get(player["team_name"], player["team_name"])
        pool = tm[tm["team_key"] == team]
        if pool.empty:
            pool = tm
        choices = []
        for _, cand in pool.iterrows():
            keys = [k for k in (cand.get("name_key"), cand.get("slug_key"), cand.get("alt_key")) if isinstance(k, str) and k]
            if not keys:
                continue
            score = max(
                fuzz.WRatio(player["name_key"], k) for k in keys
            )
            if cand["position_group"] == player["position_group"]:
                score += 4
            if str(player.get("country", "")).lower()[:4] in str(cand.get("citizenship", "")).lower():
                score += 3
            choices.append((score, cand))
        choices.sort(key=lambda x: x[0], reverse=True)
        if not choices:
            rows.append({"sb_player_id": player["player_id"], "sb_player_name": player["player_name"], "tm_player_id": None, "tm_player_name": None, "confidence": 0, "manual": False})
            continue
        score, cand = choices[0]
        rows.append(
            {
                "sb_player_id": player["player_id"],
                "sb_player_name": player["player_name"],
                "sb_team": player["team_name"],
                "tm_player_id": int(cand["player_id"]),
                "tm_player_name": cand.get("player_name") if isinstance(cand.get("player_name"), str) else cand.get("player_slug"),
                "confidence": round(float(score), 1),
                "manual": False,
            }
        )

    mapping = pd.DataFrame(rows)
    # Explicit fixes for names that the fuzzy matcher cannot recover.
    fixes = {
        "N''Golo Kanté": 225083,
        "Bamidele Alli": 207929,
        "Andrew Philip King": 56872,
        "José Leonardo Ulloa": 54890,
        "Gökhan İnler": 19041,
        "Kasper Schmeichel": 16911,
    }
    for name, tm_id in fixes.items():
        mask = mapping["sb_player_name"] == name
        if mask.any():
            mapping.loc[mask, "tm_player_id"] = tm_id
            mapping.loc[mask, "manual"] = True
            mapping.loc[mask, "confidence"] = 100.0
            prof_row = prof[prof["player_id"] == tm_id]
            if not prof_row.empty:
                mapping.loc[mask, "tm_player_name"] = prof_row.iloc[0]["player_name"] if isinstance(prof_row.iloc[0]["player_name"], str) else prof_row.iloc[0]["player_slug"]

    # Reject uncertain matches. The source has gaps, and a wrong valuation is
    # worse than a missing one for a transfer shortlist.
    weak = (~mapping["manual"]) & (mapping["confidence"] < 92)
    mapping.loc[weak, "tm_player_id"] = None
    mapping.loc[weak, "tm_player_name"] = None

    # Keep only one StatsBomb player per Transfermarkt id, the most confident one.
    dup = mapping[mapping["tm_player_id"].notna()].sort_values("confidence", ascending=False)
    keep = dup.drop_duplicates("tm_player_id")["sb_player_id"]
    drop = dup[~dup["sb_player_id"].isin(keep)]["sb_player_id"]
    mapping.loc[mapping["sb_player_id"].isin(drop), ["tm_player_id", "tm_player_name"]] = None

    mapping = mapping.drop_duplicates("sb_player_id")
    mapping.to_csv(PROCESSED / "player_map.csv", index=False)
    low = mapping[mapping["confidence"] < 92]
    print("mapped", mapping["tm_player_id"].notna().sum(), "of", len(mapping), "low confidence", len(low), flush=True)
    if len(low):
        print(low[["sb_player_name", "sb_team", "tm_player_id", "tm_player_name", "confidence"]].to_string(index=False), flush=True)
    return mapping


def build_case_dataset() -> pd.DataFrame:
    market = pd.read_csv(PROCESSED / "market_players.csv")
    case = market[(market["league"] == CASE_LEAGUE) & (market["season_name"] == "15/16")].copy()
    sb = pd.read_csv(PROCESSED / "sb_players.csv")
    mapping = map_statsbomb_to_tm()
    sb = sb.rename(columns={"player_id": "sb_player_id"})
    sb = sb.merge(mapping[["sb_player_id", "tm_player_id", "confidence", "manual"]], on="sb_player_id", how="left")
    sb = sb.rename(columns={"tm_player_id": "player_id"})
    case = case.merge(
        sb[
            [
                "player_id",
                "player_name",
                "team_name",
                "position",
                "position_group",
                "minutes",
                "matches",
                "starts",
                "passes_p90",
                "pass_completion",
                "progressive_passes_p90",
                "progressive_pass_share",
                "final_third_passes_p90",
                "passes_into_box_p90",
                "long_balls_p90",
                "crosses_p90",
                "key_passes_p90",
                "xa_p90",
                "shots_p90",
                "shots_on_target_p90",
                "goals",
                "xg_p90",
                "shots_in_box_p90",
                "touches_p90",
                "touches_box_p90",
                "carries_p90",
                "progressive_carries_p90",
                "carries_final_third_p90",
                "carries_into_box_p90",
                "pressures_p90",
                "counterpressures_p90",
                "tackles_p90",
                "tackles_won_p90",
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
                "yellow_cards",
                "red_cards",
                "ball_receipts_p90",
                "pass_completion",
                "progressive_pass_share",
                "progressive_carry_share",
                "shot_conversion",
                "defensive_actions_p90",
                "ball_winning_p90",
                "pressing_p90",
                "security_p90",
                "avg_pass_start_x",
                "avg_def_action_x",
                "confidence",
                "manual",
            ]
        ],
        on="player_id",
        how="inner",
        suffixes=("", "_tm"),
    )
    name = case["player_name_tm"].where(case["player_name_tm"].notna(), case["player_name"])
    case["display_name"] = (
        name.astype(str)
        .str.replace(r"\s*\(\d+\)$", "", regex=True)
        .str.replace("''", "'", regex=False)
    )
    case.to_csv(PROCESSED / "case_players.csv", index=False)
    print("case players", case.shape, flush=True)
    return case


if __name__ == "__main__":
    build_market_dataset()
    build_case_dataset()
