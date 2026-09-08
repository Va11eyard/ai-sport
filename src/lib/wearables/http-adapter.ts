import { AdapterError } from "./errors";
import type { WearableAdapter } from "./interface";
import type {
  Athlete,
  DailyPhysio,
  DayAnalysis,
  InjuryFactors,
  IsoDate,
  Recommendation,
  TeamSummary,
} from "./types";

const base = () => process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

async function getJson<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${base()}${path}`, { cache: "no-store" });
  } catch {
    throw new AdapterError("source_not_configured", "источник не сконфигурирован");
  }
  if (res.status === 503) {
    throw new AdapterError("source_not_configured", "источник не сконфигурирован");
  }
  if (!res.ok) {
    throw new AdapterError("invalid_snapshot", `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export class HttpWearableAdapter implements WearableAdapter {
  async asOf(): Promise<IsoDate> {
    const meta = await getJson<{ asOf: IsoDate }>("/meta");
    return meta.asOf;
  }

  async roster() {
    return getJson<Athlete[]>("/athletes");
  }

  async teamSummary(today: IsoDate) {
    return getJson<TeamSummary>(`/summary?today=${today}`);
  }

  async todaySnapshot(athleteId: string, today: IsoDate) {
    return getJson<DailyPhysio | null>(
      `/athletes/${athleteId}/snapshot?today=${today}`,
    );
  }

  async athleteSeries(athleteId: string, from: IsoDate, to: IsoDate) {
    return getJson<(DailyPhysio | null)[]>(
      `/athletes/${athleteId}/series?from=${from}&to=${to}`,
    );
  }

  async todayRecommendations(athleteId: string, today: IsoDate) {
    return getJson<Recommendation[]>(
      `/athletes/${athleteId}/recommendations?today=${today}`,
    );
  }

  async injuryFactorBreakdown(athleteId: string, today: IsoDate) {
    return getJson<InjuryFactors>(
      `/athletes/${athleteId}/injury-factors?today=${today}`,
    );
  }

  async todayAnalysis(athleteId: string, today: IsoDate) {
    return getJson<DayAnalysis>(
      `/athletes/${athleteId}/analysis?today=${today}`,
    );
  }
}