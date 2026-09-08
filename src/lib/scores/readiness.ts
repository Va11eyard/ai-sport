import { clamp, lerp } from "./math";

export function readinessScore(
  recovery: number,
  workload: number,
  hrvRmssd: number,
): number {
  const value =
    recovery * 0.55 +
    (1 - lerp(workload, 4, 18)) * 20 +
    lerp(hrvRmssd, 25, 80) * 25;
  return clamp(Math.round(value), 0, 100);
}