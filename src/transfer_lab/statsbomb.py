from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import pandas as pd

from .config import POSITION_GROUP, SB_RAW, PROCESSED, TABLES


def _load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _clock(value: str | None, period: int | None) -> float:
    if not value:
        return 45.0 if period == 1 else 90.0
    parts = [float(p) for p in value.split(":")]
    if len(parts) == 2:
        return parts[0] + parts[1] / 60.0
    return parts[0] * 60 + parts[1] + parts[2] / 60.0


def _position_minutes(player: dict) -> tuple[float, str, int]:
    total = 0.0
    by_pos: dict[str, float] = defaultdict(float)
    starts = 0
    for pos in player.get("positions", []):
        start = _clock(pos.get("from"), pos.get("from_period"))
        end = _clock(pos.get("to"), pos.get("to_period"))
        minutes = max(0.0, min(90.0, end - start))
        total += minutes
        by_pos[pos["position"]] += minutes
        if start <= 0.01:
            starts = 1
    primary = max(by_pos, key=by_pos.get) if by_pos else ""
    return min(90.0, total), primary, starts


def normalise_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("''", "'").replace("`", "'")
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    value = re.sub(r"[^a-z0-9' ]", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def in_box(location) -> bool:
    if not location:
        return False
    return location[0] >= 102 and 18 <= location[1] <= 62


def parse_match(match: dict) -> tuple[list[dict], dict]:
    match_id = match["match_id"]
    lineups = _load(SB_RAW / "lineups" / f"{match_id}.json")
    events = _load(SB_RAW / "events" / f"{match_id}.json")

    team_names = {t["team_id"]: t["team_name"] for t in lineups}
    player_rows: dict[int, dict] = {}
    for team in lineups:
        for player in team["lineup"]:
            minutes, position, starts = _position_minutes(player)
            if minutes <= 0:
                continue
            player_rows[player["player_id"]] = {
                "match_id": match_id,
                "player_id": player["player_id"],
                "player_name": player["player_name"],
                "team_id": team["team_id"],
                "team_name": team["team_name"],
                "opponent": "",
                "position": position,
                "position_group": POSITION_GROUP.get(position, "OTHER"),
                "minutes": minutes,
                "starts": starts,
                "country": (player.get("country") or {}).get("name", ""),
                "passes": 0,
                "passes_completed": 0,
                "progressive_passes": 0,
                "final_third_passes": 0,
                "passes_into_box": 0,
                "long_balls": 0,
                "crosses": 0,
                "key_passes": 0,
                "xa": 0.0,
                "shots": 0,
                "shots_on_target": 0,
                "goals": 0,
                "xg": 0.0,
                "shots_in_box": 0,
                "penalty_goals": 0,
                "touches": 0,
                "touches_box": 0,
                "carries": 0,
                "progressive_carries": 0,
                "carries_final_third": 0,
                "carries_into_box": 0,
                "pressures": 0,
                "counterpressures": 0,
                "tackles": 0,
                "tackles_won": 0,
                "interceptions": 0,
                "blocks": 0,
                "clearances": 0,
                "recoveries": 0,
                "aerials_lost": 0,
                "dribbles_completed": 0,
                "dispossessed": 0,
                "miscontrols": 0,
                "fouls_committed": 0,
                "fouls_won": 0,
                "yellow_cards": 0,
                "red_cards": 0,
                "ball_receipts": 0,
                "pass_start_x_sum": 0.0,
                "pass_start_x_n": 0,
                "def_action_x_sum": 0.0,
                "def_action_x_n": 0,
            }

    for team in lineups:
        other = [t["team_name"] for t in lineups if t["team_id"] != team["team_id"]][0]
        for player in team["lineup"]:
            if player["player_id"] in player_rows:
                player_rows[player["player_id"]]["opponent"] = other

    pass_owner: dict[str, int] = {}
    for event in events:
        etype = event["type"]["name"]
        player = event.get("player")
        if not player:
            continue
        pid = player["id"]
        row = player_rows.get(pid)
        if row is None:
            continue
        location = event.get("location")
        if location:
            row["touches"] += 1
            if in_box(location):
                row["touches_box"] += 1

        if etype == "Pass":
            data = event.get("pass", {})
            row["passes"] += 1
            completed = "outcome" not in data
            end = data.get("end_location")
            if location:
                row["pass_start_x_sum"] += location[0]
                row["pass_start_x_n"] += 1
            if completed:
                row["passes_completed"] += 1
                if end and end[0] - location[0] >= 10 and end[0] >= 40:
                    row["progressive_passes"] += 1
                if end and end[0] >= 80:
                    row["final_third_passes"] += 1
                if end and in_box(end):
                    row["passes_into_box"] += 1
            if data.get("length", 0) >= 32:
                row["long_balls"] += 1
            if data.get("cross"):
                row["crosses"] += 1
            if data.get("shot_assist") or data.get("goal_assist"):
                row["key_passes"] += 1
            pass_owner[event["id"]] = pid

        elif etype == "Shot":
            data = event.get("shot", {})
            row["shots"] += 1
            row["xg"] += float(data.get("statsbomb_xg", 0.0))
            outcome = (data.get("outcome") or {}).get("name")
            if outcome == "Goal":
                row["goals"] += 1
                if (data.get("type") or {}).get("name") == "Penalty":
                    row["penalty_goals"] += 1
            if outcome in {"Goal", "Saved", "Saved to Post"}:
                row["shots_on_target"] += 1
            if in_box(location):
                row["shots_in_box"] += 1
            key_pass_id = data.get("key_pass_id")
            if key_pass_id and key_pass_id in pass_owner:
                passer = player_rows.get(pass_owner[key_pass_id])
                if passer is not None:
                    passer["xa"] += float(data.get("statsbomb_xg", 0.0))

        elif etype == "Carry":
            data = event.get("carry", {})
            row["carries"] += 1
            end = data.get("end_location")
            if location and end:
                if end[0] - location[0] >= 10 and end[0] >= 40:
                    row["progressive_carries"] += 1
                if end[0] >= 80:
                    row["carries_final_third"] += 1
                if in_box(end):
                    row["carries_into_box"] += 1

        elif etype == "Pressure":
            row["pressures"] += 1
        elif etype == "Counterpress":
            row["counterpressures"] += 1
        elif etype == "Interception":
            row["interceptions"] += 1
            if location:
                row["def_action_x_sum"] += location[0]
                row["def_action_x_n"] += 1
        elif etype == "Block":
            row["blocks"] += 1
            if location:
                row["def_action_x_sum"] += location[0]
                row["def_action_x_n"] += 1
        elif etype == "Clearance":
            row["clearances"] += 1
            if location:
                row["def_action_x_sum"] += location[0]
                row["def_action_x_n"] += 1
        elif etype == "Ball Recovery":
            row["recoveries"] += 1
        elif etype == "Duel":
            data = event.get("duel", {})
            dtype = (data.get("type") or {}).get("name")
            outcome = (data.get("outcome") or {}).get("name")
            if dtype == "Tackle":
                row["tackles"] += 1
                if outcome in {"Won", "Success In Play", "Success Out"}:
                    row["tackles_won"] += 1
                if location:
                    row["def_action_x_sum"] += location[0]
                    row["def_action_x_n"] += 1
            elif dtype == "Aerial Lost":
                row["aerials_lost"] += 1
        elif etype == "Dribble":
            outcome = (event.get("dribble", {}).get("outcome") or {}).get("name")
            if outcome == "Complete":
                row["dribbles_completed"] += 1
        elif etype == "Dispossessed":
            row["dispossessed"] += 1
        elif etype == "Miscontrol":
            row["miscontrols"] += 1
        elif etype == "Foul Committed":
            row["fouls_committed"] += 1
            card = (event.get("foul_committed", {}).get("card") or {}).get("name")
            if card == "Yellow Card":
                row["yellow_cards"] += 1
            elif card == "Red Card":
                row["red_cards"] += 1
        elif etype == "Foul Won":
            row["fouls_won"] += 1
        elif etype == "Ball Receipt*":
            row["ball_receipts"] += 1

    team_totals: dict[int, dict] = {}
    for team in lineups:
        tid = team["team_id"]
        team_totals[tid] = {
            "match_id": match_id,
            "team_id": tid,
            "team_name": team["team_name"],
            "opponent": [t["team_name"] for t in lineups if t["team_id"] != tid][0],
            "date": match["match_date"],
            "goals": 0,
            "xg": 0.0,
            "shots": 0,
            "passes": 0,
            "passes_completed": 0,
            "progressive_passes": 0,
            "final_third_passes": 0,
            "long_balls": 0,
            "pressures": 0,
            "tackles": 0,
            "interceptions": 0,
            "blocks": 0,
            "clearances": 0,
            "recoveries": 0,
            "box_entries": 0,
            "counter_xg": 0.0,
            "set_piece_xg": 0.0,
            "pass_start_x_sum": 0.0,
            "def_action_x_sum": 0.0,
            "def_action_x_n": 0,
        }

    for event in events:
        if event["type"]["name"] != "Shot":
            continue
        data = event.get("shot", {})
        team_id = event["team"]["id"]
        if team_id not in team_totals:
            continue
        row = team_totals[team_id]
        xg = float(data.get("statsbomb_xg", 0.0))
        row["xg"] += xg
        row["shots"] += 1
        if (data.get("outcome") or {}).get("name") == "Goal":
            row["goals"] += 1
        if (data.get("type") or {}).get("name") in {"Free Kick", "Corner", "Penalty"}:
            row["set_piece_xg"] += xg
        if (event.get("play_pattern") or {}).get("name") == "From Counter":
            row["counter_xg"] += xg

    for row in player_rows.values():
        team = team_totals[row["team_id"]]
        team["box_entries"] += row["passes_into_box"] + row["carries_into_box"]
        for key in (
            "passes",
            "passes_completed",
            "progressive_passes",
            "final_third_passes",
            "long_balls",
            "pressures",
            "tackles",
            "interceptions",
            "blocks",
            "clearances",
            "recoveries",
            "pass_start_x_sum",
            "def_action_x_sum",
            "def_action_x_n",
        ):
            team[key] += row[key]

    for row in team_totals.values():
        opposite = [r for r in team_totals.values() if r["team_id"] != row["team_id"]][0]
        row["pass_share"] = row["passes"] / max(1, row["passes"] + opposite["passes"]) * 100
        row["xg_against"] = opposite["xg"]
        row["pass_completion"] = row["passes_completed"] / max(1, row["passes"]) * 100
        row["progressive_pass_share"] = row["progressive_passes"] / max(1, row["passes_completed"]) * 100
        row["long_ball_share"] = row["long_balls"] / max(1, row["passes"]) * 100
        row["pressures_per_opponent_pass"] = row["pressures"] / max(1, opposite["passes"])
        row["counter_xg_share"] = row["counter_xg"] / max(1e-9, row["xg"]) * 100
        row["set_piece_xg_share"] = row["set_piece_xg"] / max(1e-9, row["xg"]) * 100
        row["avg_pass_start_x"] = row["pass_start_x_sum"] / max(1, row["passes"])
        row["avg_def_action_x"] = row["def_action_x_sum"] / max(1, row["def_action_x_n"])

    return list(player_rows.values()), list(team_totals.values())


def build(force: bool = False) -> dict[str, Path]:
    matches = _load(SB_RAW / "matches" / "premier_league_1516.json")
    player_rows: list[dict] = []
    team_rows: list[dict] = []
    for i, match in enumerate(matches, 1):
        players, teams = parse_match(match)
        player_rows.extend(players)
        team_rows.extend(teams)
        if i % 50 == 0:
            print(f"parsed {i}/{len(matches)} matches", flush=True)

    players = pd.DataFrame(player_rows)
    teams = pd.DataFrame(team_rows)
    players["name_key"] = players["player_name"].map(normalise_name)
    teams["date"] = pd.to_datetime(teams["date"])

    agg = (
        players.groupby("player_id")
        .agg(
            player_name=("player_name", "first"),
            name_key=("name_key", "first"),
            team_name=("team_name", lambda s: s.value_counts().index[0]),
            country=("country", "first"),
            position=("position", lambda s: players.loc[s.index].groupby("position")["minutes"].sum().idxmax()),
            position_group=("position_group", lambda s: s.value_counts().index[0]),
            minutes=("minutes", "sum"),
            matches=("match_id", "nunique"),
            starts=("starts", "sum"),
            passes=("passes", "sum"),
            passes_completed=("passes_completed", "sum"),
            progressive_passes=("progressive_passes", "sum"),
            final_third_passes=("final_third_passes", "sum"),
            passes_into_box=("passes_into_box", "sum"),
            long_balls=("long_balls", "sum"),
            crosses=("crosses", "sum"),
            key_passes=("key_passes", "sum"),
            xa=("xa", "sum"),
            shots=("shots", "sum"),
            shots_on_target=("shots_on_target", "sum"),
            goals=("goals", "sum"),
            xg=("xg", "sum"),
            shots_in_box=("shots_in_box", "sum"),
            penalty_goals=("penalty_goals", "sum"),
            touches=("touches", "sum"),
            touches_box=("touches_box", "sum"),
            carries=("carries", "sum"),
            progressive_carries=("progressive_carries", "sum"),
            carries_final_third=("carries_final_third", "sum"),
            carries_into_box=("carries_into_box", "sum"),
            pressures=("pressures", "sum"),
            counterpressures=("counterpressures", "sum"),
            tackles=("tackles", "sum"),
            tackles_won=("tackles_won", "sum"),
            interceptions=("interceptions", "sum"),
            blocks=("blocks", "sum"),
            clearances=("clearances", "sum"),
            recoveries=("recoveries", "sum"),
            aerials_lost=("aerials_lost", "sum"),
            dribbles_completed=("dribbles_completed", "sum"),
            dispossessed=("dispossessed", "sum"),
            miscontrols=("miscontrols", "sum"),
            fouls_committed=("fouls_committed", "sum"),
            fouls_won=("fouls_won", "sum"),
            yellow_cards=("yellow_cards", "sum"),
            red_cards=("red_cards", "sum"),
            ball_receipts=("ball_receipts", "sum"),
            pass_start_x_sum=("pass_start_x_sum", "sum"),
            def_action_x_sum=("def_action_x_sum", "sum"),
            def_action_x_n=("def_action_x_n", "sum"),
        )
        .reset_index()
    )

    for col in (
        "passes",
        "progressive_passes",
        "final_third_passes",
        "passes_into_box",
        "long_balls",
        "crosses",
        "key_passes",
        "xa",
        "shots",
        "shots_on_target",
        "goals",
        "xg",
        "shots_in_box",
        "touches",
        "touches_box",
        "carries",
        "progressive_carries",
        "carries_final_third",
        "carries_into_box",
        "pressures",
        "counterpressures",
        "tackles",
        "tackles_won",
        "interceptions",
        "blocks",
        "clearances",
        "recoveries",
        "aerials_lost",
        "dribbles_completed",
        "dispossessed",
        "miscontrols",
        "fouls_committed",
        "fouls_won",
        "yellow_cards",
        "red_cards",
        "ball_receipts",
    ):
        agg[f"{col}_p90"] = agg[col] / agg["minutes"].clip(lower=1) * 90

    agg["pass_completion"] = agg["passes_completed"] / agg["passes"].clip(lower=1) * 100
    agg["progressive_pass_share"] = agg["progressive_passes"] / agg["passes_completed"].clip(lower=1) * 100
    agg["progressive_carry_share"] = agg["progressive_carries"] / agg["carries"].clip(lower=1) * 100
    agg["shot_conversion"] = agg["goals"] / agg["shots"].clip(lower=1) * 100
    agg["defensive_actions_p90"] = (
        agg[["tackles", "interceptions", "blocks", "clearances", "recoveries"]].sum(axis=1)
        / agg["minutes"].clip(lower=1)
        * 90
    )
    agg["ball_winning_p90"] = (
        agg[["tackles", "interceptions", "recoveries"]].sum(axis=1) / agg["minutes"].clip(lower=1) * 90
    )
    agg["pressing_p90"] = (agg["pressures"] + agg["counterpressures"]) / agg["minutes"].clip(lower=1) * 90
    agg["security_p90"] = (agg["dispossessed"] + agg["miscontrols"]) / agg["minutes"].clip(lower=1) * 90
    agg["avg_pass_start_x"] = agg["pass_start_x_sum"] / agg["passes"].clip(lower=1)
    agg["avg_def_action_x"] = agg["def_action_x_sum"] / agg["def_action_x_n"].clip(lower=1)

    # A match-level table is easier to use if both sides are in one row.
    meta = {
        m["match_id"]: (
            m["home_team"]["home_team_name"],
            m["away_team"]["away_team_name"],
            int(m["home_score"]),
            int(m["away_score"]),
        )
        for m in matches
    }
    pairs = []
    for match_id, grp in teams.groupby("match_id"):
        if len(grp) != 2 or match_id not in meta:
            continue
        home_name, away_name, home_goals, away_goals = meta[match_id]
        home = grp[grp["team_name"] == home_name]
        away = grp[grp["team_name"] == away_name]
        if home.empty or away.empty:
            continue
        a, b = home.iloc[0], away.iloc[0]
        pairs.append(
            {
                "match_id": match_id,
                "date": a["date"],
                "home": a["team_name"],
                "away": b["team_name"],
                "home_goals": home_goals,
                "away_goals": away_goals,
                "home_xg": a["xg"],
                "away_xg": b["xg"],
                "home_shots": int(a["shots"]),
                "away_shots": int(b["shots"]),
                "home_possession": a["pass_share"],
                "away_possession": b["pass_share"],
                "home_press_intensity": a["pressures_per_opponent_pass"],
                "away_press_intensity": b["pressures_per_opponent_pass"],
            }
        )
    match_table = pd.DataFrame(pairs)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    paths = {
        "players": PROCESSED / "sb_players.csv",
        "team_matches": PROCESSED / "sb_team_matches.csv",
        "matches": PROCESSED / "sb_matches.csv",
        "player_matches": PROCESSED / "sb_player_matches.csv",
    }
    agg.to_csv(paths["players"], index=False)
    teams.to_csv(paths["team_matches"], index=False)
    match_table.to_csv(paths["matches"], index=False)
    players.to_csv(paths["player_matches"], index=False)
    return paths


if __name__ == "__main__":
    build()
