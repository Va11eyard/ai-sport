# Heuristic readiness — keep in sync with src/lib/scores/readiness.ts


def _lerp(x: float, a: float, b: float) -> float:
    if b == a:
        return 0.0
    t = (x - a) / (b - a)
    return max(0.0, min(1.0, t))


def readiness_score(recovery: int, workload: float, hrv_rmssd: float) -> int:
    value = (
        recovery * 0.55
        + (1 - _lerp(workload, 4, 18)) * 20
        + _lerp(hrv_rmssd, 25, 80) * 25
    )
    return max(0, min(100, round(value)))