import { FLAG_THRESHOLD } from "@/src/lib/scores/constants";
import { addDays, mean } from "@/src/lib/scores/math";
import {
  availabilityForToday,
  primaryWhyLabel,
  sortTeamQueue,
} from "@/src/lib/athletes/availability";
import type { Availability } from "@/src/lib/athletes/availability";
import type { WearableAdapter } from "@/src/lib/wearables/interface";
import type { Athlete, DailyPhysio, RiskZone, Trend } from "@/src/lib/wearables/types";
import { factorsFor } from "@/src/lib/wearables/queries";

export type TeamRow = {
  athlete: Athlete;
  today: DailyPhysio | null;
  hrv7: (number | null)[];
  zone: RiskZone;
  trend: Trend;
  availability: Availability;
  why: string;
};

export async function buildTeamRowsFromAdapter(
  adapter: WearableAdapter,
  asOf: string,
): Promise<TeamRow[]> {
  const athletes = await adapter.roster();
  const rows = await Promise.all(
    athletes.map(async (athlete) => {
      const today = await adapter.todaySnapshot(athlete.id, asOf);
      const series = await adapter.athleteSeries(
        athlete.id,
        addDays(asOf, -13),
        asOf,
      );
      const last7 = series.slice(-7).map((s) => s?.hrvRmssd ?? null);
      const prev7 = series.slice(0, 7).map((s) => s?.hrvRmssd ?? null);
      const hist = series
        .slice(0, -1)
        .filter((s): s is DailyPhysio => s != null);
      return assembleRow(athlete, today, last7, prev7, hist);
    }),
  );
  return queue(rows);
}

export function buildTeamRows(
  athletes: Athlete[],
  snapshots: DailyPhysio[],
  asOf: string,
): TeamRow[] {
  return queue(
    athletes.map((athlete) => {
      const mine = snapshots
        .filter((s) => s.athleteId === athlete.id)
        .sort((a, b) => a.date.localeCompare(b.date));
      const today = mine.find((s) => s.date === asOf) ?? null;
      const last7 = lastN(mine, asOf, 7);
      const prev7 = lastN(mine, addDays(asOf, -7), 7);
      const hist = mine.filter((s) => s.date < asOf);
      return assembleRow(athlete, today, last7, prev7, hist);
    }),
  );
}

function assembleRow(
  athlete: Athlete,
  today: DailyPhysio | null,
  last7: (number | null)[],
  prev7: (number | null)[],
  hist: DailyPhysio[],
): TeamRow {
  const a = mean(last7.filter((n): n is number => n != null));
  const b = mean(prev7.filter((n): n is number => n != null));
  let trend: Trend = "flat";
  if (last7.some((n) => n != null) && prev7.some((n) => n != null)) {
    if (a > b + 1) trend = "up";
    else if (a < b - 1) trend = "down";
  }
  const zone: RiskZone = !today
    ? "missing"
    : today.injuryRisk >= FLAG_THRESHOLD
      ? "flag"
      : "normal";
  const availability = availabilityForToday(today);
  const why = primaryWhyLabel(
    availability === "missing" ? null : factorsFor(athlete, today, hist),
    availability,
  );
  return { athlete, today, hrv7: last7, zone, trend, availability, why };
}

function queue(rows: TeamRow[]): TeamRow[] {
  return sortTeamQueue(
    rows.map((r) => ({ ...r, readiness: r.today?.readiness ?? null })),
  ).map(({ readiness: _r, ...row }) => row);
}

function lastN(mine: DailyPhysio[], end: string, n: number): (number | null)[] {
  const out: (number | null)[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const date = addDays(end, -i);
    out.push(mine.find((s) => s.date === date)?.hrvRmssd ?? null);
  }
  return out;
}
