import { randomUUID } from "node:crypto";
import type { Hono } from "hono";
import { prisma } from "./db";
import { toAthlete, toSnapshot } from "./map";
import { scoresFromDay } from "./scores-from-day";
import {
  createAthleteBody,
  dayBody,
  labBody,
  nutritionBody,
  psychBody,
} from "./validate";

function fail(c: { json: (b: unknown, s: number) => Response }, parsed: { success: false; error: { flatten: () => unknown } }) {
  return c.json({ error: "validation", issues: parsed.error.flatten() }, 400);
}

async function bumpAsOf(date: string) {
  const meta = await prisma.meta.findUnique({ where: { id: 1 } });
  if (!meta) {
    await prisma.meta.create({
      data: { id: 1, asOf: date, seedKey: "manual" },
    });
    return;
  }
  if (date > meta.asOf) {
    await prisma.meta.update({ where: { id: 1 }, data: { asOf: date } });
  }
}

export function registerEntry(app: Hono) {
  app.get("/athletes/:id/day", async (c) => {
    const date = c.req.query("date");
    if (!date) return c.json({ error: "date required" }, 400);
    const id = c.req.param("id");
    const [snap, lab, psych, nutrition, training] = await Promise.all([
      prisma.dailySnapshot.findUnique({
        where: { athleteId_date: { athleteId: id, date } },
      }),
      prisma.labPanel.findUnique({
        where: { athleteId_date: { athleteId: id, date } },
      }),
      prisma.psychCheckin.findUnique({
        where: { athleteId_date: { athleteId: id, date } },
      }),
      prisma.nutritionDay.findUnique({
        where: { athleteId_date: { athleteId: id, date } },
      }),
      prisma.trainingSession.findUnique({
        where: { athleteId_date: { athleteId: id, date } },
      }),
    ]);
    return c.json({
      snapshot: snap ? toSnapshot(snap) : null,
      extras: snap
        ? {
            respRate: snap.respRate,
            temperature: snap.temperature,
            weightKg: snap.weightKg,
            bodyFatPct: snap.bodyFatPct,
            muscleMassKg: snap.muscleMassKg,
            sleepEfficiency: snap.sleepEfficiency,
            remHours: snap.remHours,
            deepHours: snap.deepHours,
            awakenings: snap.awakenings,
            sleepLatencyMin: snap.sleepLatencyMin,
          }
        : null,
      lab,
      psych,
      nutrition,
      training,
    });
  });

  app.post("/athletes", async (c) => {
    let raw: unknown;
    try {
      raw = await c.req.json();
    } catch {
      return c.json({ error: "invalid_json" }, 400);
    }
    const parsed = createAthleteBody.safeParse(raw);
    if (!parsed.success) return fail(c, parsed);
    const id = `ath_${randomUUID()}`;
    const row = await prisma.athlete.create({
      data: { id, ...parsed.data },
    });
    return c.json(toAthlete(row), 201);
  });

  app.put("/athletes/:id/day", async (c) => {
    const id = c.req.param("id");
    const athlete = await prisma.athlete.findUnique({ where: { id } });
    if (!athlete) return c.json({ error: "not_found" }, 404);
    const parsed = dayBody.safeParse(await c.req.json());
    if (!parsed.success) return fail(c, parsed);
    const b = parsed.data;
    const hist = await prisma.dailySnapshot.findMany({
      where: { athleteId: id, date: { lt: b.date } },
      orderBy: { date: "desc" },
      take: 14,
    });
    const scores = scoresFromDay({
      sleepHours: b.sleepHours,
      hrvRmssd: b.hrvRmssd,
      restingHr: b.restingHr,
      workload: b.workload,
      previousInjury: athlete.previousInjury,
      histHrv: hist.map((h) => h.hrvRmssd),
      histWorkload: hist.slice(0, 7).map((h) => h.workload),
    });
    const snap = await prisma.dailySnapshot.upsert({
      where: { athleteId_date: { athleteId: id, date: b.date } },
      create: {
        athleteId: id,
        date: b.date,
        sleepHours: b.sleepHours,
        restingHr: b.restingHr,
        hrvRmssd: b.hrvRmssd,
        workload: b.workload,
        missedSession: b.missedSession,
        ...scores,
        respRate: b.respRate,
        temperature: b.temperature,
        weightKg: b.weightKg,
        bodyFatPct: b.bodyFatPct,
        muscleMassKg: b.muscleMassKg,
        sleepEfficiency: b.sleepEfficiency,
        remHours: b.remHours,
        deepHours: b.deepHours,
        awakenings: b.awakenings,
        sleepLatencyMin: b.sleepLatencyMin,
      },
      update: {
        sleepHours: b.sleepHours,
        restingHr: b.restingHr,
        hrvRmssd: b.hrvRmssd,
        workload: b.workload,
        missedSession: b.missedSession,
        ...scores,
        respRate: b.respRate,
        temperature: b.temperature,
        weightKg: b.weightKg,
        bodyFatPct: b.bodyFatPct,
        muscleMassKg: b.muscleMassKg,
        sleepEfficiency: b.sleepEfficiency,
        remHours: b.remHours,
        deepHours: b.deepHours,
        awakenings: b.awakenings,
        sleepLatencyMin: b.sleepLatencyMin,
      },
    });
    await prisma.trainingSession.upsert({
      where: { athleteId_date: { athleteId: id, date: b.date } },
      create: {
        athleteId: id,
        date: b.date,
        distanceM: b.distanceM,
        speedAvg: b.speedAvg,
        accelerations: b.accelerations,
        shots: b.shots,
        throwPower: b.throwPower,
        powerWatts: b.powerWatts,
      },
      update: {
        distanceM: b.distanceM,
        speedAvg: b.speedAvg,
        accelerations: b.accelerations,
        shots: b.shots,
        throwPower: b.throwPower,
        powerWatts: b.powerWatts,
      },
    });
    await bumpAsOf(b.date);
    return c.json(toSnapshot(snap));
  });

  app.put("/athletes/:id/labs", async (c) => {
    const id = c.req.param("id");
    if (!(await prisma.athlete.findUnique({ where: { id } }))) {
      return c.json({ error: "not_found" }, 404);
    }
    const parsed = labBody.safeParse(await c.req.json());
    if (!parsed.success) return fail(c, parsed);
    const b = parsed.data;
    const row = await prisma.labPanel.upsert({
      where: { athleteId_date: { athleteId: id, date: b.date } },
      create: { athleteId: id, ...b },
      update: b,
    });
    await bumpAsOf(b.date);
    return c.json(row);
  });

  app.put("/athletes/:id/psych", async (c) => {
    const id = c.req.param("id");
    if (!(await prisma.athlete.findUnique({ where: { id } }))) {
      return c.json({ error: "not_found" }, 404);
    }
    const parsed = psychBody.safeParse(await c.req.json());
    if (!parsed.success) return fail(c, parsed);
    const b = parsed.data;
    const row = await prisma.psychCheckin.upsert({
      where: { athleteId_date: { athleteId: id, date: b.date } },
      create: { athleteId: id, ...b },
      update: b,
    });
    await bumpAsOf(b.date);
    return c.json(row);
  });

  app.put("/athletes/:id/nutrition", async (c) => {
    const id = c.req.param("id");
    if (!(await prisma.athlete.findUnique({ where: { id } }))) {
      return c.json({ error: "not_found" }, 404);
    }
    const parsed = nutritionBody.safeParse(await c.req.json());
    if (!parsed.success) return fail(c, parsed);
    const b = parsed.data;
    const row = await prisma.nutritionDay.upsert({
      where: { athleteId_date: { athleteId: id, date: b.date } },
      create: { athleteId: id, ...b },
      update: b,
    });
    await bumpAsOf(b.date);
    return c.json(row);
  });
}