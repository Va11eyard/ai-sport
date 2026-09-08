const base = () =>
  process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${base()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    throw Object.assign(new Error("save_failed"), { status: res.status, data });
  }
  return data as T;
}

export async function putJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${base()}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    throw Object.assign(new Error("save_failed"), { status: res.status, data });
  }
  return data as T;
}

export async function getDay(athleteId: string, date: string) {
  const res = await fetch(
    `${base()}/athletes/${athleteId}/day?date=${date}`,
    { cache: "no-store" },
  );
  if (!res.ok) throw new Error("load_failed");
  return res.json() as Promise<import("./types").DayPayload>;
}

export function compactNums(body: Record<string, unknown>) {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(body)) {
    if (v == null) continue;
    if (typeof v === "number" && Number.isNaN(v)) continue;
    out[k] = v;
  }
  return out;
}