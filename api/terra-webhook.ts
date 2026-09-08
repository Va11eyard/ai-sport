import type { Hono } from "hono";
import { prisma } from "./db";
import { scoresFromDay } from "./scores-from-day";
import { terraSourceReady, verifyTerraHmac } from "../src/lib/terra/hmac";
import { mapTerraDay, terraDayFromWebhook } from "../src/lib/terra/map";

async function bumpAsOf(date: string) {
  const meta = await prisma.meta.findUnique({ where: { id: 1 } });
  if (!meta) {
    await prisma.meta.create({
      data: { id: 1, asOf: date, seedKey: "terra" },
    });
    return;
  }
  if (date > meta.asOf) {
    await prisma.meta.update({ where: { id: 1 }, data: { asOf: date } });
  }
}

export function registerTerraWebhook(app: Hono) {
  app.post("/webhooks/terra", async (c) => {
    if (!terraSourceReady(process.env)) {
      return c.json({ error: "источник не сконфигурирован" }, 503);
    }
    const raw = await c.req.text();
    const secret = process.env.TERRA_WEBHOOK_SECRET ?? "";
    if (!verifyTerraHmac(raw, c.req.header("terra-signature"), secret)) {
      return c.json({ error: "forbidden" }, 401);
    }
    let payload: unknown;
    try {
      payload = JSON.parse(raw);
    } catch {
      return c.json({ error: "invalid_json" }, 400);
    }
    let mapped;
    try {
      mapped = mapTerraDay(terraDayFromWebhook(payload));
    } catch {
      return c.json({ error: "invalid_payload" }, 400);
    }
    const userId = terraDayFromWebhook(payload).userId;
    const athlete = await prisma.athlete.findUnique({
      where: { terraUserId: userId },
    });
    if (!athlete) return c.json({ error: "unknown_user" }, 404);
    const hist = await prisma.dailySnapshot.findMany({
      where: { athleteId: athlete.id, date: { lt: mapped.date } },
      orderBy: { date: "desc" },
      take: 14,
    });
    const scores = scoresFromDay({
      sleepHours: mapped.sleepHours,
      hrvRmssd: mapped.hrvRmssd,
      restingHr: mapped.restingHr,
      workload: mapped.workload,
      previousInjury: athlete.previousInjury,
      histHrv: hist.map((h) => h.hrvRmssd),
      histWorkload: hist.slice(0, 7).map((h) => h.workload),
    });
    await prisma.dailySnapshot.upsert({
      where: { athleteId_date: { athleteId: athlete.id, date: mapped.date } },
      create: {
        athleteId: athlete.id,
        date: mapped.date,
        sleepHours: mapped.sleepHours,
        restingHr: mapped.restingHr,
        hrvRmssd: mapped.hrvRmssd,
        workload: mapped.workload,
        missedSession: mapped.missedSession,
        sleepEfficiency: mapped.sleepEfficiency,
        remHours: mapped.remHours,
        deepHours: mapped.deepHours,
        ...scores,
      },
      update: {
        sleepHours: mapped.sleepHours,
        restingHr: mapped.restingHr,
        hrvRmssd: mapped.hrvRmssd,
        workload: mapped.workload,
        missedSession: mapped.missedSession,
        sleepEfficiency: mapped.sleepEfficiency,
        remHours: mapped.remHours,
        deepHours: mapped.deepHours,
        ...scores,
      },
    });
    await bumpAsOf(mapped.date);
    return c.json({ ok: true });
  });
}
