"use client";

import { useMemo, useState, type ReactNode } from "react";
import { EmptyState } from "@astryxdesign/core/EmptyState";
import { Selector } from "@astryxdesign/core/Selector";
import { VStack } from "@astryxdesign/core/VStack";
import { AthleteCard } from "@/components/AthleteCard";
import { needsAttention } from "@/lib/athletes/availability";
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

  const attention = filtered.filter((r) => needsAttention(r.availability));
  const water = filtered.filter((r) => r.availability === "water");
  const emptyCombo = position !== "all" && risk === "flag" && filtered.length === 0;

  return (
    <VStack gap={6}>
      <div>
        <p className="roster-caption">Сузить список</p>
        <div className="team-filters">
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
            label="флаг риска"
            value={risk}
            onChange={(v) => setRisk(v as RiskZone | "all")}
            options={[
              { value: "all", label: "все" },
              { value: "normal", label: "норма" },
              { value: "flag", label: "флаг" },
            ]}
          />
          <Selector
            label="HRV за 7 дней"
            value={trend}
            onChange={(v) => setTrend(v as Trend | "all")}
            options={[
              { value: "all", label: "все" },
              { value: "up", label: "рост" },
              { value: "down", label: "снижение" },
            ]}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="Нет атлетов по выбранным условиям"
          description="Снимите фильтры, чтобы увидеть весь состав."
          headingLevel={2}
        />
      ) : (
        <>
          <RosterBlock
            step="1"
            title="Внимание"
            hint="Нет данных, вне воды или ограничение. Разберите их до сессии."
            count={attention.length}
          >
            {attention.length === 0 ? (
              <p className="roster-empty">Сейчас никого в очереди внимания.</p>
            ) : (
              <div className="roster-grid roster-grid--attention">
                {attention.map((r, i) => (
                  <AthleteCard
                    key={r.athlete.id}
                    athlete={r.athlete}
                    today={r.today}
                    hrv7={r.hrv7}
                    zone={r.zone}
                    availability={r.availability}
                    why={r.why}
                    featured={i < 3}
                  />
                ))}
              </div>
            )}
          </RosterBlock>
          <RosterBlock
            step="2"
            title="На воду"
            hint="Полная сессия. Нажмите карточку, если нужен день и рекомендации."
            count={water.length}
          >
            {water.length === 0 ? (
              <p className="roster-empty">По фильтрам нет атлетов на воду.</p>
            ) : (
              <div className="roster-grid">
                {water.map((r) => (
                  <AthleteCard
                    key={r.athlete.id}
                    athlete={r.athlete}
                    today={r.today}
                    hrv7={r.hrv7}
                    zone={r.zone}
                    availability={r.availability}
                    why={r.why}
                  />
                ))}
              </div>
            )}
          </RosterBlock>
        </>
      )}
    </VStack>
  );
}

function RosterBlock({
  step,
  title,
  hint,
  count,
  children,
}: {
  step: string;
  title: string;
  hint: string;
  count: number;
  children: ReactNode;
}) {
  return (
    <section className="roster-block">
      <header className="roster-block__head">
        <h2 className="roster-block__title">
          <span className="roster-block__step font-num">{step}</span>
          {title}
          <span className="roster-block__count font-num">{count}</span>
        </h2>
        <p className="roster-block__hint">{hint}</p>
      </header>
      {children}
    </section>
  );
}
