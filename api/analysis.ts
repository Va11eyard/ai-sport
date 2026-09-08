import type { Hono } from "hono";
import { prisma } from "./db";
import {
  analysisKeyReady,
  bulletsFromModelText,
  buildAnalysisPrompt,
  type DayAnalysis,
} from "../src/lib/analysis/parse";

const MODEL = "claude-sonnet-4-6";

async function complete(prompt: string): Promise<string> {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": process.env.ANTHROPIC_API_KEY ?? "",
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 400,
      messages: [{ role: "user", content: prompt }],
    }),
  });
  if (!res.ok) throw new Error("upstream");
  const data = (await res.json()) as {
    content?: { type: string; text?: string }[];
  };
  const text = data.content?.find((p) => p.type === "text")?.text;
  if (!text) throw new Error("upstream");
  return text;
}

export function registerAnalysis(app: Hono) {
  app.get("/athletes/:id/analysis", async (c) => {
    const today = c.req.query("today");
    const empty = (status: DayAnalysis["status"]): DayAnalysis => ({
      status,
      bullets: [],
    });
    if (!today) return c.json({ error: "today required" }, 400);
    if (!analysisKeyReady(process.env)) {
      return c.json(empty("unconfigured"));
    }
    const id = c.req.param("id");
    const snap = await prisma.dailySnapshot.findUnique({
      where: { athleteId_date: { athleteId: id, date: today } },
    });
    if (!snap) return c.json(empty("no_snapshot"));
    const cached = await prisma.aiAnalysis.findUnique({
      where: { athleteId_date: { athleteId: id, date: today } },
    });
    if (cached) {
      return c.json({
        status: "ok" as const,
        bullets: JSON.parse(cached.bullets) as string[],
      });
    }
    const psych = await prisma.psychCheckin.findUnique({
      where: { athleteId_date: { athleteId: id, date: today } },
    });
    const prompt = buildAnalysisPrompt({
      recovery: snap.recovery,
      readiness: snap.readiness,
      injuryRisk: snap.injuryRisk,
      sleepHours: snap.sleepHours,
      hrvRmssd: snap.hrvRmssd,
      psych: psych
        ? {
            stress: psych.stress,
            burnout: psych.burnout,
            mood: psych.mood,
          }
        : null,
    });
    try {
      const text = await complete(prompt);
      const parsed = bulletsFromModelText(text);
      if (!parsed.ok) return c.json(empty("invalid_output"));
      await prisma.aiAnalysis.create({
        data: {
          athleteId: id,
          date: today,
          bullets: JSON.stringify(parsed.bullets),
          model: MODEL,
        },
      });
      return c.json({ status: "ok", bullets: parsed.bullets });
    } catch {
      return c.json(empty("upstream_error"));
    }
  });
}
