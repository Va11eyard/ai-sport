import { describe, expect, it } from "vitest";
import { AdapterError } from "./errors";
import { TerraWearableAdapter } from "./terra-adapter";
import { generateSynthetic } from "@/src/lib/synthetic/generate";
import { seriesForAthlete } from "./queries";

describe("wearable adapter contract", () => {
  it("generated snapshots have the stable schema", () => {
    const row = generateSynthetic().snapshots[0];
    expect(row).toEqual(
      expect.objectContaining({
        athleteId: expect.any(String),
        date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
        sleepHours: expect.any(Number),
        restingHr: expect.any(Number),
        hrvRmssd: expect.any(Number),
        workload: expect.any(Number),
        recovery: expect.any(Number),
        readiness: expect.any(Number),
        injuryRisk: expect.any(Number),
        missedSession: expect.any(Boolean),
      }),
    );
  });

  it("terra without credentials raises configured error", async () => {
    delete process.env.TERRA_API_KEY;
    const terra = new TerraWearableAdapter();
    await expect(
      terra.athleteSeries("wp-01", "2026-08-01", "2026-09-08"),
    ).rejects.toMatchObject({
      code: "source_not_configured",
    });
    expect(
      () => {
        throw new AdapterError(
          "source_not_configured",
          "источник не сконфигурирован",
        );
      },
    ).toThrow(/не сконфигурирован/);
  });

  it("series uses nulls for gaps not zeros", () => {
    const bundle = generateSynthetic();
    const athlete = bundle.athletes[0];
    const from = addFrom(bundle.meta.asOf, -89);
    const series = seriesForAthlete(
      bundle.snapshots.filter((s) => s.athleteId === athlete.id),
      athlete.id,
      from,
      bundle.meta.asOf,
    );
    expect(series.some((s) => s === null)).toBe(true);
  });
});

function addFrom(iso: string, days: number) {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}