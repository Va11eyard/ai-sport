# Stub for Terra API. Same fields as TS DailyPhysio.
# Real fetch comes later; UI uses WearableAdapter in Next.js.

from __future__ import annotations

from dataclasses import dataclass


class SourceNotConfigured(Exception):
    pass


@dataclass
class DailyPhysio:
    athleteId: str
    date: str
    sleepHours: float
    restingHr: float
    hrvRmssd: float
    workload: float
    recovery: int
    readiness: int
    injuryRisk: int
    missedSession: bool


def fetch_series(athlete_id: str) -> list[DailyPhysio]:
    raise SourceNotConfigured("источник не сконфигурирован")