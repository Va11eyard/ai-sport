import { rosterAthletes } from "@/src/lib/athletes/roster";
import {
  ATHLETE_COUNT,
  DAYS,
  LOW_SLEEP_H,
  RANGES,
  SEED_KEY,
} from "@/src/lib/scores/constants";
import { breakdownFactors } from "@/src/lib/scores/factors";
import { injuryRiskInputs, injuryRiskScore } from "@/src/lib/scores/injury-risk";
import { clamp, mean, median } from "@/src/lib/scores/math";
import { readinessScore } from "@/src/lib/scores/readiness";
import { recoveryScore } from "@/src/lib/scores/recovery";
import type {
  Athlete,
  DailyPhysio,
  IsoDate,
  SyntheticMeta,
} from "@/src/lib/wearables/types";
import { gauss, hashString, mulberry32 } from "./rng";

export const DEFAULT_AS_OF: IsoDate = "2026-09-08";

function addDays(iso: IsoDate, days: number): IsoDate {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

function dateRange(asOf: IsoDate, days: number): IsoDate[] {
  const start = addDays(asOf, -(days - 1));
  return Array.from({ length: days }, (_, i) => addDays(start, i));
}

function pickGaps(rng: () => number, dates: IsoDate[], asOf: IsoDate): Set<IsoDate> {
  const candidates = dates.filter((d) => d !== asOf);
  const gaps = new Set<IsoDate>();
  while (gaps.size < 5 && candidates.length > 0) {
    const i = Math.floor(rng() * candidates.length);
    gaps.add(candidates.splice(i, 1)[0]);
  }
  return gaps;
}

function inRange(
  n: number,
  range: { min: number; max: number },
  digits = 2,
): number {
  const v = clamp(n, range.min, range.max);
  return Number(v.toFixed(digits));
}

export type SyntheticBundle = {
  athletes: Athlete[];
  snapshots: DailyPhysio[];
  meta: SyntheticMeta;
};

export function generateSynthetic(
  seedKey = SEED_KEY,
  asOf: IsoDate = DEFAULT_AS_OF,
): SyntheticBundle {
  const athletes = rosterAthletes();
  if (athletes.length !== ATHLETE_COUNT) {
    throw new Error("roster size");
  }
  const dates = dateRange(asOf, DAYS);
  const snapshots: DailyPhysio[] = [];

  for (const athlete of athletes) {
    const gapRng = mulberry32(hashString(`${seedKey}:gaps:${athlete.id}`));
    const gaps = pickGaps(gapRng, dates, asOf);
    const skipToday = athlete.id === "wp-24" || athlete.id === "wp-25";
    const history: DailyPhysio[] = [];
    const sleep0 = 6.6 + (hashString(athlete.id) % 150) / 1000;

    for (const date of dates) {
      if (gaps.has(date) || (skipToday && date === asOf)) {
        continue;
      }
      const rng = mulberry32(hashString(`${seedKey}:${athlete.id}:${date}`));
      const illness = rng() < 0.04 ? 1 : 0;
      const sleepHours = inRange(
        sleep0 + gauss(rng) * 0.55 - 0.9 * illness,
        RANGES.sleepHours,
      );
      const restingHr = inRange(
        52 + (7.2 - sleepHours) * 4.1 + gauss(rng) * 1.4,
        RANGES.restingHr,
        1,
      );
      const hrvRmssd = inRange(
        58 -
          (restingHr - 52) * 2.2 -
          (7.2 - sleepHours) * 3.0 +
          gauss(rng) * 3,
        RANGES.hrvRmssd,
        1,
      );
      const utcDay = new Date(`${date}T00:00:00Z`).getUTCDay();
      const rest = utcDay === 0 || rng() < 0.1;
      const planned = rest ? 0 : 8 + rng() * 10;
      const hrvHist = history.slice(-14).map((s) => s.hrvRmssd);
      const wlHist = history.slice(-7).map((s) => s.workload);
      const parts = injuryRiskInputs({
        sleepHours,
        hrvRmssd,
        medianHrv14: hrvHist.length ? median(hrvHist) : hrvRmssd,
        workload: planned,
        meanWorkload7: wlHist.length ? mean(wlHist) : 0.5,
        previousInjury: athlete.previousInjury,
      });
      const recovery = recoveryScore(sleepHours, hrvRmssd, restingHr);
      const injuryRisk = injuryRiskScore(parts);
      let workload = inRange(planned, RANGES.workload, 1);
      let missedSession = false;
      if (injuryRisk >= 70 && planned > 0 && rng() < 0.55) {
        missedSession = true;
        workload = 0;
      }
      const readiness = readinessScore(recovery, workload, hrvRmssd);
      const row: DailyPhysio = {
        athleteId: athlete.id,
        date,
        sleepHours,
        restingHr,
        hrvRmssd,
        workload,
        recovery,
        readiness,
        injuryRisk,
        missedSession,
      };
      history.push(row);
      snapshots.push(row);
    }
  }

  return {
    athletes,
    snapshots,
    meta: {
      seedKey,
      asOf,
      athleteCount: ATHLETE_COUNT,
      days: DAYS,
    },
  };
}

export function assertPhysiologyCorrelations(snapshots: DailyPhysio[]) {
  const low = snapshots.filter((s) => s.sleepHours < LOW_SLEEP_H);
  const high = snapshots.filter((s) => s.sleepHours >= 7.2);
  if (low.length === 0 || high.length === 0) {
    throw new Error("not enough sleep buckets");
  }
  const avg = (xs: DailyPhysio[], key: keyof DailyPhysio) =>
    xs.reduce((a, s) => a + (s[key] as number), 0) / xs.length;
  if (!(avg(low, "restingHr") > avg(high, "restingHr"))) {
    throw new Error("rhr correlation");
  }
  if (!(avg(low, "hrvRmssd") < avg(high, "hrvRmssd"))) {
    throw new Error("hrv correlation");
  }
  if (!(avg(low, "injuryRisk") > avg(high, "injuryRisk"))) {
    throw new Error("risk correlation");
  }
}

export function factorFromSnapshot(
  snap: DailyPhysio,
  previousInjury: boolean,
  history: DailyPhysio[],
) {
  const hrvHist = history.map((s) => s.hrvRmssd);
  const wlHist = history.map((s) => s.workload);
  const parts = injuryRiskInputs({
    sleepHours: snap.sleepHours,
    hrvRmssd: snap.hrvRmssd,
    medianHrv14: hrvHist.length ? median(hrvHist) : snap.hrvRmssd,
    workload: snap.workload,
    meanWorkload7: wlHist.length ? mean(wlHist) : 0.5,
    previousInjury,
  });
  return breakdownFactors(parts);
}