import { clamp } from "./math";

export type PsychScales = {
  stress: number;
  motivation: number;
  anxiety: number;
  burnout: number;
  mood: number;
  cognitive: number;
};

/** 0–100 индекс, не вероятность именованного диагноза. */
export function burnoutIndex(p: PsychScales): number {
  const raw =
    p.burnout * 8 +
    p.stress * 5 +
    p.anxiety * 4 -
    p.mood * 4 -
    p.motivation * 3 -
    p.cognitive * 2;
  return Math.round(clamp(raw, 0, 100));
}

export function nutritionTargets(weightKg: number | null | undefined) {
  const w = weightKg && weightKg >= 40 ? weightKg : 82;
  return {
    kcal: Math.round(w * 50),
    proteinG: Math.round(w * 2.2),
    carbsG: Math.round(w * 6.2),
    fatG: Math.round(w * 1.15),
    waterL: Math.round(w * 0.07 * 10) / 10,
  };
}
