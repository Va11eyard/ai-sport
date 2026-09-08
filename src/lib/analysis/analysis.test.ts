import { describe, expect, it } from "vitest";
import {
  analysisKeyReady,
  bulletsFromModelText,
  buildAnalysisPrompt,
  hasNamedInjuryClaim,
} from "./parse";

describe("analysis key", () => {
  it("is unconfigured without ANTHROPIC_API_KEY", () => {
    expect(analysisKeyReady({ ANTHROPIC_API_KEY: undefined })).toBe(false);
    expect(analysisKeyReady({ ANTHROPIC_API_KEY: "sk-ant" })).toBe(true);
  });
});

describe("hasNamedInjuryClaim", () => {
  it("flags named-injury probability copy", () => {
    expect(hasNamedInjuryClaim("Вероятность травмы плеча 34%")).toBe(true);
    expect(hasNamedInjuryClaim("Флаг риска — рекомендуется консультация врача")).toBe(
      false,
    );
  });
});

describe("bulletsFromModelText", () => {
  it("parses 2-5 russian bullets", () => {
    const parsed = bulletsFromModelText(
      JSON.stringify({
        bullets: [
          "Сон 7.2 ч, HRV в зоне; нагрузку не расширять.",
          "Recovery 72: без утренней высокоинтенсивной работы.",
        ],
      }),
    );
    expect(parsed.ok).toBe(true);
    if (parsed.ok) expect(parsed.bullets).toHaveLength(2);
  });

  it("rejects named injury probability in bullets", () => {
    const parsed = bulletsFromModelText(
      JSON.stringify({
        bullets: ["Вероятность разрыва ACL 23%", "Контроль сна"],
      }),
    );
    expect(parsed.ok).toBe(false);
  });

  it("parses JSON wrapped in prose", () => {
    const parsed = bulletsFromModelText(
      'ok\n{"bullets":["Сон в норме, без расширения объёма.","HRV стабилен, контроль завтра."]}',
    );
    expect(parsed.ok).toBe(true);
  });

  it("rejects invalid json", () => {
    expect(bulletsFromModelText("not json").ok).toBe(false);
  });

  it("rejects inner braces that are not json", () => {
    expect(bulletsFromModelText("xx {nope} yy").ok).toBe(false);
  });
});

describe("buildAnalysisPrompt", () => {
  it("builds a prompt without named-injury diagnosis", () => {
    const p = buildAnalysisPrompt({
      recovery: 70,
      readiness: 80,
      injuryRisk: 40,
      sleepHours: 7,
      hrvRmssd: 50,
      psych: { stress: 4, burnout: 3, mood: 6 },
    });
    expect(p).toMatch(/чек-ин стресс=4/);
    expect(p).toMatch(/recovery=70/);
    expect(p.toLowerCase()).not.toMatch(/acl|крест/);
  });
});
