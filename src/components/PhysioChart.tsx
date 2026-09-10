"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Text } from "@astryxdesign/core/Text";
import { ZONES } from "@/lib/scores/ranges";
import type { DailyPhysio } from "@/lib/wearables/types";

export function PhysioChart({
  series,
}: {
  series: (DailyPhysio | null)[];
}) {
  const data = series.map((s, i) => ({
    i,
    date: s?.date ?? "",
    hrv: s?.hrvRmssd ?? null,
    rhr: s?.restingHr ?? null,
    sleep: s?.sleepHours ?? null,
    label: s?.date?.slice(5) ?? "",
  }));

  return (
    <div>
      <div className="h-52 w-full sm:h-80">
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="rgb(255 255 255 / 0.08)" vertical={false} />
          <ReferenceArea
            yAxisId="hrv"
            y1={ZONES.hrv.min}
            y2={ZONES.hrv.max}
            fill="oklch(0.62 0.19 155 / 0.12)"
            strokeOpacity={0}
          />
          <XAxis
            dataKey="label"
            tick={{ fill: "rgb(255 255 255 / 0.45)", fontSize: 10 }}
            interval="preserveStartEnd"
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            yAxisId="hrv"
            tick={{ fill: "rgb(255 255 255 / 0.45)", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={32}
          />
          <YAxis
            yAxisId="rhr"
            orientation="right"
            tick={{ fill: "rgb(255 255 255 / 0.45)", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={28}
          />
          <YAxis yAxisId="sleep" hide domain={[4, 10]} />
          <Tooltip
            contentStyle={{
              background: "#121417",
              border: "1px solid rgb(255 255 255 / 0.08)",
              color: "rgb(255 255 255 / 0.92)",
              fontSize: 12,
            }}
            formatter={(v, name) => [v ?? "нет данных", name]}
          />
          <Line
            yAxisId="hrv"
            type="monotone"
            dataKey="hrv"
            name="HRV"
            stroke="var(--color-ready)"
            dot={false}
            connectNulls={false}
            strokeWidth={1.5}
          />
          <Line
            yAxisId="rhr"
            type="monotone"
            dataKey="rhr"
            name="пульс покоя"
            stroke="oklch(0.72 0.04 250)"
            dot={false}
            connectNulls={false}
            strokeWidth={1.2}
          />
          <Line
            yAxisId="sleep"
            type="monotone"
            dataKey="sleep"
            name="сон"
            stroke="var(--color-risk)"
            dot={false}
            connectNulls={false}
            strokeWidth={1.2}
          />
        </LineChart>
      </ResponsiveContainer>
      </div>
      <Text type="supporting" display="block">
        зона HRV {ZONES.hrv.min}–{ZONES.hrv.max} · пульс {ZONES.rhr.min}–{ZONES.rhr.max} · сон{" "}
        {ZONES.sleep.min}–{ZONES.sleep.max} ч
      </Text>
    </div>
  );
}
