import { clamp, lerp } from "./math";

export function recoveryScore(
  sleepHours: number,
  hrvRmssd: number,
  restingHr: number,
): number {
  const sleepTerm = lerp(sleepHours, 4.5, 8.2) * 40;
  const hrvTerm = lerp(hrvRmssd, 25, 80) * 35;
  const rhrTerm = (1 - lerp(restingHr, 48, 72)) * 25;
  return clamp(Math.round(sleepTerm + hrvTerm + rhrTerm), 0, 100);
}