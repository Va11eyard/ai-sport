export type WaterPoloPosition =
  | "вратарь"
  | "центральный"
  | "подвижный"
  | "крайний"
  | "полусредний";

export type Position = WaterPoloPosition;

export type IsoDate = string;

export type DailyPhysio = {
  athleteId: string;
  date: IsoDate;
  sleepHours: number;
  restingHr: number;
  hrvRmssd: number;
  workload: number;
  recovery: number;
  readiness: number;
  injuryRisk: number;
  missedSession: boolean;
};

export type DayAnalysis = {
  status:
    | "ok"
    | "unconfigured"
    | "no_snapshot"
    | "upstream_error"
    | "invalid_output";
  bullets: string[];
};

export type Athlete = {
  id: string;
  lastName: string;
  firstName: string;
  name: string;
  position: WaterPoloPosition;
  previousInjury: boolean;
  terraUserId?: string | null;
};

export type RiskZone = "flag" | "normal" | "missing";
export type Trend = "up" | "down" | "flat";

export type TeamSummary = {
  athleteCount: number;
  meanReadiness: number | null;
  flaggedCount: number;
  missedSessionsLast7d: number;
};

export type InjuryFactors = {
  workloadSpike: number;
  sleepDebt: number;
  hrvDrop: number;
  previousInjury: number;
};

export type Recommendation = {
  id: string;
  text: string;
  checked: false;
};

export type SyntheticMeta = {
  seedKey: string;
  asOf: IsoDate;
  athleteCount: number;
  days: number;
};