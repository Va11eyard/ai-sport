import { FLAG_THRESHOLD } from "@/src/lib/scores/constants";
import { addDays, mean } from "@/src/lib/scores/math";
import type { WearableAdapter } from "@/src/lib/wearables/interface";
import type { Athlete, DailyPhysio, RiskZone, Trend } from "@/src/lib/wearables/types";

export type TeamRow = {
  athlete: Athlete;
  today: DailyPhysio | null;
  hrv7: (number | null)[];
  zone: RiskZone;
  trend: Trend;
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
      return { athlete, today, hrv7: last7, zone, trend };
    }),
  );
  return rows.sort(
    (a, b) => (b.today?.readiness ?? -1) - (a.today?.readiness ?? -1),
  );
}

export function buildTeamRows(
  athletes: Athlete[],
  snapshots: DailyPhysio[],
  asOf: string,
): TeamRow[] {
  return athletes
    .map((athlete) => {
      const mine = snapshots
        .filter((s) => s.athleteId === athlete.id)
        .sort((a, b) => a.date.localeCompare(b.date));
      const today = mine.find((s) => s.date === asOf) ?? null;
      const last7 = lastN(mine, asOf, 7);
      const prev7 = lastN(mine, addDays(asOf, -7), 7);
      const a = mean(last7.filter((n): n is number => n != null));
      const b = mean(prev7.filter((n): n is number => n != null));
      let trend: Trend = "flat";
      if (
        last7.some((n) => n != null) &&
        prev7.some((n) => n != null)
      ) {
        if (a > b + 1) trend = "up";
        else if (a < b - 1) trend = "down";
      }
      const zone: RiskZone = !today
        ? "missing"
        : today.injuryRisk >= FLAG_THRESHOLD
          ? "flag"
          : "normal";
      return { athlete, today, hrv7: last7, zone, trend };
    })
    .sort((a, b) => (b.today?.readiness ?? -1) - (a.today?.readiness ?? -1));
}

function lastN(mine: DailyPhysio[], end: string, n: number): (number | null)[] {
  const out: (number | null)[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const date = addDays(end, -i);
    out.push(mine.find((s) => s.date === date)?.hrvRmssd ?? null);
  }
  return out;
}