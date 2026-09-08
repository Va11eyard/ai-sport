import { clamp } from "@/src/lib/scores/math";
import { RANGES } from "@/src/lib/scores/constants";

export type TerraDayInput = {
  userId: string;
  date: string;
  sleepSeconds: number;
  restingHr: number;
  hrvRmssd: number;
  activeSeconds: number;
  sleepEfficiency?: number;
  remHours?: number;
  deepHours?: number;
};

export function mapTerraDay(input: TerraDayInput) {
  if (!input.userId.trim()) throw new Error("user required");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.date)) throw new Error("date required");
  const sleepHours = clamp(
    input.sleepSeconds / 3600,
    RANGES.sleepHours.min,
    RANGES.sleepHours.max,
  );
  const restingHr = clamp(
    input.restingHr,
    RANGES.restingHr.min,
    RANGES.restingHr.max,
  );
  const hrvRmssd = clamp(
    input.hrvRmssd,
    RANGES.hrvRmssd.min,
    RANGES.hrvRmssd.max,
  );
  const workload = clamp(
    (input.activeSeconds / 3600) * 3,
    RANGES.workload.min,
    RANGES.workload.max,
  );
  return {
    date: input.date,
    sleepHours,
    restingHr,
    hrvRmssd,
    workload,
    missedSession: false,
    sleepEfficiency: input.sleepEfficiency,
    remHours: input.remHours,
    deepHours: input.deepHours,
  };
}

/** Best-effort extract from Terra daily webhook JSON. */
export function terraDayFromWebhook(payload: unknown): TerraDayInput {
  const p = payload as {
    user?: { user_id?: string };
    terra_user_id?: string;
    start_time?: string;
    data?: Array<{
      metadata?: { start_time?: string };
      sleep_durations_data?: {
        asleep?: { duration_asleep_state_seconds?: number };
        sleep_efficiency?: number;
        asleep_duration_rem_seconds?: number;
        asleep_duration_deep_seconds?: number;
      };
      heart_rate_data?: { summary?: { resting_hr_bpm?: number } };
      hrv_data?: { summary?: { rmssd?: number } };
      active_durations_data?: { activity_seconds?: number };
    }>;
  };
  const userId = p.user?.user_id ?? p.terra_user_id ?? "";
  const day = p.data?.[0];
  const start = day?.metadata?.start_time ?? p.start_time ?? "";
  const date = start.slice(0, 10);
  const sleep =
    day?.sleep_durations_data?.asleep?.duration_asleep_state_seconds ?? 0;
  return {
    userId,
    date,
    sleepSeconds: sleep,
    restingHr: day?.heart_rate_data?.summary?.resting_hr_bpm ?? 55,
    hrvRmssd: day?.hrv_data?.summary?.rmssd ?? 40,
    activeSeconds: day?.active_durations_data?.activity_seconds ?? 0,
    sleepEfficiency: day?.sleep_durations_data?.sleep_efficiency,
    remHours: day?.sleep_durations_data?.asleep_duration_rem_seconds
      ? day.sleep_durations_data.asleep_duration_rem_seconds / 3600
      : undefined,
    deepHours: day?.sleep_durations_data?.asleep_duration_deep_seconds
      ? day.sleep_durations_data.asleep_duration_deep_seconds / 3600
      : undefined,
  };
}
