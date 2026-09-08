import { z } from "zod";

const isoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const scale10 = z.number().int().min(0).max(10);

export const createAthleteBody = z.object({
  lastName: z.string().trim().min(1).max(80),
  firstName: z.string().trim().min(1).max(80),
  position: z.enum([
    "вратарь",
    "центральный",
    "подвижный",
    "крайний",
    "полусредний",
  ]),
  previousInjury: z.boolean(),
  terraUserId: z.string().trim().min(1).max(80).optional(),
});

export const dayBody = z.object({
  date: isoDate,
  sleepHours: z.number().min(4).max(9.5),
  restingHr: z.number().min(42).max(78),
  hrvRmssd: z.number().min(18).max(95),
  workload: z.number().min(0).max(21),
  missedSession: z.boolean().optional().default(false),
  respRate: z.number().min(8).max(40).optional(),
  temperature: z.number().min(35).max(41).optional(),
  weightKg: z.number().min(40).max(140).optional(),
  bodyFatPct: z.number().min(3).max(40).optional(),
  muscleMassKg: z.number().min(20).max(90).optional(),
  sleepEfficiency: z.number().min(50).max(100).optional(),
  remHours: z.number().min(0).max(5).optional(),
  deepHours: z.number().min(0).max(5).optional(),
  awakenings: z.number().int().min(0).max(20).optional(),
  sleepLatencyMin: z.number().min(0).max(120).optional(),
  distanceM: z.number().min(0).max(20000).optional(),
  speedAvg: z.number().min(0).max(20).optional(),
  accelerations: z.number().int().min(0).max(200).optional(),
  shots: z.number().int().min(0).max(200).optional(),
  throwPower: z.number().min(0).max(200).optional(),
  powerWatts: z.number().min(0).max(2000).optional(),
});

const optLab = z.number().min(0).max(20000).optional();

export const labBody = z.object({
  date: isoDate,
  hemoglobin: optLab,
  vitaminD: optLab,
  ferritin: optLab,
  iron: optLab,
  testosterone: optLab,
  cortisol: optLab,
  igf1: optLab,
  ck: optLab,
  crp: optLab,
  lactate: optLab,
  vo2max: z.number().min(20).max(90).optional(),
});

export const psychBody = z.object({
  date: isoDate,
  stress: scale10,
  motivation: scale10,
  anxiety: scale10,
  burnout: scale10,
  mood: scale10,
  cognitive: scale10,
});

export const nutritionBody = z.object({
  date: isoDate,
  kcal: z.number().min(800).max(8000),
  proteinG: z.number().min(20).max(400),
  carbsG: z.number().min(50).max(900),
  fatG: z.number().min(20).max(300),
  waterL: z.number().min(0.5).max(10),
});