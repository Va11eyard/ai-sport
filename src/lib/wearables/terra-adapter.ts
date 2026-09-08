import { AdapterError } from "./errors";
import type { WearableAdapter } from "./interface";
import type { IsoDate } from "./types";

export class TerraWearableAdapter implements WearableAdapter {
  private ensure() {
    if (!process.env.TERRA_API_KEY) {
      throw new AdapterError(
        "source_not_configured",
        "источник не сконфигурирован",
      );
    }
  }

  async roster() {
    this.ensure();
    return [];
  }
  async teamSummary(_today: IsoDate) {
    this.ensure();
    return {
      athleteCount: 0,
      meanReadiness: null,
      flaggedCount: 0,
      missedSessionsLast7d: 0,
    };
  }
  async todaySnapshot(_athleteId: string, _today: IsoDate) {
    this.ensure();
    return null;
  }
  async athleteSeries(_id: string, _from: IsoDate, _to: IsoDate) {
    this.ensure();
    return [];
  }
  async todayRecommendations(_id: string, _today: IsoDate) {
    this.ensure();
    return [];
  }
  async injuryFactorBreakdown(_id: string, _today: IsoDate) {
    this.ensure();
    return {
      workloadSpike: 0,
      sleepDebt: 0,
      hrvDrop: 0,
      previousInjury: 0,
    };
  }
  async asOf() {
    this.ensure();
    return "1970-01-01";
  }

  async todayAnalysis(_athleteId: string, _today: IsoDate) {
    this.ensure();
    return { status: "unconfigured" as const, bullets: [] };
  }
}