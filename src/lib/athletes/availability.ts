import { FLAG_THRESHOLD } from "@/src/lib/scores/constants";
import type { DailyPhysio, InjuryFactors } from "@/src/lib/wearables/types";

export type Availability = "water" | "restricted" | "out" | "missing";

export const WHY_LABEL: Record<keyof InjuryFactors, string> = {
  workloadSpike: "пик нагрузки",
  sleepDebt: "долг сна",
  hrvDrop: "падение HRV",
  previousInjury: "анамнез",
};

const FACTOR_ORDER: (keyof InjuryFactors)[] = [
  "workloadSpike",
  "sleepDebt",
  "hrvDrop",
  "previousInjury",
];

const QUEUE_RANK: Record<Availability, number> = {
  missing: 0,
  out: 1,
  restricted: 2,
  water: 3,
};

export function availabilityForToday(snap: DailyPhysio | null): Availability {
  if (!snap) return "missing";
  if (snap.missedSession) return "out";
  if (snap.injuryRisk >= FLAG_THRESHOLD) return "restricted";
  return "water";
}

export function needsAttention(availability: Availability): boolean {
  return availability !== "water";
}

export function countAvailability(
  statuses: Availability[],
): { availableCount: number; restrictedCount: number; outCount: number } {
  return {
    availableCount: statuses.filter((s) => s === "water").length,
    restrictedCount: statuses.filter((s) => s === "restricted").length,
    outCount: statuses.filter((s) => s === "out").length,
  };
}

export function primaryWhyLabel(
  factors: InjuryFactors | null,
  availability: Availability,
): string {
  if (availability === "missing" || !factors) return "нет снимка";
  let best: keyof InjuryFactors = "workloadSpike";
  let max = -1;
  for (const key of FACTOR_ORDER) {
    if (factors[key] > max) {
      max = factors[key];
      best = key;
    }
  }
  return WHY_LABEL[best];
}

export function sortTeamQueue<
  T extends { availability: Availability; readiness: number | null },
>(rows: T[]): T[] {
  return [...rows].sort((a, b) => {
    const rank = QUEUE_RANK[a.availability] - QUEUE_RANK[b.availability];
    if (rank !== 0) return rank;
    return (b.readiness ?? -1) - (a.readiness ?? -1);
  });
}
