import { FLAG_THRESHOLD } from "./constants";
import { DEFAULT_AS_OF } from "@/src/lib/synthetic/generate";

export { FLAG_THRESHOLD };
export const AS_OF = DEFAULT_AS_OF;

export const ZONES = {
  hrv: { min: 40, max: 80 },
  rhr: { min: 48, max: 62 },
  sleep: { min: 7, max: 9 },
} as const;