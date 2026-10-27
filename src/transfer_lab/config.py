from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"

TM_RAW = RAW / "transfermarkt"
SB_RAW = RAW / "statsbomb"

CASE_CLUB = "Leicester City"
CASE_SEASON = "2015/16"
CASE_CUTOFF = "2016-07-01"
CASE_LEAGUE = "GB1"
BUDGET_EUR = 50_000_000
TOP5 = {"GB1", "ES1", "IT1", "FR1", "L1"}

RANDOM_STATE = 42


@dataclass(frozen=True)
class Need:
    key: str
    label: str
    positions: tuple[str, ...]
    max_age: int


NEEDS = {
    "CM": Need(
        "CM",
        "Central midfielder",
        (
            "Center Midfield",
            "Left Center Midfield",
            "Right Center Midfield",
            "Center Defensive Midfield",
            "Left Defensive Midfield",
            "Right Defensive Midfield",
        ),
        27,
    ),
    "CB": Need(
        "CB",
        "Center back",
        (
            "Center Back",
            "Left Center Back",
            "Right Center Back",
        ),
        27,
    ),
    "ST": Need(
        "ST",
        "Center forward",
        (
            "Center Forward",
            "Left Center Forward",
            "Right Center Forward",
            "Striker",
        ),
        29,
    ),
}


POSITION_GROUP = {
    "Goalkeeper": "GK",
    "Center Back": "DF",
    "Left Center Back": "DF",
    "Right Center Back": "DF",
    "Left Back": "DF",
    "Right Back": "DF",
    "Left Wing Back": "DF",
    "Right Wing Back": "DF",
    "Defensive Midfield": "MF",
    "Center Defensive Midfield": "MF",
    "Left Defensive Midfield": "MF",
    "Right Defensive Midfield": "MF",
    "Center Midfield": "MF",
    "Left Center Midfield": "MF",
    "Right Center Midfield": "MF",
    "Attacking Midfield": "MF",
    "Left Attacking Midfield": "MF",
    "Right Attacking Midfield": "MF",
    "Left Midfield": "MF",
    "Right Midfield": "MF",
    "Left Wing": "FW",
    "Right Wing": "FW",
    "Left Center Forward": "FW",
    "Right Center Forward": "FW",
    "Center Forward": "FW",
    "Striker": "FW",
    "Secondary Striker": "FW",
}
