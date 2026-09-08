import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { cors } from "hono/cors";
import { prisma } from "./db";
import { toAthlete, toSnapshot } from "./map";
import { registerEntry } from "./entry";
import { registerTerraWebhook } from "./terra-webhook";
import { registerAnalysis } from "./analysis";
import { burnoutIndex } from "./src/lib/scores/mental";
import {
  addDays,
  computeTeamSummary,
  factorsFor,
  recommendationsFor,
  seriesForAthlete,
} from "./src/lib/wearables/queries";

const app = new Hono();
const origin = process.env.CORS_ORIGIN ?? "http://localhost:3400";

app.use(
  "*",
  cors({
    origin:
      origin === "*"
        ? "*"
        : origin.split(",").map((item) => item.trim()),
  }),
);

registerTerraWebhook(app);
registerEntry(app);
registerAnalysis(app);

app.get("/health", (c) => c.json({ ok: true }));

app.get("/meta", async (c) => {
  const meta = await prisma.meta.findUnique({ where: { id: 1 } });
  if (!meta) return c.json({ error: "источник не сконфигурирован" }, 503);
  return c.json({ asOf: meta.asOf, seedKey: meta.seedKey });
});

app.get("/athletes", async (c) => {
  const rows = await prisma.athlete.findMany({ orderBy: { lastName: "asc" } });
  return c.json(rows.map(toAthlete));
});

app.get("/athletes/:id", async (c) => {
  const row = await prisma.athlete.findUnique({
    where: { id: c.req.param("id") },
  });
  if (!row) return c.json({ error: "not_found" }, 404);
  return c.json(toAthlete(row));
});

app.get("/summary", async (c) => {
  const today = c.req.query("today");
  if (!today) return c.json({ error: "today required" }, 400);
  const athletes = (await prisma.athlete.findMany()).map(toAthlete);
  const snapshots = (await prisma.dailySnapshot.findMany()).map(toSnapshot);
  return c.json(computeTeamSummary(athletes, snapshots, today));
});

app.get("/athletes/:id/snapshot", async (c) => {
  const today = c.req.query("today");
  if (!today) return c.json({ error: "today required" }, 400);
  const row = await prisma.dailySnapshot.findUnique({
    where: {
      athleteId_date: { athleteId: c.req.param("id"), date: today },
    },
  });
  return c.json(row ? toSnapshot(row) : null);
});

app.get("/athletes/:id/series", async (c) => {
  const from = c.req.query("from");
  const to = c.req.query("to");
  if (!from || !to) return c.json({ error: "from and to required" }, 400);
  const id = c.req.param("id");
  const snapshots = (
    await prisma.dailySnapshot.findMany({ where: { athleteId: id } })
  ).map(toSnapshot);
  return c.json(seriesForAthlete(snapshots, id, from, to));
});

app.get("/athletes/:id/recommendations", async (c) => {
  const today = c.req.query("today");
  if (!today) return c.json({ error: "today required" }, 400);
  const id = c.req.param("id");
  const athleteRow = await prisma.athlete.findUnique({ where: { id } });
  const athlete = athleteRow ? toAthlete(athleteRow) : undefined;
  const snapRow = await prisma.dailySnapshot.findUnique({
    where: { athleteId_date: { athleteId: id, date: today } },
  });
  const hist = (
    await prisma.dailySnapshot.findMany({
      where: {
        athleteId: id,
        date: { gte: addDays(today, -14), lt: today },
      },
    })
  ).map(toSnapshot);
  const psych = await prisma.psychCheckin.findUnique({
    where: { athleteId_date: { athleteId: id, date: today } },
  });
  return c.json(
    recommendationsFor(
      athlete,
      snapRow ? toSnapshot(snapRow) : null,
      hist,
      psych ? burnoutIndex(psych) : undefined,
    ),
  );
});

app.get("/athletes/:id/injury-factors", async (c) => {
  const today = c.req.query("today");
  if (!today) return c.json({ error: "today required" }, 400);
  const id = c.req.param("id");
  const athleteRow = await prisma.athlete.findUnique({ where: { id } });
  const athlete = athleteRow ? toAthlete(athleteRow) : undefined;
  const snapRow = await prisma.dailySnapshot.findUnique({
    where: {
      athleteId_date: { athleteId: id, date: today },
    },
  });
  const hist = (
    await prisma.dailySnapshot.findMany({
      where: {
        athleteId: id,
        date: { gte: addDays(today, -14), lt: today },
      },
    })
  ).map(toSnapshot);
  return c.json(factorsFor(athlete, snapRow ? toSnapshot(snapRow) : null, hist));
});

const handler = new Hono();
handler.route("/", app);
handler.route("/api", app);

export default handler;

if (!process.env.VERCEL) {
  const port = Number(process.env.PORT ?? 8080);
  serve({ fetch: handler.fetch, port }, () => {
    console.log(`api listening on ${port}`);
  });
}