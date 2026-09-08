import { HStack } from "@astryxdesign/core/HStack";
import { Text } from "@astryxdesign/core/Text";
import { addDays } from "@/lib/scores/math";
import type { DailyPhysio } from "@/lib/wearables/types";

export function LoadHeatmap({
  series,
  asOf,
}: {
  series: (DailyPhysio | null)[];
  asOf: string;
}) {
  const byDate = new Map(series.filter(Boolean).map((s) => [s!.date, s!.workload]));
  const weekStart = mondayOnOrBefore(asOf);
  const first = addDays(weekStart, -49);
  const weeks: { date: string; load: number | null }[][] = [];
  for (let w = 0; w < 8; w++) {
    const col: { date: string; load: number | null }[] = [];
    for (let d = 0; d < 7; d++) {
      const date = addDays(first, w * 7 + d);
      const load = date > asOf ? null : (byDate.get(date) ?? null);
      col.push({ date, load });
    }
    weeks.push(col);
  }
  const loads = weeks.flat().map((c) => c.load).filter((n): n is number => n != null);
  const q75 = quantile(loads, 0.75);

  return (
    <div className="w-full">
      <div className="-mx-1 overflow-x-auto overscroll-x-contain">
        <div className="flex min-w-[min(100%,22rem)] w-full gap-2 px-1">
          <div className="flex shrink-0 flex-col justify-between py-0.5 text-[10px] text-secondary">
            {["пн", "вт", "ср", "чт", "пт", "сб", "вс"].map((d) => (
              <span key={d} className="leading-none">
                {d}
              </span>
            ))}
          </div>
          <div
            className="grid min-w-0 flex-1 grid-cols-8 gap-1.5"
            style={{ gridAutoFlow: "column", gridTemplateRows: "repeat(7, minmax(0, 1fr))" }}
          >
            {weeks.flatMap((col) =>
              col.map((c) => (
                <div
                  key={c.date}
                  title={`${c.date} ${c.load ?? "—"}`}
                  className="aspect-square min-h-6 w-full rounded-md"
                  style={{ background: cellColor(c.load, q75) }}
                />
              )),
            )}
          </div>
        </div>
      </div>
      <HStack hAlign="start" vAlign="center" gap={4} className="mt-3" wrap="wrap">
        <LegendSwatch color={cellColor(null, q75)} label="покой" />
        <LegendSwatch color={cellColor(8, q75)} label="норма" />
        <LegendSwatch color={cellColor(Math.max(q75, 16), q75)} label="пик" />
      </HStack>
    </div>
  );
}

function LegendSwatch({ color, label }: { color: string; label: string }) {
  return (
    <HStack hAlign="start" vAlign="center" gap={2}>
      <span className="size-3.5 rounded-sm" style={{ background: color }} />
      <Text type="supporting">{label}</Text>
    </HStack>
  );
}

function mondayOnOrBefore(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  const dow = dt.getUTCDay();
  const back = (dow + 6) % 7;
  dt.setUTCDate(dt.getUTCDate() - back);
  return dt.toISOString().slice(0, 10);
}

function quantile(xs: number[], q: number): number {
  if (xs.length === 0) return 80;
  const s = [...xs].sort((a, b) => a - b);
  return s[Math.min(s.length - 1, Math.floor(s.length * q))];
}

function cellColor(load: number | null, q75: number): string {
  if (load == null) return "oklch(0.93 0.015 155)";
  const t = Math.min(1, load / 21);
  if (load >= q75) {
    return `oklch(${0.78 - t * 0.16} 0.19 48)`;
  }
  return `oklch(${0.82 - t * 0.22} ${0.14 + t * 0.06} 155)`;
}
