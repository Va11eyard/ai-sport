import { createHmac, timingSafeEqual } from "node:crypto";

export function terraSourceReady(env: { TERRA_API_KEY?: string }): boolean {
  return Boolean(env.TERRA_API_KEY?.trim());
}

function hexToBytes(hex: string): Buffer | null {
  if (!/^[0-9a-fA-F]+$/.test(hex) || hex.length % 2 !== 0) return null;
  return Buffer.from(hex, "hex");
}

export function verifyTerraHmac(
  rawBody: string,
  header: string | undefined,
  secret: string,
): boolean {
  if (!header || !secret) return false;
  const v1 = header.includes("v1=")
    ? header.split("v1=")[1]?.split(",")[0]
    : header.trim();
  if (!v1) return false;
  const expected = createHmac("sha256", secret).update(rawBody).digest();
  const got = hexToBytes(v1);
  if (!got || got.length !== expected.length) return false;
  return timingSafeEqual(got, expected);
}
