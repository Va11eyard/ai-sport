export const SEED_KEY = "dat-waterpolo-v1";
export const ATHLETE_COUNT = 25;
export const DAYS = 90;
export const FLAG_THRESHOLD = 62;
export const LOW_SLEEP_H = 6.2;
export const WORKLOAD_SPIKE_REL = 0.25;

export const RANGES = {
  sleepHours: { min: 4.0, max: 9.5 },
  restingHr: { min: 42, max: 78 },
  hrvRmssd: { min: 18, max: 95 },
  workload: { min: 0, max: 21 },
  score: { min: 0, max: 100 },
} as const;