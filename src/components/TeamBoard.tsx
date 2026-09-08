"use client";

import { useMemo, useState } from "react";
import { EmptyState } from "@astryxdesign/core/EmptyState";
import { Grid } from "@astryxdesign/core/Grid";
import { Selector } from "@astryxdesign/core/Selector";
import { VStack } from "@astryxdesign/core/VStack";
import { AthleteCard } from "@/components/AthleteCard";
import { POSITIONS } from "@/lib/athletes/positions";
import type { TeamRow } from "@/lib/athletes/teamRows";
import type { Position, RiskZone, Trend } from "@/lib/wearables/types";

export function TeamBoard({ rows }: { rows: TeamRow[] }) {
  const [position, setPosition] = useState<Position | "all">("all");
  const [risk, setRisk] = useState<RiskZone | "all">("all");
  const [trend, setTrend] = useState<Trend | "all">("all");

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      if (position !== "all" && r.athlete.position !== position) return false;
      if (risk !== "all" && r.zone !== risk) return false;
      if (trend !== "all" && r.trend !== trend) return false;
      return true;
    });
  }, [rows, position, risk, trend]);

  const emptyCombo = position !== "all" && risk === "flag" && filtered.length === 0;

  return (
    <VStack gap={5}>
      <Grid columns={{ minWidth: 200, max: 3 }} gap={4}>
        <Selector
          label="позиция"
          value={position}
          onChange={(v) => setPosition(v as Position | "all")}
          options={[
            { value: "all", label: "все" },
            ...POSITIONS.map((p) => ({ value: p, label: p })),
          ]}
          status={
            emptyCombo
              ? { type: "warning", message: "Нет атлетов по выбранным условиям" }
              : undefined
          }
        />
        <Selector
          label="риск"
          value={risk}
          onChange={(v) => setRisk(v as RiskZone | "all")}
          options={[
            { value: "all", label: "все" },
            { value: "normal", label: "норма" },
            { value: "flag", label: "флаг" },
          ]}
        />
        <Selector
          label="тренд"
          value={trend}
          onChange={(v) => setTrend(v as Trend | "all")}
          options={[
            { value: "all", label: "все" },
            { value: "up", label: "рост" },
            { value: "down", label: "снижение" },
          ]}
        />
      </Grid>

      {filtered.length === 0 ? (
        <EmptyState
          title="Нет атлетов по выбранным условиям"
          description="Снимите фильтры, чтобы увидеть весь состав."
          headingLevel={2}
        />
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
          {filtered.map((r, i) => (
            <div
              key={r.athlete.id}
              className={i < 3 ? "sm:col-span-2 xl:row-span-2" : ""}
            >
              <AthleteCard
                athlete={r.athlete}
                today={r.today}
                hrv7={r.hrv7}
                zone={r.zone}
                featured={i < 3}
              />
            </div>
          ))}
        </div>
      )}
    </VStack>
  );
}
