import type {
  Athlete,
  DailyPhysio,
  DayAnalysis,
  InjuryFactors,
  IsoDate,
  Recommendation,
  TeamSummary,
} from "./types";

export interface WearableAdapter {
  roster(): Promise<Athlete[]>;
  teamSummary(today: IsoDate): Promise<TeamSummary>;
  todaySnapshot(
    athleteId: string,
    today: IsoDate,
  ): Promise<DailyPhysio | null>;
  athleteSeries(
    athleteId: string,
    from: IsoDate,
    to: IsoDate,
  ): Promise<(DailyPhysio | null)[]>;
  todayRecommendations(
    athleteId: string,
    today: IsoDate,
  ): Promise<Recommendation[]>;
  injuryFactorBreakdown(
    athleteId: string,
    today: IsoDate,
  ): Promise<InjuryFactors>;
  asOf(): Promise<IsoDate>;
  todayAnalysis(athleteId: string, today: IsoDate): Promise<DayAnalysis>;
}