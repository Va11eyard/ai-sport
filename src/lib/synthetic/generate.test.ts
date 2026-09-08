import { describe, expect, it } from "vitest";
import {
  assertPhysiologyCorrelations,
  generateSynthetic,
} from "./generate";
import { ATHLETE_COUNT, DAYS, RANGES } from "@/src/lib/scores/constants";

describe("synthetic seed", () => {
  it("creates 25 athletes and ~90 days with correlations", () => {
    const a = generateSynthetic();
    expect(a.athletes).toHaveLength(ATHLETE_COUNT);
    const byId = new Map<string, number>();
    for (const s of a.snapshots) {
      byId.set(s.athleteId, (byId.get(s.athleteId) ?? 0) + 1);
    }
    expect(byId.size).toBe(ATHLETE_COUNT);
    for (const n of byId.values()) {
      expect(n).toBeLessThanOrEqual(DAYS);
      expect(n).toBeGreaterThanOrEqual(DAYS - 7);
    }
    assertPhysiologyCorrelations(a.snapshots);
  });

  it("is reproducible with the same seed key", () => {
    const a = JSON.stringify(generateSynthetic());
    const b = JSON.stringify(generateSynthetic());
    expect(a).toBe(b);
  });

  it("clamps metrics", () => {
    for (const s of generateSynthetic().snapshots) {
      expect(s.sleepHours).toBeGreaterThanOrEqual(RANGES.sleepHours.min);
      expect(s.sleepHours).toBeLessThanOrEqual(RANGES.sleepHours.max);
      expect(s.restingHr).toBeGreaterThanOrEqual(RANGES.restingHr.min);
      expect(s.restingHr).toBeLessThanOrEqual(RANGES.restingHr.max);
      expect(s.hrvRmssd).toBeGreaterThanOrEqual(RANGES.hrvRmssd.min);
      expect(s.hrvRmssd).toBeLessThanOrEqual(RANGES.hrvRmssd.max);
      expect(s.workload).toBeGreaterThanOrEqual(RANGES.workload.min);
      expect(s.workload).toBeLessThanOrEqual(RANGES.workload.max);
      expect(s.readiness).toBeGreaterThanOrEqual(0);
      expect(s.readiness).toBeLessThanOrEqual(100);
      expect(s.recovery).toBeGreaterThanOrEqual(0);
      expect(s.recovery).toBeLessThanOrEqual(100);
      expect(s.injuryRisk).toBeGreaterThanOrEqual(0);
      expect(s.injuryRisk).toBeLessThanOrEqual(100);
    }
  });
});