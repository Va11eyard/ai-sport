export type DayPayload = {
  snapshot: {
    sleepHours: number;
    restingHr: number;
    hrvRmssd: number;
    workload: number;
    recovery: number;
    readiness: number;
    injuryRisk: number;
  } | null;
  extras: {
    respRate: number | null;
    temperature: number | null;
    weightKg: number | null;
    bodyFatPct: number | null;
    muscleMassKg: number | null;
    sleepEfficiency: number | null;
    remHours: number | null;
    deepHours: number | null;
    awakenings: number | null;
    sleepLatencyMin: number | null;
  } | null;
  lab: Record<string, number | null> | null;
  psych: {
    stress: number;
    motivation: number;
    anxiety: number;
    burnout: number;
    mood: number;
    cognitive: number;
  } | null;
  nutrition: {
    kcal: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
    waterL: number;
  } | null;
  training: {
    distanceM: number | null;
    shots: number | null;
  } | null;
};
