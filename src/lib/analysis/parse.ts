export type AnalysisStatus =
  | "ok"
  | "unconfigured"
  | "no_snapshot"
  | "upstream_error"
  | "invalid_output";

export type DayAnalysis = {
  status: AnalysisStatus;
  bullets: string[];
};

export function analysisKeyReady(env: { ANTHROPIC_API_KEY?: string }): boolean {
  return Boolean(env.ANTHROPIC_API_KEY?.trim());
}

export function hasNamedInjuryClaim(text: string): boolean {
  const t = text.toLowerCase();
  if (!t.includes("вероятност")) return false;
  return /плеч|acl|крест|колен|локте|голеностоп/.test(t);
}

function readBullets(parsed: unknown): string[] | null {
  if (!parsed || typeof parsed !== "object" || !("bullets" in parsed)) {
    return null;
  }
  const raw = (parsed as { bullets: unknown }).bullets;
  if (!Array.isArray(raw) || raw.length < 2 || raw.length > 5) return null;
  const bullets: string[] = [];
  for (const item of raw) {
    if (typeof item !== "string") return null;
    const s = item.trim();
    if (s.length < 8 || s.length > 280) return null;
    bullets.push(s);
  }
  return bullets;
}

export function bulletsFromModelText(
  text: string,
): { ok: true; bullets: string[] } | { ok: false } {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    const start = text.indexOf("{");
    const end = text.lastIndexOf("}");
    if (start < 0 || end < 0) return { ok: false };
    try {
      parsed = JSON.parse(text.slice(start, end + 1));
    } catch {
      return { ok: false };
    }
  }
  const bullets = readBullets(parsed);
  if (!bullets) return { ok: false };
  if (hasNamedInjuryClaim(bullets.join(" "))) return { ok: false };
  return { ok: true, bullets };
}

export function buildAnalysisPrompt(input: {
  recovery: number;
  readiness: number;
  injuryRisk: number;
  sleepHours: number;
  hrvRmssd: number;
  psych?: { stress: number; burnout: number; mood: number } | null;
}): string {
  return [
    "Ты помощник спортивного врача. Ответь ТОЛЬКО JSON {\"bullets\":[...]} 2–5 коротких фраз на русском.",
    "Не называй вероятность именованной травмы. Не ставь диагнозы суставов.",
    `recovery=${input.recovery} readiness=${input.readiness} injuryRisk=${input.injuryRisk}`,
    `сон_ч=${input.sleepHours} HRV=${input.hrvRmssd}`,
    input.psych
      ? `чек-ин стресс=${input.psych.stress} выгорание=${input.psych.burnout} настроение=${input.psych.mood}`
      : "чек-ин нет",
  ].join("\n");
}
