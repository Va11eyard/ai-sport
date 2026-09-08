import { FLAG_THRESHOLD } from "@/src/lib/scores/constants";
import { injuryRiskInputs } from "@/src/lib/scores/injury-risk";
import { mean, median } from "@/src/lib/scores/math";
import { todayRecommendations as buildRecs } from "@/src/lib/scores/recommendations";
import { factorFromSnapshot } from "@/src/lib/synthetic/generate";
import type {
  Athlete,
  DailyPhysio,
  InjuryFactors,
  IsoDate,
  Recommendation,
  TeamSummary,
} from "./types";

export function addDays(iso: IsoDate, days: number): IsoDate {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

export function enumerateDates(from: IsoDate, to: IsoDate): IsoDate[] {
  const out: IsoDate[] = [];
  let cur = from;
  while (cur <= to) {
    out.push(cur);
    cur = addDays(cur, 1);
  }
  return out;
}

export function computeTeamSummary(
  athletes: Athlete[],
  snapshots: DailyPhysio[],
  today: IsoDate,
): TeamSummary {
  const byAthleteToday = new Map(
    snapshots.filter((s) => s.date === today).map((s) => [s.athleteId, s]),
  );
  const withScore = [...byAthleteToday.values()];
  const meanReadiness =
    withScore.length === 0
      ? null
      : Math.round(
          withScore.reduce((a, s) => a + s.readiness, 0) / withScore.length,
        );
  const flaggedCount = withScore.filter(
    (s) => s.injuryRisk >= FLAG_THRESHOLD,
  ).length;
  const from = addDays(today, -6);
  const missedSessionsLast7d = snapshots.filter(
    (s) => s.date >= from && s.date <= today && s.missedSession,
  ).length;
  return {
    athleteCount: athletes.length,
    meanReadiness,
    flaggedCount,
    missedSessionsLast7d,
  };
}

export function seriesForAthlete(
  snapshots: DailyPhysio[],
  athleteId: string,
  from: IsoDate,
  to: IsoDate,
): (DailyPhysio | null)[] {
  const map = new Map(
    snapshots
      .filter((s) => s.athleteId === athleteId)
      .map((s) => [s.date, s]),
  );
  return enumerateDates(from, to).map((d) => map.get(d) ?? null);
}

export function recommendationsFor(
  athlete: Athlete | undefined,
  snap: DailyPhysio | null,
  hist: DailyPhysio[],
  burnoutIndex?: number,
): Recommendation[] {
  if (!snap) return [];
  const parts = injuryRiskInputs({
    sleepHours: snap.sleepHours,
    hrvRmssd: snap.hrvRmssd,
    medianHrv14: hist.length
      ? median(hist.map((s) => s.hrvRmssd))
      : snap.hrvRmssd,
    workload: snap.workload,
    meanWorkload7: hist.length ? mean(hist.map((s) => s.workload)) : 0.5,
    previousInjury: athlete?.previousInjury ?? false,
  });
  return buildRecs({
    injuryRisk: snap.injuryRisk,
    sleepHours: snap.sleepHours,
    spike: parts.spike,
    hrvDrop: parts.hrvDrop,
    burnoutIndex,
  });
}

export function factorsFor(
  athlete: Athlete | undefined,
  snap: DailyPhysio | null,
  hist: DailyPhysio[],
): InjuryFactors {
  if (!snap) {
    return {
      workloadSpike: 34,
      sleepDebt: 33,
      hrvDrop: 33,
      previousInjury: 0,
    };
  }
  return factorFromSnapshot(snap, athlete?.previousInjury ?? false, hist);
}