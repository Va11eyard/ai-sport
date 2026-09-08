import type { WearableAdapter } from "./interface";
import { HttpWearableAdapter } from "./http-adapter";

export function getWearableAdapter(): WearableAdapter {
  return new HttpWearableAdapter();
}

export { AdapterError } from "./errors";
export type { WearableAdapter } from "./interface";