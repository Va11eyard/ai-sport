import { describe, expect, it } from "vitest";
import { FLAG_THRESHOLD } from "@/src/lib/scores/constants";
import {
  availabilityForToday,
  countAvailability,
  needsAttention,
  primaryWhyLabel,
  sortTeamQueue,
} from "./availability";
import { generateSynthetic } from "@/src/lib/synthetic/generate";
import { computeTeamSummary } from "@/src/lib/wearables/queries";
import { buildTeamRows } from "./teamRows";
import type { DailyPhysio, InjuryFactors } from "@/src/lib/wearables/types";

function snap(over: Partial<DailyPhysio>): DailyPhysio {
  return {
    athleteId: "wp-01",
    date: "2026-09-08",
    sleepHours: 7.5,
    restingHr: 52,
    hrvRmssd: 60,
    workload: 10,
    recovery: 70,
    readiness: 70,
    injuryRisk: 40,
    missedSession: false,
    ...over,
  };
}

describe("daily availability", () => {
  it("maps snapshot to water / restricted / out / missing", () => {
    expect(availabilityForToday(null)).toBe("missing");
    expect(availabilityForToday(snap({ injuryRisk: FLAG_THRESHOLD - 1 }))).toBe(
      "water",
    );
    expect(
      availabilityForToday(snap({ injuryRisk: FLAG_THRESHOLD })),
    ).toBe("restricted");
    expect(
      availabilityForToday(snap({ missedSession: true, injuryRisk: 80 })),
    ).toBe("out");
  });

  it("does not treat missing data as out", () => {
    expect(availabilityForToday(null)).not.toBe("out");
    expect(
      countAvailability(["missing", "water", "water", "restricted", "out"]),
    ).toEqual({
      availableCount: 2,
      restrictedCount: 1,
      outCount: 1,
    });
  });

  it("queues missing, out and flagged ahead of water", () => {
    const ordered = sortTeamQueue([
      { id: "ok", availability: "water" as const, readiness: 90 },
      { id: "gap", availability: "missing" as const, readiness: null },
      { id: "ok2", availability: "water" as const, readiness: 80 },
      { id: "out", availability: "out" as const, readiness: 50 },
      { id: "flag", availability: "restricted" as const, readiness: 40 },
    ]);
    expect(ordered.map((r) => r.id)).toEqual(["gap", "out", "flag", "ok", "ok2"]);
    expect(sortTeamQueue([])).toEqual([]);
    expect(needsAttention("missing")).toBe(true);
    expect(needsAttention("out")).toBe(true);
    expect(needsAttention("restricted")).toBe(true);
    expect(needsAttention("water")).toBe(false);
  });

  it("names the largest factor without a named injury", () => {
    const factors: InjuryFactors = {
      workloadSpike: 40,
      sleepDebt: 30,
      hrvDrop: 30,
      previousInjury: 0,
    };
    expect(primaryWhyLabel(factors, "water")).toBe("пик нагрузки");
    expect(
      primaryWhyLabel(
        { workloadSpike: 1, sleepDebt: 90, hrvDrop: 1, previousInjury: 0 },
        "water",
      ),
    ).toBe("долг сна");
    expect(
      primaryWhyLabel(
        { workloadSpike: 1, sleepDebt: 1, hrvDrop: 90, previousInjury: 0 },
        "restricted",
      ),
    ).toBe("падение HRV");
    expect(primaryWhyLabel(null, "missing")).toBe("нет снимка");
    expect(primaryWhyLabel(factors, "missing")).toBe("нет снимка");
    expect(primaryWhyLabel(factors, "water")).not.toMatch(/acl|крест|разрыв/i);
    expect(
      primaryWhyLabel(
        { workloadSpike: 10, sleepDebt: 10, hrvDrop: 10, previousInjury: 50 },
        "restricted",
      ),
    ).toBe("анамнез");
  });

  it("counts water/restricted/out from snapshots without treating gaps as out", () => {
    const bundle = generateSynthetic();
    const summary = computeTeamSummary(
      bundle.athletes,
      bundle.snapshots,
      bundle.meta.asOf,
    );
    expect(
      summary.availableCount + summary.restrictedCount + summary.outCount,
    ).toBeLessThanOrEqual(bundle.athletes.length);
    expect(
      summary.availableCount + summary.restrictedCount + summary.outCount,
    ).toBe(bundle.athletes.length - 2);
    const rows = buildTeamRows(
      bundle.athletes,
      bundle.snapshots,
      bundle.meta.asOf,
    );
    const missing = rows.filter((r) => r.availability === "missing");
    expect(missing).toHaveLength(2);
    expect(missing.every((r) => r.why === "нет снимка")).toBe(true);
    expect(rows[0]?.availability).not.toBe("water");
    expect(summary.outCount).toBe(
      rows.filter((r) => r.availability === "out").length,
    );
    expect(summary.restrictedCount).toBe(
      rows.filter((r) => r.availability === "restricted").length,
    );
    expect(summary.availableCount).toBe(
      rows.filter((r) => r.availability === "water").length,
    );
    expect(rows.some((r) => /acl|крест/i.test(r.why))).toBe(false);
  });
});
