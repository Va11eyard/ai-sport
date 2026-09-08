"use client";

import { motion } from "motion/react";
import { Text } from "@astryxdesign/core/Text";

const TONE_COLOR: Record<"ready" | "risk" | "recover", string> = {
  ready: "var(--color-ready)",
  risk: "var(--color-risk)",
  recover: "var(--color-recovery)",
};

export function ArcGauge({
  value,
  size,
  label,
  tone = "ready",
}: {
  value: number | null;
  size: number;
  label: string;
  tone?: "ready" | "risk" | "recover";
}) {
  const stroke = Math.max(8, size * 0.12);
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circ = 2 * Math.PI * r * 0.75;
  const color = TONE_COLOR[tone];
  const offset = value == null ? circ : circ * (1 - value / 100);

  return (
    <div className="flex shrink-0 flex-col items-start gap-1">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-label={label}>
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke="oklch(0 0 0 / 0.1)"
          strokeWidth={stroke}
          strokeLinecap="round"
          transform={`rotate(135 ${cx} ${cy})`}
          strokeDasharray={`${circ} ${2 * Math.PI * r}`}
        />
        <motion.circle
          cx={cx}
          cy={cy}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          transform={`rotate(135 ${cx} ${cy})`}
          strokeDasharray={`${circ} ${2 * Math.PI * r}`}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        />
        <text
          x={cx}
          y={cy + 4}
          textAnchor="middle"
          className="font-num"
          fill="currentColor"
          fontSize={size * 0.28}
        >
          {value == null ? "—" : value}
        </text>
      </svg>
      <Text type="supporting" display="block">
        {label}
      </Text>
    </div>
  );
}
