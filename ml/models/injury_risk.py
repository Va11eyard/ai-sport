# Adapted from Athlete-Injury-Risk-Analyzer (low/medium/high idea), not a fork.
# https://github.com/AzaRKazar/Athlete-Injury-Risk-Analyzer — check LICENSE before commercial use.

from __future__ import annotations


def injury_risk_score(
    sleep_debt: float,
    hrv_drop: float,
    spike: float,
    hist: float,
) -> int:
    raw = (
        28 * sleep_debt
        + 27 * min(1.0, max(0.0, hrv_drop / 0.25))
        + 25 * min(1.0, max(0.0, spike / 0.4))
        + 20 * hist
    )
    return max(0, min(100, round(raw)))


def risk_band(score: int) -> str:
    if score >= 62:
        return "high"
    if score >= 40:
        return "medium"
    return "low"