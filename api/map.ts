import type { Athlete, DailyPhysio } from "../src/lib/wearables/types";
import type { Athlete as AthleteRow, DailySnapshot } from "@prisma/client";

export function toAthlete(row: AthleteRow): Athlete {
  return {
    id: row.id,
    lastName: row.lastName,
    firstName: row.firstName,
    name: `${row.lastName} ${row.firstName}`,
    position: row.position as Athlete["position"],
    previousInjury: row.previousInjury,
    terraUserId: row.terraUserId,
  };
}

export function toSnapshot(row: DailySnapshot): DailyPhysio {
  return {
    athleteId: row.athleteId,
    date: row.date,
    sleepHours: row.sleepHours,
    restingHr: row.restingHr,
    hrvRmssd: row.hrvRmssd,
    workload: row.workload,
    recovery: row.recovery,
    readiness: row.readiness,
    injuryRisk: row.injuryRisk,
    missedSession: row.missedSession,
  };
}