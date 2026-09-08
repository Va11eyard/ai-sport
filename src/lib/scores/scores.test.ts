import { describe, expect, it } from "vitest";
import { breakdownFactors } from "@/src/lib/scores/factors";
import { recoveryScore } from "@/src/lib/scores/recovery";
import { readinessScore } from "@/src/lib/scores/readiness";
import { burnoutIndex } from "@/src/lib/scores/mental";
import { todayRecommendations } from "@/src/lib/scores/recommendations";

describe("scores", () => {
  it("keeps recovery/readiness in 0-100", () => {
    expect(recoveryScore(8, 70, 50)).toBeGreaterThanOrEqual(0);
    expect(recoveryScore(8, 70, 50)).toBeLessThanOrEqual(100);
    expect(readinessScore(80, 10, 60)).toBeGreaterThanOrEqual(0);
    expect(readinessScore(80, 10, 60)).toBeLessThanOrEqual(100);
  });

  it("renormalizes factors to 100 with zero injury history", () => {
    const f = breakdownFactors({
      spike: 0.4,
      sleepDebt: 0.3,
      hrvDrop: 0.2,
      hist: 0,
    });
    expect(f.previousInjury).toBe(0);
    expect(
      f.workloadSpike + f.sleepDebt + f.hrvDrop + f.previousInjury,
    ).toBe(100);
  });

  it("does not diagnose a named injury in recommendations", () => {
    const recs = todayRecommendations({
      injuryRisk: 80,
      sleepHours: 5,
      spike: 0.4,
      hrvDrop: 0.2,
      burnoutIndex: 80,
    });
    expect(recs.length).toBeGreaterThanOrEqual(2);
    expect(recs.length).toBeLessThanOrEqual(4);
    const blob = recs.map((r) => r.text).join(" ");
    expect(blob).toMatch(/врача/);
    expect(blob).not.toMatch(/вероятност/);
    expect(blob.toLowerCase()).not.toMatch(/acl|крест/);
    expect(blob).toMatch(/психолог/);
  });

  it("maps check-in to a 0-100 burnout index", () => {
    expect(
      burnoutIndex({
        stress: 8,
        motivation: 3,
        anxiety: 7,
        burnout: 8,
        mood: 3,
        cognitive: 4,
      }),
    ).toBeGreaterThanOrEqual(65);
  });
});