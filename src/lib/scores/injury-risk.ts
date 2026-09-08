import { clamp, lerp } from "./math";

export function injuryRiskInputs(args: {
  sleepHours: number;
  hrvRmssd: number;
  medianHrv14: number;
  workload: number;
  meanWorkload7: number;
  previousInjury: boolean;
}) {
  const sleepDebt = 1 - lerp(args.sleepHours, 5.0, 8.0);
  const hrvDrop = Math.max(
    0,
    (args.medianHrv14 - args.hrvRmssd) / Math.max(args.medianHrv14, 1),
  );
  const spike = Math.max(
    0,
    args.workload / Math.max(args.meanWorkload7, 0.5) - 1,
  );
  const hist = args.previousInjury ? 1 : 0;
  return { sleepDebt, hrvDrop, spike, hist };
}

export function injuryRiskScore(parts: {
  sleepDebt: number;
  hrvDrop: number;
  spike: number;
  hist: number;
}): number {
  const raw =
    28 * parts.sleepDebt +
    27 * clamp(parts.hrvDrop / 0.25, 0, 1) +
    25 * clamp(parts.spike / 0.4, 0, 1) +
    20 * parts.hist;
  return clamp(Math.round(raw), 0, 100);
}