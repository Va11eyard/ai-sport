import { createHmac } from "node:crypto";
import { describe, expect, it } from "vitest";
import { terraSourceReady, verifyTerraHmac } from "./hmac";
import { mapTerraDay, terraDayFromWebhook } from "./map";

describe("terra hmac", () => {
  it("accepts hmac-sha256 of the raw body", () => {
    const secret = "whsec_test";
    const body = '{"user":{"user_id":"u1"}}';
    const header = createHmac("sha256", secret).update(body).digest("hex");
    expect(verifyTerraHmac(body, header, secret)).toBe(true);
  });

  it("accepts v1= hex in the signature header", () => {
    const secret = "whsec_test";
    const body = "{}";
    const hex = createHmac("sha256", secret).update(body).digest("hex");
    expect(verifyTerraHmac(body, `t=1,v1=${hex}`, secret)).toBe(true);
  });

  it("rejects missing header and odd hex", () => {
    expect(verifyTerraHmac("{}", undefined, "s")).toBe(false);
    expect(verifyTerraHmac("{}", "abc", "secret")).toBe(false);
  });
});

describe("terra source ready", () => {
  it("is unconfigured without API key", () => {
    expect(terraSourceReady({ TERRA_API_KEY: "" })).toBe(false);
    expect(terraSourceReady({ TERRA_API_KEY: "tk" })).toBe(true);
  });
});

describe("mapTerraDay", () => {
  it("maps sleep HRV resting HR and clamps sleep into schema range", () => {
    const day = mapTerraDay({
      userId: "terra-1",
      date: "2026-09-08",
      sleepSeconds: 3 * 3600,
      restingHr: 50,
      hrvRmssd: 55,
      activeSeconds: 3600,
    });
    expect(day.date).toBe("2026-09-08");
    expect(day.sleepHours).toBe(4);
    expect(day.restingHr).toBe(50);
    expect(day.hrvRmssd).toBe(55);
    expect(day.workload).toBeGreaterThan(0);
    expect(day.workload).toBeLessThanOrEqual(21);
  });

  it("throws on a bad date", () => {
    expect(() =>
      mapTerraDay({
        userId: "u",
        date: "08-09-2026",
        sleepSeconds: 8 * 3600,
        restingHr: 52,
        hrvRmssd: 40,
        activeSeconds: 0,
      }),
    ).toThrow(/date/i);
  });

  it("throws when user id is empty", () => {
    expect(() =>
      mapTerraDay({
        userId: "",
        date: "2026-09-08",
        sleepSeconds: 8 * 3600,
        restingHr: 52,
        hrvRmssd: 40,
        activeSeconds: 0,
      }),
    ).toThrow(/user/i);
  });

  it("reads a Terra-shaped webhook payload", () => {
    const input = terraDayFromWebhook({
      user: { user_id: "u-apple" },
      data: [
        {
          metadata: { start_time: "2026-09-08T00:00:00Z" },
          sleep_durations_data: {
            asleep: { duration_asleep_state_seconds: 8 * 3600 },
            sleep_efficiency: 90,
            asleep_duration_rem_seconds: 3600,
            asleep_duration_deep_seconds: 5400,
          },
          heart_rate_data: { summary: { resting_hr_bpm: 48 } },
          hrv_data: { summary: { rmssd: 60 } },
          active_durations_data: { activity_seconds: 1800 },
        },
      ],
    });
    expect(input.userId).toBe("u-apple");
    expect(input.date).toBe("2026-09-08");
    expect(input.sleepSeconds).toBe(8 * 3600);
    const day = mapTerraDay(input);
    expect(day.sleepHours).toBe(8);
    expect(day.remHours).toBe(1);
  });

  it("uses defaults when webhook fields are missing", () => {
    const input = terraDayFromWebhook({});
    expect(input.userId).toBe("");
    expect(input.restingHr).toBe(55);
  });
});
