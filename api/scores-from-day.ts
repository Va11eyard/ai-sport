import { injuryRiskInputs, injuryRiskScore } from "./src/lib/scores/injury-risk";
import { mean, median } from "./src/lib/scores/math";
import { readinessScore } from "./src/lib/scores/readiness";
import { recoveryScore } from "./src/lib/scores/recovery";
import type { DailyPhysio } from "./src/lib/wearables/types";

export function scoresFromDay(args: {
  sleepHours: number;
  hrvRmssd: number;
  restingHr: number;
  workload: number;
  previousInjury: boolean;
  histHrv: number[];
  histWorkload: number[];
}): Pick<DailyPhysio, "recovery" | "readiness" | "injuryRisk"> {
  const recovery = recoveryScore(args.sleepHours, args.hrvRmssd, args.restingHr);
  const parts = injuryRiskInputs({
    sleepHours: args.sleepHours,
    hrvRmssd: args.hrvRmssd,
    medianHrv14: args.histHrv.length ? median(args.histHrv) : args.hrvRmssd,
    workload: args.workload,
    meanWorkload7: args.histWorkload.length ? mean(args.histWorkload) : 0.5,
    previousInjury: args.previousInjury,
  });
  return {
    recovery,
    readiness: readinessScore(recovery, args.workload, args.hrvRmssd),
    injuryRisk: injuryRiskScore(parts),
  };
}